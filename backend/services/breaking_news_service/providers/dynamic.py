# -*- coding: utf-8 -*-
"""Busca de noticias em tempo real via Perplexity, sem persistencia."""

import logging
import os

from services.perplexity_food_content_service import search_food_content

logger = logging.getLogger(__name__)


def _food_terms(dish_slug, family_slug, ingredientes):
    primary = str(dish_slug or family_slug or "").replace("_", " ").strip()
    aliases = []
    for raw in (family_slug, *(ingredientes or [])):
        value = str(raw or "").replace("_", " ").strip()
        if value and value.lower() != primary.lower() and value not in aliases:
            aliases.append(value)
    return primary, aliases[:10]


async def fetch(dish_slug, family_slug, ingredientes, category):
    """Busca uma noticia atual e retorna somente candidato validado."""
    primary, aliases = _food_terms(dish_slug, family_slug, ingredientes)
    if not primary:
        return None

    api_key = os.getenv("PERPLEXITY_API_KEY", "").strip()
    if not api_key:
        logger.info("[BREAKING_NEWS][dynamic] chave ausente")
        return None

    try:
        result = await search_food_content(
            primary,
            aliases=aliases,
            api_key=api_key,
            use_agent=True,
            agent_max_items=2,
            agent_allow_web_search=False,
        )
    except Exception as exc:
        logger.warning(
            "[BREAKING_NEWS][dynamic] busca falhou: %s",
            type(exc).__name__,
        )
        return None

    candidates = result.get("candidates") or []
    if not candidates:
        return None

    prioridade_impacto = {
        "critico": 4,
        "alto": 3,
        "medio": 2,
        "baixo": 1,
        "nao_informado": 0,
    }
    prioridade_categoria = {
        "alerta": 3,
        "risco": 2,
        "novidade": 1,
        "beneficio": 0,
    }
    item = sorted(
        candidates,
        key=lambda candidate: (
            prioridade_impacto.get(candidate.get("impacto"), 0),
            prioridade_categoria.get(candidate.get("categoria"), 0),
            candidate.get("relevancia_publica") == "alta",
        ),
        reverse=True,
    )[0]
    categoria = item.get("categoria") or "novidade"
    polaridade = (
        "alerta"
        if categoria in {"alerta", "risco"}
        else "beneficio"
        if categoria in {"beneficio", "boa_noticia"}
        else "neutro"
    )

    return {
        "titulo": item.get("titulo"),
        "url": item.get("url"),
        "fonte": item.get("fonte"),
        "polaridade": polaridade,
        "categoria": categoria,
        "impacto": item.get("impacto", "nao_informado"),
        "resumo": item.get("resumo"),
        "mensagem_alerta": (
            "ALERTA: Existe informação relevante relacionada a este alimento. "
            "Clique aqui para ler a notícia."
            if categoria in {"alerta", "risco"}
            else None
        ),
        "valido_ate": item.get("valido_ate"),
        "data": item.get("data"),
        "tags_matched": item.get("tags") or [primary],
        "score": item.get("score"),
    }
