#!/usr/bin/env python3
"""Migra imagens locais para Object Storage S3 com retry robusto."""
import os, sys, time, requests, pymongo, unicodedata
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
LOCAL_DIR = Path("/app/datasets/organized")
MIME_TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
DELAY_BETWEEN = 1.0  # segundos entre uploads
MAX_RETRIES = 3
RETRY_WAIT = 5  # segundos antes de retry

client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
db = client[os.environ.get("DB_NAME", "soulnutri")]

storage_key = None

def init_storage():
    global storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key

def upload_with_retry(path, data, content_type):
    global storage_key
    for attempt in range(MAX_RETRIES):
        try:
            if not storage_key:
                init_storage()
            resp = requests.put(
                f"{STORAGE_URL}/objects/{path}",
                headers={"X-Storage-Key": storage_key, "Content-Type": content_type},
                data=data, timeout=120
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 500:
                print(f"(500, retry {attempt+1}/{MAX_RETRIES})", end=" ", flush=True)
                storage_key = None  # Force reinit
                time.sleep(RETRY_WAIT * (attempt + 1))
                init_storage()
                continue
            resp.raise_for_status()
        except Exception as e:
            print(f"(err: {e}, retry {attempt+1})", end=" ", flush=True)
            time.sleep(RETRY_WAIT)
            storage_key = None
            try:
                init_storage()
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

def migrate_dish(slug):
    doc = db.dish_storage.find_one({"slug": slug})
    if not doc:
        return 0, 0, "nao encontrado"
    
    images = doc.get("images", [])
    if not images:
        return 0, 0, "sem imagens"
    
    if images[0].get("source") == "cloud" and not images[0].get("storage_path","").startswith("local:"):
        return 0, 0, "ja cloud"
    
    folder = find_local_folder(slug)
    if not folder:
        return 0, 0, "sem pasta local"
    
    uploaded = 0
    errors = 0
    new_images = []
    consecutive_fails = 0
    
    for img_entry in images:
        fname = img_entry.get("filename", "")
        local_file = folder / fname
        
        if not local_file.exists():
            new_images.append(img_entry)
            continue
        
        ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else "jpg"
        content_type = MIME_TYPES.get(ext, "image/jpeg")
        storage_path = f"soulnutri/dishes/{slug}/{fname}"
        data = local_file.read_bytes()
        
        result = upload_with_retry(storage_path, data, content_type)
        
        if result:
            new_images.append({
                "filename": fname,
                "storage_path": result.get("path", storage_path),
                "size": len(data),
                "source": "cloud"
            })
            uploaded += 1
            consecutive_fails = 0
        else:
            errors += 1
            consecutive_fails += 1
            new_images.append(img_entry)
            if consecutive_fails >= 3:
                # S3 provavelmente caiu, salvar progresso e parar
                print(f"3 falhas consecutivas, salvando progresso...", flush=True)
                break
        
        time.sleep(DELAY_BETWEEN)
    
    # SEMPRE salvar progresso (mesmo parcial)
    if uploaded > 0:
        db.dish_storage.update_one(
            {"slug": slug},
            {"$set": {"images": new_images, "count": len(new_images)}}
        )
    
    return uploaded, errors, "3 falhas consecutivas" if consecutive_fails >= 3 else "OK"


# Main
init_storage()
print(f"Storage inicializado")

letter_filter = sys.argv[1].lower() if len(sys.argv) > 1 else None

# Get local dishes
local_dishes = []
for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1}):
    slug = doc["slug"]
    full = db.dish_storage.find_one({"slug": slug})
    imgs = full.get("images", [])
    if imgs and (imgs[0].get("source") == "local" or imgs[0].get("storage_path","").startswith("local:")):
        if letter_filter and slug[0].lower() != letter_filter:
            continue
        local_dishes.append(slug)

print(f"Migrando {len(local_dishes)} pratos (letra: {letter_filter or 'TODAS'})")

total_up = 0
total_err = 0
s3_down = False

for i, slug in enumerate(sorted(local_dishes)):
    print(f"[{i+1}/{len(local_dishes)}] {slug}: ", end="", flush=True)
    up, err, msg = migrate_dish(slug)
    total_up += up
    total_err += err
    print(f"{up} ok, {err} err - {msg}")
    
    if "3 falhas" in msg:
        s3_down = True
        print(f"\nS3 instavel! Progresso salvo. Total: {total_up} fotos migradas.")
        break

print(f"\n=== RESULTADO ===")
print(f"Fotos migradas: {total_up} | Erros: {total_err}")
if s3_down:
    print("S3 caiu durante migracao. Execute novamente para continuar de onde parou.")
