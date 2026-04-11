"""
SoulNutri - Serviço Gemini 2.5 Flash para Identificação de Alimentos
====================================================================
"""
import os

def is_gemini_flash_available() -> bool:
    """Verifica se o Gemini Flash está disponível"""
    try:
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        return bool(api_key)
    except Exception:
        return False

def get_gemini_flash_status() -> dict:
    """Retorna status do Gemini Flash"""
    available = is_gemini_flash_available()
    return {"available": available, "model": "gemini-2.0-flash-lite" if available else None}

"""
OBJETIVO: Identificar pratos com alta precisão e retornar dados completos
- Nome do prato
- Ingredientes
- Informações nutricionais (calorias, macros)
- Alérgenos detectados
- Alertas personalizados baseados no perfil do usuário

PERFORMANCE: ~340ms (tempo até primeira resposta)
CUSTO: ~$0.075/1M tokens input, $0.30/1M tokens output
FREE TIER: 1.500 requisições/dia grátis
"""

import os
import json
import tempfile
import time
import logging
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT OTIMIZADO PARA GEMINI 2.5 FLASH
# Foco: Precisão, velocidade e dados completos em UM único request
# ═══════════════════════════════════════════════════════════════════════════════

# PROMPT OTIMIZADO - Melhor precisão mantendo velocidade
SYSTEM_PROMPT_FLASH = """Identifique o prato na imagem. Linguiça/salsicha/embutidos=proteína animal. Retorne APENAS JSON:
{"nome":"Nome do prato","cat":"v|veg|p","kcal":XXX,"prot":XX,"carb":XX,"gord":XX,"alerg":["gluten","lactose"],"score":0.9,"ing":["ingrediente1","ingrediente2","ingrediente3"]}
cat:v=vegano,veg=vegetariano,p=proteína animal. score:confiança 0-1. alerg:apenas presentes. ing:3-5 ingredientes visíveis. Porção ~150g."""

# Prompt para enriquecimento Premium (segunda chamada, background)
ENRICH_TEMPLATE_PRE = 'Dado o prato "'
ENRICH_TEMPLATE_MID = '" com ingredientes ['
ENRICH_TEMPLATE_POST = """], retorne APENAS JSON válido com os campos: benef (3 benefícios nutricionais reais), riscos (2 riscos ESPECÍFICOS com dados concretos), curios (1 curiosidade científica), combo (2 combinações que potencializam), noticias (1-2 alertas recentes de saúde/nutrição sobre ingredientes). Formato: {"benef":["...","...","..."],"riscos":["...","..."],"curios":"...","combo":["...","..."],"noticias":["..."]}"""

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PARA ALERTAS PERSONALIZADOS (segunda etapa, se necessário)
# ═══════════════════════════════════════════════════════════════════════════════

PROMPT_ALERTAS_PERSONALIZADOS = """Com base nas informações do prato e no perfil do usuário, gere alertas personalizados.

PRATO: {prato_nome}
INGREDIENTES: {ingredientes}
ALÉRGENOS DETECTADOS: {alergenos}
CATEGORIA: {categoria}
CALORIAS: {calorias}

PERFIL DO USUÁRIO:
- Nome: {usuario_nome}
- Alergias: {alergias}
- Restrições: {restricoes}
- Objetivo: {objetivo}
- Meta calórica diária: {meta_calorica}

GERE ALERTAS AMIGÁVEIS E ÚTEIS:
1. Se o prato contém algo que o usuário não pode comer, ALERTE
2. Se o prato é muito calórico para o objetivo, SUGIRA moderação
3. Se o prato é adequado, ELOGIE a escolha

Tom: Amigável, como um nutricionista cuidadoso falando com um paciente.
Exemplo: "Olá João, este prato parece ter camarão. Você mencionou alergia a frutos do mar - confirme com o atendente antes de servir."

RETORNE JSON:
{
    "alertas": [
        {
            "tipo": "alergia|restricao|calorico|positivo",
            "severidade": "alta|media|baixa",
            "mensagem": "Mensagem personalizada para o usuário",
            "icone": "⚠️|🚫|⚡|✅"
        }
    ],
    "mensagem_geral": "Resumo geral para o usuário"
}"""


