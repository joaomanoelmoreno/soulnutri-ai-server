# -*- coding: utf-8 -*-
"""Contrato local nome_en -> alias do Radar, sem chamadas externas."""

import ast
import asyncio
import json
import os
import re
import sys
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from services.gemini_flash_service import identify_dish_gemini_flash
from services.perplexity_food_content_service import build_queries, evaluate_result


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = BACKEND_ROOT / "server.py"
FRONTEND_PATH = BACKEND_ROOT.parent / "frontend" / "src" / "App.js"
NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


def _load_server_helper():
    tree = ast.parse(SERVER_PATH.read_text(encoding="utf-8"), filename=str(SERVER_PATH))
    helper = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_radar_aliases_from_gemini"
    )
    module = ast.Module(body=[helper], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(SERVER_PATH), "exec"), namespace)
    return namespace["_radar_aliases_from_gemini"]


def _frontend_alias_param(result):
    source = FRONTEND_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"const getRadarAliasesParam = \(result\) => \{(.*?)\n\};",
        source,
        re.DOTALL,
    )
    if not match:
        raise AssertionError("getRadarAliasesParam não encontrada")
    script = (
        f"const result = {json.dumps(result, ensure_ascii=False)};"
        f"const encodeURIComponent = global.encodeURIComponent;"
        f"const fn = (result) => {{{match.group(1)}}};"
        "process.stdout.write(fn(result));"
    )
    import subprocess
    completed = subprocess.run(
        ["node", "-e", script], check=True, capture_output=True, text=True
    )
    return completed.stdout


class _FakeImage:
    size = (100, 100)
    mode = "RGB"
    format = "JPEG"

    def getexif(self):
        return {}

    def resize(self, _size, _filter):
        return self

    def convert(self, _mode):
        return self

    def save(self, buffer, **_kwargs):
        buffer.write(b"fake-jpeg")


class _GeminiHarness:
    def __init__(self, response_payload):
        self.calls = 0
        self.response_payload = response_payload

    def modules(self):
        harness = self

        class _Models:
            def generate_content(self, **_kwargs):
                harness.calls += 1
                return types.SimpleNamespace(text=json.dumps(harness.response_payload))

        class _Client:
            def __init__(self, **_kwargs):
                self.models = _Models()

        fake_genai = types.SimpleNamespace(
            Client=_Client,
            types=types.SimpleNamespace(
                Part=types.SimpleNamespace(from_bytes=lambda **_kwargs: object())
            ),
        )
        fake_google = types.ModuleType("google")
        fake_google.genai = fake_genai
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = types.SimpleNamespace(
            open=lambda _stream: _FakeImage(),
            LANCZOS=1,
        )
        return {"google": fake_google, "PIL": fake_pil}


class RadarGeminiAliasTest(unittest.TestCase):
    def _identify(self, payload):
        harness = _GeminiHarness(payload)
        with patch.dict(sys.modules, harness.modules()):
            with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-local-key"}, clear=False):
                result = asyncio.run(identify_dish_gemini_flash(b"fake-image"))
        return result, harness.calls

    def test_same_gemini_call_preserves_portuguese_name_and_english_name(self):
        result, calls = self._identify({
            "nome": "Brotos de brócolis",
            "nome_en": "Broccoli Sprouts",
            "cat": "v",
            "kcal": 35,
            "prot": 3,
            "carb": 4,
            "gord": 1,
            "alerg": [],
            "ing": ["brócolis"],
        })

        self.assertEqual(calls, 1)
        self.assertEqual(result["nome"], "Brotos de brócolis")
        self.assertEqual(result["nome_en"], "Broccoli Sprouts")

    def test_missing_english_name_preserves_previous_result_shape_behavior(self):
        result, calls = self._identify({
            "nome": "Brotos de brócolis",
            "cat": "v",
            "ing": ["brócolis"],
        })

        self.assertEqual(calls, 1)
        self.assertEqual(result["nome"], "Brotos de brócolis")
        self.assertEqual(result["nome_en"], "")

    def test_server_builds_only_explicit_non_duplicate_radar_alias(self):
        helper = _load_server_helper()
        self.assertEqual(
            helper({"nome": "Brotos de brócolis", "nome_en": "Broccoli Sprouts"}),
            ["Broccoli Sprouts"],
        )
        self.assertEqual(helper({"nome": "Brotos de brócolis"}), [])
        self.assertEqual(helper({"nome": "Atum", "nome_en": "atum"}), [])
        source = SERVER_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "'radar_aliases': _radar_aliases_from_gemini(flash_result)",
            source,
        )
        self.assertIn(
            '"radar_aliases": decision.get(\'radar_aliases\', [])',
            source,
        )

    def test_english_alias_is_used_by_queries_and_local_matching(self):
        queries = build_queries(
            "Brotos de brócolis", aliases=["Broccoli Sprouts"]
        )
        self.assertTrue(all('"Brotos de brócolis"' in query for query in queries))
        self.assertTrue(all('"Broccoli Sprouts"' in query for query in queries))

        candidate = evaluate_result({
            "title": "National broccoli sprouts recall after contamination warning",
            "snippet": "Broccoli sprouts distributed nationally were recalled.",
            "url": "https://www.fda.gov/safety/recalls-market-withdrawals/broccoli-sprouts",
            "date": "2026-09-20",
        }, "Brotos de brócolis", aliases=["Broccoli Sprouts"], now=NOW)
        self.assertTrue(candidate["accepted"])
        self.assertNotIn("alimento_nao_confirmado", candidate["reasons"])

    def test_vaguely_related_english_result_remains_rejected(self):
        candidate = evaluate_result({
            "title": "Broccoli research examines nutrition",
            "snippet": "A recent study discusses broccoli nutrition.",
            "url": "https://www.bmj.com/content/broccoli-nutrition",
            "date": "2026-09-20",
        }, "Brotos de brócolis", aliases=["Broccoli Sprouts"], now=NOW)

        self.assertFalse(candidate["accepted"])
        self.assertIn("alimento_nao_confirmado", candidate["reasons"])

    def test_frontend_omits_alias_for_cibi_or_old_cached_response(self):
        self.assertEqual(_frontend_alias_param({
            "source": "local_index",
            "dish_display": "Feijão do Chef",
        }), "")
        self.assertEqual(_frontend_alias_param({
            "source": "gemini_flash",
            "dish_display": "Brotos de brócolis",
            "radar_aliases": ["Broccoli Sprouts"],
        }), "&aliases=Broccoli%20Sprouts")
        source = FRONTEND_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "const radarAliasesParam = getRadarAliasesParam(resultWithTime);",
            source,
        )
        self.assertIn("${radarAliasesParam}", source)


if __name__ == "__main__":
    unittest.main()
