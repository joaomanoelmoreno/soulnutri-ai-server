# -*- coding: utf-8 -*-
"""Explicit, reversible v1/v2 recognition-index selection tests."""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import ai.index as index_module  # noqa: E402
import server  # noqa: E402
from ai.index import (  # noqa: E402
    APPROVED_V2_EMBEDDING_DIM,
    APPROVED_V2_EMBEDDINGS,
    APPROVED_V2_EMBEDDINGS_SHA256,
    APPROVED_V2_INDEX_SHA256,
    APPROVED_V2_VISUAL_CLASSES,
    DishIndex,
    RecognitionIndexConfigurationError,
    resolve_index_configuration,
)


class IndexVersionConfigurationTest(unittest.TestCase):
    def test_absent_version_defaults_to_v1(self):
        config = resolve_index_configuration({})
        self.assertEqual(config.version, "v1")
        self.assertEqual(config.expected_schema_version, 1)
        self.assertIsNone(config.expected_index_sha256)

    def test_explicit_v1_preserves_v1(self):
        config = resolve_index_configuration(
            {
                "RECOGNITION_INDEX_VERSION": "v1",
                "RECOGNITION_V1_INDEX_FILE": "/tmp/current.json",
            }
        )
        self.assertEqual(config.version, "v1")
        self.assertEqual(config.index_file, "/tmp/current.json")
        self.assertEqual(
            config.embeddings_file, "/tmp/current_embeddings.npy"
        )

    def test_explicit_v2_selects_only_approved_candidate_contract(self):
        config = resolve_index_configuration(
            {
                "RECOGNITION_INDEX_VERSION": "v2",
                "RECOGNITION_V2_INDEX_FILE": "/tmp/candidate.json",
            }
        )
        self.assertEqual(config.version, "v2")
        self.assertEqual(config.expected_schema_version, 2)
        self.assertEqual(config.expected_index_sha256, APPROVED_V2_INDEX_SHA256)
        self.assertEqual(
            config.expected_embeddings_sha256,
            APPROVED_V2_EMBEDDINGS_SHA256,
        )
        self.assertEqual(
            config.expected_visual_classes, APPROVED_V2_VISUAL_CLASSES
        )
        self.assertEqual(config.expected_embeddings, APPROVED_V2_EMBEDDINGS)
        self.assertEqual(
            config.expected_embedding_dim, APPROVED_V2_EMBEDDING_DIM
        )

    def test_invalid_version_fails_closed(self):
        with self.assertRaisesRegex(
            RecognitionIndexConfigurationError,
            "RECOGNITION_INDEX_VERSION",
        ):
            resolve_index_configuration(
                {"RECOGNITION_INDEX_VERSION": "automatic"}
            )

    def test_get_index_does_not_activate_v2_from_file_availability(self):
        sentinel = object()
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(index_module, "_INDEX", None),
            patch.object(index_module, "DishIndex", return_value=sentinel) as ctor,
        ):
            self.assertIs(index_module.get_index(), sentinel)
        self.assertEqual(ctor.call_args.kwargs["configured_version"], "v1")
        self.assertEqual(ctor.call_args.kwargs["expected_schema_version"], 1)
        self.assertFalse(ctor.call_args.kwargs["strict_load"])
        index_module._INDEX = None

    def test_get_index_v2_is_explicit_and_strict(self):
        sentinel = object()
        env = {
            "RECOGNITION_INDEX_VERSION": "v2",
            "RECOGNITION_V2_INDEX_FILE": "/tmp/approved.json",
        }
        with (
            patch.dict(os.environ, env, clear=True),
            patch.object(index_module, "_INDEX", None),
            patch.object(index_module, "DishIndex", return_value=sentinel) as ctor,
        ):
            self.assertIs(index_module.get_index(), sentinel)
        self.assertEqual(ctor.call_args.kwargs["configured_version"], "v2")
        self.assertEqual(ctor.call_args.kwargs["expected_schema_version"], 2)
        self.assertTrue(ctor.call_args.kwargs["strict_load"])
        index_module._INDEX = None

    def test_explicit_v2_rejects_v1_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_path = root / "dish_index.json"
            embeddings_path = root / "dish_index_embeddings.npy"
            index_path.write_text(
                json.dumps(
                    {
                        "dishes": ["Arroz Branco"],
                        "dish_to_idx": {"Arroz Branco": [0]},
                        "metadata": {"Arroz Branco": {"image_count": 1}},
                        "version": "1.0",
                        "total_items": 1,
                        "total_dishes": 1,
                    }
                ),
                encoding="utf-8",
            )
            np.save(
                embeddings_path,
                np.asarray([[0.0] * 512], dtype=np.float32),
            )
            with self.assertRaisesRegex(
                RecognitionIndexConfigurationError,
                "schema v1, expected v2",
            ):
                DishIndex(
                    index_file=str(index_path),
                    embeddings_file=str(embeddings_path),
                    configured_version="v2",
                    expected_schema_version=2,
                    strict_load=True,
                )

    def test_legacy_reindex_is_disabled_while_v2_is_active(self):
        index = DishIndex.__new__(DishIndex)
        index.configured_version = "v2"
        with self.assertRaisesRegex(
            RecognitionIndexConfigurationError,
            "legacy reindex is disabled",
        ):
            index.build_index()

    def test_missing_v2_artifact_fails_without_exposing_path(self):
        sensitive_path = "/private/staging/recognition-v2/dish_index.json"
        with self.assertRaises(RecognitionIndexConfigurationError) as raised:
            DishIndex(
                index_file=sensitive_path,
                configured_version="v2",
                expected_schema_version=2,
                strict_load=True,
            )
        self.assertNotIn(sensitive_path, str(raised.exception))
        self.assertEqual(
            str(raised.exception),
            "configured recognition index JSON is unavailable",
        )

    def test_packaged_v2_candidate_matches_approved_gate(self):
        index_path = (
            BACKEND_DIR.parent
            / "datasets"
            / "recognition_v2"
            / "dish_index.json"
        )
        embeddings_path = index_path.with_name("dish_index_embeddings.npy")

        index = DishIndex(
            index_file=str(index_path),
            embeddings_file=str(embeddings_path),
            configured_version="v2",
            expected_schema_version=2,
            expected_index_sha256=APPROVED_V2_INDEX_SHA256,
            expected_embeddings_sha256=APPROVED_V2_EMBEDDINGS_SHA256,
            expected_visual_classes=APPROVED_V2_VISUAL_CLASSES,
            expected_embeddings=APPROVED_V2_EMBEDDINGS,
            expected_embedding_dim=APPROVED_V2_EMBEDDING_DIM,
            strict_load=True,
        )

        self.assertIsNotNone(index.embeddings)
        self.assertEqual(len(index.dish_to_idx), 237)
        self.assertEqual(len(index.dishes), 1518)
        self.assertEqual(index.embeddings.shape[1], 512)

    def test_explicit_v2_still_rejects_unapproved_hash(self):
        index_path = (
            BACKEND_DIR.parent
            / "datasets"
            / "recognition_v2"
            / "dish_index.json"
        )
        embeddings_path = index_path.with_name("dish_index_embeddings.npy")

        with self.assertRaisesRegex(
            RecognitionIndexConfigurationError,
            "does not match the approved SHA-256",
        ):
            DishIndex(
                index_file=str(index_path),
                embeddings_file=str(embeddings_path),
                configured_version="v2",
                expected_schema_version=2,
                expected_index_sha256="0" * 64,
                expected_embeddings_sha256=APPROVED_V2_EMBEDDINGS_SHA256,
                expected_visual_classes=APPROVED_V2_VISUAL_CLASSES,
                expected_embeddings=APPROVED_V2_EMBEDDINGS,
                expected_embedding_dim=APPROVED_V2_EMBEDDING_DIM,
                strict_load=True,
            )


