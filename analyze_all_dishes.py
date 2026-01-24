#!/usr/bin/env python3
"""
Script para analisar todos os pratos com IA e gerar informações corretas.
Analisa a FOTO do prato para gerar: ingredientes, descrição, benefícios, riscos, categoria.
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, '/app/backend')

async def analyze_dish(dish_dir: Path):
    """Analisa um prato usando a foto e gera informações."""
    from services.generic_ai import identify_unknown_dish
    
    slug = dish_dir.name
    info_file = dish_dir / "dish_info.json"
    
    # Buscar primeira imagem
    images = list(dish_dir.glob("*.jpg")) + list(dish_dir.glob("*.jpeg"))
    if not images:
        return None, "Sem imagem"
    
    # Ler imagem
    with open(images[0], "rb") as f:
        image_bytes = f.read()
    
    # Nome do prato
    nome = slug.replace("_", " ").title()
    
    # Carregar info existente
    existing = {}
    if info_file.exists():
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
                nome = existing.get("nome", nome)
        except:
            pass
    
    # Chamar IA
    try:
        result = await identify_unknown_dish(image_bytes, nome)
        
        if result:
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
