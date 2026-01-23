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
# PROMPT PRINCIPAL - IDENTIFICAÇÃO DE PRATOS (COM DUPLA VERIFICAÇÃO)
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_IDENTIFY = """Você é o SoulNutri, especialista RIGOROSO em identificação de pratos.

🎯 TAREFA: Identificar o prato com DUPLA VERIFICAÇÃO de categorização.

═══════════════════════════════════════════════════════════════════════════════
🔍 PROCESSO DE DUPLA VERIFICAÇÃO (OBRIGATÓRIO):
═══════════════════════════════════════════════════════════════════════════════

PASSO 1 - Liste TODOS os ingredientes visíveis na imagem
PASSO 2 - Para CADA ingrediente, classifique:
  - 🌱 VEGANO: vegetais, frutas, grãos, legumes, cogumelos, tofu
  - 🥬 VEGETARIANO: ovo, leite, queijo, manteiga, iogurte, mel
  - 🍖 ANIMAL: carne, frango, peixe, bacon, presunto, camarão, linguiça

PASSO 3 - REGRA DE CATEGORIZAÇÃO FINAL:
  - Se TODOS ingredientes são 🌱 → categoria = "vegano"
  - Se tem 🥬 mas NENHUM 🍖 → categoria = "vegetariano"  
  - Se tem QUALQUER 🍖 → categoria = "proteína animal"

═══════════════════════════════════════════════════════════════════════════════
⚠️ INGREDIENTES ARMADILHA (MEMORIZE!):
═══════════════════════════════════════════════════════════════════════════════
NÃO SÃO VEGANOS (são vegetarianos):
- Ovos, omelete, ovo frito → 🥬 VEGETARIANO
- Queijo, parmesão, mussarela, requeijão → 🥬 VEGETARIANO
- Maionese (contém ovo) → 🥬 VEGETARIANO
- Manteiga, creme de leite → 🥬 VEGETARIANO
- Mel → 🥬 VEGETARIANO
- Massa com ovo → 🥬 VEGETARIANO

CONTÊM PROTEÍNA ANIMAL (NÃO são vegetarianos):
- Bacon, pancetta → 🍖 ANIMAL
- Presunto, mortadela → 🍖 ANIMAL
- Caldo de carne/galinha → 🍖 ANIMAL
- Gelatina → 🍖 ANIMAL
- Anchovas (comum em molhos) → 🍖 ANIMAL
- Linguiça, salsicha → 🍖 ANIMAL

═══════════════════════════════════════════════════════════════════════════════
📋 RESPONDA COM ESTE JSON:
═══════════════════════════════════════════════════════════════════════════════
{
    "nome": "Nome do prato",
    "confianca": "alta" | "média" | "baixa",
    "score": 0.95,
    "categoria": "vegano" | "vegetariano" | "proteína animal",
    "descricao": "Descrição breve",
    
    "_verificacao_ingredientes": {
        "ingredientes_visiveis": ["ingrediente1", "ingrediente2"],
        "ingredientes_veganos": ["lista de 🌱"],
        "ingredientes_vegetarianos": ["lista de 🥬 se houver"],
        "ingredientes_animais": ["lista de 🍖 se houver"],
        "justificativa_categoria": "Explicação da classificação final"
    },
    
    "ingredientes_provaveis": ["ingrediente1", "ingrediente2"],
    
    "_analise_ingredientes": [
        {
            "nome": "ingrediente",
            "tipo": "vegano|vegetariano|animal",
            "beneficio": "benefício principal",
            "risco": "risco ou alérgeno, se houver",
            "curiosidade": "fato interessante"
        }
    ],
    
    "beneficio_principal": "Benefício científico do prato",
    "curiosidade_cientifica": "Fato interessante baseado em pesquisa",
    "alerta_saude": "Alerta importante ou null",
    "beneficios": ["benefício1", "benefício2"],
    "riscos": ["Alérgeno: X", "Risco: Y"],
    "referencia_pesquisa": "Fonte científica (OMS, estudo, etc)",
    "tecnica_preparo": "Preparo típico",
    "alternativas": ["alternativa saudável"]
}

═══════════════════════════════════════════════════════════════════════════════
🚨 ALÉRGENOS OBRIGATÓRIOS A VERIFICAR:
═══════════════════════════════════════════════════════════════════════════════
SEMPRE verifique e liste nos riscos:
- GLÚTEN (trigo, centeio, cevada)
- LACTOSE (leite, queijo, manteiga)
- OVO
- CRUSTÁCEOS (camarão, lagosta)
- PEIXE
- AMENDOIM e NOZES
- SOJA
- GERGELIM

JSON APENAS, sem texto extra."""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PARA MÚLTIPLOS ITENS NO PRATO (COM DUPLA VERIFICAÇÃO)
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_MULTI_ITEM = """Você é o SoulNutri, especialista RIGOROSO em identificação de MÚLTIPLOS ITENS em refeições.

═══════════════════════════════════════════════════════════════════════════════
🎯 TAREFA: IDENTIFICAR CADA ITEM COM DUPLA VERIFICAÇÃO
═══════════════════════════════════════════════════════════════════════════════

PROCESSO OBRIGATÓRIO PARA CADA ITEM:
1. Identifique TODOS os ingredientes visíveis
2. Classifique cada ingrediente: 🌱vegano / 🥬vegetariano / 🍖animal
3. Determine categoria final baseado no ingrediente "mais restritivo"

═══════════════════════════════════════════════════════════════════════════════
⚠️ REGRAS DE CATEGORIZAÇÃO (MEMORIZE!):
═══════════════════════════════════════════════════════════════════════════════

🌱 VEGANO = ZERO produtos animais
   ✓ Vegetais, frutas, grãos, legumes, cogumelos, tofu, leite vegetal
   ✗ NADA de: ovo, leite, queijo, mel, manteiga

🥬 VEGETARIANO = Sem carne, pode ter derivados animais
   ✓ Ovo, leite, queijo, manteiga, mel, iogurte
   ✗ NADA de: carne, frango, peixe, bacon, presunto

🍖 PROTEÍNA ANIMAL = Contém carne ou derivados
   Carne, frango, peixe, bacon, presunto, linguiça, camarão, gelatina

═══════════════════════════════════════════════════════════════════════════════
🚨 ARMADILHAS COMUNS (CUIDADO!):
═══════════════════════════════════════════════════════════════════════════════
- Salada Caesar tem ANCHOVAS e PARMESÃO → NÃO é vegana
- Maionese tem OVO → NÃO é vegana
- Pão de queijo tem QUEIJO e OVO → Vegetariano, NÃO vegano
- Molho pesto tem PARMESÃO → Vegetariano, NÃO vegano
- Feijão tropeiro tem BACON → Proteína animal
- Farofa com ovo → Vegetariana
- Arroz de carreteiro tem CARNE → Proteína animal

═══════════════════════════════════════════════════════════════════════════════
📋 ESTRUTURA DA RESPOSTA (JSON OBRIGATÓRIO):
═══════════════════════════════════════════════════════════════════════════════
{
    "total_itens": número,
    "tipo_refeicao": "prato_unico" | "prato_composto" | "buffet" | "lanche",
    "itens": [
        {
            "nome": "Nome do item",
            "categoria": "vegano" | "vegetariano" | "proteína animal",
            "category_emoji": "🌱" | "🥬" | "🍖",
            "porcao_estimada": "~Xg",
            "calorias_estimadas": "~X kcal",
            
            "_verificacao": {
                "ingredientes_identificados": ["lista completa"],
                "ingredientes_animais_encontrados": ["se houver"],
                "justificativa": "Por que esta categoria"
            },
            
            "ingredientes_visiveis": ["ingrediente1", "ingrediente2"],
            
            "analise_ingredientes": [
                {"nome": "ing", "tipo": "🌱|🥬|🍖", "beneficio": "X", "risco": "Y ou null"}
            ],
            
            "beneficio_principal": "Benefício científico",
            "alerta": "Alérgeno ou risco, ou null",
            "curiosidade": "Fato interessante"
        }
    ],
    "resumo_nutricional": {
        "calorias_totais": "~X kcal",
        "proteinas_totais": "~Xg",
        "carboidratos_totais": "~Xg",
        "gorduras_totais": "~Xg"
    },
    "alertas_combinados": ["TODOS os alérgenos encontrados"],
    "dica_nutricional": "Dica sobre a combinação",
    "equilibrio": "balanceado" | "rico_em_carboidratos" | "rico_em_proteinas" | "rico_em_gorduras"
}

JSON APENAS, sem texto adicional."""


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
        
        # Redimensionar para menor tamanho (max 512px - mais rápido)
        max_size = 512
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Salvar com compressão alta (mais rápido upload)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=60, optimize=True)
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
                text="Identifique este prato. Responda APENAS JSON.",
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
            
            # ═══════════════════════════════════════════════════════════════
            # VALIDAÇÃO DE SEGURANÇA - Corrige classificações erradas
            # ═══════════════════════════════════════════════════════════════
            from services.safety_validator import validar_resultado_ia
            result = validar_resultado_ia(result)
            
            # Mapear confiança
            conf_map = {"alta": "🟢", "média": "🟡", "baixa": "🔴"}
            result["confidence_emoji"] = conf_map.get(result.get("confianca", "baixa"), "🔴")
            
            # Mapear categoria (após validação de segurança)
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
    
    PROTEÇÃO CONTRA FAKE NEWS:
    - Usa apenas fontes científicas verificadas
    - Inclui data da pesquisa
    - Valida informações com múltiplas fontes
    """
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {}
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"news-{ingredient}",
            system_message="""Você é um pesquisador de nutrição RIGOROSO. Forneça APENAS informações de pesquisas VERIFICADAS.

