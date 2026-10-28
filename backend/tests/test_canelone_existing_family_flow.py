# -*- coding: utf-8 -*-
"""Regression coverage for Canelone using the existing family enrichment flow."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
PLAN_PATH = (
    REPO_ROOT
    / "experiments"
    / "canelone_existing_family_flow_2026-10-28"
    / "canelone_family_registration_plan.json"
)
sys.path.insert(0, str(BACKEND_DIR))

import server  # noqa: E402
from ai.index_loader import LoadedIndexArtifacts  # noqa: E402
from services.cache_service import cache_result, clear_cache  # noqa: E402


PLAN = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
FAMILY = PLAN["family_upsert"]["set"]
MEMBER_SLUGS = set(FAMILY["members_slugs"])


class _DishesCollection:
    async def find_one(self, query, projection=None):
        if "$or" in query:
            return {
                "category": "Vegetariano",
                "ingredients": ["massa", "molho"],
            }
        slug = query.get("slug")
        if slug in MEMBER_SLUGS:
            return {"family": FAMILY["slug"]}
        if slug == "pastel":
            return {"family": "pasteis"}
        if slug == "brocolisgratinado":
            return {"family": "gratinados"}
        return None


class _FamiliesCollection:
    async def find_one(self, query, _projection=None):
        if query.get("slug") == FAMILY["slug"]:
            return dict(FAMILY)
        if query.get("slug") == "pasteis":
            return {
                "slug": "pasteis",
                "name": "Pastéis",
                "members_display": ["Pastel"],
                "members_slugs": ["pastel"],
            }
        if query.get("slug") == "gratinados":
            return {
                "slug": "gratinados",
                "name": "Gratinados",
                "members_display": ["Brócolis Gratinado", "Couve-flor Gratinada"],
                "members_slugs": ["brocolisgratinado", "couveflorgratinada"],
            }
        return None


class _EmptyCollection:
    async def find_one(self, *_args, **_kwargs):
        return None


class _FailingCollection:
    async def find_one(self, *_args, **_kwargs):
        raise RuntimeError("mongo unavailable")

    async def update_one(self, *_args, **_kwargs):
        raise AssertionError("no write is allowed")


class _MissingFamilyDatabase:
    dishes = _DishesCollection()
    dish_families = _EmptyCollection()
    users = _EmptyCollection()


class _FailingDatabase:
    dishes = _FailingCollection()
    dish_families = _FailingCollection()
    users = _FailingCollection()
    daily_logs = _FailingCollection()


class _InconsistentFamiliesCollection:
    async def find_one(self, query, _projection=None):
        if query.get("slug") == FAMILY["slug"]:
            return {
                "slug": FAMILY["slug"],
                "name": "Canelone inconsistente",
                "members_display": ["Canelone de Espinafre"],
                "members_slugs": [],
                # Flag deliberadamente ausente.
            }
        return None


class _InconsistentFamilyDatabase:
    dishes = _DishesCollection()
    dish_families = _InconsistentFamiliesCollection()
    users = _EmptyCollection()


class _PremiumUsersCollection:
    async def find_one(self, *_args, **_kwargs):
        return {"nome": "Teste", "premium_ativo": True}


class _PremiumDatabase:
    dishes = _DishesCollection()
    dish_families = _FamiliesCollection()
    users = _PremiumUsersCollection()


class _FakeDatabase:
    dishes = _DishesCollection()
    dish_families = _FamiliesCollection()
    users = _EmptyCollection()


class _FakeIndex:
    def __init__(self, dish, score=0.91):
        embeddings = np.asarray([[0.1] * 512], dtype=np.float32)
        embeddings.setflags(write=False)
        self.loaded_artifacts = LoadedIndexArtifacts(
            schema_version=2,
            embeddings=embeddings,
            visual_labels=(dish,),
            dish_to_idx={dish: (0,)},
            provenance=(
                {
                    "embedding_index": 0,
                    "visual_class_id": dish,
                    "visual_class": dish,
                },
            ),
            legacy_metadata={dish: {"image_count": 1}},
            index_metadata={
                "version": "2.0",
                "index_id": "synthetic-canelone-family",
                "model_version": "openclip-synthetic-v1",
                "preprocessing_version": "preprocess-synthetic-v1",
                "taxonomy_version": "visual-family-initial-3-v1",
            },
        )
        self.results = [
            {
                "dish": dish,
                "score": score,
                "raw_score": score,
                "confidence": "alta" if score >= 0.90 else "media",
                "gap": 0.08,
                "consistency": 2,
                "image_count": 1,
            }
        ]

    def is_ready(self):
        return True

    def search(self, _content, _top_k):
        return [dict(row) for row in self.results]


class _LegacyCacheOnlyIndex:
    loaded_artifacts = None

    def is_ready(self):
        return True

    def search(self, *_args, **_kwargs):
        raise AssertionError("legacy response cache should short-circuit search")


async def _disabled_setting(*_args, **_kwargs):
    return False


async def _nutrition_for_recognized_name(dish_name):
    calories = 111 if dish_name == "canelonedeespinafre" else 222
    return {
        "calorias_kcal": calories,
        "proteinas_g": 10.0,
        "carboidratos_g": 20.0,
        "gorduras_g": 5.0,
        "fonte": f"fixture:{dish_name}",
    }


class CaneloneExistingFamilyFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(server.app)

    def setUp(self):
        clear_cache()
        server._dish_name_cache.clear()

    def _post(self, dish, score=0.91, database=None, extra_data=None):
        index = _FakeIndex(dish, score=score)
        with (
            patch("ai.index.get_index", return_value=index),
            patch.object(server, "db", database or _FakeDatabase()),
            patch.object(server, "get_setting", _disabled_setting),
            patch.object(
                server,
                "lookup_nutrition_sheet",
                _nutrition_for_recognized_name,
            ),
        ):
            response = self.client.post(
                "/api/ai/identify",
                files={"file": ("fixture.jpg", b"fixture", "image/jpeg")},
                data={"restaurant": "cibi_sana", **(extra_data or {})},
            )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_spinach_top1_uses_existing_family_block_contract(self):
        body = self._post("canelonedeespinafre")
        self.assertEqual(body["dish"], "canelonedeespinafre")
        self.assertEqual(body["dish_display"], "Canelone")
        self.assertEqual(body["visual_class"]["id"], "canelonedeespinafre")
        self.assertEqual(body["family_name"], "Canelone")
        self.assertEqual(body["family_candidates"], FAMILY["members_display"])
        self.assertIsNone(body["display_variant"])
        self.assertTrue(body["family_member_confirmation_required"])
        self.assertFalse(body["family_member_confirmed"])

    def test_old_client_contract_never_receives_member_specific_data(self):
        body = self._post("canelonedeespinafre")
        self.assertEqual(body["dish_display"], "Canelone")
        self.assertIsNone(body["nutrition"])
        self.assertEqual(body["ingredientes"], [])
        self.assertEqual(body["beneficios"], [])
        self.assertEqual(body["riscos"], [])
        self.assertEqual(body["alergenos"], {})
        self.assertIsNone(body["descricao"])
        self.assertIsNone(body["tecnica"])
        self.assertIn("Familia visual", body["message"])

    def test_four_cheese_top1_withholds_specific_nutrition_until_confirmation(self):
        body = self._post("canelone4queijos")
        self.assertEqual(body["dish"], "canelone4queijos")
        self.assertEqual(body["family_candidates"], FAMILY["members_display"])
        self.assertIsNone(body["nutrition"])
        self.assertFalse(body["specific_nutrition_authorized"])
        self.assertEqual(
            body["nutrition_status"],
            "withheld_pending_family_member_confirmation",
        )

    def test_wrong_variant_inside_family_does_not_expose_its_nutrition(self):
        body = self._post("canelonedeespinafre")
        self.assertEqual(body["family_candidates"], FAMILY["members_display"])
        self.assertIsNone(body["nutrition"])
        self.assertEqual(body["ingredientes"], [])
        self.assertEqual(body["beneficios"], [])
        self.assertEqual(body["riscos"], [])

    def test_mongo_unavailable_fails_closed_for_known_canelone(self):
        body = self._post("canelonedeespinafre", database=_FailingDatabase())
        self.assertEqual(body["family_name"], "Canelone")
        self.assertEqual(body["family_candidates"], FAMILY["members_display"])
        self.assertEqual(body["dish_display"], "Canelone")
        self.assertIsNone(body["nutrition"])
        self.assertFalse(body["specific_nutrition_authorized"])

    def test_missing_family_document_fails_closed_for_known_canelone(self):
        body = self._post(
            "canelone4queijos",
            database=_MissingFamilyDatabase(),
        )
        self.assertEqual(body["family_name"], "Canelone")
        self.assertEqual(body["family_candidates"], FAMILY["members_display"])
        self.assertIsNone(body["nutrition"])
        self.assertFalse(body["specific_nutrition_authorized"])

    def test_inconsistent_family_and_missing_flag_fail_closed(self):
        body = self._post(
            "canelonedeespinafre",
            database=_InconsistentFamilyDatabase(),
        )
        self.assertEqual(body["family_name"], "Canelone")
        self.assertEqual(body["family_candidates"], FAMILY["members_display"])
        self.assertEqual(body["family_members_slugs"], FAMILY["members_slugs"])
        self.assertFalse(body["specific_nutrition_authorized"])

    def test_visual_cache_hit_reapplies_fail_closed_safety(self):
        first = self._post("canelonedeespinafre", database=_FailingDatabase())
        second = self._post("canelonedeespinafre", database=_FailingDatabase())
        self.assertFalse(first.get("from_visual_cache", False))
        self.assertTrue(second["from_visual_cache"])
        self.assertEqual(second["dish_display"], "Canelone")
        self.assertIsNone(second["nutrition"])
        self.assertFalse(second["specific_nutrition_authorized"])

    def test_legacy_response_cache_is_sanitized_before_old_client_receives_it(self):
        cache_result(
            b"fixture",
            {
                "ok": True,
                "identified": True,
                "dish": "canelonedeespinafre",
                "dish_display": "Canelone de Espinafre",
                "confidence": "alta",
                "score": 0.91,
                "message": "Identificado: Canelone de Espinafre",
                "nutrition": {"calorias": "111 kcal"},
                "ingredientes": ["espinafre"],
                "alergenos": {"lactose": True},
                "premium": {"alertas_alergenos": ["lactose"]},
            },
            restaurant="cibi_sana",
        )
        with (
            patch("ai.index.get_index", return_value=_LegacyCacheOnlyIndex()),
            patch.object(server, "db", _FailingDatabase()),
            patch.object(server, "get_setting", _disabled_setting),
        ):
            response = self.client.post(
                "/api/ai/identify",
                files={"file": ("fixture.jpg", b"fixture", "image/jpeg")},
                data={"restaurant": "cibi_sana"},
            )
        body = response.json()
        self.assertEqual(body["dish_display"], "Canelone")
        self.assertIsNone(body["nutrition"])
        self.assertEqual(body["ingredientes"], [])
        self.assertEqual(body["alergenos"], {})
        self.assertFalse(body["specific_nutrition_authorized"])

    def test_premium_identify_does_not_return_member_enrichment(self):
        body = self._post(
            "canelonedeespinafre",
            database=_PremiumDatabase(),
            extra_data={"pin": "1234", "nome": "Teste"},
        )
        self.assertTrue(body["is_premium"])
        self.assertEqual(body["dish_display"], "Canelone")
        self.assertIsNone(body["nutrition"])
        self.assertEqual(body["premium"], {})
        self.assertEqual(body["alertas_personalizados"], [])

    def test_enrich_route_blocks_known_unconfirmed_member_before_paid_work(self):
        with patch.object(server, "db", _FailingDatabase()):
            response = self.client.post(
                "/api/ai/enrich",
                json={
                    "nome": "Canelone de Espinafre",
                    "ingredientes": ["espinafre"],
                    "pin": "1234",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["error"], "family_member_confirmation_required")

    def test_log_meal_blocks_known_unconfirmed_family_before_database_write(self):
        with patch.object(server, "db", _FailingDatabase()):
            response = self.client.post(
                "/api/premium/log-meal",
                data={
                    "pin": "1234",
                    "prato_nome": "Canelone",
                    "calorias": "200",
                    "proteinas": "10",
                    "carboidratos": "20",
                    "gorduras": "5",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["error"], "family_member_confirmation_required")

    def test_other_pasta_does_not_receive_canelone_family(self):
        body = self._post("Nhoque ao Sugo")
        self.assertIsNone(body.get("family_name"))
        self.assertEqual(body.get("family_candidates"), [])
        self.assertEqual(body["nutrition"]["calorias_kcal"], 222)
        self.assertTrue(body["specific_nutrition_authorized"])

    def test_rejected_result_does_not_receive_family(self):
        body = self._post("canelonedeespinafre", score=0.71)
        self.assertFalse(body["identified"])
        self.assertIsNone(body.get("family_name"))
        self.assertEqual(body.get("family_candidates"), [])

    def test_existing_pastel_family_uses_the_same_unmodified_path(self):
        body = self._post("pastel")
        self.assertEqual(body["family_name"], "Pastéis")
        self.assertEqual(body["family_candidates"], ["Pastel"])
        self.assertEqual(body["nutrition"]["calorias_kcal"], 222)
        self.assertFalse(body["family_member_confirmation_required"])
        self.assertTrue(body["specific_nutrition_authorized"])

    def test_existing_gratinados_family_uses_the_same_unmodified_path(self):
        body = self._post("brocolisgratinado")
        self.assertEqual(body["family_name"], "Gratinados")
        self.assertEqual(
            body["family_candidates"],
            ["Brócolis Gratinado", "Couve-flor Gratinada"],
        )
        self.assertEqual(body["nutrition"]["calorias_kcal"], 222)
        self.assertFalse(body["family_member_confirmation_required"])
        self.assertTrue(body["specific_nutrition_authorized"])


if __name__ == "__main__":
    unittest.main()
