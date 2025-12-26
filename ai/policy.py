# ai/policy.py
"""
SoulNutri AI — Policy (Servidor B)

Define a política de decisão a partir do score de similaridade (cosine).
Você já havia definido faixas:
- alta:   >= 0.85
- média:  >= 0.50 e < 0.85
- baixa:  < 0.50

Obs: Esses thresholds são ajustáveis conforme testes reais.
"""

from typing import Literal

Level = Literal["alta", "media", "média", "baixa"]


def confidence_level(score: float) -> str:
    """
    Converte score (0..1) em nível: alta / média / baixa.

    Mantém "média" com acento no retorno para ficar consistente com seu app.
    """
    try:
        s = float(score)
    except Exception:
        return "baixa"

    if s >= 0.85:
        return "alta"
    if s >= 0.50:
        return "média"
    return "baixa"
