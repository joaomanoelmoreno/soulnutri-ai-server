"""
SoulNutri - Serviço de IA Genérica para Identificação e Informações Nutricionais
Foco: Informações RELEVANTES, CIENTÍFICAS e RECENTES que o cliente NÃO conhece
"""

import os
import base64
import json
import tempfile
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PRINCIPAL - IDENTIFICAÇÃO DE PRATOS (OTIMIZADO PARA VELOCIDADE)
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_IDENTIFY = """Você é o SoulNutri, especialista em identificação de pratos.

🎯 TAREFA: Identificar o prato e fornecer informações nutricionais.

REGRAS DE CATEGORIZAÇÃO (SIGA EXATAMENTE):
- "vegano": ZERO produtos animais (sem carne, peixe, ovo, leite, queijo, mel)
- "vegetariano": SEM carne/peixe, MAS pode ter ovo, leite, queijo
- "proteína animal": Contém carne, peixe, frango, camarão, bacon, presunto

⚠️ ATENÇÃO ESPECIAL:
- OVOS = NÃO É VEGANO (é vegetariano)
- QUEIJO = NÃO É VEGANO (é vegetariano)
- MAIONESE = Contém ovo, NÃO É VEGANO
- MEL = NÃO É VEGANO

RESPONDA APENAS COM ESTE JSON:
{
    "nome": "Nome do prato",
    "confianca": "alta" | "média" | "baixa",
    "score": 0.95,
    "categoria": "vegano" | "vegetariano" | "proteína animal",
    "descricao": "Descrição breve",
    "ingredientes_provaveis": ["ingrediente1", "ingrediente2"],
    "beneficio_principal": "Benefício científico",
    "curiosidade_cientifica": "Fato interessante",
    "alerta_saude": "Alerta ou null",
    "beneficios": ["benefício1"],
    "riscos": ["Alérgeno: X"],
    "referencia_pesquisa": "Fonte",
    "tecnica_preparo": "Preparo",
    "alternativas": []
}

JSON APENAS, sem texto extra."""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PARA MÚLTIPLOS ITENS NO PRATO
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_MULTI_ITEM = """Você é o SoulNutri, um agente de nutrição virtual especialista em IDENTIFICAR MÚLTIPLOS ITENS em uma imagem de refeição.

═══════════════════════════════════════════════════════════════════════════════
🎯 TAREFA: IDENTIFICAR TODOS OS ITENS SEPARADAMENTE
═══════════════════════════════════════════════════════════════════════════════

Analise a imagem e identifique CADA ITEM/PRATO separadamente.
Isso é útil para buffets, pratos compostos, ou refeições com múltiplos componentes.

REGRAS:
1. Identifique CADA item visível separadamente
2. Se for um prato único (ex: pizza), retorne apenas 1 item
3. Se forem vários itens (ex: arroz + feijão + carne + salada), liste CADA UM
4. Forneça informações nutricionais e científicas para CADA item
5. NUNCA invente ingredientes que não são visíveis

═══════════════════════════════════════════════════════════════════════════════
📋 ESTRUTURA DA RESPOSTA (JSON OBRIGATÓRIO):
═══════════════════════════════════════════════════════════════════════════════
{
    "total_itens": número de itens identificados,
    "tipo_refeicao": "prato_unico" | "prato_composto" | "buffet" | "lanche",
    "itens": [
        {
            "nome": "Nome do item (ex: Arroz Branco)",
            "categoria": "vegano" | "vegetariano" | "proteína animal",
            "category_emoji": "🌱" | "🥬" | "🍖",
            "porcao_estimada": "aproximado em gramas ou colheres",
            "calorias_estimadas": "~X kcal",
            "ingredientes_visiveis": ["ingrediente1", "ingrediente2"],
            "beneficio_principal": "Benefício científico do item",
            "alerta": "Alerta de alérgeno ou saúde, ou null",
            "curiosidade": "Fato interessante sobre o item"
        }
    ],
    "resumo_nutricional": {
        "calorias_totais": "~X kcal",
        "proteinas_totais": "~Xg",
        "carboidratos_totais": "~Xg",
        "gorduras_totais": "~Xg"
    },
    "alertas_combinados": ["Lista de TODOS os alérgenos presentes"],
    "dica_nutricional": "Dica sobre a combinação dos alimentos",
    "equilibrio": "balanceado" | "rico_em_carboidratos" | "rico_em_proteinas" | "rico_em_gorduras"
}

═══════════════════════════════════════════════════════════════════════════════
🏷️ CATEGORIZAÇÃO POR ITEM:
═══════════════════════════════════════════════════════════════════════════════
- "vegano" 🌱: SEM nenhum produto animal
- "vegetariano" 🥬: Pode ter ovo/leite/queijo, SEM carne/peixe
- "proteína animal" 🍖: Contém carne/peixe/frango/camarão

🚨 ALÉRGENOS A VERIFICAR:
- GLÚTEN, LACTOSE, OVO, CRUSTÁCEOS, PEIXE, AMENDOIM, SOJA

Responda APENAS com JSON válido, sem texto adicional."""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PARA ENRIQUECER INFORMAÇÕES DE PRATOS EXISTENTES
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_ENRICH = """Você é o SoulNutri, especialista em nutrição baseada em evidências científicas.

Sua tarefa é ENRIQUECER as informações de um prato brasileiro com dados RELEVANTES e CIENTÍFICOS.

REGRAS:
1. NÃO use informações óbvias (colesterol faz mal, açúcar engorda)
2. CITE fontes científicas (OMS, ANVISA, estudos)
3. EXPLIQUE por que cada nutriente é importante para o corpo
4. ALERTE sobre riscos baseados em pesquisas recentes
5. INCLUA curiosidades científicas que surpreendem

Retorne JSON com:
{
    "beneficio_principal": "Benefício mais relevante COM DADOS e explicação do efeito no corpo",
    "alerta_saude": "Alerta científico relevante OU null se não houver",
    "curiosidade_cientifica": "Fato surpreendente baseado em pesquisa",
    "beneficios": ["benefício 1 com dados", "benefício 2"],
    "riscos": ["risco relevante se houver"],
    "referencia_pesquisa": "Fonte científica principal"
}"""


