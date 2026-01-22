"""
SoulNutri - Serviço FatSecret API
Reconhecimento de alimentos via imagem
Free tier: 150.000 requests/mês via RapidAPI
"""

import os
import base64
import httpx
import json
from typing import Optional
from io import BytesIO
from PIL import Image

# Configuração
FATSECRET_RAPIDAPI_KEY = os.environ.get('FATSECRET_RAPIDAPI_KEY')
FATSECRET_API_HOST = "fatsecret4.p.rapidapi.com"


async def identify_with_fatsecret(image_bytes: bytes) -> dict:
    """
    Identifica alimento usando FatSecret API via RapidAPI.
    Retorna informações nutricionais e nome do alimento.
    
    Args:
        image_bytes: Imagem em bytes
        
    Returns:
        dict com resultado da identificação
    """
    if not FATSECRET_RAPIDAPI_KEY:
        return {"ok": False, "error": "FATSECRET_RAPIDAPI_KEY não configurada", "source": "fatsecret"}
    
    try:
        # Otimizar imagem (redimensionar para 512x512 max)
        img = Image.open(BytesIO(image_bytes))
        
        # Redimensionar se necessário
        max_size = 512
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Converter para RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Converter para base64
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=80)
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Fazer request para FatSecret
        url = "https://fatsecret4.p.rapidapi.com/rest/image-recognition/v2"
        
        headers = {
            "X-RapidAPI-Key": FATSECRET_RAPIDAPI_KEY,
            "X-RapidAPI-Host": FATSECRET_API_HOST,
            "Content-Type": "application/json"
        }
        
        payload = {
            "image_b64": image_b64,
            "include_food_data": True,
            "region": "BR",
            "language": "pt"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                return {
                    "ok": False, 
                    "error": f"FatSecret API error: {response.status_code}",
                    "source": "fatsecret"
                }
            
            data = response.json()
        
        # Processar resposta
        if "food_response" in data and data["food_response"].get("food"):
            foods = data["food_response"]["food"]
            if isinstance(foods, dict):
                foods = [foods]
            
            if foods:
                food = foods[0]  # Pegar o primeiro resultado
                
                # Extrair informações nutricionais
                servings = food.get("servings", {}).get("serving", [])
                if isinstance(servings, dict):
                    servings = [servings]
                
                nutrition = {}
                if servings:
                    serving = servings[0]
                    nutrition = {
                        "calorias": f"{serving.get('calories', 'N/A')} kcal",
                        "proteinas": f"{serving.get('protein', 'N/A')}g",
                        "carboidratos": f"{serving.get('carbohydrate', 'N/A')}g",
                        "gorduras": f"{serving.get('fat', 'N/A')}g",
                        "fibras": f"{serving.get('fiber', 'N/A')}g",
                        "sodio": f"{serving.get('sodium', 'N/A')}mg"
                    }
                
                # Determinar categoria
                categoria = "proteína animal"
                food_name_lower = food.get("food_name", "").lower()
                
                # Verificar se é vegano/vegetariano
                vegan_keywords = ["salada", "vegano", "vegan", "legume", "verdura", "fruta", "grão"]
                vegetarian_keywords = ["ovo", "queijo", "leite", "iogurte"]
                meat_keywords = ["carne", "frango", "peixe", "bacon", "presunto", "camarão"]
                
                if any(kw in food_name_lower for kw in meat_keywords):
                    categoria = "proteína animal"
                elif any(kw in food_name_lower for kw in vegetarian_keywords):
                    categoria = "vegetariano"
                elif any(kw in food_name_lower for kw in vegan_keywords):
                    categoria = "vegano"
                
                # Emoji da categoria
                cat_emoji = {"vegano": "🌱", "vegetariano": "🥬", "proteína animal": "🍖"}
                
                return {
                    "ok": True,
                    "identified": True,
                    "nome": food.get("food_name", "Alimento"),
                    "dish_display": food.get("food_name", "Alimento"),
                    "food_id": food.get("food_id"),
                    "categoria": categoria,
                    "category": categoria,
                    "category_emoji": cat_emoji.get(categoria, "🍽️"),
                    "confidence": "alta",
                    "score": 0.90,
                    "nutrition": nutrition,
                    "descricao": food.get("food_description", ""),
                    "brand": food.get("brand_name"),
                    "source": "fatsecret",
                    "ingredientes": [],
                    "beneficios": [],
                    "riscos": []
                }
        
        # Nenhum alimento reconhecido
        return {
            "ok": True,
            "identified": False,
            "message": "FatSecret não reconheceu o alimento",
            "source": "fatsecret"
        }
        
    except httpx.TimeoutException:
        return {"ok": False, "error": "Timeout na API FatSecret", "source": "fatsecret"}
    except Exception as e:
        return {"ok": False, "error": str(e), "source": "fatsecret"}


async def test_fatsecret_performance():
    """
    Testa a performance da API FatSecret.
    """
    import time
    
    # Criar imagem de teste simples
    img = Image.new('RGB', (256, 256), color='green')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    
    start = time.time()
    result = await identify_with_fatsecret(image_bytes)
    elapsed = (time.time() - start) * 1000
    
    return {
        "elapsed_ms": round(elapsed, 2),
        "result": result
    }
