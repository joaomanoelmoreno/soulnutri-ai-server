"""Deterministic, write-free building blocks for a future visual index v2.

This module does not load an embedding model and does not write JSON or NPY
artifacts. It prepares and validates deterministic selections plus portable
per-embedding provenance for a later, explicitly invoked builder stage.
"""

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from .families import get_visual_family


RECOGNITION_SCHEMA_VERSION = 2
BUILDER_VERSION = "visual-index-builder-v2"
EMBEDDING_DIM = 512
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class VisualIndexBuilderError(ValueError):
    """Raised when a v2 build input is incomplete or inconsistent."""


@dataclass(frozen=True)
class ImageReference:
    """Portable source-image provenance before an embedding is generated."""

    visual_class_id: str
    visual_class: str
    source_relative_path: str
    source_filename: str
    source_sha256: str
    source_bytes: int
    source_variant_id: Optional[str] = None
    source_variant_status: Optional[str] = None
    source_variant_source: Optional[str] = None
    legacy_label: Optional[str] = None
    original_class: Optional[str] = None
    human_decision_refs: Tuple[str, ...] = ()
    duplicate_source_paths: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ClassSelectionStats:
    """Deterministic counts for one visual class."""

    visual_class_id: str
    visual_class: str
    total_paths: int
    unique_sha256: int
    selected: int


@dataclass(frozen=True)
class SelectionResult:
    """Stable reference order and its content-derived manifest hash."""

    references: Tuple[ImageReference, ...]
    class_stats: Tuple[ClassSelectionStats, ...]
    manifest_sha256: str


@dataclass(frozen=True)
class BuilderContext:
    """Explicit versions/hashes required by the portable v2 structure."""

    index_id: str
    recognition_schema_version: int
    builder_version: str
    preprocessing_version: str
    model_identifier: str
    model_version: str
    model_sha256: str
    source_corpus_id: str
    source_corpus_version: str
    source_corpus_manifest_sha256: str
    taxonomy_sha256: str
    embeddings_sha256: str


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VisualIndexBuilderError(f"{field} must be a non-empty string")
    if value != value.strip():
        raise VisualIndexBuilderError(
            f"{field} must not contain surrounding whitespace"
        )
    return value


def _require_sha256(value: Any, field: str) -> str:
    text = _require_text(value, field)
    if not _SHA256_RE.fullmatch(text):
        raise VisualIndexBuilderError(f"{field} must be a lowercase SHA-256")
    return text


def _normalize_relative_path(value: Any, field: str) -> str:
    text = unicodedata.normalize("NFC", _require_text(value, field)).replace(
        "\\", "/"
    )
    path = PurePosixPath(text)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise VisualIndexBuilderError(f"{field} must be a safe relative path")
    return path.as_posix()


def _validate_variant_provenance(
    reference: ImageReference, family: Optional[Mapping[str, Any]]
) -> None:
    variant_id = reference.source_variant_id
    supporting_fields = (
        reference.source_variant_status,
        reference.source_variant_source,
    )
    if variant_id is None:
        if any(value is not None for value in supporting_fields):
            raise VisualIndexBuilderError(
                "variant status/source require source_variant_id"
            )
        return

    if family is None:
        raise VisualIndexBuilderError(
            "source_variant_id requires a configured visual family"
        )

    if variant_id in set(family.get("must_not_group", [])):
        raise VisualIndexBuilderError(
            f"explicitly excluded source_variant_id for "
            f"{reference.visual_class}: {variant_id}"
        )

    allowed_ids = {variant["id"] for variant in family["variants"]}
    if variant_id not in allowed_ids:
        raise VisualIndexBuilderError(
            f"unknown source_variant_id for {reference.visual_class}: {variant_id}"
        )
    _require_text(reference.source_variant_status, "source_variant_status")
    _require_text(reference.source_variant_source, "source_variant_source")


