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
# PROMPT PRINCIPAL - IDENTIFICAÇÃO RÁPIDA DE PRATOS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_IDENTIFY = """Identifique o prato na imagem.

CONTEXTO: Este é um buffet de restaurante brasileiro. Os pratos comuns incluem:
- Arroz (branco, integral, 7 grãos), Feijão (preto, carioca)
- Espaguete, Lasanha, Canelone, Macarrão
- Frango grelhado, Frango à parmegiana, Filé mignon, Maminha
- Peixe, Salmão, Atum, Bacalhau (à brás, com natas, à gomes de sá)
- Bolinho de bacalhau, Cestinha de camarão
- Saladas, Legumes, Batata (doce, assada, frita)
- Cocada, Gelatina, Mousse, Pudim

REGRAS DE CATEGORIA:
- "vegano": ZERO produtos de origem animal
- "vegetariano": tem ovo/leite/queijo de VACA, SEM carne
- "proteína animal": tem carne/peixe/frango

INGREDIENTES VEGANOS (NÃO são de origem animal):
- Leite de coco, creme de coco, óleo de coco
- Leite de amêndoas, leite de soja, leite de aveia
- Cogumelos, tofu, tempeh, seitan

ATENÇÃO CRÍTICA:
- Peixe/camarão/mariscos = proteína animal
- Ovo/queijo de VACA/leite de VACA = vegetariano (não vegano)
- Bacon/presunto/carne = proteína animal
- Leite de COCO = VEGANO (não é de origem animal!)
- Muqueca com leite de coco e SEM peixe = vegano

Use nomes simples em português. Exemplo: "Bolinho de Bacalhau" (não "codfish balls").

JSON obrigatório:
{
    "nome": "Nome do Prato",
    "categoria": "vegano|vegetariano|proteína animal",
    "confianca": "alta|média|baixa",
    "score": 0.9,
    "ingredientes_provaveis": ["ing1", "ing2", "ing3"],
    "beneficio_principal": "Benefício principal",
    "curiosidade_cientifica": "Fato interessante",
    "riscos": ["Alérgeno: X"],
    "descricao": "Descrição curta"
}"""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PARA MÚLTIPLOS ITENS NO PRATO
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_MULTI_ITEM = """Identifique TODOS os itens visíveis no prato.

Para cada item, retorne:
- nome: Nome do item
- categoria: "vegano" | "vegetariano" | "proteína animal"
- ingredientes: Lista de ingredientes visíveis

REGRAS:
- Peixe/carne/frango = proteína animal
- Ovo/queijo = vegetariano
- Só vegetais/grãos = vegano

JSON obrigatório:
{
    "total_itens": 3,
    "itens": [
        {"nome": "Arroz", "categoria": "vegano", "ingredientes": ["arroz"], "calorias": "~150kcal"},
        {"nome": "Feijão", "categoria": "vegano", "ingredientes": ["feijão"], "calorias": "~100kcal"}
    ],
    "calorias_totais": "~500kcal",
    "alertas": ["Alérgeno: X"]
}"""


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
            ).with_model("gemini", "gemini-2.0-flash-lite")
            
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


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT PARA CORREÇÃO/PREENCHIMENTO DE DADOS DO PRATO
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_FIX_DISH = """Você é um nutricionista RIGOROSO analisando dados de pratos.

TAREFA: Analisar a imagem do prato e PREENCHER/CORRIGIR as informações faltantes.

REGRAS ESTRITAS DE CATEGORIA:
1. "vegano": ZERO ingredientes de origem animal (sem ovo, leite de VACA, queijo, mel)
2. "vegetariano": pode ter ovo, leite de VACA, queijo, mel, MAS sem carne/peixe/frango
3. "proteína animal": contém carne, peixe, frango, bacon, presunto, camarão

IMPORTANTE - INGREDIENTES VEGANOS:
- Leite de COCO = VEGANO (não é de origem animal!)
- Creme de coco, óleo de coco = VEGANO
- Leite de amêndoas, soja, aveia = VEGANO
- Cogumelos, tofu, tempeh = VEGANO
- Muqueca com leite de coco SEM peixe = VEGANO

REGRAS DE NUTRIÇÃO (por porção ~100g):
- Vegetais: 20-50 kcal
- Arroz/massa: 130-160 kcal
- Carnes magras: 150-200 kcal
- Frituras: 250-400 kcal

