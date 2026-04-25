# -*- coding: utf-8 -*-
"""
Pipeline de Fichas Nutricionais v2 - Busca por NOME DO PRATO
SoulNutri v1.23

Abordagem: Como apps de nutricao (MyFitnessPal, FatSecret) - buscar
pelo nome do prato diretamente nas bases, nao decompor ingredientes.

Fontes:
1. TACO (local) - busca por ingredientes (unica opcao para base brasileira)
2. USDA FNDDS (Survey) - busca pelo nome do prato em ingles (pratos compostos)
3. Open Food Facts - busca por categoria do prato

Metodo: Media das fontes que retornam dados, com exclusao de outliers.
"""

import os
import httpx
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

USDA_API_KEY = os.environ.get("USDA_API_KEY", "DEMO_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
OFF_BASE_URL = "https://world.openfoodfacts.net/api/v2/search"

NUTRIENT_KEYS = [
    "calorias_kcal", "proteinas_g", "carboidratos_g",
    "gorduras_g", "fibras_g", "sodio_mg",
]

# Traducao do NOME DO PRATO para busca no USDA FNDDS
# Usar termos que o USDA reconhece como pratos compostos
DISH_USDA_QUERY = {
    "Tortinha de Figo e Gorgonzola": "cheese pastry puffs",
    "Umami de Tomates": "tomatoes stewed",
    "Uva": "Grapes, raw",
    "Vinagrete de Lula": "squid cooked",
    "Vol Au Vent (Pimentao ou Espinafre)": "spinach cheese pie",
}

# Categoria OFF para busca direta
DISH_OFF_CATEGORY = {
    "Uva": "en:grapes",
}

# Mapeamento USDA nutrientes
USDA_NUTRIENT_MAP = {
    "Protein": "proteinas_g",
    "Carbohydrate, by difference": "carboidratos_g",
    "Total lipid (fat)": "gorduras_g",
    "Fiber, total dietary": "fibras_g",
    "Sodium, Na": "sodio_mg",
}


# ============================================================
# ============================================================
# FONTE 1: TACO (Local - por ingredientes com PROPORÇÕES COMERCIAIS)
# REGRA: NUNCA dividir igualmente — usar calcular_nutricao_prato()
# ============================================================
def query_taco(ingredientes: list) -> Optional[dict]:
    """Busca na TACO por ingredientes com pesos proporcionais comerciais.

    USA calcular_nutricao_prato() da taco_database — NUNCA divisão igual.
    Regra: arroz=50%, frango=30%, alho=2%, etc. (PROPORCOES comerciais reais)
    """
    from data.taco_database import calcular_nutricao_prato

    if not ingredientes:
        return None

    result = calcular_nutricao_prato(ingredientes, porcao_gramas=100)
    if not result:
        return None

    encontrados = result.get("ingredientes_encontrados", [])
    if not encontrados:
        return None

    n = len(ingredientes)
    return {
        "calorias_kcal": round(result.get("calorias", 0), 1),
        "proteinas_g": round(result.get("proteinas", 0), 1),
        "carboidratos_g": round(result.get("carboidratos", 0), 1),
        "gorduras_g": round(result.get("gorduras", 0), 1),
        "fibras_g": round(result.get("fibras", 0), 1),
        "sodio_mg": round(result.get("sodio", 0), 1),
        "cobertura": round((len(encontrados) / n) * 100),
    }


# ============================================================
# FONTE 2: USDA FNDDS (Busca por nome do prato)
# ============================================================
async def query_usda(nome: str) -> Optional[dict]:
    """Busca no USDA pelo nome do PRATO (nao por ingredientes)."""
    query = DISH_USDA_QUERY.get(nome)
    if not query:
        # Tentar nome direto
        query = nome

    try:
        async with httpx.AsyncClient() as client:
            # Buscar em Survey (FNDDS) primeiro - tem pratos compostos
            resp = await client.get(
                f"{USDA_BASE_URL}/foods/search",
                params={
                    "api_key": USDA_API_KEY,
                    "query": query,
                    "pageSize": 3,
                    "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"],
                },
                timeout=15,
            )
            if resp.status_code == 429:
                logger.warning(f"[USDA] Rate limited para '{query}'")
                return None
            if resp.status_code != 200:
                return None

            foods = resp.json().get("foods", [])
            if not foods:
                return None

            # Pegar o melhor resultado com Energy em KCAL
            for food in foods:
                nutrients = {}
                for fn in food.get("foodNutrients", []):
                    name = fn.get("nutrientName", "")
                    unit = fn.get("unitName", "").upper()
                    value = fn.get("value", 0)
                    if name == "Energy" and unit == "KCAL":
                        nutrients["calorias_kcal"] = value
                    elif name in USDA_NUTRIENT_MAP:
                        nutrients[USDA_NUTRIENT_MAP[name]] = value

                cal = nutrients.get("calorias_kcal", 0)
                if cal > 0 and cal < 900:
                    desc = food.get("description", "?")
                    logger.info(f"[USDA] '{query}' -> '{desc}': {cal} kcal")
                    return {k: round(nutrients.get(k, 0), 1) for k in NUTRIENT_KEYS}

            return None

    except Exception as e:
        logger.warning(f"[USDA] Erro: {e}")
        return None


