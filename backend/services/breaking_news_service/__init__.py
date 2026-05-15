# -*- coding: utf-8 -*-
"""
SoulNutri — Breaking News Service (Camada 1).

Servico contextual de "breaking news" para o momento do scan no buffet.
Retorna no maximo 1 noticia com URL real e relacao semantica forte com o
prato escaneado. Retorna None se nenhuma atingir score minimo.

Esta camada e PREMIUM ONLY (gate aplicado no server.py).

Providers suportados:
- curated: le da collection Mongo `contextual_breaking_news` (seed manual).
- dynamic: futuro (RSS/API editorial com filtro semantico).

Uso:
    from services.breaking_news_service import get_breaking_news
    item = await get_breaking_news(
        dish_slug=..., family_slug=..., ingredientes=[...], category=...
    )
"""

from .api import get_breaking_news

__all__ = ["get_breaking_news"]
