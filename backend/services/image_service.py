# -*- coding: utf-8 -*-
"""
SoulNutri - Serviço de Imagens
Camada de abstração para operações com imagens de pratos.
Usa Object Storage (S3) como fonte primária, disco local como fallback.
"""
import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

LOCAL_DATASET_DIR = Path("/app/datasets/organized")


def _get_db():
    """Obtém conexão síncrona com MongoDB."""
    import pymongo
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
    client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
    return client[os.environ.get("DB_NAME", "soulnutri")]


def _get_async_db():
    """Obtém referência ao db async (motor) do server.py."""
    # Importação tardia para evitar circular
    from server import db
    return db


def get_dish_images_from_db(slug: str) -> list:
    """Retorna lista de imagens de um prato a partir do MongoDB dish_storage."""
    try:
        db = _get_db()
        # Try exact match first
        doc = db.dish_storage.find_one(
            {"slug": slug},
            {"_id": 0, "images": 1}
        )
        if doc and doc.get("images"):
            return doc["images"]
        
        # Try normalized match
        norm = slug.lower().replace(' ', '_').replace('-', '_')
        for d in db.dish_storage.find({}, {"_id": 0, "slug": 1, "images": 1}):
            s = d.get("slug", "")
            if s.lower().replace(' ', '_').replace('-', '_') == norm:
                return d.get("images", [])
    except Exception as e:
        logger.warning(f"[IMG] MongoDB indisponivel para {slug}: {e}")
    
    return []


def _find_local_folder(slug: str) -> Optional[Path]:
    """Encontra a pasta local correspondente ao slug, testando variações."""
    import unicodedata
    # Try direct match
    direct = LOCAL_DATASET_DIR / slug
    if direct.exists():
        return direct
    # Try all folders and match by normalized comparison
    slug_norm = slug.lower().replace('-', '').replace('_', '').replace(' ', '')
    nfkd = unicodedata.normalize('NFKD', slug_norm)
    slug_norm = ''.join(c for c in nfkd if not unicodedata.combining(c))
    for folder in LOCAL_DATASET_DIR.iterdir():
        if folder.is_dir():
            folder_norm = folder.name.lower().replace('-', '').replace('_', '').replace(' ', '')
            nfkd = unicodedata.normalize('NFKD', folder_norm)
            folder_norm = ''.join(c for c in nfkd if not unicodedata.combining(c))
            if folder_norm == slug_norm:
                return folder
    return None


def get_dish_image_bytes(slug: str, filename: str = None) -> tuple:
    """
    Retorna (bytes, content_type) de uma imagem.
    Verifica source (cloud vs local) no dish_storage.
    Cloud: busca do Object Storage.
    Local: busca do disco.
    """
    from services.storage_service import get_dish_image as s3_get_image

    images = get_dish_images_from_db(slug)
    source = "cloud"  # default
    # Detect source from first image entry
    if images and images[0].get("source") == "local":
        source = "local"
    elif images and images[0].get("storage_path", "").startswith("local:"):
        source = "local"

    target_img = None
    if filename:
        for img in images:
            if img.get("filename") == filename:
                target_img = img
                break
    elif images:
        # Prefer larger images over tiny thumbnails
        for img in images:
            if img.get("size", 0) > 5000:
                target_img = img
                break
        if not target_img:
            target_img = images[0]

    if target_img:
        storage_path = target_img.get("storage_path", "")
        fname = target_img.get("filename", "")

        if source == "cloud" and not storage_path.startswith("local:"):
            try:
                data, ct = s3_get_image(storage_path)
                return data, ct
            except Exception as e:
                logger.warning(f"[IMG] Cloud falhou para {fname}: {e}, tentando local")

        # Local fallback
        local_folder = _find_local_folder(slug)
        if local_folder:
            local_path = local_folder / fname
            if local_path.exists():
                ext = local_path.suffix.lower()
                ct = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext.lstrip('.'), "image/jpeg")
                return local_path.read_bytes(), ct

    # Final fallback: find image in local folder
    local_folder = _find_local_folder(slug)
    if local_folder:
        if filename:
            # Se um filename específico foi pedido, buscar APENAS ele
            local_path = local_folder / filename
            if local_path.exists():
                return local_path.read_bytes(), "image/jpeg"
            # Não encontrou o arquivo específico
            return None, None
        # Sem filename específico: retornar qualquer imagem
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            found = sorted(local_folder.glob(ext))
            if found:
                return found[0].read_bytes(), "image/jpeg"

    return None, None


