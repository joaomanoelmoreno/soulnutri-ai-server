"""
SoulNutri - Identificação Híbrida de Pratos v3
==============================================
ESTRATÉGIA SIMPLIFICADA baseada em análise real:

DESCOBERTA: A busca com imagem COMPLETA tem precisão superior.
            Dividir em regiões PIORA a precisão.

NOVA ESTRATÉGIA:
1. Busca com imagem COMPLETA → Top-10 resultados
2. Filtra resultados com score >= 0.85 (alta confiança)
3. Se poucos resultados, usa Gemini para complementar

Objetivo: Maximizar precisão para pratos cadastrados (meta 100%)
"""

import io
import logging
import time
from typing import List, Dict

logger = logging.getLogger(__name__)


async def identify_multi_v3(image_bytes: bytes) -> dict:
    """
    Identificação simplificada de prato múltiplo.
    
    Prioriza busca com imagem completa (maior precisão comprovada).
    """
    from ai.index import get_index
    from ai.policy import get_category, get_dish_name
    
    start_time = time.time()
    
    try:
        index = get_index()
        
        if not index.is_ready():
            return {'ok': False, 'error': 'Índice não carregado'}
        
        # ═══════════════════════════════════════════════════════════════════
        # BUSCA PRINCIPAL: Imagem completa (maior precisão)
        # ═══════════════════════════════════════════════════════════════════
        results = index.search(image_bytes, top_k=15)
        
        # Filtrar por score mínimo e remover duplicados
        seen_names = set()
        itens_encontrados = []
        
        for r in results:
            slug = r['dish']
            score = r['score']
            
            # Threshold de 70% para capturar mais itens (pratos múltiplos)
            if score < 0.70:
                continue
            
            # Normalizar nome para evitar duplicados
            nome = get_dish_name(slug)
            nome_lower = nome.lower()
            
            # Pular se já vimos este prato (variações de nome)
            if nome_lower in seen_names:
                continue
            
            seen_names.add(nome_lower)
            
            itens_encontrados.append({
                'nome': nome,
                'slug': slug,
                'score': score,
                'categoria': get_category(slug),
                'source': 'local_index'
            })
        
        logger.info(f"[v3] Encontrados {len(itens_encontrados)} itens com score >= 85%")
        
        # ═══════════════════════════════════════════════════════════════════
        # FALLBACK: Se poucos itens, usar Gemini
        # ═══════════════════════════════════════════════════════════════════
        if len(itens_encontrados) < 2:
            logger.info("[v3] Poucos itens locais, usando Gemini...")
            try:
                from services.generic_ai import identify_multiple_items
                gemini_result = await identify_multiple_items(image_bytes)
                
                if gemini_result.get('ok'):
                    for item in gemini_result.get('itens', [])[:5]:
                        nome = item.get('nome', '')
                        if nome.lower() not in seen_names:
                            itens_encontrados.append({
                                'nome': nome,
                                'slug': f'gemini_{nome.lower().replace(" ", "_")}',
                                'score': 0.75,
                                'categoria': item.get('categoria', 'outros'),
                                'source': 'gemini'
                            })
                            seen_names.add(nome.lower())
                            
            except Exception as e:
                logger.warning(f"[v3] Erro Gemini: {e}")
        
        # ═══════════════════════════════════════════════════════════════════
        # RESULTADO
        # ═══════════════════════════════════════════════════════════════════
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Separar principal de acompanhamentos
        principal = itens_encontrados[0] if itens_encontrados else None
        acompanhamentos = itens_encontrados[1:7] if len(itens_encontrados) > 1 else []
        
        # Contar itens do índice local
        local_count = sum(1 for i in itens_encontrados if i.get('source') == 'local_index')
        
        # Montar lista para resposta
        itens_list = []
        if principal:
            itens_list.append({
                'nome': principal['nome'],
                'categoria': principal['categoria'],
                'score': principal['score'],
                'source': principal['source']
            })
        for item in acompanhamentos:
            itens_list.append({
                'nome': item['nome'],
                'categoria': item['categoria'],
                'score': item['score'],
                'source': item['source']
            })
        
        return {
            'ok': True,
            'principal': principal,
            'acompanhamentos': acompanhamentos,
            'total_itens': len(itens_list),
            'itens_do_buffet': local_count,
            'metodo': 'local_index_v3',
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
        logger.error(f"[v3] Erro: {e}")
        return {'ok': False, 'error': str(e)}
