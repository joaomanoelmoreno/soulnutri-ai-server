# -*- coding: utf-8 -*-
"""
Modulo neutro de acesso Mongo para o subsistema breaking_news_service.

Sem logica de negocio. Sem startup hook. Sem side effects.
Lazy singleton simples. Reuso por novos providers do subsistema.

NOTA: providers/curated.py mantem cliente proprio (legado, intocado).
Este modulo serve providers NOVOS (a partir do PR #4a).
"""

import os
from pathlib import Path

from dotenv import load_dotenv
import pymongo

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

_client = None
_db = None


def get_db():
    """Retorna instancia singleton do banco Mongo (sync)."""
    global _client, _db
    if _db is None:
        _client = pymongo.MongoClient(os.environ['MONGO_URL'])
        _db = _client[os.environ['DB_NAME']]
    return _db
