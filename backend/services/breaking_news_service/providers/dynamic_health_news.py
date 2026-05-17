# -*- coding: utf-8 -*-
"""
Provider: dynamic_health_news.

MVP EXPERIMENTAL — endpoint nao-oficial Google News RSS.
Busca noticias de saude relacionadas ao item escaneado e retorna no maximo
1 manchete com URL real, fonte confiavel e data recente.

PT-BR only nesta etapa (fallback EN proibido).

DORMENTE: este provider so e executado se incluido em PROVIDERS_ORDER
(api.py). No PR #4a, PROVIDERS_ORDER permanece ["curated"] — provider
nao roda em runtime.

DIRETRIZES JURIDICAS:
- Nao interpreta;
- Nao diagnostica;
- Nao reescreve manchete;
- Nao afirma contaminacao/seguranca;
- Apenas referencia materia existente da fonte.
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote, urlparse

import httpx
from lxml import etree
from pymongo.errors import PyMongoError

from .._mongo import get_db

logger = logging.getLogger(__name__)

# ─── CONFIG ──────────────────────────────────────────────────────────────────

MAX_AGE_DAYS_DYNAMIC = 30
MIN_SCORE_DYNAMIC = 3
FETCH_TIMEOUT_SEC = 2.0
CACHE_TTL_HIT_SEC = 6 * 3600
CACHE_TTL_MISS_SEC = 24 * 3600
CACHE_TTL_ERROR_SEC = 15 * 60

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
)

# Whitelist conservadora (8 dominios). Expandir apenas via curadoria humana.
WHITELIST_DOMAINS = {
    "anvisa.gov.br",
    "gov.br",
    "fiocruz.br",
    "reuters.com",
    "bbc.com",
    "bbc.co.uk",
    "agenciabrasil.ebc.com.br",
    "who.int",
    "fda.gov",
}

# Dominios "prime" recebem bonus de score.
WHITELIST_PRIME = {"reuters.com", "bbc.com", "anvisa.gov.br", "who.int", "fda.gov"}

# Sinonimos minimos (apenas acentuacao). Sem categorias amplas.
SYNONYMS = {
    "camarao": ["camarão"],
    "salmao": ["salmão"],
    "atum": ["atum"],
    "linguica": ["linguiça"],
    "frango": ["frango"],
    "brocolis": ["brócolis"],
    "ovo": ["ovo"],
    "leite": ["leite"],
    "queijo": ["queijo"],
    "pao": ["pão"],
}

HEALTH_KEYWORDS = re.compile(
    r"\b(saúde|estudo|pesquisa|alerta|risco|benefíc|nutrient|"
    r"recall|alergia|sanitár|científ|recolh)\b",
    re.IGNORECASE,
)

REJECT_KEYWORDS = re.compile(
    r"\b(receita|recipe|como fazer|oferta|desconto|promoç|cupom)\b",
    re.IGNORECASE,
)

IMPERATIVE_REJECT = re.compile(
    r"^(não consuma|evite|deixe de|pare de|cuidado com)",
    re.IGNORECASE,
)

ALERTA_KEYWORDS = re.compile(
    r"\b(alerta|risco|contamina|recall|alergia|tóxico|perigo|"
    r"surto|proib|inseguro|sanitár|recolh)\b",
    re.IGNORECASE,
)

BENEFICIO_KEYWORDS = re.compile(
    r"\b(benefíc|reduz|protege|melhora|previne|reforça|favorece)\b",
    re.IGNORECASE,
)

# ─── HELPERS ─────────────────────────────────────────────────────────────────

_indexes_created = False


def _ensure_cache_indexes():
    """Cria indice TTL idempotente no cache."""
    global _indexes_created
    if _indexes_created:
        return
    try:
        coll = get_db().breaking_news_cache
        coll.create_index([("expires_at", 1)], expireAfterSeconds=0, background=True)
        _indexes_created = True
        logger.info("[BREAKING_NEWS][dynamic] cache indices garantidos")
    except Exception as e:
        logger.warning(f"[BREAKING_NEWS][dynamic] falha indices cache: {e}")


def _norm(s):
    """Lowercase + remove diacriticos basicos para matching."""
    if not s:
        return ""
    s = s.lower()
    # Remoção simples de acentos comuns PT-BR
    table = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçñ", "aaaaaeeeeiiiiooooouuuucn")
    return s.translate(table)


def _build_query_pt(dish_slug):
    """Constroi query Google News PT-BR para o item escaneado."""
    syns = SYNONYMS.get(dish_slug, [dish_slug.replace("_", " ")])
    if len(syns) == 1:
        item_clause = f'"{syns[0]}"'
    else:
        item_clause = "(" + " OR ".join(f'"{s}"' for s in syns) + ")"
    return f"{item_clause} (saúde OR estudo OR pesquisa OR alerta) when:30d"


def _parse_rss(content):
    """Parsea XML RSS protegido contra XXE. Retorna list[dict]."""
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=True)
    try:
        root = etree.fromstring(content, parser=parser)
    except Exception as e:
        logger.warning(f"[BREAKING_NEWS][dynamic] parse XML falhou: {e}")
        return []
    items = []
    for it in root.iterfind(".//item"):
        items.append({
            "titulo": (it.findtext("title") or "").strip(),
            "url": (it.findtext("link") or "").strip(),
            "fonte": (it.findtext("source") or "").strip(),
            "pubdate": (it.findtext("pubDate") or "").strip(),
            "summary": (it.findtext("description") or "").strip(),
        })
    return items


def _parse_date(rfc822):
    """Converte data RFC822 para datetime aware UTC ou None."""
    if not rfc822:
        return None
    try:
        dt = parsedate_to_datetime(rfc822)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _domain(url):
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def _domain_in_whitelist(domain):
    if not domain:
        return False
    for w in WHITELIST_DOMAINS:
        if domain == w or domain.endswith("." + w):
            return True
    return False


def _passes_filters(item, dish_slug):
    """Aplica filtros C1-C5 + recencia + imperativo. True se passa, False se rejeita."""
    titulo = item.get("titulo") or ""
    summary = item.get("summary") or ""
    url = item.get("url") or ""

    if not titulo or not url:
        return False

    text = _norm(titulo + " " + summary)
    dish_terms = [_norm(t) for t in SYNONYMS.get(dish_slug, [dish_slug.replace("_", " ")])]

    # C1: item escaneado aparece no titulo ou summary
    if not any(t and t in text for t in dish_terms):
        return False

    # C2: fonte na whitelist (pelo dominio da URL)
    if not _domain_in_whitelist(_domain(url)):
        return False

    # C3: data recente
    dt = _parse_date(item.get("pubdate"))
    if not dt:
        return False
    age_days = (datetime.now(timezone.utc) - dt).days
    if age_days < 0 or age_days > MAX_AGE_DAYS_DYNAMIC:
        return False
    item["_age_days"] = age_days
    item["_data_dt"] = dt

    # C4: tem palavra-chave de saude
    if not HEALTH_KEYWORDS.search(titulo + " " + summary):
        return False

    # C5: nao e receita/blog/promocao
    if REJECT_KEYWORDS.search(titulo):
        return False

    # Anti-diagnostico: imperativo medico no titulo sem atribuir a fonte
    if IMPERATIVE_REJECT.search(titulo.strip()):
        return False

    return True


def _score_item(item, dish_slug):
    """Calcula score (>=MIN_SCORE_DYNAMIC para entrar)."""
    titulo_n = _norm(item.get("titulo") or "")
    summary_n = _norm(item.get("summary") or "")
    dish_terms = [_norm(t) for t in SYNONYMS.get(dish_slug, [dish_slug.replace("_", " ")])]

    score = 0
    in_titulo = any(t and t in titulo_n for t in dish_terms)
    in_summary = any(t and t in summary_n for t in dish_terms)
    if in_titulo:
        score += 3
    elif in_summary:
        score += 2

    domain = _domain(item.get("url") or "")
    if any(domain == w or domain.endswith("." + w) for w in WHITELIST_PRIME):
        score += 1

    age = item.get("_age_days")
    if isinstance(age, int) and age <= 7:
        score += 1

    return score


def _classify_polarity(titulo, summary):
    text = (titulo or "") + " " + (summary or "")
    has_alerta = bool(ALERTA_KEYWORDS.search(text))
    has_benef = bool(BENEFICIO_KEYWORDS.search(text))
    if has_alerta and not has_benef:
        return "alerta"
    if has_benef and not has_alerta:
        return "beneficio"
    return "neutro"


# ─── CACHE ───────────────────────────────────────────────────────────────────

def _cache_get(key):
    try:
        coll = get_db().breaking_news_cache
        doc = coll.find_one({"_id": key}, {"_id": 0})
        if not doc:
            return None
        exp = doc.get("expires_at")
        if isinstance(exp, datetime) and exp.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return doc
    except PyMongoError as e:
        logger.warning(f"[BREAKING_NEWS][dynamic] cache_get erro: {e}")
        return None


def _cache_set(key, best, ttl_seconds):
    try:
        coll = get_db().breaking_news_cache
        now = datetime.now(timezone.utc)
        coll.replace_one(
            {"_id": key},
            {
                "_id": key,
                "best": best,
                "fetched_at": now,
                "expires_at": now + timedelta(seconds=ttl_seconds),
            },
            upsert=True,
        )
    except PyMongoError as e:
        logger.warning(f"[BREAKING_NEWS][dynamic] cache_set erro: {e}")


# ─── FETCH EXTERNO ───────────────────────────────────────────────────────────

async def _fetch_external(query):
    """Faz GET na RSS Google News. Retorna bytes ou None em erro/timeout."""
    url = GOOGLE_NEWS_RSS.format(q=quote(query))
    try:
        async with httpx.AsyncClient(timeout=FETCH_TIMEOUT_SEC) as c:
            r = await c.get(url, headers={"User-Agent": "SoulNutri/1.0"})
            if r.status_code != 200:
                return None
            return r.content
    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.info(f"[BREAKING_NEWS][dynamic] fetch falhou: {e}")
        return None


# ─── API DO PROVIDER ─────────────────────────────────────────────────────────

async def fetch(dish_slug, family_slug, ingredientes, category):
    """
    Entry-point do provider. Retorna dict ou None.

    DORMENTE: nao e chamado em runtime enquanto PROVIDERS_ORDER == ["curated"].
    """
    if not dish_slug:
        return None

    _ensure_cache_indexes()
    cache_key = f"dyn:{dish_slug}:pt"

    cached = _cache_get(cache_key)
    if cached is not None:
        return cached.get("best")

    query = _build_query_pt(dish_slug)
    content = await _fetch_external(query)
    if content is None:
        _cache_set(cache_key, None, CACHE_TTL_ERROR_SEC)
        return None

    items = _parse_rss(content)
    if not items:
        _cache_set(cache_key, None, CACHE_TTL_MISS_SEC)
        return None

    valid = [it for it in items if _passes_filters(it, dish_slug)]
    if not valid:
        _cache_set(cache_key, None, CACHE_TTL_MISS_SEC)
        return None

    scored = []
    for it in valid:
        s = _score_item(it, dish_slug)
        if s >= MIN_SCORE_DYNAMIC:
            scored.append((s, it))

    if not scored:
        _cache_set(cache_key, None, CACHE_TTL_MISS_SEC)
        return None

    scored.sort(key=lambda x: (x[0], x[1].get("_data_dt") or datetime.min), reverse=True)
    best_score, best = scored[0]

    result = {
        "titulo": best["titulo"],
        "url": best["url"],
        "fonte": best.get("fonte") or _domain(best["url"]),
        "polaridade": _classify_polarity(best["titulo"], best.get("summary", "")),
        "data": (best.get("_data_dt") or datetime.now(timezone.utc)).isoformat(),
        "tags_matched": [dish_slug],
        "score": best_score,
    }
    _cache_set(cache_key, result, CACHE_TTL_HIT_SEC)
    return result
