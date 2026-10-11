"""SoulNutri AI - Familias de Pratos
Baseado nos documentos:
- /app/docs/PLANO_ORGANIZACAO_SOULNUTRI.md
- /app/docs/REVISAO_COMPLETA_SOULNUTRI.md

Familias agrupam pratos VISUALMENTE similares.
Quando o CLIP retorna top matches de uma mesma familia com scores proximos,
o sistema e HONESTO e sugere candidatos ao inves de afirmar.
"""

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple, Union


SUPPORTED_TAXONOMY_SCHEMA_VERSION = 1
DEFAULT_VISUAL_TAXONOMY_PATH = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "recognition_visual_taxonomy.json"
)
_ALLOWED_EVIDENCE_SOURCES = {"human_admin", "structured_metadata", "ocr"}


class VisualTaxonomyValidationError(ValueError):
    """Raised when a visual taxonomy cannot be trusted."""


def _require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VisualTaxonomyValidationError(f"{field} must be a non-empty string")
    if value != value.strip():
        raise VisualTaxonomyValidationError(
            f"{field} must not contain surrounding whitespace"
        )
    return value


def validate_visual_taxonomy(data: Any) -> Dict[str, Any]:
    """Validate a taxonomy without normalizing or repairing its contents."""
    if not isinstance(data, dict):
        raise VisualTaxonomyValidationError("taxonomy root must be an object")

    schema_version = data.get("taxonomy_schema_version")
    if type(schema_version) is not int:
        raise VisualTaxonomyValidationError(
            "taxonomy_schema_version must be an integer"
        )
    if schema_version != SUPPORTED_TAXONOMY_SCHEMA_VERSION:
        raise VisualTaxonomyValidationError(
            f"unsupported taxonomy_schema_version: {schema_version}"
        )

    _require_non_empty_string(data.get("taxonomy_version"), "taxonomy_version")

    families = data.get("families")
    if not isinstance(families, list) or not families:
        raise VisualTaxonomyValidationError("families must be a non-empty list")

    seen_class_ids = set()
    seen_class_names = set()
    exclusions_to_check = []

    external_classes = data.get("external_visual_classes", [])
    if not isinstance(external_classes, list):
        raise VisualTaxonomyValidationError(
            "external_visual_classes must be a list"
        )
    external_class_names = {}
    for external_index, external_class in enumerate(external_classes):
        prefix = f"external_visual_classes[{external_index}]"
        if not isinstance(external_class, dict):
            raise VisualTaxonomyValidationError(f"{prefix} must be an object")
        external_id = _require_non_empty_string(
            external_class.get("visual_class_id"), f"{prefix}.visual_class_id"
        )
        external_name = _require_non_empty_string(
            external_class.get("canonical_name"), f"{prefix}.canonical_name"
        )
        if external_id in external_class_names:
            raise VisualTaxonomyValidationError(
                f"duplicate external visual_class_id: {external_id}"
            )
        if external_name in external_class_names.values():
            raise VisualTaxonomyValidationError(
                f"duplicate external canonical_name: {external_name}"
            )
        external_class_names[external_id] = external_name

    for family_index, family in enumerate(families):
        prefix = f"families[{family_index}]"
        if not isinstance(family, dict):
            raise VisualTaxonomyValidationError(f"{prefix} must be an object")

        class_id = _require_non_empty_string(
            family.get("visual_class_id"), f"{prefix}.visual_class_id"
        )
        class_name = _require_non_empty_string(
            family.get("canonical_name"), f"{prefix}.canonical_name"
        )
        if class_id in seen_class_ids:
            raise VisualTaxonomyValidationError(
                f"duplicate visual_class_id: {class_id}"
            )
        if class_name in seen_class_names:
            raise VisualTaxonomyValidationError(
                f"duplicate visual_class: {class_name}"
            )
        seen_class_ids.add(class_id)
        seen_class_names.add(class_name)

        variants = family.get("variants")
        if not isinstance(variants, list) or not variants:
            raise VisualTaxonomyValidationError(
                f"{prefix}.variants must be a non-empty list"
            )

        variant_ids = set()
        variant_names = set()
        for variant_index, variant in enumerate(variants):
            variant_prefix = f"{prefix}.variants[{variant_index}]"
            if not isinstance(variant, dict):
                raise VisualTaxonomyValidationError(
                    f"{variant_prefix} must be an object"
                )
            variant_id = _require_non_empty_string(
                variant.get("id"), f"{variant_prefix}.id"
            )
            display_name = _require_non_empty_string(
                variant.get("display_name"), f"{variant_prefix}.display_name"
            )
            if variant_id in variant_ids:
                raise VisualTaxonomyValidationError(
                    f"duplicate variant id in {class_name}: {variant_id}"
                )
            if display_name in variant_names:
                raise VisualTaxonomyValidationError(
                    f"duplicate variant in {class_name}: {display_name}"
                )
            variant_ids.add(variant_id)
            variant_names.add(display_name)
            aliases = variant.get("aliases", [])
            if not isinstance(aliases, list):
                raise VisualTaxonomyValidationError(
                    f"{variant_prefix}.aliases must be a list"
                )
            seen_aliases = set()
            for alias_index, alias in enumerate(aliases):
                alias_name = _require_non_empty_string(
                    alias, f"{variant_prefix}.aliases[{alias_index}]"
                )
                if alias_name in seen_aliases:
                    raise VisualTaxonomyValidationError(
                        f"duplicate alias in {class_name}: {alias_name}"
                    )
                if alias_name in variant_ids or alias_name in variant_names:
                    raise VisualTaxonomyValidationError(
                        f"variant alias collides with canonical variant: {alias_name}"
                    )
                seen_aliases.add(alias_name)

        all_aliases = [
            alias
            for variant in variants
            for alias in variant.get("aliases", [])
        ]
        if len(all_aliases) != len(set(all_aliases)):
            raise VisualTaxonomyValidationError(
                f"duplicate variant alias in {class_name}"
            )
        canonical_variant_tokens = variant_ids | variant_names
        alias_collision = canonical_variant_tokens.intersection(all_aliases)
        if alias_collision:
            raise VisualTaxonomyValidationError(
                "variant alias collides with canonical variant: "
                f"{sorted(alias_collision)[0]}"
            )

        variant_aliases = family.get("variant_aliases", {})
        if not isinstance(variant_aliases, dict):
            raise VisualTaxonomyValidationError(
                f"{prefix}.variant_aliases must be an object"
            )
        for alias, target_value in variant_aliases.items():
            alias_name = _require_non_empty_string(
                alias, f"{prefix}.variant_aliases alias"
            )
            target_id = _require_non_empty_string(
                target_value, f"{prefix}.variant_aliases[{alias_name}]"
            )
            if target_id not in variant_ids:
                raise VisualTaxonomyValidationError(
                    f"variant alias {alias_name} targets unknown variant: {target_id}"
                )
            if alias_name in canonical_variant_tokens or alias_name in all_aliases:
                raise VisualTaxonomyValidationError(
                    f"variant alias collides with configured variant: {alias_name}"
                )

        exclusions = family.get("must_not_group", [])
        if not isinstance(exclusions, list):
            raise VisualTaxonomyValidationError(
                f"{prefix}.must_not_group must be a list"
            )
        seen_exclusions = set()
        for exclusion_index, excluded_value in enumerate(exclusions):
            excluded_id = _require_non_empty_string(
                excluded_value,
                f"{prefix}.must_not_group[{exclusion_index}]",
            )
            if excluded_id == class_id:
                raise VisualTaxonomyValidationError(
                    f"visual class cannot exclude itself: {class_name}"
                )
            if excluded_id in seen_exclusions:
                raise VisualTaxonomyValidationError(
                    f"duplicate exclusion in {class_name}: {excluded_id}"
                )
            seen_exclusions.add(excluded_id)
            exclusions_to_check.append((class_name, excluded_id))

        evidence_sources = family.get("accepted_evidence_sources")
        if not isinstance(evidence_sources, list) or not evidence_sources:
            raise VisualTaxonomyValidationError(
                f"{prefix}.accepted_evidence_sources must be a non-empty list"
            )
        seen_evidence_sources = set()
        for source in evidence_sources:
            source_name = _require_non_empty_string(
                source, f"{prefix}.accepted_evidence_sources"
            )
            if source_name in seen_evidence_sources:
                raise VisualTaxonomyValidationError(
                    f"duplicate accepted_evidence_sources in {class_name}"
                )
            seen_evidence_sources.add(source_name)
            if source_name not in _ALLOWED_EVIDENCE_SOURCES:
                raise VisualTaxonomyValidationError(
                    f"unsupported evidence source in {class_name}: {source_name}"
                )

        metadata = family.get("metadata", {})
        if not isinstance(metadata, dict):
            raise VisualTaxonomyValidationError(f"{prefix}.metadata must be an object")

    overlap = seen_class_ids.intersection(external_class_names)
    if overlap:
        raise VisualTaxonomyValidationError(
            f"external visual class collides with family: {sorted(overlap)[0]}"
        )
    name_overlap = seen_class_names.intersection(external_class_names.values())
    if name_overlap:
        raise VisualTaxonomyValidationError(
            "external canonical_name collides with family: "
            f"{sorted(name_overlap)[0]}"
        )

    known_class_ids = seen_class_ids | set(external_class_names)
    for owner_name, excluded_id in exclusions_to_check:
        if excluded_id not in known_class_ids:
            raise VisualTaxonomyValidationError(
                f"unknown exclusion in {owner_name}: {excluded_id}"
            )

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise VisualTaxonomyValidationError("metadata must be an object")

    return copy.deepcopy(data)


