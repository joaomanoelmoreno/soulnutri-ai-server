"""
SoulNutri - Google Cloud Vision API Service
Fallback para reconhecimento de imagem quando CLIP local tem baixa confiança.

CUSTO: 
- 1.000 imagens/mês GRÁTIS
- Depois: $1.50 por 1000 imagens (R$ 0,0075 por imagem)

VELOCIDADE:
- ~300-500ms por requisição
"""

import os
import base64
import logging
import time
from typing import Optional, Dict, List
from datetime import datetime, timezone
import httpx
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

# Configuração - carrega do .env
GOOGLE_VISION_API_KEY = os.environ.get('GOOGLE_VISION_API_KEY', '')
GOOGLE_VISION_ENDPOINT = "https://vision.googleapis.com/v1/images:annotate"

# Cache simples para evitar chamadas repetidas
_vision_cache: Dict[str, dict] = {}
_MAX_CACHE_SIZE = 100

# Contadores em memória (backup até salvar no MongoDB)
_usage_counter = {"calls": 0, "month": datetime.now(timezone.utc).strftime("%Y-%m")}


async def log_google_vision_usage(db):
    """Registra uso do Google Vision no MongoDB para controle de custos"""
    try:
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        await db.api_usage.update_one(
            {"service": "google_vision", "month": current_month},
            {
                "$inc": {"calls": 1},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )
    except Exception as e:
        logger.warning(f"[GoogleVision] Erro ao registrar uso: {e}")


async def get_google_vision_usage(db) -> Dict:
    """Retorna estatísticas de uso do Google Vision"""
    try:
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        
        # Uso do mês atual
        current = await db.api_usage.find_one({"service": "google_vision", "month": current_month})
        current_calls = current.get("calls", 0) if current else 0
        
        # Histórico dos últimos 3 meses
        history = []
        cursor = db.api_usage.find({"service": "google_vision"}).sort("month", -1).limit(3)
        async for doc in cursor:
            history.append({
                "month": doc.get("month"),
                "calls": doc.get("calls", 0)
            })
        
        # Calcular custo estimado
        free_tier = 1000
        calls_paid = max(0, current_calls - free_tier)
        cost_usd = calls_paid * 0.0015  # $1.50 per 1000
        cost_brl = cost_usd * 5  # Aproximado
        
        return {
            "current_month": current_month,
            "calls_this_month": current_calls,
            "free_tier": free_tier,
            "calls_remaining_free": max(0, free_tier - current_calls),
            "calls_paid": calls_paid,
            "estimated_cost_usd": round(cost_usd, 2),
            "estimated_cost_brl": round(cost_brl, 2),
            "history": history
        }
    except Exception as e:
        logger.error(f"[GoogleVision] Erro ao obter uso: {e}")
        return {"error": str(e)}


async def detect_labels_google_vision(
    image_bytes: bytes,
    max_results: int = 10
) -> Dict:
    """
    Detecta labels em uma imagem usando Google Cloud Vision API.
    
    Args:
        image_bytes: Bytes da imagem
        max_results: Número máximo de labels a retornar
        
    Returns:
        Dict com labels detectados e scores
    """
    if not GOOGLE_VISION_API_KEY:
        logger.warning("[GoogleVision] API key não configurada")
        return {
            "ok": False,
            "error": "GOOGLE_VISION_API_KEY não configurada",
            "labels": []
        }
    
    start_time = time.time()
    
    try:
        # Codificar imagem em base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Verificar cache
        cache_key = image_base64[:100]  # Usar primeiros 100 chars como chave
        if cache_key in _vision_cache:
            logger.info("[GoogleVision] Resultado do cache")
            return _vision_cache[cache_key]
        
        # Preparar requisição
        request_body = {
            "requests": [{
                "image": {
                    "content": image_base64
                },
                "features": [
                    {
                        "type": "LABEL_DETECTION",
                        "maxResults": max_results
                    }
                ]
            }]
        }
        
        # Fazer requisição
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GOOGLE_VISION_ENDPOINT}?key={GOOGLE_VISION_API_KEY}",
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code != 200:
            logger.error(f"[GoogleVision] Erro API: {response.status_code} - {response.text}")
            return {
                "ok": False,
                "error": f"API error: {response.status_code}",
                "labels": [],
                "elapsed_ms": elapsed_ms
            }
        
        data = response.json()
        
        # Extrair labels
        labels = []
        if "responses" in data and len(data["responses"]) > 0:
            annotations = data["responses"][0].get("labelAnnotations", [])
            for ann in annotations:
                labels.append({
                    "description": ann.get("description", ""),
                    "score": ann.get("score", 0.0),
                    "mid": ann.get("mid", "")
                })
        
        result = {
            "ok": True,
            "labels": labels,
            "elapsed_ms": round(elapsed_ms, 2),
            "source": "google_vision"
        }
        
        # Adicionar ao cache
        if len(_vision_cache) >= _MAX_CACHE_SIZE:
            # Limpar metade do cache
            keys = list(_vision_cache.keys())[:_MAX_CACHE_SIZE // 2]
            for k in keys:
                del _vision_cache[k]
        _vision_cache[cache_key] = result
        
        logger.info(f"[GoogleVision] {len(labels)} labels em {elapsed_ms:.0f}ms")
        return result
        
    except httpx.TimeoutException:
        logger.error("[GoogleVision] Timeout na requisição")
        return {
            "ok": False,
            "error": "Timeout",
            "labels": []
        }
    except Exception as e:
        logger.error(f"[GoogleVision] Erro: {e}")
        return {
            "ok": False,
            "error": str(e),
            "labels": []
        }


def match_google_labels_to_dishes(
    labels: List[Dict],
    dish_index: Dict[str, List[int]]
) -> Optional[Dict]:
    """
    Tenta encontrar correspondência entre labels do Google Vision
    e pratos no índice local.
    
    Args:
        labels: Lista de labels do Google Vision
        dish_index: Dicionário dish_to_idx do índice local
        
    Returns:
        Dict com prato encontrado ou None
    """
    if not labels:
        return None
    
    # Mapeamento de termos em inglês para português
    FOOD_TRANSLATIONS = {
        "rice": "arroz",
        "beans": "feijao",
        "chicken": "frango",
        "beef": "carne",
        "fish": "peixe",
        "salad": "salada",
        "vegetables": "legumes",
        "pasta": "massa",
        "soup": "sopa",
        "egg": "ovo",
        "potato": "batata",
        "tomato": "tomate",
        "onion": "cebola",
        "garlic": "alho",
        "bread": "pao",
        "cheese": "queijo",
        "milk": "leite",
        "fruit": "fruta",
        "meat": "carne",
        "pork": "porco",
        "shrimp": "camarao",
        "seafood": "frutos_do_mar",
        "grilled": "grelhado",
        "fried": "frito",
        "roasted": "assado",
        "steamed": "cozido",
        "vegetable": "vegetal",
        "cooked": "cozido",
        "food": "comida",
        "dish": "prato",
        "cuisine": "culinaria",
        "meal": "refeicao",
        "lunch": "almoco",
        "dinner": "jantar",
        "stew": "ensopado",
        "casserole": "cacarola",
        "curry": "curry",
        "tofu": "tofu",
        "lentil": "lentilha",
        "spinach": "espinafre",
        "carrot": "cenoura",
        "broccoli": "brocolis",
        "cauliflower": "couve_flor",
        "zucchini": "abobrinha",
        "squash": "abobora",
        "pepper": "pimentao",
        "mushroom": "cogumelo"
    }
    
    dish_slugs = list(dish_index.keys())
    best_match = None
    best_score = 0.0
    
    for label in labels:
        desc = label.get("description", "").lower()
        score = label.get("score", 0.0)
        
        # Traduzir para português se necessário
        desc_pt = FOOD_TRANSLATIONS.get(desc, desc)
        
        # Buscar correspondência no índice
        for slug in dish_slugs:
            slug_clean = slug.lower().replace("_", " ")
            
            # Verificar se há correspondência
            if desc_pt in slug_clean or slug_clean in desc_pt:
                if score > best_score:
                    best_score = score
                    best_match = {
                        "dish": slug,
                        "score": score,
                        "matched_label": desc,
                        "source": "google_vision"
                    }
            
            # Verificar termo original também
            if desc in slug_clean:
                if score > best_score:
                    best_score = score
                    best_match = {
                        "dish": slug,
                        "score": score,
                        "matched_label": desc,
                        "source": "google_vision"
                    }
    
    return best_match


def is_google_vision_available() -> bool:
    """Verifica se Google Vision está configurado"""
    return bool(GOOGLE_VISION_API_KEY)


def get_google_vision_status() -> Dict:
    """Retorna status do serviço Google Vision"""
    return {
        "available": is_google_vision_available(),
        "api_key_set": bool(GOOGLE_VISION_API_KEY),
        "endpoint": GOOGLE_VISION_ENDPOINT,
        "cache_size": len(_vision_cache)
    }
