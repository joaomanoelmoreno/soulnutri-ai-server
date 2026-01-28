"""
SoulNutri - Serviço de IA Genérica - DESABILITADO PARA ECONOMIZAR CRÉDITOS
=============================================================================
TODAS as funções retornam erro/vazio para não consumir créditos.
Para reativar, restaure o arquivo generic_ai.py.BACKUP_COM_IA
"""

import logging

logger = logging.getLogger(__name__)

# Mensagem padrão de economia
ECONOMIA_MSG = "IA desabilitada para economizar créditos. Use dados locais."


async def identify_unknown_dish(image_bytes: bytes) -> dict:
    """DESABILITADO - Usa índice local"""
    logger.info("[ECONOMIA] identify_unknown_dish BLOQUEADO - sem créditos")
    return {
        "ok": False, 
        "error": ECONOMIA_MSG,
        "disabled": True
    }


async def enrich_dish_info(dish_name: str, ingredients: list = None) -> dict:
    """DESABILITADO - Use local_dish_updater"""
    logger.info("[ECONOMIA] enrich_dish_info BLOQUEADO - sem créditos")
    return {
        "ok": False, 
        "error": ECONOMIA_MSG,
        "disabled": True
    }


async def search_ingredient_news(ingredient: str) -> dict:
    """DESABILITADO - Sem notícias por enquanto"""
    logger.info("[ECONOMIA] search_ingredient_news BLOQUEADO - sem créditos")
    return {
        "ok": False, 
        "error": ECONOMIA_MSG,
        "disabled": True,
        "noticias": []
    }


async def identify_multiple_items(image_bytes: bytes) -> dict:
    """DESABILITADO - Usa índice local"""
    logger.info("[ECONOMIA] identify_multiple_items BLOQUEADO - sem créditos")
    return {
        "ok": False, 
        "error": ECONOMIA_MSG,
        "disabled": True,
        "itens": []
    }


async def fix_dish_data_with_ai(image_bytes: bytes, current_info: dict) -> dict:
    """DESABILITADO - Use local_dish_updater"""
    logger.info("[ECONOMIA] fix_dish_data_with_ai BLOQUEADO - sem créditos")
    return {
        "ok": False, 
        "error": ECONOMIA_MSG,
        "disabled": True
    }


async def batch_fix_dishes(slugs: list, max_concurrent: int = 3) -> dict:
    """DESABILITADO - Use atualização local em massa"""
    logger.info("[ECONOMIA] batch_fix_dishes BLOQUEADO - sem créditos")
    return {
        "ok": False, 
        "error": ECONOMIA_MSG,
        "disabled": True,
        "results": []
    }


async def regenerate_dish_info_from_name(dish_name: str, old_info: dict = None) -> dict:
    """DESABILITADO - Use local_dish_updater.atualizar_prato_local()"""
    logger.info("[ECONOMIA] regenerate_dish_info_from_name BLOQUEADO - sem créditos")
    return {
        "ok": False, 
        "error": ECONOMIA_MSG,
        "disabled": True
    }


async def analyze_dish_for_correction(image_bytes: bytes, dish_info: dict) -> dict:
    """DESABILITADO - Use correção manual"""
    logger.info("[ECONOMIA] analyze_dish_for_correction BLOQUEADO - sem créditos")
    return {
        "ok": False,
        "error": ECONOMIA_MSG,
        "disabled": True
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE UTILIDADE - MANTIDAS (não consomem créditos)
# ═══════════════════════════════════════════════════════════════════════════════

def get_ai_status() -> dict:
    """Retorna status do serviço de IA"""
    return {
        "enabled": False,
        "reason": "Desabilitado para economizar créditos",
        "restore_file": "generic_ai.py.BACKUP_COM_IA"
    }
