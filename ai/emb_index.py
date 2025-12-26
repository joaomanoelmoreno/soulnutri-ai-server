# ai/emb_index.py
"""
SoulNutri AI — Servidor B (Embeddings + Similaridade)

Arquivo 4/6: IMPLEMENTAÇÃO REAL do EmbeddingIndex (CLIP + busca vetorial)

O índice é persistido em JSON (visual_index.json) para uso no Render.
O fluxo típico é:
- /ai/reindex  -> gera (ou regenera) visual_index.json
- /ai/identify-image -> gera embedding do upload e faz busca por similaridade

Observações importantes:
- Este módulo NÃO deve indexar "data/candidates".
- A indexação é feita por pasta de prato (slug), com imagens dentro.
- Usa open_clip (CLIP) para embedding, e sklearn para similaridade (cosine).
"""

import os
import json
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

import numpy as np
from PIL import Image

# open_clip + torch (CPU ok no Render)
import torch
import open_clip

# Similaridade
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# Helpers
# =========================================================

ALLOWED_EXTS = {".jpeg", ".jpg", ".png", ".webp"}


def _safe_ext(filename: str) -> str:
    _, ext = os.path.splitext((filename or "").lower())
    return ext


def _is_image_file(path: str) -> bool:
    return _safe_ext(path) in ALLOWED_EXTS


def _l2_normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v) + 1e-12)
    return (v / n).astype(np.float32)


def _basename_no_ext(p: str) -> str:
    return os.path.splitext(os.path.basename(p))[0]


def _is_candidates_dir(path: str) -> bool:
    return os.path.basename(path.rstrip("/")) == "candidates"


# =========================================================
# CLIP Embedder (cache global)
# =========================================================

_MODEL = None
_PREPROCESS = None


def _load_model():
    """
    Carrega CLIP (open_clip) em CPU.
    Mantém em cache global para evitar reload a cada request.
    """
    global _MODEL, _PREPROCESS
    if _MODEL is None or _PREPROCESS is None:
        # Modelo estável e leve para CPU: ViT-B-32
        # (compatível com os pins do requirements.txt)
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name="ViT-B-32",
            pretrained="openai",
        )
        model.eval()
        model = model.to("cpu")
        _MODEL = model
        _PREPROCESS = preprocess
    return _MODEL, _PREPROCESS


def image_embedding(image_path: str) -> np.ndarray:
    """
    Gera embedding L2-normalizado (np.float32) para uma imagem no disco.
    """
    model, preprocess = _load_model()

    img = Image.open(image_path).convert("RGB")
    img_t = preprocess(img).unsqueeze(0)  # [1, 3, H, W]
    img_t = img_t.to("cpu")

    with torch.no_grad():
        feats = model.encode_image(img_t)  # [1, D]
        feats = feats / feats.norm(dim=-1, keepdim=True)

    v = feats.cpu().numpy()[0].astype(np.float32)
    return _l2_normalize(v)


# =========================================================
# Data structures
# =========================================================

@dataclass
class IndexItem:
    dish: str
    image_path: str
    embedding: List[float]  # JSON-friendly


# =========================================================
# EmbeddingIndex
# =========================================================

