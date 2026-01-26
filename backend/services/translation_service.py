"""
SoulNutri - Serviço de Tradução
Usa LibreTranslate (GRATUITO e open-source)
Suporta: Português, Inglês, Espanhol, Francês, Alemão, Chinês
"""

import httpx
import logging
from typing import Optional, Dict, List
from functools import lru_cache

logger = logging.getLogger(__name__)

# LibreTranslate API - Gratuito!
LIBRETRANSLATE_URL = "https://libretranslate.com/translate"

# Idiomas suportados
SUPPORTED_LANGUAGES = {
    "pt": {"name": "Português", "flag": "🇧🇷", "native": "Português"},
    "en": {"name": "English", "flag": "🇺🇸", "native": "English"},
    "es": {"name": "Español", "flag": "🇪🇸", "native": "Español"},
    "fr": {"name": "Français", "flag": "🇫🇷", "native": "Français"},
    "de": {"name": "Deutsch", "flag": "🇩🇪", "native": "Deutsch"},
    "zh": {"name": "中文", "flag": "🇨🇳", "native": "中文"},
}

# Cache de traduções para evitar chamadas repetidas
_translation_cache: Dict[str, str] = {}

# Traduções estáticas da interface (não precisam de API)
UI_TRANSLATIONS = {
    "pt": {
        "identify_dish": "Identificar Prato",
        "gallery": "Galeria",
        "new_scan": "Nova",
        "loading": "Identificando...",
        "position_dish": "Posicione o prato aqui",
        "tap_to_photo": "Toque para fotografar",
        "high_confidence": "ALTA CONFIANÇA",
        "medium_confidence": "MÉDIA CONFIANÇA",
        "low_confidence": "BAIXA CONFIANÇA",
        "ingredients": "Ingredientes",
        "benefits": "Benefícios para a Saúde",
        "risks": "Riscos e Alertas",
        "nutrition_info": "Informação Nutricional (100g)",
        "calories": "Calorias",
        "proteins": "Proteínas",
        "carbs": "Carboidratos",
        "fats": "Gorduras",
        "no_allergens": "Não contém alérgenos conhecidos",
        "share": "Compartilhar",
        "feedback_question": "Este reconhecimento está correto?",
        "yes_correct": "Sim, correto",
        "no_correct": "Não, corrigir",
        "thanks_feedback": "Obrigado pelo feedback!",
        "premium": "Premium",
        "diet": "Dieta",
        "your_plate": "Seu Prato",
        "items": "itens",
        "add_more": "Adicionar mais",
        "plate_complete": "Prato completo",
        "scientific_info": "Você Sabia?",
        "curiosity": "Curiosidade Científica",
        "truth_or_myth": "Verdade ou Mito?",
        "truth": "VERDADE",
        "myth": "MITO",
        "partial": "PARCIALMENTE",
        "camera_error": "Câmera não disponível",
        "try_again": "Tentar novamente",
        "vegan": "vegano",
        "vegetarian": "vegetariano",
        "animal_protein": "proteína animal",
        "select_language": "Selecionar idioma",
    },
    "en": {
        "identify_dish": "Identify Dish",
        "gallery": "Gallery",
        "new_scan": "New",
        "loading": "Identifying...",
        "position_dish": "Position the dish here",
        "tap_to_photo": "Tap to take photo",
        "high_confidence": "HIGH CONFIDENCE",
        "medium_confidence": "MEDIUM CONFIDENCE",
        "low_confidence": "LOW CONFIDENCE",
        "ingredients": "Ingredients",
        "benefits": "Health Benefits",
        "risks": "Risks and Alerts",
        "nutrition_info": "Nutrition Information (100g)",
        "calories": "Calories",
        "proteins": "Proteins",
        "carbs": "Carbohydrates",
        "fats": "Fats",
        "no_allergens": "No known allergens",
        "share": "Share",
        "feedback_question": "Is this identification correct?",
        "yes_correct": "Yes, correct",
        "no_correct": "No, correct it",
        "thanks_feedback": "Thanks for your feedback!",
        "premium": "Premium",
        "diet": "Diet",
        "your_plate": "Your Plate",
        "items": "items",
        "add_more": "Add more",
        "plate_complete": "Plate complete",
        "scientific_info": "Did You Know?",
        "curiosity": "Scientific Curiosity",
        "truth_or_myth": "Truth or Myth?",
        "truth": "TRUTH",
        "myth": "MYTH",
        "partial": "PARTIALLY",
        "camera_error": "Camera not available",
        "try_again": "Try again",
        "vegan": "vegan",
        "vegetarian": "vegetarian",
        "animal_protein": "animal protein",
        "select_language": "Select language",
    },
    "es": {
        "identify_dish": "Identificar Plato",
        "gallery": "Galería",
        "new_scan": "Nueva",
        "loading": "Identificando...",
        "position_dish": "Coloque el plato aquí",
        "tap_to_photo": "Toque para fotografiar",
        "high_confidence": "ALTA CONFIANZA",
        "medium_confidence": "CONFIANZA MEDIA",
        "low_confidence": "BAJA CONFIANZA",
        "ingredients": "Ingredientes",
        "benefits": "Beneficios para la Salud",
        "risks": "Riesgos y Alertas",
        "nutrition_info": "Información Nutricional (100g)",
        "calories": "Calorías",
        "proteins": "Proteínas",
        "carbs": "Carbohidratos",
        "fats": "Grasas",
        "no_allergens": "Sin alérgenos conocidos",
        "share": "Compartir",
        "feedback_question": "¿Es correcto este reconocimiento?",
        "yes_correct": "Sí, correcto",
        "no_correct": "No, corregir",
        "thanks_feedback": "¡Gracias por tu comentario!",
        "premium": "Premium",
        "diet": "Dieta",
        "your_plate": "Tu Plato",
        "items": "elementos",
        "add_more": "Añadir más",
        "plate_complete": "Plato completo",
        "scientific_info": "¿Sabías que?",
        "curiosity": "Curiosidad Científica",
        "truth_or_myth": "¿Verdad o Mito?",
        "truth": "VERDAD",
        "myth": "MITO",
        "partial": "PARCIALMENTE",
        "camera_error": "Cámara no disponible",
        "try_again": "Intentar de nuevo",
        "vegan": "vegano",
        "vegetarian": "vegetariano",
        "animal_protein": "proteína animal",
        "select_language": "Seleccionar idioma",
    },
    "fr": {
        "identify_dish": "Identifier le Plat",
        "gallery": "Galerie",
        "new_scan": "Nouveau",
        "loading": "Identification...",
        "position_dish": "Placez le plat ici",
        "tap_to_photo": "Appuyez pour photographier",
        "high_confidence": "HAUTE CONFIANCE",
        "medium_confidence": "CONFIANCE MOYENNE",
        "low_confidence": "FAIBLE CONFIANCE",
        "ingredients": "Ingrédients",
        "benefits": "Bienfaits pour la Santé",
        "risks": "Risques et Alertes",
        "nutrition_info": "Information Nutritionnelle (100g)",
        "calories": "Calories",
        "proteins": "Protéines",
        "carbs": "Glucides",
        "fats": "Lipides",
        "no_allergens": "Pas d'allergènes connus",
        "share": "Partager",
        "feedback_question": "Cette identification est-elle correcte?",
        "yes_correct": "Oui, correct",
        "no_correct": "Non, corriger",
        "thanks_feedback": "Merci pour votre retour!",
        "premium": "Premium",
        "diet": "Régime",
        "your_plate": "Votre Assiette",
        "items": "éléments",
        "add_more": "Ajouter plus",
        "plate_complete": "Assiette complète",
        "scientific_info": "Le Saviez-Vous?",
        "curiosity": "Curiosité Scientifique",
        "truth_or_myth": "Vérité ou Mythe?",
        "truth": "VÉRITÉ",
        "myth": "MYTHE",
        "partial": "PARTIELLEMENT",
        "camera_error": "Caméra non disponible",
        "try_again": "Réessayer",
        "vegan": "végan",
        "vegetarian": "végétarien",
        "animal_protein": "protéine animale",
        "select_language": "Sélectionner la langue",
    },
    "de": {
        "identify_dish": "Gericht Identifizieren",
        "gallery": "Galerie",
        "new_scan": "Neu",
        "loading": "Identifizieren...",
        "position_dish": "Platzieren Sie das Gericht hier",
        "tap_to_photo": "Tippen zum Fotografieren",
        "high_confidence": "HOHE SICHERHEIT",
        "medium_confidence": "MITTLERE SICHERHEIT",
        "low_confidence": "NIEDRIGE SICHERHEIT",
        "ingredients": "Zutaten",
        "benefits": "Gesundheitsvorteile",
        "risks": "Risiken und Warnungen",
        "nutrition_info": "Nährwertinformation (100g)",
        "calories": "Kalorien",
        "proteins": "Proteine",
        "carbs": "Kohlenhydrate",
        "fats": "Fette",
        "no_allergens": "Keine bekannten Allergene",
        "share": "Teilen",
        "feedback_question": "Ist diese Erkennung korrekt?",
        "yes_correct": "Ja, korrekt",
        "no_correct": "Nein, korrigieren",
        "thanks_feedback": "Danke für Ihr Feedback!",
        "premium": "Premium",
        "diet": "Diät",
        "your_plate": "Ihr Teller",
        "items": "Artikel",
        "add_more": "Mehr hinzufügen",
        "plate_complete": "Teller komplett",
        "scientific_info": "Wussten Sie?",
        "curiosity": "Wissenschaftliche Neugierde",
        "truth_or_myth": "Wahrheit oder Mythos?",
        "truth": "WAHRHEIT",
        "myth": "MYTHOS",
        "partial": "TEILWEISE",
        "camera_error": "Kamera nicht verfügbar",
        "try_again": "Erneut versuchen",
        "vegan": "vegan",
        "vegetarian": "vegetarisch",
        "animal_protein": "tierisches Protein",
        "select_language": "Sprache auswählen",
    },
    "zh": {
        "identify_dish": "识别菜品",
        "gallery": "图库",
        "new_scan": "新扫描",
        "loading": "识别中...",
        "position_dish": "将菜品放在这里",
        "tap_to_photo": "点击拍照",
        "high_confidence": "高置信度",
        "medium_confidence": "中置信度",
        "low_confidence": "低置信度",
        "ingredients": "配料",
        "benefits": "健康益处",
        "risks": "风险和警告",
        "nutrition_info": "营养信息 (100克)",
        "calories": "卡路里",
        "proteins": "蛋白质",
        "carbs": "碳水化合物",
        "fats": "脂肪",
        "no_allergens": "无已知过敏原",
        "share": "分享",
        "feedback_question": "这个识别正确吗？",
        "yes_correct": "是的，正确",
        "no_correct": "不，纠正",
        "thanks_feedback": "感谢您的反馈！",
        "premium": "高级版",
        "diet": "饮食",
        "your_plate": "您的餐盘",
        "items": "项目",
        "add_more": "添加更多",
        "plate_complete": "餐盘完成",
        "scientific_info": "您知道吗？",
        "curiosity": "科学趣闻",
        "truth_or_myth": "真相还是谣言？",
        "truth": "真相",
        "myth": "谣言",
        "partial": "部分正确",
        "camera_error": "相机不可用",
        "try_again": "重试",
        "vegan": "纯素",
        "vegetarian": "素食",
        "animal_protein": "动物蛋白",
        "select_language": "选择语言",
    },
}


