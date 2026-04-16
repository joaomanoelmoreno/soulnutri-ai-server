"""SoulNutri - Servico de Text-to-Speech
Scan (buffet): gTTS gratuito, rapido
Prato Completo (premium): OpenAI TTS com fallback para gTTS

Objetivos desta versao:
- Forcar texto em portugues do Brasil natural
- Evitar leitura de unidades em ingles (ex.: "grams", "cals")
- Tratar estruturas heterogeneas (strings, dicts, arrays)
- Manter baixo custo e fallback seguro
"""

import io
import logging
import re
from typing import Any, Iterable, Optional

logger = logging.getLogger(__name__)


async def generate_dish_audio(
    dish_data: dict,
    voice: str = "nova",
    premium_tts: bool = False,
) -> Optional[bytes]:
    """
    Gera audio MP3 descrevendo o prato.

    Regras:
    - Sempre tenta OpenAI primeiro para maior naturalidade/consistencia
    - Se falhar, cai para gTTS em pt-BR
    - Normaliza o texto antes de sintetizar
    """
    text = _build_dish_description(dish_data)
    if not text:
        return None

    text = _normalize_text_for_tts(text)

    result = await _generate_openai_tts(text=text, voice=voice)
    if result:
        return result

    return await _generate_gtts(text)


