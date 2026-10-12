"""Backend-only response integration for legacy v1 and visual index v2.

This module deliberately has no database, network, or model side effects. It
joins validated index artifacts with the pure variant resolver and the isolated
visual cache, producing a backward-compatible response dictionary.
"""

import copy
from typing import Any, Dict, Mapping, Optional, Sequence

from .families import (
    VariantEvidence,
    get_visual_family,
    load_visual_taxonomy,
    resolve_display_variant,
)
from .index_loader import LoadedIndexArtifacts


class RecognitionResponseIntegrationError(ValueError):
    """Raised when a v2 visual decision cannot be mapped safely."""


def _require_decision(decision: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(decision, Mapping):
        raise RecognitionResponseIntegrationError("decision must be a mapping")
    return copy.deepcopy(dict(decision))


def _decision_visual_class(decision: Mapping[str, Any]) -> tuple[Optional[str], Optional[str]]:
    declared = decision.get("visual_class")
    if declared is None:
        name = decision.get("dish") or decision.get("dish_display")
        return None, name if isinstance(name, str) and name else None
    if isinstance(declared, str):
        return None, declared if declared else None
    if not isinstance(declared, Mapping):
        raise RecognitionResponseIntegrationError(
            "visual_class must be a string or mapping"
        )
    class_id = declared.get("id")
    class_name = declared.get("name")
    if class_id is not None and (not isinstance(class_id, str) or not class_id):
        raise RecognitionResponseIntegrationError("visual_class.id must be text")
    if not isinstance(class_name, str) or not class_name:
        raise RecognitionResponseIntegrationError("visual_class.name must be text")
    return class_id, class_name


def _provenance_visual_class_id(
    artifacts: LoadedIndexArtifacts, visual_class_name: str
) -> str:
    class_ids = {
        item.get("visual_class_id")
        for item in artifacts.provenance
        if item.get("visual_class") == visual_class_name
    }
    class_ids.discard(None)
    if len(class_ids) != 1:
        raise RecognitionResponseIntegrationError(
            "v2 visual class must map to exactly one provenance class id"
        )
    return next(iter(class_ids))


def _safe_display_name(visual_class: str, display_variant: Optional[str]) -> str:
    if display_variant is None:
        return visual_class
    return f"{visual_class} — {display_variant}"


def assemble_identification_response(
    decision: Mapping[str, Any],
    artifacts: LoadedIndexArtifacts,
    *,
    evidence: Sequence[VariantEvidence] = (),
    taxonomy: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble one backend response without changing visual ranking/confidence.

    V1 decisions are returned with exactly their legacy fields.  V2 decisions
    gain optional visual-family fields.  Variant evidence is resolved only by
    the pure allowlist resolver; it never participates in ranking or score.
    """
    response = _require_decision(decision)
    if not isinstance(artifacts, LoadedIndexArtifacts):
        raise RecognitionResponseIntegrationError(
            "artifacts must be LoadedIndexArtifacts"
        )

    if artifacts.schema_version == 1:
        return response
    if artifacts.schema_version != 2:
        raise RecognitionResponseIntegrationError(
            f"unsupported recognition schema: {artifacts.schema_version}"
        )

    original_score = copy.deepcopy(response.get("score"))
    original_confidence = copy.deepcopy(response.get("confidence"))
    declared_class_id, visual_class_name = _decision_visual_class(response)

    if not response.get("identified") or visual_class_name is None:
        response.update(
            {
                "recognition_schema_version": 2,
                "visual_class": None,
                "display_variant": None,
                "variant_source": None,
                "variant_status": "absent",
                "variant_evidence_id": None,
                "variant_evidence_ids": [],
                "variant_reason": "no_identified_visual_class",
            }
        )
        return response

    if visual_class_name not in artifacts.dish_to_idx:
        raise RecognitionResponseIntegrationError(
            "identified visual class is not present in loaded v2 artifacts"
        )

    provenance_class_id = _provenance_visual_class_id(
        artifacts, visual_class_name
    )
    if declared_class_id is not None and declared_class_id != provenance_class_id:
        raise RecognitionResponseIntegrationError(
            "declared visual class id conflicts with index provenance"
        )

    visual_taxonomy = taxonomy if taxonomy is not None else load_visual_taxonomy()
    family = get_visual_family(visual_taxonomy, provenance_class_id)
    if family is None:
        if get_visual_family(visual_taxonomy, visual_class_name) is not None:
            raise RecognitionResponseIntegrationError(
                "visual class is inconsistent with the loaded taxonomy"
            )
        resolution = resolve_display_variant(
            visual_taxonomy, visual_class_name, evidence
        )
    elif family.get("canonical_name") != visual_class_name:
        raise RecognitionResponseIntegrationError(
            "visual class is inconsistent with the loaded taxonomy"
        )
    else:
        resolution = resolve_display_variant(
            visual_taxonomy, provenance_class_id, evidence
        )
    evidence_ids = list(resolution.variant_evidence_ids)
    display_name = _safe_display_name(
        visual_class_name, resolution.display_variant
    )

    response.update(
        {
            "recognition_schema_version": 2,
            "visual_class": {
                "id": provenance_class_id,
                "name": visual_class_name,
            },
            "display_variant": resolution.display_variant,
            "variant_source": resolution.variant_source,
            "variant_status": resolution.variant_status,
            "variant_evidence_id": (
                evidence_ids[0] if len(evidence_ids) == 1 else None
            ),
            "variant_evidence_ids": evidence_ids,
            "variant_reason": resolution.reason,
            "dish": visual_class_name,
            "dish_display": display_name,
            "index_version": artifacts.index_metadata.get("index_id")
            or artifacts.index_metadata.get("version"),
            "taxonomy_version": artifacts.index_metadata.get("taxonomy_version"),
        }
    )

    if response.get("score") != original_score:
        raise RecognitionResponseIntegrationError(
            "variant integration changed visual score"
        )
    if response.get("confidence") != original_confidence:
        raise RecognitionResponseIntegrationError(
            "variant integration changed visual confidence"
        )
    return response


def _visual_cache_context(artifacts: LoadedIndexArtifacts):
    from services.cache_service import VisualCacheContext

    metadata = artifacts.index_metadata
    required = {
        "index_version": metadata.get("index_id") or metadata.get("version"),
        "model_version": metadata.get("model_version"),
        "preprocessing_version": metadata.get("preprocessing_version"),
        "taxonomy_version": metadata.get("taxonomy_version"),
    }
    missing = [field for field, value in required.items() if not value]
    if missing:
        raise RecognitionResponseIntegrationError(
            "v2 cache context is incomplete: " + ", ".join(sorted(missing))
        )
    return VisualCacheContext(schema_version=2, **required)


def get_cached_identification_response(
    image_bytes: bytes,
    artifacts: LoadedIndexArtifacts,
    *,
    evidence: Sequence[VariantEvidence] = (),
    taxonomy: Optional[Mapping[str, Any]] = None,
    restaurant: str = "",
) -> Optional[Dict[str, Any]]:
    """Resolve current-request evidence over a cached v2 visual decision."""
    if not isinstance(artifacts, LoadedIndexArtifacts):
        raise RecognitionResponseIntegrationError(
            "artifacts must be LoadedIndexArtifacts"
        )
    if artifacts.schema_version != 2:
        return None

    from services.cache_service import get_cached_visual_decision

    cached = get_cached_visual_decision(
        image_bytes,
        _visual_cache_context(artifacts),
        restaurant=restaurant,
    )
    if cached is None:
        return None
    response = assemble_identification_response(
        cached,
        artifacts,
        evidence=evidence,
        taxonomy=taxonomy,
    )
    response["from_visual_cache"] = True
    return response


def assemble_identification_response_with_visual_cache(
    image_bytes: bytes,
    artifacts: LoadedIndexArtifacts,
    *,
    decision: Optional[Mapping[str, Any]] = None,
    evidence: Sequence[VariantEvidence] = (),
    taxonomy: Optional[Mapping[str, Any]] = None,
    restaurant: str = "",
) -> Dict[str, Any]:
    """Reuse a v2 visual decision and resolve variant per current request.

    Legacy v1 bypasses this namespace and preserves the existing response.
    The v2 cache stores only the stable visual decision; variant evidence is
    always applied again for the current request.
    """
    if not isinstance(artifacts, LoadedIndexArtifacts):
        raise RecognitionResponseIntegrationError(
            "artifacts must be LoadedIndexArtifacts"
        )
    if artifacts.schema_version == 1:
        if decision is None:
            raise RecognitionResponseIntegrationError(
                "legacy v1 requires the current decision"
            )
        return assemble_identification_response(
            decision, artifacts, evidence=evidence, taxonomy=taxonomy
        )

    from services.cache_service import cache_visual_decision

    cached_response = get_cached_identification_response(
        image_bytes,
        artifacts,
        evidence=evidence,
        taxonomy=taxonomy,
        restaurant=restaurant,
    )
    if cached_response is not None:
        return cached_response
    if decision is None:
        raise RecognitionResponseIntegrationError(
            "v2 cache miss requires the current visual decision"
        )
    visual_decision = assemble_identification_response(
        decision, artifacts, evidence=(), taxonomy=taxonomy
    )
    cache_visual_decision(
        image_bytes,
        visual_decision,
        _visual_cache_context(artifacts),
        restaurant=restaurant,
    )
    response = assemble_identification_response(
        visual_decision,
        artifacts,
        evidence=evidence,
        taxonomy=taxonomy,
    )
    response["from_visual_cache"] = False
    return response
