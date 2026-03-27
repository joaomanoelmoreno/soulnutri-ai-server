"""
Reconstrói o MongoDB a partir do progresso da migração + disco local.
Cria dados limpos para TODOS os pratos:
- Pratos migrados: referencia cloud storage
- Pratos não migrados: referencia disco local
"""
import pymongo, os, json
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
import unicodedata

load_dotenv(Path(__file__).parent / '.env')

client = pymongo.MongoClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'soulnutri')]

DATASETS_DIR = Path("/app/datasets/organized")
PROGRESS_FILE = "/app/migration_progress.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
APP_NAME = "soulnutri"

def make_clean_slug(folder_name):
    s = folder_name.strip().replace('_', ' ')
    nfkd = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in nfkd if not unicodedata.combining(c))
    s = s.lower().strip()
    s = ''.join(c if c.isalnum() or c in (' ', '-') else '' for c in s)
    s = '-'.join(s.split())
    while '--' in s:
        s = s.replace('--', '-')
    return s.strip('-')

def normalize_for_comparison(s):
    nfkd = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return s.lower().replace(' ', '').replace('_', '').replace('-', '')

def scan_disk():
    junk_prefixes = ['test_action_', 'prato_corrigido_', 'prato_com_']
    raw = []
    for folder in sorted(DATASETS_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        is_junk = any(folder.name.lower().startswith(p) for p in junk_prefixes)
        if is_junk or len(folder.name) > 80:
            continue
        imgs = sorted([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS])
        if imgs:
            raw.append({"folder": folder.name, "images": imgs, "count": len(imgs),
                        "norm": normalize_for_comparison(folder.name)})

    merged = {}
    for f in raw:
        key = f["norm"]
        if key not in merged:
            merged[key] = {"display_name": f["folder"], "images": [], "seen": set()}
        if len(f["images"]) > len(merged[key]["images"]) or \
           (f["folder"][0].isupper() and not merged[key]["display_name"][0].isupper()):
            merged[key]["display_name"] = f["folder"]
        for img in f["images"]:
            if img.name not in merged[key]["seen"]:
                merged[key]["images"].append(img)
                merged[key]["seen"].add(img.name)

    dishes = []
    for key, data in sorted(merged.items()):
        name = data["display_name"]
        if '_' in name and ' ' not in name:
            name = name.replace('_', ' ').title()
        slug = make_clean_slug(name)
        dishes.append({"slug": slug, "name": name,
                       "images": sorted(data["images"], key=lambda x: x.name),
                       "count": len(data["images"])})
    return dishes

# Load migration progress
progress = {}
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE) as f:
        progress = json.load(f)
migrated_slugs = set(progress.get("completed_slugs", {}).keys())
print(f"Slugs migrados para cloud: {len(migrated_slugs)}")

# Scan disk
all_dishes = scan_disk()
print(f"Total pratos no disco: {len(all_dishes)}")

# Drop and rebuild both collections
db.dish_storage.drop()
db.dishes.drop()
print("Collections limpas")

now = datetime.now(timezone.utc).isoformat()

dish_storage_docs = []
dishes_docs = []

for dish in all_dishes:
    slug = dish["slug"]
    name = dish["name"]
    images = dish["images"]

    if slug in migrated_slugs:
        # Cloud: reference storage paths
        img_entries = []
        for img in images:
            img_entries.append({
                "filename": img.name,
                "storage_path": f"{APP_NAME}/dishes/{slug}/{img.name}",
                "size": img.stat().st_size,
                "source": "cloud"
            })
        dish_storage_docs.append({
            "slug": slug,
            "name": name,
            "images": img_entries,
            "count": len(img_entries),
            "source": "cloud",
            "migrated_at": now,
        })
    else:
        # Disk only: reference local paths
        img_entries = []
        for img in images:
            img_entries.append({
                "filename": img.name,
                "storage_path": f"local:{img}",
                "size": img.stat().st_size,
                "source": "local"
            })
        dish_storage_docs.append({
            "slug": slug,
            "name": name,
            "images": img_entries,
            "count": len(img_entries),
            "source": "local",
            "migrated_at": None,
        })

    dishes_docs.append({
        "name": name,
        "slug": slug,
        "ingredients": [],
        "category": [],
        "has_gluten": None,
        "is_vegan": None,
        "nutrition": None,
        "created_at": now,
    })

# Insert all
if dish_storage_docs:
    db.dish_storage.insert_many(dish_storage_docs)
if dishes_docs:
    db.dishes.insert_many(dishes_docs)

cloud_count = sum(1 for d in dish_storage_docs if d["source"] == "cloud")
local_count = sum(1 for d in dish_storage_docs if d["source"] == "local")
total_imgs = sum(d["count"] for d in dish_storage_docs)

print(f"\nReconstrução completa:")
print(f"  dish_storage: {len(dish_storage_docs)} docs")
print(f"    - Cloud: {cloud_count} pratos")
print(f"    - Local: {local_count} pratos")
print(f"    - Total imagens referenciadas: {total_imgs}")
print(f"  dishes: {len(dishes_docs)} docs")
