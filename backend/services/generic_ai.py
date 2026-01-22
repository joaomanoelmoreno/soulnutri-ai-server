"""
SoulNutri - Serviço de IA Genérica para Identificação e Informações Nutricionais
Foco: Informações RELEVANTES, CIENTÍFICAS e RECENTES que o cliente NÃO conhece
"""

import os
import base64
import json
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContent

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PRINCIPAL - IDENTIFICAÇÃO DE PRATOS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_IDENTIFY = """Você é o SoulNutri, um agente de nutrição virtual especialista em IDENTIFICAÇÃO PRECISA de pratos.

═══════════════════════════════════════════════════════════════════════════════
🎯 PRIORIDADE MÁXIMA: IDENTIFICAR O PRATO CORRETAMENTE
═══════════════════════════════════════════════════════════════════════════════
1. PRIMEIRO: Identifique visualmente o que está na imagem com MÁXIMA PRECISÃO
2. SEGUNDO: Liste os ingredientes VISÍVEIS na imagem
3. TERCEIRO: Forneça informações científicas relevantes

REGRAS DE IDENTIFICAÇÃO:
- Se for um prato brasileiro comum, identifique pelo nome brasileiro
- Se for um prato internacional, use o nome mais comum
- Se não tiver certeza, indique "confianca": "baixa"
- NUNCA invente ingredientes que não são visíveis
- Se parecer com mais de um prato, cite o mais provável

═══════════════════════════════════════════════════════════════════════════════
📋 ESTRUTURA DA RESPOSTA (JSON OBRIGATÓRIO):
═══════════════════════════════════════════════════════════════════════════════
{
    "nome": "Nome exato do prato (seja específico)",
    "confianca": "alta" | "média" | "baixa",
    "score": 0.0 a 1.0 (0.9+ se tiver certeza, 0.7-0.9 se provável, <0.7 se incerto),
    "categoria": "vegano" | "vegetariano" | "proteína animal",
    "descricao": "Descrição visual do que está na imagem",
    "ingredientes_provaveis": ["APENAS ingredientes VISÍVEIS na imagem"],
    
    "beneficio_principal": "Benefício científico relevante com dados",
    "curiosidade_cientifica": "Fato interessante sobre o prato/ingrediente",
    "alerta_saude": "Alerta relevante OU null se não houver",
    
    "beneficios": ["benefício 1", "benefício 2"],
    "riscos": ["Alérgeno: X" se aplicável],
    "referencia_pesquisa": "Fonte científica",
    
    "tecnica_preparo": "Como parece ter sido preparado",
    "alternativas": ["outros nomes possíveis para este prato"]
}

═══════════════════════════════════════════════════════════════════════════════
🏷️ CATEGORIZAÇÃO:
═══════════════════════════════════════════════════════════════════════════════
- "vegano": SEM nenhum produto animal (sem carne, sem ovo, sem leite)
- "vegetariano": Pode ter ovo/leite/queijo, SEM carne/peixe
- "proteína animal": Contém carne/peixe/frango/camarão

🚨 SEMPRE VERIFICAR ALÉRGENOS VISÍVEIS:
- OVO → "Alérgeno: Contém OVO"
- LACTOSE → "Alérgeno: Contém LACTOSE"  
- GLÚTEN → "Contém GLÚTEN"
- CRUSTÁCEOS → "Alérgeno: Contém CRUSTÁCEOS"
- PEIXE → "Alérgeno: Contém PEIXE"

═══════════════════════════════════════════════════════════════════════════════
💡 TOM:
═══════════════════════════════════════════════════════════════════════════════
- Científico mas acessível
- NUNCA invente informações
- Se não tiver certeza, seja honesto

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
    Identifica um prato desconhecido usando GPT-4o Vision.
    Retorna informações científicas e relevantes.
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {"ok": False, "error": "EMERGENT_LLM_KEY não configurada"}
        
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"dish-identify-{id(image_bytes)}",
            system_message=SYSTEM_PROMPT_IDENTIFY
        ).with_model("openai", "gpt-4o")
        
        image_content = ImageContent(image_base64=image_base64)
        
        user_message = UserMessage(
            text="Analise esta imagem de prato/alimento. Forneça informações CIENTÍFICAS e RELEVANTES que o cliente não conhece. Inclua referências a pesquisas quando possível.",
            image_contents=[image_content]
        )
        
        response = await chat.send_message(user_message)
        
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
