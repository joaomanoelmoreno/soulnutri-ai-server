# -*- coding: utf-8 -*-
"""
Script para gerar fichas nutricionais de pratos ESPECÍFICOS.
SEGURO: Só toca nos pratos listados, nada mais.
"""
import os, sys, json, asyncio
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

from services.nutrition_3sources import generate_nutrition_3sources, DISH_USDA_QUERY, DISH_OFF_CATEGORY
from pymongo import MongoClient

# Mapeamentos USDA para os novos pratos
DISH_USDA_QUERY.update({
    "Tortilha Espanhola de Batata": "spanish omelette potato",
    "Torradas": "toast bread garlic",
    "Torta de Legumes": "vegetable pie quiche",
    "Tabule": "tabbouleh salad",
    "Tomate": "tomato raw",
    "Steak de Couve Flor": "cauliflower steak roasted",
    "Strogonoff (Frango Carne ou Vegano)": "beef stroganoff",
    "Sushi Vietnamita": "vegetable sushi roll",
    "Salpicao de Frango": "chicken salad mayonnaise",
    "Sobrecoxa ao Tandoori": "chicken thigh tandoori",
    "Sobrecoxa ao Limao": "chicken thigh lemon roasted",
    "Vinagrete de Lula": "squid salad vinaigrette",
    "Vol Au Vent (Pimentao ou Espinafre)": "vol au vent pastry spinach",
})

DISH_OFF_CATEGORY.update({
    "Tomate": "en:tomatoes",
    "Torradas": "en:toasts",
    "Tabule": "en:tabbouleh",
})

# Lista EXATA dos pratos a processar
DISHES = {
    "Tortilha Espanhola de Batata": {"folder": "Tortilha Espanhola de Batata"},
    "Torradas": {"folder": "Torradas"},
    "Torta de Legumes": {"folder": "Torta de Legumes"},
    "Tabule": {"folder": "Tabule"},
    "Tomate": {"folder": "Tomate"},
    "Steak de Couve Flor": {"folder": "Steak de Couve Flor"},
    "Strogonoff (Frango Carne ou Vegano)": {"folder": "Strogonoff (Frango Carne ou Vegano)"},
    "Sushi Vietnamita": {"folder": "Sushi Vietnamita"},
    "Salpicao de Frango": {"folder": "Salpicao de Frango"},
    "Sobrecoxa ao Tandoori": {"folder": "Sobrecoxa ao Tandoori"},
    "Sobrecoxa ao Limao": {"folder": "Sobrecoxa ao Limao"},
    "Vinagrete de Lula": {"folder": "Vinagrete de Lula"},
    "Vol Au Vent (Pimentao ou Espinafre)": {"folder": "Vol Au Vent"},
}

async def main():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "soulnutri")
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    dataset_dir = Path("/app/datasets/organized")
    ok_count = 0
    fail_count = 0
    
    for nome, config in DISHES.items():
        folder = dataset_dir / config["folder"]
        info_file = folder / "dish_info.json"
        
        if not info_file.exists():
            print(f"  SKIP: {nome} - sem dish_info.json")
            fail_count += 1
            continue
        
        with open(info_file, "r", encoding="utf-8") as f:
            info = json.load(f)
        
        ingredientes = [i for i in info.get("ingredientes", []) if i.strip()]
        
        # Override para Strogonoff: considerar apenas carne
        if "Strogonoff" in nome:
            ingredientes = ["carne bovina", "creme de leite", "champignon", "cebola", "mostarda", "ketchup", "sal"]
        
        print(f"\n>>> {nome} ({len(ingredientes)} ingredientes)")
        
        result = await generate_nutrition_3sources(nome, ingredientes)
        
        if not result:
            print(f"  FAIL: Nenhuma fonte retornou dados")
            fail_count += 1
            continue
        
        # Adicionar metadados
        now = datetime.now(timezone.utc).isoformat()
        slug = config["folder"]
        
        sheet = {
            **result,
            "slug": slug,
            "nomes_alternativos": [nome],
            "metodo": "media_3_fontes_v1.23_proporcional",
            "gerado_em": now,
            "updated_at": now,
        }
        
        # Salvar no MongoDB - APENAS este prato (upsert por nome)
        db.nutrition_sheets.update_one(
            {"nome": nome},
            {"$set": sheet},
            upsert=True
        )
        
        # Atualizar dish_info.json - APENAS nutricao
        new_nutricao = {
            "calorias": f"{result['calorias_kcal']:.0f} kcal",
            "proteinas": f"{result['proteinas_g']:.1f}g",
            "carboidratos": f"{result['carboidratos_g']:.1f}g",
            "gorduras": f"{result['gorduras_g']:.1f}g",
            "fibras": f"{result['fibras_g']:.1f}g",
            "sodio": f"{result.get('sodio_mg', 0):.0f}mg",
            "fonte": result.get("fonte_principal", ""),
        }
        info["nutricao"] = new_nutricao
        
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        fontes = ", ".join(result["fontes_usadas"])
        print(f"  OK: {result['calorias_kcal']:.0f} kcal | P:{result['proteinas_g']:.1f}g C:{result['carboidratos_g']:.1f}g G:{result['gorduras_g']:.1f}g | {fontes}")
        ok_count += 1
    
    client.close()
    print(f"\n{'='*50}")
    print(f"RESULTADO: {ok_count} OK, {fail_count} falhas de {len(DISHES)} pratos")

asyncio.run(main())
