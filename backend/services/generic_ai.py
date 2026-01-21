"""
SoulNutri - Serviço de IA Genérica para Pratos Desconhecidos
Usa GPT-4o Vision para identificar pratos não cadastrados no sistema
"""

import os
import base64
import json
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

load_dotenv()

SYSTEM_PROMPT = """Você é um nutricionista especialista em identificação de pratos brasileiros.
Sua tarefa é analisar imagens de pratos e fornecer informações PRECISAS.

REGRAS IMPORTANTES DE CATEGORIZAÇÃO:
- "vegano": SEM nenhum produto animal (sem carne, sem peixe, sem ovo, sem leite, sem queijo, sem mel)
- "vegetariano": Pode ter ovo, leite, queijo, mel - MAS sem carne e sem peixe
- "proteína animal": Contém carne, peixe, frango, camarão ou qualquer carne

ALÉRGENOS OBRIGATÓRIOS A VERIFICAR:
- OVO: Se contém ovo, SEMPRE adicione "Alérgeno: Contém OVO"
- LACTOSE: Se contém leite/queijo/manteiga, adicione "Alérgeno: Contém LACTOSE"
- GLÚTEN: Se contém trigo/farinha/pão/massa, adicione "Contém glúten"
- CRUSTÁCEOS: Se contém camarão/lagosta/caranguejo, adicione "Alérgeno: Contém CRUSTÁCEOS"
- PEIXE: Se contém peixe/atum/salmão, adicione "Alérgeno: Contém PEIXE"
- SOJA: Se contém soja/tofu/shoyu, adicione "Alérgeno: Contém SOJA"
- AMENDOIM: Se contém amendoim, adicione "Alérgeno: Contém AMENDOIM"
- CASTANHAS: Se contém castanhas/nozes, adicione "Alérgeno: Contém OLEAGINOSAS"

Retorne SEMPRE um JSON válido:
{
    "nome": "Nome do prato",
    "confianca": "alta" | "média" | "baixa",
    "score": 0.0 a 1.0,
    "categoria": "vegano" | "vegetariano" | "proteína animal",
    "descricao": "Descrição breve",
    "ingredientes_provaveis": ["ingrediente1", "ingrediente2"],
    "beneficios": ["benefício1", "benefício2"],
    "riscos": ["Alérgeno: Contém X", "Contém glúten"],
    "tecnica_preparo": "Técnica de preparo",
    "alternativas": ["nome alternativo"]
}

ATENÇÃO: Se o prato contém OVO, a categoria NÃO pode ser "vegano", deve ser "vegetariano".
Se contém qualquer carne/peixe/frango, deve ser "proteína animal".
Responda APENAS com o JSON."""

async def identify_unknown_dish(image_bytes: bytes) -> dict:
    """
    Identifica um prato desconhecido usando GPT-4o Vision.
    
    Args:
        image_bytes: Bytes da imagem do prato
        
    Returns:
        Dict com informações do prato identificado
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {
                "ok": False,
                "error": "EMERGENT_LLM_KEY não configurada"
            }
        
        # Converter imagem para base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Criar instância do chat
        chat = LlmChat(
            api_key=api_key,
            session_id=f"dish-identify-{id(image_bytes)}",
            system_message=SYSTEM_PROMPT
        ).with_model("openai", "gpt-4o")
        
        # Criar conteúdo da imagem
        image_content = ImageContent(image_base64=image_base64)
        
        # Criar mensagem com a imagem
        user_message = UserMessage(
            text="Analise esta imagem de prato/alimento e retorne as informações no formato JSON especificado.",
            image_contents=[image_content]
        )
        
        # Enviar e obter resposta
        response = await chat.send_message(user_message)
        
        # Tentar parsear o JSON da resposta
        try:
            # Limpar resposta (remover markdown se houver)
            response_clean = response.strip()
            if response_clean.startswith("```"):
                response_clean = response_clean.split("```")[1]
                if response_clean.startswith("json"):
                    response_clean = response_clean[4:]
            response_clean = response_clean.strip()
            
            result = json.loads(response_clean)
            result["ok"] = True
            result["source"] = "generic_ai"
            result["model"] = "gpt-4o"
            
            # Mapear confiança para emoji
            conf_map = {
                "alta": "🟢",
                "média": "🟡", 
                "baixa": "🔴"
            }
            result["confidence_emoji"] = conf_map.get(result.get("confianca", "baixa"), "🔴")
            
            # Mapear categoria para emoji
            cat_map = {
                "vegano": "🌱",
                "vegetariano": "🥬",
                "proteína animal": "🍖"
            }
            result["category_emoji"] = cat_map.get(result.get("categoria", ""), "🍽️")
            
            return result
            
        except json.JSONDecodeError:
            # Se não conseguir parsear, retornar resposta bruta
            return {
                "ok": True,
                "source": "generic_ai",
                "raw_response": response,
                "nome": "Prato não identificado",
                "confianca": "baixa",
                "score": 0.3,
                "descricao": response[:200] if len(response) > 200 else response
            }
            
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "source": "generic_ai"
        }


async def enrich_dish_info(dish_name: str, current_info: dict) -> dict:
    """
    Enriquece as informações de um prato usando IA.
    Útil para completar dados genéricos.
    
    Args:
        dish_name: Nome do prato
        current_info: Informações atuais (podem estar incompletas)
        
    Returns:
        Dict com informações enriquecidas
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return current_info
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"enrich-{dish_name}",
            system_message="""Você é um nutricionista especialista em culinária brasileira.
Forneça informações detalhadas e precisas sobre pratos, considerando:
- Ingredientes típicos brasileiros
- Benefícios nutricionais reais
- Riscos e alérgenos
- Técnicas de preparo tradicionais

Retorne SEMPRE um JSON válido."""
        ).with_model("openai", "gpt-4o-mini")
        
        prompt = f"""Complete as informações deste prato brasileiro:
Nome: {dish_name}
Informações atuais: {json.dumps(current_info, ensure_ascii=False)}

Retorne um JSON com:
{{
    "descricao": "descrição detalhada",
    "ingredientes": ["lista", "completa", "de", "ingredientes"],
    "beneficios": ["benefício real 1", "benefício real 2"],
    "riscos": ["risco/alérgeno 1", "risco/alérgeno 2"],
    "tecnica": "técnica de preparo"
}}"""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parsear resposta
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        
        enriched = json.loads(response_clean.strip())
        
        # Mesclar com informações existentes
        result = {**current_info}
        for key, value in enriched.items():
            if value and (not result.get(key) or result.get(key) == []):
                result[key] = value
        
        return result
        
    except Exception as e:
        print(f"Erro ao enriquecer prato {dish_name}: {e}")
        return current_info
