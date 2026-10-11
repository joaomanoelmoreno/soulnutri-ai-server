"""
SoulNutri - Sistema de Cache para Identificação de Pratos
Reduz tempo de resposta para pratos já identificados de ~4s para ~0ms
"""

import copy
import hashlib
import json
import time
import unicodedata
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


def _normalize_confidence(value) -> str:
    """Normaliza confidence para comparacao (case + acento insensitive).

    'Média' / 'média' / 'MEDIA' / ' media ' -> 'media'
    Usa unicodedata.NFKD (stdlib) para remover diacriticos de forma robusta,
    sem dependencias externas.
    """
    text = str(value or '').strip().lower()
    text = unicodedata.normalize('NFKD', text)
    return ''.join(ch for ch in text if not unicodedata.combining(ch))

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

# Namespace separado para decisões visuais do índice v2. O cache legado acima
# permanece com a chave e o payload históricos.
_visual_decision_cache = LRUCache(max_size=500)


@dataclass(frozen=True)
class VisualCacheContext:
    """Versions that make one visual decision safe to reuse."""

    schema_version: int
    index_version: str
    model_version: str
    preprocessing_version: str
    taxonomy_version: str


class VisualCacheValidationError(ValueError):
    """Raised when a v2 cache input is incomplete or contextual."""


def _validate_visual_cache_context(context: VisualCacheContext) -> None:
    if not isinstance(context, VisualCacheContext):
        raise VisualCacheValidationError("context must be VisualCacheContext")
    if context.schema_version != 2:
        raise VisualCacheValidationError("visual cache requires schema version 2")
    for field in (
        "index_version",
        "model_version",
        "preprocessing_version",
        "taxonomy_version",
    ):
        value = getattr(context, field)
        if not isinstance(value, str) or not value or value != value.strip():
            raise VisualCacheValidationError(f"{field} must be non-empty text")


