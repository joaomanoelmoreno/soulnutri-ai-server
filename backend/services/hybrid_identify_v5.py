"""
SoulNutri - Identificação Híbrida de Pratos v5
==============================================
PROBLEMA v4: Threshold de 65% retorna muitos itens errados.

SOLUÇÃO v5:
1. Threshold ALTO de 88% - só itens muito similares
2. Gap mínimo entre principal e acompanhamentos
3. Máximo de 6 itens (1 principal + 5 acompanhamentos)
4. Se só 1 item tem score alto, retorna só ele (prato único)
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
        
        results = index.search(image_bytes, top_k=20)
        if not results:
            return {'ok': False, 'error': 'Nenhum resultado encontrado'}
        
        principal_result = results[0]
        principal_score = principal_result['score']
        principal_slug = principal_result['dish']
        
        # Calcular gap para o segundo lugar
        gap = (principal_score - results[1]['score']) if len(results) > 1 else 1.0
        
        # Prato único se: score >= 95% OU gap >= 8%
        is_prato_unico = principal_score >= 0.95 or gap >= 0.08
        
        logger.info(f"[v5] Principal: {principal_slug} = {principal_score:.2%} | Gap: {gap:.2%} | Único: {is_prato_unico}")
        
        # Threshold e limite baseado no tipo
        if is_prato_unico:
            threshold = principal_score - 0.03
            max_itens = 2
        else:
            threshold = max(0.88, principal_score - 0.05)
            max_itens = 4
        
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
            'metodo': 'local_index_v5',
            'search_time_ms': round(elapsed_ms, 2),
            'itens': itens_list
        }
        
    except Exception as e:
        logger.error(f"[v5] Erro: {e}")
        return {'ok': False, 'error': str(e)}