def load_visual_taxonomy(
    path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Load and validate a taxonomy file without caching or side effects."""
    taxonomy_path = Path(path) if path is not None else DEFAULT_VISUAL_TAXONOMY_PATH
    try:
        raw = taxonomy_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise VisualTaxonomyValidationError(
            f"unable to read visual taxonomy: {taxonomy_path}"
        ) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VisualTaxonomyValidationError(
            f"invalid visual taxonomy JSON at line {exc.lineno}, column {exc.colno}"
        ) from exc

    return validate_visual_taxonomy(data)


def _resolve_visual_class_id(
    taxonomy: Mapping[str, Any], visual_class: str
) -> Optional[str]:
    for family in taxonomy.get("families", []):
        if visual_class in (
            family.get("visual_class_id"),
            family.get("canonical_name"),
        ):
            return family.get("visual_class_id")
    return None


def get_visual_family(
    taxonomy: Mapping[str, Any], visual_class: str
) -> Optional[Dict[str, Any]]:
    """Return a defensive copy of an exact class or configured alias match."""
    class_id = _resolve_visual_class_id(taxonomy, visual_class)
    if class_id is None:
        return None
    for family in taxonomy.get("families", []):
        if family.get("visual_class_id") == class_id:
            return copy.deepcopy(family)
    return None


def get_allowed_variants(
    taxonomy: Mapping[str, Any], visual_class: str
) -> Tuple[str, ...]:
    """Return canonical display names in configured order."""
    family = get_visual_family(taxonomy, visual_class)
    if family is None:
        return ()
    return tuple(variant["display_name"] for variant in family["variants"])


def resolve_variant_alias(
    taxonomy: Mapping[str, Any], visual_class: str, alias: str
) -> Optional[str]:
    """Resolve only an explicitly configured alias to a canonical display name."""
    family = get_visual_family(taxonomy, visual_class)
    if family is None:
        return None
    for variant in family["variants"]:
        if alias in variant.get("aliases", []):
            return variant["display_name"]
    target_id = family.get("variant_aliases", {}).get(alias)
    if target_id is not None:
        for variant in family["variants"]:
            if variant["id"] == target_id:
                return variant["display_name"]
    return None


def is_valid_variant(
    taxonomy: Mapping[str, Any], visual_class: str, variant: str
) -> bool:
    """Check an exact canonical variant or explicitly configured alias."""
    family = get_visual_family(taxonomy, visual_class)
    if family is None:
        return False
    for configured in family["variants"]:
        if variant in (configured["id"], configured["display_name"]):
            return True
    return resolve_variant_alias(taxonomy, visual_class, variant) is not None


def is_excluded_from_family(
    taxonomy: Mapping[str, Any], visual_class: str, candidate: str
) -> bool:
    """Check an exact exclusion by canonical name or stable class ID."""
    family = get_visual_family(taxonomy, visual_class)
    if family is None:
        return False
    excluded_ids = set(family.get("must_not_group", []))
    if candidate in excluded_ids:
        return True
    for configured in taxonomy.get("families", []):
        if (
            configured.get("visual_class_id") in excluded_ids
            and configured.get("canonical_name") == candidate
        ):
            return True
    return any(
        configured.get("visual_class_id") in excluded_ids
        and configured.get("canonical_name") == candidate
        for configured in taxonomy.get("external_visual_classes", [])
    )


@dataclass(frozen=True)
class VariantEvidence:
    """One explicit source of variant evidence for a recognized visual class."""

    source: str
    values: Tuple[str, ...]
    evidence_id: Optional[str] = None


@dataclass(frozen=True)
class VariantResolution:
    """Fail-safe result of post-visual variant resolution."""

    visual_class: str
    display_variant: Optional[str]
    variant_source: Optional[str]
    variant_status: str
    variant_evidence_ids: Tuple[str, ...]
    reason: str


_VARIANT_SOURCE_PRIORITY = {
    "human_admin": 0,
    "structured_metadata": 1,
    "ocr": 2,
}


def _as_evidence_values(value: Union[str, Sequence[str]]) -> Tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(value)
    raise VisualTaxonomyValidationError(
        "variant evidence must be a string or sequence of strings"
    )


def collect_variant_evidence(
    *,
    human_admin: Optional[Union[str, Sequence[str]]] = None,
    structured_metadata: Optional[Union[str, Sequence[str]]] = None,
    ocr: Optional[Union[str, Sequence[str]]] = None,
    evidence_ids: Optional[Mapping[str, str]] = None,
) -> Tuple[VariantEvidence, ...]:
    """Collect explicit evidence in the approved priority order."""
    identifiers = evidence_ids or {}
    if not isinstance(identifiers, Mapping):
        raise VisualTaxonomyValidationError("evidence_ids must be a mapping")

    collected = []
    for source, value in (
        ("human_admin", human_admin),
        ("structured_metadata", structured_metadata),
        ("ocr", ocr),
    ):
        if value is None:
            continue
        evidence_id = identifiers.get(source)
        if evidence_id is not None:
            _require_non_empty_string(evidence_id, f"evidence_ids[{source}]")
        collected.append(
            VariantEvidence(
                source=source,
                values=_as_evidence_values(value),
                evidence_id=evidence_id,
            )
        )
    return tuple(collected)


def _canonical_variant_display(
    family: Mapping[str, Any], candidate: str
) -> Optional[str]:
    for variant in family.get("variants", []):
        if candidate in (variant.get("id"), variant.get("display_name")):
            return variant.get("display_name")
        if candidate in variant.get("aliases", []):
            return variant.get("display_name")
    target_id = family.get("variant_aliases", {}).get(candidate)
    if target_id is not None:
        for variant in family.get("variants", []):
            if variant.get("id") == target_id:
                return variant.get("display_name")
    return None


def _unresolved_variant(
    visual_class: str, status: str, reason: str
) -> VariantResolution:
    return VariantResolution(
        visual_class=visual_class,
        display_variant=None,
        variant_source=None,
        variant_status=status,
        variant_evidence_ids=(),
        reason=reason,
    )


def resolve_display_variant(
    taxonomy: Mapping[str, Any],
    visual_class: str,
    evidence: Sequence[VariantEvidence] = (),
) -> VariantResolution:
    """Resolve an exact display variant without scores, models, I/O, or guessing."""
    family = get_visual_family(taxonomy, visual_class)
    if family is None:
        return _unresolved_variant(
            visual_class,
            "unconfigured",
            "visual_class_has_no_variant_taxonomy",
        )

    if not isinstance(evidence, Sequence) or isinstance(
        evidence, (str, bytes, bytearray)
    ):
        raise VisualTaxonomyValidationError("evidence must be a sequence")

    resolved_by_source = {}
    evidence_ids_by_source = {}
    saw_value = False
    for item in evidence:
        if not isinstance(item, VariantEvidence):
            raise VisualTaxonomyValidationError(
                "evidence entries must be VariantEvidence"
            )
        if item.source not in _VARIANT_SOURCE_PRIORITY:
            return _unresolved_variant(
                family["canonical_name"],
                "unsupported",
                "unsupported_variant_evidence_source",
            )
        if item.evidence_id is not None:
            _require_non_empty_string(item.evidence_id, "evidence_id")
            evidence_ids_by_source.setdefault(item.source, set()).add(
                item.evidence_id
            )

        source_values = resolved_by_source.setdefault(item.source, set())
        for raw_value in item.values:
            saw_value = True
            if not isinstance(raw_value, str) or not raw_value:
                return _unresolved_variant(
                    family["canonical_name"],
                    "unsupported",
                    "unknown_variant_evidence",
                )
            if raw_value != raw_value.strip():
                return _unresolved_variant(
                    family["canonical_name"],
                    "unsupported",
                    "unknown_variant_evidence",
                )
            if is_excluded_from_family(taxonomy, visual_class, raw_value):
                return _unresolved_variant(
                    family["canonical_name"],
                    "unsupported",
                    "excluded_variant_evidence",
                )
            canonical = _canonical_variant_display(family, raw_value)
            if canonical is None:
                return _unresolved_variant(
                    family["canonical_name"],
                    "unsupported",
                    "unknown_variant_evidence",
                )
            source_values.add(canonical)

    if not saw_value:
        return _unresolved_variant(
            family["canonical_name"], "absent", "no_variant_evidence"
        )

    if any(len(values) > 1 for values in resolved_by_source.values()):
        return _unresolved_variant(
            family["canonical_name"],
            "ambiguous",
            "ambiguous_variant_evidence",
        )

    resolved_sources = {
        source: next(iter(values))
        for source, values in resolved_by_source.items()
        if values
    }
    distinct_variants = set(resolved_sources.values())
    if len(distinct_variants) > 1:
        return _unresolved_variant(
            family["canonical_name"],
            "conflict",
            "conflicting_variant_evidence",
        )
    if not distinct_variants:
        return _unresolved_variant(
            family["canonical_name"], "absent", "no_variant_evidence"
        )

    display_variant = next(iter(distinct_variants))
    agreeing_sources = [
        source
        for source, value in resolved_sources.items()
        if value == display_variant
    ]
    variant_source = min(
        agreeing_sources, key=lambda source: _VARIANT_SOURCE_PRIORITY[source]
    )
    ordered_ids = []
    for source in sorted(
        agreeing_sources, key=lambda item: _VARIANT_SOURCE_PRIORITY[item]
    ):
        ordered_ids.extend(sorted(evidence_ids_by_source.get(source, ())))

    return VariantResolution(
        visual_class=family["canonical_name"],
        display_variant=display_variant,
        variant_source=variant_source,
        variant_status="confirmed",
        variant_evidence_ids=tuple(ordered_ids),
        reason="confirmed_variant_evidence",
    )

DISH_FAMILIES = {
    "Tabules": [
        "Tabule",
    ],
    "Salada de Ovos e Batatas": [
        "Salada de Ovos",
        "Salada de Batatas e Ovos",
    ],
    "Vinagretes": [
        "Molho Vinagrete",
        "Vinagrete de Lula",
    ],
    "Maminhas com Molho Escuro": [
        "Maminha ao Molho Mongolia",
        "Maminha na Cerveja Preta",
        "Maminha Molho Madeira",
    ],
    "Bacalhaus Desfiados": [
        "Bacalhau a Bras",
        "Bacalhau com Natas",
    ],
    "Gratinados e Assadeiras": [
        "Lasanha de Espinafre",
        "Lasanha de Berinjela",
        "Lasanha de Portobello",
        "Escondidinho de Carne Seca",
        "Berinjela a Parmegiana",
        "Couve-flor Gratinada",
        "Brocolis Gratinado",
        "Alho Poro Gratinado",
        "Canelone 4 Queijos",
        "Canelone de Espinafre",
        "Conchiglione ao Creme de Avelas",
        "Torta de Legumes",
        "Tortilha Espanhola de Batata",
    ],
    "Empanados e Milanesas": [
        "Peixe a Milanesa",
    ],
    "Pasteis": [
        "Pastel",
    ],
    "Tomates": [
        "Tomate",
        "Tomate Seco",
        "Umami de Tomates",
    ],
    "Pures": [
        "Pure de Batata",
        "Pure de Mandioquinha",
        "Pure de Maca Verde",
        "Pure de Abobora",
        "Aligot",
    ],
    "Quiches": [
        "Quiche de Alho Poro",
        "Quiche de Mussarela de Bufala com Tomate Seco",
        "Quiche de Tomate",
        "Tortinha de Gorgonzola e Figo",
    ],
    "Feijoes": [
        "Feijao Branco",
        "Feijao Tropeiro",
        "Feijao do Chef",
    ],
    "Mousses": [
        "Mousse de Chocolate sem Acucar",
        "Mousse de Limao",
        "Mousse de Maracuja",
    ],
    "Gelatinas": [
        "Gelatina de Abacaxi",
        "Gelatina de Cereja",
        "Gelatina de Limao",
        "Gelatina de Uva",
    ],
    "Rolinhos Vietnamitas": [
        "Rolinho Vietnamita",
        "Rolinho Vietnamita de Camarao",
        "Sushi Vietnamita",
    ],
    "Strogonoffs": [
        "Estrogonofe de File Mignon",
        "Strogonoff Vegano",
        "Strogonoff de File Mignon",
    ],
    "Hamburgers": [
        "Hamburger Bovino",
        "Hamburger de Camarao com Pernil Suino",
        "Hamburguer Vegano",
    ],
    "Sobrecoxas": [
        "Sobrecoxa ao Limao",
        "Sobrecoxa ao Tandoori",
        "Sobrecoxa ao Tucupi",
    ],
    "Costelas": [
        "Costela Assada",
        "Costela Cibi Sana",
    ],
    "Carpaccios": [
        "Carpaccio de Laranja",
        "Carpaccio de Pera com Rucula e Amendoas",
    ],
    "Risones": [
        "Risone ao Creme de Limao",
        "Risone ao Pesto",
    ],
    "Ceviches": [
        "Ceviche",
        "Ceviche de Banana da Terra",
        "Ceviche de Manga",
    ],
    "Files de Peixe": [
        "File de Peixe ao Misso",
        "File de Peixe ao Molho Confit",
        "File de Peixe ao Molho de Frutas Secas",
        "File de Peixe ao Molho de Limao",
        "File de Peixe em Manteiga de Tomates",
        "Grelhado dos Pescadores",
    ],
    "Nhoques": [
        "Nhoque Vegano",
        "Nhoque ao Sugo",
        "Gnocchi ao Molho Branco",
    ],
    "Pudins e Doces Cremosos": [
        "Pudim",
        "Pannacotta com Frutas Vermelhas",
        "Manjar de Coco",
        "Tiramisu",
    ],
    "Bolos e Brownies": [
        "Bolo Brownie de Chocolate",
        "Bolo de Gengibre",
        "Frutas ao Ganache de Chocolate",
    ],
    "Guacamoles": [
        "Guacamole",
        "Guacamole com Manga",
    ],
    "Romeus": [
        "Romeu",
        "Romeu e Julieta",
    ],
    "Saladas Compostas": [
        "Salada Mediterranea",
        "Salada Oriental",
        "Salada Tailandesa",
        "Salada de Feijao Branco",
        "Salada de Grao de Bico",
        "Salada de Lentilha",
    ],
    "Maminha ao Molho Mostarda e Cebola": [
        "Maminha ao Molho Mostarda",
    ],
    "Feijoada": [
        "Feijoada",
        "Lentilha com Tofu",
    ],
    "Arrozes Compostos": [
        "Arroz 7 Graos",
        "Arroz Integral com Legumes",
        "Arroz Mar e Campo",
        "Arroz com Brocolis e Amendoas",
        "Baiao de Dois",
    ],
}


def _build_dish_to_family_map():
    """Constroi mapa reverso: nome_do_prato -> nome_da_familia"""
    dish_map = {}
    for family_name, dishes in DISH_FAMILIES.items():
        for dish in dishes:
            dish_map[dish] = family_name
    return dish_map


DISH_TO_FAMILY = _build_dish_to_family_map()


def get_family(dish_name: str):
    """Retorna o nome da familia de um prato, ou None se nao pertence a nenhuma."""
    return DISH_TO_FAMILY.get(dish_name)


def get_family_members(dish_name: str):
    """Retorna a lista de membros da familia de um prato."""
    family = DISH_TO_FAMILY.get(dish_name)
    if family:
        return DISH_FAMILIES[family]
    return []


def detect_family_ambiguity(results: list, raw_gap_threshold: float = 0.03):
    """
    Detecta ambiguidade de familia nos resultados do CLIP.
    
    Args:
        results: Lista de resultados do CLIP search [{dish, score, raw_score, ...}]
        raw_gap_threshold: Gap maximo entre top-1 e top-2 raw scores para considerar ambiguo
        
    Returns:
        dict com:
        - is_ambiguous: bool
        - family_name: str ou None
        - candidates: lista de nomes de pratos candidatos
        - reason: str explicando a ambiguidade
    """
    if len(results) < 2:
        return {"is_ambiguous": False, "family_name": None, "candidates": [], "reason": ""}
    
    top1 = results[0]
    top2 = results[1]
    top1_dish = top1.get("dish", "")
    top2_dish = top2.get("dish", "")
    top1_raw = top1.get("raw_score", 0)
    top2_raw = top2.get("raw_score", 0)
    gap = top1_raw - top2_raw
    
    top1_family = get_family(top1_dish)
    top2_family = get_family(top2_dish)
    
    # CASO 1: Top-1 e Top-2 sao da MESMA familia e gap e pequeno
    if top1_family and top1_family == top2_family and gap < 0.05:
        candidates = []
        for r in results[:5]:
            r_dish = r.get("dish", "")
            if get_family(r_dish) == top1_family and r_dish not in candidates:
                candidates.append(r_dish)
        
        if len(candidates) < 2:
            return {"is_ambiguous": False, "family_name": None, "candidates": [], "reason": ""}
        
        return {
            "is_ambiguous": True,
            "family_name": top1_family,
            "candidates": candidates[:4],
            "reason": f"same_family_close_scores (gap={gap:.3f})"
        }
    
    # CASO 2: Top-1 e Top-2 tem scores muito proximos (qualquer familia)
    if gap < raw_gap_threshold and top1_raw < 0.95:
        candidates = [top1_dish]
        if top2_dish not in candidates:
            candidates.append(top2_dish)
        if len(results) > 2:
            top3 = results[2]
            top3_raw = top3.get("raw_score", 0)
            if top1_raw - top3_raw < 0.06:
                top3_dish = top3.get("dish", "")
                if top3_dish not in candidates:
                    candidates.append(top3_dish)
        
        family_counts = {}
        for c in candidates:
            fam = get_family(c)
            if fam:
                family_counts[fam] = family_counts.get(fam, 0) + 1
        
        family_name = None
        if family_counts:
            best_fam = max(family_counts, key=family_counts.get)
            if family_counts[best_fam] >= len(candidates) / 2:
                family_name = best_fam
        
        return {
            "is_ambiguous": True,
            "family_name": family_name,
            "candidates": candidates[:4],
            "reason": f"very_close_scores (gap={gap:.3f})"
        }
    
    # CASO 3: Top-1 pertence a uma familia e o score nao e altissimo
    if top1_family and top1_raw < 0.95 and gap < 0.05:
        family_members = get_family_members(top1_dish)
        candidates_in_results = []
        for r in results[:5]:
            r_dish = r.get("dish", "")
            if r_dish in family_members:
                candidates_in_results.append(r_dish)
        
        if len(candidates_in_results) >= 2:
            return {
                "is_ambiguous": True,
                "family_name": top1_family,
                "candidates": candidates_in_results[:4],
                "reason": f"family_members_in_results (gap={gap:.3f})"
            }
    
    return {"is_ambiguous": False, "family_name": None, "candidates": [], "reason": ""}
