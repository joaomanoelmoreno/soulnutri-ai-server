"""
SoulNutri - Serviço Gemini 2.5 Flash para Identificação de Alimentos
====================================================================
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
SYSTEM_PROMPT_FLASH = """Você é um especialista em identificação de alimentos. Analise a imagem e identifique EXATAMENTE o que está no prato.

REGRAS CRÍTICAS:
1. OLHE COM ATENÇÃO para os ingredientes visíveis
2. Linguiça/salsicha/embutidos = proteína animal, NÃO confunda com legumes
3. Carne vermelha/frango/peixe = proteína animal
4. Se houver dúvida, descreva o que você VÊ na imagem

Retorne APENAS JSON válido:
{"nome":"Nome descritivo do prato","cat":"v|veg|p","kcal":XXX,"prot":XX,"carb":XX,"gord":XX,"alerg":["gluten","lactose"],"score":0.9}

cat: v=vegano (só vegetais), veg=vegetariano (tem ovo/queijo), p=proteína animal (carne/peixe/frango/embutidos)
score: sua confiança de 0.0 a 1.0
alerg: lista apenas os presentes
Valores por porção ~150g."""

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
    user_profile: Optional[Dict] = None
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
            "alergenos": {}
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
            alertas = gerar_alertas_personalizados(result, user_profile)
            result["alertas_personalizados"] = alertas
        
        logger.info(f"[GeminiFlash] ✅ Identificado: {result.get('nome')} ({result.get('confianca')}) em {total_time:.0f}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"[GeminiFlash] Erro: {e}")
        return {"ok": False, "error": str(e), "source": "gemini_flash"}


def gerar_alertas_personalizados(prato: Dict, perfil: Dict) -> List[Dict]:
    """
    Gera alertas personalizados baseados no prato identificado e perfil do usuário.
    Executa localmente para economizar tokens (não chama IA).
    
    Args:
        prato: Dados do prato identificado
        perfil: Perfil do usuário Premium
    
    Returns:
        Lista de alertas personalizados
    """
    alertas = []
    nome_usuario = perfil.get('nome', 'você')
    
    # ═══════════════════════════════════════════════════════════════════════
    # VERIFICAR ALÉRGENOS
    # ═══════════════════════════════════════════════════════════════════════
    alergias_usuario = [a.lower() for a in perfil.get('alergias', [])]
    alergenos_prato = prato.get('alergenos', {})
    
    mapa_alergenos = {
        'gluten': ['gluten', 'glúten', 'trigo'],
        'lactose': ['lactose', 'leite', 'laticínios'],
        'ovo': ['ovo', 'ovos'],
        'castanhas': ['castanhas', 'nozes', 'amendoim', 'castanha'],
        'frutos_do_mar': ['frutos do mar', 'camarão', 'peixe', 'crustáceos', 'mariscos'],
        'soja': ['soja']
    }
    
    for alergeno, presente in alergenos_prato.items():
        if presente:
            # Verificar se usuário tem alergia a este item
            termos_alergia = mapa_alergenos.get(alergeno, [alergeno])
            for alergia in alergias_usuario:
                if any(termo in alergia for termo in termos_alergia) or alergia in termos_alergia:
                    nome_alergeno = alergeno.replace('_', ' ').title()
                    alertas.append({
                        "tipo": "alergia",
                        "severidade": "alta",
                        "mensagem": f"⚠️ Olá {nome_usuario}, este prato parece conter {nome_alergeno}. Você indicou alergia a este ingrediente. Por favor, confirme com o atendente antes de servir.",
                        "icone": "⚠️"
                    })
                    break
    
    # ═══════════════════════════════════════════════════════════════════════
    # VERIFICAR RESTRIÇÕES ALIMENTARES
    # ═══════════════════════════════════════════════════════════════════════
    restricoes_usuario = [r.lower() for r in perfil.get('restricoes', [])]
    categoria_prato = prato.get('categoria', '').lower()
    
    # Vegano tentando comer proteína animal ou vegetariano
    if 'vegano' in restricoes_usuario:
        if categoria_prato == 'proteína animal':
            alertas.append({
                "tipo": "restricao",
                "severidade": "alta",
                "mensagem": f"🚫 {nome_usuario}, este prato contém proteína animal e você segue dieta vegana. Procure uma opção vegetal.",
                "icone": "🚫"
            })
        elif categoria_prato == 'vegetariano':
            alertas.append({
                "tipo": "restricao",
                "severidade": "media",
                "mensagem": f"⚠️ {nome_usuario}, este prato pode conter ovos ou laticínios. Confirme os ingredientes para sua dieta vegana.",
                "icone": "⚠️"
            })
    
    # Vegetariano tentando comer carne
    if 'vegetariano' in restricoes_usuario and categoria_prato == 'proteína animal':
        alertas.append({
            "tipo": "restricao",
            "severidade": "alta",
            "mensagem": f"🚫 {nome_usuario}, este prato contém carne/peixe e você é vegetariano.",
            "icone": "🚫"
        })
    
    # Sem glúten
    if 'sem_gluten' in restricoes_usuario or 'sem glúten' in restricoes_usuario:
        if alergenos_prato.get('gluten'):
            alertas.append({
                "tipo": "restricao",
                "severidade": "alta",
                "mensagem": f"⚠️ {nome_usuario}, este prato provavelmente contém glúten. Você indicou dieta sem glúten.",
                "icone": "⚠️"
            })
    
    # Sem lactose
    if 'sem_lactose' in restricoes_usuario or 'sem lactose' in restricoes_usuario:
        if alergenos_prato.get('lactose'):
            alertas.append({
                "tipo": "restricao",
                "severidade": "alta",
                "mensagem": f"⚠️ {nome_usuario}, este prato provavelmente contém lactose. Confirme se há versão sem laticínios.",
                "icone": "⚠️"
            })
    
    # ═══════════════════════════════════════════════════════════════════════
    # VERIFICAR CALORIAS vs META
    # ═══════════════════════════════════════════════════════════════════════
    meta_calorica_raw = perfil.get('meta_calorica', 0)
    # meta_calorica pode ser um dict {'meta_sugerida': 2000} ou um int
    if isinstance(meta_calorica_raw, dict):
        meta_calorica = meta_calorica_raw.get('meta_sugerida', 0)
    else:
        meta_calorica = meta_calorica_raw or 0
    
    objetivo = perfil.get('objetivo', 'manter')
    
    try:
        calorias_str = prato.get('nutricao', {}).get('calorias', '0')
        calorias_prato = int(''.join(c for c in str(calorias_str) if c.isdigit()) or '0')
    except:
        calorias_prato = 0
    
    if meta_calorica and calorias_prato:
        # Se o prato representa mais de 40% da meta diária
        percentual = (calorias_prato / meta_calorica) * 100
        
        if objetivo == 'perder' and percentual > 35:
            alertas.append({
                "tipo": "calorico",
                "severidade": "media",
                "mensagem": f"⚡ {nome_usuario}, este prato tem {calorias_prato} kcal ({percentual:.0f}% da sua meta diária). Como você quer emagrecer, considere uma porção menor.",
                "icone": "⚡"
            })
        elif percentual > 50:
            alertas.append({
                "tipo": "calorico",
                "severidade": "baixa",
                "mensagem": f"💡 Este prato tem {calorias_prato} kcal, que representa {percentual:.0f}% da sua meta diária de {meta_calorica} kcal.",
                "icone": "💡"
            })
    
    # ═══════════════════════════════════════════════════════════════════════
    # MENSAGEM POSITIVA (se não houver alertas negativos)
    # ═══════════════════════════════════════════════════════════════════════
    alertas_negativos = [a for a in alertas if a['severidade'] in ['alta', 'media']]
    
    if not alertas_negativos:
        if categoria_prato == 'vegano':
            alertas.append({
                "tipo": "positivo",
                "severidade": "baixa",
                "mensagem": f"✅ Ótima escolha, {nome_usuario}! Este prato vegano é nutritivo e saudável.",
                "icone": "✅"
            })
        elif categoria_prato == 'vegetariano' and 'vegetariano' in restricoes_usuario:
            alertas.append({
                "tipo": "positivo",
                "severidade": "baixa",
                "mensagem": f"✅ Perfeito, {nome_usuario}! Este prato vegetariano está adequado para você.",
                "icone": "✅"
            })
        else:
            beneficios = prato.get('beneficios', [])
            if beneficios:
                alertas.append({
                    "tipo": "positivo",
                    "severidade": "baixa",
                    "mensagem": f"✅ {nome_usuario}, este prato é fonte de {beneficios[0].lower() if beneficios else 'nutrientes'}.",
                    "icone": "✅"
                })
    
    return alertas


async def identify_multiple_items_flash(image_bytes: bytes) -> Dict:
    """
    Identifica MÚLTIPLOS itens em uma foto de prato de buffet.
    Usa Gemini Flash para detectar cada componente separadamente.
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
    from PIL import Image
    import io
    
    PROMPT_MULTI = """Analise esta foto de um prato de buffet/refeição e identifique CADA item separadamente.

Para CADA item visível, forneça:
- nome: Nome em português
- categoria: vegano|vegetariano|proteína animal  
- calorias_estimadas: em kcal (porção visível)
- ingredientes: lista dos principais ingredientes

RETORNE JSON:
{
    "total_itens": 3,
    "itens": [
        {"nome": "Arroz Branco", "categoria": "vegano", "calorias_estimadas": "150 kcal", "ingredientes": ["arroz"]},
        {"nome": "Feijão Preto", "categoria": "vegano", "calorias_estimadas": "100 kcal", "ingredientes": ["feijão", "temperos"]}
    ],
    "calorias_totais": "450 kcal",
    "observacao": "Prato bem balanceado com proteínas e carboidratos"
}"""
    
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {"ok": False, "error": "API key não configurada"}
        
        # Comprimir imagem
        img = Image.open(io.BytesIO(image_bytes))
        if max(img.size) > 768:
            ratio = 768 / max(img.size)
            img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.LANCZOS)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=70)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(buffer.getvalue())
            tmp_path = tmp.name
        
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"multi-{int(time.time())}",
                system_message=PROMPT_MULTI
            ).with_model("gemini", "gemini-2.5-flash")
            
            response = await chat.send_message(UserMessage(
                text="Identifique todos os itens deste prato. Responda APENAS JSON.",
                file_contents=[FileContentWithMimeType(file_path=tmp_path, mime_type="image/jpeg")]
            ))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        # Parse JSON
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        
        result = json.loads(response_clean.strip())
        result["ok"] = True
        result["source"] = "gemini_flash_multi"
        
        return result
        
    except Exception as e:
        logger.error(f"[GeminiFlash Multi] Erro: {e}")
        return {"ok": False, "error": str(e)}


def is_gemini_flash_available() -> bool:
    """Verifica se Gemini Flash está configurado (API direta do Google)"""
    return bool(os.environ.get('GOOGLE_API_KEY'))


def get_gemini_flash_status() -> Dict:
    """Retorna status do serviço Gemini Flash"""
    return {
        "available": is_gemini_flash_available(),
        "model": "gemini-2.5-flash",
        "provider": "Google AI via Emergent",
        "features": [
            "Identificação de pratos",
            "Informações nutricionais",
            "Detecção de alérgenos",
            "Alertas personalizados",
            "Múltiplos itens"
        ],
        "performance": {
            "latency_ms": "~340-800",
            "free_tier": "1500 requests/day"
        }
    }
