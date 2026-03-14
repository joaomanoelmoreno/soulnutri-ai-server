#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para re-processar os 5 pratos adicionando dados do USDA.
Apenas ADICIONA a fonte USDA e recalcula a media - nao apaga dados existentes.
Roda quando o rate limit do USDA DEMO_KEY resetar.
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


async def main():
    from motor.motor_asyncio import AsyncIOMotorClient
    from services.nutrition_3sources import query_usda, NUTRIENT_KEYS

    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "soulnutri")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # Test USDA availability first
    import httpx
    resp = httpx.get(
        "https://api.nal.usda.gov/fdc/v1/foods/search",
        params={"api_key": os.environ.get("USDA_API_KEY", "DEMO_KEY"), "query": "grape", "pageSize": 1},
        timeout=10,
    )
    if resp.status_code == 429:
        print("USDA ainda bloqueado (429). Tente novamente mais tarde.")
        client.close()
        return
    print(f"USDA disponivel (status: {resp.status_code})")

    # Process each dish
    async for doc in db.nutrition_sheets.find({}, {"_id": 0}):
        nome = doc["nome"]
        ingredientes = doc.get("ingredientes", [])
        existing_sources = doc.get("detalhes_fontes", {})

        if "USDA" in existing_sources:
            print(f"SKIP: {nome} - ja tem USDA")
            continue

        print(f"\nProcessando: {nome} ({len(ingredientes)} ingredientes)...")
        usda_data = await query_usda(nome, ingredientes)

        if usda_data:
            existing_sources["USDA"] = {k: usda_data.get(k, 0) for k in NUTRIENT_KEYS}
            existing_sources["USDA"]["cobertura"] = usda_data.get("cobertura", 0)

            # Recalculate average
            num_fontes = len(existing_sources)
            media = {}
            for k in NUTRIENT_KEYS:
                values = [src[k] for src in existing_sources.values() if src.get(k, 0) > 0]
                media[k] = round(sum(values) / len(values), 1) if values else 0.0

            fontes_usadas = list(existing_sources.keys())

            await db.nutrition_sheets.update_one(
                {"nome": nome},
                {"$set": {
                    **media,
                    "num_fontes": num_fontes,
                    "fontes_usadas": fontes_usadas,
                    "fonte_principal": f"Media de {num_fontes} fontes ({', '.join(fontes_usadas)})",
                    "detalhes_fontes": existing_sources,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
            print(f"  ATUALIZADO: {nome} - agora com {num_fontes} fontes")
            print(f"  USDA calorias: {usda_data.get('calorias_kcal')} kcal")
        else:
            print(f"  USDA nao retornou dados para: {nome}")

        await asyncio.sleep(3)  # Be respectful with rate limits

    # Final summary
    print("\n=== RESUMO FINAL ===")
    async for doc in db.nutrition_sheets.find({}, {"_id": 0, "nome": 1, "calorias_kcal": 1, "num_fontes": 1, "fontes_usadas": 1}):
        print(f"  {doc['nome']}: {doc['calorias_kcal']}kcal ({doc['num_fontes']} fontes: {', '.join(doc['fontes_usadas'])})")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
