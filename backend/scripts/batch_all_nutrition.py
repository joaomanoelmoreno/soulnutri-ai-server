# -*- coding: utf-8 -*-
"""
Script para gerar fichas nutricionais de TODOS os pratos restantes.
SEGURO: Só atualiza campo 'nutricao' no dish_info.json. Nao toca em nada mais.
"""
import os, sys, json, asyncio, time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

from services.nutrition_3sources import generate_nutrition_3sources, DISH_USDA_QUERY, DISH_OFF_CATEGORY
from pymongo import MongoClient

# Conectar MongoDB
mongo_url = os.environ.get("MONGO_URL")
db_name = os.environ.get("DB_NAME", "soulnutri")
client = MongoClient(mongo_url)
db = client[db_name]

# Pegar lista de pratos JA processados
existing = set()
for doc in db.nutrition_sheets.find({}, {"_id": 0, "nome": 1, "slug": 1}):
    existing.add(doc.get("nome", ""))
    existing.add(doc.get("slug", ""))

print(f"Ja processados: {len(existing)} nomes/slugs no MongoDB")

# Listar TODOS os pratos do dataset
dataset_dir = Path("/app/datasets/organized")
all_dishes = []

for folder in sorted(dataset_dir.iterdir()):
    if not folder.is_dir():
        continue
    info_file = folder / "dish_info.json"
    if not info_file.exists():
        continue
    
    folder_name = folder.name
    
    # Verificar se ja foi processado
    with open(info_file, "r", encoding="utf-8") as f:
        info = json.load(f)
    
    nome = info.get("nome", folder_name)
    
    if nome in existing or folder_name in existing:
        continue
    
    ingredientes = [i for i in info.get("ingredientes", []) if i and i.strip()]
    
    all_dishes.append({
        "nome": nome,
        "folder": folder_name,
        "ingredientes": ingredientes,
        "info_file": str(info_file),
    })

print(f"Pratos a processar: {len(all_dishes)}")
print(f"{'='*60}")

LOG_FILE = "/tmp/nutrition_batch.log"

async def process_all():
    ok_count = 0
    fail_count = 0
    skip_count = 0
    start = time.time()
    
    with open(LOG_FILE, "w") as log:
        log.write(f"INICIO: {datetime.now().isoformat()}\n")
        log.write(f"Total a processar: {len(all_dishes)}\n\n")
    
    for i, dish in enumerate(all_dishes):
        nome = dish["nome"]
        folder = dish["folder"]
        ingredientes = dish["ingredientes"]
        
        progress = f"[{i+1}/{len(all_dishes)}]"
        
        if not ingredientes:
            msg = f"{progress} SKIP (sem ingredientes): {nome}"
            print(msg)
            skip_count += 1
            with open(LOG_FILE, "a") as log:
                log.write(msg + "\n")
            continue
        
        try:
            result = await generate_nutrition_3sources(nome, ingredientes)
            
            if not result:
                msg = f"{progress} FAIL (sem dados): {nome}"
                print(msg)
                fail_count += 1
                with open(LOG_FILE, "a") as log:
                    log.write(msg + "\n")
                continue
            
            now = datetime.now(timezone.utc).isoformat()
            
            # Salvar no MongoDB
            sheet = {
                **result,
                "slug": folder,
                "nomes_alternativos": [nome],
                "metodo": "media_3_fontes_v1.24_batch",
                "gerado_em": now,
                "updated_at": now,
            }
            db.nutrition_sheets.update_one(
                {"nome": nome},
                {"$set": sheet},
                upsert=True
            )
            
            # Atualizar APENAS nutricao no dish_info.json
            info_path = Path(dish["info_file"])
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            
            info["nutricao"] = {
                "calorias": f"{result['calorias_kcal']:.0f} kcal",
                "proteinas": f"{result['proteinas_g']:.1f}g",
                "carboidratos": f"{result['carboidratos_g']:.1f}g",
                "gorduras": f"{result['gorduras_g']:.1f}g",
                "fibras": f"{result['fibras_g']:.1f}g",
                "sodio": f"{result.get('sodio_mg', 0):.0f}mg",
                "fonte": result.get("fonte_principal", ""),
            }
            
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            
            fontes = ", ".join(result["fontes_usadas"])
            msg = f"{progress} OK: {nome} -> {result['calorias_kcal']:.0f} kcal | {fontes}"
            print(msg)
            ok_count += 1
            
            with open(LOG_FILE, "a") as log:
                log.write(msg + "\n")
            
            # Pausa entre chamadas para nao sobrecarregar USDA
            await asyncio.sleep(0.3)
            
        except Exception as e:
            msg = f"{progress} ERROR: {nome} -> {str(e)}"
            print(msg)
            fail_count += 1
            with open(LOG_FILE, "a") as log:
                log.write(msg + "\n")
    
    elapsed = time.time() - start
    
    summary = f"""
{'='*60}
RESULTADO FINAL
{'='*60}
OK:    {ok_count}
FAIL:  {fail_count}
SKIP:  {skip_count}
Total: {len(all_dishes)}
Tempo: {elapsed:.0f}s ({elapsed/60:.1f} min)
{'='*60}
"""
    print(summary)
    
    with open(LOG_FILE, "a") as log:
        log.write(summary)
    
    # Salvar status final
    with open("/tmp/nutrition_batch_status.json", "w") as f:
        json.dump({
            "completed": True,
            "ok": ok_count,
            "fail": fail_count,
            "skip": skip_count,
            "total": len(all_dishes),
            "elapsed_seconds": round(elapsed),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, f)
    
    client.close()

asyncio.run(process_all())
