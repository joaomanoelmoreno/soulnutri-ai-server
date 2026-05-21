# -*- coding: utf-8 -*-
"""
P1 — Politica de TTL por confianca no cache de identificacao por imagem.

Cobre os casos:
- confidence == 'alta'   -> cacheia por 3600s
- confidence == 'media'  -> cacheia por 300s
- confidence == 'média'  -> cacheia por 300s (acento)
- confidence == 'baixa'  -> NAO cacheia + log [CACHE] ignorado
- identified == False    -> NAO cacheia
- confidence ausente     -> respeita ttl_seconds passado (back-compat)

Executar:
    python3 -m pytest backend/tests/test_cache_service_ttl.py -v
ou direto:
    python3 backend/tests/test_cache_service_ttl.py
"""

import sys
import time
import logging
from pathlib import Path

# Permitir rodar isolado (sem pytest)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.cache_service import (  # noqa: E402
    cache_result,
    get_cached_result,
    clear_cache,
    _dish_cache,
)


def _make_result(confidence, identified=True, dish="Ceviche"):
    return {
        "ok": True,
        "identified": identified,
        "dish": dish.lower(),
        "dish_display": dish,
        "confidence": confidence,
        "source": "local_index",
    }


def _ttl_of(image_bytes, restaurant=''):
    """Retorna TTL real (segundos) gravado no _dish_cache para a chave."""
    from services.cache_service import get_image_hash
    key = get_image_hash(image_bytes, restaurant)
    entry = _dish_cache.cache.get(key)
    if not entry:
        return None
    return int(round(entry['_expires_at'] - entry['_cached_at']))


def test_alta_cacheia_3600s(caplog):
    clear_cache()
    img = b"alta-bytes"
    with caplog.at_level(logging.INFO, logger="services.cache_service"):
        cache_result(img, _make_result("alta"), restaurant="cibi_sana", ttl_seconds=3600)
    assert _ttl_of(img, "cibi_sana") == 3600
    assert any("conf=alta" in r.message and "TTL=3600s" in r.message for r in caplog.records)


def test_media_sem_acento_cacheia_300s(caplog):
    clear_cache()
    img = b"media-bytes"
    with caplog.at_level(logging.INFO, logger="services.cache_service"):
        cache_result(img, _make_result("media"), restaurant="cibi_sana", ttl_seconds=3600)
    assert _ttl_of(img, "cibi_sana") == 300
    assert any("conf=media" in r.message and "TTL=300s" in r.message for r in caplog.records)


def test_media_com_acento_cacheia_300s(caplog):
    clear_cache()
    img = b"media-acento-bytes"
    with caplog.at_level(logging.INFO, logger="services.cache_service"):
        cache_result(img, _make_result("média"), restaurant="cibi_sana", ttl_seconds=3600)
    assert _ttl_of(img, "cibi_sana") == 300


def test_baixa_nao_cacheia(caplog):
    clear_cache()
    img = b"baixa-bytes"
    with caplog.at_level(logging.INFO, logger="services.cache_service"):
        cache_result(img, _make_result("baixa"), restaurant="cibi_sana", ttl_seconds=3600)
    assert _ttl_of(img, "cibi_sana") is None  # NADA gravado
    assert get_cached_result(img, "cibi_sana") is None
    assert any("[CACHE] ignorado: conf=baixa" in r.message for r in caplog.records)


def test_identified_false_nao_cacheia():
    clear_cache()
    img = b"unid-bytes"
    cache_result(img, _make_result("alta", identified=False), restaurant="cibi_sana", ttl_seconds=3600)
    assert _ttl_of(img, "cibi_sana") is None


def test_confidence_ausente_respeita_ttl_passado():
    """Back-compat: sem confidence no result, segue o ttl_seconds do chamador."""
    clear_cache()
    img = b"sem-conf-bytes"
    res = _make_result("alta")
    res.pop("confidence")
    cache_result(img, res, restaurant="external", ttl_seconds=120)
    assert _ttl_of(img, "external") == 120


def test_alta_respeita_teto_menor_passado():
    """Se chamador passar TTL menor para 'alta', usa o menor (back-compat)."""
    clear_cache()
    img = b"alta-cap-bytes"
    cache_result(img, _make_result("alta"), restaurant="cibi_sana", ttl_seconds=600)
    assert _ttl_of(img, "cibi_sana") == 600


# ───────────────────────────────────────────────────────────────────
# Permite rodar sem pytest: `python3 backend/tests/test_cache_service_ttl.py`
# (Standalone: checa apenas estado do cache; logs sao validados via pytest.)
# ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    def _t_alta():
        clear_cache(); img = b"alta"
        cache_result(img, _make_result("alta"), "cibi_sana", 3600)
        assert _ttl_of(img, "cibi_sana") == 3600

    def _t_media():
        clear_cache(); img = b"media"
        cache_result(img, _make_result("media"), "cibi_sana", 3600)
        assert _ttl_of(img, "cibi_sana") == 300

    def _t_media_acento():
        clear_cache(); img = b"med-ac"
        cache_result(img, _make_result("média"), "cibi_sana", 3600)
        assert _ttl_of(img, "cibi_sana") == 300

    def _t_baixa():
        clear_cache(); img = b"baixa"
        cache_result(img, _make_result("baixa"), "cibi_sana", 3600)
        assert _ttl_of(img, "cibi_sana") is None
        assert get_cached_result(img, "cibi_sana") is None

    cases = [
        ("alta cacheia 3600s", _t_alta),
        ("media cacheia 300s", _t_media),
        ("média (acento) cacheia 300s", _t_media_acento),
        ("baixa NAO cacheia", _t_baixa),
        ("identified=False NAO cacheia", test_identified_false_nao_cacheia),
        ("confidence ausente respeita ttl", test_confidence_ausente_respeita_ttl_passado),
        ("alta respeita teto menor", test_alta_respeita_teto_menor_passado),
    ]
    failed = 0
    for name, fn in cases:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{'='*40}\n{len(cases) - failed}/{len(cases)} testes passaram")
    sys.exit(0 if failed == 0 else 1)
