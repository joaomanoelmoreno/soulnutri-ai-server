# -*- coding: utf-8 -*-
"""Compatibility tests for the isolated v1/v2 index artifact loader."""

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

from ai.families import load_visual_taxonomy  # noqa: E402
from ai.index_builder_v2 import (  # noqa: E402
    BUILDER_VERSION,
    BuilderContext,
    EMBEDDING_DIM,
    ImageReference,
    build_v2_index_structure,
    select_deterministic_references,
)
from ai.index_loader import (  # noqa: E402
    IndexArtifactValidationError,
    load_index_artifacts,
)


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class IndexLoaderCompatibilityTest(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.taxonomy = load_visual_taxonomy()

    def tearDown(self):
        self._temporary.cleanup()

    def _write_json(self, path, payload):
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _legacy_fixture(self):
        index_path = self.root / "legacy.json"
        embeddings_path = self.root / "legacy_embeddings.npy"
        embeddings = np.array(
            [
                [0.1] * EMBEDDING_DIM,
                [0.2] * EMBEDDING_DIM,
                [0.3] * EMBEDDING_DIM,
            ],
            dtype=np.float32,
        )
        np.save(embeddings_path, embeddings)
        payload = {
            "dishes": ["Arroz Branco", "Arroz Branco", "Feijão"],
            "dish_to_idx": {"Arroz Branco": [0, 1], "Feijão": [2]},
            "metadata": {
                "Arroz Branco": {"image_count": 2},
                "Feijão": {"image_count": 1},
            },
            "version": "1.0",
            "total_items": 3,
            "total_dishes": 2,
        }
        self._write_json(index_path, payload)
        return index_path, embeddings_path, payload

    def _reference(self, token, variant_id):
        return ImageReference(
            visual_class_id="maminha_molho_claro",
            visual_class="Maminha Molho Claro",
            source_relative_path=f"Maminha Molho Claro/{token}.jpg",
            source_filename=f"{token}.jpg",
            source_sha256=_sha(token),
            source_bytes=len(token.encode("utf-8")),
            source_variant_id=variant_id,
            source_variant_status="reference_annotation",
            source_variant_source="human_manifest",
            original_class="Maminha Molho Claro",
            human_decision_refs=("REV-TEST",),
        )

    def _v2_fixture_for_references(self, references, stem="candidate"):
        index_path = self.root / f"{stem}.json"
        embeddings_path = self.root / f"{stem}_embeddings.npy"
        selection = select_deterministic_references(
            references, self.taxonomy, max_per_visual_class=10
        )
        embeddings = np.array(
            [
                [float(index + 1)] * EMBEDDING_DIM
                for index in range(len(selection.references))
            ],
            dtype=np.float32,
        )
        np.save(embeddings_path, embeddings)
        embeddings_sha = hashlib.sha256(embeddings_path.read_bytes()).hexdigest()
        context = BuilderContext(
            index_id="visual-index-loader-test",
            recognition_schema_version=2,
            builder_version=BUILDER_VERSION,
            preprocessing_version="clip-vit-b16-soulnutri-v1",
            model_identifier="ViT-B-16",
            model_version="datacomp_xl_s13b_b90k",
            model_sha256="a" * 64,
            source_corpus_id="P0_CANDIDATE",
            source_corpus_version="p0-test-v1",
            source_corpus_manifest_sha256="b" * 64,
            taxonomy_sha256="c" * 64,
            embeddings_sha256=embeddings_sha,
        )
        payload = build_v2_index_structure(
            selection, embeddings.tolist(), self.taxonomy, context
        )
        self._write_json(index_path, payload)
        return index_path, embeddings_path, payload

    def _v2_fixture(self):
        return self._v2_fixture_for_references(
            [
                self._reference("creme", "creme_de_cebola"),
                self._reference("mostarda", "mostarda"),
            ]
        )

    def _simple_reference(self, token="arroz"):
        return ImageReference(
            visual_class_id="arroz_branco",
            visual_class="Arroz Branco",
            source_relative_path=f"Arroz Branco/{token}.jpg",
            source_filename=f"{token}.jpg",
            source_sha256=_sha(token),
            source_bytes=len(token.encode("utf-8")),
        )

    def _rewrite(self, index_path, payload):
        self._write_json(index_path, payload)

    def test_valid_legacy_v1_loads(self):
        index_path, _, _ = self._legacy_fixture()
        loaded = load_index_artifacts(index_path)
        self.assertEqual(loaded.schema_version, 1)
        self.assertEqual(loaded.embeddings.shape, (3, EMBEDDING_DIM))

    def test_legacy_v1_structure_is_preserved(self):
        index_path, _, payload = self._legacy_fixture()
        loaded = load_index_artifacts(index_path)
        self.assertEqual(loaded.visual_labels, tuple(payload["dishes"]))
        self.assertEqual(loaded.dish_to_idx["Arroz Branco"], (0, 1))
        self.assertEqual(
            loaded.legacy_metadata["Feijão"]["image_count"], 1
        )

    def test_legacy_v1_accepts_absence_of_v2_fields(self):
        index_path, _, _ = self._legacy_fixture()
        loaded = load_index_artifacts(index_path)
        self.assertEqual(loaded.provenance, ())
        self.assertNotIn("index_id", loaded.index_metadata)

    def test_valid_v2_loads(self):
        index_path, _, _ = self._v2_fixture()
        loaded = load_index_artifacts(index_path, taxonomy=self.taxonomy)
        self.assertEqual(loaded.schema_version, 2)
        self.assertEqual(loaded.embeddings.shape, (2, EMBEDDING_DIM))

    def test_v2_visual_class_is_loaded(self):
        index_path, _, _ = self._v2_fixture()
        loaded = load_index_artifacts(index_path, taxonomy=self.taxonomy)
        self.assertEqual(
            loaded.visual_labels,
            ("Maminha Molho Claro", "Maminha Molho Claro"),
        )
        self.assertEqual(
            {item["visual_class_id"] for item in loaded.provenance},
            {"maminha_molho_claro"},
        )

    def test_v2_simple_class_outside_taxonomy_loads_and_preserves_name(self):
        index_path, _, _ = self._v2_fixture_for_references(
            [self._simple_reference()], stem="simple"
        )
        loaded = load_index_artifacts(index_path, taxonomy=self.taxonomy)
        self.assertEqual(loaded.visual_labels, ("Arroz Branco",))
        self.assertEqual(
            loaded.provenance[0]["visual_class_id"], "arroz_branco"
        )

    def test_builder_and_loader_accept_same_mixed_visual_classes(self):
        references = [
            self._simple_reference(),
            self._reference("mostarda-mixed", "mostarda"),
        ]
        index_path, _, payload = self._v2_fixture_for_references(
            references, stem="mixed"
        )
        loaded = load_index_artifacts(index_path, taxonomy=self.taxonomy)
        self.assertEqual(set(loaded.visual_labels), set(payload["dishes"]))
        self.assertEqual(
            set(loaded.dish_to_idx), {"Arroz Branco", "Maminha Molho Claro"}
        )

    def test_v2_provenance_is_aligned_one_to_one(self):
        index_path, _, _ = self._v2_fixture()
        loaded = load_index_artifacts(index_path, taxonomy=self.taxonomy)
        self.assertEqual(len(loaded.provenance), len(loaded.embeddings))
        for index, reference in enumerate(loaded.provenance):
            self.assertEqual(reference["embedding_index"], index)
            self.assertEqual(loaded.visual_labels[index], reference["visual_class"])

    def test_v2_schema_version_and_versions_are_exposed(self):
        index_path, _, _ = self._v2_fixture()
        loaded = load_index_artifacts(index_path, taxonomy=self.taxonomy)
        self.assertEqual(loaded.schema_version, 2)
        self.assertEqual(loaded.index_metadata["builder_version"], BUILDER_VERSION)
        self.assertEqual(
            loaded.index_metadata["preprocessing_version"],
            "clip-vit-b16-soulnutri-v1",
        )

    def test_same_loader_handles_v1_and_v2_without_shared_state(self):
        legacy_path, _, _ = self._legacy_fixture()
        legacy = load_index_artifacts(legacy_path)
        candidate_path, _, _ = self._v2_fixture()
        candidate = load_index_artifacts(candidate_path, taxonomy=self.taxonomy)
        self.assertEqual(legacy.schema_version, 1)
        self.assertEqual(candidate.schema_version, 2)
        self.assertEqual(legacy.visual_labels[0], "Arroz Branco")
        self.assertEqual(candidate.visual_labels[0], "Maminha Molho Claro")
        self.assertFalse(legacy.embeddings.flags.writeable)
        self.assertFalse(candidate.embeddings.flags.writeable)

    def test_unknown_schema_fails_closed(self):
        index_path, _, payload = self._legacy_fixture()
        payload["recognition_schema_version"] = 3
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(
            IndexArtifactValidationError, "unsupported recognition_schema_version"
        ):
            load_index_artifacts(index_path)

    def test_v2_fields_without_explicit_schema_fail_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload.pop("recognition_schema_version")
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(
            IndexArtifactValidationError, "recognition_schema_version is required"
        ):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_malformed_json_fails_closed(self):
        index_path = self.root / "broken.json"
        embeddings_path = self.root / "broken_embeddings.npy"
        index_path.write_text("{not-json", encoding="utf-8")
        np.save(embeddings_path, np.zeros((1, EMBEDDING_DIM), dtype=np.float32))
        with self.assertRaisesRegex(IndexArtifactValidationError, "invalid index JSON"):
            load_index_artifacts(index_path)

    def test_missing_npy_fails_closed(self):
        index_path, embeddings_path, _ = self._legacy_fixture()
        embeddings_path.unlink()
        with self.assertRaisesRegex(IndexArtifactValidationError, "does not exist"):
            load_index_artifacts(index_path)

    def test_embedding_and_provenance_count_mismatch_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"] = payload["references"][:1]
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(
            IndexArtifactValidationError, "provenance reference count"
        ):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_invalid_sha_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][0]["source_sha256"] = "invalid"
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "source_sha256"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_empty_visual_class_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][0]["visual_class"] = ""
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "visual_class"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_duplicate_provenance_sha_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][1]["source_sha256"] = payload["references"][0][
            "source_sha256"
        ]
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(
            IndexArtifactValidationError, "duplicate embedding provenance"
        ):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_incorrect_field_type_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][0]["source_bytes"] = "12"
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "source_bytes"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_mismatched_configured_family_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][0]["visual_class_id"] = "maminha_molho_escuro"
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "mismatched"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_taxonomy_version_mismatch_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["provenance"]["taxonomy_version"] = "unknown-taxonomy"
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "taxonomy version"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_unknown_source_variant_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][0]["source_variant_id"] = "unknown_variant"
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "not allowed"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_explicit_exclusion_source_variant_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][0]["source_variant_id"] = "maminha_molho_escuro"
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "not allowed"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_embeddings_hash_mismatch_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["provenance"]["embeddings_sha256"] = "0" * 64
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "SHA-256 mismatch"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_missing_builder_version_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["provenance"].pop("builder_version")
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "builder_version"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_invalid_relative_path_fails_closed(self):
        index_path, _, payload = self._v2_fixture()
        payload["references"][0]["source_relative_path"] = "../outside.jpg"
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "relative path"):
            load_index_artifacts(index_path, taxonomy=self.taxonomy)

    def test_loader_does_not_resolve_display_variant(self):
        index_path, _, _ = self._v2_fixture()
        loaded = load_index_artifacts(index_path, taxonomy=self.taxonomy)
        self.assertNotIn("display_variant", loaded.index_metadata)
        self.assertTrue(
            all("display_variant" not in item for item in loaded.provenance)
        )

    def test_v1_mapping_mismatch_fails_closed(self):
        index_path, _, payload = self._legacy_fixture()
        payload["dish_to_idx"]["Arroz Branco"] = [0, 2]
        self._rewrite(index_path, payload)
        with self.assertRaisesRegex(IndexArtifactValidationError, "not aligned"):
            load_index_artifacts(index_path)


if __name__ == "__main__":
    unittest.main()
