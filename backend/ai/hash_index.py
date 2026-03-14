"""
SoulNutri - Serviço de Hash de Imagem
Detecta imagens idênticas/muito similares ao dataset para retorno instantâneo.
Usa thumbnail hash: reduz imagem a 16x16 grayscale e gera hash dos pixels.
"""

import hashlib
import logging
import json
import os
import time
from pathlib import Path
from PIL import Image
import io

logger = logging.getLogger(__name__)

_HASH_INDEX = None

def _compute_image_hash(image_bytes: bytes) -> str:
    """Gera hash perceptual básico: thumbnail 16x16 grayscale → SHA256."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("L").resize((16, 16), Image.LANCZOS)
        pixel_data = img.tobytes()
        return hashlib.sha256(pixel_data).hexdigest()
    except Exception as e:
        logger.warning(f"[hash] Erro ao computar hash: {e}")
        return None


class ImageHashIndex:
    """Índice de hashes de imagens do dataset para match instantâneo."""
    
    def __init__(self):
        self.hash_to_dish = {}
        self.total_hashes = 0
        self.index_file = Path("/app/datasets/image_hash_index.json")
    
    def build(self, dataset_dir: str = "/app/datasets/organized"):
        """Constrói o índice de hashes a partir das imagens do dataset."""
        start = time.time()
        self.hash_to_dish = {}
        
        base = Path(dataset_dir)
        if not base.exists():
            logger.warning("[hash] Diretório do dataset não encontrado")
            return
        
        for dish_dir in base.iterdir():
            if not dish_dir.is_dir():
                continue
            
            dish_slug = dish_dir.name
            
            # Ler nome de exibição do dish_info.json
            display_name = dish_slug
            info_path = dish_dir / "dish_info.json"
            if info_path.exists():
                try:
                    with open(info_path) as f:
                        info = json.load(f)
                    display_name = info.get("nome", dish_slug)
                except Exception:
                    pass
            
            # Hashear todas as imagens do prato
            for img_file in dish_dir.iterdir():
                if img_file.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                    try:
                        img_bytes = img_file.read_bytes()
                        h = _compute_image_hash(img_bytes)
                        if h:
                            self.hash_to_dish[h] = {
                                "slug": dish_slug,
                                "display_name": display_name
                            }
                    except Exception as e:
                        logger.warning(f"[hash] Erro ao processar {img_file.name}: {e}")
        
        self.total_hashes = len(self.hash_to_dish)
        elapsed = time.time() - start
        logger.info(f"[hash] Índice construído: {self.total_hashes} hashes em {elapsed:.1f}s")
        
        # Salvar para carregamento rápido
        self._save()
    
    def _save(self):
        """Salva índice em disco."""
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.hash_to_dish, f)
            logger.info(f"[hash] Índice salvo: {self.index_file}")
        except Exception as e:
            logger.error(f"[hash] Erro ao salvar: {e}")
    
    def load(self):
        """Carrega índice do disco."""
        if self.index_file.exists():
            try:
                with open(self.index_file) as f:
                    self.hash_to_dish = json.load(f)
                self.total_hashes = len(self.hash_to_dish)
                logger.info(f"[hash] Índice carregado: {self.total_hashes} hashes")
                return True
            except Exception as e:
                logger.error(f"[hash] Erro ao carregar: {e}")
        return False
    
    def lookup(self, image_bytes: bytes) -> dict:
        """
        Busca uma imagem no índice de hashes.
        Retorna dict com slug e display_name se encontrado, None caso contrário.
        """
        if not self.hash_to_dish:
            return None
        
        h = _compute_image_hash(image_bytes)
        if h and h in self.hash_to_dish:
            match = self.hash_to_dish[h]
            logger.info(f"[hash] Match exato encontrado: {match['display_name']}")
            return match
        
        return None
    
    def is_ready(self) -> bool:
        return self.total_hashes > 0
    
    def status(self) -> dict:
        return {
            "ready": self.is_ready(),
            "total_hashes": self.total_hashes
        }


# Singleton
_HASH_INDEX = None

def get_hash_index() -> ImageHashIndex:
    global _HASH_INDEX
    if _HASH_INDEX is None:
        _HASH_INDEX = ImageHashIndex()
        if not _HASH_INDEX.load():
            _HASH_INDEX.build()
    return _HASH_INDEX