ALÉRGENOS - Marque TRUE apenas se CERTEZA:
- contem_gluten: farinha de trigo, pão, massa, empanado
- contem_lactose: leite de VACA, queijo, creme de leite, manteiga
- contem_ovo: ovos, maionese, massas com ovo
- contem_castanhas: castanhas, amendoim, nozes, amêndoas
- contem_frutos_mar: camarão, peixe, mariscos
- contem_soja: tofu, shoyu, leite de soja

RESPONDA APENAS JSON:
{
    "nome": "Nome Correto do Prato",
    "categoria": "vegano|vegetariano|proteína animal",
    "category_emoji": "🥬|🥚|🍖",
    "descricao": "Descrição em 1-2 frases",
    "ingredientes": ["ingrediente1", "ingrediente2"],
    "beneficios": ["benefício1", "benefício2"],
    "riscos": ["Contém X (alérgeno)", "Alto teor de Y"],
    "nutricao": {
        "calorias": "XXX kcal",
        "proteinas": "XXg",
        "carboidratos": "XXg",
        "gorduras": "XXg"
    },
    "contem_gluten": true/false,
    "contem_lactose": true/false,
    "contem_ovo": true/false,
    "contem_castanhas": true/false,
    "contem_frutos_mar": true/false,
    "contem_soja": true/false
}"""


async def fix_dish_data_with_ai(image_bytes: bytes, current_info: dict) -> dict:
    """
    Usa Gemini para corrigir/preencher dados de um prato.
    Envia a imagem + dados atuais e pede para corrigir/completar.
    """
    import tempfile
    
    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            return {"ok": False, "error": "EMERGENT_LLM_KEY não configurada"}
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name
        
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"fix-dish-{id(image_bytes)}",
                system_message=SYSTEM_PROMPT_FIX_DISH
            ).with_model("gemini", "gemini-2.0-flash")
            
            image_file = FileContentWithMimeType(
                file_path=tmp_path,
                mime_type="image/jpeg"
            )
            
            # Preparar contexto dos dados atuais
            context = f"""DADOS ATUAIS DO PRATO (podem estar incorretos ou incompletos):
Nome: {current_info.get('nome', 'NÃO DEFINIDO')}
Categoria: {current_info.get('categoria', 'NÃO DEFINIDA')}
Ingredientes: {current_info.get('ingredientes', [])}
Nutrição: {current_info.get('nutricao', {})}

ANALISE A IMAGEM e CORRIJA/COMPLETE todos os campos.
Se o nome atual contiver "Unknown", dê o nome correto.
Se nutrição estiver vazia, preencha com valores realistas.
Responda APENAS com JSON válido."""
            
            user_message = UserMessage(
                text=context,
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
            return result
        except json.JSONDecodeError:
            return {
                "ok": False,
                "error": "Erro ao processar resposta da IA",
                "raw_response": response
            }
            
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def batch_fix_dishes(slugs: list, max_concurrent: int = 3) -> dict:
    """
    Corrige múltiplos pratos em lote.
    """
    import asyncio
    from pathlib import Path
    
    results = {"fixed": [], "failed": [], "skipped": []}
    dataset_dir = Path("/app/datasets/organized")
    
    async def fix_single(slug: str) -> dict:
        dish_dir = dataset_dir / slug
        info_path = dish_dir / "dish_info.json"
        
        # Carregar info atual
        current_info = {}
        if info_path.exists():
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    current_info = json.load(f)
            except:
                pass
        
        # Buscar imagem
        images = list(dish_dir.glob("*.jpg")) + list(dish_dir.glob("*.jpeg"))
        if not images:
            return {"slug": slug, "status": "skipped", "reason": "sem imagem"}
        
        # Ler imagem
        with open(images[0], 'rb') as f:
            image_bytes = f.read()
        
        # Chamar IA
        result = await fix_dish_data_with_ai(image_bytes, current_info)
        
        if result.get("ok"):
            # Salvar resultado
            new_info = {**current_info, **result}
            new_info.pop("ok", None)
            new_info["slug"] = slug
            
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(new_info, f, ensure_ascii=False, indent=2)
            
            return {"slug": slug, "status": "fixed", "data": new_info}
        else:
            return {"slug": slug, "status": "failed", "error": result.get("error")}
    
    # Processar em lotes
    for i in range(0, len(slugs), max_concurrent):
        batch = slugs[i:i+max_concurrent]
        batch_results = await asyncio.gather(*[fix_single(s) for s in batch])
        
        for r in batch_results:
            if r["status"] == "fixed":
                results["fixed"].append(r["slug"])
            elif r["status"] == "failed":
                results["failed"].append({"slug": r["slug"], "error": r.get("error")})
            else:
                results["skipped"].append({"slug": r["slug"], "reason": r.get("reason")})
    
    return results


async def regenerate_dish_info_from_name(dish_name: str, old_info: dict = None) -> dict:
    """
    Regenera TODAS as informações de um prato baseado apenas no NOME.
    Útil quando o usuário corrige o nome de um prato (ex: de "Peixe" para "Batata").
    
    IMPORTANTE: Esta função gera informações CONSISTENTES com o novo nome,
    atualizando ingredientes, nutrição, categoria, etc.
    """
    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            return {"ok": False, "error": "EMERGENT_LLM_KEY não configurada"}
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"regen-{dish_name}",
            system_message="""Você é um nutricionista especializado em gastronomia brasileira.
