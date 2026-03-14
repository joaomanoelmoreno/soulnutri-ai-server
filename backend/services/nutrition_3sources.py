# -*- coding: utf-8 -*-
"""
Pipeline de Fichas Nutricionais - 3 Fontes Globais
SoulNutri v1.23

Fontes:
1. TACO (Tabela Brasileira de Composicao de Alimentos) - Local, 597 alimentos
2. USDA FoodData Central - Governo EUA, 300K+ alimentos, API gratuita
3. Open Food Facts - Global, 4M+ produtos, open source

Metodo: Media simples dos valores retornados pelas fontes disponíveis.
Transparencia: Cada fonte salva individualmente + media final.
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

MAX_RETRIES = 2
RETRY_DELAY = 5  # segundos entre retries

# Mapeamento PT -> EN para busca no USDA
INGREDIENT_PT_TO_EN = {
    "uva": "Grapes, Thompson seedless, raw",
    "figo": "Figs, raw",
    "queijo gorgonzola": "Cheese, blue",
    "massa folhada": "pastry puff frozen baked",
    "cebolinha": "Chives, raw",
    "frutas vermelhas": "Strawberries, raw",
    "tomate": "Tomatoes, red, raw",
    "tomate cereja": "Tomatoes, grape, raw",
    "tomates cereja": "Tomatoes, grape, raw",
    "tomate sem pele": "Tomatoes, red, raw",
    "azeite de oliva": "Oil, olive, extra virgin",
    "azeite extravirgem": "Oil, olive, extra virgin",
    "azeite": "Oil, olive, extra virgin",
    "vinagre": "Vinegar, distilled",
    "vinagre ": "Vinegar, distilled",
    "alho": "Garlic, raw",
    "alho ": "Garlic, raw",
    "ervas": "Spices, parsley, dried",
    "cebola": "Onions, raw",
    "lula": "Mollusks, squid, mixed species, raw",
    "lulas": "Mollusks, squid, mixed species, raw",
    "pimentao": "Peppers, sweet, red, raw",
    "espinafre": "Spinach, cooked",
    "ricota": "Cheese, ricotta, whole milk",
    "cheiro-verde": "Parsley, fresh",
    "temperos": "Spices, parsley, dried",
    "cebolinha picada": "Chives, raw",
}

DISH_NAME_PT_TO_EN = {
    "Uva": "grape raw",
    "Umami de Tomates": "tomato confit olive oil",
    "Tortinha de Figo e Gorgonzola": "fig gorgonzola tart pastry",
    "Vinagrete de Lula": "squid vinaigrette tomato onion",
    "Vol Au Vent (Pimentao ou Espinafre)": "vol au vent pastry spinach",
}

# Mapeamento PT -> OFF category tag para busca precisa
INGREDIENT_PT_TO_OFF_CAT = {
    "uva": "en:grapes",
    "figo": "en:figs",
    "queijo gorgonzola": "en:gorgonzola",
    "massa folhada": "en:puff-pastries",
    "cebolinha": "en:chives",
    "cebolinha picada": "en:chives",
    "frutas vermelhas": "en:berries",
    "tomate": "en:tomatoes",
    "tomate cereja": "en:cherry-tomatoes",
    "tomates cereja": "en:cherry-tomatoes",
    "tomate sem pele": "en:peeled-tomatoes",
    "azeite de oliva": "en:olive-oils",
    "azeite extravirgem": "en:olive-oils",
    "azeite": "en:olive-oils",
    "vinagre": "en:vinegars",
    "alho": "en:garlics",
    "ervas": "en:herbs",
    "cebola": "en:onions",
    "lula": "en:squids",
    "lulas": "en:squids",
    "pimentao": "en:bell-peppers",
    "espinafre": "en:spinachs",
    "ricota": "en:ricotta",
    "cheiro-verde": "en:parsley",
    "temperos": "en:seasonings",
}

DISH_NAME_TO_OFF_CAT = {
    "Uva": "en:grapes",
}

NUTRIENT_KEYS = [
    "calorias_kcal", "proteinas_g", "carboidratos_g",
    "gorduras_g", "fibras_g", "sodio_mg",
    "calcio_mg", "ferro_mg", "potassio_mg", "zinco_mg",
]

# ============================================================
# PESOS PROPORCIONAIS POR TIPO DE INGREDIENTE
# Em uma porcao de 100g, cada ingrediente recebe um peso proporcional
# ao seu papel real no prato (nao divisao igual).
# ============================================================
INGREDIENT_TYPE = {
    # GORDURAS/OLEOS: 3-5g em 100g de prato
    "azeite de oliva": "gordura",
    "azeite extravirgem": "gordura",
    "azeite": "gordura",
    # CONDIMENTOS: 2-3g em 100g de prato
    "vinagre": "condimento",
    "alho": "condimento",
    "alho ": "condimento",
    "ervas": "condimento",
    "temperos": "condimento",
    "cheiro-verde": "condimento",
    "cebolinha": "condimento",
    "cebolinha picada": "condimento",
    # PROTEINAS: 20-30g em 100g de prato
    "queijo gorgonzola": "proteina",
    "lula": "proteina",
    "lulas": "proteina",
    "ricota": "proteina",
    # VEGETAIS: proporcao principal
    "tomate": "vegetal",
    "tomate cereja": "vegetal",
    "tomates cereja": "vegetal",
    "tomate sem pele": "vegetal",
    "cebola": "vegetal",
    "pimentao": "vegetal",
    "espinafre": "vegetal",
    # BASES/MASSAS: proporcao significativa
    "massa folhada": "base",
    # FRUTAS
    "figo": "fruta",
    "frutas vermelhas": "fruta",
    "uva": "fruta",
}

# Peso relativo por tipo (sera normalizado para somar 100g)
TYPE_WEIGHT = {
    "gordura": 5,       # ~5g de oleo por 100g de prato
    "condimento": 3,    # ~3g de tempero
    "proteina": 25,     # ~25g de proteina
    "vegetal": 30,      # ~30g de vegetal
    "base": 25,         # ~25g de massa/base
    "fruta": 30,        # ~30g de fruta
    "desconhecido": 15, # default
}


def calculate_proportional_weights(ingredientes: list) -> dict:
    """
    Calcula gramas proporcionais para cada ingrediente baseado no tipo.
    Retorna dict {ingrediente: gramas_por_100g}.
    """
    if not ingredientes:
        return {}

    weights = {}
    for ing in ingredientes:
        ing_clean = ing.strip().lower()
        tipo = INGREDIENT_TYPE.get(ing_clean, "desconhecido")
        weights[ing] = TYPE_WEIGHT.get(tipo, 15)

    # Normalizar para somar 100g
    total_weight = sum(weights.values())
    if total_weight > 0:
        factor = 100.0 / total_weight
        weights = {k: round(v * factor, 1) for k, v in weights.items()}

    return weights


# ============================================================
# FONTE 1: TACO (Local)
# ============================================================
def query_taco(ingredientes: list, porcao_g: int = 100) -> Optional[dict]:
    """Busca valores na Tabela TACO local por ingredientes com pesos proporcionais."""
    from data.taco_database import buscar_dados_taco

    if not ingredientes:
        return None

    weights = calculate_proportional_weights(ingredientes)
    totais = {k: 0.0 for k in NUTRIENT_KEYS}
    encontrados = 0

    for ing in ingredientes:
        dados = buscar_dados_taco(ing)
        gramas = weights.get(ing, 100 / len(ingredientes))
        if dados:
            fator = gramas / 100
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
            encontrados += 1

    if encontrados == 0:
        return None

    n = len(ingredientes)
    cobertura = encontrados / n
    result = {k: round(v, 1) for k, v in totais.items()}
    result["cobertura"] = round(cobertura * 100)
    result["ingredientes_encontrados"] = encontrados
    result["ingredientes_total"] = n
    return result


# ============================================================
# FONTE 2: USDA FoodData Central (API)
# ============================================================

# Mapeamento de nutrientes USDA -> nossos campos
USDA_NUTRIENT_MAP = {
    "Energy": "calorias_kcal",
    "Protein": "proteinas_g",
    "Carbohydrate, by difference": "carboidratos_g",
    "Total lipid (fat)": "gorduras_g",
    "Fiber, total dietary": "fibras_g",
    "Sodium, Na": "sodio_mg",
    "Calcium, Ca": "calcio_mg",
    "Iron, Fe": "ferro_mg",
    "Potassium, K": "potassio_mg",
    "Zinc, Zn": "zinco_mg",
}


async def _usda_search_one(client: httpx.AsyncClient, query: str) -> Optional[dict]:
    """Busca um alimento no USDA e retorna nutrientes por 100g. Com retry."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = await client.get(
                f"{USDA_BASE_URL}/foods/search",
                params={
                    "api_key": USDA_API_KEY,
                    "query": query,
                    "pageSize": 1,
                    "dataType": ["Foundation", "SR Legacy"],
                },
                timeout=15,
            )
            if resp.status_code == 429:
                if attempt < MAX_RETRIES:
                    wait = RETRY_DELAY * (attempt + 1)
                    logger.info(f"[USDA] Rate limited, aguardando {wait}s...")
                    await asyncio.sleep(wait)
                    continue
                logger.warning(f"[USDA] Rate limit esgotado para '{query}'")
                return None

            if resp.status_code != 200:
                logger.warning(f"[USDA] HTTP {resp.status_code} para '{query}'")
                return None

            data = resp.json()
            foods = data.get("foods", [])
            if not foods:
                return None

            food = foods[0]
            nutrients = {}
            for fn in food.get("foodNutrients", []):
                name = fn.get("nutrientName", "")
                unit = fn.get("unitName", "").upper()
                value = fn.get("value", 0)
                if name == "Energy":
                    # USDA has Energy in both KCAL and KJ - only use KCAL
                    if unit == "KCAL":
                        nutrients["calorias_kcal"] = value
                elif name in USDA_NUTRIENT_MAP:
                    nutrients[USDA_NUTRIENT_MAP[name]] = value

            if not nutrients:
                return None

            # Sanity check: calorias > 900 kcal/100g is almost certainly wrong
            if nutrients.get("calorias_kcal", 0) > 900:
                logger.warning(f"[USDA] Valor suspeito para '{query}': {nutrients.get('calorias_kcal')} kcal - ignorando")
                return None

            logger.info(f"[USDA] '{query}' -> '{food.get('description', '?')}' ({len(nutrients)} nutrientes)")
            return nutrients

        except Exception as e:
            logger.warning(f"[USDA] Erro buscando '{query}': {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)
                continue
            return None
    return None


async def query_usda(nome: str, ingredientes: list, porcao_g: int = 100) -> Optional[dict]:
    """Busca valores no USDA por ingredientes traduzidos para ingles."""
    is_simple = len(ingredientes) <= 2

    async with httpx.AsyncClient() as client:
        # Para itens simples, buscar diretamente pelo nome do prato
        if is_simple:
            en_name = DISH_NAME_PT_TO_EN.get(nome)
            if en_name:
                result = await _usda_search_one(client, en_name)
                if result:
                    final = {k: round(result.get(k, 0), 1) for k in NUTRIENT_KEYS}
                    final["cobertura"] = 100
                    return final

        # Para compostos, buscar por ingredientes com pesos proporcionais
        weights = calculate_proportional_weights(ingredientes)
        totais = {k: 0.0 for k in NUTRIENT_KEYS}
        encontrados = 0

        for ing in ingredientes:
            ing_clean = ing.strip().lower()
            if not ing_clean:
                continue
            en_query = INGREDIENT_PT_TO_EN.get(ing_clean, ing_clean)
            gramas = weights.get(ing, 100 / len(ingredientes))

            nutrients = await _usda_search_one(client, en_query)
            if nutrients:
                fator = gramas / 100
                for k in NUTRIENT_KEYS:
                    totais[k] += nutrients.get(k, 0) * fator
                encontrados += 1

            await asyncio.sleep(0.5)

        if encontrados == 0:
            return None

        n = len(ingredientes)
        cobertura = encontrados / n
        result = {k: round(v, 1) for k, v in totais.items()}
        result["cobertura"] = round(cobertura * 100)
        result["ingredientes_encontrados"] = encontrados
        result["ingredientes_total"] = n
        return result


# ============================================================
# FONTE 3: Open Food Facts (API)
# ============================================================
async def _off_search_by_category(client: httpx.AsyncClient, category_tag: str) -> Optional[dict]:
    """Busca no Open Food Facts por categoria e retorna nutrientes por 100g."""
    try:
        resp = await client.get(
            OFF_BASE_URL,
            params={
                "categories_tags_en": category_tag,
                "page_size": 3,
                "fields": "product_name,nutriments",
            },
            headers={"User-Agent": "SoulNutri/1.0 (soulnutri.app@proton.me)"},
            timeout=15,
        )
        if resp.status_code != 200:
            logger.warning(f"[OFF] HTTP {resp.status_code} para categoria '{category_tag}'")
            return None

        data = resp.json()
        products = data.get("products", [])
        if not products:
            return None

        for p in products:
            n = p.get("nutriments", {})
            energy = n.get("energy-kcal_100g")
            if energy is not None and float(energy) > 0:
                result = {
                    "calorias_kcal": round(float(energy), 1),
                    "proteinas_g": round(float(n.get("proteins_100g", 0) or 0), 1),
                    "carboidratos_g": round(float(n.get("carbohydrates_100g", 0) or 0), 1),
                    "gorduras_g": round(float(n.get("fat_100g", 0) or 0), 1),
                    "fibras_g": round(float(n.get("fiber_100g", 0) or 0), 1),
                    "sodio_mg": round(float(n.get("sodium_100g", 0) or 0) * 1000, 1),
                }
                pname = p.get("product_name", "?")
                logger.info(f"[OFF] '{category_tag}' -> '{pname}' ({result['calorias_kcal']} kcal)")
                return result

        return None

    except Exception as e:
        logger.warning(f"[OFF] Erro buscando categoria '{category_tag}': {e}")
        return None


async def query_off(nome: str, ingredientes: list, porcao_g: int = 100) -> Optional[dict]:
    """Busca valores no Open Food Facts por categorias de ingredientes."""
    is_simple = len(ingredientes) <= 2

    async with httpx.AsyncClient() as client:
        # Para itens simples, buscar diretamente pela categoria do prato
        if is_simple:
            cat = DISH_NAME_TO_OFF_CAT.get(nome)
            if cat:
                result = await _off_search_by_category(client, cat)
                if result:
                    final = {k: round(float(result.get(k, 0) or 0), 1) for k in NUTRIENT_KEYS}
                    final["cobertura"] = 100
                    return final

        # Para compostos, buscar por ingredientes usando categorias com pesos proporcionais
        weights = calculate_proportional_weights(ingredientes)
        totais = {k: 0.0 for k in NUTRIENT_KEYS}
        encontrados = 0

        for ing in ingredientes:
            ing_clean = ing.strip().lower()
            if not ing_clean:
                continue

            cat_tag = INGREDIENT_PT_TO_OFF_CAT.get(ing_clean)
            if not cat_tag:
                continue

            gramas = weights.get(ing, 100 / len(ingredientes))
            nutrients = await _off_search_by_category(client, cat_tag)
            if nutrients:
                fator = gramas / 100
                for k in NUTRIENT_KEYS:
                    val = float(nutrients.get(k, 0) or 0)
                    totais[k] += val * fator
                encontrados += 1

            await asyncio.sleep(0.3)

        if encontrados == 0:
            return None

        n = len(ingredientes)
        cobertura = encontrados / n
        result = {k: round(v, 1) for k, v in totais.items()}
        result["cobertura"] = round(cobertura * 100)
        result["ingredientes_encontrados"] = encontrados
        result["ingredientes_total"] = n
        return result


# ============================================================
# PIPELINE: Media das 3 Fontes
# ============================================================
async def generate_nutrition_3sources(nome: str, ingredientes: list) -> dict:
    """
    Gera ficha nutricional usando media de 3 fontes globais.

    Retorna dict com:
    - Valores medios por 100g
    - Valores individuais de cada fonte (transparencia)
    - Numero de fontes que retornaram dados
    """
    logger.info(f"[NUTRI-3SRC] Processando: {nome} ({len(ingredientes)} ingredientes)")

    is_simple = len(ingredientes) <= 2

    # Consultar as 3 fontes
    taco_data = query_taco(ingredientes)
    usda_data = await query_usda(nome, ingredientes)
    # OFF so para itens simples - para compostos, retorna produtos processados com valores inflados
    off_data = await query_off(nome, ingredientes) if is_simple else None

    sources = {}
    if taco_data:
        sources["TACO"] = {k: taco_data.get(k, 0) for k in NUTRIENT_KEYS}
        sources["TACO"]["cobertura"] = taco_data.get("cobertura", 0)
    if usda_data:
        sources["USDA"] = {k: usda_data.get(k, 0) for k in NUTRIENT_KEYS}
        sources["USDA"]["cobertura"] = usda_data.get("cobertura", 0)
    if off_data:
        sources["OpenFoodFacts"] = {k: off_data.get(k, 0) for k in NUTRIENT_KEYS}
        sources["OpenFoodFacts"]["cobertura"] = off_data.get("cobertura", 0)

    num_fontes = len(sources)
    logger.info(f"[NUTRI-3SRC] {nome}: {num_fontes}/3 fontes retornaram dados: {list(sources.keys())}")

    if num_fontes == 0:
        logger.warning(f"[NUTRI-3SRC] Nenhuma fonte retornou dados para: {nome}")
        return None

    # Calcular media com exclusao de outliers
    # Se uma fonte difere >2x da mediana das outras, é excluida
    media = {}
    for k in NUTRIENT_KEYS:
        values = [src[k] for src in sources.values() if src.get(k, 0) > 0]
        if not values:
            media[k] = 0.0
            continue
        if len(values) <= 2:
            media[k] = round(sum(values) / len(values), 1)
        else:
            # Com 3+ valores: excluir outlier se >2x a mediana dos outros
            sorted_vals = sorted(values)
            median_val = sorted_vals[len(sorted_vals) // 2]
            filtered = [v for v in values if v <= median_val * 2.5]
            if filtered:
                media[k] = round(sum(filtered) / len(filtered), 1)
            else:
                media[k] = round(sum(values) / len(values), 1)

    result = {
        "nome": nome,
        "ingredientes": ingredientes,
        **media,
        "num_fontes": num_fontes,
        "fontes_usadas": list(sources.keys()),
        "fonte_principal": f"Media de {num_fontes} fontes ({', '.join(sources.keys())})",
        "detalhes_fontes": sources,
    }

    return result
