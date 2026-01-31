"""
SoulNutri - Serviço LogMeal API (Nível 2 do Sistema Híbrido)
============================================================
API especializada em reconhecimento de alimentos com 93-98% de precisão.
Usada como fallback quando o índice local (OpenCLIP) tem confiança < 90%.

Documentação: https://docs.logmeal.com
"""

import httpx
import base64
import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuração
LOGMEAL_API_KEY = os.environ.get('LOGMEAL_API_KEY', '')
LOGMEAL_API_URL = os.environ.get('LOGMEAL_API_URL', 'https://api.logmeal.com')


class LogMealService:
    """
    Serviço para interação com a LogMeal API.
    
    Fluxo:
    1. recognize_dish() - Identifica o prato na imagem
    2. get_nutritional_info() - Obtém informações nutricionais detalhadas
    """
    
    def __init__(self):
        self.api_key = LOGMEAL_API_KEY
        self.api_url = LOGMEAL_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def is_configured(self) -> bool:
        """Verifica se a API key está configurada"""
        return bool(self.api_key and len(self.api_key) > 10)
    
    async def recognize_dish(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Envia imagem para LogMeal API para reconhecimento.
        
        Args:
            image_bytes: Bytes da imagem (JPEG/PNG)
            
        Returns:
            Dict com resultado do reconhecimento incluindo:
            - imageId: ID para consultas posteriores
            - recognition: Lista de pratos identificados com probabilidades
            - foodType: Tipo de alimento (prepared_food, drink, etc)
        """
        if not self.is_configured():
            logger.warning("LogMeal API key não configurada")
            return {"ok": False, "error": "API key não configurada"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Endpoint de segmentação completa - identifica todos os itens na imagem
                # Documentação: https://docs.logmeal.com/reference/post_v2-image-segmentation-complete
                
                files = {
                    "image": ("food.jpg", image_bytes, "image/jpeg")
                }
                
                response = await client.post(
                    f"{self.api_url}/v2/image/segmentation/complete/v1.0",
                    files=files,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"LogMeal reconheceu: {data.get('imageId', 'N/A')}")
                    return {"ok": True, "data": data}
                elif response.status_code == 401:
                    logger.error("LogMeal: API key inválida ou não confirmada")
                    return {"ok": False, "error": "API key inválida"}
                elif response.status_code == 429:
                    logger.warning("LogMeal: Rate limit excedido")
                    return {"ok": False, "error": "Rate limit excedido"}
                else:
                    logger.error(f"LogMeal API error: {response.status_code} - {response.text}")
                    return {"ok": False, "error": f"Status {response.status_code}"}
                    
            except httpx.TimeoutException:
                logger.error("LogMeal API timeout")
                return {"ok": False, "error": "Timeout na requisição"}
            except httpx.RequestError as e:
                logger.error(f"LogMeal connection error: {e}")
                return {"ok": False, "error": f"Erro de conexão: {str(e)}"}
    
    async def get_nutritional_info(self, image_id: str) -> Dict[str, Any]:
        """
        Obtém informações nutricionais detalhadas para um prato reconhecido.
        
        Args:
            image_id: ID retornado pela função recognize_dish()
            
        Returns:
            Dict com 39 indicadores nutricionais incluindo:
            - energy_kcal, protein, carbs, fat, fiber
            - vitaminas, minerais, etc.
        """
        if not self.is_configured():
            return {"ok": False, "error": "API key não configurada"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Endpoint de informações nutricionais
                # Documentação: https://docs.logmeal.com/docs/guides-features-nutritional-information
                
                headers = self.headers.copy()
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                
                response = await client.post(
                    f"{self.api_url}/v2/nutrition/recipe/ingredients/v1.0",
                    data={"imageId": image_id},
                    headers=headers
                )
                
                if response.status_code == 200:
                    return {"ok": True, "data": response.json()}
                else:
                    logger.error(f"LogMeal nutrition error: {response.status_code}")
                    return {"ok": False, "error": f"Status {response.status_code}"}
                    
            except Exception as e:
                logger.error(f"LogMeal nutrition error: {e}")
                return {"ok": False, "error": str(e)}
    
    def parse_recognition_result(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte resposta da LogMeal para o formato padrão do SoulNutri.
        
        Args:
            raw_response: Resposta bruta da API
            
        Returns:
            Dict no formato padrão do SoulNutri
        """
        if not raw_response.get("ok"):
            return {
                "ok": False,
                "identified": False,
                "confidence": "baixa",
                "score": 0.0,
                "error": raw_response.get("error", "Erro desconhecido")
            }
        
        data = raw_response.get("data", {})
        
        # Extrair informações das regiões identificadas
        regions = data.get("segmentation_results", [])
        if not regions:
            regions = data.get("recognition_results", [])
        
        if not regions:
            return {
                "ok": True,
                "identified": False,
                "confidence": "baixa",
                "score": 0.0,
                "message": "Nenhum alimento identificado na imagem"
            }
        
        # Pegar o resultado com maior probabilidade
        best_result = None
        best_prob = 0.0
        
        for region in regions:
            recognition_list = region.get("recognition_results", [])
            if not recognition_list:
                recognition_list = [region] if "name" in region else []
            
            for rec in recognition_list:
                prob = rec.get("prob", rec.get("probability", 0.0))
                if prob > best_prob:
                    best_prob = prob
                    best_result = rec
        
        if not best_result:
            return {
                "ok": True,
                "identified": False,
                "confidence": "baixa",
                "score": 0.0,
                "message": "Não foi possível identificar o alimento"
            }
        
        # Determinar nível de confiança
        if best_prob >= 0.85:
            confidence = "alta"
        elif best_prob >= 0.60:
            confidence = "média"
        else:
            confidence = "baixa"
        
        # Extrair nome do prato
        dish_name = best_result.get("name", best_result.get("foodName", "Prato Desconhecido"))
        
        # Extrair food type
        food_type = data.get("foodType", {})
        if isinstance(food_type, dict):
            food_type_name = food_type.get("name", "prepared_food")
        else:
            food_type_name = str(food_type) if food_type else "prepared_food"
        
        # Mapear categoria
        category = self._map_category(food_type_name, dish_name)
        category_emoji = self._get_category_emoji(category)
        
        return {
            "ok": True,
            "identified": True,
            "dish": dish_name.lower().replace(" ", "_"),
            "dish_display": dish_name,
            "confidence": confidence,
            "score": best_prob,
            "message": f"Identificado pela LogMeal: {dish_name}",
            "category": category,
            "category_emoji": category_emoji,
            "image_id": data.get("imageId", ""),
            "food_type": food_type_name,
            "source": "logmeal"
        }
    
    def _map_category(self, food_type: str, dish_name: str) -> str:
        """Mapeia o tipo de alimento para categoria do SoulNutri"""
        dish_lower = dish_name.lower()
        
        # Detectar proteína animal
        animal_keywords = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 
                          'meat', 'steak', 'bacon', 'sausage', 'frango', 'carne', 'peixe',
                          'camarão', 'atum', 'salmão', 'porco', 'bife', 'linguiça']
        
        for keyword in animal_keywords:
            if keyword in dish_lower:
                return "proteína animal"
        
        # Detectar vegano (sem ovos, sem laticínios)
        vegan_keywords = ['salad', 'vegetable', 'fruit', 'vegan', 'legumes', 'salada',
                         'vegetal', 'fruta', 'grão', 'bean', 'lentil', 'tofu']
        
        dairy_egg_keywords = ['cheese', 'egg', 'milk', 'cream', 'butter', 'queijo', 
                             'ovo', 'leite', 'creme', 'manteiga', 'yogurt', 'iogurte']
        
        has_dairy_egg = any(k in dish_lower for k in dairy_egg_keywords)
        has_vegan = any(k in dish_lower for k in vegan_keywords)
        
        if has_vegan and not has_dairy_egg:
            return "vegano"
        elif has_vegan:
            return "vegetariano"
        
        # Default baseado no food_type
        if food_type in ['fresh', 'fruit', 'vegetable']:
            return "vegano"
        
        return "outros"
    
    def _get_category_emoji(self, category: str) -> str:
        """Retorna emoji para a categoria"""
        emojis = {
            "vegano": "🌱",
            "vegetariano": "🥚",
            "proteína animal": "🍖",
            "outros": "🍽️"
        }
        return emojis.get(category, "🍽️")


# Instância global do serviço
logmeal_service = LogMealService()


async def identify_with_logmeal(image_bytes: bytes) -> Dict[str, Any]:
    """
    Função de conveniência para identificar prato usando LogMeal.
    
    Args:
        image_bytes: Bytes da imagem
        
    Returns:
        Dict com resultado no formato padrão do SoulNutri
    """
    # Verificar se está configurado
    if not logmeal_service.is_configured():
        logger.warning("LogMeal não configurado, pulando Nível 2")
        return {
            "ok": False,
            "identified": False,
            "confidence": "baixa",
            "score": 0.0,
            "error": "LogMeal API não configurada",
            "source": "logmeal"
        }
    
    # Fazer reconhecimento
    recognition_result = await logmeal_service.recognize_dish(image_bytes)
    
    # Parsear resultado
    parsed = logmeal_service.parse_recognition_result(recognition_result)
    
    # Se identificou com sucesso, tentar obter info nutricional
    if parsed.get("ok") and parsed.get("identified") and parsed.get("image_id"):
        nutrition_result = await logmeal_service.get_nutritional_info(parsed["image_id"])
        if nutrition_result.get("ok"):
            parsed["nutrition_data"] = nutrition_result.get("data", {})
    
    return parsed
