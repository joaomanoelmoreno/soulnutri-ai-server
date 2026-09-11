# -*- coding: utf-8 -*-
"""Busca e triagem de conteudo alimentar via Perplexity Search e Agent API.

Etapa 2: modulo isolado, somente ``dry-run``. Este arquivo nao grava no MongoDB,
nao e importado por ``server.py`` e nunca deve ser chamado durante o scan.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import parse_qs, urlparse

import httpx


PERPLEXITY_SEARCH_URL = "https://api.perplexity.ai/search"
PERPLEXITY_AGENT_URL = "https://api.perplexity.ai/v1/agent"
PERPLEXITY_AGENT_MODEL = "openai/gpt-5.6-luna"
PERPLEXITY_GENERAL_MODEL = "perplexity/glm-5.3-flash"
PERPLEXITY_ALERT_MODEL = "openai/gpt-5.6-luna"
REQUEST_TIMEOUT_SECONDS = 12.0
AGENT_TIMEOUT_SECONDS = 60.0
AGENT_BATCH_SIZE = 2

# Limite oficial da Search API: no maximo 20 dominios por allowlist.
TRUSTED_DOMAINS = (
    "anvisa.gov.br",
    "fda.gov",
    "foodsafety.gov",
    "who.int",
    "ec.europa.eu",
    "food.gov.uk",
    "canada.ca",
    "health.gov.au",
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "cnn.com",
    "uol.com.br",
    "estadao.com.br",
    "pubmed.ncbi.nlm.nih.gov",
    "nature.com",
    "science.org",
    "thelancet.com",
    "bmj.com",
    "harvard.edu",
)

SOURCE_NAMES = {
    "anvisa.gov.br": "Anvisa",
    "fda.gov": "FDA",
    "foodsafety.gov": "FoodSafety.gov",
    "who.int": "OMS",
    "ec.europa.eu": "Comissao Europeia",
    "food.gov.uk": "Food Standards Agency",
    "canada.ca": "Governo do Canada",
    "health.gov.au": "Department of Health Australia",
    "reuters.com": "Reuters",
    "apnews.com": "Associated Press",
    "bbc.com": "BBC",
    "cnn.com": "CNN",
    "uol.com.br": "UOL",
    "estadao.com.br": "Estadao",
    "pubmed.ncbi.nlm.nih.gov": "PubMed",
    "nature.com": "Nature",
    "science.org": "Science",
    "thelancet.com": "The Lancet",
    "bmj.com": "BMJ",
    "harvard.edu": "Harvard",
}

CATEGORY_MAX_AGE_DAYS = {
    "alerta": 7,
    "boa_noticia": 30,
    "novidade": 30,
    "pesquisa": 90,
    "beneficio": 365,
    "risco": 365,
    "combinacao": 365,
    "curiosidade": 365,
}

ALERT_TERMS = (
    "alert", "warning", "recall", "recalled", "outbreak", "contamination",
    "contaminated", "listeria", "salmonella", "e. coli", "mercury",
    "food poisoning", "alergeno nao declarado", "alérgeno não declarado",
    "recolhimento", "contaminacao", "contaminação", "surto", "intoxicacao",
    "intoxicação",
)
ALERT_ROUTING_TERMS = (
    "food safety alert", "alert", "warning", "recall", "recalled", "outbreak",
    "contamination", "contaminated", "food poisoning", "undeclared allergen",
    "alergeno nao declarado", "alérgeno não declarado", "recolhimento",
    "contaminacao", "contaminação", "surto", "intoxicacao", "intoxicação",
)
RESEARCH_TERMS = (
    "study", "research", "clinical trial", "meta-analysis", "systematic review",
    "estudo", "pesquisa", "ensaio clinico", "ensaio clínico", "nova descoberta",
)
COMBINATION_TERMS = (
    "absorption", "bioavailability", "synergy", "combine", "pairing",
    "absorcao", "absorção", "biodisponibilidade", "sinergia", "combinar",
    "combinacao", "combinação", "potencializa",
)
RISK_TERMS = (
    "risk", "adverse", "harm", "caution", "contraindication", "excess",
    "risco", "efeito adverso", "cuidado", "contraindicacao", "contraindicação",
    "excesso",
)
BENEFIT_TERMS = (
    "benefit", "improve", "protect", "healthy", "health effect",
    "beneficio", "benefício", "melhora", "protege", "saudavel", "saudável",
)
POSITIVE_TERMS = (
    "good news", "promising", "breakthrough", "positive result", "advance",
    "boa noticia", "boa notícia", "promissor", "resultado positivo", "avanco",
    "avanço",
)
NEWS_TERMS = ("news", "new", "latest", "novidade", "novo", "nova", "recente")

BROAD_ALERT_TERMS = (
    "worldwide", "global", "international", "exported", "multiple countries",
    "several countries", "nationwide", "national recall", "multiple states",
    "several states", "across the country", "distributed nationally",
    "distribuido nacionalmente", "distribuído nacionalmente", "exportado",
    "varios paises", "vários países", "diversos paises", "diversos países",
    "todo o pais", "todo o país", "surto nacional", "alerta nacional",
)

FORBIDDEN_HOSTS = {"rmb.reuters.com"}
FORBIDDEN_PATH_PARTS = ("/rss/", "/feed/", "/search/", "/tag/")

AGENT_CATEGORIES = (
    "alerta",
    "boa_noticia",
    "novidade",
    "pesquisa",
    "beneficio",
    "risco",
    "combinacao",
    "curiosidade",
    "irrelevante",
)
ALERT_ACCEPTED_SCOPES = {"global", "multinacional", "nacional"}

AGENT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "relevante": {"type": "boolean"},
                    "categoria": {"type": "string", "enum": list(AGENT_CATEGORIES)},
                    "alimento_relacionado": {"type": "boolean"},
                    "abrangencia": {
                        "type": "string",
                        "enum": [
                            "global", "multinacional", "nacional", "regional",
                            "local", "nao_informada",
                        ],
                    },
                    "vigente": {"type": "boolean"},
                    "confianca": {"type": "string", "enum": ["alta", "media", "baixa"]},
                    "manchete_pt": {"type": "string"},
                    "resumo_pt": {"type": "string"},
                    "motivo": {"type": "string"},
                },
                "required": [
                    "id", "relevante", "categoria", "alimento_relacionado",
                    "abrangencia", "vigente", "confianca", "manchete_pt",
                    "resumo_pt", "motivo",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}


class PerplexityConfigurationError(RuntimeError):
    """Configuracao ausente ou invalida."""


class PerplexitySearchError(RuntimeError):
    """Falha controlada na Search API."""


class PerplexityAgentError(RuntimeError):
    """Falha controlada na classificacao do Agent API."""


def normalize_text(value: Any) -> str:
    """Normaliza texto para comparacoes conservadoras."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text)).strip()


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    normalized_terms = (normalize_text(term) for term in terms)
    return any(term and term in text for term in normalized_terms)