async def identify_dish_gemini_flash(
    image_bytes: bytes,
    user_profile: Optional[Dict] = None,
    restaurant: Optional[str] = None
) -> Dict:
    """
    Identifica um prato usando Gemini Flash.
    PRIORIDADE: Google API (rápido ~300ms, barato) -> Emergent Key (fallback ~5s)
    
    Performance esperada:
    - Google API: 200-500ms ✅
    - Emergent Key: 3000-8000ms (fallback)
    """
    from PIL import Image
    from google import genai
    import io
    
    start_time = time.time()
    
    try:
        # ═══════════════════════════════════════════════════════════════════
        # OTIMIZAÇÃO DE IMAGEM: Balanço entre qualidade e velocidade
        # Imagem menor = upload mais rápido = resposta mais rápida
        # ═══════════════════════════════════════════════════════════════════
        img = Image.open(io.BytesIO(image_bytes))
        
        # 384px é suficiente para identificação e mais rápido que 512px
        max_size = 384
        ratio = max_size / max(img.size)
        if ratio < 1:
            img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.LANCZOS)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # JPEG quality 65 é suficiente para identificação
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=65)
        img_bytes = buffer.getvalue()
        
        prep_time = (time.time() - start_time) * 1000
        logger.info(f"[GeminiFlash] Imagem preparada em {prep_time:.0f}ms ({len(img_bytes)/1024:.1f}KB)")
        
        # ═══════════════════════════════════════════════════════════════════
        # CHAMAR GEMINI - Google API primeiro (rápido), Emergent como fallback
        # ═══════════════════════════════════════════════════════════════════
        
        response_text = None
        source_used = None
        api_time_ms = 0
        
        prompt = f"""{SYSTEM_PROMPT_FLASH}

Identifique este prato. O que você vê na imagem? Seja preciso."""
        
        # ═══════════════════════════════════════════════════════════════════
        # OPÇÃO 1: Google API direta (PREFERIDO - rápido e barato)
        # Esperado: 200-500ms
        # ═══════════════════════════════════════════════════════════════════
        google_key = os.environ.get('GOOGLE_API_KEY')
        if google_key:
            # Usar apenas o modelo mais rápido primeiro
            try:
                client = genai.Client(api_key=google_key)
                
                api_start = time.time()
                response = client.models.generate_content(
                    model='gemini-2.0-flash-lite',
                    contents=[
                        prompt,
                        genai.types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                    ]
                )
                api_time_ms = (time.time() - api_start) * 1000
                
                response_text = response.text.strip()
                source_used = "google_api"
                logger.info(f"[GeminiFlash] ✅ GOOGLE API respondeu em {api_time_ms:.0f}ms")
                
            except Exception as e:
                error_str = str(e)
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                    logger.warning(f"[GeminiFlash] ⚠️ Cota Google ESGOTADA - usando fallback Emergent...")
                else:
                    logger.warning(f"[GeminiFlash] Google API erro: {error_str[:80]}")
        
        # ═══════════════════════════════════════════════════════════════════
        # OPÇÃO 2: Emergent LLM Key (FALLBACK - mais lento mas confiável)
        # Esperado: 3000-8000ms
        # ═══════════════════════════════════════════════════════════════════
        if response_text is None:
            emergent_key = os.environ.get('EMERGENT_LLM_KEY')
            if emergent_key:
                try:
                    from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
                    
                    # Salvar imagem temporária
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=70)
                    
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        tmp_file.write(buffer.getvalue())
                        tmp_path = tmp_file.name
                    
                    try:
                        chat = LlmChat(
                            api_key=emergent_key,
                            session_id=f"sn-{int(time.time())}",
                            system_message=SYSTEM_PROMPT_FLASH
                        ).with_model("gemini", "gemini-2.0-flash-lite")
                        
                        image_file = FileContentWithMimeType(
                            file_path=tmp_path,
                            mime_type="image/jpeg"
                        )
                        
                        user_message = UserMessage(
                            text="Identifique este prato. O que você vê na imagem? Seja preciso.",
                            file_contents=[image_file]
                        )
                        
                        api_start = time.time()
                        response = await chat.send_message(user_message)
                        api_time_ms = (time.time() - api_start) * 1000
                        
                        response_text = response.strip()
                        source_used = "emergent_fallback"
                        logger.info(f"[GeminiFlash] ⚠️ EMERGENT FALLBACK respondeu em {api_time_ms:.0f}ms (mais lento)")
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                            
                except Exception as e:
                    logger.error(f"[GeminiFlash] Emergent LLM também falhou: {e}")
        
        if response_text is None:
            return {"ok": False, "error": "Todos os serviços de IA indisponíveis"}
        
        logger.info(f"[GeminiFlash] Resposta via {source_used}: {response_text[:200]}...")
        
        # ═══════════════════════════════════════════════════════════════════
        # PARSE DA RESPOSTA JSON
        # ═══════════════════════════════════════════════════════════════════
        response_clean = response_text.strip()
        
        # Remover marcadores de código se presentes
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        response_clean = response_clean.strip()
        
        try:
            result = json.loads(response_clean)
        except json.JSONDecodeError as e:
            logger.error(f"[GeminiFlash] Erro ao parsear JSON: {e}")
            logger.error(f"[GeminiFlash] Resposta raw: {response_text[:500]}")
            return {
                "ok": False,
                "error": "Erro ao processar resposta da IA",
                "raw_response": response_text[:500]
            }
        
        # ═══════════════════════════════════════════════════════════════════
        # EXPANDIR RESULTADO COMPACTO
        # {"nome":"X","cat":"p","kcal":300,"prot":25,"carb":10,"gord":15,"alerg":["gluten"]}
        # ═══════════════════════════════════════════════════════════════════
        cat_expand = {"v": "vegano", "veg": "vegetariano", "p": "proteína animal"}
        
        expanded = {
            "ok": True,
            "source": "gemini_flash",
            "nome": result.get("nome", "Não identificado"),
            "categoria": cat_expand.get(result.get("cat"), result.get("cat", "")),
            "confianca": "alta",
            "score": 0.90,
            "nutricao": {
                "calorias": f"{result.get('kcal', 0)} kcal",
                "proteinas": f"{result.get('prot', 0)}g",
                "carboidratos": f"{result.get('carb', 0)}g",
                "gorduras": f"{result.get('gord', 0)}g"
            },
            "alergenos": {},
            "ingredientes": result.get("ing", []),
            "beneficios": [],
            "riscos": [],
            "curiosidade": "",
            "combinacoes": [],
            "noticias": []
        }
        
        # Converter lista de alérgenos para dict
        alerg_list = result.get("alerg", [])
        if isinstance(alerg_list, list):
            for a in ["gluten", "lactose", "ovo", "castanhas", "frutos_mar", "soja"]:
                expanded["alergenos"][a] = a in alerg_list or a.replace("_", " ") in str(alerg_list).lower()
        
        result = expanded
        
        # ═══════════════════════════════════════════════════════════════════
        # ENRIQUECER RESULTADO
        # ═══════════════════════════════════════════════════════════════════
        result["ok"] = True
        result["source"] = "gemini_flash"
        
        # Tempo total
        total_time = (time.time() - start_time) * 1000
        result["tempo_processamento_ms"] = round(total_time, 2)
        
        # Emojis de confiança e categoria
        conf_map = {"alta": "🟢", "média": "🟡", "baixa": "🔴"}
        result["confidence_emoji"] = conf_map.get(result.get("confianca", "baixa"), "🔴")
        
        cat_map = {"vegano": "🌱", "vegetariano": "🥬", "proteína animal": "🍖"}
        result["category_emoji"] = cat_map.get(result.get("categoria", ""), "🍽️")
        
        # ═══════════════════════════════════════════════════════════════════
        # ALERTAS PERSONALIZADOS (se tiver perfil Premium)
        # ═══════════════════════════════════════════════════════════════════
        if user_profile:
            try:
                alertas = gerar_alertas_personalizados(result, user_profile)
                if alertas:
                    result["alertas_personalizados"] = alertas
            except Exception as e:
                logger.warning(f"[GeminiFlash] Erro ao gerar alertas: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"[GeminiFlash] Erro geral: {e}")
        return {"ok": False, "error": str(e)}


def gerar_alertas_personalizados(result: dict, profile: dict) -> list:
    """Gera alertas baseados no perfil do usuário"""
    alertas = []
    try:
        restricoes = profile.get("restricoes", [])
        alergenos = result.get("alergenos", {})
        for r in restricoes:
            r_lower = r.lower().replace(" ", "_")
            if alergenos.get(r_lower):
                alertas.append(f"Contém {r}")
    except Exception:
        pass
    return alertas


# ═══════════════════════════════════════════════════════════════════════════════
# ENRIQUECIMENTO PREMIUM (chamada em background, não bloqueia o scan)
# ═══════════════════════════════════════════════════════════════════════════════
async def enrich_dish_gemini(nome: str, ingredientes: list) -> Dict:
    """Enriquece o prato com dados Premium via Gemini (background)."""
    import time as _time
    start = _time.time()
    
    prompt = ENRICH_TEMPLATE_PRE + nome + ENRICH_TEMPLATE_MID + (", ".join(ingredientes) if ingredientes else "não informados") + ENRICH_TEMPLATE_POST
    
    response_text = None
    
    # Tentar Google API primeiro
    google_key = os.environ.get('GOOGLE_API_KEY')
    if google_key:
        try:
            from google import genai
            client = genai.Client(api_key=google_key)
            response = client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=[prompt]
            )
            response_text = response.text.strip()
        except Exception as e:
            logger.warning(f"[Enrich] Google API erro: {str(e)[:60]}")
    
    # Fallback: Emergent Key
    if response_text is None:
        emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        if emergent_key:
            try:
                from emergentintegrations.llm.chat import LlmChat, UserMessage
                chat = LlmChat(
                    api_key=emergent_key,
                    session_id=f"enrich-{int(_time.time())}",
                    system_message="Retorne apenas JSON válido."
                ).with_model("gemini", "gemini-2.0-flash-lite")
                msg = UserMessage(text=prompt)
                resp = await chat.send_message(msg)
                response_text = resp.strip() if resp else None
            except Exception as e:
                logger.warning(f"[Enrich] Emergent erro: {str(e)[:60]}")
    
    if not response_text:
        return {}
    
    try:
        import json, re
        clean = response_text
        if '```' in clean:
            clean = re.sub(r'```(?:json)?\s*', '', clean).replace('```', '')
        clean = clean.strip()
        logger.info(f"[Enrich] Raw response: {clean[:200]}")
        parsed = json.loads(clean)
        
        # Normalizar: o Gemini pode retornar com nomes curtos ou longos
        beneficios = parsed.get("benef") or parsed.get("beneficios") or []
        riscos = parsed.get("riscos") or []
        curiosidade = parsed.get("curios") or parsed.get("curiosidade") or ""
        combinacoes = parsed.get("combo") or parsed.get("combinacoes") or []
        noticias = parsed.get("noticias") or []
        
        elapsed = (_time.time() - start) * 1000
        logger.info(f"[Enrich] Premium data para '{nome}' em {elapsed:.0f}ms")
        return {
            "beneficios": beneficios,
            "riscos": riscos,
            "curiosidade": curiosidade,
            "combinacoes": combinacoes,
            "noticias": noticias
        }
    except Exception as e:
        logger.warning(f"[Enrich] Parse erro: {str(e)[:100]} | Raw: {response_text[:100] if response_text else 'None'}")
        return {}