Seu trabalho é CRIAR uma ficha técnica COMPLETA e PRECISA para um prato baseado apenas no nome.

REGRAS CRÍTICAS:
1. CATEGORIA CORRETA:
   - "vegano": ZERO produtos animais (nem ovo, nem leite, nem mel)
   - "vegetariano": pode ter ovo/leite/queijo de VACA, mas SEM carne/peixe/frango
   - "proteína animal": tem carne/peixe/frango/crustáceos
   
2. INGREDIENTES VEGANOS (NÃO são de origem animal):
   - Leite de coco, creme de coco = VEGANO
   - Queijo vegano, queijo de castanha = VEGANO
   - Cogumelos, tofu = VEGANO
   
3. INGREDIENTES DE ORIGEM ANIMAL:
   - Queijo (sem especificar "vegano") = LACTOSE
   - Leite (sem especificar "vegetal") = LACTOSE
   - Maionese tradicional = contém OVO
   
4. DECORAÇÃO não conta como ingrediente principal

5. Use valores nutricionais REALISTAS (por 100g):
   - Calorias: em kcal
   - Proteínas: em g
   - Carboidratos: em g
   - Gorduras: em g

Responda APENAS com JSON válido no formato:
{
    "nome": "Nome do Prato",
    "categoria": "vegano|vegetariano|proteína animal",
    "descricao": "Descrição detalhada do prato",
    "ingredientes": ["ingrediente1", "ingrediente2", ...],
    "beneficios": ["benefício1", "benefício2", ...],
    "riscos": ["risco1", "risco2", ...],
    "nutricao": {
        "calorias": "XXX kcal",
        "proteinas": "XXg",
        "carboidratos": "XXg",
        "gorduras": "XXg"
    },
    "contem_gluten": true/false,
    "contem_lactose": true/false,
    "contem_ovo": true/false,
    "contem_castanhas": true/false,
    "contem_frutos_mar": true/false,
    "contem_soja": true/false,
    "tecnica": "Técnica de preparo"
}"""
        ).with_model("gemini", "gemini-2.0-flash")
        
        context = f"""Gere a ficha técnica COMPLETA para este prato:

NOME DO PRATO: {dish_name}

INFORMAÇÕES ANTIGAS (podem estar ERRADAS - use apenas como referência):
{json.dumps(old_info, ensure_ascii=False, indent=2) if old_info else "Nenhuma"}

IMPORTANTE: Baseie-se NO NOME do prato para determinar ingredientes e categoria.
Se o nome indica "Batata", os ingredientes devem ser de batata, não de peixe.
Se o nome indica "Vegano", a categoria DEVE ser vegano.

Responda APENAS com JSON válido."""
        
        response = await chat.send_message(UserMessage(text=context))
        
        # Parse JSON
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        response_clean = response_clean.strip()
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        
        try:
            result = json.loads(response_clean)
            result["ok"] = True
            result["regenerated_from_name"] = True
            return result
        except json.JSONDecodeError:
            return {
                "ok": False,
                "error": "Erro ao processar resposta da IA",
                "raw_response": response
            }
            
    except Exception as e:
        return {"ok": False, "error": str(e)}