class IndexStatusObservabilityTest(unittest.TestCase):
    def test_ai_status_exposes_version_hashes_and_counts(self):
        class FakeIndex:
            def get_stats(self):
                return {
                    "ready": True,
                    "total_dishes": APPROVED_V2_VISUAL_CLASSES,
                    "total_visual_classes": APPROVED_V2_VISUAL_CLASSES,
                    "total_embeddings": APPROVED_V2_EMBEDDINGS,
                    "embedding_dim": APPROVED_V2_EMBEDDING_DIM,
                    "recognition_index_version": "v2",
                    "index_metadata_sha256": APPROVED_V2_INDEX_SHA256,
                    "embeddings_sha256": APPROVED_V2_EMBEDDINGS_SHA256,
                }

        with patch("ai.index.get_index", return_value=FakeIndex()):
            response = asyncio.run(server.ai_status())

        self.assertTrue(response.ok)
        self.assertEqual(response.recognition_index_version, "v2")
        self.assertEqual(
            response.total_visual_classes, APPROVED_V2_VISUAL_CLASSES
        )
        self.assertEqual(response.total_embeddings, APPROVED_V2_EMBEDDINGS)
        self.assertEqual(
            response.embedding_dimension, APPROVED_V2_EMBEDDING_DIM
        )
        self.assertEqual(
            response.index_metadata_sha256, APPROVED_V2_INDEX_SHA256
        )
        self.assertEqual(
            response.embeddings_sha256, APPROVED_V2_EMBEDDINGS_SHA256
        )


if __name__ == "__main__":
    unittest.main()
