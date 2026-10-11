# -*- coding: utf-8 -*-
"""Local route integration tests for the synthetic visual index v2 flow."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import numpy as np
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import server  # noqa: E402
from ai.index import DishIndex  # noqa: E402
from ai.index_loader import LoadedIndexArtifacts  # noqa: E402
from services.cache_service import clear_cache  # noqa: E402


class _EmptyCollection:
    async def find_one(self, *_args, **_kwargs):
        return None


class _FakeDatabase:
    dishes = _EmptyCollection()
    dish_families = _EmptyCollection()
    users = _EmptyCollection()


async def _disabled_setting(*_args, **_kwargs):
    return False


async def _no_nutrition(*_args, **_kwargs):
    return None


def _artifacts(schema_version, class_id, class_name):
    embeddings = np.asarray([[0.1] * 512], dtype=np.float32)
    embeddings.setflags(write=False)
    if schema_version == 1:
        return LoadedIndexArtifacts(
            schema_version=1,
            embeddings=embeddings,
            visual_labels=(class_name,),
            dish_to_idx={class_name: (0,)},
            provenance=(),
            legacy_metadata={class_name: {"image_count": 1}},
            index_metadata={"version": "1.0"},
        )
    return LoadedIndexArtifacts(
        schema_version=2,
        embeddings=embeddings,
        visual_labels=(class_name,),
        dish_to_idx={class_name: (0,)},
        provenance=(
            {
                "embedding_index": 0,
                "visual_class_id": class_id,
                "visual_class": class_name,
            },
        ),
        legacy_metadata={class_name: {"image_count": 1}},
        index_metadata={
            "version": "2.0",
            "index_id": f"synthetic-{class_id}",
            "model_version": "openclip-synthetic-v1",
            "preprocessing_version": "preprocess-synthetic-v1",
            "taxonomy_version": "visual-family-initial-3-v1",
        },
    )


class _FakeIndex:
    def __init__(self, artifacts, results):
        self.loaded_artifacts = artifacts
        self.results = results
        self.search_calls = 0

    def is_ready(self):
        return True

    def search(self, _image_bytes, _top_k):
        self.search_calls += 1
        return [dict(item) for item in self.results]


def _result(dish, score=0.82):
    return {
        "dish": dish,
        "score": score,
        "raw_score": score,
        "confidence": "media" if score < 0.90 else "alta",
        "gap": 0.08,
        "consistency": 2,
        "image_count": 1,
    }


class IdentifyRouteVisualV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(server.app)

    def setUp(self):
        clear_cache()
        server._dish_name_cache.clear()

    def _post(self, index, image_bytes, evidence=None):
        data = {"restaurant": "cibi_sana"}
        if evidence is not None:
            data["variant_evidence_json"] = json.dumps(
                evidence, ensure_ascii=False
            )
        with (
            patch("ai.index.get_index", return_value=index),
            patch.object(server, "db", _FakeDatabase()),
            patch.object(server, "get_setting", _disabled_setting),
            patch.object(server, "lookup_nutrition_sheet", _no_nutrition),
        ):
            response = self.client.post(
                "/api/ai/identify",
                files={"file": ("synthetic.jpg", image_bytes, "image/jpeg")},
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def _v2_index(self, class_id="maminha_molho_claro", class_name="Maminha Molho Claro"):
        return _FakeIndex(
            _artifacts(2, class_id, class_name),
            [_result(class_name), _result("Maminha Molho Escuro", 0.74)],
        )

    def test_v1_valid_request_preserves_legacy_response(self):
        index = _FakeIndex(
            _artifacts(1, "arrozbranco", "arrozbranco"),
            [_result("arrozbranco", 0.91)],
        )
        body = self._post(index, b"legacy-image")
        self.assertEqual(body["dish"], "arrozbranco")
        self.assertEqual(body["dish_display"], "Arroz Branco")
        self.assertEqual(body["score"], 0.91)
        self.assertEqual(body["confidence"], "alta")
        self.assertNotIn("recognition_schema_version", body)
        self.assertNotIn("visual_class", body)
        self.assertNotIn("display_variant", body)

    def test_v2_without_variant_returns_raw_top1_family(self):
        index = self._v2_index()
        body = self._post(index, b"v2-family-only")
        self.assertEqual(
            body["visual_class"],
            {"id": "maminha_molho_claro", "name": "Maminha Molho Claro"},
        )
        self.assertIsNone(body["display_variant"])
        self.assertEqual(body["dish"], "Maminha Molho Claro")
        self.assertEqual(body["dish_display"], "Maminha Molho Claro")
        self.assertEqual(body["score"], 0.82)
        self.assertEqual(body["confidence"], "media")

    def test_v2_cibi_sana_remains_openclip_only(self):
        index = self._v2_index()
        with patch(
            "services.gemini_flash_service.identify_dish_gemini_flash",
            new_callable=AsyncMock,
        ) as gemini:
            body = self._post(index, b"v2-cibi-openclip-only")
        self.assertEqual(body["source"], "local_index")
        self.assertEqual(index.search_calls, 1)
        gemini.assert_not_awaited()

    def test_v2_structured_metadata_resolves_variant(self):
        index = self._v2_index()
        body = self._post(
            index,
            b"v2-metadata",
            {
                "structured_metadata": {
                    "value": "Mostarda",
                    "evidence_id": "menu-slot-1",
                }
            },
        )
        self.assertEqual(body["display_variant"], "Mostarda")
        self.assertEqual(body["variant_source"], "structured_metadata")
        self.assertEqual(
            body["dish_display"], "Maminha Molho Claro — Mostarda"
        )

    def test_v2_exact_ocr_resolves_variant(self):
        index = self._v2_index()
        body = self._post(
            index,
            b"v2-ocr",
            {"ocr": {"value": "Gorgonzola", "evidence_id": "ocr-1"}},
        )
        self.assertEqual(body["display_variant"], "Gorgonzola")
        self.assertEqual(body["variant_source"], "ocr")

    def test_v2_conflict_keeps_family_without_variant(self):
        index = self._v2_index()
        body = self._post(
            index,
            b"v2-conflict",
            {
                "structured_metadata": {"value": "Mostarda"},
                "ocr": {"value": "Gorgonzola"},
            },
        )
        self.assertIsNone(body["display_variant"])
        self.assertEqual(body["variant_status"], "conflict")
        self.assertEqual(body["dish_display"], "Maminha Molho Claro")

    def test_v2_cache_hit_recomputes_variant_without_leak(self):
        index = self._v2_index()
        first = self._post(
            index,
            b"same-route-image",
            {"structured_metadata": {"value": "Mostarda"}},
        )
        second = self._post(
            index,
            b"same-route-image",
            {"structured_metadata": {"value": "Gorgonzola"}},
        )
        self.assertEqual(first["display_variant"], "Mostarda")
        self.assertFalse(first["from_visual_cache"])
        self.assertEqual(second["display_variant"], "Gorgonzola")
        self.assertTrue(second["from_visual_cache"])
        self.assertEqual(index.search_calls, 1)
        self.assertEqual(first["score"], second["score"])
        self.assertEqual(first["confidence"], second["confidence"])

    def test_berinjela_is_never_file_parmegiana_variant(self):
        index = self._v2_index("file_a_parmegiana", "Filé à Parmegiana")
        body = self._post(
            index,
            b"v2-parmegiana",
            {"structured_metadata": {"value": "Berinjela à Parmegiana"}},
        )
        self.assertIsNone(body["display_variant"])
        self.assertEqual(body["variant_status"], "unsupported")
        self.assertEqual(body["dish_display"], "Filé à Parmegiana")

    def test_light_and_dark_maminha_do_not_cross(self):
        light = self._v2_index()
        light_body = self._post(
            light,
            b"v2-light",
            {"structured_metadata": {"value": "Madeira"}},
        )
        clear_cache()
        dark = self._v2_index(
            "maminha_molho_escuro", "Maminha Molho Escuro"
        )
        dark_body = self._post(
            dark,
            b"v2-dark",
            {"structured_metadata": {"value": "Madeira"}},
        )
        self.assertIsNone(light_body["display_variant"])
        self.assertEqual(light_body["visual_class"]["id"], "maminha_molho_claro")
        self.assertEqual(dark_body["display_variant"], "Madeira")
        self.assertEqual(dark_body["visual_class"]["id"], "maminha_molho_escuro")


class DishIndexSchemaIntegrationTest(unittest.TestCase):
    def _load_with(self, artifacts):
        with tempfile.TemporaryDirectory() as directory:
            index_path = Path(directory) / "synthetic.json"
            embeddings_path = Path(directory) / "synthetic_embeddings.npy"
            index_path.write_text("{}", encoding="utf-8")
            np.save(embeddings_path, artifacts.embeddings)
            with patch("ai.index.load_index_artifacts", return_value=artifacts):
                return DishIndex(index_file=str(index_path))

    def test_dish_index_uses_declared_v1_schema(self):
        index = self._load_with(_artifacts(1, "arrozbranco", "arrozbranco"))
        self.assertEqual(index.recognition_schema_version, 1)
        self.assertEqual(index.dishes, ["arrozbranco"])

    def test_dish_index_uses_declared_v2_schema(self):
        index = self._load_with(
            _artifacts(2, "maminha_molho_claro", "Maminha Molho Claro")
        )
        self.assertEqual(index.recognition_schema_version, 2)
        self.assertEqual(index.dishes, ["Maminha Molho Claro"])
        self.assertIsNotNone(index.loaded_artifacts)


if __name__ == "__main__":
    unittest.main()
