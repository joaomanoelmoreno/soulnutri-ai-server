# -*- coding: utf-8 -*-
"""Synthetic integration tests for the backend v1/v2 response boundary."""

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from ai.families import (  # noqa: E402
    VariantEvidence,
    collect_variant_evidence,
    load_visual_taxonomy,
)
from ai.index_builder_v2 import (  # noqa: E402
    BUILDER_VERSION,
    BuilderContext,
    EMBEDDING_DIM,
    ImageReference,
    build_v2_index_structure,
    select_deterministic_references,
)
from ai.index_loader import load_index_artifacts  # noqa: E402
from ai.recognition_response import (  # noqa: E402
    RecognitionResponseIntegrationError,
    assemble_identification_response,
)


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class BackendVisualResponseIntegrationTest(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.taxonomy = load_visual_taxonomy()
        self.v1 = self._load_v1()
        self.v2 = self._load_v2()

    def tearDown(self):
        self._temporary.cleanup()

    def _write_pair(self, stem, payload, embeddings):
        index_path = self.root / f"{stem}.json"
        embeddings_path = self.root / f"{stem}_embeddings.npy"
        np.save(embeddings_path, np.asarray(embeddings, dtype=np.float32))
        index_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return index_path, embeddings_path

    def _load_v1(self):
        payload = {
            "dishes": ["Arroz Branco"],
            "dish_to_idx": {"Arroz Branco": [0]},
            "metadata": {"Arroz Branco": {"image_count": 1}},
            "version": "1.0",
            "total_items": 1,
            "total_dishes": 1,
        }
        index_path, embeddings_path = self._write_pair(
            "legacy", payload, [[0.1] * EMBEDDING_DIM]
        )
        return load_index_artifacts(index_path, embeddings_path)

    def _reference(self, class_id, class_name, token, variant_id):
        return ImageReference(
            visual_class_id=class_id,
            visual_class=class_name,
            source_relative_path=f"{class_name}/{token}.jpg",
            source_filename=f"{token}.jpg",
            source_sha256=_sha(token),
            source_bytes=len(token),
            source_variant_id=variant_id,
            source_variant_status=(
                "reference_annotation" if variant_id is not None else None
            ),
            source_variant_source=(
                "human_manifest" if variant_id is not None else None
            ),
            original_class=class_name,
            human_decision_refs=("REV-TEST",),
        )

    def _load_v2(self):
        references = [
            self._reference(
                "maminha_molho_claro",
                "Maminha Molho Claro",
                "claro",
                "mostarda",
            ),
            self._reference(
                "maminha_molho_escuro",
                "Maminha Molho Escuro",
                "escuro",
                "madeira",
            ),
            self._reference(
                "file_a_parmegiana",
                "Filé à Parmegiana",
                "parmegiana",
                "frango",
            ),
            self._reference(
                "vol_au_vent",
                "Vol Au Vent",
                "vol-au-vent",
                None,
            ),
        ]
        selection = select_deterministic_references(
            references, self.taxonomy, max_per_visual_class=10
        )
        embeddings = [
            [0.1 + (index * 0.01)] * EMBEDDING_DIM
            for index in range(len(selection.references))
        ]
        embeddings_path = self.root / "candidate_embeddings.npy"
        np.save(embeddings_path, np.asarray(embeddings, dtype=np.float32))
        context = BuilderContext(
            index_id="visual-index-response-test",
            recognition_schema_version=2,
            builder_version=BUILDER_VERSION,
            preprocessing_version="clip-test-v1",
            model_identifier="ViT-B-16",
            model_version="test-model-v1",
            model_sha256="a" * 64,
            source_corpus_id="P0_CANDIDATE_TEST",
            source_corpus_version="test-v1",
            source_corpus_manifest_sha256="b" * 64,
            taxonomy_sha256="c" * 64,
            embeddings_sha256=hashlib.sha256(
                embeddings_path.read_bytes()
            ).hexdigest(),
        )
        payload = build_v2_index_structure(
            selection, embeddings, self.taxonomy, context
        )
        index_path = self.root / "candidate.json"
        index_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return load_index_artifacts(
            index_path, embeddings_path, taxonomy=self.taxonomy
        )

    @staticmethod
    def _decision(dish, score=0.8123, confidence="media"):
        return {
            "ok": True,
            "identified": True,
            "dish": dish,
            "dish_display": dish,
            "score": score,
            "confidence": confidence,
            "message": "Provável identificação.",
            "source": "local_index",
            "alternatives": [],
        }

    def test_v1_legacy_response_is_field_for_field_unchanged(self):
        decision = self._decision("Arroz Branco", 0.91, "alta")
        result = assemble_identification_response(decision, self.v1)
        self.assertEqual(result, decision)
        self.assertIsNot(result, decision)
        self.assertNotIn("recognition_schema_version", result)
        self.assertNotIn("visual_class", result)

    def test_v2_without_evidence_returns_family_and_null_variant(self):
        decision = self._decision("Maminha Molho Claro")
        result = assemble_identification_response(
            decision, self.v2, taxonomy=self.taxonomy
        )
        self.assertEqual(
            result["visual_class"],
            {"id": "maminha_molho_claro", "name": "Maminha Molho Claro"},
        )
        self.assertIsNone(result["display_variant"])
        self.assertIsNone(result["variant_source"])
        self.assertEqual(result["variant_status"], "absent")
        self.assertEqual(result["dish_display"], "Maminha Molho Claro")

    def test_v2_standalone_class_preserves_provenance_without_variant(self):
        decision = self._decision("Vol Au Vent", 1.0, "alta")
        evidence = collect_variant_evidence(
            structured_metadata="unconfigured value"
        )
        result = assemble_identification_response(
            decision, self.v2, evidence=evidence, taxonomy=self.taxonomy
        )
        self.assertEqual(
            result["visual_class"],
            {"id": "vol_au_vent", "name": "Vol Au Vent"},
        )
        self.assertIsNone(result["display_variant"])
        self.assertIsNone(result["variant_source"])
        self.assertEqual(result["variant_status"], "unconfigured")
        self.assertEqual(
            result["variant_reason"], "visual_class_has_no_variant_taxonomy"
        )
        self.assertEqual(result["dish"], "Vol Au Vent")
        self.assertEqual(result["dish_display"], "Vol Au Vent")
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["confidence"], "alta")

    def test_v2_valid_metadata_returns_family_and_variant(self):
        decision = self._decision("Maminha Molho Claro")
        evidence = collect_variant_evidence(
            structured_metadata="Mostarda",
            evidence_ids={"structured_metadata": "menu-slot-1"},
        )
        result = assemble_identification_response(
            decision, self.v2, evidence=evidence, taxonomy=self.taxonomy
        )
        self.assertEqual(result["display_variant"], "Mostarda")
        self.assertEqual(result["variant_source"], "structured_metadata")
        self.assertEqual(result["variant_status"], "confirmed")
        self.assertEqual(result["variant_evidence_id"], "menu-slot-1")
        self.assertEqual(
            result["dish_display"], "Maminha Molho Claro — Mostarda"
        )

    def test_v2_explicit_admin_evidence_uses_same_response_contract(self):
        evidence = collect_variant_evidence(human_admin="Gorgonzola")
        result = assemble_identification_response(
            self._decision("Maminha Molho Claro"),
            self.v2,
            evidence=evidence,
            taxonomy=self.taxonomy,
        )
        self.assertEqual(result["display_variant"], "Gorgonzola")
        self.assertEqual(result["variant_source"], "human_admin")

    def test_v2_exact_ocr_evidence_uses_same_response_contract(self):
        evidence = collect_variant_evidence(ocr="Cerveja Preta")
        result = assemble_identification_response(
            self._decision("Maminha Molho Escuro"),
            self.v2,
            evidence=evidence,
            taxonomy=self.taxonomy,
        )
        self.assertEqual(result["display_variant"], "Cerveja Preta")
        self.assertEqual(result["variant_source"], "ocr")

    def test_conflict_keeps_family_and_returns_null_variant(self):
        evidence = collect_variant_evidence(
            structured_metadata="Mostarda", ocr="Gorgonzola"
        )
        result = assemble_identification_response(
            self._decision("Maminha Molho Claro"),
            self.v2,
            evidence=evidence,
            taxonomy=self.taxonomy,
        )
        self.assertIsNone(result["display_variant"])
        self.assertIsNone(result["variant_source"])
        self.assertEqual(result["variant_status"], "conflict")
        self.assertEqual(result["dish"], "Maminha Molho Claro")
        self.assertEqual(result["dish_display"], "Maminha Molho Claro")

    def test_score_and_confidence_are_identical_for_all_variant_outcomes(self):
        decision = self._decision("Maminha Molho Claro", 0.8491, "media")
        cases = (
            (),
            collect_variant_evidence(structured_metadata="Mostarda"),
            collect_variant_evidence(
                structured_metadata="Mostarda", ocr="Gorgonzola"
            ),
        )
        for evidence in cases:
            with self.subTest(evidence=evidence):
                result = assemble_identification_response(
                    decision,
                    self.v2,
                    evidence=evidence,
                    taxonomy=self.taxonomy,
                )
                self.assertEqual(result["score"], 0.8491)
                self.assertEqual(result["confidence"], "media")

    def test_berinjela_is_not_a_file_parmegiana_variant(self):
        evidence = collect_variant_evidence(
            structured_metadata="Berinjela à Parmegiana"
        )
        result = assemble_identification_response(
            self._decision("Filé à Parmegiana"),
            self.v2,
            evidence=evidence,
            taxonomy=self.taxonomy,
        )
        self.assertIsNone(result["display_variant"])
        self.assertEqual(result["variant_status"], "unsupported")
        self.assertEqual(result["variant_reason"], "excluded_variant_evidence")

    def test_light_and_dark_maminha_remain_distinct(self):
        light = assemble_identification_response(
            self._decision("Maminha Molho Claro"),
            self.v2,
            evidence=collect_variant_evidence(structured_metadata="Madeira"),
            taxonomy=self.taxonomy,
        )
        dark = assemble_identification_response(
            self._decision("Maminha Molho Escuro"),
            self.v2,
            evidence=collect_variant_evidence(structured_metadata="Madeira"),
            taxonomy=self.taxonomy,
        )
        self.assertIsNone(light["display_variant"])
        self.assertEqual(light["variant_status"], "unsupported")
        self.assertEqual(dark["display_variant"], "Madeira")
        self.assertEqual(dark["visual_class"]["id"], "maminha_molho_escuro")

    def test_openclip_evidence_cannot_select_variant(self):
        evidence = (
            VariantEvidence("openclip", ("Mostarda",), "visual-top1"),
        )
        result = assemble_identification_response(
            self._decision("Maminha Molho Claro"),
            self.v2,
            evidence=evidence,
            taxonomy=self.taxonomy,
        )
        self.assertIsNone(result["display_variant"])
        self.assertEqual(result["variant_status"], "unsupported")

    def test_declared_visual_class_conflict_fails_closed(self):
        decision = self._decision("Maminha Molho Claro")
        decision["visual_class"] = {
            "id": "maminha_molho_escuro",
            "name": "Maminha Molho Claro",
        }
        with self.assertRaisesRegex(
            RecognitionResponseIntegrationError, "conflicts with index provenance"
        ):
            assemble_identification_response(
                decision, self.v2, taxonomy=self.taxonomy
            )

    def test_configured_family_name_mismatch_still_fails_closed(self):
        inconsistent_taxonomy = copy.deepcopy(self.taxonomy)
        for family in inconsistent_taxonomy["families"]:
            if family["visual_class_id"] == "maminha_molho_claro":
                family["canonical_name"] = "Maminha Clara Inconsistente"
                break
        with self.assertRaisesRegex(
            RecognitionResponseIntegrationError,
            "visual class is inconsistent with the loaded taxonomy",
        ):
            assemble_identification_response(
                self._decision("Maminha Molho Claro"),
                self.v2,
                taxonomy=inconsistent_taxonomy,
            )

    def test_v2_response_includes_versioned_optional_metadata(self):
        result = assemble_identification_response(
            self._decision("Filé à Parmegiana"),
            self.v2,
            taxonomy=self.taxonomy,
        )
        self.assertEqual(result["recognition_schema_version"], 2)
        self.assertEqual(result["index_version"], "visual-index-response-test")
        self.assertEqual(
            result["taxonomy_version"], "visual-family-initial-3-v1"
        )


if __name__ == "__main__":
    unittest.main()
