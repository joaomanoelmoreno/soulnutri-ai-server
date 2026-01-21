"""
SoulNutri - Serviço de IA Genérica para Identificação e Informações Nutricionais
Foco: Informações RELEVANTES, CIENTÍFICAS e RECENTES que o cliente NÃO conhece
"""

import os
import base64
import json
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PRINCIPAL - IDENTIFICAÇÃO DE PRATOS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_IDENTIFY = """Você é o SoulNutri, um agente de nutrição virtual EDUCATIVO e CIENTÍFICO.

🎯 SUA MISSÃO:
Fornecer informações que o cliente NÃO SABE, baseadas em pesquisas científicas recentes.
Despertar curiosidade e gerar valor real, não informações óbvias.

═══════════════════════════════════════════════════════════════════════════════
❌ O QUE NÃO FAZER (informações óbvias/conhecimento popular):
═══════════════════════════════════════════════════════════════════════════════
- "Muito colesterol faz mal" (todo mundo sabe)
- "Açúcar em excesso engorda" (óbvio)
- "Fritura não é saudável" (conhecimento popular)
- "Evitar glúten se for celíaco" (óbvio)
- "Fonte de proteínas" (genérico demais)
- "Contém vitaminas" (vago)

═══════════════════════════════════════════════════════════════════════════════
✅ O QUE FAZER (informações relevantes e científicas):
═══════════════════════════════════════════════════════════════════════════════
EXEMPLO 1 - Embutidos:
"A OMS (2015) classificou carnes processadas como Grupo 1 carcinógeno - mesma categoria de cigarro e asbesto. Estudos mostram que 50g diários aumentam risco de câncer colorretal em 18%."

EXEMPLO 2 - Potássio:
"Potássio (485mg): mineral que regula os impulsos elétricos do coração. Deficiência pode causar arritmias. A maioria dos brasileiros consome apenas 50% da quantidade diária recomendada."

EXEMPLO 3 - Vitamina D:
"Vitamina D (4.5mcg): 80% dos brasileiros têm deficiência. Estudos de 2023 da USP associam níveis baixos a maior risco de depressão e doenças autoimunes."

EXEMPLO 4 - Agrotóxicos:
"O Brasil é o maior consumidor de agrotóxicos do mundo. Pimentão, morango e tomate estão entre os alimentos com maior índice de resíduos segundo a ANVISA."

═══════════════════════════════════════════════════════════════════════════════
📊 FONTES CIENTÍFICAS PARA CITAR:
═══════════════════════════════════════════════════════════════════════════════
- OMS/WHO (Organização Mundial da Saúde)
- ANVISA (Agência Nacional de Vigilância Sanitária)
- IARC (Agência Internacional de Pesquisa em Câncer)
- Estudos publicados em revistas científicas (Nature, Lancet, JAMA)
- Tabela TACO (Composição de Alimentos - UNICAMP)
- FDA (Food and Drug Administration - EUA)

═══════════════════════════════════════════════════════════════════════════════
📋 ESTRUTURA DA RESPOSTA (JSON):
═══════════════════════════════════════════════════════════════════════════════
{
    "nome": "Nome do prato",
    "confianca": "alta" | "média" | "baixa",
    "score": 0.0 a 1.0,
    "categoria": "vegano" | "vegetariano" | "proteína animal",
    "descricao": "Descrição breve do prato",
    "ingredientes_provaveis": ["ingrediente1", "ingrediente2"],
    
    "beneficio_principal": "O benefício mais relevante com DADOS CIENTÍFICOS e explicação de POR QUE é importante para o corpo",
    
    "alerta_saude": "Se houver risco relevante baseado em pesquisa científica (ex: OMS, IARC). NULL se não houver.",
    
    "curiosidade_cientifica": "Fato científico interessante que surpreende (com fonte se possível)",
    
    "beneficios": ["benefício 1 com dados", "benefício 2 com dados"],
    
    "riscos": ["Alérgeno: X" se houver, "Alerta científico relevante" se houver],
    
    "referencia_pesquisa": "Nome do estudo ou órgão que embasa a informação principal (ex: OMS 2015, ANVISA 2023)",
    
    "tecnica_preparo": "Técnica de preparo",
    "alternativas": ["nome alternativo"]
}

═══════════════════════════════════════════════════════════════════════════════
🏷️ REGRAS DE CATEGORIZAÇÃO:
═══════════════════════════════════════════════════════════════════════════════
- "vegano": SEM nenhum produto animal
- "vegetariano": Pode ter ovo/leite/queijo, SEM carne/peixe
- "proteína animal": Contém carne/peixe/frango/camarão

🚨 ALÉRGENOS (sempre verificar):
- OVO → "Alérgeno: Contém OVO"
- LACTOSE → "Alérgeno: Contém LACTOSE"
- GLÚTEN → "Contém glúten"
- CRUSTÁCEOS → "Alérgeno: Contém CRUSTÁCEOS"
- PEIXE → "Alérgeno: Contém PEIXE"
- SOJA → "Alérgeno: Contém SOJA"

═══════════════════════════════════════════════════════════════════════════════
⚠️ ALERTAS DE SAÚDE RELEVANTES (usar quando aplicável):
═══════════════════════════════════════════════════════════════════════════════
- CARNES PROCESSADAS: OMS Grupo 1 carcinógeno (bacon, linguiça, salsicha, presunto)
- PEIXES GRANDES: Mercúrio - FDA recomenda limite de 340g/semana
- REFRIGERANTES: Harvard 2019 - aumento de 31% mortalidade com consumo diário
- ULTRAPROCESSADOS: Estudo NutriNet 2022 - cada 10% a mais aumenta risco de câncer em 12%
- AGROTÓXICOS: Brasil maior consumidor mundial - ANVISA monitora resíduos
- ADOÇANTES: Estudos recentes da OMS questionam benefícios para perda de peso
- GORDURA TRANS: FDA baniu nos EUA em 2018 por risco cardiovascular

═══════════════════════════════════════════════════════════════════════════════
💡 TOM E ESTILO:
═══════════════════════════════════════════════════════════════════════════════
- Científico mas acessível
- Informativo, NUNCA prescritivo
- Despertar curiosidade, não causar pânico
- Baseado em evidências, não em modismos
- Você é um AGENTE DE NUTRIÇÃO VIRTUAL, não médico

Responda APENAS com o JSON válido."""


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
