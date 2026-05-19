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

# ── TIER 1 — Editorial/jornalistico (headline principal, +2 score) ────────────
# Lingugem clara, jornalistica, comprensivel para o cliente final.
WHITELIST_TIER1 = {
    # Internacional
    "reuters.com",
    "bbc.com",
    "bbc.co.uk",
    "apnews.com",
    "theguardian.com",
    "medicalnewstoday.com",
    "healthline.com",
    "webmd.com",
    "sciencedaily.com",
    "medicalxpress.com",
    "eatingwell.com",
    "prevention.com",
    "everydayhealth.com",
    "health.usnews.com",
    # Brasil / PT-BR
    "g1.globo.com",
    "cnnbrasil.com.br",
    "folha.uol.com.br",
    "estadao.com.br",
    "veja.abril.com.br",
    "saude.abril.com.br",
    "uol.com.br",
    "exame.com",
}

# ── TIER 2 — Oficial/cientifico (lastro de credibilidade, +1 score) ───────────
# Fallback quando Tier 1 nao encontrar resultado. Linguagem tecnica aceita.
WHITELIST_TIER2 = {
    "anvisa.gov.br",
    "gov.br",
    "fiocruz.br",
    "agenciabrasil.ebc.com.br",
    "who.int",
    "fda.gov",
    "cdc.gov",
    "nih.gov",
    "mayoclinic.org",
    "health.harvard.edu",
    "hopkinsmedicine.org",
    "minsaude.gov.br",
    "cfn.org.br",
}

# Uniao de todos os dominios aceitos
WHITELIST_DOMAINS = WHITELIST_TIER1 | WHITELIST_TIER2

# Sinonimos expandidos para ingredientes comuns do menu Cibi Sana.
SYNONYMS = {
    # Proteinas animais
    "camarao": ["camarão"],
    "salmao": ["salmão"],
    "atum": ["atum"],
    "linguica": ["linguiça"],
    "frango": ["frango"],
    "tilapia": ["tilápia"],
    "bacalhau": ["bacalhau"],
    "file_de_peixe": ["filé de peixe", "peixe"],
    "carne_bovina": ["carne bovina", "carne vermelha"],
    "maminha": ["maminha", "carne bovina"],
    "sobrecoxa": ["sobrecoxa", "frango"],
    "ovos": ["ovo", "ovos"],
    "ovo": ["ovo", "ovos"],
    # Laticinios
    "leite": ["leite"],
    "queijo": ["queijo"],
    "iogurte": ["iogurte"],
    "manteiga": ["manteiga"],
    # Graos e carboidratos
    "arroz": ["arroz"],
    "feijao": ["feijão"],
    "lentilha": ["lentilha"],
    "grao_de_bico": ["grão-de-bico", "grão de bico"],
    "pao": ["pão"],
    "macarrao": ["macarrão"],
    "quinoa": ["quinoa"],
    "aveia": ["aveia"],
    # Vegetais
    "brocolis": ["brócolis"],
    "abobrinha": ["abobrinha"],
    "berinjela": ["berinjela"],
    "espinafre": ["espinafre"],
    "couve": ["couve"],
    "tomate": ["tomate"],
    "cenoura": ["cenoura"],
    "batata_doce": ["batata-doce", "batata doce"],
    "abobora": ["abóbora"],
    "alho": ["alho"],
    "cebola": ["cebola"],
    # Gorduras / outros
    "azeite": ["azeite"],
    "abacate": ["abacate"],
    "castanha": ["castanha"],
    "amendoa": ["amêndoa"],
    "nozes": ["nozes"],
    "banana": ["banana"],
    "maca": ["maçã"],
    "laranja": ["laranja"],
}

# Linguagem jornalistica clara — bonus +1 se presente no titulo.
ACCEPT_PATTERNS = re.compile(
    r"\b("
    r"especialistas (alertam|recomendam|indicam|confirmam)|"
    r"pesquisadores (descobr|revelam|identificam|apontam)|"
    r"(novo|recente) estudo|estudo (aponta|revela|sugere|indica|mostra)|"
    r"pesquisa (indica|revela|aponta|mostra|confirma)|"
    r"cientistas (confirmam|identificam|descobr)|"
    r"entenda por que|saiba (como|o que|por que)|"
    r"o que (acontece|diz a ciência|os estudos|os especialistas)|"
    r"consumo (excessivo|moderado|regular|elevado) de|"
    r"alimento (pode|ajuda|reduz|aumenta|protege|prejudica)|"
    r"nutricionistas (recomendam|alertam|explicam)|"
    r"médicos (aconselham|alertam|recomendam)|"
    r"benefíc(io|ios) (do|da|de)|risco(s)? de consumir|"
    r"estudo da (Harvard|USP|Fiocruz|UFMG|Oxford|Stanford|UNICAMP)"
    r")\b",
    re.IGNORECASE,
)

