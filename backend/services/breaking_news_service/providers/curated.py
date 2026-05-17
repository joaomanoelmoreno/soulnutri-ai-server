# -*- coding: utf-8 -*-
"""
Provider: curated.

Le da collection Mongo `contextual_breaking_news` (seed manual editorial).
Sem chamadas externas. Sem cache aqui (Mongo + indices ja sao rapidos).
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv
import pymongo

from ..ranking import build_term_set, score_item, is_relevant, MAX_AGE_DAYS

logger = logging.getLogger(__name__)

# Lazy/single-process client (server.py compartilha o mesmo padrao).
load_dotenv(Path(__file__).resolve().parents[3] / '.env')
_client = pymongo.MongoClient(os.environ['MONGO_URL'])
_db = _client[os.environ['DB_NAME']]
_collection = _db.contextual_breaking_news

_indexes_created = False


def _ensure_indexes():
    """Cria indices uma unica vez por processo. Idempotente."""
    global _indexes_created
    if _indexes_created:
        return
    try:
        _collection.create_index([("tags", 1)], background=True)
        _collection.create_index([("data", -1)], background=True)
        _collection.create_index([("ativo", 1)], background=True)
        _collection.create_index([("id", 1)], unique=True, background=True, sparse=True)
        _indexes_created = True
        logger.info("[BREAKING_NEWS][curated] indices garantidos")
    except Exception as e:
        # Indices opcionais — nao bloquear leitura por isso.
        logger.warning(f"[BREAKING_NEWS][curated] falha ao criar indices: {e}")


async def fetch(dish_slug, family_slug, ingredientes, category):
    """
    Busca melhor item curado para o contexto fornecido.

    Retorna dict no schema unificado (com 'score' e 'origem' nao incluidos —
    api.py os anexa), ou None se nenhum item atingir score minimo.
    """
    _ensure_indexes()

    terms = build_term_set(dish_slug, family_slug, ingredientes, category)
    if not terms:
        return None

    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    # Filtro Mongo: ativo, com tags em comum, dentro da janela de recencia.
    query = {
        "ativo": True,
        "tags": {"$in": list(terms)},
        "data": {"$gte": cutoff},
    }

    try:
        cursor = _collection.find(query, {"_id": 0})
    except Exception as e:
        logger.error(f"[BREAKING_NEWS][curated] erro de leitura Mongo: {e}")
        return None

    best = None
    best_score = -1
    best_matched = []

    for doc in cursor:
        score, matched = score_item(doc, terms)
        if not is_relevant(score):
            continue
        # Desempate: score maior > data mais recente.
        if score > best_score or (
            score == best_score
            and isinstance(doc.get('data'), datetime)
            and isinstance((best or {}).get('data'), datetime)
            and doc['data'] > best['data']
        ):
            best = doc
            best_score = score
            best_matched = matched

    if not best:
        return None

    data_val = best.get('data')
    data_iso = data_val.isoformat() if isinstance(data_val, datetime) else data_val

    return {
        "titulo": best.get('titulo'),
        "url": best.get('url'),
        "fonte": best.get('fonte'),
        "polaridade": best.get('polaridade', 'neutro'),
        "data": data_iso,
        "tags_matched": best_matched,
        "score": best_score,
    }
