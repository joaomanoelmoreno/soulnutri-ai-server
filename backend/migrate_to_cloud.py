"""
SoulNutri - Script de Migração de Imagens para Object Storage
=============================================================
Lê as pastas de imagens do disco (fonte da verdade),
faz upload para o Emergent Object Storage, e reconstrói
o MongoDB com dados limpos e corretos.

Uso: python3 migrate_to_cloud.py
"""
import os
import sys
import json
import time
import logging
import requests
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/app/migration_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ CONFIG ============
DATASETS_DIR = Path("/app/datasets/organized")
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "soulnutri"
PROGRESS_FILE = "/app/migration_progress.json"

MIME_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".webp": "image/webp",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# ============ STORAGE FUNCTIONS ============
storage_key = None

def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    resp = requests.post(
        f"{STORAGE_URL}/init",
        json={"emergent_key": EMERGENT_KEY},
        timeout=30
    )
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    logger.info("Storage inicializado com sucesso")
    return storage_key

def upload_image(storage_path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    for attempt in range(3):
        try:
            resp = requests.put(
                f"{STORAGE_URL}/objects/{storage_path}",
                headers={"X-Storage-Key": key, "Content-Type": content_type},
                data=data,
                timeout=120
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < 2:
                logger.warning(f"  Tentativa {attempt+1} falhou: {e}. Retentando...")
                time.sleep(2 * (attempt + 1))
            else:
                raise

# ============ SLUG UTILS ============
def make_clean_slug(folder_name: str) -> str:
    """Gera slug limpo a partir do nome da pasta."""
    import unicodedata
    s = folder_name.strip()
    s = s.replace('_', ' ')
    # Normaliza e remove acentos
    nfkd = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # Lowercase e substitui espaços por hífens
    s = s.lower().strip()
    # Remove caracteres especiais exceto letras, números, espaços e hífens
    s = ''.join(c if c.isalnum() or c in (' ', '-') else '' for c in s)
    # Substitui espaços por hífens
    s = '-'.join(s.split())
    # Remove hífens duplicados
    while '--' in s:
        s = s.replace('--', '-')
    return s.strip('-')

def normalize_for_comparison(s: str) -> str:
    """Normaliza para comparação entre slugs."""
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return s.lower().replace(' ', '').replace('_', '').replace('-', '')

# ============ SCAN DISK ============
def scan_disk():
    """Escaneia o disco e retorna dados consolidados por slug."""
    logger.info(f"Escaneando {DATASETS_DIR}...")
    
    # First pass: collect all folders
    raw_folders = []
    for folder in sorted(DATASETS_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        imgs = sorted([
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ])
        if not imgs:
            continue
        raw_folders.append({
            "folder_name": folder.name,
            "folder_path": folder,
            "images": imgs,
            "count": len(imgs),
            "norm_key": normalize_for_comparison(folder.name),
        })
    
    # Filter out test/junk folders
    junk_prefixes = ['test_action_', 'prato_corrigido_', 'prato_com_']
    clean_folders = []
    junk_folders = []
    for f in raw_folders:
        is_junk = any(f["folder_name"].lower().startswith(p) for p in junk_prefixes)
        is_too_long = len(f["folder_name"]) > 80
        if is_junk or is_too_long:
            junk_folders.append(f)
        else:
            clean_folders.append(f)
    
    if junk_folders:
        logger.info(f"Ignorando {len(junk_folders)} pastas de teste/lixo:")
        for f in junk_folders:
            logger.info(f"  - '{f['folder_name']}' ({f['count']} imgs)")
    
    # Second pass: merge duplicates
    merged = {}  # norm_key -> consolidated data
    for f in clean_folders:
        key = f["norm_key"]
        if key not in merged:
            merged[key] = {
                "display_name": f["folder_name"],
                "images": [],
                "seen_filenames": set(),
            }
        # Use the folder with most images as the canonical display name
        if len(f["images"]) > len(merged[key]["images"]) or \
           (f["folder_name"][0].isupper() and not merged[key]["display_name"][0].isupper()):
            merged[key]["display_name"] = f["folder_name"]
        
        # Add images, avoiding duplicates by filename
        for img in f["images"]:
            if img.name not in merged[key]["seen_filenames"]:
                merged[key]["images"].append(img)
                merged[key]["seen_filenames"].add(img.name)
    
    # Build final list
    dishes = []
    for key, data in sorted(merged.items()):
        display_name = data["display_name"]
        # Prefer "Title Case" name over "slug_case"
        if '_' in display_name and not ' ' in display_name:
            display_name = display_name.replace('_', ' ').title()
        
        slug = make_clean_slug(display_name)
        dishes.append({
            "slug": slug,
            "display_name": display_name,
            "images": sorted(data["images"], key=lambda x: x.name),
            "count": len(data["images"]),
        })
    
    logger.info(f"Scan completo: {len(dishes)} pratos, "
                f"{sum(d['count'] for d in dishes)} imagens totais")
    return dishes

# ============ PROGRESS TRACKING ============
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed_slugs": {}, "started_at": None, "total_uploaded": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

# ============ MIGRATION ============
def migrate_all():
    import pymongo
    
    logger.info("=" * 60)
    logger.info("INICIANDO MIGRAÇÃO PARA OBJECT STORAGE")
    logger.info("=" * 60)
    
    # Init storage
    init_storage()
    
    # Connect to MongoDB
    client = pymongo.MongoClient(os.environ.get('MONGO_URL'))
    db = client[os.environ.get('DB_NAME', 'soulnutri')]
    
    # Scan disk
    dishes = scan_disk()
    
    # Load progress (for resumability)
    progress = load_progress()
    if not progress["started_at"]:
        progress["started_at"] = datetime.now(timezone.utc).isoformat()
    
    total_dishes = len(dishes)
    total_images = sum(d["count"] for d in dishes)
    logger.info(f"Pratos a migrar: {total_dishes}")
    logger.info(f"Imagens a migrar: {total_images}")
    
    # Clear old dish_storage (it's empty anyway, but just in case)
    db.dish_storage.drop()
    logger.info("Coleção dish_storage limpa")
    
    uploaded_total = 0
    errors_total = 0
    
    for idx, dish in enumerate(dishes):
        slug = dish["slug"]
        display_name = dish["display_name"]
        images = dish["images"]
        
        # Check if already migrated
        if slug in progress["completed_slugs"]:
            uploaded_total += progress["completed_slugs"][slug]
            logger.info(f"[{idx+1}/{total_dishes}] {display_name} - JÁ MIGRADO ({progress['completed_slugs'][slug]} imgs)")
            continue
        
        logger.info(f"[{idx+1}/{total_dishes}] Migrando: {display_name} ({len(images)} imgs)")
        
        uploaded_images = []
        dish_errors = 0
        
        for img_idx, img_path in enumerate(images):
            ext = img_path.suffix.lower()
            content_type = MIME_TYPES.get(ext, "image/jpeg")
            storage_path = f"{APP_NAME}/dishes/{slug}/{img_path.name}"
            
            try:
                data = img_path.read_bytes()
                result = upload_image(storage_path, data, content_type)
                actual_path = result.get("path", storage_path)
                
                uploaded_images.append({
                    "filename": img_path.name,
                    "storage_path": actual_path,
                    "size": len(data),
                })
                uploaded_total += 1
                
                if (img_idx + 1) % 10 == 0:
                    logger.info(f"  ... {img_idx+1}/{len(images)} imagens enviadas")
                
                # Small delay to avoid overwhelming the storage service
                time.sleep(0.15)
                    
            except Exception as e:
                logger.error(f"  ERRO ao enviar {img_path.name}: {e}")
                dish_errors += 1
                errors_total += 1
        
        # Save to MongoDB dish_storage
        if uploaded_images:
            db.dish_storage.insert_one({
                "slug": slug,
                "name": display_name,
                "images": uploaded_images,
                "count": len(uploaded_images),
                "migrated_at": datetime.now(timezone.utc).isoformat(),
            })
        
        # Track progress
        progress["completed_slugs"][slug] = len(uploaded_images)
        progress["total_uploaded"] = uploaded_total
        save_progress(progress)
        
        logger.info(f"  ✓ {display_name}: {len(uploaded_images)} OK, {dish_errors} erros")
    
    # ============ REBUILD dishes COLLECTION ============
    logger.info("")
    logger.info("=" * 60)
    logger.info("RECONSTRUINDO COLEÇÃO 'dishes'")
    logger.info("=" * 60)
    
    # Keep old dishes data for reference (feedback links etc)
    old_dishes = list(db.dishes.find({}, {"_id": 0}))
    
    # Drop and rebuild
    db.dishes.drop()
    
    new_dishes = []
    for dish in dishes:
        new_doc = {
            "name": dish["display_name"],
            "slug": dish["slug"],
            "ingredients": [],
            "category": [],
            "has_gluten": None,
            "is_vegan": None,
            "nutrition": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        new_dishes.append(new_doc)
    
    if new_dishes:
        db.dishes.insert_many(new_dishes)
    
    logger.info(f"Coleção 'dishes' recriada com {len(new_dishes)} pratos limpos")
    
    # ============ FINAL REPORT ============
    logger.info("")
    logger.info("=" * 60)
    logger.info("MIGRAÇÃO CONCLUÍDA")
    logger.info("=" * 60)
    logger.info(f"Pratos migrados: {total_dishes}")
    logger.info(f"Imagens enviadas: {uploaded_total}")
    logger.info(f"Erros: {errors_total}")
    logger.info(f"Progresso salvo em: {PROGRESS_FILE}")
    logger.info(f"Log completo em: /app/migration_log.txt")
    
    # Save final report
    report = {
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total_dishes": total_dishes,
        "total_images_uploaded": uploaded_total,
        "total_errors": errors_total,
        "dishes_migrated": [
            {"slug": d["slug"], "name": d["display_name"], "images": d["count"]}
            for d in dishes
        ]
    }
    with open('/app/migration_report.json', 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

if __name__ == "__main__":
    if not EMERGENT_KEY:
        print("ERRO: EMERGENT_LLM_KEY não configurada")
        sys.exit(1)
    
    report = migrate_all()
    print(f"\nMigração concluída! {report['total_images_uploaded']} imagens, {report['total_errors']} erros")