HEALTH_KEYWORDS = re.compile(
    r"\b("
    r"saúde|estudo|pesquisa|alerta|risco|benefíc|nutrient|"
    r"recall|alergia|sanitár|científ|recolh|"
    r"especialistas|pesquisadores|nutricionistas|médicos|"
    r"descoberta|revelou|confirma|aponta|sugere|indica|"
    r"prevenç|proteç|inflamaç|metabolis|cardiovascular|imunidade"
    r")\b",
    re.IGNORECASE,
)

REJECT_KEYWORDS = re.compile(
    r"\b("
    # Comercial / receita
    r"receita|recipe|como fazer|passo a passo|"
    r"oferta|desconto|promoç|cupom|preço|compre|"
    # Clickbait / terrorismo alimentar
    r"emagreça|perca peso|elimine gordura|seque a barriga|"
    r"milagre|milagroso|cure|cura definitiva|"
    r"dieta (detox|da moda|milagrosa)|suco (detox|milagroso)|"
    r"nunca mais coma|pare de comer|"
    # Diagnostico / prescricao nao-atribuida
    r"você (deve|precisa|tem que) (comer|evitar|consumir)|"
    r"faça isso|experimente (este|esse)|"
    # Sensacionalismo
    r"chocante|inacreditável|vai te surpreender|"
    r"(médicos|especialistas) não querem (que você saiba)|"
    r"a verdade (sobre|que esconderam)|"
    # Blog / baixa qualidade
    r"dica rápida|truque infalível|segredo"
    r")\b",
    re.IGNORECASE,
)

IMPERATIVE_REJECT = re.compile(
    r"^(não consuma|evite|deixe de|pare de|cuidado com|"
    r"nunca coma|jamais coma|pare de comer|elimine|"
    r"você precisa parar|beba mais|coma mais)",
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


def _domain_tier(domain):
    """Retorna 1 (editorial), 2 (oficial) ou 0 (nao listado)."""
    if not domain:
        return 0
    for w in WHITELIST_TIER1:
        if domain == w or domain.endswith("." + w):
            return 1
    for w in WHITELIST_TIER2:
        if domain == w or domain.endswith("." + w):
            return 2
    return 0


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
    """
    Calcula score (>=MIN_SCORE_DYNAMIC para entrar).

    Pontuacao:
      +3  prato no titulo
      +2  prato apenas no summary
      +2  dominio Tier 1 (editorial — preferencia ativa)
      +1  dominio Tier 2 (oficial — apenas lastro)
      +1  noticia com <= 7 dias
      +1  titulo tem padrao jornalistico confirmado (ACCEPT_PATTERNS)
    """
    titulo_n = _norm(item.get("titulo") or "")
    summary_n = _norm(item.get("summary") or "")
    titulo_raw = item.get("titulo") or ""
    dish_terms = [_norm(t) for t in SYNONYMS.get(dish_slug, [dish_slug.replace("_", " ")])]

    score = 0
    in_titulo = any(t and t in titulo_n for t in dish_terms)
    in_summary = any(t and t in summary_n for t in dish_terms)
    if in_titulo:
        score += 3
    elif in_summary:
        score += 2
    else:
        return 0   # prato ausente — bonus de tier nao se aplica

    domain = _domain(item.get("url") or "")
    tier = _domain_tier(domain)
    if tier == 1:
        score += 2   # editorial — preferencia ativa; Tier 2 nao pontua

    age = item.get("_age_days")
    if isinstance(age, int) and age <= 7:
        score += 1

    if ACCEPT_PATTERNS.search(titulo_raw):
        score += 1   # linguagem jornalistica confirmada

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
        "tier": _domain_tier(_domain(best["url"])),   # 1=editorial, 2=oficial
        "polaridade": _classify_polarity(best["titulo"], best.get("summary", "")),
        "data": (best.get("_data_dt") or datetime.now(timezone.utc)).isoformat(),
        "tags_matched": [dish_slug],
        "score": best_score,
    }
    _cache_set(cache_key, result, CACHE_TTL_HIT_SEC)
    return result
