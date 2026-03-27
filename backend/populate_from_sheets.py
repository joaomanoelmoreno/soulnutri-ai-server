"""
Copia dados das nutrition_sheets para dentro dos pratos (dishes).
NAO MEXE EM IMAGENS.
"""
import pymongo, os, unicodedata
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

client = pymongo.MongoClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'soulnutri')]

def norm(s):
    nfkd = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return s.lower().replace(' ', '').replace('_', '').replace('-', '')

# Index nutrition_sheets by normalized name/slug
sheets = {}
for doc in db.nutrition_sheets.find({}, {"_id": 0}):
    nome = doc.get('nome', '')
    slug = doc.get('slug', '')
    for alt in doc.get('nomes_alternativos', []):
        key = norm(alt)
        if key:
            sheets[key] = doc
    for key_field in [nome, slug]:
        key = norm(key_field)
        if key:
            sheets[key] = doc

print(f"Fichas nutricionais indexadas: {len(sheets)} chaves")

# Update each dish
updated = 0
not_found = []
for dish_doc in db.dishes.find():
    doc_id = dish_doc['_id']
    slug = dish_doc.get('slug', '')
    name = dish_doc.get('name', '')
    
    sheet = sheets.get(norm(name)) or sheets.get(norm(slug))
    if not sheet:
        not_found.append(f"{name} ({slug})")
        continue
    
    update = {}
    
    # Ingredientes
    ingr = sheet.get('ingredientes', [])
    if ingr:
        update['ingredients'] = ingr
    
    # Nutrição
    nutrition = {}
    for field_map in [
        ('calorias_kcal', 'calorias'),
        ('proteinas_g', 'proteinas'),
        ('carboidratos_g', 'carboidratos'),
        ('gorduras_g', 'gorduras'),
        ('fibras_g', 'fibras'),
        ('sodio_mg', 'sodio'),
    ]:
        src, dst = field_map
        val = sheet.get(src)
        if val is not None:
            nutrition[dst] = val
    if nutrition:
        update['nutrition'] = nutrition
    
    # Fontes
    update['fontes_nutricionais'] = sheet.get('fontes_usadas', [])
    update['fonte_principal'] = sheet.get('fonte_principal', '')
    update['detalhes_fontes'] = sheet.get('detalhes_fontes', {})
    
    if update:
        result = db.dishes.update_one({"_id": doc_id}, {"$set": update})
        if result.modified_count > 0:
            updated += 1

print(f"\nPratos atualizados com dados nutricionais: {updated}")
print(f"Pratos sem ficha correspondente: {len(not_found)}")
if not_found:
    print("\nSem correspondência:")
    for nf in not_found[:20]:
        print(f"  - {nf}")
    if len(not_found) > 20:
        print(f"  ... e mais {len(not_found) - 20}")

# Verify
print("\n=== VERIFICAÇÃO ===")
total = db.dishes.count_documents({})
with_ingr = db.dishes.count_documents({"ingredients": {"$exists": True, "$ne": []}})
with_nutri = db.dishes.count_documents({"nutrition": {"$exists": True, "$ne": None, "$ne": {}}})
print(f"Total pratos: {total}")
print(f"Com ingredientes: {with_ingr}")
print(f"Com nutrição: {with_nutri}")
