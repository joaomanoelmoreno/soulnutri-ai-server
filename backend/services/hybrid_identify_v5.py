"""
SoulNutri - Identificação Híbrida de Pratos v5.3
================================================
LÓGICA MELHORADA:
- Prato único: score >= 99% E gap >= 15%
- Threshold fixo de 85% para acompanhamentos (não relativo ao principal)
- Máximo 6 itens para múltiplo
"""

import logging
import time
from typing import Set

logger = logging.getLogger(__name__)

PRATOS_GENERICOS = {'peixe', 'carne', 'frango', 'camarao', 'salada', 'arroz', 'legumes', 'bife', 'empanada'}

def is_generic_dish(slug: str) -> bool:
    slug_lower = slug.lower().replace('_', '')
    return slug_lower in PRATOS_GENERICOS or len(slug_lower) < 6

def are_similar_dishes(slug1: str, slug2: str) -> bool:
    s1 = slug1.lower().replace('_', '')
    s2 = slug2.lower().replace('_', '')
    if s1 in s2 or s2 in s1:
        return True
    prefix_len = min(len(s1), len(s2), 8)
    if prefix_len >= 6 and s1[:prefix_len] == s2[:prefix_len]:
        return True
    return False

async def identify_multi_v5(image_bytes: bytes) -> dict:
    from ai.index import get_index
    from ai.policy import get_category, get_dish_name
    
    start_time = time.time()
    
    try:
        index = get_index()
        if not index.is_ready():
            return {'ok': False, 'error': 'Índice não carregado'}
        
        results = index.search(image_bytes, top_k=30)
        if not results:
            return {'ok': False, 'error': 'Nenhum resultado encontrado'}
        
        principal_result = results[0]
        principal_score = principal_result['score']
        principal_slug = principal_result['dish']
        
        # Calcular gap para o segundo lugar
        gap = (principal_score - results[1]['score']) if len(results) > 1 else 1.0
        
        # Contar quantos itens têm score >= 85%
        high_score_count = sum(1 for r in results[:10] if r['score'] >= 0.85)
        
        # Prato único SOMENTE se:
        # - score >= 99% E gap >= 15% E menos de 3 itens com score alto
        is_prato_unico = (principal_score >= 0.99 and gap >= 0.15 and high_score_count < 3)
        
        logger.info(f"[v5.3] Principal: {principal_slug} = {principal_score:.2%} | Gap: {gap:.2%} | High scores: {high_score_count} | Único: {is_prato_unico}")
        
        # Threshold FIXO de 85% para todos
        threshold = 0.85
        
        # Limite de itens
        if is_prato_unico:
            max_itens = 2
        else:
            max_itens = 6
        
        logger.info(f"[v5.3] Threshold: {threshold:.2%} | Max: {max_itens}")
        
        itens_filtrados = []
        slugs_adicionados: Set[str] = set()
        
        for r in results:
            slug = r['dish']
            score = r['score']
            
            if score < threshold:
                continue
            
            # Pular similares
            if any(are_similar_dishes(slug, s) for s in slugs_adicionados):
                continue
            
            # Pular genéricos se existe específico
            if is_generic_dish(slug):
                if any(slug.lower() in o['dish'].lower() and o['dish'] != slug and o['score'] >= threshold for o in results):
                    continue
            
            itens_filtrados.append({
                'slug': slug,
                'score': score,
                'nome': get_dish_name(slug),
                'categoria': get_category(slug)
            })
            slugs_adicionados.add(slug)
            
            if len(itens_filtrados) >= max_itens:
                break
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        itens_list = [{'nome': i['nome'], 'slug': i['slug'], 'categoria': i['categoria'], 'score': i['score'], 'source': 'local_index'} for i in itens_filtrados]
        
        principal = itens_list[0] if itens_list else None
        acompanhamentos = itens_list[1:] if len(itens_list) > 1 else []
        
        return {
            'ok': True,
            'principal': principal,
            'acompanhamentos': acompanhamentos,
            'total_itens': len(itens_list),
            'is_prato_unico': is_prato_unico,
            'metodo': 'local_index_v5.3',
            'search_time_ms': round(elapsed_ms, 2),
            'itens': itens_list
        }
        
    except Exception as e:
        logger.error(f"[v5.3] Erro: {e}")
        return {'ok': False, 'error': str(e)}