async def identify_unknown_dish(image_bytes: bytes) -> dict:
    """
    Identifica um prato desconhecido usando Gemini Vision.
    OTIMIZADO para velocidade: comprime imagem antes de enviar.
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {"ok": False, "error": "EMERGENT_LLM_KEY não configurada"}
        
        # OTIMIZAÇÃO: Comprimir imagem para envio mais rápido
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_bytes))
        
        # Redimensionar se muito grande (max 800px no lado maior)
        max_size = 800
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Salvar com compressão
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=75, optimize=True)
        compressed_bytes = buffer.getvalue()
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(compressed_bytes)
            tmp_path = tmp_file.name
        
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"dish-{id(image_bytes)}",
                system_message=SYSTEM_PROMPT_IDENTIFY
            ).with_model("gemini", "gemini-2.0-flash")
            
            image_file = FileContentWithMimeType(
                file_path=tmp_path,
                mime_type="image/jpeg"
            )
            
            user_message = UserMessage(
                text="Identifique o prato. JSON apenas.",
                file_contents=[image_file]
            )
            
            response = await chat.send_message(user_message)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        # Parse JSON
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        response_clean = response_clean.strip()
        
        try:
            result = json.loads(response_clean)
            result["ok"] = True
            result["source"] = "generic_ai"
            
            # Mapear confiança
            conf_map = {"alta": "🟢", "média": "🟡", "baixa": "🔴"}
            result["confidence_emoji"] = conf_map.get(result.get("confianca", "baixa"), "🔴")
            
            # Mapear categoria
            cat_map = {"vegano": "🌱", "vegetariano": "🥬", "proteína animal": "🍖"}
            result["category_emoji"] = cat_map.get(result.get("categoria", ""), "🍽️")
            
            return result
            
        except json.JSONDecodeError:
            return {
                "ok": True,
                "source": "generic_ai",
                "raw_response": response,
                "nome": "Prato não identificado",
                "confianca": "baixa",
                "score": 0.3
            }
            
    except Exception as e:
        return {"ok": False, "error": str(e), "source": "generic_ai"}


async def enrich_dish_info(dish_name: str, ingredients: list = None) -> dict:
    """
    Enriquece informações de um prato com dados científicos.
    Usado para melhorar pratos existentes no banco.
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {}
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"enrich-{dish_name}",
            system_message=SYSTEM_PROMPT_ENRICH
        ).with_model("openai", "gpt-4o-mini")
        
        ingredients_text = ", ".join(ingredients) if ingredients else "não especificados"
        
        prompt = f"""Enriqueça as informações deste prato brasileiro com dados CIENTÍFICOS:

Prato: {dish_name}
Ingredientes: {ingredients_text}

Forneça:
1. Benefício principal com DADOS (mg, %, estudos)
2. Alerta de saúde SE houver pesquisa relevante
3. Curiosidade científica surpreendente
4. Referência da fonte principal"""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        
        return json.loads(response_clean.strip())
        
    except Exception as e:
        print(f"Erro ao enriquecer {dish_name}: {e}")
        return {}


