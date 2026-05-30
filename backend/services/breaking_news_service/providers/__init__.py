# -*- coding: utf-8 -*-
"""Providers de breaking news contextual. Cada provider implementa fetch(...)."""

import logging

from . import curated

logger = logging.getLogger(__name__)

# Registry. Ordem em `api.py` controla qual e tentado primeiro.
PROVIDERS = {
    "curated": curated,
}

# Import protegido do provider dinamico (MVP EXPERIMENTAL — DORMENTE).
# Se import falhar (lib ausente, env quebrado), curated permanece operacional.
# A dormencia e garantida por api.py: PROVIDERS_ORDER == ["curated"].
try:
    from . import dynamic_health_news
    PROVIDERS["dynamic_health_news"] = dynamic_health_news
except Exception as e:  # noqa: BLE001
    logger.warning(f"[BREAKING_NEWS] dynamic_health_news indisponivel: {e}")

__all__ = ["PROVIDERS", "curated"]
