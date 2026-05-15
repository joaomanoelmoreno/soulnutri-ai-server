# -*- coding: utf-8 -*-
"""Providers de breaking news contextual. Cada provider implementa fetch(...)."""

from . import curated

# Registry. Ordem em `api.py` controla qual e tentado primeiro.
PROVIDERS = {
    "curated": curated,
}

__all__ = ["PROVIDERS", "curated"]
