# -*- coding: utf-8 -*-
"""Atualização automática de conteúdos Perplexity para o SoulNutri®."""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from services.perplexity_food_content_service import search_food_content_batch

load_dotenv()

logger = logging.getLogger("perplexity_auto_update")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


def parse_datetime(value):
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, str) and value.strip():
        result = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    else:
        return None

    if result.tzinfo is None:
        return result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def polaridade_for(categoria):
    if categoria == "alerta":
        return "alerta"
    if categoria in {"beneficio", "boa_noticia"}:
        return "beneficio"
    return "neutro"


def build_document(item):
    categoria = str(item.get("categoria") or "").strip().lower()
    data = parse_datetime(item.get("data"))
    valido_ate = parse_datetime(item.get("valido_ate"))

    if not item.get("id") or not item.get("url") or not data:
        return None

    titulo = str(item.get("titulo") or "").strip()
    resumo = str(item.get("resumo") or "").strip()

    fonte = str(item.get("fonte") or "").strip()
    url = str(item.get("url") or "").strip()
    categorias_validas = {
        "alerta", "boa_noticia", "novidade", "pesquisa",
        "beneficio", "risco", "combinacao", "curiosidade",
    }

    if (
        not titulo
        or not resumo
        or not fonte
        or not url.startswith("https://")
        or categoria not in categorias_validas
        or not valido_ate
    ):
        return None

    document = {
        "id": str(item["id"]),
        "titulo": titulo,
        "url": url,
        "fonte": fonte,
        "polaridade": polaridade_for(categoria),
        "categoria": categoria,
        "resumo": resumo,
        "data": data,
        "valido_ate": valido_ate,
        "tags": [
            str(tag).strip().lower()
            for tag in (item.get("tags") or [])
            if str(tag).strip()
        ],
        "origem": "perplexity_search_agent",
        "ativo": True,
        "publicacao_automatica": True,
        "disclaimer": (
            "Conteúdo informativo. O SoulNutri® não é médico, nutricionista, "
            "biólogo, laboratório ou instrumento de diagnóstico."
        ),
        "updated_at": datetime.now(timezone.utc),
    }

    if categoria == "alerta":
        document["mensagem_alerta"] = (
            f"ALERTA: Existe informação relevante relacionada a {titulo}, "
            "divulgada por uma fonte especializada. "
            "Clique aqui para ler a notícia."
        )

    return document


async def expire_old_contents(collection):
    now = datetime.now(timezone.utc)
    result = await collection.update_many(
        {
            "origem": "perplexity_search_agent",
            "ativo": True,
            "valido_ate": {"$lt": now},
        },
        {
            "$set": {
                "ativo": False,
                "desativado_automaticamente": True,
                "desativado_em": now,
                "updated_at": now,
            }
        },
    )
    return result.modified_count


async def run():
    api_key = os.getenv("PERPLEXITY_API_KEY", "").strip()
    mongo_url = os.getenv("MONGO_URL", "").strip()
    db_name = os.getenv("DB_NAME", "soulnutri").strip()
    foods_json = os.getenv("PERPLEXITY_AUTO_FOODS_JSON", "").strip()

    if not api_key.startswith("pplx-"):
        raise RuntimeError("PERPLEXITY_API_KEY ausente ou inválida")
    if not mongo_url:
        raise RuntimeError("MONGO_URL ausente")
    if not foods_json:
        raise RuntimeError("PERPLEXITY_AUTO_FOODS_JSON ausente")

    foods = json.loads(foods_json)
    if not isinstance(foods, list) or not foods:
        raise RuntimeError("PERPLEXITY_AUTO_FOODS_JSON deve ser uma lista não vazia")

    client = AsyncIOMotorClient(mongo_url)
    collection = client[db_name].contextual_breaking_news

    try:
        expired_count = await expire_old_contents(collection)
        published_count = 0
        error_count = 0
        candidate_count = 0

        for start in range(0, len(foods), 10):
            batch = foods[start:start + 10]
            result = await search_food_content_batch(
                batch,
                api_key=api_key,
                use_agent=True,
                max_foods=10,
            )

            error_count += int(result.get("error_count") or 0)

            for food_result in result.get("results") or []:
                for item in food_result.get("candidates") or []:
                    candidate_count += 1
                    document = build_document(item)
                    if not document:
                        error_count += 1
                        continue

                    await collection.update_one(
                        {"id": document["id"]},
                        {"$set": document},
                        upsert=True,
                    )
                    published_count += 1

        logger.info(
            "[PERPLEXITY_AUTO] foods=%d candidates=%d published=%d "
            "expired=%d errors=%d",
            len(foods),
            candidate_count,
            published_count,
            expired_count,
            error_count,
        )

        return {
            "ok": error_count == 0,
            "foods": len(foods),
            "candidates": candidate_count,
            "published": published_count,
            "expired": expired_count,
            "errors": error_count,
        }
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(run())