async def search_ingredient_news(ingredient: str) -> dict:
    """
    Busca notícias/pesquisas recentes sobre um ingrediente.
    Para o recurso "veja esta notícia recente".
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {}
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"news-{ingredient}",
            system_message="""Você é um pesquisador de nutrição. Forneça informações sobre pesquisas RECENTES (últimos 5 anos) relacionadas ao ingrediente.

Foque em:
- Estudos da OMS, IARC, ANVISA, FDA
- Pesquisas publicadas em revistas científicas
- Alertas de saúde pública
- Descobertas nutricionais relevantes

Retorne JSON:
{
    "ingrediente": "nome",
    "pesquisa_recente": "Descrição da pesquisa mais relevante",
    "fonte": "OMS 2023 / Estudo Harvard / etc",
    "impacto_saude": "O que isso significa para o consumidor",
    "recomendacao": "Sugestão baseada na pesquisa"
}"""
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message(UserMessage(
            text=f"Busque pesquisas científicas RECENTES sobre: {ingredient}. Foque em estudos dos últimos 5 anos sobre impactos na saúde."
        ))
        
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        
        return json.loads(response_clean.strip())
        
    except Exception as e:
        return {"error": str(e)}


async def identify_multiple_items(image_bytes: bytes) -> dict:
    """
    Identifica MÚLTIPLOS itens em uma imagem de refeição.
    Útil para buffets, pratos compostos ou refeições com vários componentes.
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {"ok": False, "error": "EMERGENT_LLM_KEY não configurada"}
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name
        
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"multi-item-{id(image_bytes)}",
                system_message=SYSTEM_PROMPT_MULTI_ITEM
            ).with_model("gemini", "gemini-2.0-flash")
            
            image_file = FileContentWithMimeType(
                file_path=tmp_path,
                mime_type="image/jpeg"
            )
            
            user_message = UserMessage(
                text="Analise esta imagem e identifique TODOS os itens/pratos separadamente. Se for um buffet ou prato composto, liste cada componente. Responda APENAS com JSON válido.",
                file_contents=[image_file]
            )
            
            response = await chat.send_message(user_message)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        # Parse JSON
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        response_clean = response_clean.strip()
        
        try:
            result = json.loads(response_clean)
            result["ok"] = True
            result["source"] = "generic_ai_multi"
            return result
        except json.JSONDecodeError:
            return {
                "ok": False,
                "error": "Erro ao processar resposta da IA",
                "raw_response": response
            }
            
    except Exception as e:
        return {"ok": False, "error": str(e)}
