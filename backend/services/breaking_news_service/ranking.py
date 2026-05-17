# -*- coding: utf-8 -*-
"""
Ranking semantico para breaking news contextuais (Camada 1).

Funcoes puras, testaveis. Sem efeitos colaterais. Sem I/O.
"""

import re
from datetime import datetime, timezone


# Score minimo para o item ser considerado relevante.
# (matches >= 1 ja garante score 2 via pesos abaixo.)
MIN_SCORE = 2

# Janela maxima de recencia para um item ser considerado.
MAX_AGE_DAYS = 365

# Janela "recente" — entrega bonus extra.
RECENT_AGE_DAYS = 90

# Pesos
WEIGHT_TAG_MATCH = 2     # por tag interseccionada
WEIGHT_RECENT_BONUS = 1  # se data dentro de RECENT_AGE_DAYS
WEIGHT_ALERTA_BONUS = 1  # se polaridade == "alerta"


def slugify(value):
    """Normaliza para slug: lower, sem acento de tipo ascii basico, _ como sep."""
    s = (value or '').lower().strip()
    s = re.sub(r'[^a-z0-9\s_-]', '', s)
    s = re.sub(r'[\s_-]+', '_', s)
    return s


def build_term_set(dish_slug, family_slug, ingredientes, category):
    """
    Constroi conjunto de termos relevantes para matching contra tags da noticia.
    Inclui o slug completo + cada parte separada por '_' (com >= 3 chars).
    """
    terms = set()

    for raw in (dish_slug, family_slug, category):
        if not raw:
            continue
        slug = slugify(raw)
        if not slug:
            continue
        terms.add(slug)
        for part in slug.split('_'):
            if len(part) >= 3:
                terms.add(part)

    for ing in (ingredientes or []):
        s = slugify(ing)
        if not s:
            continue
        terms.add(s)
        for part in s.split('_'):
            if len(part) >= 3:
                terms.add(part)

    return terms


def score_item(doc, terms):
    """
    Calcula score de relevancia de um documento de noticia frente ao conjunto
    de termos do prato. Retorna (score:int, matched_tags:list[str]).
    """
    tags = set(doc.get('tags') or [])
    matched = tags & terms
    score = len(matched) * WEIGHT_TAG_MATCH

    data = doc.get('data')
    if isinstance(data, datetime):
        # Normaliza timezone
        d = data if data.tzinfo else data.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - d).days
        if 0 <= age_days <= RECENT_AGE_DAYS:
            score += WEIGHT_RECENT_BONUS

    if doc.get('polaridade') == 'alerta':
        score += WEIGHT_ALERTA_BONUS

    return score, sorted(matched)


def is_relevant(score):
    """Decide se score atinge limiar minimo para exibicao."""
    return score >= MIN_SCORE
