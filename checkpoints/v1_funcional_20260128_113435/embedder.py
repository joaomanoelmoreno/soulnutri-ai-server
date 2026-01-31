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
    """Gera embedding de uma imagem a partir de bytes"""
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


# Aliases para compatibilidade com index.py
def image_embedding_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Alias para get_image_embedding"""
    return get_image_embedding(image_bytes)


def image_embedding_from_path(image_path: str) -> np.ndarray:
    """Gera embedding de uma imagem a partir do caminho do arquivo"""
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return get_image_embedding(image_bytes)


def _get_embedding_via_api(image_bytes: bytes) -> np.ndarray:
    """DESABILITADO - Retorna embedding aleatório para não gastar créditos"""
    import json
    
    start = time.time()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ECONOMIA DE CRÉDITOS: Não chamar Gemini, usar fallback direto
    # ═══════════════════════════════════════════════════════════════════════════
    logger.info("[embedder] API externa DESABILITADA para economizar créditos")
    
    # Fallback: embedding aleatório normalizado
    # Isso faz o sistema usar apenas o índice existente
    random_emb = np.random.randn(512).astype(np.float32)
    return random_emb / np.linalg.norm(random_emb)


def _get_best_match_embedding(dish_name: str) -> np.ndarray:
    """Busca o embedding mais similar ao nome do prato no índice local"""
    try:
        import json
        from difflib import SequenceMatcher
        
        index_file = "/app/datasets/dish_index.json"
        emb_file = "/app/datasets/dish_index_embeddings.npy"
        
        if not os.path.exists(index_file) or not os.path.exists(emb_file):
            return None
        
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        
        embeddings = np.load(emb_file)
        dishes = index_data.get('dishes', [])
        dish_to_idx = index_data.get('dish_to_idx', {})
        
        # Normalizar nome para busca
        dish_name_clean = dish_name.lower().replace('_', ' ').strip()
        
        # Buscar prato mais similar por nome usando SequenceMatcher
        best_match = None
        best_score = 0
        
        for slug in dish_to_idx.keys():
            slug_clean = slug.lower().replace('_', ' ')
            
            # Calcular similaridade com SequenceMatcher (mais preciso)
            score = SequenceMatcher(None, dish_name_clean, slug_clean).ratio()
            
            # Boost se uma string contém a outra
            if dish_name_clean in slug_clean or slug_clean in dish_name_clean:
                score = min(1.0, score + 0.3)
            
            if score > best_score:
                best_score = score
                best_match = slug
        
        # Só usar se tiver uma boa correspondência (>50%)
        if best_match and best_score > 0.5 and best_match in dish_to_idx:
            # Pegar primeiro embedding desse prato
            idx = dish_to_idx[best_match][0]
            logger.info(f"[embedder] Match encontrado: '{dish_name_clean}' -> '{best_match}' (score={best_score:.2f})")
            return embeddings[idx]
        
        logger.warning(f"[embedder] Nenhum match bom encontrado para '{dish_name_clean}' (best: {best_match}, score: {best_score:.2f})")
        
        # Retornar None para usar fallback do Gemini
        return None
        
    except Exception as e:
        logger.error(f"[embedder] Erro ao buscar embedding local: {e}")
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
