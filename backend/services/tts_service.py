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
    """Constroi texto natural e completo para o TTS ler.
    Inclui: nome, calorias, macros, ingredientes, beneficios, riscos,
    alergenos, alertas, curiosidade, noticias, verdade/mito, resumo premium."""
    parts = []
    
    nome = data.get("dish_display") or data.get("nome")
    if not nome:
        return ""
    
    parts.append(f"{nome}.")
    
    # Categoria
    categoria = data.get("category") or data.get("categoria")
    if categoria:
        parts.append(f"Categoria: {categoria}.")
    
    # Calorias e Macros
    nutrition = data.get("nutrition") or {}
    calorias = nutrition.get("calorias") or data.get("calorias_estimadas")
    if calorias:
        cal_str = str(calorias).replace("kcal", "").replace("cal", "").strip()
        parts.append(f"{cal_str} calorias por porcao.")
    
    macros = []
    if nutrition.get("proteinas"):
        macros.append(f"proteinas {nutrition['proteinas']}")
    if nutrition.get("carboidratos"):
        macros.append(f"carboidratos {nutrition['carboidratos']}")
    if nutrition.get("gorduras"):
        macros.append(f"gorduras {nutrition['gorduras']}")
    if nutrition.get("fibras"):
        macros.append(f"fibras {nutrition['fibras']}")
    if nutrition.get("sodio"):
        macros.append(f"sodio {nutrition['sodio']}")
    if macros:
        parts.append("Dados nutricionais: " + ", ".join(macros) + ".")
    
    # Ingredientes
    ingredientes = data.get("ingredientes") or []
    if ingredientes:
        parts.append("Ingredientes: " + ", ".join(ingredientes[:10]) + ".")
    
    # Alergenos - CRITICO para acessibilidade
    alergenos = data.get("alergenos") or {}
    contidos = [nome_al for nome_al, presente in alergenos.items() if presente]
    if contidos:
        parts.append(f"Atencao! Contem: {', '.join(contidos)}.")
    
    # Alertas personalizados
    alertas = data.get("alertas_personalizados") or []
    for alerta in alertas[:3]:
        msg = alerta.get("mensagem") or alerta.get("msg") or str(alerta)
        if isinstance(msg, str) and msg:
            parts.append(msg + ".")
    
    # Alertas premium (alergenos do perfil)
    premium = data.get("premium") or {}
    alertas_alergenos = premium.get("alertas_alergenos") or []
    for alerta in alertas_alergenos[:3]:
        msg = alerta.get("mensagem", "")
        if msg:
            parts.append(f"Alerta importante: {msg}")
    
    # Alertas de historico
    alertas_hist = premium.get("alertas_historico") or []
    for hist in alertas_hist[:2]:
        if isinstance(hist, dict):
            breve = hist.get("alerta_breve", "")
            if breve:
                parts.append(breve + ".")
            consumo = hist.get("alerta_consumo")
            if consumo and isinstance(consumo, dict):
                for sub_alert in consumo.get("alerts", [])[:2]:
                    txt = sub_alert.get("texto", "")
                    if txt:
                        parts.append(txt)
    
    # Beneficios
    beneficios = data.get("beneficios") or []
    if beneficios:
        parts.append("Beneficios: " + ". ".join(beneficios[:3]) + ".")
    
    # Riscos
    riscos = data.get("riscos") or []
    if riscos:
        parts.append("Riscos: " + ". ".join(riscos[:2]) + ".")
    
    # Curiosidade
    curiosidade = data.get("curiosidade") or data.get("curiosidade_cientifica") or ""
    if curiosidade:
        parts.append(f"Curiosidade: {curiosidade}")
    
    # Verdade ou Mito
    mito = data.get("mito_verdade")
    if mito and isinstance(mito, dict):
        afirmacao = mito.get("afirmacao", "")
        resposta = mito.get("resposta", "")
        explicacao = mito.get("explicacao", "")
        if afirmacao:
            parts.append(f"Verdade ou mito: {afirmacao}. {resposta}. {explicacao}")
    
    # Noticias
    noticias = data.get("noticias") or []
    if noticias:
        for noticia in noticias[:2]:
            if isinstance(noticia, str):
                parts.append(f"Noticia: {noticia}")
            elif isinstance(noticia, dict):
                txt = noticia.get("texto") or noticia.get("titulo", "")
                if txt:
                    parts.append(f"Noticia: {txt}")
    
    # Beneficio principal e alerta de saude (Premium MongoDB)
    benef_principal = data.get("beneficio_principal")
    if benef_principal:
        parts.append(f"Beneficio principal: {benef_principal}")
    
    alerta_saude = data.get("alerta_saude")
    if alerta_saude:
        parts.append(f"Alerta de saude: {alerta_saude}")
    
    return " ".join(parts)