def save_dish_image(slug: str, filename: str, content: bytes) -> dict:
    """
    Salva imagem no S3 e atualiza MongoDB dish_storage.
    Também salva localmente como cache.
    """
    from services.storage_service import upload_dish_image

    result = {"ok": False}

    # 1. Upload para S3
    try:
        storage_path = upload_dish_image(slug, filename, content)
        result["storage_path"] = storage_path
        result["ok"] = True
        logger.info(f"[IMG] Upload S3 OK: {storage_path}")
    except Exception as e:
        logger.error(f"[IMG] Erro S3 upload {slug}/{filename}: {e}")
        result["error"] = str(e)

    # 2. Atualizar MongoDB dish_storage
    try:
        db = _get_db()
        image_entry = {
            "filename": filename,
            "storage_path": result.get("storage_path", f"soulnutri/dishes/{slug}/{filename}"),
            "size": len(content)
        }
        db.dish_storage.update_one(
            {"slug": slug},
            {
                "$push": {"images": image_entry},
                "$inc": {"count": 1},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"[IMG] Erro MongoDB update {slug}: {e}")

    # 3. Salvar localmente como cache (para CLIP index)
    try:
        local_dir = LOCAL_DATASET_DIR / slug
        local_dir.mkdir(parents=True, exist_ok=True)
        (local_dir / filename).write_bytes(content)
    except Exception as e:
        logger.warning(f"[IMG] Erro ao salvar local {slug}/{filename}: {e}")

    return result


def delete_dish_image_from_storage(slug: str, filename: str) -> dict:
    """Remove imagem do MongoDB dish_storage e do disco local."""
    try:
        db = _get_db()
        db.dish_storage.update_one(
            {"slug": slug},
            {
                "$pull": {"images": {"filename": filename}},
                "$inc": {"count": -1}
            }
        )
        # Remover localmente usando _find_local_folder (resolve slug vs nome real da pasta)
        local_folder = _find_local_folder(slug)
        if local_folder:
            local_path = local_folder / filename
            if local_path.exists():
                local_path.unlink()
        return {"ok": True}
    except Exception as e:
        logger.error(f"[IMG] Erro ao deletar {slug}/{filename}: {e}")
        return {"ok": False, "error": str(e)}


def get_all_dishes_stats() -> dict:
    """Retorna estatísticas de todos os pratos usando MongoDB dish_storage."""
    db = _get_db()
    stats = {}
    total_images = 0

    for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1, "name": 1, "count": 1}):
        slug = doc.get("slug", "")
        count = doc.get("count", 0)
        stats[slug] = count
        total_images += count

    return {
        "ok": True,
        "total_dishes": len(stats),
        "total_images": total_images,
        "dishes": stats
    }


def get_dish_image_count(slug: str) -> int:
    """Retorna o número de imagens de um prato."""
    db = _get_db()
    doc = db.dish_storage.find_one({"slug": slug}, {"_id": 0, "count": 1})
    if doc:
        return doc.get("count", 0)
    return 0


def get_dish_all_image_names(slug: str) -> list:
    """Retorna lista de nomes de todas as imagens de um prato."""
    images = get_dish_images_from_db(slug)
    return [img.get("filename", "") for img in images]


def find_dish_slug_match(dish_name: str) -> Optional[str]:
    """Busca slug do prato mais similar no dish_storage."""
    from difflib import SequenceMatcher
    db = _get_db()
    dish_lower = dish_name.lower().replace('_', ' ')
    best_match = None
    best_score = 0

    for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1}):
        slug = doc.get("slug", "")
        slug_lower = slug.lower().replace('_', ' ')

        if slug == dish_name or slug_lower == dish_lower:
            return slug

        score = SequenceMatcher(None, dish_lower, slug_lower).ratio()
        if dish_lower in slug_lower or slug_lower in dish_lower:
            score = min(1.0, score + 0.3)
        if score > best_score:
            best_score = score
            best_match = slug

    if best_score > 0.7:
        return best_match
    return None
