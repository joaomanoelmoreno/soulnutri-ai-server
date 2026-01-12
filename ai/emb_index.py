import os
import json
import numpy as np
import torch
from typing import Optional, List, Tuple
from PIL import Image

# =========================
# Embedding Index
# =========================

class EmbIndex:
    def __init__(
        self,
        data_dir: str = "data",
        index_filename: str = "emb_index.json",
        device: Optional[str] = None,
    ):
        # Diretório base de dados
        self.data_dir = data_dir

        # Normalização do caminho do índice (SEMPRE arquivo, nunca diretório)
        if not index_filename:
            index_filename = "emb_index.json"

        self.index_path = os.path.join(self.data_dir, index_filename)

        # Estruturas em memória
        self.items: List[Tuple[str, str]] = []
        self.matrix: Optional[np.ndarray] = None

        # Device
        if device:
            self._device = device
        else:
            self._device = "cuda" if torch.cuda.is_available() else "cpu"

        # Backend de embeddings
        self._backend = None
        self._model = None
        self._preprocess = None

        # Inicialização
        self._init_backend()
        self._load_index_if_exists()

    # -----------------------------
    # Backend (OpenCLIP)
    # -----------------------------
    def _init_backend(self):
        try:
            import open_clip

            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="openai"
            )
            model = model.to(self._device)
            model.eval()

            self._backend = "open_clip"
            self._model = model
            self._preprocess = preprocess
            print("[emb] backend=open_clip OK")

        except Exception as e:
            self._backend = None
            self._model = None
            self._preprocess = None
            print(f"[emb] backend=NONE (open_clip unavailable): {e}")

    # -----------------------------
    # Index persistence
    # -----------------------------
    def _load_index_if_exists(self):
        # Se não existir, nada a fazer
        if not self.index_path:
            return
        if not os.path.exists(self.index_path):
            return
        # Blindagem: nunca tentar abrir diretório
        if os.path.isdir(self.index_path):
            print(f"[emb] index_path is a directory, skipping load: {self.index_path!r}")
            return

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.items = [(x["dish"], x["path"]) for x in data.get("items", [])]

            mat = data.get("matrix")
            if mat is not None:
                self.matrix = np.array(mat, dtype=np.float32)

            print(f"[emb] loaded index: items={len(self.items)}")

        except Exception as e:
            print(f"[emb] failed to load index: {e}")

    def _save_index(self):
        # Blindagem: não salva se path inválido
        if not self.index_path or os.path.isdir(self.index_path):
            print(f"[emb] index_path invalid for save: {self.index_path!r}")
            return

        payload = {
            "items": [{"dish": d, "path": p} for (d, p) in self.items],
            "matrix": self.matrix.tolist() if self.matrix is not None else None,
        }

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        print(f"[emb] index saved: {self.index_path}")

    # -----------------------------
    # Embeddings
    # -----------------------------
    def _embed_image(self, img_path: str) -> Optional[np.ndarray]:
        if self._backend is None or self._model is None or self._preprocess is None:
            return None

        img = Image.open(img_path).convert("RGB")
        x = self._preprocess(img).unsqueeze(0).to(self._device)

        with torch.no_grad():
            feats = self._model.encode_image(x)
            feats = feats / feats.norm(dim=-1, keepdim=True)
            vec = feats.squeeze(0).cpu().numpy().astype(np.float32)

        return vec

    # -----------------------------
    # Public API
    # -----------------------------
    def build_from_folder(self, dish_folder: str):
        dish_slug = os.path.basename(dish_folder.rstrip("/"))
        exts = {".jpg", ".jpeg", ".png", ".webp"}

        for fn in sorted(os.listdir(dish_folder)):
            _, ext = os.path.splitext(fn.lower())
            if ext not in exts:
                continue

            img_path = os.path.join(dish_folder, fn)
            vec = self._embed_image(img_path)
            if vec is None:
                continue

            if self.matrix is None:
                self.matrix = vec.reshape(1, -1)
            else:
                self.matrix = np.vstack([self.matrix, vec])

            self.items.append((dish_slug, img_path))

        self._save_index()

    def is_ready(self) -> bool:
        return self.matrix is not None and len(self.items) > 0
