# -*- coding: utf-8 -*-
"""
Script de migração de imagens do disco local para Emergent Object Storage.
Processa todos os pratos do dataset, faz upload das imagens e salva os paths no MongoDB.
"""
import os, sys, json, time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

from services.storage_service import init_storage, upload_dish_image
from pymongo import MongoClient

# Conectar MongoDB
client = MongoClient(os.environ.get("MONGO_URL"))
db_name = os.environ.get("DB_NAME", "soulnutri")
db = client[db_name]

dataset_dir = Path("/app/datasets/organized")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
LOG_FILE = "/tmp/storage_migration.log"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def main():
    # Inicializar storage
    init_storage()
    log(f"MIGRAÇÃO INICIADA: {datetime.now().isoformat()}")
    
    # Listar todas as pastas de pratos
    folders = sorted([
        f for f in dataset_dir.iterdir()
        if f.is_dir() and (f / "dish_info.json").exists()
    ])
    
    log(f"Total de pratos: {len(folders)}")
    
    total_uploaded = 0
    total_failed = 0
    total_skipped = 0
    start_time = time.time()
    
    for i, folder in enumerate(folders):
        dish_slug = folder.name
        
        # Verificar se já foi migrado
        existing = db.dish_storage.find_one({"slug": dish_slug}, {"_id": 0, "images": 1})
        if existing and existing.get("images"):
            total_skipped += len(existing["images"])
            continue
        
        # Listar imagens na pasta
        images = sorted([
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ])
        
        if not images:
            continue
        
        uploaded_images = []
        
        for img in images:
            try:
                data = img.read_bytes()
                path = upload_dish_image(dish_slug, img.name, data)
                uploaded_images.append({
                    "filename": img.name,
                    "storage_path": path,
                    "size": len(data),
                })
                total_uploaded += 1
            except Exception as e:
                log(f"  ERRO: {dish_slug}/{img.name}: {e}")
                total_failed += 1
        
        # Salvar paths no MongoDB
        if uploaded_images:
            db.dish_storage.update_one(
                {"slug": dish_slug},
                {"$set": {
                    "slug": dish_slug,
                    "images": uploaded_images,
                    "count": len(uploaded_images),
                    "migrated_at": datetime.now(timezone.utc).isoformat(),
                }},
                upsert=True
            )
        
        progress = f"[{i+1}/{len(folders)}]"
        log(f"{progress} {dish_slug}: {len(uploaded_images)} imagens OK")
    
    elapsed = time.time() - start_time
    
    summary = f"""
{'='*60}
MIGRAÇÃO COMPLETA
{'='*60}
Uploaded: {total_uploaded}
Failed:   {total_failed}
Skipped:  {total_skipped} (já migrados)
Tempo:    {elapsed:.0f}s ({elapsed/60:.1f} min)
{'='*60}
"""
    log(summary)
    
    # Salvar status
    with open("/tmp/storage_migration_status.json", "w") as f:
        json.dump({
            "completed": True,
            "uploaded": total_uploaded,
            "failed": total_failed,
            "skipped": total_skipped,
            "elapsed_seconds": round(elapsed),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, f)
    
    client.close()

if __name__ == "__main__":
    main()
