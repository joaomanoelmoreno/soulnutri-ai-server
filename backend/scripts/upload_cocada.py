#!/usr/bin/env python3
"""Upload cocada photos from ZIP to R2 and update MongoDB."""
import sys
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, '/app/backend')
os.chdir('/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from services.r2_service import r2_upload_image
import pymongo

SLUG = "cocada"
SOURCE_DIR = Path("/tmp/cocada_extract")
BUCKET_PREFIX = f"dishes/{SLUG}"

def main():
    # Connect to MongoDB
    client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
    db = client[os.environ.get("DB_NAME", "soulnutri")]
    
    # Get existing images for cocada
    doc = db.dish_storage.find_one({"slug": SLUG}, {"_id": 0})
    existing_images = doc.get("images", []) if doc else []
    existing_filenames = {img.get("filename") for img in existing_images}
    print(f"[cocada] Imagens existentes: {len(existing_filenames)}")
    
    # Process each photo
    photos = sorted(SOURCE_DIR.glob("*.jpg"))
    uploaded = 0
    
    for photo in photos:
        # Generate unique filename
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        h = hashlib.md5(photo.read_bytes()[:1024]).hexdigest()[:8]
        new_filename = f"cocada_{ts}_{h}.jpg"
        
        if new_filename in existing_filenames:
            print(f"  [SKIP] {photo.name} -> {new_filename} (already exists)")
            continue
        
        content = photo.read_bytes()
        r2_key = f"{BUCKET_PREFIX}/{new_filename}"
        
        # Upload to R2
        ok = r2_upload_image(r2_key, content, "image/jpeg")
        if not ok:
            print(f"  [FAIL] {photo.name} -> R2 upload failed")
            continue
        
        # Save locally too
        local_dir = Path(f"/app/datasets/organized/{SLUG}")
        local_dir.mkdir(parents=True, exist_ok=True)
        (local_dir / new_filename).write_bytes(content)
        
        # Update MongoDB
        image_entry = {
            "filename": new_filename,
            "storage_path": f"r2:{r2_key}",
            "size": len(content),
            "source": "r2"
        }
        db.dish_storage.update_one(
            {"slug": SLUG},
            {
                "$push": {"images": image_entry},
                "$inc": {"count": 1},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
        uploaded += 1
        print(f"  [OK] {photo.name} -> {new_filename} ({len(content)} bytes)")
        
        # Small delay between uploads to avoid hash collision
        import time
        time.sleep(0.5)
    
    # Verify final count
    doc = db.dish_storage.find_one({"slug": SLUG}, {"_id": 0, "images": 1, "count": 1})
    final_count = len(doc.get("images", [])) if doc else 0
    print(f"\n[RESULTADO] Uploaded: {uploaded}, Total cocada images: {final_count}")
    
    client.close()

if __name__ == "__main__":
    main()
