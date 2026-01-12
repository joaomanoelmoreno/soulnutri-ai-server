import os
import json
from typing import Optional, List, Tuple

import numpy as np
from PIL import Image


class EmbIndex:
    """
    Índice por embeddings (OpenCLIP).
    Versão "Render-safe": não carrega modelo no startup e permite desabilitar por ENV.
    """

    def __init__(
        self,
        data_dir: str = "data",
        index_filename: str = "emb_index.json",
        device: Optional[str] = None,
    ):
        self.data_dir = data_dir
        if not index_filename:
            index_filename = "emb_index.json"
        self.index_path = os.path.join(self.data_dir, index_filename)

        self.items: List[Tuple[str, str]] = []
        self.matrix: Optional[np.ndarray] = None

        # Embeddings / backend (lazy)
        self._backend: Optional[str] = None
        self._model = None
        self._preprocess = None

        # Device (lazy: só resolve quando for carregar torch)
        self._device_pref = device  # "cpu" / "cuda" / None

        # Flag para desabilitar embeddings completamente (ex.: Render 512Mi)
        self._emb_disabled = os.getenv("SOULNUTRI_EMB_DISABLED", "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        if self._emb_disabled:
            print("[emb] disabled by env SOULNUTRI_EMB_DISABLED=1")

        # Carrega índice em disco se existir (isso é leve)
        self._load_index_if_exists()

    # -----------------------------
    # Index persistence
    # -----------------------------
    def _load_index_if_exists(self):
        if not self.index_path:
            return
        if not os.path.exists(self.index_path):
            return
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
    # Backend (lazy open_clip)
    # -----------------------------
    def _ensure_backend(self) -> bool:
        """
        Garante que o backend/modelo estão carregados.
        Retorna True se pronto, False se indisponível/desabilitado.
        """
        if self._emb_disabled:
            return False

        if self._backend == "open_clip" and self._model is not None and self._preprocess is not None:
            return True

        try:
            import torch  # import pesado, mas só ocorre quando necessário
            import open_clip

            if self._device_pref:
                device = self._device_pref
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"

            model, _, preprocess = open_clip.create_model_and_transforms(
                "ViT-B-32",
                pretrained="openai",
            )
            model = model.to(device)
            model.eval()

            self._backend = "open_clip"
            self._model = model
            self._preprocess = preprocess
            self._device = device
            print("[emb] backend=open_clip OK (lazy loaded)")
            return True

        except Exception as e:
            self._backend = None
            self._model = None
            self._preprocess = None
            print(f"[emb] backend=NONE (open_clip unavailable): {e}")
            return False

    # -----------------------------
    # Embeddings
    # -----------------------------
    def _embed_image(self, img_path: str) -> Optional[np.ndarray]:
        if not self._ensure_backend():
            return None

        # imports aqui para reduzir startup footprint
        import torch

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
    def is_ready(self) -> bool:
        return self.matrix is not None and len(self.items) > 0

    def build_from_folder(self, dish_folder: str):
        """
        Constrói embeddings do folder. Atenção: isso pode consumir muita RAM/CPU.
        Em instância 512Mi, recomenda-se NÃO rodar reindex aqui.
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
                # embeddings desabilitados ou backend indisponível
                continue

            if self.matrix is None:
                self.matrix = vec.reshape(1, -1)
            else:
                self.matrix = np.vstack([self.matrix, vec])

            self.items.append((dish_slug, img_path))

        # salva índice (se existiu construção)
        if self.matrix is not None and self.items:
            self._save_index()
