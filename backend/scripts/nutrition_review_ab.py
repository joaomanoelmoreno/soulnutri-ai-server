#!/usr/bin/env python3
"""
Revisão Nutricional Inteligente - SoulNutri
============================================
Usa Gemini Flash para determinar proporções REAIS dos ingredientes
e TACO para calcular a nutrição com essas proporções.
"""
import os
import sys
import json
import asyncio
from datetime import datetime, timezone

sys.path.insert(0, '/app/backend')
os.chdir('/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from data.taco_database import buscar_dados_taco, TACO_DATABASE

import pymongo


def get_dishes_ab():
    """Busca pratos A e B do banco."""
    client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
    db = client[os.environ.get("DB_NAME", "soulnutri")]
    dishes = list(db.dishes.find(
        {"$or": [{"slug": {"$regex": "^a"}}, {"slug": {"$regex": "^b"}}]},
        {"_id": 0, "slug": 1, "name": 1, "ingredients": 1, "nutrition": 1, "category": 1}
    ).sort("slug", 1))
    client.close()
    return dishes


async def get_proportions_from_gemini(dish_name, ingredients):
    """Usa Gemini para determinar proporções realistas por 100g."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        return None
    
    ing_list = ", ".join(ingredients)
    prompt = f"""Você é um nutricionista brasileiro especialista em gastronomia. 
Para o prato "{dish_name}" com os ingredientes [{ing_list}], determine a proporção REALISTA em gramas de cada ingrediente para uma porção de 100g.

REGRAS:
- A soma DEVE ser exatamente 100g
- Use bom senso culinário (temperos = 1-3g, ingredientes base = 40-80g, etc.)
- Considere como o prato é realmente feito na culinária brasileira
- Retorne APENAS um JSON, sem texto adicional

Formato de resposta (APENAS JSON):
{{"ingredientes": [{{"nome": "ingrediente1", "gramas": 70}}, {{"nome": "ingrediente2", "gramas": 20}}, {{"nome": "ingrediente3", "gramas": 10}}]}}"""

    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"nutri-review-{int(datetime.now().timestamp())}",
            system_message="Você é um nutricionista brasileiro. Responda APENAS em JSON válido."
        ).with_model("gemini", "gemini-2.0-flash-lite")
        
        response = await chat.send_message(UserMessage(text=prompt))
        # emergentintegrations returns string directly
        text = response.strip() if isinstance(response, str) else response.text.strip()
        
        # Clean response - extract JSON
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        
        data = json.loads(text)
        return data.get("ingredientes", [])
    except Exception as e:
        print(f"  [GEMINI ERROR] {dish_name}: {e}")
        return None


def calculate_nutrition_with_proportions(ingredients_with_grams):
    """Calcula nutrição usando TACO com proporções reais."""
    totais = {
        "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, 
        "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "vitamina_c": 0,
        "potassio": 0, "zinco": 0,
        "ingredientes_encontrados": [], "ingredientes_nao_encontrados": []
    }
    
    for item in ingredients_with_grams:
        nome = item["nome"]
        gramas = item["gramas"]
        dados = buscar_dados_taco(nome)
        
        if dados:
            fator = gramas / 100  # TACO values are per 100g
            for key in ["calorias", "proteinas", "carboidratos", "gorduras", "fibras",
                       "sodio", "calcio", "ferro", "vitamina_c", "potassio", "zinco"]:
                totais[key] += dados.get(key, 0) * fator
            totais["ingredientes_encontrados"].append(f"{nome} ({gramas}g)")
        else:
            totais["ingredientes_nao_encontrados"].append(f"{nome} ({gramas}g)")
    
    return totais


def detect_category(ingredients):
    """Detecta categoria com base nos ingredientes."""
    ing_text = " ".join(ingredients).lower()
    
    animais = ['frango', 'carne', 'boi', 'porco', 'bacon', 'peixe', 'camarao',
               'atum', 'salmao', 'bacalhau', 'costela', 'linguica', 'presunto',
               'file', 'sobrecoxa', 'peito de frango', 'maminha', 'alcatra',
               'lombo', 'pernil', 'polvo', 'lula', 'sardinha']
    vegetarianos = ['ovo', 'leite', 'queijo', 'manteiga', 'creme de leite', 
                    'iogurte', 'requeijao', 'parmesao', 'mussarela', 'gorgonzola']
    veganos_ok = ['leite de coco', 'leite de soja', 'queijo vegano', 'manteiga vegetal']
    
    for ing in animais:
        if ing in ing_text:
            return "proteina animal"
    
    for ing in vegetarianos:
        if ing in ing_text:
            is_vegan = any(v in ing_text for v in veganos_ok)
            if not is_vegan:
                return "vegetariano"
    
    return "vegano"


def parse_nutrition_value(val):
    """Converte strings como '123 kcal' ou '4.5g' para float."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        return float(''.join(c for c in val if c.isdigit() or c == '.') or '0')
    return 0


async def review_all_ab():
    """Revisa todos os pratos A e B."""
    dishes = get_dishes_ab()
    print(f"\n{'='*80}")
    print(f"  REVISÃO NUTRICIONAL - PRATOS A e B ({len(dishes)} pratos)")
    print(f"{'='*80}\n")
    
    results = []
    
    for i, dish in enumerate(dishes, 1):
        slug = dish["slug"]
        name = dish.get("name") or slug
        ingredients = dish.get("ingredients", [])
        old_nutrition = dish.get("nutrition", {})
        old_category = dish.get("category", "")
        if isinstance(old_category, list):
            old_category = old_category[0] if old_category else ""
        
        print(f"\n[{i}/{len(dishes)}] {name} ({slug})")
        print(f"  Ingredientes: {ingredients}")
        
        if not ingredients or len(ingredients) == 0:
            print(f"  ⚠️ SEM INGREDIENTES - pulando")
            results.append({
                "slug": slug, "name": name,
                "status": "SEM_INGREDIENTES",
                "divergencias": ["Prato sem ingredientes cadastrados"]
            })
            continue
        
        # Get proportions from Gemini
        proportions = await get_proportions_from_gemini(name, ingredients)
        
        if not proportions:
            print(f"  ⚠️ Gemini não retornou proporções - usando fallback")
            # Fallback: ingredient-role-based estimation
            proportions = [{"nome": ing, "gramas": round(100/len(ingredients), 1)} for ing in ingredients]
        
        print(f"  Proporções:")
        for p in proportions:
            print(f"    - {p['nome']}: {p['gramas']}g")
        
        # Calculate with TACO
        new_nutrition = calculate_nutrition_with_proportions(proportions)
        new_category = detect_category(ingredients)
        
        # Compare with existing
        divergencias = []
        
        old_cal = parse_nutrition_value(old_nutrition.get("calorias", 0))
        new_cal = new_nutrition["calorias"]
        
        if old_cal > 0 and abs(old_cal - new_cal) > 30:
            divergencias.append(f"Calorias: {old_cal:.0f} → {new_cal:.0f} kcal (diff: {abs(old_cal-new_cal):.0f})")
        elif old_cal == 0:
            divergencias.append(f"Calorias: SEM DADOS → {new_cal:.0f} kcal")
        
        old_prot = parse_nutrition_value(old_nutrition.get("proteinas", 0))
        new_prot = new_nutrition["proteinas"]
        if old_prot > 0 and abs(old_prot - new_prot) > 3:
            divergencias.append(f"Proteínas: {old_prot:.1f}g → {new_prot:.1f}g")
        
        old_carb = parse_nutrition_value(old_nutrition.get("carboidratos", 0))
        new_carb = new_nutrition["carboidratos"]
        if old_carb > 0 and abs(old_carb - new_carb) > 5:
            divergencias.append(f"Carboidratos: {old_carb:.1f}g → {new_carb:.1f}g")
        
        old_gord = parse_nutrition_value(old_nutrition.get("gorduras", 0))
        new_gord = new_nutrition["gorduras"]
        if old_gord > 0 and abs(old_gord - new_gord) > 3:
            divergencias.append(f"Gorduras: {old_gord:.1f}g → {new_gord:.1f}g")
        
        if old_category and old_category != new_category:
            divergencias.append(f"Categoria: '{old_category}' → '{new_category}'")
        
        if new_nutrition["ingredientes_nao_encontrados"]:
            divergencias.append(f"Não encontrados na TACO: {new_nutrition['ingredientes_nao_encontrados']}")
        
        status = "DIVERGENTE" if divergencias else "OK"
        
        result = {
            "slug": slug,
            "name": name,
            "status": status,
            "proporcoes": proportions,
            "nova_nutricao": {
                "calorias": f"{new_nutrition['calorias']:.0f} kcal",
                "proteinas": f"{new_nutrition['proteinas']:.1f}g",
                "carboidratos": f"{new_nutrition['carboidratos']:.1f}g",
                "gorduras": f"{new_nutrition['gorduras']:.1f}g",
                "fibras": f"{new_nutrition['fibras']:.1f}g",
                "sodio": f"{new_nutrition['sodio']:.0f}mg",
                "calcio": f"{new_nutrition['calcio']:.0f}mg",
                "ferro": f"{new_nutrition['ferro']:.1f}mg",
                "vitamina_c": f"{new_nutrition['vitamina_c']:.1f}mg"
            },
            "antiga_nutricao": old_nutrition,
            "nova_categoria": new_category,
            "antiga_categoria": old_category,
            "divergencias": divergencias,
            "taco_match": new_nutrition["ingredientes_encontrados"],
            "taco_miss": new_nutrition["ingredientes_nao_encontrados"]
        }
        results.append(result)
        
        if divergencias:
            print(f"  ⚠️ DIVERGÊNCIAS:")
            for d in divergencias:
                print(f"    - {d}")
        else:
            print(f"  ✅ OK (sem divergências significativas)")
        
        print(f"  Nova nutrição: {new_nutrition['calorias']:.0f} kcal | P:{new_nutrition['proteinas']:.1f}g | C:{new_nutrition['carboidratos']:.1f}g | G:{new_nutrition['gorduras']:.1f}g")
    
    # Save report
    report = {
        "data": datetime.now(timezone.utc).isoformat(),
        "total_pratos": len(dishes),
        "divergentes": sum(1 for r in results if r["status"] == "DIVERGENTE"),
        "sem_ingredientes": sum(1 for r in results if r["status"] == "SEM_INGREDIENTES"),
        "ok": sum(1 for r in results if r["status"] == "OK"),
        "resultados": results
    }
    
    report_path = "/app/backend/scripts/nutrition_review_AB.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"  RESUMO:")
    print(f"  Total: {report['total_pratos']} | Divergentes: {report['divergentes']} | OK: {report['ok']} | Sem ingredientes: {report['sem_ingredientes']}")
    print(f"  Relatório salvo em: {report_path}")
    print(f"{'='*80}")
    
    return report


if __name__ == "__main__":
    report = asyncio.run(review_all_ab())
