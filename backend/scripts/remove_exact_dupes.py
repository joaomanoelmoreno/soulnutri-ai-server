#!/usr/bin/env python3
"""Remove exact duplicate images (same size) from R2 and MongoDB."""
import os, re, boto3
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import pymongo

client = pymongo.MongoClient(os.environ.get('MONGO_URL'))
db = client[os.environ.get('DB_NAME', 'soulnutri')]

s3 = boto3.client('s3',
    endpoint_url=os.environ.get('R2_ENDPOINT'),
    aws_access_key_id=os.environ.get('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('R2_SECRET_ACCESS_KEY')
)
BUCKET = 'soulnutri-images'

all_storages = list(db.dish_storage.find({}, {'_id': 0, 'slug': 1, 'images': 1}))

total_removed = 0
total_kept = 0
dishes_cleaned = 0
pattern = re.compile(r'\(\d+\)')

for doc in all_storages:
    slug = doc['slug']
    images = doc.get('images', [])
    
    filenames = []
    for img in images:
        fn = img.get('filename', '') if isinstance(img, dict) else str(img)
        filenames.append(fn)
    
    suffix_files = [fn for fn in filenames if pattern.search(fn)]
    if not suffix_files:
        continue
    
    # Get R2 sizes
    prefix = f'dishes/{slug}/'
    try:
        r2_items = {}
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
            for item in page.get('Contents', []):
                r2_items[item['Key'].split('/')[-1]] = item['Size']
    except Exception as e:
        print(f'  [SKIP] {slug}: {e}')
        continue
    
    to_remove = []
    
    for fn in suffix_files:
        base = pattern.sub('', fn)
        if base in r2_items and fn in r2_items:
            if r2_items[fn] == r2_items[base]:
                to_remove.append(fn)
    
    if not to_remove:
        total_kept += len(suffix_files)
        continue
    
    dishes_cleaned += 1
    
    for fn in to_remove:
        r2_key = f'dishes/{slug}/{fn}'
        try:
            s3.delete_object(Bucket=BUCKET, Key=r2_key)
        except Exception as e:
            print(f'  [R2 ERROR] {slug}/{fn}: {e}')
            continue
        
        # Remove from MongoDB
        db.dish_storage.update_one(
            {'slug': slug},
            {'$pull': {'images': {'filename': fn}}}
        )
        
        base = pattern.sub('', fn)
        total_removed += 1
        print(f'  [REMOVED] {slug}/{fn} (exact dupe of {base})')
    
    # Update count
    updated = db.dish_storage.find_one({'slug': slug}, {'_id': 0, 'images': 1})
    new_count = len(updated.get('images', []))
    db.dish_storage.update_one({'slug': slug}, {'$set': {'count': new_count}})
    total_kept += len(suffix_files) - len(to_remove)

total_images = sum(len(d.get('images', [])) for d in db.dish_storage.find({}, {'_id': 0, 'images': 1}))

print(f'\n===== RESULTADO =====')
print(f'Pratos limpos: {dishes_cleaned}')
print(f'Duplicatas exatas removidas: {total_removed}')
print(f'Burst photos mantidas: {total_kept}')
print(f'Total imagens restantes: {total_images}')

client.close()