def validate_image_reference(
    reference: ImageReference, taxonomy: Mapping[str, Any]
) -> ImageReference:
    """Validate one source reference without repairing its provenance."""
    if not isinstance(reference, ImageReference):
        raise VisualIndexBuilderError("reference must be an ImageReference")

    class_id = _require_text(reference.visual_class_id, "visual_class_id")
    class_name = _require_text(reference.visual_class, "visual_class")
    family = get_visual_family(taxonomy, class_id)
    if family is not None and (
        family.get("visual_class_id") != class_id
        or family.get("canonical_name") != class_name
    ):
        raise VisualIndexBuilderError(
            f"unknown or mismatched visual_class: {class_id}"
        )
    family_by_name = get_visual_family(taxonomy, class_name)
    if family is None and family_by_name is not None:
        raise VisualIndexBuilderError(
            f"unknown or mismatched visual_class: {class_id}"
        )
    for external_class in taxonomy.get("external_visual_classes", []):
        id_matches = external_class.get("visual_class_id") == class_id
        name_matches = external_class.get("canonical_name") == class_name
        if id_matches != name_matches:
            raise VisualIndexBuilderError(
                f"unknown or mismatched visual_class: {class_id}"
            )

    relative_path = _normalize_relative_path(
        reference.source_relative_path, "source_relative_path"
    )
    if relative_path != reference.source_relative_path:
        raise VisualIndexBuilderError(
            "source_relative_path must already be normalized"
        )
    filename = _require_text(reference.source_filename, "source_filename")
    if PurePosixPath(relative_path).name != filename:
        raise VisualIndexBuilderError(
            "source_filename must match source_relative_path"
        )
    if Path(filename).suffix.lower() not in IMAGE_EXTENSIONS:
        raise VisualIndexBuilderError(f"unsupported image extension: {filename}")
    _require_sha256(reference.source_sha256, "source_sha256")
    if type(reference.source_bytes) is not int or reference.source_bytes < 0:
        raise VisualIndexBuilderError("source_bytes must be a non-negative integer")

    _validate_variant_provenance(reference, family)

    for field in ("legacy_label", "original_class"):
        value = getattr(reference, field)
        if value is not None:
            _require_text(value, field)

    normalized_decisions = []
    for decision in reference.human_decision_refs:
        normalized_decisions.append(_require_text(decision, "human_decision_refs"))
    if len(normalized_decisions) != len(set(normalized_decisions)):
        raise VisualIndexBuilderError("human_decision_refs contains duplicates")
    if tuple(normalized_decisions) != tuple(sorted(normalized_decisions)):
        raise VisualIndexBuilderError("human_decision_refs must be sorted")

    normalized_duplicates = []
    for duplicate_path in reference.duplicate_source_paths:
        normalized_duplicates.append(
            _normalize_relative_path(duplicate_path, "duplicate_source_paths")
        )
    if len(normalized_duplicates) != len(set(normalized_duplicates)):
        raise VisualIndexBuilderError("duplicate_source_paths contains duplicates")
    if tuple(normalized_duplicates) != tuple(reference.duplicate_source_paths):
        raise VisualIndexBuilderError(
            "duplicate_source_paths must already be normalized"
        )
    if tuple(normalized_duplicates) != tuple(sorted(normalized_duplicates)):
        raise VisualIndexBuilderError("duplicate_source_paths must be sorted")
    if relative_path in normalized_duplicates:
        raise VisualIndexBuilderError(
            "duplicate_source_paths must not repeat source_relative_path"
        )

    return reference


def create_image_reference(
    image_path: Path,
    corpus_root: Path,
    taxonomy: Mapping[str, Any],
    *,
    visual_class_id: str,
    source_variant_id: Optional[str] = None,
    source_variant_status: Optional[str] = None,
    source_variant_source: Optional[str] = None,
    legacy_label: Optional[str] = None,
    original_class: Optional[str] = None,
    human_decision_refs: Sequence[str] = (),
) -> ImageReference:
    """Read one existing image and create portable, hash-based provenance."""
    root = Path(corpus_root).resolve()
    source = Path(image_path).resolve()
    if not source.exists() or not source.is_file():
        raise VisualIndexBuilderError(f"image does not exist: {image_path}")
    try:
        relative_path = source.relative_to(root).as_posix()
    except ValueError as exc:
        raise VisualIndexBuilderError("image must be inside corpus_root") from exc

    family = get_visual_family(taxonomy, visual_class_id)
    relative_parts = PurePosixPath(relative_path).parts
    if family is None and len(relative_parts) < 2:
        raise VisualIndexBuilderError(
            "unconfigured visual class image must be inside a class directory"
        )
    class_name = (
        family["canonical_name"] if family is not None else relative_parts[0]
    )

    content = source.read_bytes()
    reference = ImageReference(
        visual_class_id=visual_class_id,
        visual_class=class_name,
        source_relative_path=_normalize_relative_path(
            relative_path, "source_relative_path"
        ),
        source_filename=source.name,
        source_sha256=hashlib.sha256(content).hexdigest(),
        source_bytes=len(content),
        source_variant_id=source_variant_id,
        source_variant_status=source_variant_status,
        source_variant_source=source_variant_source,
        legacy_label=legacy_label,
        original_class=original_class,
        human_decision_refs=tuple(sorted(human_decision_refs)),
    )
    return validate_image_reference(reference, taxonomy)


