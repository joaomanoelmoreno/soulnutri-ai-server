"""
SoulNutri - Serviço Hugging Face Food Recognition
Modelo: nateraw/food (Food-101, 89% precisão)
GRATUITO - Inference API do Hugging Face
"""

import os
import httpx
import base64
from io import BytesIO
from PIL import Image
from typing import Optional

# Token do Hugging Face (opcional para uso básico, recomendado para rate limits maiores)
HF_TOKEN = os.environ.get('HF_TOKEN', '')

# Mapeamento de classes Food-101 para português
FOOD101_CLASSES_PT = {
    "apple_pie": "Torta de Maçã",
    "baby_back_ribs": "Costela de Porco",
    "baklava": "Baklava",
    "beef_carpaccio": "Carpaccio de Carne",
    "beef_tartare": "Steak Tartare",
    "beet_salad": "Salada de Beterraba",
    "beignets": "Beignets",
    "bibimbap": "Bibimbap",
    "bread_pudding": "Pudim de Pão",
    "breakfast_burrito": "Burrito de Café da Manhã",
    "bruschetta": "Bruschetta",
    "caesar_salad": "Salada Caesar",
    "cannoli": "Cannoli",
    "caprese_salad": "Salada Caprese",
    "carrot_cake": "Bolo de Cenoura",
    "ceviche": "Ceviche",
    "cheesecake": "Cheesecake",
    "cheese_plate": "Tábua de Queijos",
    "chicken_curry": "Frango ao Curry",
    "chicken_quesadilla": "Quesadilla de Frango",
    "chicken_wings": "Asas de Frango",
    "chocolate_cake": "Bolo de Chocolate",
    "chocolate_mousse": "Mousse de Chocolate",
    "churros": "Churros",
    "clam_chowder": "Sopa de Mariscos",
    "club_sandwich": "Club Sandwich",
    "crab_cakes": "Bolinhos de Caranguejo",
    "creme_brulee": "Crème Brûlée",
    "croque_madame": "Croque Madame",
    "cup_cakes": "Cupcakes",
    "deviled_eggs": "Ovos Recheados",
    "donuts": "Donuts",
    "dumplings": "Dumplings",
    "edamame": "Edamame",
    "eggs_benedict": "Ovos Benedict",
    "escargots": "Escargots",
    "falafel": "Falafel",
    "filet_mignon": "Filé Mignon",
    "fish_and_chips": "Fish and Chips",
    "foie_gras": "Foie Gras",
    "french_fries": "Batata Frita",
    "french_onion_soup": "Sopa de Cebola",
    "french_toast": "Rabanada",
    "fried_calamari": "Lula Frita",
    "fried_rice": "Arroz Frito",
    "frozen_yogurt": "Frozen Yogurt",
    "garlic_bread": "Pão de Alho",
    "gnocchi": "Nhoque",
    "greek_salad": "Salada Grega",
    "grilled_cheese_sandwich": "Sanduíche de Queijo Grelhado",
    "grilled_salmon": "Salmão Grelhado",
    "guacamole": "Guacamole",
    "gyoza": "Gyoza",
    "hamburger": "Hambúrguer",
    "hot_and_sour_soup": "Sopa Agridoce",
    "hot_dog": "Cachorro-Quente",
    "huevos_rancheros": "Huevos Rancheros",
    "hummus": "Homus",
    "ice_cream": "Sorvete",
    "lasagna": "Lasanha",
    "lobster_bisque": "Bisque de Lagosta",
    "lobster_roll_sandwich": "Sanduíche de Lagosta",
    "macaroni_and_cheese": "Macarrão com Queijo",
    "macarons": "Macarons",
    "miso_soup": "Sopa de Missô",
    "mussels": "Mexilhões",
    "nachos": "Nachos",
    "omelette": "Omelete",
    "onion_rings": "Anéis de Cebola",
    "oysters": "Ostras",
    "pad_thai": "Pad Thai",
    "paella": "Paella",
    "pancakes": "Panquecas",
    "panna_cotta": "Panna Cotta",
    "peking_duck": "Pato à Pequim",
    "pho": "Pho",
    "pizza": "Pizza",
    "pork_chop": "Costeleta de Porco",
    "poutine": "Poutine",
    "prime_rib": "Costela Premium",
    "pulled_pork_sandwich": "Sanduíche de Carne Desfiada",
    "ramen": "Ramen",
    "ravioli": "Ravióli",
    "red_velvet_cake": "Bolo Red Velvet",
    "risotto": "Risoto",
    "samosa": "Samosa",
    "sashimi": "Sashimi",
    "scallops": "Vieiras",
    "seaweed_salad": "Salada de Algas",
    "shrimp_and_grits": "Camarão com Grits",
    "spaghetti_bolognese": "Espaguete à Bolonhesa",
    "spaghetti_carbonara": "Espaguete Carbonara",
    "spring_rolls": "Rolinho Primavera",
    "steak": "Bife",
    "strawberry_shortcake": "Shortcake de Morango",
    "sushi": "Sushi",
    "tacos": "Tacos",
    "takoyaki": "Takoyaki",
    "tiramisu": "Tiramisù",
    "tuna_tartare": "Tartar de Atum",
    "waffles": "Waffles"
}

