# -*- coding: utf-8 -*-
"""Isolated tests for the versioned visual-family taxonomy."""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from ai.families import (  # noqa: E402
    DEFAULT_VISUAL_TAXONOMY_PATH,
    VariantEvidence,
    VisualTaxonomyValidationError,
    collect_variant_evidence,
    get_allowed_variants,
    get_visual_family,
    is_excluded_from_family,
    is_valid_variant,
    load_visual_taxonomy,
    resolve_display_variant,
    resolve_variant_alias,
    validate_visual_taxonomy,
)


class VisualFamilyResolutionTest(unittest.TestCase):
    def setUp(self):
        self.taxonomy = load_visual_taxonomy()

    def _assert_invalid(self, data, message):
        with self.assertRaisesRegex(VisualTaxonomyValidationError, message):
            validate_visual_taxonomy(data)

    def test_valid_config_loads_and_reads_version(self):
        self.assertTrue(DEFAULT_VISUAL_TAXONOMY_PATH.is_file())
        self.assertEqual(self.taxonomy["taxonomy_schema_version"], 1)
        self.assertEqual(
            self.taxonomy["taxonomy_version"], "visual-family-initial-3-v1"
        )
        self.assertEqual(len(self.taxonomy["families"]), 3)

    def test_three_visual_families_exist(self):
        names = {
            family["canonical_name"] for family in self.taxonomy["families"]
        }
        self.assertEqual(
            names,
            {
                "Maminha Molho Claro",
                "Maminha Molho Escuro",
                "Filé à Parmegiana",
            },
        )

    def test_light_sauce_variants(self):
        self.assertEqual(
            get_allowed_variants(self.taxonomy, "Maminha Molho Claro"),
            ("Creme de Cebola", "Mostarda", "Gorgonzola"),
        )
        for variant in ("Creme de Cebola", "Mostarda", "Gorgonzola"):
            self.assertTrue(
                is_valid_variant(self.taxonomy, "Maminha Molho Claro", variant)
            )
        self.assertFalse(
            is_valid_variant(self.taxonomy, "Maminha Molho Claro", "Madeira")
        )

    def test_dark_sauce_variants(self):
        self.assertEqual(
            get_allowed_variants(self.taxonomy, "Maminha Molho Escuro"),
            ("Mongólia", "Madeira", "Cerveja Preta", "Funghi", "Champignon"),
        )
        for variant in (
            "Mongólia",
            "Madeira",
            "Cerveja Preta",
            "Funghi",
            "Champignon",
        ):
            self.assertTrue(
                is_valid_variant(self.taxonomy, "Maminha Molho Escuro", variant)
            )
        self.assertFalse(
            is_valid_variant(self.taxonomy, "Maminha Molho Escuro", "Gorgonzola")
        )

    def test_funghi_and_champignon_are_not_aliases(self):
        family = get_visual_family(self.taxonomy, "Maminha Molho Escuro")
        self.assertTrue(all(not variant["aliases"] for variant in family["variants"]))
        self.assertIsNone(
            resolve_variant_alias(self.taxonomy, "Maminha Molho Escuro", "Funghi")
        )
        self.assertIsNone(
            resolve_variant_alias(
                self.taxonomy, "Maminha Molho Escuro", "Champignon"
            )
        )

    def test_parmegiana_variants_and_berinjela_exclusion(self):
        self.assertEqual(
            get_allowed_variants(self.taxonomy, "Filé à Parmegiana"),
            ("Filé Mignon", "Frango", "Peixe"),
        )
        for variant in ("Filé Mignon", "Frango", "Peixe"):
            self.assertTrue(
                is_valid_variant(self.taxonomy, "Filé à Parmegiana", variant)
            )
        self.assertFalse(
            is_valid_variant(
                self.taxonomy, "Filé à Parmegiana", "Berinjela à Parmegiana"
            )
        )
        self.assertTrue(
            is_excluded_from_family(
                self.taxonomy, "Filé à Parmegiana", "Berinjela à Parmegiana"
            )
        )

    def test_visual_class_lookup_accepts_exact_id_and_name(self):
        by_id = get_visual_family(self.taxonomy, "maminha_molho_claro")
        by_name = get_visual_family(self.taxonomy, "Maminha Molho Claro")
        self.assertEqual(by_id, by_name)
        self.assertEqual(by_name["visual_class_id"], "maminha_molho_claro")

    def test_typo_is_not_normalized(self):
        self.assertIsNone(
            get_visual_family(self.taxonomy, "Maminha molho claro")
        )
        self.assertFalse(
            is_valid_variant(self.taxonomy, "Maminha Molho Claro", "MOSTARDA")
        )

    def test_only_explicit_variant_alias_is_resolved(self):
        configured = copy.deepcopy(self.taxonomy)
        configured["families"][0]["variant_aliases"] = {
            "Molho de Mostarda": "mostarda"
        }
        validated = validate_visual_taxonomy(configured)
        self.assertEqual(
            resolve_variant_alias(
                validated, "Maminha Molho Claro", "Molho de Mostarda"
            ),
            "Mostarda",
        )
        self.assertTrue(
            is_valid_variant(
                validated, "Maminha Molho Claro", "Molho de Mostarda"
            )
        )
        self.assertFalse(
            is_valid_variant(validated, "Maminha Molho Claro", "Molho Mostarda")
        )

    def test_load_has_no_global_mutable_cache(self):
        self.taxonomy["families"][0]["canonical_name"] = "changed locally"
        reloaded = load_visual_taxonomy()
        self.assertEqual(
            reloaded["families"][0]["canonical_name"], "Maminha Molho Claro"
        )

    def test_malformed_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "taxonomy.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(
                VisualTaxonomyValidationError, "invalid visual taxonomy JSON"
            ):
                load_visual_taxonomy(path)

    def test_missing_schema_version_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid.pop("taxonomy_schema_version")
        self._assert_invalid(invalid, "taxonomy_schema_version")

    def test_unsupported_schema_version_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["taxonomy_schema_version"] = 2
        self._assert_invalid(invalid, "unsupported")

    def test_empty_visual_class_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][0]["canonical_name"] = ""
        self._assert_invalid(invalid, "canonical_name")

    def test_duplicate_visual_class_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        duplicate = copy.deepcopy(invalid["families"][0])
        duplicate["visual_class_id"] = "different_id"
        invalid["families"].append(duplicate)
        self._assert_invalid(invalid, "duplicate visual_class")

    def test_empty_variant_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][0]["variants"][0]["display_name"] = ""
        self._assert_invalid(invalid, "display_name")

    def test_duplicate_variant_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        duplicate = copy.deepcopy(invalid["families"][0]["variants"][0])
        duplicate["id"] = "different_id"
        invalid["families"][0]["variants"].append(duplicate)
        self._assert_invalid(invalid, "duplicate variant")

    def test_duplicate_alias_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][0]["variants"][0]["aliases"] = ["Molho Antigo"]
        invalid["families"][0]["variants"][1]["aliases"] = ["Molho Antigo"]
        self._assert_invalid(invalid, "duplicate variant alias")

    def test_alias_collision_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][0]["variants"][0]["aliases"] = ["Mostarda"]
        self._assert_invalid(invalid, "collides with canonical variant")

    def test_alias_to_unknown_variant_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][0]["variant_aliases"] = {
            "Molho Misterioso": "missing_variant"
        }
        self._assert_invalid(invalid, "targets unknown variant")

    def test_self_exclusion_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][0]["must_not_group"] = ["maminha_molho_claro"]
        self._assert_invalid(invalid, "exclude itself")

    def test_unknown_exclusion_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][2]["must_not_group"] = ["classe_inexistente"]
        self._assert_invalid(invalid, "unknown exclusion")

    def test_invalid_evidence_source_fails_closed(self):
        invalid = copy.deepcopy(self.taxonomy)
        invalid["families"][0]["accepted_evidence_sources"] = ["openclip"]
        self._assert_invalid(invalid, "unsupported evidence source")


