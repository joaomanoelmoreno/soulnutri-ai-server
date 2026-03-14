# -*- coding: utf-8 -*-
"""
SERVICO DE GERACAO DE FICHAS NUTRICIONAIS v2
SoulNutri - Estrategia CORRIGIDA:
- Gemini AI como fonte principal para TODOS os pratos compostos
- TACO como fonte principal APENAS para itens simples (1-2 ingredientes)
- TACO como referencia de validacao para pratos compostos

PROBLEMA v1: A divisao igual de peso entre ingredientes (100g/N) gerava
valores absurdos - ex: Espetinho de File Mignon com 20 kcal.
"""

import os
import json
import logging
import asyncio
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


def generate_taco_nutrition(ingredientes: list, porcao_g: int = 100) -> dict:
    """
    Gera ficha nutricional usando APENAS a Tabela TACO.
    Retorna valores por 100g do prato pronto.
    NOTA: Usa divisao igual de peso - so e preciso para itens simples.
    """
    from data.taco_database import buscar_dados_taco

    if not ingredientes:
        return None

    n = len(ingredientes)
    gramas_cada = porcao_g / n

    totais = {
        "calorias_kcal": 0, "proteinas_g": 0, "carboidratos_g": 0,
        "gorduras_g": 0, "fibras_g": 0, "sodio_mg": 0,
        "calcio_mg": 0, "ferro_mg": 0, "potassio_mg": 0, "zinco_mg": 0,
    }
    encontrados = []
    nao_encontrados = []

    for ing in ingredientes:
        dados = buscar_dados_taco(ing)
        if dados:
            fator = gramas_cada / 100
            totais["calorias_kcal"] += dados.get("calorias", 0) * fator
            totais["proteinas_g"] += dados.get("proteinas", 0) * fator
            totais["carboidratos_g"] += dados.get("carboidratos", 0) * fator
            totais["gorduras_g"] += dados.get("gorduras", 0) * fator
            totais["fibras_g"] += dados.get("fibras", 0) * fator
            totais["sodio_mg"] += dados.get("sodio", 0) * fator
            totais["calcio_mg"] += dados.get("calcio", 0) * fator
            totais["ferro_mg"] += dados.get("ferro", 0) * fator
            totais["potassio_mg"] += dados.get("potassio", 0) * fator
            totais["zinco_mg"] += dados.get("zinco", 0) * fator
            encontrados.append(ing)
        else:
            nao_encontrados.append(ing)

    for k in totais:
        totais[k] = round(totais[k], 1)

    cobertura = len(encontrados) / n if n > 0 else 0

    return {
        **totais,
        "fonte": "TACO",
        "cobertura_taco": round(cobertura * 100, 0),
        "ingredientes_encontrados": encontrados,
        "ingredientes_nao_encontrados": nao_encontrados,
    }


async def generate_gemini_nutrition(nome: str, ingredientes: list) -> dict:
    """
    Gera ficha nutricional usando Gemini AI.
    Retorna valores por 100g do prato pronto.
    """
    if not EMERGENT_LLM_KEY:
        logger.warning("[NUTRI-GEMINI] EMERGENT_LLM_KEY nao configurada")
        return None

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        ingredientes_texto = ", ".join(ingredientes) if ingredientes else "nao especificados"

        prompt = (
            f"Prato: {nome}\n"
            f"Ingredientes: {ingredientes_texto}\n\n"
            "Forneca os valores nutricionais POR 100g do prato PRONTO/SERVIDO.\n"
            "Considere as proporcoes tipicas de cada ingrediente no prato "
            "(ex: em um espetinho de carne, a carne representa ~70% do peso).\n"
            "Considere o metodo de preparo tipico (frito, grelhado, assado, cru).\n"
            "Responda APENAS em JSON valido, sem markdown, sem crases.\n"
            "Use este formato exato:\n"
            '{"calorias_kcal":0,"proteinas_g":0.0,"carboidratos_g":0.0,'
            '"gorduras_g":0.0,"fibras_g":0.0,"sodio_mg":0,'
            '"calcio_mg":0,"ferro_mg":0.0,"potassio_mg":0,"zinco_mg":0.0}'
        )

        llm = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"nutri-v2-{nome[:20]}",
            system_message=(
                "Voce e um nutricionista profissional brasileiro. "
                "Use como referencia a Tabela TACO e USDA para estimar valores precisos. "
                "Responda APENAS o JSON solicitado, sem nenhum texto adicional."
            ),
        )
        llm = llm.with_model("gemini", "gemini-2.0-flash-lite")
        response = await llm.send_message(UserMessage(text=prompt))

        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]
        if text.startswith("json"):
            text = text[4:]

        data = json.loads(text.strip())

        result = {}
        for k in ["calorias_kcal", "proteinas_g", "carboidratos_g", "gorduras_g",
                   "fibras_g", "sodio_mg", "calcio_mg", "ferro_mg", "potassio_mg", "zinco_mg"]:
            result[k] = round(float(data.get(k, 0)), 1)

        result["fonte"] = "Gemini AI"
        return result

    except Exception as e:
        logger.error(f"[NUTRI-GEMINI] Erro para {nome}: {e}")
        return None


async def generate_nutrition_sheet(nome: str, ingredientes: list) -> dict:
    """
    Gera ficha nutricional combinada.

    Estrategia v2 (CORRIGIDA):
    - Pratos simples (1-2 ingredientes) com boa cobertura TACO: usa TACO
    - Pratos compostos (3+ ingredientes): SEMPRE usa Gemini como principal
    - TACO como referencia de validacao (nao como fonte principal p/ compostos)
    """
    is_simple = len(ingredientes) <= 2

    taco_data = generate_taco_nutrition(ingredientes)
    gemini_data = await generate_gemini_nutrition(nome, ingredientes)

    if not taco_data and not gemini_data:
        return None

    cobertura = taco_data.get("cobertura_taco", 0) if taco_data else 0

    # Item simples com boa cobertura TACO -> usa TACO
    if is_simple and cobertura >= 80 and taco_data:
        result = {k: v for k, v in taco_data.items()
                  if k not in ("ingredientes_encontrados", "ingredientes_nao_encontrados", "cobertura_taco")}
        result["fonte_principal"] = "TACO"
        result["cobertura_taco"] = cobertura
        if gemini_data:
            result["validacao_gemini"] = {
                k: v for k, v in gemini_data.items() if k != "fonte"
            }
    elif gemini_data:
        # Prato composto ou TACO insuficiente -> Gemini como principal
        result = {k: v for k, v in gemini_data.items() if k != "fonte"}
        result["fonte_principal"] = "Gemini AI"
        result["cobertura_taco"] = cobertura
        if taco_data:
            result["referencia_taco"] = {
                k: v for k, v in taco_data.items()
                if k not in ("ingredientes_encontrados", "ingredientes_nao_encontrados", "cobertura_taco", "fonte")
            }
    else:
        # Fallback: TACO parcial (melhor que nada)
        result = {k: v for k, v in taco_data.items()
                  if k not in ("ingredientes_encontrados", "ingredientes_nao_encontrados", "cobertura_taco")}
        result["fonte_principal"] = "TACO (parcial)"
        result["cobertura_taco"] = cobertura

    result["nome"] = nome
    result["ingredientes"] = ingredientes
    result["gerado_em"] = datetime.now(timezone.utc).isoformat()

    return result
