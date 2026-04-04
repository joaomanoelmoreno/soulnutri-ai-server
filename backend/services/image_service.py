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
    """Encontra a pasta local correspondente ao slug, testando variações.
    Retorna a pasta com MAIS imagens quando há múltiplas correspondências."""
    import unicodedata
    
    def _normalize(name):
        n = name.lower().replace('-', '').replace('_', '').replace(' ', '').replace('(', '').replace(')', '')
        nfkd = unicodedata.normalize('NFKD', n)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))
    
    def _count_images(folder):
        count = 0
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            count += len(list(folder.glob(ext)))
        return count
    
    slug_norm = _normalize(slug)
    best_folder = None
    best_count = 0
    
    # Check ALL matching folders and pick the one with most images
    for folder in LOCAL_DATASET_DIR.iterdir():
        if folder.is_dir() and _normalize(folder.name) == slug_norm:
            count = _count_images(folder)
            if count > best_count:
                best_count = count
                best_folder = folder
    
    if best_folder:
        return best_folder
    
    # Direct match as last resort (for write operations)
    direct = LOCAL_DATASET_DIR / slug
    if direct.exists():
        return direct
    return None


def get_dish_image_bytes(slug: str, filename: str = None) -> tuple:
    """
    Retorna (bytes, content_type) de uma imagem.
    LOCAL primeiro (rapido), R2 como fallback.
    """
    # 1. Tentar local PRIMEIRO (instantaneo)
    local_folder = _find_local_folder(slug)
    if local_folder:
        if filename:
            local_path = local_folder / filename
            if local_path.exists():
                ext = local_path.suffix.lower()
                ct = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
                return local_path.read_bytes(), ct
        else:
            for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
                found = sorted(local_folder.glob(pattern), key=lambda f: f.stat().st_size, reverse=True)
                if found:
                    ext = found[0].suffix.lower()
                    ct = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
                    return found[0].read_bytes(), ct

    # 2. Tentar R2 (Cloudflare)
    images = get_dish_images_from_db(slug)
    target_img = None
    if filename:
        for img in images:
            if img.get("filename") == filename:
                target_img = img
                break
    elif images:
        for img in images:
            if img.get("size", 0) > 5000:
                target_img = img
                break
        if not target_img:
            target_img = images[0]

    if target_img:
        storage_path = target_img.get("storage_path", "")
        if storage_path.startswith("r2:"):
            try:
                from services.r2_service import r2_get_image
                data, ct = r2_get_image(storage_path)
                if data:
                    return data, ct
            except Exception as e:
                logger.warning(f"[IMG] R2 falhou para {slug}/{filename}: {e}")
        elif storage_path and not storage_path.startswith("local:"):
            try:
                from services.storage_service import get_dish_image as s3_get_image
                data, ct = s3_get_image(storage_path)
                return data, ct
            except Exception as e:
                logger.warning(f"[IMG] Cloud falhou para {slug}/{filename}: {e}")

    return None, None


def save_dish_image(slug: str, filename: str, content: bytes) -> dict:
    """
    Salva imagem localmente + R2 e atualiza MongoDB dish_storage.
    Resolve slug canonico para evitar pastas duplicadas.
    """
    result = {"ok": False}
    MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    
    ext = Path(filename).suffix.lower()
    ct = MIME.get(ext, "image/jpeg")
    
    # Resolver slug canonico: buscar pasta existente ou dish_storage existente
    canonical_slug = _resolve_canonical_slug(slug)
    
    r2_key = f"dishes/{canonical_slug}/{filename}"

    # 1. Salvar localmente (instantaneo)
    try:
        local_folder = _find_local_folder(canonical_slug)
        local_dir = local_folder if local_folder else LOCAL_DATASET_DIR / canonical_slug
        local_dir.mkdir(parents=True, exist_ok=True)
        (local_dir / filename).write_bytes(content)
        result["ok"] = True
    except Exception as e:
        logger.error(f"[IMG] Erro local {canonical_slug}/{filename}: {e}")

    # 2. Upload para R2 (background-safe)
    try:
        from services.r2_service import r2_upload_image
        r2_upload_image(r2_key, content, ct)
    except Exception as e:
        logger.warning(f"[IMG] R2 upload falhou {canonical_slug}/{filename}: {e}")

    # 3. Atualizar MongoDB
    try:
        db = _get_db()
        image_entry = {
            "filename": filename,
            "storage_path": f"r2:{r2_key}",
            "size": len(content),
            "source": "r2"
        }
        db.dish_storage.update_one(
            {"slug": canonical_slug},
            {
                "$push": {"images": image_entry},
                "$inc": {"count": 1},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"[IMG] MongoDB update {canonical_slug}: {e}")

    return result


def _resolve_canonical_slug(slug: str) -> str:
    """
    Resolve o slug canonico de um prato.
    Prioridade: pasta local existente > dish_storage > dishes collection > slug original.
    Evita criar pastas duplicadas (ex: 'Bacalhau com Natas' vs 'bacalhau_com_natas').
    """
    import unicodedata
    
    def _normalize(name):
        n = name.lower().replace('-', '').replace('_', '').replace(' ', '').replace('(', '').replace(')', '')
        nfkd = unicodedata.normalize('NFKD', n)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))
    
    slug_norm = _normalize(slug)
    
    # 1. Verificar pasta local existente (fonte mais confiavel)
    for folder in LOCAL_DATASET_DIR.iterdir():
        if folder.is_dir() and _normalize(folder.name) == slug_norm:
            return folder.name  # Retorna o nome EXATO da pasta (com espacos)
    
    # 2. Verificar dish_storage no MongoDB
    try:
        db = _get_db()
        for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1}):
            s = doc.get("slug", "")
            if _normalize(s) == slug_norm:
                return s
    except Exception:
        pass
    
    # 3. Verificar dishes collection
    try:
        db = _get_db()
        for doc in db.dishes.find({}, {"_id": 0, "slug": 1}):
            s = doc.get("slug", "")
            if _normalize(s) == slug_norm:
                return s
    except Exception:
        pass
    
    # 4. Fallback: slug original
    return slug


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
    """Retorna o número de imagens de um prato (contagem real da lista)."""
    db = _get_db()
    doc = db.dish_storage.find_one({"slug": slug}, {"_id": 0, "images": 1})
    if doc:
        return len(doc.get("images", []))
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