class DisplayVariantResolutionTest(unittest.TestCase):
    def setUp(self):
        self.taxonomy = load_visual_taxonomy()

    def _resolve(self, visual_class, **sources):
        evidence = collect_variant_evidence(**sources)
        return resolve_display_variant(self.taxonomy, visual_class, evidence)

    def _assert_confirmed(self, result, variant, source="structured_metadata"):
        self.assertEqual(result.visual_class, result.visual_class.strip())
        self.assertEqual(result.display_variant, variant)
        self.assertEqual(result.variant_source, source)
        self.assertEqual(result.variant_status, "confirmed")
        self.assertEqual(result.reason, "confirmed_variant_evidence")

    def test_light_metadata_creme_de_cebola_resolves(self):
        result = self._resolve(
            "Maminha Molho Claro", structured_metadata="Creme de Cebola"
        )
        self._assert_confirmed(result, "Creme de Cebola")

    def test_light_metadata_mostarda_resolves(self):
        result = self._resolve(
            "Maminha Molho Claro", structured_metadata="Mostarda"
        )
        self._assert_confirmed(result, "Mostarda")

    def test_light_metadata_gorgonzola_resolves(self):
        result = self._resolve(
            "Maminha Molho Claro", structured_metadata="Gorgonzola"
        )
        self._assert_confirmed(result, "Gorgonzola")

    def test_light_rejects_madeira(self):
        result = self._resolve(
            "Maminha Molho Claro", structured_metadata="Madeira"
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "unsupported")

    def test_light_without_evidence_returns_null(self):
        result = self._resolve("Maminha Molho Claro")
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "absent")

    def test_dark_metadata_mongolia_resolves(self):
        result = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Mongólia"
        )
        self._assert_confirmed(result, "Mongólia")

    def test_dark_metadata_madeira_resolves(self):
        result = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Madeira"
        )
        self._assert_confirmed(result, "Madeira")

    def test_dark_metadata_cerveja_preta_resolves(self):
        result = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Cerveja Preta"
        )
        self._assert_confirmed(result, "Cerveja Preta")

    def test_dark_metadata_funghi_resolves(self):
        result = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Funghi"
        )
        self._assert_confirmed(result, "Funghi")

    def test_dark_metadata_champignon_resolves(self):
        result = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Champignon"
        )
        self._assert_confirmed(result, "Champignon")

    def test_dark_rejects_gorgonzola(self):
        result = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Gorgonzola"
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "unsupported")

    def test_funghi_and_champignon_remain_distinct(self):
        funghi = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Funghi"
        )
        champignon = self._resolve(
            "Maminha Molho Escuro", structured_metadata="Champignon"
        )
        self.assertEqual(funghi.display_variant, "Funghi")
        self.assertEqual(champignon.display_variant, "Champignon")
        self.assertNotEqual(funghi.display_variant, champignon.display_variant)

    def test_parmegiana_file_mignon_resolves(self):
        result = self._resolve(
            "Filé à Parmegiana", structured_metadata="Filé Mignon"
        )
        self._assert_confirmed(result, "Filé Mignon")

    def test_parmegiana_frango_resolves(self):
        result = self._resolve(
            "Filé à Parmegiana", structured_metadata="Frango"
        )
        self._assert_confirmed(result, "Frango")

    def test_parmegiana_peixe_resolves(self):
        result = self._resolve(
            "Filé à Parmegiana", structured_metadata="Peixe"
        )
        self._assert_confirmed(result, "Peixe")

    def test_parmegiana_rejects_berinjela(self):
        result = self._resolve(
            "Filé à Parmegiana",
            structured_metadata="Berinjela à Parmegiana",
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "unsupported")
        self.assertEqual(result.reason, "excluded_variant_evidence")

    def test_parmegiana_without_evidence_returns_null(self):
        result = self._resolve("Filé à Parmegiana")
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "absent")

    def test_explicit_admin_evidence_resolves(self):
        result = self._resolve("Maminha Molho Claro", human_admin="Mostarda")
        self._assert_confirmed(result, "Mostarda", "human_admin")

    def test_structured_metadata_evidence_resolves(self):
        result = self._resolve(
            "Maminha Molho Claro", structured_metadata="Mostarda"
        )
        self._assert_confirmed(result, "Mostarda", "structured_metadata")

    def test_exact_ocr_evidence_resolves(self):
        result = self._resolve("Maminha Molho Claro", ocr="Mostarda")
        self._assert_confirmed(result, "Mostarda", "ocr")

    def test_concordant_sources_resolve_with_highest_priority_source(self):
        evidence = collect_variant_evidence(
            human_admin="Mostarda",
            structured_metadata="Mostarda",
            ocr="Mostarda",
            evidence_ids={
                "human_admin": "admin-1",
                "structured_metadata": "menu-1",
                "ocr": "ocr-1",
            },
        )
        result = resolve_display_variant(
            self.taxonomy, "Maminha Molho Claro", evidence
        )
        self._assert_confirmed(result, "Mostarda", "human_admin")
        self.assertEqual(
            result.variant_evidence_ids,
            ("admin-1", "menu-1", "ocr-1"),
        )

    def test_conflicting_sources_return_null(self):
        result = self._resolve(
            "Maminha Molho Claro",
            structured_metadata="Mostarda",
            ocr="Gorgonzola",
        )
        self.assertIsNone(result.display_variant)
        self.assertIsNone(result.variant_source)
        self.assertEqual(result.variant_status, "conflict")
        self.assertEqual(result.reason, "conflicting_variant_evidence")

    def test_admin_conflict_does_not_hide_other_valid_source(self):
        result = self._resolve(
            "Maminha Molho Claro",
            human_admin="Mostarda",
            structured_metadata="Gorgonzola",
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "conflict")

    def test_ambiguous_ocr_returns_null(self):
        result = self._resolve(
            "Maminha Molho Escuro", ocr=("Funghi", "Champignon")
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "ambiguous")
        self.assertEqual(result.reason, "ambiguous_variant_evidence")

    def test_unknown_variant_returns_null(self):
        result = self._resolve(
            "Maminha Molho Claro", structured_metadata="Molho Misterioso"
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "unsupported")
        self.assertEqual(result.reason, "unknown_variant_evidence")

    def test_openclip_is_not_accepted_as_variant_evidence(self):
        evidence = (
            VariantEvidence(
                source="openclip",
                values=("Mostarda",),
                evidence_id="visual-result",
            ),
        )
        result = resolve_display_variant(
            self.taxonomy, "Maminha Molho Claro", evidence
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "unsupported")
        self.assertEqual(
            result.reason, "unsupported_variant_evidence_source"
        )

    def test_unknown_visual_class_does_not_choose_variant(self):
        result = self._resolve(
            "Classe Visual Inexistente", structured_metadata="Mostarda"
        )
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "unconfigured")

    def test_unconfigured_regular_class_does_not_error(self):
        result = self._resolve("Arroz Branco", structured_metadata="Mostarda")
        self.assertIsNone(result.display_variant)
        self.assertEqual(result.variant_status, "unconfigured")
        self.assertEqual(
            result.reason, "visual_class_has_no_variant_taxonomy"
        )

    def test_typo_and_case_are_not_normalized(self):
        typo = self._resolve(
            "Maminha Molho Claro", structured_metadata="Mostárda"
        )
        changed_case = self._resolve(
            "Maminha Molho Claro", structured_metadata="MOSTARDA"
        )
        self.assertIsNone(typo.display_variant)
        self.assertEqual(typo.variant_status, "unsupported")
        self.assertIsNone(changed_case.display_variant)
        self.assertEqual(changed_case.variant_status, "unsupported")

    def test_score_and_confidence_are_outside_resolution_contract(self):
        recognition = {"score": 0.731, "confidence": "media"}
        before = copy.deepcopy(recognition)
        result = self._resolve(
            "Maminha Molho Claro", structured_metadata="Mostarda"
        )
        self.assertEqual(recognition, before)
        self.assertFalse(hasattr(result, "score"))
        self.assertFalse(hasattr(result, "confidence"))

    def test_resolution_has_no_global_mutation(self):
        taxonomy_before = copy.deepcopy(self.taxonomy)
        evidence = collect_variant_evidence(structured_metadata="Mostarda")
        evidence_before = copy.deepcopy(evidence)
        resolve_display_variant(self.taxonomy, "Maminha Molho Claro", evidence)
        self.assertEqual(self.taxonomy, taxonomy_before)
        self.assertEqual(evidence, evidence_before)


if __name__ == "__main__":
    unittest.main()
