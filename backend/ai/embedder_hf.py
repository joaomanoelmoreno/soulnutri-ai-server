"""SoulNutri AI - Embedder usando Hugging Face Inference API
Versão leve sem PyTorch local - usa API externa GRATUITA
"""

import os
import numpy as np
from PIL import Image
import io
import time
import base64
import httpx
import logging

logger = logging.getLogger(__name__)

# Hugging Face Inference API (GRATUITO)
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/openai/clip-vit-base-patch32"
HF_TOKEN = os.environ.get("HF_TOKEN", "")  # Opcional - funciona sem token para uso básico

# Cache de embeddings
_EMBEDDING_CACHE = {}

async def get_image_embedding_async(image_bytes: bytes) -> np.ndarray:
    """Gera embedding de imagem usando Hugging Face API"""
    start = time.time()
    
    # Verificar cache (usando hash da imagem)
    img_hash = hash(image_bytes)
    if img_hash in _EMBEDDING_CACHE:
        logger.info(f"[embedder] Cache hit! {(time.time()-start)*1000:.0f}ms")
        return _EMBEDDING_CACHE[img_hash]
    
    try:
        # Converter imagem para base64
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        headers = {"Content-Type": "application/json"}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                HF_API_URL,
                headers=headers,
                json={"inputs": {"image": img_base64}}
            )
            
            if response.status_code == 200:
                embedding = np.array(response.json(), dtype=np.float32)
                # Normalizar
                embedding = embedding / np.linalg.norm(embedding)
                
                # Salvar no cache
                _EMBEDDING_CACHE[img_hash] = embedding
                
                logger.info(f"[embedder] Embedding gerado via HF API: {(time.time()-start)*1000:.0f}ms")
                return embedding
            else:
                logger.error(f"[embedder] HF API error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"[embedder] Erro ao gerar embedding: {e}")
        return None


def get_image_embedding(image_bytes: bytes) -> np.ndarray:
    """Versão síncrona (fallback)"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(get_image_embedding_async(image_bytes))


def preload_model():
    """Não precisa pré-carregar - API externa"""
    logger.info("[embedder] Usando Hugging Face Inference API (sem modelo local)")
    return True


def get_model_info():
    """Retorna informações do modelo"""
    return {
        "model": "openai/clip-vit-base-patch32",
        "provider": "Hugging Face Inference API",
        "local": False,
        "device": "cloud"
    }