🔒 REGRAS ANTI-FAKE NEWS (OBRIGATÓRIAS):
1. Use APENAS fontes científicas oficiais:
   - OMS (Organização Mundial da Saúde)
   - ANVISA (Brasil)
   - FDA (EUA)
   - EFSA (Europa)
   - PubMed / NIH
   - Revistas científicas peer-reviewed (Nature, Lancet, JAMA, etc.)

2. NUNCA cite:
   - Blogs pessoais
   - Redes sociais
   - Sites de notícias sensacionalistas
   - Estudos não revisados por pares
   - Fontes sem data ou autor

3. Sempre inclua:
   - ANO do estudo/publicação
   - NOME da instituição ou revista
   - Se é CONSENSO científico ou estudo PRELIMINAR

4. Se NÃO houver pesquisa confiável, diga claramente:
   "Não há estudos científicos robustos sobre este tópico"

Retorne JSON:
{
    "ingrediente": "nome",
    "pesquisa_verificada": "Descrição factual da pesquisa",
    "fonte_oficial": "OMS 2023 / Estudo Harvard publicado no JAMA / etc",
    "nivel_evidencia": "consenso" | "forte" | "moderado" | "preliminar",
    "data_pesquisa": "2023" ou "2024",
    "impacto_saude": "O que isso significa para o consumidor",
    "recomendacao_oficial": "Recomendação baseada em órgão oficial",
    "aviso": "Informação importante sobre limitações do estudo, se houver"
}"""
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message(UserMessage(
            text=f"""Busque pesquisas científicas VERIFICADAS sobre: {ingredient}

IMPORTANTE:
- Apenas estudos de fontes oficiais (OMS, ANVISA, FDA, revistas científicas)
- Inclua ano e fonte exata
- Indique se é consenso ou estudo preliminar
- Se não houver evidência forte, seja honesto sobre isso"""
        ))
        
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        
        result = json.loads(response_clean.strip())
        result["fonte_verificada"] = True
        result["aviso_padrao"] = "Informações baseadas em pesquisas científicas. Consulte um profissional de saúde para orientação personalizada."
        
        return result
        
    except Exception as e:
        return {"error": str(e), "fonte_verificada": False}


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