def get_visual_cache_key(
    image_bytes: bytes,
    restaurant: str,
    context: VisualCacheContext,
) -> str:
    """Build a versioned v2 key without variant/contextual evidence."""
    if not isinstance(image_bytes, bytes) or not image_bytes:
        raise VisualCacheValidationError("image_bytes must be non-empty bytes")
    _validate_visual_cache_context(context)
    stable_context = {
        "index_version": context.index_version,
        "model_version": context.model_version,
        "preprocessing_version": context.preprocessing_version,
        "restaurant": (restaurant or "").strip().lower(),
        "schema_version": context.schema_version,
        "taxonomy_version": context.taxonomy_version,
    }
    context_digest = hashlib.sha256(
        json.dumps(
            stable_context,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    image_digest = hashlib.sha256(image_bytes).hexdigest()
    return f"visual:v2:{image_digest}:{context_digest}"


def _visual_cache_ttl(result: Mapping[str, Any], ttl_seconds: int) -> Optional[int]:
    if not result.get("ok") or not result.get("identified"):
        return None
    confidence = _normalize_confidence(result.get("confidence"))
    if confidence == "baixa":
        return None
    if confidence == "media":
        return 300
    if confidence == "alta":
        return min(int(ttl_seconds) if ttl_seconds else 3600, 3600)
    return int(ttl_seconds) if ttl_seconds else 3600


def _visual_cache_payload(
    result: Mapping[str, Any], context: VisualCacheContext
) -> dict:
    if not isinstance(result, Mapping):
        raise VisualCacheValidationError("visual result must be a mapping")
    if result.get("recognition_schema_version") != 2:
        raise VisualCacheValidationError("visual result must use schema version 2")
    visual_class = result.get("visual_class")
    if not isinstance(visual_class, Mapping):
        raise VisualCacheValidationError("visual_class must be a mapping")
    class_id = visual_class.get("id")
    class_name = visual_class.get("name")
    if not isinstance(class_id, str) or not class_id:
        raise VisualCacheValidationError("visual_class.id must be non-empty text")
    if not isinstance(class_name, str) or not class_name:
        raise VisualCacheValidationError("visual_class.name must be non-empty text")

    payload = {
        "ok": bool(result.get("ok")),
        "identified": bool(result.get("identified")),
        "recognition_schema_version": 2,
        "visual_class": {"id": class_id, "name": class_name},
        "score": copy.deepcopy(result.get("score")),
        "confidence": copy.deepcopy(result.get("confidence")),
        "source": result.get("source", "local_index"),
        "alternatives": copy.deepcopy(result.get("alternatives", [])),
        "index_version": context.index_version,
        "model_version": context.model_version,
        "preprocessing_version": context.preprocessing_version,
        "taxonomy_version": context.taxonomy_version,
    }
    for field in ("raw_score", "gap", "consistency", "image_count"):
        if field in result:
            payload[field] = copy.deepcopy(result[field])
    return payload


def cache_visual_decision(
    image_bytes: bytes,
    result: Mapping[str, Any],
    context: VisualCacheContext,
    *,
    restaurant: str = "",
    ttl_seconds: int = 3600,
) -> bool:
    """Cache only stable visual identity; contextual variant fields are dropped."""
    _validate_visual_cache_context(context)
    if not isinstance(result, Mapping):
        raise VisualCacheValidationError("visual result must be a mapping")
    effective_ttl = _visual_cache_ttl(result, ttl_seconds)
    if effective_ttl is None:
        return False
    payload = _visual_cache_payload(result, context)
    key = get_visual_cache_key(image_bytes, restaurant, context)
    _visual_decision_cache.set(key, payload, effective_ttl)
    logger.info(
        "[VISUAL_CACHE] stored class=%r confidence=%s TTL=%ss",
        payload["visual_class"]["name"],
        _normalize_confidence(payload.get("confidence")) or "unknown",
        effective_ttl,
    )
    return True


def get_cached_visual_decision(
    image_bytes: bytes,
    context: VisualCacheContext,
    *,
    restaurant: str = "",
) -> Optional[dict]:
    """Return a defensive copy of the stable v2 visual decision."""
    key = get_visual_cache_key(image_bytes, restaurant, context)
    result = _visual_decision_cache.get(key)
    if result is None:
        return None
    response = {
        field: copy.deepcopy(value)
        for field, value in result.items()
        if not field.startswith("_")
    }
    response["from_visual_cache"] = True
    return response


def get_visual_cache_stats() -> dict:
    """Return v2 cache statistics without changing the legacy stats contract."""
    return _visual_decision_cache.stats()


def clear_visual_cache() -> None:
    """Clear only the isolated v2 visual namespace."""
    _visual_decision_cache.clear()


def get_image_hash(image_bytes: bytes, restaurant: str = '') -> str:
    """Gera hash MD5 da imagem + restaurant para identificação única.
    
    A chave inclui o restaurant normalizado para evitar que resultados
    Gemini (external) sejam reutilizados dentro do Cibi Sana (ONNX/CLIP).
    """
    restaurant_key = (restaurant or '').strip().lower()
    return hashlib.md5(image_bytes + restaurant_key.encode()).hexdigest()


def get_cached_result(image_bytes: bytes, restaurant: str = '') -> Optional[dict]:
    """Busca resultado em cache baseado no hash da imagem + restaurant."""
    image_hash = get_image_hash(image_bytes, restaurant)
    result = _dish_cache.get(image_hash)
    
    if result:
        # Remove metadados internos do cache antes de retornar
        result_copy = {k: v for k, v in result.items() if not k.startswith('_')}
        result_copy['source'] = result.get('source', 'unknown') + '_cached'
        result_copy['from_cache'] = True
        logger.info(f"[CACHE] ✓ Hit! Prato: {result_copy.get('dish_display', 'N/A')} (restaurant={restaurant or 'external'})")
        return result_copy
    
    return None


def cache_result(image_bytes: bytes, result: dict, restaurant: str = '', ttl_seconds: int = 3600):
    """Salva resultado no cache keyed por imagem + restaurant.

    Politica de TTL por confianca (P1 — protege contra "fotos teimosas"):
        - confidence == 'alta'           -> 3600s (1h)
        - confidence == 'media'/'média'  -> 300s  (5min) — pode ser falso positivo
        - confidence == 'baixa'          -> NAO cacheia
        - identified == False            -> NAO cacheia (compat anterior)

    O parametro `ttl_seconds` recebido e' usado APENAS como teto para 'alta'
    quando explicitamente menor (back-compat). Para 'media' a politica e' fixa
    em 300s para evitar contaminacao de 1h por identificacao incerta.

    O comportamento de outros caches (enrich/premium/dish-name) NAO e' afetado:
    este servico e' usado exclusivamente pelo cache de identificacao por imagem.
    """
    if not result.get('ok') or not result.get('identified'):
        return  # Nao cachear erros ou nao identificados

    # Normaliza confidence (case + acento insensitive) via helper privado.
    conf = _normalize_confidence(result.get('confidence'))

    if conf == 'baixa':
        logger.info(f"[CACHE] ignorado: conf=baixa dish={result.get('dish_display', 'N/A')!r}")
        return

    if conf == 'media':
        effective_ttl = 300
    elif conf == 'alta':
        # Respeita teto vindo do chamador, se menor que 3600.
        effective_ttl = min(int(ttl_seconds) if ttl_seconds else 3600, 3600)
    else:
        # Confidence ausente/desconhecido: usa exatamente o que o chamador pediu.
        effective_ttl = int(ttl_seconds) if ttl_seconds else 3600

    image_hash = get_image_hash(image_bytes, restaurant)
    _dish_cache.set(image_hash, result.copy(), effective_ttl)
    logger.info(
        f"[CACHE] + Salvo: {result.get('dish_display', 'N/A')} "
        f"conf={conf or 'unknown'} TTL={effective_ttl}s "
        f"(restaurant={restaurant or 'external'})"
    )


def get_cache_stats() -> dict:
    """Retorna estatísticas do cache."""
    return _dish_cache.stats()


def clear_cache():
    """Limpa o cache."""
    _dish_cache.clear()
    _visual_decision_cache.clear()
    logger.info("[CACHE] Cache limpo")
