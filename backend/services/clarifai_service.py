"""
SoulNutri - Serviço Clarifai API (Nível 2 do Sistema Híbrido)
=============================================================
API com 1.000 requisições/mês GRÁTIS
Reconhece 547+ tipos de alimentos

Documentação: https://clarifai.com/clarifai/main/models/food-item-recognition
"""

import httpx
import base64
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuração
CLARIFAI_PAT = os.environ.get('CLARIFAI_PAT', '')
CLARIFAI_USER_ID = "clarifai"
CLARIFAI_APP_ID = "main"
CLARIFAI_MODEL_ID = "food-item-recognition"


class ClarifaiService:
    """
    Serviço para reconhecimento de alimentos via Clarifai.
    Free tier: 1.000 requisições/mês
    """
    
    def __init__(self):
        self.pat = CLARIFAI_PAT
        # URL correta da API v2 com user_id e app_id
        self.api_url = f"https://api.clarifai.com/v2/users/{CLARIFAI_USER_ID}/apps/{CLARIFAI_APP_ID}/models/{CLARIFAI_MODEL_ID}/outputs"
        
    def is_configured(self) -> bool:
        """Verifica se a API está configurada"""
        return bool(self.pat and len(self.pat) > 10)
    
    async def recognize_food(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Envia imagem para Clarifai para reconhecimento de alimentos.
        
        Args:
            image_bytes: Bytes da imagem (JPEG/PNG)
            
        Returns:
            Dict com resultado do reconhecimento
        """
        if not self.is_configured():
            logger.warning("Clarifai PAT não configurado")
            return {"ok": False, "error": "Clarifai PAT não configurado"}
        
        # Converter imagem para base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        headers = {
            "Authorization": f"Key {self.pat}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": [
                {
                    "data": {
                        "image": {
                            "base64": image_base64
                        }
                    }
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {"ok": True, "data": data}
                elif response.status_code == 401:
                    logger.error("Clarifai: PAT inválido")
                    return {"ok": False, "error": "PAT inválido"}
                elif response.status_code == 402:
                    logger.error("Clarifai: Limite de requisições atingido")
                    return {"ok": False, "error": "Limite mensal atingido"}
                elif response.status_code == 429:
                    logger.warning("Clarifai: Rate limit")
                    return {"ok": False, "error": "Rate limit"}
                else:
                    logger.error(f"Clarifai error: {response.status_code} - {response.text[:200]}")
                    return {"ok": False, "error": f"Status {response.status_code}"}
                    
            except httpx.TimeoutException:
                logger.error("Clarifai timeout")
                return {"ok": False, "error": "Timeout"}
            except Exception as e:
                logger.error(f"Clarifai error: {e}")
                return {"ok": False, "error": str(e)}
    
    def parse_result(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte resposta da Clarifai para formato SoulNutri.
        """
        if not raw_response.get("ok"):
            return {
                "ok": False,
                "identified": False,
                "confidence": "baixa",
                "score": 0.0,
                "error": raw_response.get("error", "Erro desconhecido"),
                "source": "clarifai"
            }
        
        data = raw_response.get("data", {})
        outputs = data.get("outputs", [])
        
        if not outputs:
            return {
                "ok": True,
                "identified": False,
                "confidence": "baixa",
                "score": 0.0,
                "message": "Nenhum alimento identificado",
                "source": "clarifai"
            }
        
        # Pegar os conceitos (alimentos identificados)
        concepts = outputs[0].get("data", {}).get("concepts", [])
        
        if not concepts:
            return {
                "ok": True,
                "identified": False,
                "confidence": "baixa",
                "score": 0.0,
                "message": "Nenhum conceito alimentar identificado",
                "source": "clarifai"
            }
        
        # Pegar o resultado com maior probabilidade
        best = concepts[0]
        best_prob = best.get("value", 0.0)
        best_name = best.get("name", "Alimento")
        
        # Formatar nome (capitalizar)
        dish_display = best_name.replace("_", " ").title()
        
        # Determinar confiança
        if best_prob >= 0.85:
            confidence = "alta"
        elif best_prob >= 0.60:
            confidence = "média"
        else:
            confidence = "baixa"
        
        # Extrair ingredientes secundários (top 5)
        ingredients = [c.get("name", "").replace("_", " ").title() 
                      for c in concepts[1:6] if c.get("value", 0) > 0.3]
        
        # Categorizar
        category = self._categorize(best_name, concepts)
        category_emoji = {"vegano": "🌱", "vegetariano": "🥚", "proteína animal": "🍖"}.get(category, "🍽️")
        
        return {
            "ok": True,
            "identified": True,
            "dish": best_name.lower().replace(" ", "_"),
            "dish_display": dish_display,
            "confidence": confidence,
            "score": best_prob,
            "message": f"Identificado pela Clarifai: {dish_display}",
            "category": category,
            "category_emoji": category_emoji,
            "ingredientes": ingredients,
            "source": "clarifai",
            "all_concepts": [{"name": c.get("name"), "score": c.get("value")} 
                           for c in concepts[:10]]
        }
    
    def _categorize(self, main_food: str, concepts: list) -> str:
        """Categoriza o alimento"""
        all_names = [main_food.lower()] + [c.get("name", "").lower() for c in concepts[:10]]
        all_text = " ".join(all_names)
        
        # Proteína animal
        animal = ["meat", "chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp",
                 "bacon", "sausage", "steak", "ham", "seafood", "lamb", "turkey", "duck"]
        if any(a in all_text for a in animal):
            return "proteína animal"
        
        # Laticínios/Ovos (vegetariano)
        dairy = ["cheese", "egg", "milk", "cream", "butter", "yogurt"]
        if any(d in all_text for d in dairy):
            return "vegetariano"
        
        # Vegano (frutas, vegetais, grãos)
        vegan = ["vegetable", "fruit", "salad", "bean", "rice", "bread", "pasta", "noodle"]
        if any(v in all_text for v in vegan):
            return "vegano"
        
        return "outros"


# Instância global
clarifai_service = ClarifaiService()


async def identify_with_clarifai(image_bytes: bytes) -> Dict[str, Any]:
    """
    Função de conveniência para identificar alimento via Clarifai.
    """
    if not clarifai_service.is_configured():
        logger.warning("Clarifai não configurado, pulando Nível 2")
        return {
            "ok": False,
            "identified": False,
            "error": "Clarifai não configurado",
            "source": "clarifai"
        }
    
    result = await clarifai_service.recognize_food(image_bytes)
    return clarifai_service.parse_result(result)
