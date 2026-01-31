"""
SoulNutri - Identificação Híbrida de Pratos Múltiplos v2
=========================================================
Estratégia MELHORADA:
1. Busca no índice local com a imagem COMPLETA (top-10)
2. Busca com ZOOM central (60%) para item principal
3. Busca por REGIÕES para identificar componentes específicos
4. Usa Gemini apenas para completar/validar

Objetivo: Maximizar uso do índice local treinado com as fotos do CibiSana
"""

import io
import logging
from PIL import Image
import numpy as np
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)

def apply_center_zoom(image_bytes: bytes, zoom_factor: float = 0.6) -> bytes:
    """Aplica zoom central na imagem"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        width, height = img.size
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)
        
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        
        cropped = img.crop((left, top, right, bottom))
        cropped = cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        cropped.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        return output.read()
        
    except Exception as e:
        logger.warning(f"[ZOOM] Erro: {e}")
        return image_bytes


def extract_quadrants(image_bytes: bytes) -> List[bytes]:
    """Divide a imagem em 9 regiões (grid 3x3) para busca localizada"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        
        # 9 regiões (3x3)
        regions = []
        for row in range(3):
            for col in range(3):
                left = col * width // 3
                top = row * height // 3
                right = left + width // 3
                bottom = top + height // 3
                
                region = img.crop((left, top, right, bottom))
                region = region.resize((224, 224), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                region.save(output, format='JPEG', quality=80)
                output.seek(0)
                regions.append(output.read())
        
        return regions
        
    except Exception as e:
        logger.warning(f"[QUADRANTS] Erro: {e}")
        return []


def normalize_dish_name(slug: str) -> str:
    """Converte slug para nome de exibição legível"""
    # Remove prefixos comuns
    name = slug.lower()
    
    # Substitui underscores por espaços
    name = name.replace('_', ' ')
    
    # Capitaliza cada palavra
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name


async def identify_multi_hybrid_v2(image_bytes: bytes) -> dict:
    """
    Identificação híbrida v2 - PRIORIZA ÍNDICE LOCAL
    
    Estratégia:
    1. Busca imagem completa no índice (top-10)
    2. Busca com zoom central (top-5)
    3. Busca em quadrantes (top-3 cada)
    4. Consolida resultados únicos
    5. Gemini apenas para validar/completar se necessário
    """
    from ai.index import get_index
    from ai.policy import get_category
    
    start_time = time.time()
    
    try:
        index = get_index()
        
        if not index.is_ready():
            return {'ok': False, 'error': 'Índice não carregado'}
        
        identified_items = {}  # slug -> {nome, score, categoria, source}
        
        # ═══════════════════════════════════════════════════════════════════
        # PASSO 1: Busca com imagem COMPLETA (captura itens grandes/centrais)
        # ═══════════════════════════════════════════════════════════════════
        logger.info("[HÍBRIDO v2] Buscando com imagem completa...")
        results_full = index.search(image_bytes, top_k=10)
        
        for result in results_full:
            slug = result['dish']
            score = result['score']
            
            # Threshold de 0.55 para imagem completa (mais permissivo)
            if score >= 0.55:
                if slug not in identified_items or score > identified_items[slug]['score']:
                    identified_items[slug] = {
                        'nome': normalize_dish_name(slug),
                        'slug': slug,
                        'score': score,
                        'categoria': get_category(slug),
                        'source': 'local_full'
                    }
        
        logger.info(f"[HÍBRIDO v2] Imagem completa: {len(identified_items)} itens")
        
        # ═══════════════════════════════════════════════════════════════════
        # PASSO 2: Busca com ZOOM central (item principal)
        # ═══════════════════════════════════════════════════════════════════
        logger.info("[HÍBRIDO v2] Buscando com zoom central...")
        zoomed = apply_center_zoom(image_bytes, 0.5)
        results_zoom = index.search(zoomed, top_k=5)
        
        for result in results_zoom:
            slug = result['dish']
            score = result['score']
            
            # Threshold de 0.60 para zoom
            if score >= 0.60:
                if slug not in identified_items or score > identified_items[slug]['score']:
                    identified_items[slug] = {
                        'nome': normalize_dish_name(slug),
                        'slug': slug,
                        'score': score,
                        'categoria': get_category(slug),
                        'source': 'local_zoom'
                    }
        
        logger.info(f"[HÍBRIDO v2] Após zoom: {len(identified_items)} itens")
        
        # ═══════════════════════════════════════════════════════════════════
        # PASSO 3: Busca por REGIÕES (itens nas bordas/cantos)
        # ═══════════════════════════════════════════════════════════════════
        logger.info("[HÍBRIDO v2] Buscando por regiões...")
        quadrants = extract_quadrants(image_bytes)
        
        for i, quad_bytes in enumerate(quadrants):
            results_quad = index.search(quad_bytes, top_k=3)
            
            for result in results_quad:
                slug = result['dish']
                score = result['score']
                
                # Threshold de 0.55 para regiões
                if score >= 0.55:
                    if slug not in identified_items or score > identified_items[slug]['score']:
                        identified_items[slug] = {
                            'nome': normalize_dish_name(slug),
                            'slug': slug,
                            'score': score,
                            'categoria': get_category(slug),
                            'source': f'local_region_{i}'
                        }
        
        logger.info(f"[HÍBRIDO v2] Após regiões: {len(identified_items)} itens")
        
        # ═══════════════════════════════════════════════════════════════════
        # PASSO 4: Ordenar por score e separar principal de acompanhamentos
        # ═══════════════════════════════════════════════════════════════════
        sorted_items = sorted(
            identified_items.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        principal = None
        acompanhamentos = []
        
        if sorted_items:
            # Principal é o de maior score
            principal = sorted_items[0]
            
            # Acompanhamentos são os demais
            for item in sorted_items[1:6]:  # Máximo 6 acompanhamentos
                acompanhamentos.append(item)
        
        # ═══════════════════════════════════════════════════════════════════
        # PASSO 5: Se poucos itens, usar Gemini para completar
        # ═══════════════════════════════════════════════════════════════════
        if len(sorted_items) < 3:
            logger.info("[HÍBRIDO v2] Poucos itens locais, usando Gemini...")
            try:
                from services.generic_ai import identify_multiple_items
                gemini_result = await identify_multiple_items(image_bytes)
                
                if gemini_result.get('ok'):
                    gemini_items = gemini_result.get('itens', [])
                    
                    for item in gemini_items[:5]:
                        nome = item.get('nome', '')
                        
                        # Não adicionar se já existe
                        slug = nome.lower().replace(' ', '_')
                        if slug in identified_items:
                            continue
                        
                        new_item = {
                            'nome': nome,
                            'slug': f'gemini_{slug}',
                            'score': 0.75,
                            'categoria': item.get('categoria', 'outros'),
                            'source': 'gemini'
                        }
                        
                        if not principal:
                            principal = new_item
                        else:
                            acompanhamentos.append(new_item)
                            
            except Exception as e:
                logger.warning(f"[HÍBRIDO v2] Erro Gemini: {e}")
        
        # ═══════════════════════════════════════════════════════════════════
        # RESULTADO FINAL
        # ═══════════════════════════════════════════════════════════════════
        elapsed_ms = (time.time() - start_time) * 1000
        
        total_items = (1 if principal else 0) + len(acompanhamentos)
        local_count = sum(1 for item in ([principal] if principal else []) + acompanhamentos 
                        if item and 'local' in item.get('source', ''))
        
        # Montar lista de itens para resposta
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
            'total_itens': total_items,
            'itens_do_buffet': local_count,
            'metodo': 'hibrido_local_v2',
            'search_time_ms': round(elapsed_ms, 2),
            'itens': itens_list,
            'resumo_nutricional': {
                'calorias_totais': f'~{total_items * 120} kcal',
                'proteinas_totais': f'~{sum(1 for i in itens_list if i.get("categoria") == "proteína animal") * 20 + (total_items - sum(1 for i in itens_list if i.get("categoria") == "proteína animal")) * 5}g',
                'carboidratos_totais': f'~{total_items * 15}g',
                'gorduras_totais': f'~{total_items * 5}g'
            }
        }
        
    except Exception as e:
        logger.error(f"[HÍBRIDO v2] Erro: {e}")
        return {'ok': False, 'error': str(e)}