# ============================================================
# FONTE 3: Open Food Facts (Busca por categoria - so itens simples)
# ============================================================
async def query_off(nome: str) -> Optional[dict]:
    """Busca no OFF por categoria - apenas para itens simples."""
    cat = DISH_OFF_CATEGORY.get(nome)
    if not cat:
        return None

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                OFF_BASE_URL,
                params={
                    "categories_tags_en": cat,
                    "page_size": 3,
                    "fields": "product_name,nutriments",
                },
                headers={"User-Agent": "SoulNutri/1.0"},
                timeout=15,
            )
            if resp.status_code != 200:
                return None

            products = resp.json().get("products", [])
            for p in products:
                n = p.get("nutriments", {})
                energy = n.get("energy-kcal_100g")
                if energy and float(energy) > 0:
                    return {
                        "calorias_kcal": round(float(energy), 1),
                        "proteinas_g": round(float(n.get("proteins_100g", 0) or 0), 1),
                        "carboidratos_g": round(float(n.get("carbohydrates_100g", 0) or 0), 1),
                        "gorduras_g": round(float(n.get("fat_100g", 0) or 0), 1),
                        "fibras_g": round(float(n.get("fiber_100g", 0) or 0), 1),
                        "sodio_mg": round(float(n.get("sodium_100g", 0) or 0) * 1000, 1),
                    }
            return None

    except Exception as e:
        logger.warning(f"[OFF] Erro: {e}")
        return None


# ============================================================
# PIPELINE: Media das fontes disponiveis
# ============================================================
async def generate_nutrition_3sources(nome: str, ingredientes: list) -> dict:
    """
    Gera ficha nutricional buscando pelo NOME DO PRATO.
    TACO usa ingredientes (unica opcao para base BR).
    USDA busca prato composto no FNDDS.
    OFF busca por categoria (so itens simples).
    """
    logger.info(f"[NUTRI] Processando: {nome}")

    taco_data = query_taco(ingredientes)
    usda_data = await query_usda(nome)
    off_data = await query_off(nome)

    sources = {}
    if taco_data:
        sources["TACO"] = taco_data
    if usda_data:
        sources["USDA"] = usda_data
    if off_data:
        sources["OpenFoodFacts"] = off_data

    num_fontes = len(sources)
    if num_fontes == 0:
        return None

    # Calcular media (com exclusao de outlier se 3 fontes)
    media = {}
    for k in NUTRIENT_KEYS:
        values = [src[k] for src in sources.values() if src.get(k, 0) > 0]
        if not values:
            media[k] = 0.0
        elif len(values) <= 2:
            media[k] = round(sum(values) / len(values), 1)
        else:
            sorted_vals = sorted(values)
            median_val = sorted_vals[1]
            filtered = [v for v in values if v <= median_val * 2.5]
            media[k] = round(sum(filtered) / len(filtered), 1) if filtered else round(sum(values) / len(values), 1)

    return {
        "nome": nome,
        "ingredientes": ingredientes,
        **media,
        "num_fontes": num_fontes,
        "fontes_usadas": list(sources.keys()),
        "fonte_principal": f"Media de {num_fontes} fontes ({', '.join(sources.keys())})",
        "detalhes_fontes": sources,
    }