def _domain(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def normalize_url(value: Any) -> str:
    """Converte URL Markdown da Search API para URL direta."""
    raw = str(value or "").strip()
    match = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", raw)
    if match:
        return match.group(2).strip()
    return raw


def _trusted_domain(domain: str) -> Optional[str]:
    for trusted in TRUSTED_DOMAINS:
        if domain == trusted or domain.endswith("." + trusted):
            return trusted
    return None


def validate_direct_url(url: str) -> List[str]:
    """Retorna motivos de rejeicao; lista vazia significa URL aceita."""
    reasons: List[str] = []
    parsed = urlparse(url or "")
    domain = _domain(url)
    path = parsed.path or "/"

    if parsed.scheme != "https" or not domain:
        reasons.append("url_nao_https")
        return reasons
    if not _trusted_domain(domain):
        reasons.append("fonte_fora_allowlist")
    if domain in FORBIDDEN_HOSTS:
        reasons.append("url_intermediaria")
    if any(part in path.lower() for part in FORBIDDEN_PATH_PARTS):
        reasons.append("url_nao_artigo")
    if re.fullmatch(r"/\d{4}/\d{1,2}/?", path):
        reasons.append("pagina_de_arquivo")

    status_values = [v.lower() for v in parse_qs(parsed.query).get("status", [])]
    if "resolved" in status_values:
        reasons.append("alerta_encerrado")
    return reasons


def parse_publication_date(value: Any) -> Optional[datetime]:
    if not value:
        return None
    raw = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        try:
            parsed = datetime.strptime(raw[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def classify_content(title: str, snippet: str) -> Optional[str]:
    text = normalize_text(f"{title} {snippet}")
    if _contains_any(text, ALERT_TERMS):
        return "alerta"
    if _contains_any(text, RESEARCH_TERMS):
        return "pesquisa"
    if _contains_any(text, COMBINATION_TERMS):
        return "combinacao"
    if _contains_any(text, RISK_TERMS):
        return "risco"
    if _contains_any(text, BENEFIT_TERMS):
        return "beneficio"
    if _contains_any(text, POSITIVE_TERMS):
        return "boa_noticia"
    if _contains_any(text, NEWS_TERMS):
        return "novidade"
    return None


def _mentions_food(title: str, snippet: str, food: str) -> bool:
    text = normalize_text(f"{title} {snippet}")
    food_normalized = normalize_text(food)
    if not food_normalized:
        return False
    padded_text = f" {text} "
    if f" {food_normalized} " in padded_text:
        return True
    meaningful = [token for token in food_normalized.split() if len(token) >= 4]
    return bool(meaningful) and all(f" {token} " in padded_text for token in meaningful)


def _mentions_any_food(
    title: str,
    snippet: str,
    food: str,
    aliases: Iterable[str],
) -> bool:
    return any(
        _mentions_food(title, snippet, name)
        for name in [food, *aliases]
        if str(name or "").strip()
    )


def _prefilter_for_food(
    food: str,
    raw_results: Iterable[Dict[str, Any]],
    aliases: Iterable[str],
) -> tuple:
    """Remove resultados inseguros antes de qualquer chamada ao Agent API."""
    eligible: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen_urls = set()
    for raw in raw_results:
        if not isinstance(raw, dict):
            continue
        url = normalize_url(raw.get("url"))
        title = str(raw.get("title") or "").strip()
        snippet = str(raw.get("snippet") or "").strip()
        reasons = validate_direct_url(url)
        if not title:
            reasons.append("titulo_ausente")
        if not parse_publication_date(raw.get("date")):
            reasons.append("data_ausente_ou_invalida")
        if not _mentions_any_food(title, snippet, food, aliases):
            reasons.append("alimento_nao_confirmado")
        if url in seen_urls:
            reasons.append("url_duplicada")
        if reasons:
            rejected.append({
                "id": _candidate_id(url) if url else None,
                "titulo": title,
                "url": url,
                "reasons": sorted(set(reasons)),
            })
            continue
        seen_urls.add(url)
        eligible.append(raw)
    return eligible, rejected


def _has_broad_alert_scope(title: str, snippet: str) -> bool:
    text = normalize_text(f"{title} {snippet}")
    return _contains_any(text, BROAD_ALERT_TERMS)


def evaluate_result(
    raw: Dict[str, Any],
    food: str,
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Avalia um resultado sem gravar ou publicar nada."""
    now_utc = now or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)

    title = str(raw.get("title") or "").strip()
    snippet = str(raw.get("snippet") or "").strip()
    url = normalize_url(raw.get("url"))
    published_at = parse_publication_date(raw.get("date"))
    category = classify_content(title, snippet)
    reasons = validate_direct_url(url)

    if not title:
        reasons.append("titulo_ausente")
    if not snippet:
        reasons.append("resumo_ausente")
    if not _mentions_food(title, snippet, food):
        reasons.append("alimento_nao_confirmado")
    if not category:
        reasons.append("categoria_nao_confirmada")
    if not published_at:
        reasons.append("data_ausente_ou_invalida")
    elif category:
        age = now_utc - published_at
        if age < timedelta(days=-1):
            reasons.append("data_futura")
        elif age > timedelta(days=CATEGORY_MAX_AGE_DAYS[category]):
            reasons.append("conteudo_expirado")
    if category == "alerta" and not _has_broad_alert_scope(title, snippet):
        reasons.append("abrangencia_insuficiente")

    trusted = _trusted_domain(_domain(url))
    accepted = not reasons
    valid_until = None
    if accepted and published_at and category:
        valid_until = published_at + timedelta(days=CATEGORY_MAX_AGE_DAYS[category])

    return {
        "id": hashlib.sha256(url.encode("utf-8")).hexdigest()[:24] if url else None,
        "status": "candidate" if accepted else "rejected",
        "accepted": accepted,
        "reasons": sorted(set(reasons)),
        "categoria": category,
        "titulo": title,
        "resumo": snippet[:600],
        "url": url,
        "fonte": SOURCE_NAMES.get(trusted or "", trusted or ""),
        "data": published_at.isoformat() if published_at else None,
        "valido_ate": valid_until.isoformat() if valid_until else None,
        "tags": [normalize_text(food).replace(" ", "_")],
        "origem": "perplexity_search",
        "ativo": False,
    }


def build_queries(food: str, aliases: Optional[Iterable[str]] = None) -> List[str]:
    """Cinco angulos em uma unica unidade faturavel da Search API."""
    clean_food = " ".join(str(food or "").split())
    if not clean_food:
        raise ValueError("food obrigatorio")
    names = [clean_food]
    for alias in aliases or []:
        clean_alias = " ".join(str(alias or "").split())
        if clean_alias and normalize_text(clean_alias) not in {
            normalize_text(name) for name in names
        }:
            names.append(clean_alias)
    food_expression = " OR ".join(f'"{name}"' for name in names[:4])
    return [
        f'{food_expression} food safety alert contamination recall outbreak exported international',
        f'{food_expression} good news nutrition positive health discovery recent',
        f'{food_expression} new nutrition research study clinical trial systematic review',
        f'{food_expression} health benefits risks evidence recent',
        f'{food_expression} nutrient absorption food combination synergy curiosity research',
    ]


def _candidate_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def _extract_agent_output(data: Dict[str, Any]) -> Dict[str, Any]:
    text = data.get("output_text")
    if not text:
        parts: List[str] = []
        for item in data.get("output") or []:
            if not isinstance(item, dict):
                continue
            for content in item.get("content") or []:
                if isinstance(content, dict) and content.get("type") == "output_text":
                    parts.append(str(content.get("text") or ""))
        text = "".join(parts)
    if not isinstance(text, str) or not text.strip():
        raise PerplexityAgentError("resposta do Agent API sem output_text")
    try:
        parsed = json.loads(text)
    except (TypeError, ValueError) as exc:
        raise PerplexityAgentError("Agent API retornou JSON invalido") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("items"), list):
        raise PerplexityAgentError("Agent API retornou schema inesperado")
    return parsed


def _build_agent_prompt(
    food: str,
    aliases: Iterable[str],
    candidates: List[Dict[str, Any]],
    now_utc: datetime,
) -> str:
    compact = [
        {
            "id": item["id"],
            "titulo": item["title"],
            "resumo": item["snippet"],
            "fonte": item["source"],
            "data": item["date"],
        }
        for item in candidates
    ]
    return (
        "Voce e um classificador editorial conservador de conteudo alimentar. "
        "Analise SOMENTE os candidatos fornecidos, sem pesquisar e sem acrescentar fatos. "
        f"Alimento: {food}. Sinonimos: {list(aliases)}. Data UTC: {now_utc.date().isoformat()}. "
        "Marque alimento_relacionado somente quando a relacao for direta. "
        "Categorias validas: alerta, boa_noticia, novidade, pesquisa, beneficio, risco, "
        "combinacao, curiosidade ou irrelevante. Alerta significa recall, contaminacao, "
        "surto, adulteracao ou alergeno nao declarado ainda relevante. Para alerta, "
        "classifique a abrangencia; marca local ou regional sem distribuicao ampla nao basta. "
        "Vigente deve ser falso quando o texto indicar encerrado ou resolvido. "
        "Use confianca baixa se o titulo/resumo nao sustentar a decisao. "
        "Crie manchete jornalistica neutra em portugues com no maximo 18 palavras e resumo "
        "original com no maximo 40 palavras. Nao invente fonte, URL, data ou alcance. "
        "Devolva exatamente um item para cada id recebido. Candidatos JSON: "
        + json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
    )


async def classify_results_with_agent(
    food: str,
    raw_results: Iterable[Dict[str, Any]],
    *,
    aliases: Optional[Iterable[str]] = None,
    api_key: Optional[str] = None,
    client: Optional[Any] = None,
    now: Optional[datetime] = None,
    model: str = PERPLEXITY_AGENT_MODEL,
) -> Dict[str, Any]:
    """Classifica resultados ja encontrados; nao pesquisa, persiste ou publica."""
    key = (api_key or os.getenv("PERPLEXITY_API_KEY") or "").strip()
    if not key.startswith("pplx-"):
        raise PerplexityConfigurationError("PERPLEXITY_API_KEY ausente ou invalida")

    now_utc = now or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_utc = now_utc.astimezone(timezone.utc)
    alias_list = [str(alias).strip() for alias in aliases or [] if str(alias).strip()]

    prefiltered: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen_urls = set()
    for raw in raw_results:
        if not isinstance(raw, dict):
            continue
        url = normalize_url(raw.get("url"))
        title = str(raw.get("title") or "").strip()
        snippet = str(raw.get("snippet") or "").strip()
        published = parse_publication_date(raw.get("date"))
        reasons = validate_direct_url(url)
        if not title:
            reasons.append("titulo_ausente")
        if not published:
            reasons.append("data_ausente_ou_invalida")
        if not _mentions_any_food(title, snippet, food, alias_list):
            reasons.append("alimento_nao_confirmado")
        if url in seen_urls:
            reasons.append("url_duplicada")
        if reasons:
            rejected.append({
                "id": _candidate_id(url) if url else None,
                "titulo": title,
                "url": url,
                "reasons": sorted(set(reasons)),
            })
            continue
        seen_urls.add(url)
        trusted = _trusted_domain(_domain(url))
        prefiltered.append({
            "id": _candidate_id(url),
            "title": title,
            "snippet": snippet[:1200],
            "url": url,
            "date": published.isoformat(),
            "published_at": published,
            "source": SOURCE_NAMES.get(trusted or "", trusted or ""),
        })

    if not prefiltered:
        return {
            "ok": True, "dry_run": True, "model": model, "candidate_count": 0,
            "rejected_count": len(rejected), "candidates": [], "rejected": rejected,
            "usage": {}, "agent_calls": 0,
        }

    payload = {
        "model": model,
        "input": _build_agent_prompt(food, alias_list, prefiltered, now_utc),
        "tools": [],
        "max_output_tokens": min(2400, 180 + len(prefiltered) * 180),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "soulnutri_food_content_v1",
                "schema": AGENT_RESPONSE_SCHEMA,
            },
        },
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    async def _request(http_client: Any) -> Dict[str, Any]:
        try:
            response = await http_client.post(
                PERPLEXITY_AGENT_URL, headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise PerplexityAgentError(
                f"falha no Agent API: {type(exc).__name__}"
            ) from exc
        if not isinstance(data, dict):
            raise PerplexityAgentError("resposta invalida do Agent API")
        return data

    if client is None:
        async with httpx.AsyncClient(timeout=AGENT_TIMEOUT_SECONDS) as owned_client:
            response_data = await _request(owned_client)
    else:
        response_data = await _request(client)

    agent_data = _extract_agent_output(response_data)
    by_id = {item["id"]: item for item in prefiltered}
    accepted: List[Dict[str, Any]] = []
    returned_ids = set()
    for decision in agent_data["items"]:
        if not isinstance(decision, dict):
            continue
        item_id = str(decision.get("id") or "")
        original = by_id.get(item_id)
        if not original or item_id in returned_ids:
            continue
        returned_ids.add(item_id)
        category = decision.get("categoria")
        reasons: List[str] = []
        if not decision.get("relevante") or category == "irrelevante":
            reasons.append("agent_irrelevante")
        if not decision.get("alimento_relacionado"):
            reasons.append("alimento_nao_confirmado")
        if decision.get("confianca") == "baixa":
            reasons.append("confianca_baixa")
        if category not in CATEGORY_MAX_AGE_DAYS:
            reasons.append("categoria_nao_confirmada")
        else:
            age = now_utc - original["published_at"]
            if age < timedelta(days=-1):
                reasons.append("data_futura")
            elif age > timedelta(days=CATEGORY_MAX_AGE_DAYS[category]):
                reasons.append("conteudo_expirado")
        if category == "alerta":
            if not decision.get("vigente"):
                reasons.append("alerta_encerrado")
            if decision.get("abrangencia") not in ALERT_ACCEPTED_SCOPES:
                reasons.append("abrangencia_insuficiente")

        if reasons:
            rejected.append({
                "id": item_id,
                "titulo": original["title"],
                "url": original["url"],
                "reasons": sorted(set(reasons)),
                "agent": decision,
            })
            continue

        valid_until = original["published_at"] + timedelta(
            days=CATEGORY_MAX_AGE_DAYS[category]
        )
        accepted.append({
            "id": item_id,
            "status": "candidate",
            "accepted": True,
            "categoria": category,
            "titulo": str(decision.get("manchete_pt") or original["title"]).strip(),
            "titulo_original": original["title"],
            "resumo": str(decision.get("resumo_pt") or original["snippet"]).strip(),
            # Fonte, URL e data sao SEMPRE copiados do Search API, nunca do modelo.
            "url": original["url"],
            "fonte": original["source"],
            "data": original["date"],
            "valido_ate": valid_until.isoformat(),
            "abrangencia": decision.get("abrangencia"),
            "confianca": decision.get("confianca"),
            "classificador": response_data.get("model") or model,
            "tags": [normalize_text(food).replace(" ", "_")],
            "origem": "perplexity_search_agent",
            "ativo": False,
        })

    for missing_id in sorted(set(by_id) - returned_ids):
        original = by_id[missing_id]
        rejected.append({
            "id": missing_id,
            "titulo": original["title"],
            "url": original["url"],
            "reasons": ["agent_sem_decisao"],
        })

    return {
        "ok": True,
        "dry_run": True,
        "model": response_data.get("model") or model,
        "candidate_count": len(accepted),
        "rejected_count": len(rejected),
        "candidates": accepted,
        "rejected": rejected,
        "usage": response_data.get("usage") or {},
        "agent_calls": 1,
    }


def _merge_usage(total: Dict[str, Any], current: Dict[str, Any]) -> None:
    """Soma apenas metricas numericas de uso/custo devolvidas pela API."""
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        value = current.get(key)
        if isinstance(value, (int, float)):
            total[key] = total.get(key, 0) + value
    current_cost = current.get("cost") or {}
    if isinstance(current_cost, dict):
        total_cost = total.setdefault("cost", {})
        for key, value in current_cost.items():
            if isinstance(value, (int, float)):
                total_cost[key] = total_cost.get(key, 0) + value
            elif key == "currency" and value:
                total_cost[key] = value


async def classify_results_in_batches(
    food: str,
    raw_results: Iterable[Dict[str, Any]],
    *,
    aliases: Optional[Iterable[str]] = None,
    api_key: Optional[str] = None,
    client: Optional[Any] = None,
    now: Optional[datetime] = None,
    model: str = PERPLEXITY_AGENT_MODEL,
    batch_size: int = AGENT_BATCH_SIZE,
) -> Dict[str, Any]:
    """Classifica sequencialmente em lotes pequenos para evitar respostas lentas."""
    if batch_size < 1 or batch_size > AGENT_BATCH_SIZE:
        raise ValueError(f"batch_size deve estar entre 1 e {AGENT_BATCH_SIZE}")
    items = [item for item in raw_results if isinstance(item, dict)]
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    usage: Dict[str, Any] = {}
    batch_errors = 0
    agent_calls = 0

    async def _run(http_client: Any) -> None:
        nonlocal batch_errors, agent_calls
        for batch_number, batch in enumerate(batches, 1):
            try:
                result = await classify_results_with_agent(
                    food,
                    batch,
                    aliases=aliases,
                    api_key=api_key,
                    client=http_client,
                    now=now,
                    model=model,
                )
            except PerplexityAgentError:
                batch_errors += 1
                agent_calls += 1
                for raw in batch:
                    url = normalize_url(raw.get("url"))
                    rejected.append({
                        "id": _candidate_id(url) if url else None,
                        "titulo": str(raw.get("title") or "").strip(),
                        "url": url,
                        "reasons": ["agent_lote_falhou"],
                        "batch": batch_number,
                        "classificador": model,
                    })
                continue
            accepted.extend(result.get("candidates") or [])
            rejected.extend(result.get("rejected") or [])
            _merge_usage(usage, result.get("usage") or {})
            agent_calls += result.get("agent_calls", 0)

    if client is None:
        async with httpx.AsyncClient(timeout=AGENT_TIMEOUT_SECONDS) as owned_client:
            await _run(owned_client)
    else:
        await _run(client)

    return {
        "ok": batch_errors == 0,
        "partial": batch_errors > 0 and bool(accepted),
        "dry_run": True,
        "model": model,
        "batch_size": batch_size,
        "batch_count": len(batches),
        "batch_errors": batch_errors,
        "agent_calls": agent_calls,
        "candidate_count": len(accepted),
        "rejected_count": len(rejected),
        "candidates": accepted,
        "rejected": rejected,
        "usage": usage,
    }


async def classify_results_hybrid(
    food: str,
    raw_results: Iterable[Dict[str, Any]],
    *,
    aliases: Optional[Iterable[str]] = None,
    api_key: Optional[str] = None,
    client: Optional[Any] = None,
    now: Optional[datetime] = None,
    batch_size: int = AGENT_BATCH_SIZE,
) -> Dict[str, Any]:
    """Usa Luna para possiveis alertas e GLM Flash para conteudo geral."""
    alias_list = [str(alias).strip() for alias in aliases or [] if str(alias).strip()]
    eligible, pre_rejected = _prefilter_for_food(food, raw_results, alias_list)
    possible_alerts: List[Dict[str, Any]] = []
    general_content: List[Dict[str, Any]] = []
    for raw in eligible:
        text = normalize_text(
            f"{raw.get('title') or ''} {raw.get('snippet') or ''}"
        )
        if _contains_any(text, ALERT_ROUTING_TERMS):
            possible_alerts.append(raw)
        else:
            general_content.append(raw)

    group_results: List[Dict[str, Any]] = []
    if possible_alerts:
        group_results.append(await classify_results_in_batches(
            food,
            possible_alerts,
            aliases=aliases,
            api_key=api_key,
            client=client,
            now=now,
            model=PERPLEXITY_ALERT_MODEL,
            batch_size=batch_size,
        ))
    if general_content:
        group_results.append(await classify_results_in_batches(
            food,
            general_content,
            aliases=aliases,
            api_key=api_key,
            client=client,
            now=now,
            model=PERPLEXITY_GENERAL_MODEL,
            batch_size=batch_size,
        ))

    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = list(pre_rejected)
    usage: Dict[str, Any] = {}
    agent_calls = 0
    for result in group_results:
        accepted.extend(result.get("candidates") or [])
        rejected.extend(result.get("rejected") or [])
        _merge_usage(usage, result.get("usage") or {})
        agent_calls += result.get("agent_calls", 0)

    batch_errors = sum(result.get("batch_errors", 0) for result in group_results)
    failed_models = sorted({
        str(item.get("classificador"))
        for item in rejected
        if "agent_lote_falhou" in (item.get("reasons") or [])
        and item.get("classificador")
    })
    return {
        "ok": all(result.get("ok") for result in group_results) if group_results else True,
        "partial": batch_errors > 0 and bool(accepted),
        "dry_run": True,
        "model": "hibrido",
        "models": [
            model for model, items in (
                (PERPLEXITY_ALERT_MODEL, possible_alerts),
                (PERPLEXITY_GENERAL_MODEL, general_content),
            ) if items
        ],
        "batch_size": batch_size,
        "batch_count": sum(result.get("batch_count", 0) for result in group_results),
        "batch_errors": batch_errors,
        "agent_calls": agent_calls,
        "failed_models": failed_models,
        "prefilter_rejected_count": len(pre_rejected),
        "possible_alert_count": len(possible_alerts),
        "general_count": len(general_content),
        "candidate_count": len(accepted),
        "rejected_count": len(rejected),
        "candidates": accepted,
        "rejected": rejected,
        "usage": usage,
    }


async def search_food_content(
    food: str,
    *,
    aliases: Optional[Iterable[str]] = None,
    api_key: Optional[str] = None,
    client: Optional[Any] = None,
    use_agent: bool = False,
    agent_client: Optional[Any] = None,
    agent_batch_size: int = AGENT_BATCH_SIZE,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Executa busca multi-query e triagem em dry-run, opcionalmente via Agent."""
    key = (api_key or os.getenv("PERPLEXITY_API_KEY") or "").strip()
    if not key.startswith("pplx-"):
        raise PerplexityConfigurationError("PERPLEXITY_API_KEY ausente ou invalida")

    payload = {
        "query": build_queries(food, aliases),
        "max_results": 10,
        "search_recency_filter": "year",
        "search_context_size": "low",
        "search_language_filter": ["en", "pt"],
        "search_domain_filter": list(TRUSTED_DOMAINS),
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    async def _request(http_client: Any) -> Dict[str, Any]:
        try:
            response = await http_client.post(
                PERPLEXITY_SEARCH_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise PerplexitySearchError(f"falha na Search API: {type(exc).__name__}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            raise PerplexitySearchError("resposta sem results[]")
        return data

    if client is None:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as owned_client:
            response_data = await _request(owned_client)
    else:
        response_data = await _request(client)

    unique_results: Dict[str, Dict[str, Any]] = {}
    for raw in response_data.get("results", []):
        if not isinstance(raw, dict):
            continue
        url = normalize_url(raw.get("url"))
        if url and url not in unique_results:
            unique_results[url] = raw

    if use_agent:
        agent_result = await classify_results_hybrid(
            food,
            list(unique_results.values()),
            aliases=aliases,
            api_key=key,
            client=agent_client,
            now=now,
            batch_size=agent_batch_size,
        )
        agent_result.update({
            "food": food,
            "request_id": response_data.get("id"),
            "queries": len(payload["query"]),
            "total": len(unique_results),
        })
        return agent_result

    evaluated = [evaluate_result(raw, food, now=now) for raw in unique_results.values()]
    candidates = [item for item in evaluated if item["accepted"]]
    rejected = [item for item in evaluated if not item["accepted"]]
    return {
        "ok": True,
        "dry_run": True,
        "food": food,
        "request_id": response_data.get("id"),
        "queries": len(payload["query"]),
        "total": len(evaluated),
        "candidate_count": len(candidates),
        "rejected_count": len(rejected),
        "candidates": candidates,
        "rejected": rejected,
    }
