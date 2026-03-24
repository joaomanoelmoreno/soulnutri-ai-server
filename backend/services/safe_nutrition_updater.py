# -*- coding: utf-8 -*-
"""
SoulNutri - Pipeline Seguro de Atualizacao Nutricional
SEGURANCA: Nunca toca em imagens, slugs ou estrutura.
Apenas atualiza campos nutricionais com dados de fontes confiaveis.
"""
import os
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


async def preview_nutrition_update(db, dish_slugs: list = None, limit: int = 10) -> dict:
    """
    DRY RUN: Mostra o que MUDARIA sem alterar nada.
    Compara dados atuais vs dados das fontes.
    """
    try:
        from services.nutrition_3sources import fetch_nutrition_3sources
    except ImportError:
        return {"ok": False, "error": "nutrition_3sources nao encontrado"}

    query = {}
    if dish_slugs:
        query["slug"] = {"$in": dish_slugs}

    previews = []
    async for dish in db.dishes.find(query, {"_id": 0}).limit(limit):
        slug = dish.get("slug", "")
        nome = dish.get("nome", slug.replace("_", " ").title())
        current_nutri = dish.get("nutricao", {})

        # Buscar dados das fontes
        try:
            new_data = await fetch_nutrition_3sources(nome)
        except Exception as e:
            previews.append({
                "slug": slug,
                "nome": nome,
                "status": "error",
                "error": str(e),
                "current": current_nutri,
                "proposed": None,
                "sources_used": []
            })
            continue

        if not new_data or not new_data.get("nutricao"):
            previews.append({
                "slug": slug,
                "nome": nome,
                "status": "no_data",
                "current": current_nutri,
                "proposed": None,
                "sources_used": []
            })
            continue

        proposed = new_data.get("nutricao", {})
        sources = new_data.get("fontes_utilizadas", [])

        # Calcular diferenças
        changes = {}
        for key in ["calorias_kcal", "proteinas_g", "carboidratos_g", "gorduras_g", "fibras_g", "sodio_mg"]:
            old_val = current_nutri.get(key, 0) or 0
            new_val = proposed.get(key, 0) or 0
            if abs(old_val - new_val) > 0.5:
                changes[key] = {"old": old_val, "new": new_val, "diff": round(new_val - old_val, 1)}

        previews.append({
            "slug": slug,
            "nome": nome,
            "status": "has_changes" if changes else "no_changes",
            "current": current_nutri,
            "proposed": proposed,
            "changes": changes,
            "sources_used": sources
        })

    return {
        "ok": True,
        "total_analyzed": len(previews),
        "with_changes": sum(1 for p in previews if p["status"] == "has_changes"),
        "previews": previews
    }


async def safe_update_nutrition(db, dish_slug: str, new_nutrition: dict, source_info: str = "") -> dict:
    """
    Atualiza APENAS campos nutricionais de UM prato.
    Faz backup antes de alterar.
    NUNCA toca em imagens, slug, nome ou qualquer campo estrutural.
    """
    try:
        # Buscar prato atual
        dish = await db.dishes.find_one({"slug": dish_slug})
        if not dish:
            return {"ok": False, "error": f"Prato '{dish_slug}' nao encontrado"}

        old_id = dish["_id"]
        old_nutri = dish.get("nutricao", {})

        # Criar backup
        backup = {
            "dish_slug": dish_slug,
            "dish_nome": dish.get("nome", ""),
            "old_nutrition": old_nutri,
            "new_nutrition": new_nutrition,
            "source_info": source_info,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "nutrition_update"
        }
        await db.nutrition_audit_log.insert_one(backup)

        # Atualizar APENAS o campo nutricao
        allowed_fields = {
            "calorias_kcal", "proteinas_g", "carboidratos_g",
            "gorduras_g", "fibras_g", "sodio_mg",
            "calcio_mg", "ferro_mg", "potassio_mg",
            "colesterol_mg", "vitamina_c_mg"
        }
        safe_nutri = {k: v for k, v in new_nutrition.items() if k in allowed_fields}

        result = await db.dishes.update_one(
            {"_id": old_id},
            {"$set": {"nutricao": safe_nutri, "nutricao_updated_at": datetime.now(timezone.utc).isoformat(), "nutricao_source": source_info}}
        )

        return {
            "ok": True,
            "modified": result.modified_count > 0,
            "slug": dish_slug,
            "old_nutrition": {k: old_nutri.get(k) for k in allowed_fields if old_nutri.get(k)},
            "new_nutrition": safe_nutri
        }

    except Exception as e:
        logger.error(f"[NUTRITION_UPDATE] Erro: {e}")
        return {"ok": False, "error": str(e)}


async def rollback_nutrition(db, dish_slug: str) -> dict:
    """Reverte a última atualização nutricional de um prato."""
    try:
        # Buscar último backup
        backup = await db.nutrition_audit_log.find_one(
            {"dish_slug": dish_slug},
            sort=[("timestamp", -1)]
        )
        if not backup:
            return {"ok": False, "error": "Nenhum backup encontrado"}

        old_nutri = backup.get("old_nutrition", {})

        # Reverter
        result = await db.dishes.update_one(
            {"slug": dish_slug},
            {"$set": {"nutricao": old_nutri, "nutricao_rolled_back": True}}
        )

        return {
            "ok": True,
            "rolled_back": result.modified_count > 0,
            "slug": dish_slug,
            "restored_nutrition": old_nutri
        }

    except Exception as e:
        logger.error(f"[NUTRITION_ROLLBACK] Erro: {e}")
        return {"ok": False, "error": str(e)}
