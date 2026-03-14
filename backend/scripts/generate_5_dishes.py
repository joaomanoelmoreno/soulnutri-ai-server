#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar fichas nutricionais dos 5 pratos usando 3 fontes.
Executa de forma isolada, sem alterar nenhum outro componente.

Pratos: Tortinha de Figo e Gorgonzola, Umami de Tomates, Uva,
        Vinagrete de Lula, Vol Au Vent
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

TARGET_DISHES = [
    "Tortinha de Gorgonzola e Figo",
    "Umami de Tomates",
    "Uva",
    "Vinagrete de Lula",
    "Vol Au Vent",
]


async def main():
    from motor.motor_asyncio import AsyncIOMotorClient
    from services.nutrition_3sources import generate_nutrition_3sources

    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "soulnutri")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # PASSO 1: Deletar TODAS as fichas nutricionais existentes
    count_before = await db.nutrition_sheets.count_documents({})
    print(f"\n{'='*60}")
    if count_before > 0:
        print(f"DELETANDO {count_before} fichas nutricionais existentes...")
        result = await db.nutrition_sheets.delete_many({})
        print(f"Deletados: {result.deleted_count} registros")
    count_after = await db.nutrition_sheets.count_documents({})
    print(f"Registros no banco: {count_after}")
    print(f"{'='*60}\n")

    # PASSO 2: Carregar dados dos pratos
    pratos_para_processar = []
    for folder_name in TARGET_DISHES:
        info_path = f"/app/datasets/organized/{folder_name}/dish_info.json"
        if os.path.exists(info_path):
            with open(info_path, encoding="utf-8") as f:
                info = json.load(f)
            nome = info.get("nome", folder_name)
            ingredientes = [i for i in info.get("ingredientes", []) if i.strip()]
            pratos_para_processar.append({
                "folder": folder_name,
                "nome": nome,
                "ingredientes": ingredientes,
            })
            print(f"OK: {nome} ({len(ingredientes)} ingredientes)")
        else:
            print(f"ERRO: {folder_name} - dish_info.json nao encontrado")

    print(f"\n{'='*60}")
    print(f"PROCESSANDO {len(pratos_para_processar)} PRATOS COM 3 FONTES")
    print(f"{'='*60}\n")

    # PASSO 3: Gerar fichas nutricionais
    resultados = []
    for i, prato in enumerate(pratos_para_processar, 1):
        print(f"\n--- [{i}/{len(pratos_para_processar)}] {prato['nome']} ---")
        print(f"  Ingredientes: {', '.join(prato['ingredientes'][:5])}...")

        try:
            sheet = await generate_nutrition_3sources(
                prato["nome"],
                prato["ingredientes"]
            )

            if sheet:
                # Adicionar metadados
                sheet["gerado_em"] = datetime.now(timezone.utc).isoformat()
                sheet["updated_at"] = datetime.now(timezone.utc).isoformat()
                sheet["metodo"] = "media_3_fontes_v1.23"

                # Salvar no MongoDB
                await db.nutrition_sheets.update_one(
                    {"nome": sheet["nome"]},
                    {"$set": sheet},
                    upsert=True,
                )
                print(f"  SALVO: {sheet['nome']}")
                print(f"  Fontes: {sheet['fontes_usadas']}")
                print(f"  Calorias: {sheet['calorias_kcal']} kcal")
                print(f"  Proteinas: {sheet['proteinas_g']}g")
                print(f"  Carboidratos: {sheet['carboidratos_g']}g")
                print(f"  Gorduras: {sheet['gorduras_g']}g")

                # Mostrar detalhes por fonte
                for src_name, src_vals in sheet.get("detalhes_fontes", {}).items():
                    cal = src_vals.get("calorias_kcal", "?")
                    cov = src_vals.get("cobertura", "?")
                    print(f"    {src_name}: {cal} kcal (cobertura: {cov}%)")

                resultados.append(sheet)
            else:
                print(f"  ERRO: Nenhuma fonte retornou dados para {prato['nome']}")

        except Exception as e:
            print(f"  ERRO: {e}")

        # Pausa entre pratos
        await asyncio.sleep(1)

    # PASSO 4: Resumo
    print(f"\n{'='*60}")
    print(f"RESULTADO: {len(resultados)}/{len(pratos_para_processar)} fichas geradas")
    total_db = await db.nutrition_sheets.count_documents({})
    print(f"Total no MongoDB: {total_db} registros")
    print(f"{'='*60}")

    # PASSO 5: Verificacao de integridade
    print(f"\n--- VERIFICACAO DE INTEGRIDADE ---")
    all_sheets = []
    async for doc in db.nutrition_sheets.find({}, {"_id": 0}):
        all_sheets.append(doc)
    for s in all_sheets:
        print(f"  {s['nome']}: {s['calorias_kcal']}kcal | "
              f"{s['proteinas_g']}g prot | "
              f"{s['carboidratos_g']}g carb | "
              f"{s['gorduras_g']}g gord | "
              f"Fontes: {s.get('num_fontes', '?')}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
