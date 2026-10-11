"""Strict, side-effect-free loader for legacy v1 and candidate v2 indexes.

This module is intentionally not connected to ``DishIndex`` or the identify
route. It validates complete JSON/NPY pairs and returns an internal normalized
view for isolated compatibility tests and later integration gates.
"""

import copy
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Mapping, Optional, Tuple, Union

import numpy as np

from .families import get_visual_family, load_visual_taxonomy
from .index_builder_v2 import (
    BUILDER_VERSION,
    EMBEDDING_DIM,
    RECOGNITION_SCHEMA_VERSION,
)


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_V2_ONLY_FIELDS = {
    "embedding_dim",
    "index_id",
    "provenance",
    "references",
    "variants",
    "visual_classes",
}


class IndexArtifactValidationError(ValueError):
    """Raised when an index pair cannot be trusted."""


@dataclass(frozen=True)
class LoadedIndexArtifacts:
    """Normalized, immutable metadata around a read-only embedding matrix."""

    schema_version: int
    embeddings: np.ndarray
    visual_labels: Tuple[str, ...]
    dish_to_idx: Mapping[str, Tuple[int, ...]]
    provenance: Tuple[Mapping[str, Any], ...]
    legacy_metadata: Mapping[str, Any]
    index_metadata: Mapping[str, Any]


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IndexArtifactValidationError(f"{field} must be a non-empty string")
    if value != value.strip():
        raise IndexArtifactValidationError(
            f"{field} must not contain surrounding whitespace"
        )
    return value


