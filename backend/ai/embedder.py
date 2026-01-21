"""SoulNutri AI - Embedder CLIP
Geração de embeddings visuais usando OpenCLIP (CPU otimizado)
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

# Otimizações para CPU
torch.set_num_threads(4)  # Limitar threads para evitar overhead

def _load_model():
    """Carrega o modelo CLIP (lazy loading) com otimizações"""
    global _MODEL, _PREPROCESS, _DEVICE
    
    if _MODEL is None:
        print("[embedder] Carregando modelo OpenCLIP otimizado...")
        start = time.time()
        
        _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        # ViT-B-32 é um bom equilíbrio entre velocidade e qualidade
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name="ViT-B-32",
            pretrained="openai"
        )
        model = model.to(_DEVICE)
        model.eval()
        
        # Otimização: desabilitar gradientes permanentemente
        for param in model.parameters():
            param.requires_grad = False
        
        # Tentar compilar o modelo para melhor performance (PyTorch 2.0+)
        try:
            model = torch.compile(model, mode="reduce-overhead")
            print("[embedder] Modelo compilado com torch.compile!")
        except Exception as e:
            print(f"[embedder] torch.compile não disponível: {e}")
        
        _MODEL = model
        _PREPROCESS = preprocess
        
        elapsed = time.time() - start
        print(f"[embedder] Modelo carregado em {elapsed:.2f}s (device={_DEVICE})")
        
        # Warmup: executar uma inferência fake para aquecer o modelo
        _warmup_model(model, preprocess, _DEVICE)
    
    return _MODEL, _PREPROCESS, _DEVICE


def _warmup_model(model, preprocess, device):
    """Aquece o modelo com uma inferência fake"""
    try:
        fake_image = Image.new('RGB', (224, 224), color='white')
        tensor = preprocess(fake_image).unsqueeze(0).to(device)
        with torch.no_grad():
            _ = model.encode_image(tensor)
        print("[embedder] Warmup concluído!")
    except Exception as e:
        print(f"[embedder] Warmup falhou: {e}")


def _resize_image_fast(image: Image.Image, max_size: int = 384) -> Image.Image:
    """Redimensiona imagem para acelerar processamento"""
    w, h = image.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        return image.resize(new_size, Image.BILINEAR)
    return image


def image_embedding_from_path(image_path: str) -> np.ndarray:
    """Gera embedding normalizado (L2) para uma imagem a partir do caminho"""
    model, preprocess, device = _load_model()
    
    image = Image.open(image_path).convert("RGB")
    image = _resize_image_fast(image)  # Otimização
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad(), torch.inference_mode():
        features = model.encode_image(image_tensor)
        features = features / features.norm(dim=-1, keepdim=True)
    
    return features.cpu().numpy()[0].astype(np.float32)


def image_embedding_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Gera embedding normalizado (L2) para uma imagem a partir de bytes"""
    model, preprocess, device = _load_model()
    
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = _resize_image_fast(image)  # Otimização
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad(), torch.inference_mode():
        features = model.encode_image(image_tensor)
        features = features / features.norm(dim=-1, keepdim=True)
    
    return features.cpu().numpy()[0].astype(np.float32)


def preload_model():
    """Pré-carrega o modelo no startup"""
    _load_model()
    print("[embedder] Modelo pré-carregado e pronto!")
