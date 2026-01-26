"""SoulNutri AI - Embedder CLIP
Versão híbrida: tenta usar modelo local, fallback para API externa
"""

import os
import numpy as np
from PIL import Image
import io
import time
import logging

logger = logging.getLogger(__name__)

# Tentar usar API externa primeiro (mais confiável em produção)
USE_LOCAL_MODEL = os.environ.get("USE_LOCAL_MODEL", "false").lower() == "true"

# Cache global
_MODEL = None
_PREPROCESS = None
_DEVICE = "cpu"
_USE_HF_API = True  # Flag para usar HF API

def _try_load_local_model():
    """Tenta carregar modelo local (pode falhar em ambientes sem GPU)"""
    global _MODEL, _PREPROCESS, _DEVICE, _USE_HF_API
    
    try:
        # Forçar CPU
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        os.environ["CUDA_HOME"] = ""
        os.environ["USE_CUDA"] = "0"
        
        import torch
        torch.set_num_threads(4)
        
        if hasattr(torch, 'set_default_device'):
            torch.set_default_device('cpu')
        
        import open_clip
        
        logger.info("[embedder] Carregando modelo OpenCLIP local (CPU)...")
        start = time.time()
        
        _DEVICE = "cpu"
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name="ViT-B-32",
            pretrained="openai",
            device=_DEVICE
        )
        model = model.to(_DEVICE)
        model.eval()
        
        for param in model.parameters():
            param.requires_grad = False
        
        _MODEL = model
        _PREPROCESS = preprocess
        _USE_HF_API = False
        
        logger.info(f"[embedder] Modelo local carregado em {time.time()-start:.2f}s")
        return True
        
    except Exception as e:
        logger.warning(f"[embedder] Modelo local não disponível: {e}")
        logger.info("[embedder] Usando Hugging Face Inference API como fallback")
        _USE_HF_API = True
        return False


def preload_model():
    """Pré-carrega o modelo ou configura API externa"""
    global _USE_HF_API
    
    if USE_LOCAL_MODEL:
        success = _try_load_local_model()
        if success:
            return True
    
    # Usar API externa
    _USE_HF_API = True
    logger.info("[embedder] Configurado para usar Hugging Face Inference API")
    return True


def get_image_embedding(image_bytes: bytes) -> np.ndarray:
    """Gera embedding de uma imagem"""
    global _MODEL, _PREPROCESS, _USE_HF_API
    
    start = time.time()
    
    # Se usando API externa
    if _USE_HF_API or _MODEL is None:
        return _get_embedding_via_api(image_bytes)
    
    # Modelo local
    try:
        import torch
        
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_tensor = _PREPROCESS(img).unsqueeze(0).to(_DEVICE)
        
        with torch.no_grad():
            embedding = _MODEL.encode_image(img_tensor)
            embedding = embedding.cpu().numpy().flatten()
            embedding = embedding / np.linalg.norm(embedding)
        
        logger.info(f"[embedder] Local: {(time.time()-start)*1000:.0f}ms")
        return embedding
        
    except Exception as e:
        logger.error(f"[embedder] Erro no modelo local: {e}")
        # Fallback para API
        return _get_embedding_via_api(image_bytes)


def _get_embedding_via_api(image_bytes: bytes) -> np.ndarray:
    """Gera embedding usando Hugging Face API (GRATUITO)"""
    import httpx
    import base64
    
    start = time.time()
    
    HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/openai/clip-vit-base-patch32"
    HF_TOKEN = os.environ.get("HF_TOKEN", "")
    
    try:
        # Redimensionar imagem para economizar bandwidth
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224), Image.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        headers = {"Content-Type": "application/json"}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                HF_API_URL,
                headers=headers,
                json={"inputs": {"image": img_base64}}
            )
            
            if response.status_code == 200:
                data = response.json()
                # A API retorna uma lista de floats
                if isinstance(data, list):
                    embedding = np.array(data, dtype=np.float32).flatten()
                else:
                    embedding = np.array(data, dtype=np.float32).flatten()
                
                # Normalizar
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                
                logger.info(f"[embedder] HF API: {(time.time()-start)*1000:.0f}ms, dim={len(embedding)}")
                return embedding
            else:
                logger.error(f"[embedder] HF API error: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"[embedder] Erro na API: {e}")
        return None


def get_model_info():
    """Retorna informações do modelo em uso"""
    if _USE_HF_API:
        return {
            "model": "openai/clip-vit-base-patch32",
            "provider": "Hugging Face Inference API",
            "local": False,
            "device": "cloud"
        }
    else:
        return {
            "model": "ViT-B-32",
            "provider": "OpenCLIP (local)",
            "local": True,
            "device": _DEVICE
        }
