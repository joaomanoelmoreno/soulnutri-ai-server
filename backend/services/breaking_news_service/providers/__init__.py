# -*- coding: utf-8 -*-
"""Providers de breaking news contextual. Cada provider implementa fetch(...)."""

from . import dynamic

# Registry. Ordem em `api.py` controla qual e tentado primeiro.
PROVIDERS = {
    "dynamic": dynamic,
}

__all__ = ["PROVIDERS", "dynamic"]
