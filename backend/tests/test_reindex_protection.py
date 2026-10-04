# -*- coding: utf-8 -*-
"""Testes isolados da protecao das rotas de reindexacao."""

import ast
import hashlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = BACKEND_ROOT / "server.py"


class _Logger:
    def info(self, *_args, **_kwargs):
        pass

    def error(self, *_args, **_kwargs):
        pass


class _FakeIndex:
    def __init__(self, data_dir):
        self.data_dir = str(data_dir)
        self.dishes = ["Classe A", "Classe A", "Classe B"]
        self.dish_to_idx = {"Classe A": [0, 1], "Classe B": [2]}
        self.embeddings = np.arange(12, dtype=np.float32).reshape(3, 4)
        self.build_calls = 0

    def build_index(self, max_per_dish=10):
        self.build_calls += 1
        return {
            "total_dishes": 2,
            "total_images": 3,
            "elapsed_seconds": 0.0,
        }


def _fingerprint(index):
    digest = hashlib.sha256()
    digest.update(json.dumps(index.dishes, ensure_ascii=False).encode("utf-8"))
    digest.update(
        json.dumps(index.dish_to_idx, sort_keys=True, ensure_ascii=False).encode("utf-8")
    )
    digest.update(index.embeddings.tobytes())
    return (len(index.dishes), len(index.dish_to_idx), digest.hexdigest())


def _load_test_app(index, admin_secret="test-admin-secret"):
    tree = ast.parse(SERVER_PATH.read_text(encoding="utf-8"), filename=str(SERVER_PATH))
    selected_names = {
        "verify_admin_key",
        "_validate_reindex_source",
        "reindex",
        "reindex_background",
    }
    selected = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in selected_names
    ]
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)

    router = APIRouter()
    namespace = {
        "ADMIN_SECRET_KEY": admin_secret,
        "Depends": Depends,
        "Header": Header,
        "HTTPException": HTTPException,
        "JSONResponse": JSONResponse,
        "Path": Path,
        "api_router": router,
        "logger": _Logger(),
        "os": __import__("os"),
    }

    ai_module = types.ModuleType("ai")
    ai_module.__path__ = []
    index_module = types.ModuleType("ai.index")
    index_module.get_index = lambda: index

    sys.modules["ai"] = ai_module
    sys.modules["ai.index"] = index_module
    exec(compile(module, str(SERVER_PATH), "exec"), namespace)

    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app), namespace


class ReindexProtectionTest(unittest.TestCase):
    def test_routes_reject_missing_and_invalid_credentials_without_mutation(self):
        with tempfile.TemporaryDirectory() as data_dir:
            index = _FakeIndex(data_dir)
            before = _fingerprint(index)
            client, _ = _load_test_app(index)

            for route in ("/api/ai/reindex", "/api/ai/reindex-background"):
                with self.subTest(route=route, credential="missing"):
                    response = client.post(route)
                    self.assertEqual(response.status_code, 401)
                with self.subTest(route=route, credential="invalid"):
                    response = client.post(route, headers={"X-Admin-Key": "wrong"})
                    self.assertEqual(response.status_code, 401)

            self.assertEqual(index.build_calls, 0)
            self.assertEqual(_fingerprint(index), before)

    def test_unconfigured_admin_auth_fails_closed(self):
        with tempfile.TemporaryDirectory() as data_dir:
            index = _FakeIndex(data_dir)
            before = _fingerprint(index)
            client, _ = _load_test_app(index, admin_secret="")

            response = client.post("/api/ai/reindex")

            self.assertEqual(response.status_code, 403)
            self.assertEqual(index.build_calls, 0)
            self.assertEqual(_fingerprint(index), before)

    def test_valid_credential_reaches_validation_but_missing_dataset_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as parent_dir:
            missing_dir = Path(parent_dir) / "missing"
            index = _FakeIndex(missing_dir)
            before = _fingerprint(index)
            client, _ = _load_test_app(index)

            for route in ("/api/ai/reindex", "/api/ai/reindex-background"):
                with self.subTest(route=route):
                    response = client.post(route, headers={"X-Admin-Key": "test-admin-secret"})
                    self.assertEqual(response.status_code, 409)
                    self.assertIn("Fonte de reindexacao indisponivel", response.text)

            self.assertEqual(index.build_calls, 0)
            self.assertEqual(_fingerprint(index), before)

    def test_incomplete_source_is_rejected_before_builder_without_mutation(self):
        with tempfile.TemporaryDirectory() as data_dir:
            data_path = Path(data_dir)
            class_a = data_path / "Classe A"
            class_a.mkdir()
            (class_a / "a.jpg").write_bytes(b"not-decoded-by-validation")

            index = _FakeIndex(data_path)
            before = _fingerprint(index)
            client, _ = _load_test_app(index)

            response = client.post(
                "/api/ai/reindex",
                headers={"X-Admin-Key": "test-admin-secret"},
            )

            self.assertEqual(response.status_code, 409)
            self.assertIn("nao cobre todas as classes atuais", response.text)
            self.assertEqual(index.build_calls, 0)
            self.assertEqual(_fingerprint(index), before)

    def test_valid_credential_and_coherent_source_reach_builder(self):
        with tempfile.TemporaryDirectory() as data_dir:
            data_path = Path(data_dir)
            for dish_name, image_names in {
                "Classe A": ("a1.jpg", "a2.jpg"),
                "Classe B": ("b1.png",),
            }.items():
                dish_dir = data_path / dish_name
                dish_dir.mkdir()
                for image_name in image_names:
                    (dish_dir / image_name).write_bytes(b"not-decoded-by-validation")

            index = _FakeIndex(data_path)
            client, _ = _load_test_app(index)

            response = client.post(
                "/api/ai/reindex",
                headers={"X-Admin-Key": "test-admin-secret"},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(index.build_calls, 1)


if __name__ == "__main__":
    unittest.main()
