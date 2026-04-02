"""SoulNutri AI - Índice Visual
Índice de embeddings para busca por similaridade (Top-K)
Meta: resposta em 100ms
"""

import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)

from .embedder import image_embedding_from_path, image_embedding_from_bytes


class DishIndex:
    """
    Índice visual de pratos usando embeddings.
    Usa busca por similaridade de cosseno para identificar pratos.
    """
    
    def __init__(self, data_dir: str = "/app/datasets/organized", index_file: str = "/app/datasets/dish_index.json"):
        self.data_dir = data_dir
        self.index_file = index_file
        
        # Estrutura do índice
        self.dishes: List[str] = []  # Lista de nomes de pratos
        self.embeddings: Optional[np.ndarray] = None  # Matriz de embeddings
        self.dish_to_idx: Dict[str, List[int]] = {}  # Mapa prato -> índices
        self.metadata: Dict[str, dict] = {}  # Metadados por prato
        
        # Tenta carregar índice existente
        self._load_index()
    
    def _load_index(self) -> bool:
        """Carrega índice do disco se existir"""
        if not os.path.exists(self.index_file):
            print(f"[index] Índice não encontrado: {self.index_file}")
            return False
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.dishes = data.get('dishes', [])
            self.dish_to_idx = data.get('dish_to_idx', {})
            self.metadata = data.get('metadata', {})
            
            # Carrega embeddings
            emb_file = self.index_file.replace('.json', '_embeddings.npy')
            if os.path.exists(emb_file):
                self.embeddings = np.load(emb_file)
                print(f"[index] Índice carregado: {len(self.dishes)} itens, {len(self.dish_to_idx)} pratos")
                return True
            
        except Exception as e:
            print(f"[index] Erro ao carregar índice: {e}")
        
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
            emb_file = self.index_file.replace('.json', '_embeddings.npy')
            if self.embeddings is not None:
                np.save(emb_file, self.embeddings)
            
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
        query_embedding = image_embedding_from_bytes(image_bytes)
        
        # Verificar se embedding foi gerado com sucesso
        if query_embedding is None:
            return [{'error': 'Falha ao gerar embedding da imagem. Tente novamente.'}]
        
        # Calcular similaridade de cosseno
        # Como os embeddings já estão normalizados, o dot product = cosine similarity
        similarities = np.dot(self.embeddings, query_embedding)
        
        # Pegar top-k índices
        top_indices = np.argsort(similarities)[::-1][:top_k * 3]  # Pega mais para agregar
        
        # Agregar por prato (pegar melhor score de cada prato)
        dish_scores: Dict[str, float] = {}
        for idx in top_indices:
            if idx >= len(self.dishes):
                continue  # Safety: skip indices beyond dishes list
            dish = self.dishes[idx]
            score = float(similarities[idx])
            if dish not in dish_scores or score > dish_scores[dish]:
                dish_scores[dish] = score
        
        # Ordenar por score
        sorted_dishes = sorted(dish_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # v1.2 restaurada: usar raw score direto, sem calibração
        results = []
        for dish_name, raw_score in sorted_dishes:
            confidence_level = self._get_confidence_level(raw_score)
            logger.info(f"[CLIP] {dish_name} - Raw: {raw_score:.3f} - {confidence_level}")
            results.append({
                'dish': dish_name,
                'score': round(raw_score, 4),
                'raw_score': round(raw_score, 4),
                'confidence': confidence_level,
                'image_count': self.metadata.get(dish_name, {}).get('image_count', 0)
            })
        
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
        """Converte score em nível de confiança"""
        if score >= 0.85:
            return "alta"
        elif score >= 0.50:
            return "média"
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
            'total_embeddings': len(self.dishes),
            'embedding_dim': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'index_file': self.index_file
        }


# Instância global do índice
_INDEX: Optional[DishIndex] = None

def get_index() -> DishIndex:
    """Retorna a instância global do índice"""
    global _INDEX
    if _INDEX is None:
        _INDEX = DishIndex()
    return _INDEX
