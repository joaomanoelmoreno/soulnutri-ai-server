# -*- coding: utf-8 -*-
"""
API publica do breaking_news_service.

Orquestra providers em ordem configuravel. Primeiro provider que retornar
item relevante vence. Erros em um provider nao bloqueiam os demais.
"""

import logging

from .providers import PROVIDERS

logger = logging.getLogger(__name__)

# Ordem dos providers. Em PR #1 so existe "curated".
# Para FASE 6 (dinamico), basta adicionar "dynamic" aqui ou expor via setting.
PROVIDERS_ORDER = ["curated"]


async def get_breaking_news(dish_slug, family_slug, ingredientes, category):
    """
    Retorna 1 noticia contextual relevante ou None.

    Schema do retorno:
        {
          "titulo": str,
          "url": str,
          "fonte": str,
          "polaridade": "alerta" | "beneficio" | "neutro",
          "data": "ISO-8601",
          "tags_matched": [str, ...],
          "origem": "curated" | "dynamic",
        }

    Silencio (None) e o estado padrao quando nada relevante e encontrado.
    """
    for name in PROVIDERS_ORDER:
        provider = PROVIDERS.get(name)
        if not provider:
            logger.warning(f"[BREAKING_NEWS] provider desconhecido: {name}")
            continue
        try:
            item = await provider.fetch(
                dish_slug=dish_slug,
                family_slug=family_slug,
                ingredientes=ingredientes,
                category=category,
            )
        except Exception as e:
            logger.warning(f"[BREAKING_NEWS] provider={name} falhou: {e}")
            continue

        if item:
            item["origem"] = name
            logger.info(
                f"[BREAKING_NEWS] hit provider={name} "
                f"polaridade={item.get('polaridade')} "
                f"score={item.get('score')} "
                f"tags_matched={item.get('tags_matched')}"
            )
            return item

    return None
