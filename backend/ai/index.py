"""SoulNutri AI - Índice Visual
Índice de embeddings para busca por similaridade (Top-K)
Meta: resposta em 100ms
"""

import os
import json
import hashlib
import numpy as np
from typing import Dict, List, Mapping, Optional, Tuple
from pathlib import Path
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from .embedder import image_embedding_from_path, image_embedding_from_bytes
from .index_loader import LoadedIndexArtifacts, load_index_artifacts


DEFAULT_V1_INDEX_FILE = "/app/datasets/dish_index.json"
DEFAULT_V2_INDEX_FILE = "/app/datasets/recognition_v2/dish_index.json"

# Candidate v2 approved by the reproducibility and holdout gates. Explicit v2
# activation must load this exact pair; availability alone never activates it.
APPROVED_V2_INDEX_SHA256 = (
    "32058e88fb3ed46a49237b7936b8f333eaea63089e0b7aa19ffb64c3b31d07e8"
)
APPROVED_V2_EMBEDDINGS_SHA256 = (
    "baa4d607c9fb4f5e53deecb96e79e818a973ed660a560426c6271f2ac64937eb"
)
APPROVED_V2_VISUAL_CLASSES = 236
APPROVED_V2_EMBEDDINGS = 1508
APPROVED_V2_EMBEDDING_DIM = 512


class RecognitionIndexConfigurationError(RuntimeError):
    """Raised when explicit index selection cannot be honored safely."""


@dataclass(frozen=True)
class RecognitionIndexConfiguration:
    version: str
    index_file: str
    embeddings_file: str
    expected_schema_version: int
    expected_index_sha256: Optional[str] = None
    expected_embeddings_sha256: Optional[str] = None
    expected_visual_classes: Optional[int] = None
    expected_embeddings: Optional[int] = None
    expected_embedding_dim: Optional[int] = None


def _paired_embeddings_file(index_file: str) -> str:
    path = Path(index_file)
    if path.suffix.lower() != ".json":
        raise RecognitionIndexConfigurationError(
            "recognition index path must end with .json"
        )
    return str(path.with_name(f"{path.stem}_embeddings.npy"))


