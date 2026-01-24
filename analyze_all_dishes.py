#!/usr/bin/env python3
"""
Script para analisar todos os pratos com IA e gerar informações corretas.
Analisa a FOTO do prato para gerar: ingredientes, descrição, benefícios, riscos, categoria.
"""
import os
import sys
import json
import asyncio
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do backend
load_dotenv('/app/backend/.env')

# Adicionar backend ao path
sys.path.insert(0, '/app/backend')

from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType

SYSTEM_PROMPT_ANALYZE = """Você é o SoulNutri, especialista em nutrição brasileira.

Analise a imagem do prato e retorne informações PRECISAS e DETALHADAS.

REGRAS DE CATEGORIA:
- "vegano": ZERO produtos animais (sem carne, peixe, ovo, leite, queijo)
- "vegetariano": tem ovo/leite/queijo, SEM carne/peixe
- "proteína animal": tem carne, peixe, frango, frutos do mar

IMPORTANTE:
- Seja ESPECÍFICO nos ingredientes (ex: "azeite de oliva", não apenas "óleo")
- Descreva o modo de preparo visível (grelhado, refogado, cozido, etc.)
- Identifique TODOS os ingredientes visíveis
- Dê informações úteis e não óbvias

Retorne JSON:
{
    "nome": "Nome completo do prato",
    "categoria": "vegano|vegetariano|proteína animal",
    "ingredientes": ["ingrediente1", "ingrediente2", "ingrediente3"],
    "descricao": "Descrição detalhada do prato e preparo",
    "beneficios": ["Benefício 1 específico", "Benefício 2"],
    "riscos": ["Contém glúten", "Alérgeno: crustáceos"],
    "curiosidade": "Fato interessante sobre o prato ou ingrediente principal"
}"""

async def analyze_dish_with_ai(image_path: str, dish_name: str) -> dict:
    """Analisa uma imagem de prato usando Gemini Vision."""
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise Exception("EMERGENT_LLM_KEY não configurada")
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"analyze-{dish_name[:20]}",
        system_message=SYSTEM_PROMPT_ANALYZE
    ).with_model("gemini", "gemini-2.0-flash-lite")
    
    image_file = FileContentWithMimeType(
        file_path=image_path,
        mime_type="image/jpeg"
    )
    
    user_message = UserMessage(
        text=f"Analise este prato chamado '{dish_name}'. Identifique ingredientes, categoria e informações nutricionais. Responda APENAS JSON.",
        file_contents=[image_file]
    )
    
    response = await chat.send_message(user_message)
    
    # Parse JSON
    response_clean = response.strip()
    if response_clean.startswith("```"):
        response_clean = response_clean.split("```")[1]
        if response_clean.startswith("json"):
            response_clean = response_clean[4:]
    response_clean = response_clean.strip()
    
    return json.loads(response_clean)

async def analyze_dish(dish_dir: Path):
    """Analisa um prato usando a foto e gera informações."""
    slug = dish_dir.name
    info_file = dish_dir / "dish_info.json"
    
    # Buscar primeira imagem
    images = list(dish_dir.glob("*.jpg")) + list(dish_dir.glob("*.jpeg")) + list(dish_dir.glob("*.png"))
    if not images:
        return None, "Sem imagem"
    
    # Nome do prato
    nome = slug.replace("_", " ").title()
    
    # Carregar info existente para pegar nome correto
    existing = {}
    if info_file.exists():
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
                nome = existing.get("nome", nome)
        except:
            pass
    
    # Chamar IA usando o arquivo diretamente
    try:
        result = await analyze_dish_with_ai(str(images[0]), nome)
        
        if result:
            # Garantir que nome seja preservado
            result["nome"] = nome
            result["slug"] = slug
            
            # Manter nutrição em branco conforme solicitado
            result["nutricao"] = {
                "calorias": "",
                "proteinas": "",
                "carboidratos": "",
                "gorduras": ""
            }
            
            # Salvar
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result, "OK"
        else:
            return None, "IA retornou vazio"
    except Exception as e:
        return None, str(e)

async def main():
    base_dir = Path("/app/datasets/organized")
    
    # Listar todos os pratos
    dishes = sorted([d for d in base_dir.iterdir() if d.is_dir()])
    total = len(dishes)
    
    print(f"📊 Analisando {total} pratos com IA...")
    print("=" * 50)
    
    success = 0
    errors = []
    
    for i, dish_dir in enumerate(dishes, 1):
        slug = dish_dir.name
        print(f"[{i}/{total}] {slug[:40]}...", end=" ", flush=True)
        
        result, status = await analyze_dish(dish_dir)
        
        if result:
            cat = result.get("categoria", "?")
            ing_count = len(result.get("ingredientes", []))
            print(f"✅ {cat} | {ing_count} ingredientes")
            success += 1
        else:
            print(f"❌ {status}")
            errors.append((slug, status))
        
        # Pequena pausa para não sobrecarregar
        await asyncio.sleep(0.5)
    
    print("=" * 50)
    print(f"✅ {success}/{total} pratos analisados com sucesso")
    
    if errors:
        print(f"\n❌ {len(errors)} erros:")
        for slug, err in errors[:10]:
            print(f"   - {slug}: {err}")

if __name__ == "__main__":
    asyncio.run(main())
