# SoulNutri AI — Embedder CLIP
# Geração de embeddings visuais usando CLIP (CPU)

import torch
import open_clip
import numpy as np
from PIL import Image

# Cache global do modelo
_MODEL = None
_PREPROCESS = None

def _load_model():
    global _MODEL, _PREPROCESS
    if _MODEL is None:
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name="ViT-B-32",
            pretrained="openai"
        )
        model.eval()
        _MODEL = model
        _PREPROCESS = preprocess
    return _MODEL, _PREPROCESS

def image_embedding(image_path: str) -> np.ndarray:
    """
    Gera embedding normalizado (L2) para uma imagem.
    """
    model, preprocess = _load_model()

    image = Image.open(image_path).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        features = model.encode_image(image_tensor)
        features = features / features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy()[0]
