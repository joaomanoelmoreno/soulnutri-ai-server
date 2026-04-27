# -*- coding: utf-8 -*-
"""
USDA Ingredient Fallback — SoulNutri
Chamado apenas quando buscar_dados_taco() retorna None.
Busca por ingrediente individual no USDA FoodData Central.
Cache em memória evita chamadas repetidas na mesma sessão.
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

USDA_API_KEY = os.environ.get("USDA_API_KEY", "DEMO_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# ── Cache em memória (reseta no restart — suficiente para batch e sessões) ──
_CACHE: dict = {}

# ── Tradução PT → EN para ingredientes comuns em restaurantes do Brasil ──────
# Apenas os que o TACO definitivamente não cobre
TRADUCAO_PT_EN: dict = {
    # Culinária japonesa / asiática
    "misso": "miso paste",
    "missô": "miso paste",
    "molho tare": "tare sauce soy",
    "kewpie": "japanese mayonnaise",
    "papel de arroz": "rice paper wrapper",
    "nori": "nori seaweed dried",
    "dashi": "dashi broth",
    "molho de ostras": "oyster sauce",
    "molho teriyaki": "teriyaki sauce",
    "sake culinario": "sake cooking wine",
    "sake culinário": "sake cooking wine",
    "shoyu": "soy sauce",
    "vinagre de arroz": "rice vinegar",
    "pasta de amendoim": "peanut butter",
    "gergelim importado": "sesame seeds",
    "tahine": "tahini",
    "tahini": "tahini",
    "tofu": "tofu firm raw",
    "edamame": "edamame frozen",
    # Culinária italiana / mediterrânea
    "pesto genovese": "pesto sauce basil",
    "ricota": "ricotta cheese",
    "ricotta": "ricotta cheese",
    "mascarpone": "mascarpone cheese",
    "provolone": "provolone cheese",
    "pecorino": "pecorino romano cheese",
    "parmigiano": "parmesan cheese",
    "burrata": "burrata cheese",
    "nduja": "nduja sausage pork",
    "speck": "prosciutto smoked",
    "bottarga": "bottarga dried fish roe",
    "aliche": "anchovies",
    "anchova": "anchovies",
    "capperi": "capers",
    # Culinária francesa
    "creme fraiche": "creme fraiche",
    "crème fraîche": "creme fraiche",
    "gruyere": "gruyere cheese",
    "gruyère": "gruyere cheese",
    "brie": "brie cheese",
    "camembert": "camembert cheese",
    "roquefort": "roquefort cheese",
    "foie gras": "foie gras duck liver",
    # Culinária árabe / israelense / mediterrânea
    "homus": "hummus",
    "hummus": "hummus",
    "pita": "pita bread",
    "falafel": "falafel",
    "kafta": "kefta ground beef lamb",
    "quibe": "kibbeh lamb",
    "tabule": "tabbouleh",
    "za atar": "za atar spice blend",
    "zaatar": "zaatar spice blend",
    "labneh": "labneh strained yogurt",
    "sumac": "sumac spice",
    "sumaque": "sumac spice",
    # Sementes e grãos
    "sementes de abobora": "pumpkin seeds",
    "sementes de abóbora": "pumpkin seeds",
    "sementes de girassol": "sunflower seeds",
    "sementes de gergelim preto": "black sesame seeds",
    "sementes de gergelim branco": "sesame seeds white",
    "sementes de chia": "chia seeds",
    "sementes de linhaca": "flaxseed",
    "sementes de linhaça": "flaxseed",
    "sementes de canhamo": "hemp seeds",
    # Frutas exóticas / internacionais
    "maple syrup": "maple syrup",
    "maple light": "maple syrup light",
    "agave": "agave syrup",
    "xarope de agave": "agave syrup",
    "frutas vermelhas": "mixed berries",
    "blueberry": "blueberries",
    "mirtilo": "blueberries",
    "cramberry": "cranberries",
    "cranberry": "cranberries",
    "framboesa": "raspberries",
    "physalis": "cape gooseberries",
    # Outros ingredientes internacionais
    "cream cheese": "cream cheese",
    "philadelphia": "cream cheese",
    "molho worcestershire": "worcestershire sauce",
    "molho tabasco": "tabasco hot sauce",
    "molho sriracha": "sriracha sauce",
    "wasabi": "wasabi paste",
    "gengibre em po": "ginger powder",
    "gengibre em pó": "ginger powder",
    "cúrcuma": "turmeric powder",
    "curcuma": "turmeric powder",
    "cominho": "cumin ground",
    "harissa": "harissa paste",
    "curry em po": "curry powder",
    "curry em pó": "curry powder",
    "pasta de curry": "curry paste",
    "leite de coco": "coconut milk",
    "creme de coco": "coconut cream",
    "agua de coco": "coconut water",
    "água de coco": "coconut water",
    "amêndoas": "almonds",
    "amendoas": "almonds",
    "nozes pecã": "pecans",
    "nozes peca": "pecans",
    "pistache": "pistachios",
    "macadamia": "macadamia nuts",
    "macadâmia": "macadamia nuts",
    "avelã": "hazelnuts",
    "avela": "hazelnuts",
    "damasco": "apricots dried",
    "tâmara": "dates",
    "tamara": "dates",
    "figo seco": "figs dried",
    "uva passa preta": "raisins",
    "geleia": "jam fruit",
    "geléia": "jam fruit",
    "mel": "honey",
    "hortelã": "spearmint",
    "hortela": "spearmint",
    "manjericao": "basil fresh",
    "manjericão": "basil fresh",
    "alecrim": "rosemary fresh",
    "tomilho": "thyme fresh",
    "louro": "bay leaf",
    "erva doce": "fennel fresh",
    "erva-doce": "fennel bulb",
    "alcaparra": "capers",
    "alcaparras": "capers",
    "picles": "pickles cucumber",
    "pepino em conserva": "pickles cucumber",
    "molho de tomate": "tomato sauce",
    "tomate seco": "sun-dried tomatoes",
    "tomate pelado": "canned tomatoes",
    "cebolinha picada": "chives",
    "salsinha picada": "parsley fresh",
    "salsinha": "parsley fresh",
}

# ── Campos nutricionais relevantes do USDA ─────────────────────────────────
USDA_NUTRIENT_MAP = {
    "Energy":                        "calorias",
    "Protein":                       "proteinas",
    "Carbohydrate, by difference":   "carboidratos",
    "Total lipid (fat)":             "gorduras",
    "Fiber, total dietary":          "fibras",
    "Sodium, Na":                    "sodio",
    "Calcium, Ca":                   "calcio",
    "Iron, Fe":                      "ferro",
    "Potassium, K":                  "potassio",
    "Zinc, Zn":                      "zinco",
    "Cholesterol":                   "colesterol",
    "Vitamin C, total ascorbic acid": "vitamina_c",
}


def _query_usda_sync(query: str) -> dict | None:
    """
    Busca síncrona no USDA FoodData Central.
    Retorna dados nutricionais por 100g ou None.
    """
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{USDA_BASE_URL}/foods/search",
                params={
                    "api_key": USDA_API_KEY,
                    "query": query,
                    "pageSize": 5,
                },
            )
        if resp.status_code == 429:
            logger.warning(f"[USDA] Rate limit para '{query}'")
            return None
        if resp.status_code != 200:
            logger.warning(f"[USDA] HTTP {resp.status_code} para '{query}'")
            return None

        foods = resp.json().get("foods", [])
        if not foods:
            return None

        for food in foods:
            nutrients = {}
            kcal_unit_ok = False
            for fn in food.get("foodNutrients", []):
                name  = fn.get("nutrientName", "")
                unit  = fn.get("unitName", "").upper()
                value = fn.get("value") or 0
                if name == "Energy":
                    if unit == "KCAL":
                        nutrients["calorias"] = value
                        kcal_unit_ok = True
                elif name in USDA_NUTRIENT_MAP:
                    nutrients[USDA_NUTRIENT_MAP[name]] = value

            cal = nutrients.get("calorias", 0)
            if kcal_unit_ok and 0 < cal < 950:
                desc = food.get("description", "?")
                logger.info(f"[USDA] '{query}' → '{desc}' ({cal} kcal)")
                result = {k: round(float(nutrients.get(k, 0)), 2) for k in USDA_NUTRIENT_MAP.values()}
                result["nome"] = f"(USDA) {desc}"
                return result

        return None

    except Exception as e:
        logger.warning(f"[USDA] Exceção para '{query}': {e}")
        return None


def buscar_dados_usda(ingrediente: str) -> dict | None:
    """
    Ponto de entrada principal.
    1. Verifica cache.
    2. Traduz PT→EN se disponível.
    3. Chama USDA.
    4. Guarda no cache.
    Retorna dict compatível com o formato do TACO_DATABASE ou None.
    """
    key = ingrediente.lower().strip()

    if key in _CACHE:
        return _CACHE[key]

    # Tradução PT → EN
    query_en = TRADUCAO_PT_EN.get(key)
    if not query_en:
        # Tentar sem acentos também
        import unicodedata
        key_ascii = unicodedata.normalize("NFKD", key).encode("ASCII", "ignore").decode()
        query_en = TRADUCAO_PT_EN.get(key_ascii, key)  # Fallback: nome original

    # Limpar caracteres especiais que a API USDA não aceita (parênteses, barras)
    import re as _re
    query_en = _re.sub(r'[()\/]', ' ', query_en)
    query_en = _re.sub(r'\s+', ' ', query_en).strip()[:80]  # max 80 chars

    result = _query_usda_sync(query_en)
    _CACHE[key] = result  # None também cacheado — evita re-tentativa
    return result