# Categorias por tipo de alimento
CATEGORIAS = {
    "vegano": ["edamame", "falafel", "french_fries", "guacamole", "hummus", "seaweed_salad", "spring_rolls"],
    "vegetariano": ["apple_pie", "beet_salad", "bread_pudding", "bruschetta", "caesar_salad", "caprese_salad", 
                    "carrot_cake", "cheesecake", "cheese_plate", "chocolate_cake", "chocolate_mousse", 
                    "churros", "creme_brulee", "cup_cakes", "deviled_eggs", "donuts", "eggs_benedict",
                    "french_toast", "frozen_yogurt", "garlic_bread", "gnocchi", "greek_salad",
                    "grilled_cheese_sandwich", "ice_cream", "macaroni_and_cheese", "macarons",
                    "omelette", "onion_rings", "pancakes", "panna_cotta", "pizza", "ravioli",
                    "red_velvet_cake", "risotto", "strawberry_shortcake", "tiramisu", "waffles"],
    "proteína animal": ["baby_back_ribs", "beef_carpaccio", "beef_tartare", "bibimbap", "breakfast_burrito",
                        "chicken_curry", "chicken_quesadilla", "chicken_wings", "clam_chowder", 
                        "club_sandwich", "crab_cakes", "croque_madame", "dumplings", "escargots",
                        "filet_mignon", "fish_and_chips", "foie_gras", "fried_calamari", "fried_rice",
                        "grilled_salmon", "gyoza", "hamburger", "hot_and_sour_soup", "hot_dog",
                        "huevos_rancheros", "lasagna", "lobster_bisque", "lobster_roll_sandwich",
                        "miso_soup", "mussels", "nachos", "oysters", "pad_thai", "paella",
                        "peking_duck", "pho", "pork_chop", "poutine", "prime_rib", 
                        "pulled_pork_sandwich", "ramen", "samosa", "sashimi", "scallops",
                        "shrimp_and_grits", "spaghetti_bolognese", "spaghetti_carbonara",
                        "steak", "sushi", "tacos", "takoyaki", "tuna_tartare", "ceviche"]
}


def get_categoria(food_class: str) -> tuple:
    """Retorna categoria e emoji do alimento"""
    food_lower = food_class.lower()
    
    for cat, foods in CATEGORIAS.items():
        if food_lower in foods:
            emoji = {"vegano": "🌱", "vegetariano": "🥬", "proteína animal": "🍖"}
            return cat, emoji.get(cat, "🍽️")
    
    return "proteína animal", "🍖"  # Default


async def identify_with_huggingface(image_bytes: bytes) -> dict:
    """
    Identifica alimento usando Hugging Face Inference API.
    Modelo: nateraw/food (Food-101)
    GRATUITO!
    
    Args:
        image_bytes: Imagem em bytes
        
    Returns:
        dict com resultado da identificação
    """
    try:
        # Otimizar imagem
        img = Image.open(BytesIO(image_bytes))
        
        # Redimensionar para 224x224 (tamanho esperado pelo ViT)
        img = img.resize((224, 224), Image.LANCZOS)
        
        # Converter para RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Salvar em buffer
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        image_data = buffer.getvalue()
        
        # API do Hugging Face
        url = "https://api-inference.huggingface.co/models/nateraw/food"
        
        headers = {
            "Content-Type": "application/octet-stream"
        }
        
        # Adicionar token se disponível (aumenta rate limit)
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=headers, content=image_data)
            
            if response.status_code == 503:
                # Modelo carregando
                return {
                    "ok": False, 
                    "error": "Modelo carregando, tente novamente em alguns segundos",
                    "source": "huggingface"
                }
            
            if response.status_code != 200:
                return {
                    "ok": False, 
                    "error": f"HuggingFace API error: {response.status_code}",
                    "source": "huggingface"
                }
            
            predictions = response.json()
        
        # Processar resultado
        if predictions and len(predictions) > 0:
            top_pred = predictions[0]
            food_class = top_pred.get("label", "unknown")
            score = top_pred.get("score", 0)
            
            # Traduzir para português
            food_name_pt = FOOD101_CLASSES_PT.get(food_class, food_class.replace("_", " ").title())
            
            # Obter categoria
            categoria, cat_emoji = get_categoria(food_class)
            
            # Determinar confiança
            if score >= 0.8:
                confidence = "alta"
            elif score >= 0.5:
                confidence = "média"
            else:
                confidence = "baixa"
            
            return {
                "ok": True,
                "identified": True,
                "nome": food_name_pt,
                "dish_display": food_name_pt,
                "food_class": food_class,
                "categoria": categoria,
                "category": categoria,
                "category_emoji": cat_emoji,
                "confidence": confidence,
                "score": round(score, 4),
                "source": "huggingface",
                "alternatives": [
                    {"nome": FOOD101_CLASSES_PT.get(p["label"], p["label"]), "score": round(p["score"], 3)}
                    for p in predictions[1:4]
                ] if len(predictions) > 1 else [],
                "ingredientes": [],
                "beneficios": [],
                "riscos": [],
                "nutrition": None
            }
        
        return {
            "ok": True,
            "identified": False,
            "message": "Não foi possível identificar o alimento",
            "source": "huggingface"
        }
        
    except httpx.TimeoutException:
        return {"ok": False, "error": "Timeout na API HuggingFace", "source": "huggingface"}
    except Exception as e:
        return {"ok": False, "error": str(e), "source": "huggingface"}
