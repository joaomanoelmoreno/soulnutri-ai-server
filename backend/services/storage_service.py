# -*- coding: utf-8 -*-
"""
SoulNutri - Serviço de Object Storage (Emergent S3-compatível)
Gerencia upload, download e listagem de imagens do dataset.
"""
import os
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "soulnutri"

storage_key = None

MIME_TYPES = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "gif": "image/gif", "webp": "image/webp",
}


def init_storage():
    """Inicializa storage uma vez. Retorna storage_key reutilizável."""
    global storage_key
    if storage_key:
        return storage_key
    if not EMERGENT_KEY:
        raise ValueError("EMERGENT_LLM_KEY não configurada")
    resp = requests.post(
        f"{STORAGE_URL}/init",
        json={"emergent_key": EMERGENT_KEY},
        timeout=30
    )
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    logger.info("[STORAGE] Inicializado com sucesso")
    return storage_key


def put_object(path: str, data: bytes, content_type: str = "image/jpeg") -> dict:
    """Upload de arquivo. Retorna {"path": "...", "size": 123, "etag": "..."}"""
    key = init_storage()
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data,
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()


def get_object(path: str) -> tuple:
    """Download de arquivo. Retorna (bytes, content_type)."""
    key = init_storage()
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key},
        timeout=60
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "image/jpeg")


def upload_dish_image(dish_slug: str, filename: str, data: bytes) -> str:
    """Upload de imagem de prato. Retorna o path no storage."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    content_type = MIME_TYPES.get(ext, "image/jpeg")
    storage_path = f"{APP_NAME}/dishes/{dish_slug}/{filename}"
    result = put_object(storage_path, data, content_type)
    return result.get("path", storage_path)


def get_dish_image(storage_path: str) -> tuple:
    """Download de imagem do storage. Retorna (bytes, content_type)."""
    return get_object(storage_path)


def migrate_dish_images(dish_slug: str, local_folder: Path, max_images: int = 50) -> list:
    """Migra imagens de uma pasta local para o storage. Retorna lista de paths."""
    uploaded = []
    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    
    files = sorted([
        f for f in local_folder.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ])[:max_images]
    
    for img_file in files:
        try:
            data = img_file.read_bytes()
            path = upload_dish_image(dish_slug, img_file.name, data)
            uploaded.append({"filename": img_file.name, "storage_path": path, "size": len(data)})
        except Exception as e:
            logger.error(f"[STORAGE] Erro ao migrar {img_file.name}: {e}")
    
    return uploaded
