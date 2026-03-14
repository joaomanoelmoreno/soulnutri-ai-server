"""
Script para migrar dados dos pratos para MongoDB
e usar IA para revisar/enriquecer informações
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Adicionar o diretório do backend ao path
sys.path.insert(0, '/app/backend')

load_dotenv('/app/backend/.env')

# Importar dados atuais
from ai.policy import DISH_NAMES, DISH_CATEGORIES, DISH_INFO, DISH_NUTRITION, PRATOS_COM_GLUTEN, AVISO_CIBI_SANA

async def migrate_dishes():
    """Migra todos os pratos para MongoDB"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'soulnutri')
    
    print(f"Conectando ao MongoDB: {mongo_url}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Coleção de pratos
    dishes_collection = db['dishes']
    
    # Limpar coleção existente
    await dishes_collection.delete_many({})
    print("Coleção 'dishes' limpa")
    
    # Preparar documentos
    dishes_docs = []
    
    for slug, name in DISH_NAMES.items():
        # Pegar categoria
        category = DISH_CATEGORIES.get(slug, 'outros')
        
        # Pegar info detalhada
        info = DISH_INFO.get(slug, {})
        
        # Determinar tipo de nutrição
        if 'arroz' in slug:
            nutr_type = 'arroz'
        elif 'feijao' in slug or 'lentilha' in slug:
            nutr_type = 'feijao'
        elif 'peixe' in slug or 'atum' in slug or 'bacalhau' in slug:
            nutr_type = 'peixe'
        elif 'frango' in slug or 'sobrecoxa' in slug:
            nutr_type = 'frango'
        elif 'carne' in slug or 'maminha' in slug or 'costela' in slug or 'kibe' in slug:
            nutr_type = 'carne'
        elif 'massa' in slug or 'espaguete' in slug or 'lasanha' in slug or 'nhoque' in slug:
            nutr_type = 'massa'
        elif 'bolo' in slug or 'brownie' in slug or 'mousse' in slug or 'cocada' in slug or 'goiabada' in slug:
            nutr_type = 'sobremesa'
        elif 'batata' in slug:
            nutr_type = 'batata'
        else:
            nutr_type = 'vegetal'
        
        nutrition = DISH_NUTRITION.get(nutr_type, DISH_NUTRITION['default'])
        
        # Verificar se contém glúten
        contem_gluten = slug in PRATOS_COM_GLUTEN
        
        # Criar documento
        doc = {
            'slug': slug,
            'nome': name,
            'categoria': category,
            'descricao': info.get('descricao', f'{name} preparado artesanalmente no Cibi Sana'),
            'ingredientes': info.get('ingredientes', []),
            'tecnica': info.get('tecnica', ''),
            'beneficios': info.get('beneficios', []),
            'riscos': info.get('riscos', []),
            'contem_gluten': contem_gluten,
            'nutricao': {
                'calorias': nutrition['calorias'],
                'proteinas': nutrition['proteinas'],
                'carboidratos': nutrition['carboidratos'],
                'gorduras': nutrition['gorduras']
            },
            'aviso_cibi_sana': AVISO_CIBI_SANA,
            'ativo': True,
            'origem': 'cibi_sana',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        dishes_docs.append(doc)
    
    # Inserir em lote
    if dishes_docs:
        result = await dishes_collection.insert_many(dishes_docs)
        print(f"✅ {len(result.inserted_ids)} pratos inseridos no MongoDB")
    
    # Criar índices
    await dishes_collection.create_index('slug', unique=True)
    await dishes_collection.create_index('categoria')
    await dishes_collection.create_index('nome')
    print("✅ Índices criados")
    
    # Estatísticas
    stats = {
        'total': await dishes_collection.count_documents({}),
        'vegano': await dishes_collection.count_documents({'categoria': 'vegano'}),
        'vegetariano': await dishes_collection.count_documents({'categoria': 'vegetariano'}),
        'proteina_animal': await dishes_collection.count_documents({'categoria': 'proteína animal'}),
        'com_gluten': await dishes_collection.count_documents({'contem_gluten': True})
    }
    
    print(f"\n📊 Estatísticas:")
    print(f"   Total de pratos: {stats['total']}")
    print(f"   Veganos: {stats['vegano']}")
    print(f"   Vegetarianos: {stats['vegetariano']}")
    print(f"   Proteína Animal: {stats['proteina_animal']}")
    print(f"   Com glúten: {stats['com_gluten']}")
    
    # Verificar pratos sem informações detalhadas
    pratos_sem_info = await dishes_collection.count_documents({'ingredientes': []})
    print(f"\n⚠️  Pratos sem ingredientes detalhados: {pratos_sem_info}")
    
    client.close()
    return stats

if __name__ == '__main__':
    asyncio.run(migrate_dishes())
