#!/usr/bin/env python3
"""Migra TODAS as imagens locais para Cloudflare R2."""
import boto3, pymongo, os, json, unicodedata, time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

BUCKET = os.environ['R2_BUCKET']
LOCAL_DIR = Path("/app/datasets/organized")
PROGRESS_FILE = Path("/app/r2_migration_progress.json")
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

s3 = boto3.client('s3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto'
)

client = pymongo.MongoClient(os.environ['MONGO_URL'])
db = client[os.environ.get('DB_NAME', 'soulnutri')]

def normalize(name):
    n = name.lower().replace('-','').replace('_','').replace(' ','').replace('(','').replace(')','')
    nfkd = unicodedata.normalize('NFKD', n)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

def find_local_folder(slug):
    slug_norm = normalize(slug)
    best, best_count = None, 0
    for folder in LOCAL_DIR.iterdir():
        if folder.is_dir() and normalize(folder.name) == slug_norm:
            count = sum(1 for f in folder.iterdir() if f.suffix.lower() in ('.jpg','.jpeg','.png','.webp'))
            if count > best_count:
                best, best_count = folder, count
    return best

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"uploaded": {}, "total": 0, "errors": 0}

def save_progress(p):
    PROGRESS_FILE.write_text(json.dumps(p))

# Main
progress = load_progress()
print(f"=== MIGRAÇÃO CLOUDFLARE R2 ===")
print(f"Progresso anterior: {progress['total']} fotos já migradas")

all_dishes = list(db.dish_storage.find({}, {"_id": 0, "slug": 1}))
print(f"Total pratos: {len(all_dishes)}")

total_new = 0
total_errors = 0

for idx, doc in enumerate(sorted(all_dishes, key=lambda x: x['slug'])):
    slug = doc['slug']
    folder = find_local_folder(slug)
    
    if not folder:
        continue
    
    files = sorted([f for f in folder.iterdir() if f.suffix.lower() in ('.jpg','.jpeg','.png','.webp')])
    if not files:
        continue
    
    dish_uploaded = 0
    dish_skipped = 0
    new_images = []
    
    for f in files:
        r2_key = f"dishes/{slug}/{f.name}"
        
        # Skip if already uploaded
        if r2_key in progress['uploaded']:
            new_images.append({
                "filename": f.name,
                "storage_path": f"r2:{r2_key}",
                "size": f.stat().st_size,
                "source": "r2"
            })
            dish_skipped += 1
            continue
        
        ct = MIME.get(f.suffix.lower(), "image/jpeg")
        try:
            s3.put_object(Bucket=BUCKET, Key=r2_key, Body=f.read_bytes(), ContentType=ct)
            progress['uploaded'][r2_key] = True
            progress['total'] += 1
            new_images.append({
                "filename": f.name,
                "storage_path": f"r2:{r2_key}",
                "size": f.stat().st_size,
                "source": "r2"
            })
            dish_uploaded += 1
            total_new += 1
        except Exception as e:
            total_errors += 1
            progress['errors'] += 1
            new_images.append({
                "filename": f.name,
                "storage_path": f"local:{f}",
                "size": f.stat().st_size,
                "source": "local"
            })
            print(f"  ERRO {slug}/{f.name}: {e}")
    
    # Update MongoDB
    if new_images:
        db.dish_storage.update_one(
            {"slug": slug},
            {"$set": {"images": new_images, "count": len(new_images)}}
        )
    
    # Save progress every dish
    save_progress(progress)
    
    status = f"{dish_uploaded} new" if dish_uploaded else "skip"
    if dish_uploaded > 0 or (idx % 20 == 0):
        print(f"[{idx+1}/{len(all_dishes)}] {slug}: {len(files)} fotos ({status}, {dish_skipped} cached)")

print(f"\n=== RESULTADO ===")
print(f"Novas migradas: {total_new}")
print(f"Total acumulado: {progress['total']}")
print(f"Erros: {total_errors}")
print(f"Timestamp: {datetime.now().isoformat()}")
