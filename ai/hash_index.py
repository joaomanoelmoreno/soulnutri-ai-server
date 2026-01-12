"""
Compat layer: o código legado importava `HashIndex` de `ai.hash_index`.
O projeto atual usa `ai.emb_index`. Este arquivo mantém compatibilidade
para evitar falhas de import em produção (Render).
"""

from __future__ import annotations

# Tentamos primeiro encontrar HashIndex diretamente no emb_index (caso exista).
try:
    from .emb_index import HashIndex as _HashIndex  # type: ignore
except Exception:
    _HashIndex = None  # type: ignore

# Se não existir, tentamos aliasar para a classe mais provável.
if _HashIndex is None:
    try:
        from .emb_index import EmbIndex as _HashIndex  # type: ignore
    except Exception:
        # Último fallback: tenta encontrar qualquer classe com nome sugestivo.
        # Isso evita deploy quebrado se houver pequenas variações.
        import inspect
        from . import emb_index as _mod  # type: ignore

        _candidates = []
        for _name, _obj in vars(_mod).items():
            if inspect.isclass(_obj) and _obj.__module__ == _mod.__name__:
                if _name.lower() in ("embindex", "embeddingindex", "vectorindex", "index"):
                    _candidates.append(_obj)

        if not _candidates:
            raise ImportError(
                "Não foi possível resolver HashIndex a partir de ai.emb_index. "
                "Verifique o nome da classe principal em ai/emb_index.py."
            )

        _HashIndex = _candidates[0]  # type: ignore

# Nome público esperado pelo main.py
HashIndex = _HashIndex  # type: ignore

__all__ = ["HashIndex"]
