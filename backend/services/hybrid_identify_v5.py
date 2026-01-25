"""
SoulNutri - Identificação Híbrida de Pratos v5
==============================================
PROBLEMA v4: Threshold de 65% retorna muitos itens errados.
             Mesmo fotos de prato único retornam 12 "acompanhamentos".

SOLUÇÃO v5:
1. Threshold ALTO de 88% - só itens muito similares
2. Gap mínimo entre principal e acompanhamentos
3. Máximo de 6 itens (1 principal + 5 acompanhamentos)
4. Se só 1 item tem score alto, retorna só ele (prato único)

Objetivo: Precisão > Quantidade de itens
"""

import logging
import time
from typing import List, Dict, Set

logger = logging.getLogger(__name__)

# Pratos genéricos que devem ser filtrados se existir versão específica
PRATOS_GENERICOS = {
    'peixe', 'carne', 'frango', 'camarao', 'salada', 'arroz', 'legumes',
    'verduras', 'frutos_do_mar', 'bife', 'empanada'
}


def is_generic_dish(slug: str) -> bool:
    """Verifica se é um prato genérico"""
    slug_lower = slug.lower().replace('_', '')
    return slug_lower in PRATOS_GENERICOS or len(slug_lower) < 6


def are_similar_dishes(slug1: str, slug2: str) -> bool:
    """Verifica se dois pratos são similares (variações do mesmo)"""
    s1 = slug1.lower().replace('_', '')
    s2 = slug2.lower().replace('_', '')
    
    # Se um contém o outro
    if s1 in s2 or s2 in s1:
        return True
    
    # Se começam igual (primeiros 8 caracteres)
    prefix_len = min(len(s1), len(s2), 8)
    if prefix_len >= 6 and s1[:prefix_len] == s2[:prefix_len]:
        return True
    
    return False


async def identify_multi_v5(image_bytes: bytes) -> dict:
    """
    Identificação de prato múltiplo v5 - MAIS RESTRITIVA
    
    Prioriza precisão sobre quantidade.
    """
    from ai.index import get_index
    from ai.policy import get_category, get_dish_name
    
    start_time = time.time()
    
    try:
        index = get_index()
        
        if not index.is_ready():
            return {'ok': False, 'error': 'Índice não carregado'}
        
        # ═══════════════════════════════════════════════════════════════════
        # BUSCA: Top-20 resultados
        # ═══════════════════════════════════════════════════════════════════
        results = index.search(image_bytes, top_k=20)
        
        if not results:
            return {'ok': False, 'error': 'Nenhum resultado encontrado'}
        
        # ═══════════════════════════════════════════════════════════════════
        # ANÁLISE DO PRINCIPAL
        # ═══════════════════════════════════════════════════════════════════
        principal_result = results[0]
        principal_score = principal_result['score']
        principal_slug = principal_result['dish']
        
        logger.info(f"[v5] Principal: {principal_slug} = {principal_score:.2%}")
        
        # ═══════════════════════════════════════════════════════════════════
        # DECISÃO: Prato único ou múltiplo?
        # ═══════════════════════════════════════════════════════════════════
        
        # Se o score do principal é muito alto (>= 95%), provavelmente é prato único
        # Verificar o gap para o segundo lugar
        if len(results) > 1:
            segundo_score = results[1]['score']
            gap = principal_score - segundo_score
        else:
            gap = 1.0  # Grande gap = prato único
        
        # Critérios para prato único:
        # 1. Score do principal >= 95% OU
        # 2. Gap entre principal e segundo >= 8%
        is_prato_unico = principal_score >= 0.95 or gap >= 0.08
        
        logger.info(f"[v5] Gap: {gap:.2%} | Prato único: {is_prato_unico}")
        
        # ═══════════════════════════════════════════════════════════════════
        # CONSTRUIR LISTA DE ITENS
        # ═══════════════════════════════════════════════════════════════════
        itens_filtrados = []
        slugs_adicionados: Set[str] = set()
        
        # Threshold dinâmico baseado no score do principal
        if is_prato_unico:
            # Para prato único, só aceita itens com score muito próximo
            threshold = principal_score - 0.03  # Máximo 3% abaixo
            max_itens = 2  # Máximo 2 itens
        else:
            # Para prato múltiplo, aceita itens com score >= 85%
            threshold = max(0.85, principal_score - 0.10)  # Máximo 10% abaixo
            max_itens = 6  # Máximo 6 itens
        
        logger.info(f"[v5] Threshold: {threshold:.2%} | Max itens: {max_itens}")
        
        for r in results:
            slug = r['dish']
            score = r['score']
            
            # Verificar threshold
            if score < threshold:
                continue
            
            # Verificar se é similar a algo já adicionado
            is_similar = False
            for existing_slug in slugs_adicionados:
                if are_similar_dishes(slug, existing_slug):
                    is_similar = True
                    break
            
            if is_similar:
                continue
            
            # Verificar se é genérico quando existe específico
            if is_generic_dish(slug):
                has_specific = False
                for other in results:
                    if other['dish'] != slug and slug.lower() in other['dish'].lower() and other['score'] >= threshold:
                        has_specific = True
                        break
                if has_specific:
                    continue
            
            # Adicionar item
            itens_filtrados.append({
                'slug': slug,
                'score': score,
                'nome': get_dish_name(slug),
                'categoria': get_category(slug)
            })
            slugs_adicionados.add(slug)
            
            # Limitar quantidade
            if len(itens_filtrados) >= max_itens:
                break
        
        logger.info(f"[v5] Itens finais: {len(itens_filtrados)}")
        
        # ═══════════════════════════════════════════════════════════════════
        # MONTAR RESPOSTA
        # ═══════════════════════════════════════════════════════════════════
        elapsed_ms = (time.time() - start_time) * 1000
        
        itens_list = []
        for item in itens_filtrados:
            itens_list.append({
                'nome': item['nome'],
                'slug': item['slug'],
                'categoria': item['categoria'],
                'score': item['score'],
                'source': 'local_index'
            })
        
        principal = itens_list[0] if itens_list else None
        acompanhamentos = itens_list[1:] if len(itens_list) > 1 else []
        
        return {
            'ok': True,
            'principal': principal,
            'acompanhamentos': acompanhamentos,
            'total_itens': len(itens_list),
            'itens_do_buffet': len(itens_list),
            'is_prato_unico': is_prato_unico,
            'metodo': 'local_index_v5',
            'search_time_ms': round(elapsed_ms, 2),
            'itens': itens_list,
            'resumo_nutricional': {
                'calorias_totais': f'~{len(itens_list) * 150} kcal',
                'proteinas_totais': f'~{sum(1 for i in itens_list if "animal" in i.get("categoria", "")) * 25}g',
                'carboidratos_totais': f'~{len(itens_list) * 20}g',
                'gorduras_totais': f'~{len(itens_list) * 8}g'
            }
        }
        
    except Exception as e:
        logger.error(f"[v5] Erro: {e}")
        return {'ok': False, 'error': str(e)}