def _duplicate_provenance_key(reference: ImageReference) -> Tuple[Any, ...]:
    return (
        reference.visual_class_id,
        reference.visual_class,
        reference.source_sha256,
        reference.source_bytes,
        reference.source_variant_id,
        reference.source_variant_status,
        reference.source_variant_source,
        reference.legacy_label,
        reference.original_class,
        tuple(sorted(reference.human_decision_refs)),
    )


def _reference_manifest_entry(reference: ImageReference) -> Dict[str, Any]:
    return {
        "visual_class_id": reference.visual_class_id,
        "visual_class": reference.visual_class,
        "source_relative_path": reference.source_relative_path,
        "source_filename": reference.source_filename,
        "source_sha256": reference.source_sha256,
        "source_bytes": reference.source_bytes,
        "source_variant_id": reference.source_variant_id,
        "source_variant_status": reference.source_variant_status,
        "source_variant_source": reference.source_variant_source,
        "legacy_label": reference.legacy_label,
        "original_class": reference.original_class,
        "human_decision_refs": list(reference.human_decision_refs),
        "duplicate_source_paths": list(reference.duplicate_source_paths),
    }


def _selection_manifest_sha256(
    references: Sequence[ImageReference],
    class_stats: Sequence[ClassSelectionStats],
) -> str:
    payload = {
        "selection_algorithm": "sha256_ascending_then_relative_path_v1",
        "references": [_reference_manifest_entry(item) for item in references],
        "class_stats": [
            {
                "visual_class_id": item.visual_class_id,
                "visual_class": item.visual_class,
                "total_paths": item.total_paths,
                "unique_sha256": item.unique_sha256,
                "selected": item.selected,
            }
            for item in class_stats
        ],
    }
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def select_deterministic_references(
    references: Sequence[ImageReference],
    taxonomy: Mapping[str, Any],
    *,
    max_per_visual_class: int = 10,
) -> SelectionResult:
    """Deduplicate per class, sort by SHA/path, and apply a stable class cap."""
    if type(max_per_visual_class) is not int or max_per_visual_class < 1:
        raise VisualIndexBuilderError(
            "max_per_visual_class must be a positive integer"
        )

    grouped: Dict[str, list] = {}
    for reference in references:
        validate_image_reference(reference, taxonomy)
        grouped.setdefault(reference.visual_class_id, []).append(reference)

    selected = []
    class_stats = []
    for class_id in sorted(grouped):
        class_references = grouped[class_id]
        class_names = {item.visual_class for item in class_references}
        if len(class_names) != 1:
            raise VisualIndexBuilderError(
                f"visual_class_id has inconsistent names: {class_id}"
            )
        by_sha: Dict[str, list] = {}
        for reference in class_references:
            by_sha.setdefault(reference.source_sha256, []).append(reference)

        unique_references = []
        for source_sha256 in sorted(by_sha):
            duplicate_group = sorted(
                by_sha[source_sha256], key=lambda item: item.source_relative_path
            )
            provenance_keys = {
                _duplicate_provenance_key(item) for item in duplicate_group
            }
            if len(provenance_keys) != 1:
                raise VisualIndexBuilderError(
                    "duplicate SHA has inconsistent provenance in visual class "
                    f"{class_id}: {source_sha256}"
                )
            primary = duplicate_group[0]
            duplicate_paths = tuple(
                item.source_relative_path for item in duplicate_group[1:]
            )
            unique_references.append(
                replace(primary, duplicate_source_paths=duplicate_paths)
            )

        unique_references.sort(
            key=lambda item: (item.source_sha256, item.source_relative_path)
        )
        class_selected = unique_references[:max_per_visual_class]
        selected.extend(class_selected)
        class_stats.append(
            ClassSelectionStats(
                visual_class_id=class_id,
                visual_class=class_references[0].visual_class,
                total_paths=len(class_references),
                unique_sha256=len(unique_references),
                selected=len(class_selected),
            )
        )

    references_tuple = tuple(selected)
    stats_tuple = tuple(class_stats)
    return SelectionResult(
        references=references_tuple,
        class_stats=stats_tuple,
        manifest_sha256=_selection_manifest_sha256(
            references_tuple, stats_tuple
        ),
    )


