import os
import json
from typing import List, Tuple, Optional

import numpy as np
from PIL import Image

import torch


class EmbeddingIndex:
    """
    Índice simples de embeddings com blindagem total:
    - NÃO faz import de open_clip no topo do arquivo.
    - Tenta open_clip dentro do método _init_backend().
    - Se falhar, backend fica NONE e o servidor NÃO cai.
    """

    def __init__(self, index_path: str):
        self.index_path = index_path

        # [(dish_slug, img_path)]
        self.items: List[Tuple[str, str]] = []
        # np.ndarray shape (N, D)
        self.matrix: Optional[np.ndarray] = None

        self._device = "cpu"
        self._backend = None  # "open_clip" | None
        self._model = None
        self._preprocess = None

        self._init_backend()
        self._load_index_if_exists()

    # -----------------------------
    # Backend init (SAFE)
    # -----------------------------
    def _init_backend(self):
        """
        Nunca derruba o servidor.
        Se open_clip não existir, só desliga o reconhecimento por imagem.
        """
        try:
            import open_clip  # <- IMPORT SOMENTE AQUI (nunca no topo)

            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="laion2b_s34b_b79k",
                device=self._device,
            )
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
        if not os.path.exists(self.index_path):
            return
        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.items = [(x["dish"], x["path"]) for x in data.get("items", [])]
            mat = data.get("matrix", None)
            if mat is not None:
                self.matrix = np.array(mat, dtype=np.float32)
            print(f"[emb] loaded index: items={len(self.items)}")
        except Exception as e:
            print(f"[emb] failed to load index: {e}")

    def _save_index(self):
        payload = {
            "items": [{"dish": d, "path": p} for (d, p) in self.items],
            "matrix": self.matrix.tolist() if self.matrix is not None else None,
        }
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

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

            # Se backend está NONE, não indexa — mas NÃO quebra.
            if vec is None:
                continue

            self.items.append((dish_slug, img_path))
            if self.matrix is None:
                self.matrix = vec.reshape(1, -1)
            else:
                self.matrix = np.vstack([self.matrix, vec.reshape(1, -1)])

        self._save_index()

    def search(self, img_path: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self._backend is None:
            return []
        if self.matrix is None or len(self.items) == 0:
            return []

        q = self._embed_image(img_path)
        if q is None:
            return []

        sims = (self.matrix @ q.reshape(-1, 1)).reshape(-1)
        idx = np.argsort(-sims)[: max(1, top_k)]

        out: List[Tuple[str, float]] = []
        for i in idx:
            dish_slug, _p = self.items[int(i)]
            out.append((dish_slug, float(sims[int(i)])))
        return out
