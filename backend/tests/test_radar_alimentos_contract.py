# -*- coding: utf-8 -*-
"""Contrato isolado do endpoint Radar da main, sem Mongo ou rede reais."""

import ast
import asyncio
import sys
import types
import unittest
import warnings
from pathlib import Path
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = BACKEND_ROOT / "server.py"


class _Router:
    def get(self, _path):
        return lambda function: function


class _Logger:
    def info(self, *_args, **_kwargs):
        pass

    def warning(self, *_args, **_kwargs):
        pass


class _Users:
    def __init__(self, user):
        self.user = user

    async def find_one(self, _query, _projection):
        return self.user


class _DB:
    def __init__(self, user):
        self.users = _Users(user)


class _Provider:
    def __init__(self, item):
        self.item = item
        self.calls = []

    async def get_breaking_news(self, **kwargs):
        self.calls.append(kwargs)
        return dict(self.item) if self.item else None


def _load_endpoint(user, provider, premium_active):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        tree = ast.parse(SERVER_PATH.read_text(encoding="utf-8"), filename=str(SERVER_PATH))
    endpoint = next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_radar_alimentos"
    )
    module = ast.Module(body=[endpoint], type_ignores=[])
    ast.fix_missing_locations(module)

    breaking_module = types.ModuleType("services.breaking_news_service")
    breaking_module.get_breaking_news = provider.get_breaking_news
    profile_module = types.ModuleType("services.profile_service")
    profile_module.hash_pin = lambda pin: f"hash:{pin}"
    profile_module.verificar_premium_ativo = lambda _user: {"ativo": premium_active}
    radar_module = types.ModuleType("services.radar_diagnostics")
    radar_module.log_runtime_status = lambda: None
    radar_module.begin_request = lambda: None
    radar_module.end_request = lambda _tokens: None
    radar_module.active = lambda: False
    radar_module.elapsed_ms = lambda: None
    radar_module.log_event = lambda *_args, **_kwargs: None

    services_module = types.ModuleType("services")
    services_module.__path__ = []
    services_module.radar_diagnostics = radar_module
    sys.modules["services"] = services_module
    sys.modules["services.breaking_news_service"] = breaking_module
    sys.modules["services.profile_service"] = profile_module
    sys.modules["services.radar_diagnostics"] = radar_module
    namespace = {
        "api_router": _Router(),
        "Header": lambda default=None, **_kwargs: default,
        "db": _DB(user),
        "logger": _Logger(),
        "_norm_nome": lambda value: value.strip(),
        "time": __import__("time"),
    }
    exec(compile(module, str(SERVER_PATH), "exec"), namespace)
    return namespace["get_radar_alimentos"]


class RadarAlimentosMainContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_free_does_not_call_provider(self):
        provider = _Provider({"categoria": "alerta", "titulo": "Alerta"})
        endpoint = _load_endpoint({"nome": "Free"}, provider, False)
        result = await endpoint("atum", pin="1234", nome="Free")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "Acesso Premium necessário")
        self.assertEqual(provider.calls, [])

    async def test_premium_keeps_main_response_and_timeout_15_seconds(self):
        original_url = "https://example.test/noticia?token=ORIGINAL#parte"
        provider = _Provider({
            "categoria": "risco",
            "titulo": "Risco atual",
            "resumo": "Resumo",
            "url": original_url,
            "fonte": "Fonte",
            "impacto": "alto",
            "data": "2026-09-20",
        })
        endpoint = _load_endpoint({"nome": "Premium"}, provider, True)
        observed_timeouts = []
        real_wait_for = asyncio.wait_for

        async def recording_wait_for(awaitable, timeout):
            observed_timeouts.append(timeout)
            return await real_wait_for(awaitable, timeout)

        with patch.object(asyncio, "wait_for", recording_wait_for):
            result = await endpoint(
                "atum", ingredientes="atum, sal", pin="5678", nome="Premium"
            )

        self.assertEqual(observed_timeouts, [15.0])
        self.assertEqual(len(provider.calls), 1)
        self.assertEqual(provider.calls[0]["ingredientes"], ["atum", "sal"])
        self.assertTrue(result["radar"]["has_alert"])
        self.assertEqual(result["radar"]["type"], "alerta")
        self.assertEqual(result["radar"]["url"], original_url)

    async def test_premium_empty_provider_result_keeps_empty_main_contract(self):
        provider = _Provider(None)
        endpoint = _load_endpoint({"nome": "Premium"}, provider, True)
        result = await endpoint("atum", pin="5678", nome="Premium")
        self.assertTrue(result["ok"])
        self.assertIsNone(result["radar"])
        self.assertEqual(len(provider.calls), 1)


if __name__ == "__main__":
    unittest.main()
