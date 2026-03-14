"""
SoulNutri - Sistema de Cache para Identificação de Pratos
Reduz tempo de resposta para pratos já identificados de ~4s para ~0ms
"""

import hashlib
import time
from typing import Optional
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

# Cache em memória com LRU (Least Recently Used)
class LRUCache:
    """Cache LRU simples em memória"""
    
    def __init__(self, max_size: int = 500):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[dict]:
        """Busca item no cache. Move para o final se encontrado (mais recente)."""
        if key in self.cache:
            # Move para o final (mais recente)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: dict, ttl_seconds: int = 3600):
        """Adiciona item ao cache com TTL opcional."""
        # Remove itens expirados e mais antigos se necessário
        current_time = time.time()
        
        # Limpar expirados
        expired_keys = [
            k for k, v in self.cache.items() 
            if v.get('_expires_at', float('inf')) < current_time
        ]
        for k in expired_keys:
            del self.cache[k]
        
        # Se ainda estiver cheio, remove o mais antigo
        while len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        # Adiciona com timestamp de expiração
        value['_expires_at'] = current_time + ttl_seconds
        value['_cached_at'] = current_time
        self.cache[key] = value
    
    def stats(self) -> dict:
        """Retorna estatísticas do cache."""
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{(self.hits / total * 100):.1f}%" if total > 0 else "N/A"
        }
    
    def clear(self):
        """Limpa o cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


# Instância global do cache
_dish_cache = LRUCache(max_size=500)


def get_image_hash(image_bytes: bytes) -> str:
    """Gera hash MD5 da imagem para identificação única."""
    return hashlib.md5(image_bytes).hexdigest()


def get_cached_result(image_bytes: bytes) -> Optional[dict]:
    """Busca resultado em cache baseado no hash da imagem."""
    image_hash = get_image_hash(image_bytes)
    result = _dish_cache.get(image_hash)
    
    if result:
        # Remove metadados internos do cache antes de retornar
        result_copy = {k: v for k, v in result.items() if not k.startswith('_')}
        result_copy['source'] = result.get('source', 'unknown') + '_cached'
        result_copy['from_cache'] = True
        logger.info(f"[CACHE] ✓ Hit! Prato: {result_copy.get('dish_display', 'N/A')}")
        return result_copy
    
    return None


def cache_result(image_bytes: bytes, result: dict, ttl_seconds: int = 3600):
    """Salva resultado no cache."""
    if not result.get('ok') or not result.get('identified'):
        return  # Não cachear erros ou não identificados
    
    image_hash = get_image_hash(image_bytes)
    _dish_cache.set(image_hash, result.copy(), ttl_seconds)
    logger.info(f"[CACHE] + Salvo: {result.get('dish_display', 'N/A')} (TTL: {ttl_seconds}s)")


def get_cache_stats() -> dict:
    """Retorna estatísticas do cache."""
    return _dish_cache.stats()


def clear_cache():
    """Limpa o cache."""
    _dish_cache.clear()
    logger.info("[CACHE] Cache limpo")
