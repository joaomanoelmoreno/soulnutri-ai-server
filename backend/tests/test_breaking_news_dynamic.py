# -*- coding: utf-8 -*-
"""
Testes unitarios do provider dynamic_health_news.

SEM rede. SEM Mongo real. SEM HTTP real.
Todos os testes usam monkeypatch para isolar dependencias.
"""

import asyncio
from datetime import datetime, timezone, timedelta

import pytest

from services.breaking_news_service.providers import dynamic_health_news as dyn
from services.breaking_news_service import api as bn_api


# ─── HELPERS ────────────────────────────────────────────────────────────────

def _rfc822(dt):
    """Datetime → string RFC822 estilo Google News."""
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _xml(items):
    """Constroi XML RSS minimo para testes."""
    parts = ['<?xml version="1.0"?><rss><channel>']
    for it in items:
        parts.append("<item>")
        parts.append(f"<title>{it.get('titulo','')}</title>")
        parts.append(f"<link>{it.get('url','')}</link>")
        parts.append(f"<source>{it.get('fonte','')}</source>")
        parts.append(f"<pubDate>{it.get('pubdate','')}</pubDate>")
        parts.append(f"<description>{it.get('summary','')}</description>")
        parts.append("</item>")
    parts.append("</channel></rss>")
    return "".join(parts).encode("utf-8")


class _FakeCache:
    """Substitui cache Mongo em memoria para isolar testes."""
    def __init__(self):
        self.store = {}
    def get(self, key):
        return self.store.get(key)
    def set(self, key, best, ttl):
        self.store[key] = {"best": best, "ttl": ttl}


@pytest.fixture(autouse=True)
def _patch_cache_and_indexes(monkeypatch):
    """Isola provider de Mongo real."""
    fake = _FakeCache()
    monkeypatch.setattr(dyn, "_cache_get", lambda k: fake.get(k))
    monkeypatch.setattr(dyn, "_cache_set", lambda k, b, t: fake.set(k, b, t))
    monkeypatch.setattr(dyn, "_ensure_cache_indexes", lambda: None)
    return fake


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ─── 1. QUERY BUILDER ───────────────────────────────────────────────────────

def test_build_query_pt_camarao_inclui_acento():
    q = dyn._build_query_pt("camarao")
    assert '"camarão"' in q
    assert "when:30d" in q
    assert "saúde" in q


def test_build_query_pt_sem_categoria_ampla():
    q = dyn._build_query_pt("camarao")
    assert "frutos do mar" not in q.lower()


# ─── 2. FILTROS ─────────────────────────────────────────────────────────────

def _item(titulo, url, summary="", days_ago=1):
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {
        "titulo": titulo,
        "url": url,
        "summary": summary,
        "pubdate": _rfc822(dt),
        "fonte": "",
    }


def test_passes_rejects_no_dish_in_text():
    it = _item("Estudo sobre saúde geral", "https://reuters.com/x")
    assert dyn._passes_filters(it, "camarao") is False


def test_passes_rejects_non_whitelist_source():
    it = _item("Estudo sobre camarão e saúde", "https://blog-aleatorio.com/x")
    assert dyn._passes_filters(it, "camarao") is False


def test_passes_rejects_recipe():
    it = _item("Receita de camarão grelhado saudável", "https://reuters.com/x")
    assert dyn._passes_filters(it, "camarao") is False


def test_passes_rejects_promo():
    it = _item("Promoção: camarão com 50% de desconto para sua saúde", "https://reuters.com/x")
    assert dyn._passes_filters(it, "camarao") is False


def test_passes_rejects_imperative():
    it = _item("Não consuma camarão crú — alerta de saúde", "https://reuters.com/x")
    assert dyn._passes_filters(it, "camarao") is False


def test_passes_rejects_old_news():
    it = _item("Estudo associa camarão a alerta de saúde", "https://reuters.com/x", days_ago=60)
    assert dyn._passes_filters(it, "camarao") is False


def test_passes_accepts_anvisa_alerta():
    it = _item("Anvisa alerta sobre camarão importado — risco de alergia", "https://www.anvisa.gov.br/noticias/x")
    assert dyn._passes_filters(it, "camarao") is True


def test_passes_requires_health_keyword():
    it = _item("Camarão vendido por mais de R$80 no mercado", "https://reuters.com/x")
    assert dyn._passes_filters(it, "camarao") is False


# ─── 3. SCORE ───────────────────────────────────────────────────────────────

