"""SoulNutri AI - Embedder CLIP
Geração de embeddings visuais usando OpenCLIP (CPU)
Meta: resposta em 100ms
"""

import torch
import open_clip
import numpy as np
from PIL import Image
import io
import time

# Cache global do modelo (carrega uma vez)
_MODEL = None
_PREPROCESS = None
_DEVICE = None

def _load_model():
    """Carrega o modelo CLIP (lazy loading)"""
    global _MODEL, _PREPROCESS, _DEVICE
    
    if _MODEL is None:
        print("[embedder] Carregando modelo OpenCLIP...")
        start = time.time()
        
        _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        # ViT-B-32 é um bom equilíbrio entre velocidade e qualidade
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name="ViT-B-32",
            pretrained="openai"
        )
        model = model.to(_DEVICE)
        model.eval()
        
        _MODEL = model
        _PREPROCESS = preprocess
        
        elapsed = time.time() - start
        print(f"[embedder] Modelo carregado em {elapsed:.2f}s (device={_DEVICE})")
    
    return _MODEL, _PREPROCESS, _DEVICE


def image_embedding_from_path(image_path: str) -> np.ndarray:
    """Gera embedding normalizado (L2) para uma imagem a partir do caminho"""
    model, preprocess, device = _load_model()
    
    image = Image.open(image_path).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        features = model.encode_image(image_tensor)
        features = features / features.norm(dim=-1, keepdim=True)
    
    return features.cpu().numpy()[0].astype(np.float32)


def image_embedding_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Gera embedding normalizado (L2) para uma imagem a partir de bytes"""
    model, preprocess, device = _load_model()
    
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        features = model.encode_image(image_tensor)
        features = features / features.norm(dim=-1, keepdim=True)
    
    return features.cpu().numpy()[0].astype(np.float32)


def preload_model():
    """Pré-carrega o modelo no startup"""
    _load_model()
    print("[embedder] Modelo pré-carregado e pronto!")
