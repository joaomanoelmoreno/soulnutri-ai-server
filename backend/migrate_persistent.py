#!/usr/bin/env python3
"""Migração persistente para S3 - roda em background com retry agressivo."""
import os, sys, time, requests, pymongo, unicodedata, json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
LOCAL_DIR = Path("/app/datasets/organized")
PROGRESS_FILE = Path("/app/migration_progress_v2.json")
LOG_FILE = Path("/app/migration_live.log")
MIME = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}

client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
db = client[os.environ.get("DB_NAME", "soulnutri")]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_storage_key():
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    return resp.json()["storage_key"]

def try_upload(sk, path, data, ct):
    try:
        r = requests.put(f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": sk, "Content-Type": ct},
            data=data, timeout=120)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def normalize(name):
    n = name.lower().replace('-','').replace('_','').replace(' ','').replace('(','').replace(')','')
    nfkd = unicodedata.normalize('NFKD', n)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

def find_local_folder(slug):
    direct = LOCAL_DIR / slug
    if direct.exists() and any(direct.glob('*.jp*')):
        return direct
    slug_norm = normalize(slug)
    for folder in LOCAL_DIR.iterdir():
        if folder.is_dir() and normalize(folder.name) == slug_norm:
            if any(folder.glob('*.jp*')) or any(folder.glob('*.png')):
                return folder
    return None

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"migrated_images": {}, "total_uploaded": 0}

def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))

# Main
log("=== MIGRACAO PERSISTENTE INICIADA ===")
sk = get_storage_key()
log("Storage key obtida")

progress = load_progress()

# Get all local dishes
local_dishes = []
for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1}):
    slug = doc["slug"]
    full = db.dish_storage.find_one({"slug": slug})
    imgs = full.get("images", [])
    if imgs and (imgs[0].get("source") == "local" or imgs[0].get("storage_path","").startswith("local:")):
        local_dishes.append(slug)

log(f"Pratos locais a migrar: {len(local_dishes)}")

total_session = 0
consecutive_global_fails = 0

for dish_idx, slug in enumerate(sorted(local_dishes)):
    doc = db.dish_storage.find_one({"slug": slug})
    images = doc.get("images", [])
    folder = find_local_folder(slug)
    
    if not folder:
        log(f"[{dish_idx+1}/{len(local_dishes)}] {slug}: SKIP (sem pasta)")
        continue
    
    dish_uploaded = 0
    new_images = []
    
    for img in images:
        fname = img.get("filename", "")
        img_key = f"{slug}/{fname}"
        
        # Skip se ja migrou nesta sessao
        if img_key in progress["migrated_images"]:
            new_images.append({
                "filename": fname,
                "storage_path": progress["migrated_images"][img_key],
                "size": img.get("size", 0),
                "source": "cloud"
            })
            dish_uploaded += 1
            continue
        
        # Skip se ja é cloud
        if img.get("source") == "cloud" and not img.get("storage_path","").startswith("local:"):
            new_images.append(img)
            continue
        
        local_file = folder / fname
        if not local_file.exists():
            new_images.append(img)
            continue
        
        data = local_file.read_bytes()
        ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else "jpg"
        ct = MIME.get(ext, "image/jpeg")
        spath = f"soulnutri/dishes/{slug}/{fname}"
        
        # Tentar até 10x com backoff
        uploaded = False
        for attempt in range(10):
            result = try_upload(sk, spath, data, ct)
            if result:
                new_images.append({
                    "filename": fname,
                    "storage_path": result.get("path", spath),
                    "size": len(data),
                    "source": "cloud"
                })
                progress["migrated_images"][img_key] = result.get("path", spath)
                progress["total_uploaded"] += 1
                save_progress(progress)
                dish_uploaded += 1
                uploaded = True
                consecutive_global_fails = 0
                break
            else:
                wait = min(3 + attempt * 2, 15)  # 3s, 5s, 7s... max 15s
                time.sleep(wait)
                # Reinit key periodically
                if attempt % 3 == 2:
                    try:
                        sk = get_storage_key()
                    except:
                        time.sleep(10)
                        try:
                            sk = get_storage_key()
                        except:
                            pass
        
        if not uploaded:
            new_images.append(img)
            consecutive_global_fails += 1
            if consecutive_global_fails >= 5:
                log(f"  {slug}: S3 totalmente indisponivel apos 5 falhas globais")
                break
        
        time.sleep(2)  # Pausa entre cada foto
    
    # Salvar progresso no MongoDB
    if dish_uploaded > 0:
        db.dish_storage.update_one(
            {"slug": slug},
            {"$set": {"images": new_images, "count": len(new_images)}}
        )
        total_session += dish_uploaded
    
    remaining_local = sum(1 for im in new_images if im.get("source") != "cloud")
    log(f"[{dish_idx+1}/{len(local_dishes)}] {slug}: {dish_uploaded} migradas, {remaining_local} restantes")
    
    if consecutive_global_fails >= 5:
        log(f"\nS3 INDISPONIVEL - Parando. Migradas nesta sessao: {total_session}")
        log(f"Total acumulado: {progress['total_uploaded']}")
        log("Execute novamente para continuar de onde parou.")
        break

log(f"\n=== RESULTADO ===")
log(f"Migradas nesta sessao: {total_session}")
log(f"Total acumulado: {progress['total_uploaded']}")

# Contagem final
cloud_count = 0
local_count = 0
for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1}):
    full = db.dish_storage.find_one({"slug": doc["slug"]})
    imgs = full.get("images", [])
    if imgs and imgs[0].get("source") == "cloud":
        cloud_count += 1
    else:
        local_count += 1
log(f"Cloud: {cloud_count} | Local: {local_count} | Total: {cloud_count + local_count}")