def get_ui_translations(lang: str = "pt") -> dict:
    """Retorna traduções da interface para o idioma especificado"""
    return UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["pt"])


def get_supported_languages() -> List[dict]:
    """Retorna lista de idiomas suportados"""
    return [
        {"code": code, **info}
        for code, info in SUPPORTED_LANGUAGES.items()
    ]


async def translate_text(
    text: str,
    source_lang: str = "pt",
    target_lang: str = "en"
) -> Optional[str]:
    """
    Traduz texto usando LibreTranslate (gratuito).
    
    Args:
        text: Texto a traduzir
        source_lang: Idioma de origem (default: pt)
        target_lang: Idioma de destino (default: en)
        
    Returns:
        Texto traduzido ou None se falhar
    """
    if source_lang == target_lang:
        return text
    
    if not text or not text.strip():
        return text
    
    # Verificar cache
    cache_key = f"{source_lang}:{target_lang}:{text}"
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                LIBRETRANSLATE_URL,
                data={
                    "q": text,
                    "source": source_lang,
                    "target": target_lang,
                    "format": "text"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get("translatedText", text)
                
                # Salvar no cache
                _translation_cache[cache_key] = translated
                
                return translated
            else:
                logger.warning(f"LibreTranslate error: {response.status_code}")
                return text
                
    except Exception as e:
        logger.error(f"Erro na tradução: {e}")
        return text


async def translate_dish_info(dish_info: dict, target_lang: str = "en") -> dict:
    """
    Traduz informações de um prato para o idioma especificado.
    
    Args:
        dish_info: Dicionário com informações do prato
        target_lang: Idioma de destino
        
    Returns:
        Dicionário com informações traduzidas
    """
    if target_lang == "pt":
        return dish_info
    
    translated = dish_info.copy()
    
    # Campos a traduzir
    text_fields = ["descricao", "tecnica", "beneficio_principal", "curiosidade_cientifica", "alerta_saude"]
    list_fields = ["ingredientes", "beneficios", "riscos"]
    
    try:
        # Traduzir campos de texto
        for field in text_fields:
            if field in translated and translated[field]:
                translated[field] = await translate_text(
                    translated[field], "pt", target_lang
                )
        
        # Traduzir listas
        for field in list_fields:
            if field in translated and translated[field]:
                translated_list = []
                for item in translated[field]:
                    translated_item = await translate_text(item, "pt", target_lang)
                    translated_list.append(translated_item)
                translated[field] = translated_list
        
        # Traduzir categoria
        if "category" in translated:
            ui_trans = get_ui_translations(target_lang)
            cat_map = {
                "vegano": ui_trans.get("vegan", "vegan"),
                "vegetariano": ui_trans.get("vegetarian", "vegetarian"),
                "proteína animal": ui_trans.get("animal_protein", "animal protein"),
            }
            translated["category"] = cat_map.get(translated["category"], translated["category"])
        
    except Exception as e:
        logger.error(f"Erro ao traduzir dish_info: {e}")
    
    return translated
