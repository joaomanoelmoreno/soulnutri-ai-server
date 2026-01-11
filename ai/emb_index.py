import os
import json
from typing import List, Tuple, Optional

import numpy as np
from PIL import Image

# Torch é necessário para qualquer modo de embeddings
import torch


class EmbeddingIndex:
    """
    Índice simples de embeddings com fallback:
      1) tenta OpenCLIP (open_clip)
      2) se não existir, tenta CLIP (openai/CLIP)
      3) se nada existir, NÃO derruba o servidor:
         - search() retorna [] e o app continua vivo
    """

    def __init__(self, index_path: str):
        self.index_path = index_path
        self.items: List[Tuple[str, str]] = []  # [(dish_slug, img_path)]
        self.matrix: Optional[np.ndarray] = None  # shape (N, D)

        self._device = "cpu"
        self._backend = None  # "open_clip" | "clip" | None
        self._model = None
        self._preprocess = None
        self._tokenizer = None  # usado no open_clip

        self._init_backend()
        self._load_index_if_exists()

    # -----------------------------
    # Backend init
    # -----------------------------
    def _init_backend(self):
        # 1) Tentar OpenCLIP
        try:
            import open_clip  # type: ignore

            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="laion2b_s34b_b79k",
                device=self._device,
            )
            model.eval()

            self._backend = "open_clip"
            self._model = model
            self._preprocess = preprocess
            self._tokenizer = open_clip.get_tokenizer("ViT-B-32")
            print("[emb] backend=open_clip OK")
            return
        except Exception as e:
            print(f"[emb] backend=open_clip NOT available: {e}")

        # 2) Tentar CLIP (OpenAI)
        try:
            import clip  # type: ignore

            model, preprocess = clip.load("ViT-B/32", device=self._device)
            model.eval()

            self._backend = "clip"
            self._model = model
            self._preprocess = preprocess
            print("[emb] backend=clip OK")
            return
        except Exception as e:
            print(f"[emb] backend=clip NOT available: {e}")

        # 3) Sem backend (não derruba o servidor)
        self._backend = None
        self._model = None
        self._preprocess = None
        self._tokenizer = None
        print("[emb] backend=NONE (service will run without image recognition)")

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
            if self._backend == "open_clip":
                # open_clip: encode_image -> tensor (1, D)
                feats = self._model.encode_image(x)
            else:
                # clip: encode_image -> tensor (1, D)
                feats = self._model.encode_image(x)

            feats = feats / feats.norm(dim=-1, keepdim=True)
            vec = feats.squeeze(0).cpu().numpy().astype(np.float32)

        return vec

    # -----------------------------
    # Public API
    # -----------------------------
    def build_from_folder(self, dish_folder: str):
        """
        Indexa todas as imagens de uma pasta de prato: data/<dish>/*.jpg
        O slug do prato é o nome da pasta.
        """
        dish_slug = os.path.basename(dish_folder.rstrip("/"))
        exts = {".jpg", ".jpeg", ".png", ".webp"}

        for fn in sorted(os.listdir(dish_folder)):
            _, ext = os.path.splitext(fn.lower())
            if ext not in exts:
                continue

            img_path = os.path.join(dish_folder, fn)

            vec = self._embed_image(img_path)
            if vec is None:
                # backend ausente: não indexa, mas não quebra
                continue

            self.items.append((dish_slug, img_path))
            if self.matrix is None:
                self.matrix = vec.reshape(1, -1)
            else:
                self.matrix = np.vstack([self.matrix, vec.reshape(1, -1)])

        # salva no final
        self._save_index()

    def search(self, img_path: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Retorna [(dish_slug, score)].
        score = similaridade cosseno (0..1 em geral).
        """
        if self._backend is None:
            return []
        if self.matrix is None or len(self.items) == 0:
            return []

        q = self._embed_image(img_path)
        if q is None:
            return []

        # cosine similarity
        sims = (self.matrix @ q.reshape(-1, 1)).reshape(-1)
        idx = np.argsort(-sims)[: max(1, top_k)]

        out: List[Tuple[str, float]] = []
        for i in idx:
            dish_slug, _p = self.items[int(i)]
            out.append((dish_slug, float(sims[int(i)])))
        return out