def _validate_builder_context(context: BuilderContext) -> None:
    if not isinstance(context, BuilderContext):
        raise VisualIndexBuilderError("context must be a BuilderContext")
    if context.recognition_schema_version != RECOGNITION_SCHEMA_VERSION:
        raise VisualIndexBuilderError(
            "unsupported recognition_schema_version: "
            f"{context.recognition_schema_version}"
        )
    if context.builder_version != BUILDER_VERSION:
        raise VisualIndexBuilderError(
            f"unsupported builder_version: {context.builder_version}"
        )
    for field in (
        "index_id",
        "preprocessing_version",
        "model_identifier",
        "model_version",
        "source_corpus_id",
        "source_corpus_version",
    ):
        _require_text(getattr(context, field), field)
    for field in (
        "model_sha256",
        "source_corpus_manifest_sha256",
        "taxonomy_sha256",
        "embeddings_sha256",
    ):
        _require_sha256(getattr(context, field), field)


def _validate_embeddings(embeddings: Sequence[Sequence[float]]) -> int:
    if not isinstance(embeddings, Sequence) or isinstance(
        embeddings, (str, bytes, bytearray)
    ):
        raise VisualIndexBuilderError("embeddings must be a sequence")
    embedding_dim = None
    for row_index, row in enumerate(embeddings):
        if not isinstance(row, Sequence) or isinstance(
            row, (str, bytes, bytearray)
        ):
            raise VisualIndexBuilderError(
                f"embedding row {row_index} must be a sequence"
            )
        if not row:
            raise VisualIndexBuilderError(
                f"embedding row {row_index} must not be empty"
            )
        if embedding_dim is None:
            embedding_dim = len(row)
        elif len(row) != embedding_dim:
            raise VisualIndexBuilderError("embedding dimensions are inconsistent")
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise VisualIndexBuilderError("embedding values must be numeric")
            if not math.isfinite(float(value)):
                raise VisualIndexBuilderError("embedding values must be finite")
    final_dimension = embedding_dim or 0
    if final_dimension != EMBEDDING_DIM:
        raise VisualIndexBuilderError(
            f"embedding dimension must be {EMBEDDING_DIM}, got {final_dimension}"
        )
    return final_dimension


def _validate_selection_stats(selection: SelectionResult) -> None:
    selected_by_class: Dict[str, int] = {}
    names_by_class: Dict[str, str] = {}
    for reference in selection.references:
        selected_by_class[reference.visual_class_id] = (
            selected_by_class.get(reference.visual_class_id, 0) + 1
        )
        names_by_class[reference.visual_class_id] = reference.visual_class

    stats_by_class = {}
    for stats in selection.class_stats:
        if stats.visual_class_id in stats_by_class:
            raise VisualIndexBuilderError("duplicate class selection stats")
        stats_by_class[stats.visual_class_id] = stats
        if stats.visual_class != names_by_class.get(stats.visual_class_id):
            raise VisualIndexBuilderError("class selection stats name mismatch")
        if stats.selected != selected_by_class.get(stats.visual_class_id, 0):
            raise VisualIndexBuilderError("class selection stats count mismatch")
        if not (
            stats.total_paths >= stats.unique_sha256 >= stats.selected >= 0
        ):
            raise VisualIndexBuilderError("class selection stats are inconsistent")

    if set(stats_by_class) != set(selected_by_class):
        raise VisualIndexBuilderError("class selection stats coverage mismatch")