def _require_int(value: Any, field: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise IndexArtifactValidationError(
            f"{field} must be an integer >= {minimum}"
        )
    return value


def _require_sha256(value: Any, field: str) -> str:
    text = _require_text(value, field)
    if not _SHA256_RE.fullmatch(text):
        raise IndexArtifactValidationError(f"{field} must be a lowercase SHA-256")
    return text


def _require_safe_relative_path(value: Any, field: str) -> str:
    text = unicodedata.normalize("NFC", _require_text(value, field)).replace(
        "\\", "/"
    )
    path = PurePosixPath(text)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise IndexArtifactValidationError(f"{field} must be a safe relative path")
    normalized = path.as_posix()
    if normalized != value:
        raise IndexArtifactValidationError(f"{field} must already be normalized")
    return normalized


def _load_json(index_path: Path) -> Dict[str, Any]:
    if not index_path.exists() or not index_path.is_file():
        raise IndexArtifactValidationError(f"index JSON does not exist: {index_path}")
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IndexArtifactValidationError(
            f"invalid index JSON at line {exc.lineno}, column {exc.colno}"
        ) from exc
    except OSError as exc:
        raise IndexArtifactValidationError(
            f"unable to read index JSON: {index_path}"
        ) from exc
    if not isinstance(data, dict):
        raise IndexArtifactValidationError("index JSON root must be an object")
    return data


def _load_embeddings(embeddings_path: Path) -> np.ndarray:
    if not embeddings_path.exists() or not embeddings_path.is_file():
        raise IndexArtifactValidationError(
            f"embeddings NPY does not exist: {embeddings_path}"
        )
    try:
        embeddings = np.load(embeddings_path, allow_pickle=False)
    except Exception as exc:
        raise IndexArtifactValidationError("unable to load embeddings NPY") from exc
    if not isinstance(embeddings, np.ndarray) or embeddings.ndim != 2:
        raise IndexArtifactValidationError("embeddings must be a 2D NumPy array")
    if not np.issubdtype(embeddings.dtype, np.number):
        raise IndexArtifactValidationError("embeddings dtype must be numeric")
    if not np.isfinite(embeddings).all():
        raise IndexArtifactValidationError("embeddings must contain finite values")
    embeddings.setflags(write=False)
    return embeddings


def _paired_embeddings_path(index_path: Path) -> Path:
    if index_path.suffix.lower() != ".json":
        raise IndexArtifactValidationError("index path must end with .json")
    return index_path.with_name(f"{index_path.stem}_embeddings.npy")


def _detect_schema(data: Mapping[str, Any]) -> int:
    if "recognition_schema_version" in data:
        schema_version = data["recognition_schema_version"]
        if type(schema_version) is not int:
            raise IndexArtifactValidationError(
                "recognition_schema_version must be an integer"
            )
        if schema_version != RECOGNITION_SCHEMA_VERSION:
            raise IndexArtifactValidationError(
                f"unsupported recognition_schema_version: {schema_version}"
            )
        return schema_version

    v2_fields = sorted(_V2_ONLY_FIELDS.intersection(data))
    if v2_fields:
        raise IndexArtifactValidationError(
            "recognition_schema_version is required for v2 fields: "
            + ", ".join(v2_fields)
        )
    return 1


def _validate_labels_and_mapping(
    data: Mapping[str, Any], embeddings: np.ndarray
) -> Tuple[Tuple[str, ...], Dict[str, Tuple[int, ...]]]:
    dishes = data.get("dishes")
    if not isinstance(dishes, list):
        raise IndexArtifactValidationError("dishes must be a list")
    labels = tuple(
        _require_text(label, f"dishes[{index}]")
        for index, label in enumerate(dishes)
    )
    if len(labels) != embeddings.shape[0]:
        raise IndexArtifactValidationError(
            "embedding row count must match dishes count"
        )

    raw_mapping = data.get("dish_to_idx")
    if not isinstance(raw_mapping, dict):
        raise IndexArtifactValidationError("dish_to_idx must be an object")
    mapping: Dict[str, Tuple[int, ...]] = {}
    all_indices = []
    for label, raw_indices in raw_mapping.items():
        class_name = _require_text(label, "dish_to_idx key")
        if not isinstance(raw_indices, list):
            raise IndexArtifactValidationError(
                f"dish_to_idx[{class_name}] must be a list"
            )
        indices = tuple(
            _require_int(value, f"dish_to_idx[{class_name}]", minimum=0)
            for value in raw_indices
        )
        if len(indices) != len(set(indices)):
            raise IndexArtifactValidationError(
                f"dish_to_idx[{class_name}] contains duplicate indices"
            )
        for index in indices:
            if index >= len(labels) or labels[index] != class_name:
                raise IndexArtifactValidationError(
                    f"dish_to_idx[{class_name}] is not aligned with dishes"
                )
        mapping[class_name] = indices
        all_indices.extend(indices)

    if sorted(all_indices) != list(range(len(labels))):
        raise IndexArtifactValidationError(
            "dish_to_idx must cover every embedding index exactly once"
        )
    return labels, mapping


def _validate_declared_counts(
    data: Mapping[str, Any], labels: Tuple[str, ...], mapping: Mapping[str, Any]
) -> None:
    if "total_items" in data:
        total_items = _require_int(data["total_items"], "total_items")
        if total_items != len(labels):
            raise IndexArtifactValidationError("total_items does not match dishes")
    if "total_dishes" in data:
        total_dishes = _require_int(data["total_dishes"], "total_dishes")
        if total_dishes != len(mapping):
            raise IndexArtifactValidationError(
                "total_dishes does not match dish_to_idx"
            )


def _validate_legacy_v1(
    data: Mapping[str, Any], embeddings: np.ndarray
) -> LoadedIndexArtifacts:
    labels, mapping = _validate_labels_and_mapping(data, embeddings)
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise IndexArtifactValidationError("metadata must be an object")
    _validate_declared_counts(data, labels, mapping)
    return LoadedIndexArtifacts(
        schema_version=1,
        embeddings=embeddings,
        visual_labels=labels,
        dish_to_idx=mapping,
        provenance=(),
        legacy_metadata=copy.deepcopy(metadata),
        index_metadata={
            "version": data.get("version"),
            "total_items": len(labels),
            "total_dishes": len(mapping),
        },
    )


def _validate_top_level_v2(
    data: Mapping[str, Any],
    embeddings: np.ndarray,
    labels: Tuple[str, ...],
    mapping: Mapping[str, Any],
) -> None:
    if data.get("version") != "2.0":
        raise IndexArtifactValidationError("v2 version must be 2.0")
    _require_text(data.get("index_id"), "index_id")
    _validate_declared_counts(data, labels, mapping)
    declared_dim = _require_int(data.get("embedding_dim"), "embedding_dim", minimum=1)
    if declared_dim != EMBEDDING_DIM or embeddings.shape[1] != EMBEDDING_DIM:
        raise IndexArtifactValidationError(
            f"v2 embedding dimension must be {EMBEDDING_DIM}"
        )
    metadata = data.get("metadata")
    visual_classes = data.get("visual_classes")
    variants = data.get("variants")
    if not isinstance(metadata, dict):
        raise IndexArtifactValidationError("metadata must be an object")
    if not isinstance(visual_classes, dict) or not visual_classes:
        raise IndexArtifactValidationError("visual_classes must be a non-empty object")
    if not isinstance(variants, dict):
        raise IndexArtifactValidationError("variants must be an object")
    for class_name, indices in mapping.items():
        class_metadata = metadata.get(class_name)
        if not isinstance(class_metadata, dict):
            raise IndexArtifactValidationError(
                f"metadata is missing for visual class: {class_name}"
            )
        if class_metadata.get("image_count") != len(indices):
            raise IndexArtifactValidationError(
                f"metadata image_count mismatch for visual class: {class_name}"
            )


def _validate_v2_provenance_header(
    data: Mapping[str, Any], embeddings_path: Path
) -> Mapping[str, Any]:
    provenance = data.get("provenance")
    if not isinstance(provenance, dict):
        raise IndexArtifactValidationError("provenance must be an object")
    for field in (
        "source_corpus_id",
        "source_corpus_version",
        "taxonomy_version",
        "model_identifier",
        "model_version",
        "preprocessing_version",
        "builder_version",
    ):
        _require_text(provenance.get(field), f"provenance.{field}")
    for field in (
        "corpus_manifest_sha256",
        "selection_manifest_sha256",
        "taxonomy_sha256",
        "embeddings_sha256",
        "model_sha256",
    ):
        _require_sha256(provenance.get(field), f"provenance.{field}")
    if provenance["builder_version"] != BUILDER_VERSION:
        raise IndexArtifactValidationError(
            f"unsupported builder_version: {provenance['builder_version']}"
        )
    actual_embeddings_sha = hashlib.sha256(embeddings_path.read_bytes()).hexdigest()
    if provenance["embeddings_sha256"] != actual_embeddings_sha:
        raise IndexArtifactValidationError("embeddings SHA-256 mismatch")
    return provenance


def _validate_v2_reference(
    reference: Any,
    embedding_index: int,
    labels: Tuple[str, ...],
    data: Mapping[str, Any],
    taxonomy: Mapping[str, Any],
    provenance_header: Mapping[str, Any],
) -> Dict[str, Any]:
    prefix = f"references[{embedding_index}]"
    if not isinstance(reference, dict):
        raise IndexArtifactValidationError(f"{prefix} must be an object")
    declared_index = _require_int(
        reference.get("embedding_index"), f"{prefix}.embedding_index"
    )
    if declared_index != embedding_index:
        raise IndexArtifactValidationError(
            f"{prefix}.embedding_index must align with its array position"
        )
    class_id = _require_text(
        reference.get("visual_class_id"), f"{prefix}.visual_class_id"
    )
    class_name = _require_text(
        reference.get("visual_class"), f"{prefix}.visual_class"
    )
    if labels[embedding_index] != class_name:
        raise IndexArtifactValidationError(
            f"{prefix}.visual_class does not match dishes"
        )
    family = get_visual_family(taxonomy, class_id)
    if family is not None and family.get("canonical_name") != class_name:
        raise IndexArtifactValidationError(
            f"{prefix} references a mismatched visual family"
        )
    if family is None:
        family_by_name = get_visual_family(taxonomy, class_name)
        if family_by_name is not None:
            raise IndexArtifactValidationError(
                f"{prefix} references a mismatched visual family"
            )
        for external_class in taxonomy.get("external_visual_classes", []):
            id_matches = external_class.get("visual_class_id") == class_id
            name_matches = external_class.get("canonical_name") == class_name
            if id_matches != name_matches:
                raise IndexArtifactValidationError(
                    f"{prefix} references a mismatched external visual class"
                )
    visual_class_entry = data["visual_classes"].get(class_id)
    if (
        not isinstance(visual_class_entry, dict)
        or visual_class_entry.get("canonical_name") != class_name
    ):
        raise IndexArtifactValidationError(
            f"{prefix} is inconsistent with visual_classes"
        )
    configured_variants = family["variants"] if family is not None else []
    configured_exclusions = (
        family.get("must_not_group", []) if family is not None else []
    )
    allowed_variant_ids = [item["id"] for item in configured_variants]
    if visual_class_entry.get("variant_ids") != allowed_variant_ids:
        raise IndexArtifactValidationError(
            f"{prefix} has variant_ids inconsistent with taxonomy"
        )
    if visual_class_entry.get("must_not_group") != configured_exclusions:
        raise IndexArtifactValidationError(
            f"{prefix} has exclusions inconsistent with taxonomy"
        )
    for variant in configured_variants:
        indexed_variant = data["variants"].get(variant["id"])
        if (
            not isinstance(indexed_variant, dict)
            or indexed_variant.get("display_name") != variant["display_name"]
            or indexed_variant.get("visual_class_id") != class_id
        ):
            raise IndexArtifactValidationError(
                f"{prefix} has variant metadata inconsistent with taxonomy"
            )

    class_metadata = data["metadata"].get(class_name)
    if not isinstance(class_metadata, dict):
        raise IndexArtifactValidationError(
            f"{prefix} has no class metadata"
        )
    if (
        class_metadata.get("visual_class_id") != class_id
        or class_metadata.get("canonical_name") != class_name
        or class_metadata.get("allowed_variant_ids") != allowed_variant_ids
    ):
        raise IndexArtifactValidationError(
            f"{prefix} is inconsistent with class metadata"
        )

    relative_path = _require_safe_relative_path(
        reference.get("source_relative_path"), f"{prefix}.source_relative_path"
    )
    filename = _require_text(
        reference.get("source_filename"), f"{prefix}.source_filename"
    )
    if PurePosixPath(relative_path).name != filename:
        raise IndexArtifactValidationError(
            f"{prefix}.source_filename does not match relative path"
        )
    _require_sha256(reference.get("source_sha256"), f"{prefix}.source_sha256")
    _require_int(reference.get("source_bytes"), f"{prefix}.source_bytes")

    source_variant_id = reference.get("source_variant_id")
    if source_variant_id is None:
        if reference.get("source_variant_status") is not None or reference.get(
            "source_variant_source"
        ) is not None:
            raise IndexArtifactValidationError(
                f"{prefix} has variant provenance without source_variant_id"
            )
    else:
        if source_variant_id not in allowed_variant_ids:
            raise IndexArtifactValidationError(
                f"{prefix}.source_variant_id is not allowed by taxonomy"
            )
        _require_text(
            reference.get("source_variant_status"),
            f"{prefix}.source_variant_status",
        )
        _require_text(
            reference.get("source_variant_source"),
            f"{prefix}.source_variant_source",
        )

    required_matches = {
        "recognition_schema_version": RECOGNITION_SCHEMA_VERSION,
        "builder_version": provenance_header["builder_version"],
        "preprocessing_version": provenance_header["preprocessing_version"],
        "model_identifier": provenance_header["model_identifier"],
        "model_version": provenance_header["model_version"],
        "source_corpus_id": provenance_header["source_corpus_id"],
        "source_corpus_version": provenance_header["source_corpus_version"],
    }
    for field, expected in required_matches.items():
        if reference.get(field) != expected:
            raise IndexArtifactValidationError(
                f"{prefix}.{field} does not match top-level provenance"
            )
    return copy.deepcopy(reference)


def _validate_v2(
    data: Mapping[str, Any],
    embeddings: np.ndarray,
    embeddings_path: Path,
    taxonomy: Mapping[str, Any],
) -> LoadedIndexArtifacts:
    labels, mapping = _validate_labels_and_mapping(data, embeddings)
    _validate_top_level_v2(data, embeddings, labels, mapping)
    provenance_header = _validate_v2_provenance_header(data, embeddings_path)
    if provenance_header["taxonomy_version"] != taxonomy.get("taxonomy_version"):
        raise IndexArtifactValidationError("taxonomy version mismatch")

    references = data.get("references")
    if not isinstance(references, list):
        raise IndexArtifactValidationError("references must be a list")
    if len(references) != embeddings.shape[0]:
        raise IndexArtifactValidationError(
            "embedding row count must match provenance reference count"
        )

    normalized_references = []
    seen_sha = set()
    for embedding_index, reference in enumerate(references):
        normalized = _validate_v2_reference(
            reference,
            embedding_index,
            labels,
            data,
            taxonomy,
            provenance_header,
        )
        source_sha = normalized["source_sha256"]
        if source_sha in seen_sha:
            raise IndexArtifactValidationError(
                f"duplicate embedding provenance SHA-256: {source_sha}"
            )
        seen_sha.add(source_sha)
        normalized_references.append(normalized)

    metadata = data["metadata"]
    return LoadedIndexArtifacts(
        schema_version=RECOGNITION_SCHEMA_VERSION,
        embeddings=embeddings,
        visual_labels=labels,
        dish_to_idx=mapping,
        provenance=tuple(normalized_references),
        legacy_metadata=copy.deepcopy(metadata),
        index_metadata={
            "version": data["version"],
            "index_id": data["index_id"],
            "total_items": len(labels),
            "total_dishes": len(mapping),
            "embedding_dim": embeddings.shape[1],
            "builder_version": provenance_header["builder_version"],
            "model_identifier": provenance_header["model_identifier"],
            "model_version": provenance_header["model_version"],
            "preprocessing_version": provenance_header["preprocessing_version"],
            "taxonomy_version": provenance_header["taxonomy_version"],
        },
    )


def load_index_artifacts(
    index_file: Union[str, Path],
    embeddings_file: Optional[Union[str, Path]] = None,
    *,
    taxonomy: Optional[Mapping[str, Any]] = None,
) -> LoadedIndexArtifacts:
    """Load and strictly validate one complete v1 or v2 JSON/NPY pair."""
    index_path = Path(index_file)
    embeddings_path = (
        Path(embeddings_file)
        if embeddings_file is not None
        else _paired_embeddings_path(index_path)
    )
    data = _load_json(index_path)
    embeddings = _load_embeddings(embeddings_path)
    schema_version = _detect_schema(data)
    if schema_version == 1:
        return _validate_legacy_v1(data, embeddings)

    visual_taxonomy = taxonomy if taxonomy is not None else load_visual_taxonomy()
    return _validate_v2(data, embeddings, embeddings_path, visual_taxonomy)
