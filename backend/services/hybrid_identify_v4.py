"""
SoulNutri - Identificação Híbrida de Pratos v4
==============================================
ESTRATÉGIA MELHORADA baseada em análise real:

PROBLEMA: Pratos corretos aparecem com scores entre 70-85%, 
          mas o threshold de 85% os excluía.

SOLUÇÃO v4:
1. Buscar top-50 resultados (não apenas 15)
2. Threshold de 65% para capturar mais itens
3. Filtrar pratos genéricos quando existem específicos
4. Limitar a 10 itens mais relevantes
5. Priorizar diversidade (não repetir categorias similares)

Objetivo: Identificar corretamente pratos de buffet com múltiplos itens
"""

import io
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
    
    # Se começam igual (ex: panceta_pururuca vs panceta_pururca)
    prefix_len = min(len(s1), len(s2), 10)
    if s1[:prefix_len] == s2[:prefix_len]:
        return True
    
    return False


async def identify_multi_v4(image_bytes: bytes) -> dict:
    """
    Identificação de prato múltiplo v4 - MELHORADA
    
    Busca mais resultados e aplica filtragem inteligente.
    """
    from ai.index import get_index
    from ai.policy import get_category, get_dish_name
    
    start_time = time.time()
    
    try:
        index = get_index()
        
        if not index.is_ready():
            return {'ok': False, 'error': 'Índice não carregado'}
        
        # ═══════════════════════════════════════════════════════════════════
        # BUSCA AMPLA: Top-50 para capturar todos os itens possíveis
        # ═══════════════════════════════════════════════════════════════════
        results = index.search(image_bytes, top_k=50)
        
        # Fase 1: Coletar todos os candidatos com score >= 65%
        candidatos = []
        seen_slugs: Set[str] = set()
        
        for r in results:
            slug = r['dish']
            score = r['score']
            
            # Threshold de 65% para teste (amanhã)
            if score < 0.65:
                continue
            
            # Pular duplicados exatos
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            
            candidatos.append({
                'slug': slug,
                'score': score,
                'nome': get_dish_name(slug),
                'categoria': get_category(slug),
                'is_generic': is_generic_dish(slug)
            })
        
        logger.info(f"[v4] Candidatos com score >= 70%: {len(candidatos)}")
        
        # ═══════════════════════════════════════════════════════════════════
        # Fase 2: Filtrar pratos similares (manter o de maior score)
        # ═══════════════════════════════════════════════════════════════════
        itens_filtrados = []
        slugs_adicionados: Set[str] = set()
        
        for item in candidatos:
            slug = item['slug']
            
            # Verificar se já adicionamos algo similar
            is_similar_to_existing = False
            for existing_slug in slugs_adicionados:
                if are_similar_dishes(slug, existing_slug):
                    is_similar_to_existing = True
                    break
            
            if is_similar_to_existing:
                continue
            
            # Se é genérico, verificar se existe versão específica
            if item['is_generic']:
                has_specific = False
                for other in candidatos:
                    if other['slug'] != slug and slug.lower() in other['slug'].lower():
                        has_specific = True
                        break
                if has_specific:
                    continue
            
            itens_filtrados.append(item)
            slugs_adicionados.add(slug)
            
            # Limitar a 12 itens
            if len(itens_filtrados) >= 12:
                break
        
        logger.info(f"[v4] Itens após filtragem: {len(itens_filtrados)}")
        
        # ═══════════════════════════════════════════════════════════════════
        # Fase 3: Montar resposta
        # ═══════════════════════════════════════════════════════════════════
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Preparar lista final
        itens_list = []
        for item in itens_filtrados:
            itens_list.append({
                'nome': item['nome'],
                'slug': item['slug'],
                'categoria': item['categoria'],
                'score': item['score'],
                'source': 'local_index'
            })
        
        # Principal e acompanhamentos
        principal = itens_list[0] if itens_list else None
        acompanhamentos = itens_list[1:] if len(itens_list) > 1 else []
        
        return {
            'ok': True,
            'principal': principal,
            'acompanhamentos': acompanhamentos,
            'total_itens': len(itens_list),
            'itens_do_buffet': len(itens_list),
            'metodo': 'local_index_v4',
            'search_time_ms': round(elapsed_ms, 2),
            'itens': itens_list,
            'resumo_nutricional': {
                'calorias_totais': f'~{len(itens_list) * 120} kcal',
                'proteinas_totais': f'~{sum(1 for i in itens_list if "animal" in i.get("categoria", "")) * 20}g',
                'carboidratos_totais': f'~{len(itens_list) * 15}g',
                'gorduras_totais': f'~{len(itens_list) * 5}g'
            }
        }
        
    except Exception as e:
        logger.error(f"[v4] Erro: {e}")
        return {'ok': False, 'error': str(e)}