def resolve_index_configuration(
    environ: Optional[Mapping[str, str]] = None,
) -> RecognitionIndexConfiguration:
    """Resolve v1/v2 explicitly; absence preserves the production v1 default."""
    env = os.environ if environ is None else environ
    raw_version = env.get("RECOGNITION_INDEX_VERSION")
    version = "v1" if raw_version is None else raw_version.strip().lower()
    if version not in {"v1", "v2"}:
        raise RecognitionIndexConfigurationError(
            "RECOGNITION_INDEX_VERSION must be 'v1' or 'v2'"
        )

    if version == "v1":
        index_file = env.get(
            "RECOGNITION_V1_INDEX_FILE", DEFAULT_V1_INDEX_FILE
        ).strip()
        if not index_file:
            raise RecognitionIndexConfigurationError(
                "RECOGNITION_V1_INDEX_FILE must not be empty"
            )
        embeddings_file = env.get(
            "RECOGNITION_V1_EMBEDDINGS_FILE",
            _paired_embeddings_file(index_file),
        ).strip()
        if not embeddings_file:
            raise RecognitionIndexConfigurationError(
                "RECOGNITION_V1_EMBEDDINGS_FILE must not be empty"
            )
        return RecognitionIndexConfiguration(
            version="v1",
            index_file=index_file,
            embeddings_file=embeddings_file,
            expected_schema_version=1,
        )

    index_file = env.get(
        "RECOGNITION_V2_INDEX_FILE", DEFAULT_V2_INDEX_FILE
    ).strip()
    if not index_file:
        raise RecognitionIndexConfigurationError(
            "RECOGNITION_V2_INDEX_FILE must not be empty"
        )
    embeddings_file = env.get(
        "RECOGNITION_V2_EMBEDDINGS_FILE",
        _paired_embeddings_file(index_file),
    ).strip()
    if not embeddings_file:
        raise RecognitionIndexConfigurationError(
            "RECOGNITION_V2_EMBEDDINGS_FILE must not be empty"
        )
    return RecognitionIndexConfiguration(
        version="v2",
        index_file=index_file,
        embeddings_file=embeddings_file,
        expected_schema_version=2,
        expected_index_sha256=APPROVED_V2_INDEX_SHA256,
        expected_embeddings_sha256=APPROVED_V2_EMBEDDINGS_SHA256,
        expected_visual_classes=APPROVED_V2_VISUAL_CLASSES,
        expected_embeddings=APPROVED_V2_EMBEDDINGS,
        expected_embedding_dim=APPROVED_V2_EMBEDDING_DIM,
    )


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class DishIndex:
    """
    Índice visual de pratos usando embeddings.
    Usa busca por similaridade de cosseno para identificar pratos.
    """
    
    def __init__(
        self,
        data_dir: str = "/app/datasets/organized",
        index_file: str = DEFAULT_V1_INDEX_FILE,
        embeddings_file: Optional[str] = None,
        *,
        configured_version: Optional[str] = None,
        expected_schema_version: Optional[int] = None,
        expected_index_sha256: Optional[str] = None,
        expected_embeddings_sha256: Optional[str] = None,
        expected_visual_classes: Optional[int] = None,
        expected_embeddings: Optional[int] = None,
        expected_embedding_dim: Optional[int] = None,
        strict_load: bool = False,
    ):
        self.data_dir = data_dir
        self.index_file = index_file
        self.embeddings_file = embeddings_file or _paired_embeddings_file(index_file)
        self.configured_version = configured_version
        self.expected_schema_version = expected_schema_version
        self.expected_index_sha256 = expected_index_sha256
        self.expected_embeddings_sha256 = expected_embeddings_sha256
        self.expected_visual_classes = expected_visual_classes
        self.expected_embeddings = expected_embeddings
        self.expected_embedding_dim = expected_embedding_dim
        self.strict_load = strict_load
        self.index_metadata_sha256: Optional[str] = None
        self.embeddings_sha256: Optional[str] = None
        
        # Estrutura do índice
        self.dishes: List[str] = []  # Lista de nomes de pratos
        self.embeddings: Optional[np.ndarray] = None  # Matriz de embeddings
        self.dish_to_idx: Dict[str, List[int]] = {}  # Mapa prato -> índices
        self.metadata: Dict[str, dict] = {}  # Metadados por prato
        self.recognition_schema_version = 1
        self.loaded_artifacts: Optional[LoadedIndexArtifacts] = None
        
        # Tenta carregar índice existente
        self._load_index()
    
    def _load_index(self) -> bool:
        """Carrega índice do disco se existir"""
        if not os.path.exists(self.index_file):
            message = f"Índice não encontrado: {self.index_file}"
            if self.strict_load:
                print("[index] Índice configurado indisponível")
                raise RecognitionIndexConfigurationError(
                    "configured recognition index JSON is unavailable"
                )
            print(f"[index] {message}")
            return False
        try:
            index_sha256 = _sha256_file(self.index_file)
            embeddings_sha256 = (
                _sha256_file(self.embeddings_file)
                if os.path.exists(self.embeddings_file)
                else None
            )
            if (
                self.expected_index_sha256 is not None
                and index_sha256 != self.expected_index_sha256
            ):
                raise RecognitionIndexConfigurationError(
                    "configured v2 index JSON does not match the approved SHA-256"
                )
            if (
                self.expected_embeddings_sha256 is not None
                and embeddings_sha256 != self.expected_embeddings_sha256
            ):
                raise RecognitionIndexConfigurationError(
                    "configured v2 embeddings do not match the approved SHA-256"
                )
            artifacts = load_index_artifacts(
                self.index_file, self.embeddings_file
            )
            if (
                self.expected_schema_version is not None
                and artifacts.schema_version != self.expected_schema_version
            ):
                raise RecognitionIndexConfigurationError(
                    f"configured {self.configured_version or 'index'} artifacts use "
                    f"schema v{artifacts.schema_version}, expected "
                    f"v{self.expected_schema_version}"
                )
            if (
                self.expected_visual_classes is not None
                and len(artifacts.dish_to_idx) != self.expected_visual_classes
            ):
                raise RecognitionIndexConfigurationError(
                    "configured v2 index has an unexpected visual class count"
                )
            if (
                self.expected_embeddings is not None
                and len(artifacts.visual_labels) != self.expected_embeddings
            ):
                raise RecognitionIndexConfigurationError(
                    "configured v2 index has an unexpected embedding count"
                )
            if (
                self.expected_embedding_dim is not None
                and artifacts.embeddings.shape[1] != self.expected_embedding_dim
            ):
                raise RecognitionIndexConfigurationError(
                    "configured v2 index has an unexpected embedding dimension"
                )
            self.dishes = list(artifacts.visual_labels)
            self.dish_to_idx = {
                name: list(indices)
                for name, indices in artifacts.dish_to_idx.items()
            }
            self.metadata = dict(artifacts.legacy_metadata)
            self.embeddings = artifacts.embeddings
            self.recognition_schema_version = artifacts.schema_version
            self.loaded_artifacts = artifacts
            self.configured_version = (
                self.configured_version or f"v{artifacts.schema_version}"
            )
            self.index_metadata_sha256 = index_sha256
            self.embeddings_sha256 = embeddings_sha256
            print(
                f"[index] Índice carregado: {len(self.dishes)} itens, "
                f"{len(self.dish_to_idx)} pratos"
            )
            return True
            
        except Exception as e:
            print(f"[index] Erro ao carregar índice: {e}")
            if self.strict_load:
                if isinstance(e, RecognitionIndexConfigurationError):
                    raise
                raise RecognitionIndexConfigurationError(
                    "configured recognition index artifacts failed validation"
                ) from e
        
        return False
    
    def _save_index(self):
        """Salva índice no disco"""
        try:
            data = {
                'dishes': self.dishes,
                'dish_to_idx': self.dish_to_idx,
                'metadata': self.metadata,
                'version': '1.0',
                'total_items': len(self.dishes),
                'total_dishes': len(self.dish_to_idx)
            }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Salva embeddings separadamente (mais eficiente)
            if self.embeddings is not None:
                np.save(self.embeddings_file, self.embeddings)
            self.recognition_schema_version = 1
            self.loaded_artifacts = None
            self.configured_version = "v1"
            self.index_metadata_sha256 = _sha256_file(self.index_file)
            self.embeddings_sha256 = _sha256_file(self.embeddings_file)
            
            print(f"[index] Índice salvo: {self.index_file}")
            
        except Exception as e:
            print(f"[index] Erro ao salvar índice: {e}")
    
    def build_index(self, max_per_dish: int = 10) -> dict:
        """
        Constrói o índice a partir das pastas de pratos.
        
        Args:
            max_per_dish: Máximo de imagens por prato (para limitar tamanho)
        
        Returns:
            Estatísticas da indexação
        """
        if self.configured_version == "v2":
            raise RecognitionIndexConfigurationError(
                "legacy reindex is disabled while recognition index v2 is active"
            )
        print(f"[index] Iniciando indexação de {self.data_dir}...")
        start_time = time.time()
        
        self.dishes = []
        self.dish_to_idx = {}
        embeddings_list = []
        
        # Listar pastas de pratos
        if not os.path.exists(self.data_dir):
            return {'error': f'Diretório não encontrado: {self.data_dir}'}
        
        dish_folders = sorted([d for d in os.listdir(self.data_dir) 
                               if os.path.isdir(os.path.join(self.data_dir, d))])
        
        total_images = 0
        
        for dish_name in dish_folders:
            dish_path = os.path.join(self.data_dir, dish_name)
            
            # Listar imagens
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
            images = [f for f in os.listdir(dish_path)
                     if Path(f).suffix.lower() in image_extensions]
            
            if not images:
                continue
            
            # Limitar número de imagens por prato
            images = images[:max_per_dish]
            
            dish_indices = []
            
            for img_file in images:
                img_path = os.path.join(dish_path, img_file)
                
                try:
                    # Gerar embedding
                    embedding = image_embedding_from_path(img_path)
                    
                    # Validar embedding antes de adicionar
                    if embedding is None or not hasattr(embedding, 'shape') or embedding.shape != (512,):
                        print(f"[index] Embedding inválido para {img_path}, pulando")
                        continue
                    
                    # Adicionar ao índice
                    idx = len(self.dishes)
                    self.dishes.append(dish_name)
                    embeddings_list.append(embedding)
                    dish_indices.append(idx)
                    total_images += 1
                    
                except Exception as e:
                    print(f"[index] Erro ao processar {img_path}: {e}")
            
            if dish_indices:
                self.dish_to_idx[dish_name] = dish_indices
                self.metadata[dish_name] = {
                    'image_count': len(dish_indices),
                    'total_available': len([f for f in os.listdir(dish_path)
                                           if Path(f).suffix.lower() in image_extensions])
                }
        
        if embeddings_list:
            self.embeddings = np.array(embeddings_list, dtype=np.float32)
            self._save_index()
        
        elapsed = time.time() - start_time
        stats = {
            'total_dishes': len(self.dish_to_idx),
            'total_images': total_images,
            'embedding_dim': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'elapsed_seconds': round(elapsed, 1)
        }
        
        print(f"[index] Indexação concluída: {stats}")
        return stats
    
    def search(self, image_bytes: bytes, top_k: int = 5) -> List[Dict]:
        """
        Busca os pratos mais similares a uma imagem.
        
        Args:
            image_bytes: Bytes da imagem de query
            top_k: Número de resultados
        
        Returns:
            Lista de resultados com prato, score e confiança
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return [{'error': 'Índice não carregado ou vazio'}]
        
        start_time = time.time()
        
        # Gerar embedding da query
        t0 = time.time()
        query_embedding = image_embedding_from_bytes(image_bytes)
        t_embed = (time.time() - t0) * 1000
        logger.info(f"[TIMING] Embedding (ONNX/PyTorch): {t_embed:.0f}ms")
        
        # Verificar se embedding foi gerado com sucesso
        if query_embedding is None:
            return [{'error': 'Falha ao gerar embedding da imagem. Tente novamente.'}]
        
        # Calcular similaridade de cosseno
        t0 = time.time()
        # Como os embeddings já estão normalizados, o dot product = cosine similarity
        similarities = np.dot(self.embeddings, query_embedding)
        t_sim = (time.time() - t0) * 1000
        logger.info(f"[TIMING] Similaridade ({len(self.embeddings)} embeddings): {t_sim:.1f}ms")
        
        # Pegar top-k índices (mais para agregar e medir consistencia)
        top_indices = np.argsort(similarities)[::-1][:top_k * 10]
        
        # Medir consistencia: dos top-15 matches individuais, quantos pratos diferentes?
        top15_dishes = []
        for idx in top_indices[:15]:
            if idx < len(self.dishes):
                top15_dishes.append(self.dishes[idx])
        consistency_dishes = len(set(top15_dishes))
        # Se top-15 tem 1-3 pratos: alta consistencia. 5+: modelo confuso.
        consistency_penalty = max(0, (consistency_dishes - 3) * 0.02)
        
        # Agregar por prato (pegar melhor score de cada prato)
        dish_scores: Dict[str, float] = {}
        for idx in top_indices:
            if idx >= len(self.dishes):
                continue
            dish = self.dishes[idx]
            score = float(similarities[idx])
            if dish not in dish_scores or score > dish_scores[dish]:
                dish_scores[dish] = score
        
        # Ordenar por score
        sorted_dishes = sorted(dish_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Calcular gap entre 1o e 2o lugar
        gap = 0.0
        if len(sorted_dishes) >= 2:
            gap = sorted_dishes[0][1] - sorted_dishes[1][1]
        
        # Penalidade por gap pequeno (modelo indeciso entre pratos)
        gap_penalty = 0.0
        if gap < 0.03:
            gap_penalty = (0.03 - gap) * 2  # Quanto menor o gap, maior a penalidade
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        results = []
        for i, (dish_name, raw_score) in enumerate(sorted_dishes):
            # Aplicar penalidades apenas ao 1o lugar
            adjusted_score = raw_score
            if i == 0:
                adjusted_score = raw_score - consistency_penalty - gap_penalty
                adjusted_score = max(0, adjusted_score)
            
            confidence_level = self._get_confidence_level(adjusted_score)
            logger.debug(f"[CLIP] {dish_name} - Raw: {raw_score:.3f} Adj: {adjusted_score:.3f} Gap: {gap:.3f} Consist: {consistency_dishes} - {confidence_level}")
            results.append({
                'dish': dish_name,
                'score': round(adjusted_score, 4),
                'raw_score': round(raw_score, 4),
                'confidence': confidence_level,
                'gap': round(gap, 4),
                'consistency': consistency_dishes,
                'image_count': self.metadata.get(dish_name, {}).get('image_count', 0)
            })

        # Preservar a identidade e as alternativas definidas pela similaridade bruta.
        # As penalidades ajustam somente o score/confianca do top-1.
        
        # Adicionar metadados da busca
        if results:
            results[0]['search_time_ms'] = round(elapsed_ms, 2)
        
        return results
    
    def search_by_dish(self, dish_name: str) -> List[Dict]:
        """Busca embeddings de um prato específico"""
        if dish_name not in self.dish_to_idx:
            return []
        
        indices = self.dish_to_idx[dish_name]
        return [{
            'dish': dish_name,
            'index': idx,
            'embedding_norm': float(np.linalg.norm(self.embeddings[idx]))
        } for idx in indices]
    
    def find_dish(self, query: str) -> Optional[str]:
        """Busca prato por nome (case-insensitive, parcial)"""
        query_lower = query.lower().strip()
        
        # Busca exata
        for dish in self.dish_to_idx:
            if dish.lower() == query_lower:
                return dish
        
        # Busca parcial
        for dish in self.dish_to_idx:
            if query_lower in dish.lower():
                return dish
        
        return None
    
    def direct_match(self, dish_name: str) -> List[Dict]:
        """Retorna match direto para um prato conhecido"""
        matched_dish = self.find_dish(dish_name)
        if not matched_dish:
            return []
        
        return [{
            'dish': matched_dish,
            'score': 0.90,
            'raw_score': 0.90,
            'confidence': 'alta',
            'image_count': self.metadata.get(matched_dish, {}).get('image_count', 0),
            'source': 'direct_match'
        }]
    
    def _get_confidence_level(self, score: float) -> str:
        """Converte score em nível de confiança (sincronizado com policy.py)"""
        if score >= 0.90:
            return "alta"
        elif score >= 0.50:
            return "media"
        else:
            return "baixa"
    
    def is_ready(self) -> bool:
        """Verifica se o índice está pronto para buscas"""
        return self.embeddings is not None and len(self.embeddings) > 0
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do índice"""
        return {
            'ready': self.is_ready(),
            'total_dishes': len(self.dish_to_idx),
            'total_visual_classes': len(self.dish_to_idx),
            'total_embeddings': len(self.dishes),
            'embedding_dim': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'recognition_index_version': self.configured_version or f"v{self.recognition_schema_version}",
            'index_metadata_sha256': self.index_metadata_sha256,
            'embeddings_sha256': self.embeddings_sha256,
            'index_file': self.index_file,
        }


# Instância global do índice
_INDEX: Optional[DishIndex] = None

def get_index() -> DishIndex:
    """Retorna a instância global do índice"""
    global _INDEX
    if _INDEX is None:
        config = resolve_index_configuration()
        _INDEX = DishIndex(
            index_file=config.index_file,
            embeddings_file=config.embeddings_file,
            configured_version=config.version,
            expected_schema_version=config.expected_schema_version,
            expected_index_sha256=config.expected_index_sha256,
            expected_embeddings_sha256=config.expected_embeddings_sha256,
            expected_visual_classes=config.expected_visual_classes,
            expected_embeddings=config.expected_embeddings,
            expected_embedding_dim=config.expected_embedding_dim,
            strict_load=config.version == "v2",
        )
    return _INDEX


def get_index_info() -> dict:
    """Retorna informacoes do indice incluindo nomes dos pratos."""
    idx = get_index()
    return {**idx.get_stats(), "dish_names": sorted(idx.dish_to_idx.keys())}
