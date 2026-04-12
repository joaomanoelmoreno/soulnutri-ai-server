"""SoulNutri - Servico de Text-to-Speech
Scan (buffet): gTTS gratuito, rapido
Prato Completo (premium): OpenAI Shimmer, voz natural"""

import io
import logging

logger = logging.getLogger(__name__)


async def generate_dish_audio(dish_data: dict, voice: str = "alloy", premium_tts: bool = False) -> bytes:
    """
    Gera audio MP3 descrevendo o prato.
    premium_tts=False: gTTS (gratuito, scan no buffet)
    premium_tts=True: OpenAI Shimmer (premium, Prato Completo)
    """
    text = _build_dish_description(dish_data)
    if not text:
        return None

    if premium_tts:
        return await _generate_openai_tts(text)
    else:
        return await _generate_gtts(text)


async def _generate_openai_tts(text: str) -> bytes:
    """OpenAI TTS - voz Shimmer 1.0x para Prato Completo premium"""
    try:
        from emergentintegrations.llm.openai import OpenAITextToSpeech
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        key = os.getenv("OPENAI_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        if not key:
            logger.warning("[TTS] Sem key OpenAI/Emergent, fallback para gTTS")
            return await _generate_gtts(text)
        
        tts = OpenAITextToSpeech(api_key=key)
        audio_bytes = await tts.generate_speech(
            text=text[:4096],
            model="tts-1",
            voice="shimmer",
            speed=1.0,
            response_format="mp3"
        )
        logger.info(f"[TTS] OpenAI Shimmer: {len(audio_bytes)//1024}KB")
        return audio_bytes
    except Exception as e:
        logger.error(f"[TTS] OpenAI falhou, fallback gTTS: {e}")
        return await _generate_gtts(text)


async def _generate_gtts(text: str) -> bytes:
    """gTTS gratuito - para scan rapido no buffet"""
    try:
        from gtts import gTTS
        
        tts = gTTS(text=text, lang='pt-br', slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)
        
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(mp3_buffer)
            audio = audio.speedup(playback_speed=1.35, chunk_size=80, crossfade=25)
            out = io.BytesIO()
            audio.export(out, format="mp3")
            out.seek(0)
            result = out.read()
            logger.info(f"[TTS] gTTS 1.35x: {len(result)//1024}KB")
        except Exception:
            mp3_buffer.seek(0)
            result = mp3_buffer.read()
            logger.info(f"[TTS] gTTS 1.0x: {len(result)//1024}KB")
        
        return result
    except Exception as e:
        logger.error(f"[TTS] gTTS erro: {e}")
        return None


def _build_dish_description(data: dict) -> str:
    """Constroi texto para o TTS ler."""
    parts = []
    
    nome = data.get("dish_display") or data.get("nome")
    if not nome:
        return ""
    
    parts.append(f"{nome}.")
    
    # Calorias e Macros
    nutrition = data.get("nutrition") or {}
    calorias = nutrition.get("calorias") or data.get("calorias_estimadas")
    if calorias:
        cal_str = str(calorias).replace("kcal", "").replace("cal", "").strip()
        parts.append(f"{cal_str} calorias por porção.")
    
    macros = []
    if nutrition.get("proteinas"):
        macros.append(f"proteínas {nutrition['proteinas']}")
    if nutrition.get("carboidratos"):
        macros.append(f"carboidratos {nutrition['carboidratos']}")
    if nutrition.get("gorduras"):
        macros.append(f"gorduras {nutrition['gorduras']}")
    if macros:
        parts.append(", ".join(macros) + ".")
    
    # Ingredientes
    ingredientes = data.get("ingredientes") or []
    if ingredientes:
        parts.append("Ingredientes: " + ", ".join(ingredientes[:8]) + ".")
    
    # Alergenos - CRITICO para acessibilidade
    alergenos = data.get("alergenos") or {}
    contidos = [nome_al for nome_al, presente in alergenos.items() if presente]
    if contidos:
        parts.append(f"Atenção! Contém: {', '.join(contidos)}.")
    
    # Alertas personalizados
    alertas = data.get("alertas_personalizados") or []
    for alerta in alertas[:3]:
        msg = alerta.get("mensagem") or alerta.get("msg") or str(alerta)
        if isinstance(msg, str) and msg:
            parts.append(msg + ".")
    
    # Alertas premium
    premium = data.get("premium") or {}
    for alerta in (premium.get("alertas_alergenos") or [])[:2]:
        msg = alerta.get("mensagem", "")
        if msg:
            parts.append(f"Alerta: {msg}")
    
    # Beneficios
    beneficios = data.get("beneficios") or []
    if beneficios:
        parts.append("Benefícios: " + ". ".join(beneficios[:3]) + ".")
    
    # Riscos
    riscos = data.get("riscos") or []
    if riscos:
        parts.append("Riscos: " + ". ".join(riscos[:2]) + ".")
    
    # Curiosidade
    curiosidade = data.get("curiosidade") or ""
    if curiosidade:
        parts.append(f"Curiosidade: {curiosidade}")
    
    # Verdade ou Mito
    mito = data.get("mito_verdade")
    if mito and isinstance(mito, dict):
        frase = mito.get("mito") or mito.get("afirmacao") or mito.get("frase", "")
        resposta = mito.get("resposta") or mito.get("verdade", "")
        if frase:
            parts.append(f"Verdade ou mito: {frase}. {resposta}")
    
    # Noticias
    noticias = data.get("noticias") or []
    for noticia in noticias[:2]:
        if isinstance(noticia, str):
            parts.append(f"Notícia: {noticia}")
        elif isinstance(noticia, dict):
            txt = noticia.get("texto") or noticia.get("titulo", "")
            if txt:
                parts.append(f"Notícia: {txt}")
    
    # Alerta de saude
    alerta_saude = data.get("alerta_saude")
    if alerta_saude:
        parts.append(f"Alerta de saúde: {alerta_saude}")
    
    return " ".join(parts)
