"""
SoulNutri - Serviço de Pratos (MongoDB)
Gerencia dados dos pratos a partir do banco de dados
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Cliente MongoDB global
_client = None
_db = None

def get_db():
    """Retorna instância do banco de dados"""
    global _client, _db
    
    if _db is None:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'soulnutri')
        _client = AsyncIOMotorClient(mongo_url)
        _db = _client[db_name]
    
    return _db

async def get_dish_by_slug(slug: str) -> Optional[Dict]:
    """Busca prato pelo slug"""
    db = get_db()
    dish = await db.dishes.find_one({'slug': slug}, {'_id': 0})
    return dish

async def get_all_dishes() -> List[Dict]:
    """Retorna todos os pratos"""
    db = get_db()
    cursor = db.dishes.find({'ativo': True}, {'_id': 0})
    return await cursor.to_list(length=500)

async def get_dishes_by_category(category: str) -> List[Dict]:
    """Retorna pratos de uma categoria"""
    db = get_db()
    cursor = db.dishes.find({'categoria': category, 'ativo': True}, {'_id': 0})
    return await cursor.to_list(length=200)

async def search_dishes(query: str) -> List[Dict]:
    """Busca pratos por nome ou ingrediente"""
    db = get_db()
    cursor = db.dishes.find({
        '$or': [
            {'nome': {'$regex': query, '$options': 'i'}},
            {'ingredientes': {'$regex': query, '$options': 'i'}}
        ],
        'ativo': True
    }, {'_id': 0})
    return await cursor.to_list(length=50)

async def update_dish(slug: str, data: Dict) -> bool:
    """Atualiza informações de um prato"""
    db = get_db()
    from datetime import datetime
    data['updated_at'] = datetime.utcnow()
    result = await db.dishes.update_one({'slug': slug}, {'$set': data})
    return result.modified_count > 0

async def add_dish(dish_data: Dict) -> bool:
    """Adiciona novo prato"""
    db = get_db()
    from datetime import datetime
    dish_data['created_at'] = datetime.utcnow()
    dish_data['updated_at'] = datetime.utcnow()
    dish_data['ativo'] = True
    result = await db.dishes.insert_one(dish_data)
    return result.inserted_id is not None

# =============================================
# FUNÇÕES DE COMPATIBILIDADE COM policy.py
# =============================================

# Cache em memória para performance
_dish_cache = {}

async def load_dish_cache():
    """Carrega cache de pratos do MongoDB"""
    global _dish_cache
    dishes = await get_all_dishes()
    _dish_cache = {d['slug']: d for d in dishes}
    return len(_dish_cache)

def get_dish_name(slug: str) -> str:
    """Retorna nome do prato"""
    if slug in _dish_cache:
        return _dish_cache[slug].get('nome', slug.replace('_', ' ').title())
    return slug.replace('_', ' ').title()

def get_category(slug: str) -> str:
    """Retorna categoria do prato"""
    if slug in _dish_cache:
        return _dish_cache[slug].get('categoria', 'outros')
    return 'outros'

def get_category_emoji(category: str) -> str:
    """Retorna emoji da categoria"""
    emojis = {
        'vegano': '🌱',
        'vegetariano': '🥬',
        'proteína animal': '🍖',
        'outros': '🍽️'
    }
    return emojis.get(category, '🍽️')

def get_dish_info(slug: str) -> Dict:
    """Retorna todas as informações do prato"""
    if slug in _dish_cache:
        dish = _dish_cache[slug]
        return {
            'descricao': dish.get('descricao', ''),
            'ingredientes': dish.get('ingredientes', []),
            'tecnica': dish.get('tecnica', ''),
            'beneficios': dish.get('beneficios', []),
            'riscos': dish.get('riscos', [])
        }
    return {}

def get_nutrition(slug: str) -> Dict:
    """Retorna informações nutricionais"""
    if slug in _dish_cache:
        return _dish_cache[slug].get('nutricao', {
            'calorias': '~150 kcal',
            'proteinas': '~5g',
            'carboidratos': '~20g',
            'gorduras': '~5g'
        })
    return {
        'calorias': '~150 kcal',
        'proteinas': '~5g',
        'carboidratos': '~20g',
        'gorduras': '~5g'
    }

def get_aviso_cibi_sana() -> str:
    """Retorna aviso padrão Cibi Sana"""
    return "Sem aditivos químicos e/ou alimentos industrializados/processados"