def build_v2_index_structure(
    selection: SelectionResult,
    embeddings: Sequence[Sequence[float]],
    taxonomy: Mapping[str, Any],
    context: BuilderContext,
) -> Dict[str, Any]:
    """Assemble a JSON-ready v2 structure without persisting any artifact."""
    if not isinstance(selection, SelectionResult):
        raise VisualIndexBuilderError("selection must be a SelectionResult")
    _validate_builder_context(context)

    for reference in selection.references:
        validate_image_reference(reference, taxonomy)
    _validate_selection_stats(selection)
    expected_manifest_sha = _selection_manifest_sha256(
        selection.references, selection.class_stats
    )
    if selection.manifest_sha256 != expected_manifest_sha:
        raise VisualIndexBuilderError("selection manifest SHA-256 mismatch")
    if len(selection.references) != len(embeddings):
        raise VisualIndexBuilderError(
            "embedding count must match selected reference count"
        )
    embedding_dim = _validate_embeddings(embeddings)

    sha_to_class: Dict[str, str] = {}
    for reference in selection.references:
        prior_class = sha_to_class.setdefault(
            reference.source_sha256, reference.visual_class_id
        )
        if prior_class != reference.visual_class_id:
            raise VisualIndexBuilderError(
                "same SHA cannot have inconsistent embedding provenance: "
                f"{reference.source_sha256}"
            )

    dishes = []
    dish_to_idx: Dict[str, list] = {}
    reference_entries = []
    for embedding_index, reference in enumerate(selection.references):
        dishes.append(reference.visual_class)
        dish_to_idx.setdefault(reference.visual_class, []).append(embedding_index)
        entry = _reference_manifest_entry(reference)
        entry["embedding_index"] = embedding_index
        entry["preprocessing_version"] = context.preprocessing_version
        entry["model_identifier"] = context.model_identifier
        entry["model_version"] = context.model_version
        entry["builder_version"] = context.builder_version
        entry["recognition_schema_version"] = context.recognition_schema_version
        entry["source_corpus_id"] = context.source_corpus_id
        entry["source_corpus_version"] = context.source_corpus_version
        reference_entries.append(entry)

    stats_by_class = {
        item.visual_class_id: item for item in selection.class_stats
    }
    visual_classes = {}
    variants = {}
    metadata = {}
    used_class_ids = {item.visual_class_id for item in selection.references}
    for class_id in sorted(used_class_ids):
        family = get_visual_family(taxonomy, class_id)
        class_name = stats_by_class[class_id].visual_class
        configured_variants = family["variants"] if family is not None else []
        configured_exclusions = (
            list(family.get("must_not_group", []))
            if family is not None
            else []
        )
        visual_classes[class_id] = {
            "canonical_name": class_name,
            "aliases": [],
            "variant_ids": [item["id"] for item in configured_variants],
            "must_not_group": configured_exclusions,
        }
        for variant in configured_variants:
            if (
                variant["id"] in variants
                and variants[variant["id"]]["visual_class_id"] != class_id
            ):
                raise VisualIndexBuilderError(
                    f"variant id is not globally unique: {variant['id']}"
                )
            variants[variant["id"]] = {
                "display_name": variant["display_name"],
                "visual_class_id": class_id,
                "aliases": list(variant.get("aliases", [])),
            }
        stats = stats_by_class[class_id]
        metadata[class_name] = {
            "visual_class_id": class_id,
            "canonical_name": class_name,
            "image_count": len(dish_to_idx[class_name]),
            "total_available": stats.unique_sha256,
            "total_paths": stats.total_paths,
            "allowed_variant_ids": [
                item["id"] for item in configured_variants
            ],
        }

    return {
        "recognition_schema_version": context.recognition_schema_version,
        "version": "2.0",
        "index_id": context.index_id,
        "total_items": len(dishes),
        "total_dishes": len(dish_to_idx),
        "embedding_dim": embedding_dim,
        "dishes": dishes,
        "dish_to_idx": dish_to_idx,
        "metadata": metadata,
        "visual_classes": visual_classes,
        "variants": variants,
        "references": reference_entries,
        "provenance": {
            "source_corpus_id": context.source_corpus_id,
            "source_corpus_version": context.source_corpus_version,
            "corpus_manifest_sha256": context.source_corpus_manifest_sha256,
            "selection_manifest_sha256": selection.manifest_sha256,
            "taxonomy_version": taxonomy["taxonomy_version"],
            "taxonomy_sha256": context.taxonomy_sha256,
            "embeddings_sha256": context.embeddings_sha256,
            "model_identifier": context.model_identifier,
            "model_version": context.model_version,
            "model_sha256": context.model_sha256,
            "preprocessing_version": context.preprocessing_version,
            "builder_version": context.builder_version,
        },
    }
