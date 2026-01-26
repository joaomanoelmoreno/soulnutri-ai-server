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
        "permission_denied": "Permissão negada. Toque para permitir.",
        "try_again": "Tentar novamente",
        "vegan": "vegano",
        "vegetarian": "vegetariano",
        "animal_protein": "proteína animal",
        "select_language": "Selecionar idioma",
        # Tutorial do Scanner
        "how_scanner_works": "Como usar o SoulNutri",
        "tutorial_step1_title": "Aponte e Fotografe",
        "tutorial_step1_desc": "Enquadre o prato na tela e toque para tirar uma foto. Em segundos você terá todas as informações.",
        "tutorial_step2_title": "Escolha Consciente",
        "tutorial_step2_desc": "Veja ingredientes, benefícios, alertas de alérgenos e muito mais. Tudo para você fazer a melhor escolha.",
        "tutorial_step3_title": "Seu Prato, Sua Escolha",
        "tutorial_step3_desc": "Monte seu prato ideal com informações completas. Saiba exatamente o que está comendo!",
        "skip": "Pular",
        "back": "Voltar",
        "next": "Próximo",
        "start_using": "Começar a usar",
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
        "permission_denied": "Permission denied. Tap to allow.",
        "try_again": "Try again",
        "vegan": "vegan",
        "vegetarian": "vegetarian",
        "animal_protein": "animal protein",
        "select_language": "Select language",
        # Scanner Tutorial
        "how_scanner_works": "How to use SoulNutri",
        "tutorial_step1_title": "Point and Snap",
        "tutorial_step1_desc": "Frame the dish on screen and tap to take a photo. In seconds you'll have all the information.",
        "tutorial_step2_title": "Informed Choice",
        "tutorial_step2_desc": "See ingredients, benefits, allergen alerts and more. Everything for you to make the best choice.",
        "tutorial_step3_title": "Your Plate, Your Choice",
        "tutorial_step3_desc": "Build your ideal plate with complete information. Know exactly what you're eating!",
        "skip": "Skip",
        "back": "Back",
        "next": "Next",
        "start_using": "Start using",
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
        "permission_denied": "Permiso denegado. Toque para permitir.",
        "try_again": "Intentar de nuevo",
        "vegan": "vegano",
        "vegetarian": "vegetariano",
        "animal_protein": "proteína animal",
        "select_language": "Seleccionar idioma",
        # Tutorial del Scanner
        "how_scanner_works": "Cómo funciona el Scanner",
        "tutorial_step1_title": "Scanner Automático",
        "tutorial_step1_desc": "Apunta a cualquier plato y descubre al instante ingredientes, beneficios y alertas de alérgenos.",
        "tutorial_step2_title": "Elección Consciente",
        "tutorial_step2_desc": "Ve si contiene gluten, lactosa u otros alérgenos. Descubre los beneficios de cada ingrediente para tu salud.",
        "tutorial_step3_title": "Tu Plato, Tu Elección",
        "tutorial_step3_desc": "Arma tu plato ideal con información completa. ¡Sabe exactamente lo que estás comiendo!",
        "skip": "Saltar",
        "back": "Atrás",
        "next": "Siguiente",
        "start_using": "Empezar a usar",
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
        "permission_denied": "Permission refusée. Appuyez pour autoriser.",
        "try_again": "Réessayer",
        "vegan": "végan",
        "vegetarian": "végétarien",
        "animal_protein": "protéine animale",
        "select_language": "Sélectionner la langue",
        # Tutoriel du Scanner
        "how_scanner_works": "Comment fonctionne le Scanner",
        "tutorial_step1_title": "Scanner Automatique",
        "tutorial_step1_desc": "Pointez vers n'importe quel plat et découvrez instantanément les ingrédients, bienfaits et alertes d'allergènes.",
        "tutorial_step2_title": "Choix Éclairé",
        "tutorial_step2_desc": "Voyez s'il contient du gluten, du lactose ou d'autres allergènes. Découvrez les bienfaits de chaque ingrédient pour votre santé.",
        "tutorial_step3_title": "Votre Assiette, Votre Choix",
        "tutorial_step3_desc": "Composez votre assiette idéale avec des informations complètes. Sachez exactement ce que vous mangez!",
        "skip": "Passer",
        "back": "Retour",
        "next": "Suivant",
        "start_using": "Commencer",
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
        "permission_denied": "Berechtigung verweigert. Tippen Sie zum Erlauben.",
        "try_again": "Erneut versuchen",
        "vegan": "vegan",
        "vegetarian": "vegetarisch",
        "animal_protein": "tierisches Protein",
        "select_language": "Sprache auswählen",
        # Scanner Tutorial
        "how_scanner_works": "Wie der Scanner funktioniert",
        "tutorial_step1_title": "Automatischer Scanner",
        "tutorial_step1_desc": "Zeigen Sie auf ein Gericht und entdecken Sie sofort Zutaten, Vorteile und Allergen-Warnungen.",
        "tutorial_step2_title": "Bewusste Wahl",
        "tutorial_step2_desc": "Sehen Sie, ob es Gluten, Laktose oder andere Allergene enthält. Entdecken Sie die Vorteile jeder Zutat für Ihre Gesundheit.",
        "tutorial_step3_title": "Ihr Teller, Ihre Wahl",
        "tutorial_step3_desc": "Stellen Sie Ihren idealen Teller mit vollständigen Informationen zusammen. Wissen Sie genau, was Sie essen!",
        "skip": "Überspringen",
        "back": "Zurück",
        "next": "Weiter",
        "start_using": "Starten",
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
        "permission_denied": "权限被拒绝。点击以允许。",
        "try_again": "重试",
        "vegan": "纯素",
        "vegetarian": "素食",
        "animal_protein": "动物蛋白",
        "select_language": "选择语言",
        # 扫描器教程
        "how_scanner_works": "扫描器如何工作",
        "tutorial_step1_title": "自动扫描",
        "tutorial_step1_desc": "指向任何菜品，即时了解成分、健康益处和过敏原警告。",
        "tutorial_step2_title": "明智选择",
        "tutorial_step2_desc": "查看是否含有麸质、乳糖或其他过敏原。了解每种成分对您健康的益处。",
        "tutorial_step3_title": "您的餐盘，您的选择",
        "tutorial_step3_desc": "用完整信息组合理想餐盘。清楚知道您在吃什么！",
        "skip": "跳过",
        "back": "返回",
        "next": "下一步",
        "start_using": "开始使用",
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
