#!/usr/bin/env python3
"""Validate Canelone through the frozen index and existing family contract."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageEnhance, ImageOps


EXPECTED = {
    "json": "64a431e60cb9d8c1f40b2593a364c52793fa8f1949b5776aa2baf15f9d9d8047",
    "npy": "1256e57367ac682cd8f6fbd5d1ad2dbd5f888a07c4239163f50b47d4eb1b1db5",
    "onnx": "8a97817ddd9947f9e1ddc43c85e7c6d0c65c55d9c7f47b81bf20e265a0fcd0da",
    "classes": 237,
    "embeddings": 1518,
    "dimension": 512,
}
CLIP_MEAN = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
CLIP_STD = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)
NEGATIVE_CLASSES = (
    "Lasanha de Berinjela",
    "Nhoque ao Sugo",
    "Panquecade Frango",
    "Ravioli",
    "Espaguete",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preprocess(content: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(content)).convert("RGB")
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Sharpness(image).enhance(1.3)
    image = ImageEnhance.Color(image).enhance(1.1)
    width, height = image.size
    if width < height:
        new_width, new_height = 224, int(height * 224 / width)
    else:
        new_height, new_width = 224, int(width * 224 / height)
    image = image.resize((new_width, new_height), Image.Resampling.BICUBIC)
    left, top = (new_width - 224) // 2, (new_height - 224) // 2
    image = image.crop((left, top, left + 224, top + 224))
    array = np.asarray(image, dtype=np.float32) / 255.0
    return ((array - CLIP_MEAN) / CLIP_STD).transpose(2, 0, 1)[None, ...]


def normalized_slug(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return re.sub(
        r"-+", "-", ascii_value.replace("_", "-").replace(" ", "-").lower().strip()
    )


def rank(
    embeddings: np.ndarray,
    labels: list[str],
    metadata: dict[str, Any],
    vector: np.ndarray,
) -> list[dict[str, Any]]:
    # NumPy 2 may emit platform-specific floating-point warnings from the
    # optimized matmul kernel even when every final value is finite. Validate
    # the observable result explicitly and fail closed on any real anomaly.
    with np.errstate(all="ignore"):
        similarities = embeddings @ vector
    if not np.isfinite(similarities).all():
        raise SystemExit("non-finite query similarities")
    top_indices = np.argsort(similarities)[::-1][:50]
    consistency = len({labels[int(position)] for position in top_indices[:15]})
    consistency_penalty = max(0.0, (consistency - 3) * 0.02)
    dish_scores: dict[str, float] = {}
    for position in top_indices:
        dish = labels[int(position)]
        score = float(similarities[int(position)])
        dish_scores[dish] = max(score, dish_scores.get(dish, -math.inf))
    ordered = sorted(dish_scores.items(), key=lambda row: row[1], reverse=True)[:5]
    gap = ordered[0][1] - ordered[1][1] if len(ordered) > 1 else 0.0
    gap_penalty = (0.03 - gap) * 2 if gap < 0.03 else 0.0
    rows = []
    for position, (dish, raw_score) in enumerate(ordered):
        adjusted = raw_score
        if position == 0:
            adjusted = max(0.0, raw_score - consistency_penalty - gap_penalty)
        rows.append(
            {
                "dish": dish,
                "raw_score": round(raw_score, 8),
                "adjusted_score": round(adjusted, 8),
                "gap": round(gap, 8),
                "consistency": consistency,
                "image_count": metadata.get(dish, {}).get("image_count", 0),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--previous-audit", type=Path, required=True)
    parser.add_argument("--index-json", type=Path, required=True)
    parser.add_argument("--index-npy", type=Path, required=True)
    parser.add_argument("--onnx", type=Path, required=True)
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--app-js", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"output already exists: {args.output}")

    actual_hashes = {
        "json": sha256(args.index_json),
        "npy": sha256(args.index_npy),
        "onnx": sha256(args.onnx),
    }
    if actual_hashes != {key: EXPECTED[key] for key in actual_hashes}:
        raise SystemExit(f"artifact hash mismatch: {actual_hashes}")

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    family = plan["family_upsert"]["set"]
    members = set(family["members_slugs"])
    if plan["status"] != "EXPERIMENTAL_NOT_APPLIED":
        raise SystemExit("registration plan must remain unapplied")
    if family["members_display"] != [
        "Canelone 4 Queijos",
        "Canelone de Espinafre",
    ]:
        raise SystemExit("unexpected Canelone candidate list")
    if not family.get("requires_member_confirmation"):
        raise SystemExit("Canelone must require explicit member confirmation")
    if plan.get("nutrition_policy") != (
        "WITHHOLD_SPECIFIC_NUTRITION_UNTIL_MEMBER_CONFIRMATION"
    ):
        raise SystemExit("unexpected Canelone nutrition policy")

    app_source = args.app_js.read_text(encoding="utf-8")
    message = plan["frontend_contract"]["message"]
    frontend_contract_ok = all(
        marker in app_source
        for marker in (
            'data-testid="family-block"',
            "r.family_candidates || []",
            message,
            "family-nutrition-pending-note",
            "canUseSpecificNutrition",
        )
    )
    if not frontend_contract_ok:
        raise SystemExit("existing frontend family contract not found")

    index = json.loads(args.index_json.read_text(encoding="utf-8"))
    embeddings = np.load(args.index_npy)
    if (
        index["total_dishes"],
        index["total_items"],
        index["embedding_dim"],
    ) != (EXPECTED["classes"], EXPECTED["embeddings"], EXPECTED["dimension"]):
        raise SystemExit("index cardinality mismatch")
    if embeddings.shape != (EXPECTED["embeddings"], EXPECTED["dimension"]):
        raise SystemExit("embedding shape mismatch")
    if not np.isfinite(embeddings).all():
        raise SystemExit("non-finite index embeddings")

    previous = json.loads(args.previous_audit.read_text(encoding="utf-8"))
    four_cheese = [
        {
            "kind": "known_regression",
            "expected": "canelone4queijos",
            "path": Path(row["source_path"]),
            "sha256": row["sha256"],
        }
        for row in previous["image_results"]
        if row["true_class"] == "canelone4queijos"
    ]
    if len(four_cheese) != 7:
        raise SystemExit(f"expected seven 4-cheese photos, found {len(four_cheese)}")

    references_by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for reference in index["references"]:
        references_by_class[reference["visual_class"]].append(reference)
    spinach = [
        {
            "kind": "indexed_reference_structural_check",
            "expected": "canelonedeespinafre",
            "path": args.corpus_root / row["source_relative_path"],
            "sha256": row["source_sha256"],
        }
        for row in references_by_class["canelonedeespinafre"]
    ]
    negatives = []
    for class_name in NEGATIVE_CLASSES:
        row = references_by_class[class_name][0]
        negatives.append(
            {
                "kind": "indexed_reference_negative_control",
                "expected": class_name,
                "path": args.corpus_root / row["source_relative_path"],
                "sha256": row["source_sha256"],
            }
        )

    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.inter_op_num_threads = 2
    options.intra_op_num_threads = 2
    options.enable_mem_pattern = False
    options.enable_cpu_mem_arena = False
    session = ort.InferenceSession(
        str(args.onnx), options, providers=["CPUExecutionProvider"]
    )

    results = []
    for item in four_cheese + spinach + negatives:
        if not item["path"].is_file() or sha256(item["path"]) != item["sha256"]:
            raise SystemExit(f"query source integrity failure: {item['path']}")
        vector = session.run(None, {"image": preprocess(item["path"].read_bytes())})[0][0]
        vector = vector.astype(np.float32)
        if not np.isfinite(vector).all():
            raise SystemExit(f"non-finite query embedding: {item['path']}")
        norm = float(np.linalg.norm(vector))
        if not math.isfinite(norm) or norm == 0:
            raise SystemExit(f"invalid query embedding: {item['path']}")
        vector /= norm
        top5 = rank(embeddings, index["dishes"], index["metadata"], vector)
        accepted = top5[0]["adjusted_score"] >= 0.72
        top1_slug = normalized_slug(top5[0]["dish"])
        family_visible = accepted and top1_slug in members
        specific_nutrition_authorized = not (
            family_visible and family.get("requires_member_confirmation")
        )
        results.append(
            {
                "kind": item["kind"],
                "filename": item["path"].name,
                "expected": item["expected"],
                "top1": top5[0]["dish"],
                "accepted": accepted,
                "family_visible": family_visible,
                "family_name": family["name"] if family_visible else None,
                "family_candidates": family["members_display"] if family_visible else [],
                "specific_nutrition_authorized": specific_nutrition_authorized,
                "top5": top5,
            }
        )

    four_rows = [row for row in results if row["kind"] == "known_regression"]
    spinach_rows = [
        row for row in results if row["kind"] == "indexed_reference_structural_check"
    ]
    negative_rows = [
        row for row in results if row["kind"] == "indexed_reference_negative_control"
    ]
    validations = {
        "seven_four_cheese_queries_evaluated": len(four_rows) == 7,
        "accepted_canelone_queries_show_existing_family": all(
            (not row["accepted"]) or row["family_visible"] for row in four_rows
        ),
        "spinach_references_show_existing_family": all(
            row["family_visible"] for row in spinach_rows
        ),
        "negative_pastas_do_not_show_canelone_family": all(
            not row["family_visible"] for row in negative_rows
        ),
        "ambiguous_canelone_withholds_specific_nutrition": all(
            not row["specific_nutrition_authorized"]
            for row in four_rows + spinach_rows
            if row["family_visible"]
        ),
        "negative_pastas_keep_specific_nutrition": all(
            row["specific_nutrition_authorized"] for row in negative_rows
        ),
        "frontend_contract_reused_with_safety_gate": frontend_contract_ok,
        "index_hashes_unchanged": actual_hashes
        == {key: EXPECTED[key] for key in actual_hashes},
    }
    report = {
        "status": "PASS" if all(validations.values()) else "FAIL",
        "mode": "OFFLINE_EXPERIMENTAL_NO_DATABASE_WRITE",
        "artifact_hashes": actual_hashes,
        "cardinality": {
            "visual_classes": index["total_dishes"],
            "embeddings": index["total_items"],
            "dimension": index["embedding_dim"],
        },
        "family_registration_plan": family,
        "frontend_message": message,
        "validations": validations,
        "summary": {
            "four_cheese_queries": len(four_rows),
            "four_cheese_accepted": sum(row["accepted"] for row in four_rows),
            "four_cheese_family_visible": sum(row["family_visible"] for row in four_rows),
            "spinach_references": len(spinach_rows),
            "spinach_family_visible": sum(row["family_visible"] for row in spinach_rows),
            "negative_pasta_controls": len(negative_rows),
            "negative_family_visible": sum(row["family_visible"] for row in negative_rows),
            "canelone_specific_nutrition_withheld": sum(
                row["family_visible"] and not row["specific_nutrition_authorized"]
                for row in four_rows + spinach_rows
            ),
        },
        "limitations": [
            "The seven 4-cheese photos are a known regression set, not independent validation.",
            "Spinach and negative controls are active index references and validate routing only, not independent accuracy.",
            "The registration plan was not applied to MongoDB or any deployed environment.",
        ],
        "results": results,
    }
    args.output.mkdir(parents=True)
    (args.output / "canelone_family_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown = [
        "# Validação experimental — Canelone no fluxo existente de famílias",
        "",
        f"- Status: **{report['status']}**",
        f"- Canelone 4 Queijos: {report['summary']['four_cheese_family_visible']}/{report['summary']['four_cheese_queries']} exibiriam a família; {report['summary']['four_cheese_accepted']} foram aceitas pela política atual.",
        f"- Referências de Espinafre: {report['summary']['spinach_family_visible']}/{report['summary']['spinach_references']} exibiriam a família.",
        f"- Controles negativos de outras massas: {report['summary']['negative_family_visible']}/{report['summary']['negative_pasta_controls']} exibiriam Canelone.",
        f"- Fichas específicas retidas por ambiguidade: {report['summary']['canelone_specific_nutrition_withheld']}.",
        "- Banco, índice, frontend e produção não foram alterados.",
        "",
        "As fotografias de regressão e as referências indexadas não constituem validação independente de acurácia.",
    ]
    (args.output / "canelone_family_validation.md").write_text(
        "\n".join(markdown) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], **report["summary"]}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
