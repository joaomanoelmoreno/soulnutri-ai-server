# -*- coding: utf-8 -*-
"""
Fase 2A — Hard Gate Backend: testes do helper verificar_premium_ativo.

Cobre AMBOS os schemas:
  A) {plano, premium_ate} (legacy profile_service)
  B) {premium_ativo, premium_expira_em, is_trial} (produção atual server.py)

Executar:
    python3 -m pytest backend/tests/test_premium_gate.py -v
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.profile_service import verificar_premium_ativo  # noqa: E402


def _iso(dt):
    return dt.isoformat()


def test_user_none():
    r = verificar_premium_ativo(None)
    assert r["ativo"] is False


def test_user_vazio():
    r = verificar_premium_ativo({})
    assert r["ativo"] is False


# ── Schema B (producao) ───────────────────────────────────────────────
def test_schemaB_trial_valido():
    user = {
        "nome": "Alice", "premium_ativo": True, "is_trial": True,
        "premium_expira_em": _iso(datetime.now(timezone.utc) + timedelta(days=5)),
    }
    r = verificar_premium_ativo(user)
    assert r["ativo"] is True
    assert r["plano"] == "premium_trial"
    assert r["dias_restantes"] >= 4


def test_schemaB_trial_expirado():
    user = {
        "nome": "Bob", "premium_ativo": True, "is_trial": True,
        "premium_expira_em": _iso(datetime.now(timezone.utc) - timedelta(days=1)),
    }
    r = verificar_premium_ativo(user)
    assert r["ativo"] is False
    assert "Expirado" in r["motivo"] or "expirado" in r["motivo"]


def test_schemaB_premium_vitalicio():
    """premium_ativo=True, sem premium_expira_em = vitalicio (admin/dev)."""
    user = {"nome": "Admin", "premium_ativo": True}
    r = verificar_premium_ativo(user)
    assert r["ativo"] is True
    assert r["expira"] is None


def test_schemaB_desativado():
    user = {
        "nome": "Carl", "premium_ativo": False,
        "premium_expira_em": _iso(datetime.now(timezone.utc) + timedelta(days=99)),
    }
    r = verificar_premium_ativo(user)
    assert r["ativo"] is False


def test_schemaB_data_invalida():
    user = {"nome": "X", "premium_ativo": True, "premium_expira_em": "not-a-date"}
    r = verificar_premium_ativo(user)
    assert r["ativo"] is False


# ── Schema A (legacy) ─────────────────────────────────────────────────
def test_schemaA_free():
    user = {"nome": "Free", "plano": "free"}
    r = verificar_premium_ativo(user)
    assert r["ativo"] is False


def test_schemaA_premium_vitalicio():
    user = {"nome": "VIP", "plano": "premium"}
    r = verificar_premium_ativo(user)
    assert r["ativo"] is True
    assert r["expira"] is None


def test_schemaA_premium_valido():
    user = {"nome": "Sub", "plano": "premium",
            "premium_ate": _iso(datetime.now(timezone.utc) + timedelta(days=10))}
    r = verificar_premium_ativo(user)
    assert r["ativo"] is True


def test_schemaA_premium_expirado():
    user = {"nome": "OldSub", "plano": "premium",
            "premium_ate": _iso(datetime.now(timezone.utc) - timedelta(hours=1))}
    r = verificar_premium_ativo(user)
    assert r["ativo"] is False


# ── PREMIUM_ONLY_FIELDS contract ─────────────────────────────────────
def test_premium_only_fields_constant_contract():
    """Garantia: lista de campos Premium-only continua incluindo os criticos."""
    from server import PREMIUM_ONLY_FIELDS, _strip_premium_fields
    must_be_premium = {
        "beneficios", "riscos", "alergenos", "alertas_personalizados",
        "noticias", "contextual_breaking_news", "curiosidade", "combinacoes",
        "voce_sabia", "mito_verdade", "dica_chef",
    }
    missing = must_be_premium - PREMIUM_ONLY_FIELDS
    assert not missing, f"Campos criticos faltando em PREMIUM_ONLY_FIELDS: {missing}"


def test_strip_premium_fields_idempotente():
    from server import _strip_premium_fields
    payload = {
        "dish_display": "Feijoada",
        "nutrition": {"cal": 300},
        "beneficios": ["x"],
        "riscos": ["y"],
        "noticias": [{"titulo": "n"}],
        "contextual_breaking_news": {"titulo": "x"},
        "alergenos": {"gluten": True},
        "curiosidade": "fato",
    }
    _strip_premium_fields(payload)
    # Listas: presentes mas vazias
    assert payload["beneficios"] == []
    assert payload["riscos"] == []
    assert payload["noticias"] == []
    # Dicts: presentes mas vazios
    assert payload["alergenos"] == {}
    # Null: presentes mas None
    assert payload["contextual_breaking_news"] is None
    assert payload["curiosidade"] is None
    # Campos Free intactos
    assert payload["dish_display"] == "Feijoada"
    assert payload["nutrition"] == {"cal": 300}
    # Idempotente
    _strip_premium_fields(payload)
    assert payload["beneficios"] == []
    assert payload["dish_display"] == "Feijoada"
