# -*- coding: utf-8 -*-
"""Unit tests for the isolated, write-free visual index v2 builder."""

import hashlib
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from ai.families import load_visual_taxonomy  # noqa: E402
from ai.index_builder_v2 import (  # noqa: E402
    BUILDER_VERSION,
    EMBEDDING_DIM,
    BuilderContext,
    ImageReference,
    SelectionResult,
    VisualIndexBuilderError,
    build_v2_index_structure,
    create_image_reference,
    select_deterministic_references,
)


def _sha(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _embedding(seed):
    return [float(seed)] * EMBEDDING_DIM


class DeterministicIndexBuilderTest(unittest.TestCase):
    def setUp(self):
        self.taxonomy = load_visual_taxonomy()
        self.context = BuilderContext(
            index_id="visual-index-test-v2",
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
            embeddings_sha256="d" * 64,
        )

    def _ref(
        self,
        token,
        *,
        class_id="maminha_molho_claro",
        class_name="Maminha Molho Claro",
        filename=None,
        sha256=None,
        variant_id=None,
    ):
        filename = filename or f"{token}.jpg"
        variant_status = "reference_annotation" if variant_id else None
        variant_source = "human_manifest" if variant_id else None
        return ImageReference(
            visual_class_id=class_id,
            visual_class=class_name,
            source_relative_path=f"{class_name}/{filename}",
            source_filename=filename,
            source_sha256=sha256 or _sha(token),
            source_bytes=len(token.encode("utf-8")),
            source_variant_id=variant_id,
            source_variant_status=variant_status,
            source_variant_source=variant_source,
            original_class=class_name,
            human_decision_refs=("REV-TEST",),
        )

    def _selection(self, references, limit=10):
        return select_deterministic_references(
            references,
            self.taxonomy,
            max_per_visual_class=limit,
        )

    def _build(self, selection, embeddings=None, context=None):
        if embeddings is None:
            embeddings = [
                _embedding(index)
                for index in range(len(selection.references))
            ]
        return build_v2_index_structure(
            selection,
            embeddings,
            self.taxonomy,
            context or self.context,
        )

    def test_input_order_does_not_change_selection(self):
        references = [self._ref(f"img-{index}") for index in range(12)]
        forward = self._selection(references)
        reverse = self._selection(list(reversed(references)))
        self.assertEqual(forward, reverse)

    def test_more_than_ten_always_selects_same_ten(self):
        references = [self._ref(f"img-{index}") for index in range(15)]
        expected = sorted(item.source_sha256 for item in references)[:10]
        selection = self._selection(references)
        self.assertEqual(
            [item.source_sha256 for item in selection.references], expected
        )
        self.assertEqual(selection.class_stats[0].selected, 10)

    def test_ten_or_fewer_preserves_all_unique_images(self):
        references = [self._ref(f"img-{index}") for index in range(7)]
        selection = self._selection(references)
        self.assertEqual(len(selection.references), 7)
        self.assertEqual(selection.class_stats[0].unique_sha256, 7)

    def test_accents_and_spaces_have_stable_path_tiebreak(self):
        shared_sha = _sha("same-content")
        references = [
            self._ref("a", filename="Maminha Árvore.jpg", sha256=shared_sha),
            self._ref("b", filename="Maminha com Espaço.jpg", sha256=shared_sha),
        ]
        selection = self._selection(list(reversed(references)))
        paths = sorted(item.source_relative_path for item in references)
        self.assertEqual(selection.references[0].source_relative_path, paths[0])
        self.assertEqual(selection.references[0].duplicate_source_paths, (paths[1],))

    def test_duplicate_content_is_identified_by_sha(self):
        shared_sha = _sha("duplicate")
        references = [
            self._ref("same", filename="copy-a.jpg", sha256=shared_sha),
            self._ref("same", filename="copy-b.jpg", sha256=shared_sha),
        ]
        selection = self._selection(references)
        self.assertEqual(len(selection.references), 1)
        self.assertEqual(selection.class_stats[0].total_paths, 2)
        self.assertEqual(selection.class_stats[0].unique_sha256, 1)
        self.assertEqual(len(selection.references[0].duplicate_source_paths), 1)

    def test_create_reference_records_file_provenance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            image = root / "Maminha Molho Claro" / "foto 01.jpg"
            image.parent.mkdir()
            image.write_bytes(b"synthetic-image-bytes")
            reference = create_image_reference(
                image,
                root,
                self.taxonomy,
                visual_class_id="maminha_molho_claro",
            )
        self.assertEqual(reference.source_filename, "foto 01.jpg")
        self.assertEqual(
            reference.source_relative_path,
            "Maminha Molho Claro/foto 01.jpg",
        )
        self.assertEqual(reference.source_sha256, _sha("synthetic-image-bytes"))
        self.assertEqual(reference.source_bytes, len(b"synthetic-image-bytes"))

    def test_unconfigured_simple_class_is_accepted(self):
        reference = self._ref(
            "rice",
            class_id="arroz_branco",
            class_name="Arroz Branco",
        )
        selection = self._selection([reference])
        self.assertEqual(selection.references, (reference,))

    def test_unconfigured_simple_class_preserves_its_own_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            image = root / "Arroz Branco" / "arroz.jpg"
            image.parent.mkdir()
            image.write_bytes(b"plain-class-image")
            reference = create_image_reference(
                image,
                root,
                self.taxonomy,
                visual_class_id="arroz_branco",
            )
        payload = self._build(self._selection([reference]))
        self.assertEqual(reference.visual_class, "Arroz Branco")
        self.assertEqual(payload["dishes"], ["Arroz Branco"])
        self.assertEqual(
            payload["visual_classes"]["arroz_branco"],
            {
                "canonical_name": "Arroz Branco",
                "aliases": [],
                "variant_ids": [],
                "must_not_group": [],
            },
        )

    def test_configured_family_still_requires_canonical_name(self):
        invalid = self._ref(
            "wrong-family-name",
            class_id="maminha_molho_claro",
            class_name="Maminha Molho Inventado",
        )
        with self.assertRaisesRegex(VisualIndexBuilderError, "mismatched"):
            self._selection([invalid])

    def test_invalid_variant_for_configured_family_still_fails_closed(self):
        invalid = self._ref("invalid-variant", variant_id="nao_configurada")
        with self.assertRaisesRegex(
            VisualIndexBuilderError, "unknown source_variant_id"
        ):
            self._selection([invalid])

    def test_unconfigured_simple_class_cannot_declare_variant(self):
        invalid = self._ref(
            "plain-with-variant",
            class_id="arroz_branco",
            class_name="Arroz Branco",
            variant_id="mostarda",
        )
        with self.assertRaisesRegex(
            VisualIndexBuilderError, "requires a configured visual family"
        ):
            self._selection([invalid])

    def test_external_exclusion_class_remains_valid_as_standalone(self):
        reference = self._ref(
            "standalone-berinjela",
            class_id="berinjela_a_parmegiana",
            class_name="Berinjela à Parmegiana",
        )
        payload = self._build(self._selection([reference]))
        self.assertEqual(payload["dishes"], ["Berinjela à Parmegiana"])
        self.assertEqual(
            payload["visual_classes"]["berinjela_a_parmegiana"][
                "variant_ids"
            ],
            [],
        )

    def test_external_exclusion_class_cannot_use_mismatched_identity(self):
        invalid = self._ref(
            "aliased-berinjela",
            class_id="berinjela_renamed",
            class_name="Berinjela à Parmegiana",
        )
        with self.assertRaisesRegex(VisualIndexBuilderError, "mismatched"):
            self._selection([invalid])

    def test_each_embedding_receives_required_versions_and_identity(self):
        selection = self._selection([self._ref("one"), self._ref("two")])
        payload = self._build(selection)
        for index, reference in enumerate(payload["references"]):
            self.assertEqual(reference["embedding_index"], index)
            self.assertEqual(reference["visual_class"], "Maminha Molho Claro")
            self.assertEqual(
                reference["preprocessing_version"],
                self.context.preprocessing_version,
            )
            self.assertEqual(reference["model_identifier"], "ViT-B-16")
            self.assertEqual(reference["builder_version"], BUILDER_VERSION)
            self.assertEqual(reference["recognition_schema_version"], 2)

    def test_embedding_to_image_relation_is_reproducible(self):
        selection = self._selection([self._ref("one"), self._ref("two")])
        payload = self._build(selection)
        for index, reference in enumerate(selection.references):
            stored = payload["references"][index]
            self.assertEqual(stored["embedding_index"], index)
            self.assertEqual(stored["source_sha256"], reference.source_sha256)
            self.assertEqual(payload["dishes"][index], reference.visual_class)

    def test_payload_carries_portable_artifact_provenance(self):
        selection = self._selection([self._ref("one")])
        payload = self._build(selection)
        provenance = payload["provenance"]
        self.assertEqual(
            provenance["selection_manifest_sha256"], selection.manifest_sha256
        )
        self.assertEqual(provenance["source_corpus_id"], "P0_CANDIDATE")
        self.assertEqual(provenance["corpus_manifest_sha256"], "b" * 64)
        self.assertEqual(provenance["taxonomy_sha256"], "c" * 64)
        self.assertEqual(provenance["embeddings_sha256"], "d" * 64)

    def test_structure_is_deterministic_for_identical_inputs(self):
        selection = self._selection([self._ref("one"), self._ref("two")])
        embeddings = [_embedding(1), _embedding(2)]
        self.assertEqual(
            self._build(selection, embeddings),
            self._build(selection, embeddings),
        )

    def test_approved_variants_converge_to_same_visual_class(self):
        references = [
            self._ref("cream", variant_id="creme_de_cebola"),
            self._ref("mustard", variant_id="mostarda"),
        ]
        payload = self._build(self._selection(references))
        self.assertEqual(set(payload["dishes"]), {"Maminha Molho Claro"})
        self.assertEqual(
            {item["source_variant_id"] for item in payload["references"]},
            {"creme_de_cebola", "mostarda"},
        )

    def test_explicit_exclusion_is_not_accepted_as_family_variant(self):
        invalid = self._ref(
            "berinjela",
            class_id="file_a_parmegiana",
            class_name="Filé à Parmegiana",
            variant_id="berinjela_a_parmegiana",
        )
        with self.assertRaisesRegex(
            VisualIndexBuilderError, "explicitly excluded source_variant_id"
        ):
            self._selection([invalid])

    def test_all_three_special_families_keep_configured_behavior(self):
        configured = (
            ("maminha_molho_claro", "Maminha Molho Claro", "mostarda"),
            ("maminha_molho_escuro", "Maminha Molho Escuro", "madeira"),
            ("file_a_parmegiana", "Filé à Parmegiana", "frango"),
        )
        for index, (class_id, class_name, variant_id) in enumerate(configured):
            with self.subTest(class_id=class_id):
                reference = self._ref(
                    f"special-{index}",
                    class_id=class_id,
                    class_name=class_name,
                    variant_id=variant_id,
                )
                payload = self._build(self._selection([reference]))
                self.assertEqual(payload["dishes"], [class_name])
                self.assertIn(
                    variant_id,
                    payload["visual_classes"][class_id]["variant_ids"],
                )

    def test_fixture_with_238_unconfigured_classes_builds(self):
        references = [
            self._ref(
                f"simple-{index:03d}",
                class_id=f"simple_{index:03d}",
                class_name=f"Simple {index:03d}",
            )
            for index in range(238)
        ]
        payload = self._build(self._selection(references))
        self.assertEqual(payload["total_dishes"], 238)
        self.assertEqual(len(payload["visual_classes"]), 238)
        self.assertEqual(payload["variants"], {})

    def test_light_and_dark_sauces_remain_distinct(self):
        references = [
            self._ref("light"),
            self._ref(
                "dark",
                class_id="maminha_molho_escuro",
                class_name="Maminha Molho Escuro",
            ),
        ]
        payload = self._build(self._selection(references))
        self.assertEqual(
            set(payload["dish_to_idx"]),
            {"Maminha Molho Claro", "Maminha Molho Escuro"},
        )
        self.assertNotEqual(
            payload["dish_to_idx"]["Maminha Molho Claro"],
            payload["dish_to_idx"]["Maminha Molho Escuro"],
        )

    def test_display_variant_is_not_resolved(self):
        selection = self._selection(
            [self._ref("mustard", variant_id="mostarda")]
        )
        payload = self._build(selection)
        self.assertNotIn("display_variant", payload)
        self.assertNotIn("display_variant", payload["references"][0])

    def test_missing_image_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaisesRegex(VisualIndexBuilderError, "does not exist"):
                create_image_reference(
                    root / "missing.jpg",
                    root,
                    self.taxonomy,
                    visual_class_id="maminha_molho_claro",
                )

    def test_image_outside_corpus_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as corpus_dir, tempfile.TemporaryDirectory() as other_dir:
            image = Path(other_dir) / "outside.jpg"
            image.write_bytes(b"outside")
            with self.assertRaisesRegex(VisualIndexBuilderError, "corpus_root"):
                create_image_reference(
                    image,
                    Path(corpus_dir),
                    self.taxonomy,
                    visual_class_id="maminha_molho_claro",
                )

    def test_missing_sha_fails_closed(self):
        invalid = replace(self._ref("one"), source_sha256="")
        with self.assertRaisesRegex(VisualIndexBuilderError, "source_sha256"):
            self._selection([invalid])

    def test_configured_family_name_cannot_be_bypassed_with_unknown_id(self):
        invalid = self._ref(
            "one", class_id="unknown", class_name="Maminha Molho Claro"
        )
        with self.assertRaisesRegex(VisualIndexBuilderError, "mismatched"):
            self._selection([invalid])

    def test_duplicate_sha_with_inconsistent_provenance_fails_closed(self):
        shared_sha = _sha("same")
        references = [
            self._ref("same", filename="one.jpg", sha256=shared_sha),
            self._ref(
                "same",
                filename="two.jpg",
                sha256=shared_sha,
                variant_id="mostarda",
            ),
        ]
        with self.assertRaisesRegex(
            VisualIndexBuilderError, "inconsistent provenance"
        ):
            self._selection(references)

    def test_cross_class_sha_with_inconsistent_provenance_fails_closed(self):
        shared_sha = _sha("cross-class")
        references = [
            self._ref("same-light", sha256=shared_sha),
            self._ref(
                "same-dark",
                class_id="maminha_molho_escuro",
                class_name="Maminha Molho Escuro",
                sha256=shared_sha,
            ),
        ]
        selection = self._selection(references)
        with self.assertRaisesRegex(
            VisualIndexBuilderError, "inconsistent embedding provenance"
        ):
            self._build(selection)

    def test_invalid_schema_version_fails_closed(self):
        selection = self._selection([self._ref("one")])
        invalid_context = replace(self.context, recognition_schema_version=3)
        with self.assertRaisesRegex(
            VisualIndexBuilderError, "recognition_schema_version"
        ):
            self._build(selection, context=invalid_context)

    def test_embedding_count_mismatch_fails_closed(self):
        selection = self._selection([self._ref("one"), self._ref("two")])
        with self.assertRaisesRegex(VisualIndexBuilderError, "embedding count"):
            self._build(selection, embeddings=[_embedding(1)])

    def test_embedding_dimension_mismatch_fails_closed(self):
        selection = self._selection([self._ref("one")])
        with self.assertRaisesRegex(VisualIndexBuilderError, "dimension"):
            self._build(selection, embeddings=[[0.1, 0.2]])

    def test_tampered_selection_manifest_fails_closed(self):
        selection = self._selection([self._ref("one")])
        tampered = SelectionResult(
            references=selection.references,
            class_stats=selection.class_stats,
            manifest_sha256="0" * 64,
        )
        with self.assertRaisesRegex(VisualIndexBuilderError, "manifest SHA"):
            self._build(tampered)


if __name__ == "__main__":
    unittest.main()
