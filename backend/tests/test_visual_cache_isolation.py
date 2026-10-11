# -*- coding: utf-8 -*-
"""Tests for the isolated, versioned visual-decision cache."""

import sys
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from ai.families import collect_variant_evidence, load_visual_taxonomy  # noqa: E402
from ai.index_loader import LoadedIndexArtifacts  # noqa: E402
from ai.recognition_response import (  # noqa: E402
    assemble_identification_response,
    assemble_identification_response_with_visual_cache,
)
from services.cache_service import (  # noqa: E402
    VisualCacheContext,
    _visual_decision_cache,
    cache_result,
    cache_visual_decision,
    clear_cache,
    get_cached_result,
    get_cached_visual_decision,
    get_image_hash,
    get_visual_cache_key,
)


class VisualCacheIsolationTest(unittest.TestCase):
    def setUp(self):
        clear_cache()
        self.taxonomy = load_visual_taxonomy()
        embeddings = np.asarray([[0.1] * 512], dtype=np.float32)
        embeddings.setflags(write=False)
        self.v2 = LoadedIndexArtifacts(
            schema_version=2,
            embeddings=embeddings,
            visual_labels=("Maminha Molho Claro",),
            dish_to_idx={"Maminha Molho Claro": (0,)},
            provenance=(
                {
                    "embedding_index": 0,
                    "visual_class_id": "maminha_molho_claro",
                    "visual_class": "Maminha Molho Claro",
                },
            ),
            legacy_metadata={"Maminha Molho Claro": {"image_count": 1}},
            index_metadata={
                "version": "2.0",
                "index_id": "visual-index-cache-test",
                "model_version": "openclip-test-v1",
                "preprocessing_version": "preprocess-test-v1",
                "taxonomy_version": "visual-family-initial-3-v1",
            },
        )
        self.v1 = LoadedIndexArtifacts(
            schema_version=1,
            embeddings=embeddings,
            visual_labels=("Arroz Branco",),
            dish_to_idx={"Arroz Branco": (0,)},
            provenance=(),
            legacy_metadata={"Arroz Branco": {"image_count": 1}},
            index_metadata={"version": "1.0"},
        )
        self.context = VisualCacheContext(
            schema_version=2,
            index_version="visual-index-cache-test",
            model_version="openclip-test-v1",
            preprocessing_version="preprocess-test-v1",
            taxonomy_version="visual-family-initial-3-v1",
        )
        self.image = b"same-visual-image"

    @staticmethod
    def _decision(confidence="media", score=0.8123, identified=True):
        return {
            "ok": True,
            "identified": identified,
            "dish": "Maminha Molho Claro",
            "dish_display": "Maminha Molho Claro",
            "score": score,
            "confidence": confidence,
            "message": "Provável identificação.",
            "source": "local_index",
            "alternatives": ["Maminha Molho Escuro"],
        }

    def _assembled(self, evidence=()):
        return assemble_identification_response(
            self._decision(),
            self.v2,
            evidence=evidence,
            taxonomy=self.taxonomy,
        )

    def _stored_ttl(self, context=None):
        active_context = context or self.context
        key = get_visual_cache_key(self.image, "cibi_sana", active_context)
        entry = _visual_decision_cache.cache.get(key)
        if entry is None:
            return None
        return int(round(entry["_expires_at"] - entry["_cached_at"]))

    def test_cache_payload_contains_visual_identity_not_display_variant(self):
        result = self._assembled(
            collect_variant_evidence(structured_metadata="Mostarda")
        )
        self.assertTrue(
            cache_visual_decision(
                self.image, result, self.context, restaurant="cibi_sana"
            )
        )
        cached = get_cached_visual_decision(
            self.image, self.context, restaurant="cibi_sana"
        )
        self.assertEqual(
            cached["visual_class"],
            {"id": "maminha_molho_claro", "name": "Maminha Molho Claro"},
        )
        for contextual in (
            "dish",
            "dish_display",
            "display_variant",
            "variant_source",
            "variant_status",
            "variant_reason",
        ):
            self.assertNotIn(contextual, cached)

    def test_variant_source_and_evidence_ids_do_not_persist(self):
        result = self._assembled(
            collect_variant_evidence(
                structured_metadata="Mostarda",
                evidence_ids={"structured_metadata": "menu-slot-1"},
            )
        )
        cache_visual_decision(
            self.image, result, self.context, restaurant="cibi_sana"
        )
        cached = get_cached_visual_decision(
            self.image, self.context, restaurant="cibi_sana"
        )
        self.assertNotIn("variant_source", cached)
        self.assertNotIn("variant_evidence_id", cached)
        self.assertNotIn("variant_evidence_ids", cached)

    def test_contextual_ocr_metadata_and_admin_fields_do_not_persist(self):
        result = self._assembled()
        result.update(
            {
                "ocr": "Mostarda",
                "structured_metadata": {"variant": "Mostarda"},
                "human_admin": "Mostarda",
                "request_context": {"meal": "current"},
            }
        )
        cache_visual_decision(
            self.image, result, self.context, restaurant="cibi_sana"
        )
        cached = get_cached_visual_decision(
            self.image, self.context, restaurant="cibi_sana"
        )
        for forbidden in (
            "ocr",
            "structured_metadata",
            "human_admin",
            "request_context",
        ):
            self.assertNotIn(forbidden, cached)

    def test_same_cached_family_resolves_different_variants_per_request(self):
        first = assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=self._decision(),
            evidence=collect_variant_evidence(structured_metadata="Mostarda"),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        second = assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=None,
            evidence=collect_variant_evidence(structured_metadata="Gorgonzola"),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        self.assertEqual(first["display_variant"], "Mostarda")
        self.assertFalse(first["from_visual_cache"])
        self.assertEqual(second["display_variant"], "Gorgonzola")
        self.assertTrue(second["from_visual_cache"])

    def test_cache_hit_without_evidence_returns_null_variant(self):
        assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=self._decision(),
            evidence=collect_variant_evidence(structured_metadata="Mostarda"),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        result = assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=None,
            evidence=(),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        self.assertIsNone(result["display_variant"])
        self.assertEqual(result["variant_status"], "absent")

    def test_cache_hit_with_conflict_returns_null_variant(self):
        assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=self._decision(),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        result = assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=None,
            evidence=collect_variant_evidence(
                structured_metadata="Mostarda", ocr="Gorgonzola"
            ),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        self.assertIsNone(result["display_variant"])
        self.assertEqual(result["variant_status"], "conflict")

    def test_legacy_v1_response_and_cache_remain_unchanged(self):
        decision = {
            "ok": True,
            "identified": True,
            "dish": "arrozbranco",
            "dish_display": "Arroz Branco",
            "score": 0.91,
            "confidence": "alta",
            "source": "local_index",
        }
        integrated = assemble_identification_response_with_visual_cache(
            self.image, self.v1, decision=decision
        )
        self.assertEqual(integrated, decision)
        cache_result(self.image, decision, restaurant="cibi_sana")
        cached = get_cached_result(self.image, restaurant="cibi_sana")
        self.assertEqual(cached["dish_display"], "Arroz Branco")
        self.assertTrue(cached["from_cache"])

    def test_score_and_confidence_are_identical_across_cache_hit(self):
        first = assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=self._decision(score=0.8491, confidence="media"),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        second = assemble_identification_response_with_visual_cache(
            self.image,
            self.v2,
            decision=None,
            evidence=collect_variant_evidence(structured_metadata="Mostarda"),
            taxonomy=self.taxonomy,
            restaurant="cibi_sana",
        )
        self.assertEqual(first["score"], second["score"])
        self.assertEqual(first["confidence"], second["confidence"])

    def test_legacy_and_v2_keys_do_not_collide(self):
        legacy_key = get_image_hash(self.image, "cibi_sana")
        visual_key = get_visual_cache_key(
            self.image, "cibi_sana", self.context
        )
        self.assertNotEqual(legacy_key, visual_key)
        self.assertTrue(visual_key.startswith("visual:v2:"))

    def test_different_index_versions_do_not_share_cache(self):
        result = self._assembled()
        cache_visual_decision(
            self.image, result, self.context, restaurant="cibi_sana"
        )
        different = replace(self.context, index_version="visual-index-other")
        self.assertIsNone(
            get_cached_visual_decision(
                self.image, different, restaurant="cibi_sana"
            )
        )

    def test_different_model_versions_do_not_share_cache(self):
        result = self._assembled()
        cache_visual_decision(
            self.image, result, self.context, restaurant="cibi_sana"
        )
        different = replace(self.context, model_version="openclip-other")
        self.assertIsNone(
            get_cached_visual_decision(
                self.image, different, restaurant="cibi_sana"
            )
        )

    def test_high_confidence_ttl_remains_3600_seconds(self):
        result = assemble_identification_response(
            self._decision(confidence="alta", score=0.91),
            self.v2,
            taxonomy=self.taxonomy,
        )
        cache_visual_decision(
            self.image, result, self.context, restaurant="cibi_sana"
        )
        self.assertEqual(self._stored_ttl(), 3600)

    def test_medium_confidence_ttl_remains_300_seconds(self):
        cache_visual_decision(
            self.image,
            self._assembled(),
            self.context,
            restaurant="cibi_sana",
        )
        self.assertEqual(self._stored_ttl(), 300)

    def test_low_confidence_is_not_cached(self):
        result = assemble_identification_response(
            self._decision(confidence="baixa", score=0.49),
            self.v2,
            taxonomy=self.taxonomy,
        )
        self.assertFalse(
            cache_visual_decision(
                self.image, result, self.context, restaurant="cibi_sana"
            )
        )
        self.assertIsNone(self._stored_ttl())

    def test_not_identified_is_not_cached(self):
        result = self._decision(confidence="baixa", score=0.1, identified=False)
        result.update(
            {
                "recognition_schema_version": 2,
                "visual_class": {
                    "id": "maminha_molho_claro",
                    "name": "Maminha Molho Claro",
                },
            }
        )
        self.assertFalse(
            cache_visual_decision(
                self.image, result, self.context, restaurant="cibi_sana"
            )
        )
        self.assertIsNone(self._stored_ttl())


if __name__ == "__main__":
    unittest.main()