async def _generate_openai_tts(text: str, voice: str = "nova") -> Optional[bytes]:
    """OpenAI TTS - tentativa principal para voz mais natural"""
    try:
        from emergentintegrations.llm.openai import OpenAITextToSpeech
        import os
        from dotenv import load_dotenv

        load_dotenv()

        key = os.getenv("OPENAI_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        if not key:
            logger.warning("[TTS] Sem key OpenAI/Emergent, fallback para gTTS")
            return await _generate_gtts(text)

        safe_voice = voice or "nova"
        safe_text = _normalize_text_for_tts(text)[:4096]

        tts = OpenAITextToSpeech(api_key=key)
        audio_bytes = await tts.generate_speech(
            text=safe_text,
            model="tts-1",
            voice=safe_voice,
            speed=0.95,
            response_format="mp3",
        )

        logger.info(f"[TTS] OpenAI voice={safe_voice}: {len(audio_bytes)//1024}KB")
        return audio_bytes

    except Exception as e:
        logger.error(f"[TTS] OpenAI falhou, fallback gTTS: {e}")
        return await _generate_gtts(text)


async def _generate_gtts(text: str) -> Optional[bytes]:
    """gTTS gratuito - fallback em pt-BR"""
    try:
        from gtts import gTTS

        safe_text = _normalize_text_for_tts(text)

        tts = gTTS(text=safe_text, lang="pt-br", slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_mp3(mp3_buffer)
            audio = audio.speedup(playback_speed=1.08, chunk_size=90, crossfade=20)

            out = io.BytesIO()
            audio.export(out, format="mp3")
            out.seek(0)
            result = out.read()
            logger.info(f"[TTS] gTTS 1.08x: {len(result)//1024}KB")
        except Exception:
            mp3_buffer.seek(0)
            result = mp3_buffer.read()
            logger.info(f"[TTS] gTTS 1.0x: {len(result)//1024}KB")

        return result

    except Exception as e:
        logger.error(f"[TTS] gTTS erro: {e}")
        return None


def _safe_str(value: Any) -> str:
    """Converte qualquer valor em string legível para TTS."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value).strip()
    if isinstance(value, dict):
        for key in ("mensagem", "msg", "texto", "titulo", "nome", "label", "value"):
            if key in value and value.get(key):
                return _safe_str(value.get(key))
        return ""
    if isinstance(value, (list, tuple, set)):
        return ", ".join([s for s in (_safe_str(v) for v in value) if s])
    return str(value).strip()


def _safe_list(items: Any) -> list[str]:
    """Normaliza listas heterogeneas em lista de strings limpas."""
    if not items:
        return []
    if not isinstance(items, (list, tuple, set)):
        items = [items]

    result = []
    for item in items:
        text = _safe_str(item)
        if text:
            result.append(text)
    return result


def _strip_unit_prefix(value: Any) -> str:
    """Limpa unidades curtas para depois verbalizar em portugues."""
    text = _safe_str(value)
    if not text:
        return ""
    text = text.replace("kcal", "").replace("cal", "").strip()
    text = re.sub(r"\bg\b", "", text).strip()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_text_for_tts(text: str) -> str:
    """Converte texto para um formato mais natural em pt-BR."""
    if not text:
        return ""

    normalized = f" {text} "

    replacements = [
        ("kcal", " calorias "),
        (" kcal ", " calorias "),
        (" cal ", " calorias "),
        (" carbs ", " carboidratos "),
        (" protein ", " proteína "),
        (" proteins ", " proteínas "),
        (" fat ", " gordura "),
        (" fats ", " gorduras "),
        (" grams ", " gramas "),
        (" gram ", " grama "),
        (" mg ", " miligramas "),
        (" kg ", " quilogramas "),
        (" mcg ", " microgramas "),
        (" g ", " gramas "),
        (" cals ", " calorias "),
    ]

    for old, new in replacements:
        normalized = normalized.replace(old, new)

    # Corrigir padrões numéricos comuns
    normalized = re.sub(r"(\d+)\s*g\b", r"\1 gramas", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(\d+)\s*kcal\b", r"\1 calorias", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(\d+)\s*cal\b", r"\1 calorias", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(\d+)\s*mg\b", r"\1 miligramas", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(\d+)\s*kg\b", r"\1 quilogramas", normalized, flags=re.IGNORECASE)

    # Limpeza final
    normalized = normalized.replace("gramas gramas", "gramas")
    normalized = normalized.replace("calorias calorias", "calorias")
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized


def _build_macro_sentence(label: str, value: Any) -> str:
    cleaned = _strip_unit_prefix(value)
    if not cleaned:
        return ""
    return f"{cleaned} gramas de {label}"


def _build_dish_description(data: dict) -> str:
    """Constroi texto para o TTS ler em pt-BR natural."""
    parts: list[str] = []

    nome = _safe_str(data.get("dish_display") or data.get("nome"))
    if not nome:
        return ""

    parts.append(f"{nome}.")

    # Calorias e macros
    nutrition = data.get("nutrition") or {}
    calorias = nutrition.get("calorias") or data.get("calorias_estimadas")
    calorias_txt = _strip_unit_prefix(calorias)
    if calorias_txt:
        parts.append(f"{calorias_txt} calorias por porção.")

    macros = []
    prot = _build_macro_sentence("proteína", nutrition.get("proteinas"))
    carb = _build_macro_sentence("carboidratos", nutrition.get("carboidratos"))
    gord = _build_macro_sentence("gorduras", nutrition.get("gorduras"))

    if prot:
        macros.append(prot)
    if carb:
        macros.append(carb)
    if gord:
        macros.append(gord)

    if macros:
        parts.append("Macronutrientes: " + ", ".join(macros) + ".")

    # Ingredientes
    ingredientes = _safe_list(data.get("ingredientes"))[:8]
    if ingredientes:
        parts.append("Ingredientes: " + ", ".join(ingredientes) + ".")

    # Alergenos - critico para acessibilidade
    alergenos = data.get("alergenos") or {}
    if isinstance(alergenos, dict):
        contidos = [_safe_str(nome_al) for nome_al, presente in alergenos.items() if presente]
        contidos = [c for c in contidos if c]
        if contidos:
            parts.append(f"Atenção. Contém: {', '.join(contidos)}.")

    # Alertas personalizados
    for alerta in _safe_list(data.get("alertas_personalizados"))[:3]:
        parts.append(f"{alerta}.")

    # Alertas premium
    premium = data.get("premium") or {}
    if isinstance(premium, dict):
        for alerta in _safe_list(premium.get("alertas_alergenos"))[:2]:
            parts.append(f"Alerta: {alerta}.")

    # Beneficios
    beneficios = _safe_list(data.get("beneficios"))[:3]
    if beneficios:
        parts.append("Benefícios: " + ". ".join(beneficios) + ".")

    # Riscos
    riscos = _safe_list(data.get("riscos"))[:2]
    if riscos:
        parts.append("Riscos: " + ". ".join(riscos) + ".")

    # Curiosidade
    curiosidade = _safe_str(data.get("curiosidade"))
    if curiosidade:
        parts.append(f"Curiosidade: {curiosidade}.")

    # Combinacoes
    combinacoes = _safe_list(data.get("combinacoes"))[:3]
    if combinacoes:
        parts.append("Combinações que potencializam esta refeição: " + ". ".join(combinacoes) + ".")

    # Verdade ou mito
    mito = data.get("mito_verdade")
    if isinstance(mito, dict):
        frase = _safe_str(mito.get("mito") or mito.get("afirmacao") or mito.get("frase"))
        resposta = _safe_str(mito.get("resposta") or mito.get("verdade"))
        if frase:
            if resposta:
                parts.append(f"Verdade ou mito: {frase}. {resposta}.")
            else:
                parts.append(f"Verdade ou mito: {frase}.")

    # Noticias
    noticias = data.get("noticias") or []
    for noticia in _safe_list(noticias)[:2]:
        parts.append(f"Notícia: {noticia}.")

    # Alerta de saude
    alerta_saude = _safe_str(data.get("alerta_saude"))
    if alerta_saude:
        parts.append(f"Alerta de saúde: {alerta_saude}.")

    text = " ".join(part.strip() for part in parts if part and part.strip())
    return _normalize_text_for_tts(text)
