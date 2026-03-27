"""
Restaura dados (ingredientes, categorias, etc.) do backup para o MongoDB atual.
NAO MEXE EM IMAGENS.
"""
import json, pymongo, os, unicodedata
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

client = pymongo.MongoClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'soulnutri')]

def norm(s):
    nfkd = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return s.lower().replace(' ', '').replace('_', '').replace('-', '')

# Load backup
with open('/app/backup_mongodb_20260327_105734.json') as f:
    backup = json.load(f)

# Index backup by normalized key
backup_index = {}
for d in backup['dishes']:
    for key_field in ['slug', 'name']:
        key = norm(d.get(key_field, ''))
        if key and key not in backup_index:
            backup_index[key] = d

# Process each current dish
restored = 0
for current_doc in db.dishes.find():
    doc_id = current_doc['_id']
    slug = current_doc.get('slug', '')
    name = current_doc.get('name', '')
    
    old = backup_index.get(norm(slug)) or backup_index.get(norm(name))
    if not old:
        continue
    
    update_fields = {}
    
    ingr = old.get('ingredients', [])
    if ingr and len(ingr) > 0:
        update_fields['ingredients'] = ingr
    
    cat = old.get('category', [])
    if isinstance(cat, str) and cat.strip():
        update_fields['category'] = [cat]
    elif isinstance(cat, list) and len(cat) > 0:
        update_fields['category'] = cat
    
    for field in ['has_gluten', 'is_vegan']:
        val = old.get(field)
        if val is not None:
            update_fields[field] = val
    
    nutri = old.get('nutrition')
    if nutri and isinstance(nutri, dict) and any(v for v in nutri.values() if v):
        update_fields['nutrition'] = nutri
    
    desc = old.get('description', old.get('descricao', ''))
    if desc and desc.strip() and 'a ser preenchido' not in desc.lower():
        update_fields['description'] = desc
    
    for field in ['beneficios', 'riscos', 'tecnica']:
        val = old.get(field)
        if val and ((isinstance(val, list) and len(val) > 0) or (isinstance(val, str) and val.strip())):
            update_fields[field] = val
    
    if update_fields:
        result = db.dishes.update_one({"_id": doc_id}, {"$set": update_fields})
        if result.modified_count > 0:
            restored += 1
            print(f"  OK: {name} ({slug}) -> {list(update_fields.keys())}")

print(f"\nTotal restaurados: {restored}")

# Verify
for slug in ['guacamole', 'ratatouille', 'espetinho-de-legumes']:
    doc = db.dishes.find_one({"slug": slug}, {"_id": 0, "slug": 1, "ingredients": 1, "category": 1})
    if doc:
        print(f"  Verify {slug}: ingr={doc.get('ingredients', [])[:3]}, cat={doc.get('category', [])}")