def test_score_zero_when_dish_absent():
    # Fonte nao-prime; dish ausente em titulo e summary → score esperado 0
    it = _item("Reportagem sobre alimentos em geral", "https://www.fiocruz.br/x")
    assert dyn._score_item(it, "camarao") == 0


def test_score_prime_source_bonus():
    it = _item("Camarão e saúde: estudo recente", "https://www.reuters.com/x", days_ago=1)
    # titulo (3) + prime (1) + recente <=7d (1) = 5
    assert dyn._score_item(it, "camarao") >= 4


# ─── 4. POLARIDADE ──────────────────────────────────────────────────────────

def test_polarity_alerta():
    p = dyn._classify_polarity("Anvisa alerta sobre risco de contaminação em camarão", "")
    assert p == "alerta"


def test_polarity_beneficio():
    p = dyn._classify_polarity("Estudo associa salmão a benefício cardiovascular e reduz risco", "")
    # Tem 'beneficio' e 'risco' → empate → neutro (regra: exclusivo)
    assert p in {"neutro", "beneficio"}


def test_polarity_neutro():
    p = dyn._classify_polarity("Cientistas pesquisam camarão em estudo recente", "")
    assert p == "neutro"


# ─── 5. FETCH (com mock httpx) ──────────────────────────────────────────────

class _FakeResponse:
    def __init__(self, status, content):
        self.status_code = status
        self.content = content


class _FakeClient:
    def __init__(self, content=None, raise_exc=None):
        self._content = content
        self._raise = raise_exc
    async def __aenter__(self):
        return self
    async def __aexit__(self, *a):
        return False
    async def get(self, url, headers=None):
        if self._raise:
            raise self._raise
        return _FakeResponse(200, self._content)


def test_fetch_silence_when_rss_empty(monkeypatch):
    monkeypatch.setattr(dyn.httpx, "AsyncClient", lambda timeout: _FakeClient(content=_xml([])))
    out = _run(dyn.fetch("camarao", None, [], None))
    assert out is None


def test_fetch_silence_when_timeout(monkeypatch):
    import httpx
    monkeypatch.setattr(
        dyn.httpx,
        "AsyncClient",
        lambda timeout: _FakeClient(raise_exc=httpx.TimeoutException("boom")),
    )
    out = _run(dyn.fetch("camarao", None, [], None))
    assert out is None


def test_fetch_returns_silence_when_no_dish_slug():
    out = _run(dyn.fetch("", None, [], None))
    assert out is None


def test_fetch_returns_item_when_valid(monkeypatch):
    items = [
        _item(
            "Anvisa alerta sobre camarão — risco de alergia em pesquisa recente",
            "https://www.anvisa.gov.br/noticias/2026/x",
            summary="Alerta sanitário",
            days_ago=2,
        ),
    ]
    monkeypatch.setattr(dyn.httpx, "AsyncClient", lambda timeout: _FakeClient(content=_xml(items)))
    out = _run(dyn.fetch("camarao", None, [], None))
    assert out is not None
    assert "camarão" in out["titulo"].lower()
    assert out["polaridade"] == "alerta"
    assert out["url"].startswith("https://www.anvisa.gov.br")


def test_fetch_silence_when_score_below_min(monkeypatch):
    # Item passa filtro mas score baixo: dish so no summary + fonte nao-prime
    items = [
        _item(
            "Notícia sobre alimentação saudável e estudo recente",
            "https://www.fiocruz.br/noticia/x",
            summary="camarão é citado brevemente neste estudo",
            days_ago=15,
        ),
    ]
    monkeypatch.setattr(dyn.httpx, "AsyncClient", lambda timeout: _FakeClient(content=_xml(items)))
    out = _run(dyn.fetch("camarao", None, [], None))
    # Item esta no summary (score=2) + fiocruz nao-prime (0) + age 15d (0) = 2 < 3
    assert out is None


# ─── 6. DORMENCIA ───────────────────────────────────────────────────────────

def test_providers_order_remains_curated_only():
    """Garantia estrutural: provider dinamico NAO e ativado em runtime."""
    assert bn_api.PROVIDERS_ORDER == ["curated"]


def test_dynamic_registered_but_dormant():
    """Provider esta no registry mas nao em PROVIDERS_ORDER."""
    from services.breaking_news_service.providers import PROVIDERS
    assert "dynamic_health_news" in PROVIDERS
    assert "dynamic_health_news" not in bn_api.PROVIDERS_ORDER
