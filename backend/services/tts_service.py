"""SoulNutri - Servico de Text-to-Speech via OpenAI TTS"""

import os
import logging
from emergentintegrations.llm.openai import OpenAITextToSpeech

logger = logging.getLogger(__name__)


async def generate_dish_audio(dish_data: dict, voice: str = "alloy") -> bytes:
    """
    Gera audio MP3 descrevendo o prato identificado.
    
    Args:
        dish_data: Dados do prato (dish_display, nutrition, alergenos, etc.)
        voice: Voz do TTS (alloy ou onyx)
    
    Returns:
        bytes do MP3 ou None se falhar
    """
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        logger.error("[TTS] EMERGENT_LLM_KEY nao configurada")
        return None
    api_key = api_key.replace('\n', '').replace('\r', '').strip()
    
    # Montar texto descritivo do prato
    text = _build_dish_description(dish_data)
    
    if not text:
        return None
    
    try:
        tts = OpenAITextToSpeech(api_key=api_key)
        
        audio = await tts.generate_speech(
            text=text,
            model="tts-1",
            voice=voice,
            speed=0.95,
            response_format="mp3"
        )
        
        logger.info(f"[TTS] Audio gerado: {len(audio)//1024}KB, voz={voice}")
        return audio
        
    except Exception as e:
        logger.error(f"[TTS] Erro ao gerar audio: {e}")
        return None


def _build_dish_description(data: dict) -> str:
    """Constroi texto natural para o TTS ler"""
    parts = []
    
    nome = data.get("dish_display") or data.get("nome")
    if not nome:
        return ""
    
    parts.append(f"{nome}.")
    
    # Calorias
    nutrition = data.get("nutrition") or {}
    calorias = nutrition.get("calorias") or data.get("calorias_estimadas")
    if calorias:
        cal_str = str(calorias).replace("kcal", "").replace("cal", "").strip()
        parts.append(f"{cal_str} calorias por porcao.")
    
    # Macros
    macros = []
    if nutrition.get("proteinas"):
        macros.append(f"proteinas {nutrition['proteinas']}")
    if nutrition.get("carboidratos"):
        macros.append(f"carboidratos {nutrition['carboidratos']}")
    if nutrition.get("gorduras"):
        macros.append(f"gorduras {nutrition['gorduras']}")
    if macros:
        parts.append(", ".join(macros) + ".")
    
    # Alergenos - CRITICO para acessibilidade
    alergenos = data.get("alergenos") or {}
    contidos = [nome for nome, presente in alergenos.items() if presente]
    if contidos:
        parts.append(f"Atencao! Contem: {', '.join(contidos)}.")
    
    # Alertas personalizados
    alertas = data.get("alertas_personalizados") or []
    if alertas:
        for alerta in alertas[:2]:
            msg = alerta.get("mensagem") or alerta.get("msg") or str(alerta)
            if isinstance(msg, str) and msg:
                parts.append(msg + ".")
    
    # Categoria
    categoria = data.get("category") or data.get("categoria")
    if categoria:
        parts.append(f"Categoria: {categoria}.")
    
    return " ".join(parts)