class EmbeddingIndex:
    """
    Índice de embeddings persistido em JSON.
    - items: lista de IndexItem
    - matrix: np.ndarray [N, D] com embeddings normalizados
    """

    def __init__(self, index_path: str):
        self.index_path = index_path
        self.items: List[Dict[str, Any]] = []
        self.matrix: Optional[np.ndarray] = None

        # Tenta carregar índice existente
        self._load_if_exists()

    # -----------------------------
    # Persistência
    # -----------------------------

    def _load_if_exists(self):
        if not self.index_path:
            return
        if not os.path.exists(self.index_path):
            return

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            items = payload.get("items", [])
            if not isinstance(items, list):
                return

            self.items = items
            self._rebuild_matrix_from_items()

        except Exception:
            # Se quebrar, deixa índice vazio e reindexa manualmente
            self.items = []
            self.matrix = None

    def _save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        payload = {
            "ok": True,
            "version": "1.0",
            "count": len(self.items),
            "items": self.items,
        }
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _rebuild_matrix_from_items(self):
        if not self.items:
            self.matrix = None
            return

        # infer D
        emb0 = self.items[0].get("embedding") or []
        d = len(emb0)
        if d <= 0:
            self.matrix = None
            return

        mat = np.zeros((len(self.items), d), dtype=np.float32)
        for i, it in enumerate(self.items):
            emb = it.get("embedding") or []
            if len(emb) != d:
                # se inconsistente, ignora (fail-safe)
                continue
            mat[i, :] = np.array(emb, dtype=np.float32)

        # Normaliza novamente por segurança
        for i in range(mat.shape[0]):
            mat[i, :] = _l2_normalize(mat[i, :])

        self.matrix = mat

    # -----------------------------
    # Construção do índice
    # -----------------------------

    def build_from_folder(self, folder_path: str):
        """
        Indexa imagens a partir de um caminho.
        Suporta dois modos:
        1) folder_path = ".../data" -> indexa subpastas (pratos) e ignora candidates/
        2) folder_path = ".../data/<dish_slug>" -> indexa apenas aquela pasta como um prato
        """
        if not os.path.isdir(folder_path):
            return

        base = os.path.basename(folder_path.rstrip("/"))

        # Caso 2: apontou para uma pasta de prato
        # (isto é o que o main.py faz no seu /ai/reindex)
        if base != "data":
            dish_slug = base
            if dish_slug == "candidates":
                return
            self._index_dish_folder(dish_slug=dish_slug, dish_path=folder_path)
            self._finalize_build()
            return

        # Caso 1: apontou para data/
        for dish_slug in sorted(os.listdir(folder_path)):
            dish_path = os.path.join(folder_path, dish_slug)
            if not os.path.isdir(dish_path):
                continue
            if dish_slug == "candidates":
                continue
            self._index_dish_folder(dish_slug=dish_slug, dish_path=dish_path)

        self._finalize_build()

    def _index_dish_folder(self, dish_slug: str, dish_path: str):
        """
        Indexa todas as imagens dentro de data/<dish_slug>/.
        """
        if not os.path.isdir(dish_path):
            return
        if _is_candidates_dir(dish_path):
            return

        for fn in sorted(os.listdir(dish_path)):
            p = os.path.join(dish_path, fn)
            if not os.path.isfile(p):
                continue
            if not _is_image_file(p):
                continue

            try:
                emb = image_embedding(p)
            except Exception:
                # ignora imagem problemática
                continue

            item = {
                "dish": dish_slug,
                "image_path": p,
                "embedding": emb.astype(np.float32).tolist(),
            }
            self.items.append(item)

    def _finalize_build(self):
        """
        Após indexar itens, recria matriz e salva em disco.
        """
        self._rebuild_matrix_from_items()
        self._save()

    # -----------------------------
    # Busca
    # -----------------------------

    def search(self, image_path: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Retorna lista [(dish_slug, score)] ordenada do melhor para o pior.

        Estratégia:
        - gera embedding da imagem de consulta
        - calcula similaridade com todos os embeddings indexados
        - agrega por dish usando o melhor score por dish (max)
        """
        if self.matrix is None or self.matrix.shape[0] == 0:
            return []

        q = image_embedding(image_path)  # (D,)
        q = q.reshape(1, -1)  # (1, D)

        # cosine_similarity retorna (1, N)
        sims = cosine_similarity(q, self.matrix)[0]  # (N,)

        # agrega por prato (pega o máximo por dish)
        best_by_dish: Dict[str, float] = {}
        for i, it in enumerate(self.items):
            dish = it.get("dish")
            if not dish:
                continue
            s = float(sims[i])
            if dish not in best_by_dish or s > best_by_dish[dish]:
                best_by_dish[dish] = s

        # ordena
        ranked = sorted(best_by_dish.items(), key=lambda kv: kv[1], reverse=True)

        if top_k and top_k > 0:
            ranked = ranked[:top_k]

        return ranked
