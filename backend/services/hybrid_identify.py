"""
SoulNutri - Identificação Híbrida de Pratos Múltiplos
=====================================================
Estratégia: Combina zoom central + busca por similaridade nos pratos únicos do buffet.

Fluxo:
1. Zoom central (60%) → Identifica ITEM PRINCIPAL via OpenCLIP
2. Análise por regiões → Busca componentes no índice local
3. Fallback Gemini → Se necessário, usa IA para itens não reconhecidos
"""

import io
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

def apply_center_zoom(image_bytes: bytes, zoom_factor: float = 0.6) -> bytes:
    """
    Aplica zoom central na imagem para focar no item principal.
    
    Args:
        image_bytes: Imagem original em bytes
        zoom_factor: Fator de zoom (0.6 = 60% central)
    
    Returns:
        Imagem com zoom em bytes
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Calcular região central
        width, height = img.size
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)
        
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        
        # Crop e resize para manter dimensões
        cropped = img.crop((left, top, right, bottom))
        cropped = cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        # Converter de volta para bytes
        output = io.BytesIO()
        cropped.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        logger.info(f"[ZOOM] Aplicado zoom central {zoom_factor*100:.0f}%")
        return output.read()
        
    except Exception as e:
        logger.warning(f"[ZOOM] Erro ao aplicar zoom: {e}")
        return image_bytes


def extract_image_regions(image_bytes: bytes, grid_size: int = 3) -> list:
    """
    Divide a imagem em regiões para análise individual.
    
    Args:
        image_bytes: Imagem em bytes
        grid_size: Tamanho da grade (3 = 9 regiões)
    
    Returns:
        Lista de regiões como bytes
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        
        region_w = width // grid_size
        region_h = height // grid_size
        
        regions = []
        for row in range(grid_size):
            for col in range(grid_size):
                left = col * region_w
                top = row * region_h
                right = left + region_w
                bottom = top + region_h
                
                region = img.crop((left, top, right, bottom))
                # Resize para tamanho padrão
                region = region.resize((224, 224), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                region.save(output, format='JPEG', quality=80)
                output.seek(0)
                regions.append({
                    'bytes': output.read(),
                    'position': f"{row}_{col}",
                    'area': f"{'top' if row == 0 else 'mid' if row == 1 else 'bottom'}_{'left' if col == 0 else 'center' if col == 1 else 'right'}"
                })
        
        logger.info(f"[REGIONS] Extraídas {len(regions)} regiões da imagem")
        return regions
        
    except Exception as e:
        logger.warning(f"[REGIONS] Erro ao extrair regiões: {e}")
        return []


async def identify_multi_hybrid(image_bytes: bytes) -> dict:
    """
    Identificação híbrida de prato múltiplo.
    
    Estratégia:
    1. Zoom central → Busca item principal no índice local
    2. Regiões → Busca componentes por similaridade
    3. Gemini → Fallback para validação/itens não reconhecidos
    
    Returns:
        Dict com item principal e acompanhamentos reconhecidos do buffet
    """
    from ai.index import get_index
    from ai.policy import get_dish_name, get_category
    
    try:
        index = get_index()
        
        # ═══════════════════════════════════════════════════════════════════════
        # PASSO 1: Zoom Central - Identificar item principal
        # ═══════════════════════════════════════════════════════════════════════
        zoomed_image = apply_center_zoom(image_bytes, zoom_factor=0.5)
        
        # Buscar no índice local
        results_principal = index.search(zoomed_image, top_k=3)
        
        principal = None
        if results_principal and results_principal[0]['score'] > 0.65:
            principal = {
                'nome': get_dish_name(results_principal[0]['dish']),
                'slug': results_principal[0]['dish'],
                'score': results_principal[0]['score'],
                'categoria': get_category(results_principal[0]['dish']),
                'source': 'local_index_zoom'
            }
            logger.info(f"[HÍBRIDO] Principal via zoom: {principal['nome']} ({principal['score']:.0%})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PASSO 2: Busca por Regiões - Identificar acompanhamentos
        # ═══════════════════════════════════════════════════════════════════════
        regions = extract_image_regions(image_bytes, grid_size=3)
        
        acompanhamentos = []
        seen_slugs = set()
        if principal:
            seen_slugs.add(principal['slug'])
        
        for region in regions:
            # Pular região central (já analisada no zoom)
            if region['area'] == 'mid_center':
                continue
            
            results = index.search(region['bytes'], top_k=2)
            
            if results and results[0]['score'] > 0.60:
                slug = results[0]['dish']
                
                # Evitar duplicatas
                if slug not in seen_slugs:
                    seen_slugs.add(slug)
                    acompanhamentos.append({
                        'nome': get_dish_name(slug),
                        'slug': slug,
                        'score': results[0]['score'],
                        'categoria': get_category(slug),
                        'area': region['area'],
                        'source': 'local_index_region'
                    })
                    logger.info(f"[HÍBRIDO] Acompanhamento via região {region['area']}: {get_dish_name(slug)} ({results[0]['score']:.0%})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PASSO 3: Fallback Gemini - Se não encontrou principal ou poucos acomp.
        # ═══════════════════════════════════════════════════════════════════════
        gemini_items = []
        use_gemini = not principal or len(acompanhamentos) < 2
        
        if use_gemini:
            try:
                from services.generic_ai import identify_multiple_items
                gemini_result = await identify_multiple_items(image_bytes)
                
                if gemini_result.get('ok'):
                    gemini_items = gemini_result.get('itens', [])
                    
                    # Se não tem principal, usar do Gemini
                    if not principal and gemini_items:
                        # Priorizar proteínas
                        proteinas = [i for i in gemini_items if i.get('categoria') == 'proteína animal']
                        first_item = proteinas[0] if proteinas else gemini_items[0]
                        principal = {
                            'nome': first_item.get('nome', 'Prato'),
                            'slug': 'gemini_' + first_item.get('nome', '').lower().replace(' ', '_'),
                            'score': 0.7,
                            'categoria': first_item.get('categoria', 'outros'),
                            'source': 'gemini'
                        }
                        logger.info(f"[HÍBRIDO] Principal via Gemini: {principal['nome']}")
                    
                    # Adicionar acompanhamentos do Gemini que não estão na lista
                    for item in gemini_items:
                        nome_lower = item.get('nome', '').lower()
                        if principal and nome_lower == principal['nome'].lower():
                            continue
                        
                        # Verificar se já existe algo similar
                        already_found = any(
                            nome_lower in a['nome'].lower() or a['nome'].lower() in nome_lower
                            for a in acompanhamentos
                        )
                        
                        if not already_found:
                            acompanhamentos.append({
                                'nome': item.get('nome'),
                                'slug': 'gemini_' + item.get('nome', '').lower().replace(' ', '_'),
                                'score': 0.65,
                                'categoria': item.get('categoria', 'vegano'),
                                'source': 'gemini'
                            })
                            
            except Exception as e:
                logger.warning(f"[HÍBRIDO] Erro no fallback Gemini: {e}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # RESULTADO FINAL
        # ═══════════════════════════════════════════════════════════════════════
        
        # Ordenar acompanhamentos por score
        acompanhamentos.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Limitar a 6 acompanhamentos
        acompanhamentos = acompanhamentos[:6]
        
        # Contar itens do índice local vs Gemini
        local_count = sum(1 for a in acompanhamentos if a.get('source', '').startswith('local'))
        if principal and principal.get('source', '').startswith('local'):
            local_count += 1
        
        total_items = 1 + len(acompanhamentos) if principal else len(acompanhamentos)
        
        return {
            'ok': True,
            'principal': principal,
            'acompanhamentos': acompanhamentos,
            'total_itens': total_items,
            'itens_do_buffet': local_count,
            'metodo': 'hibrido_zoom_regioes',
            'resumo_nutricional': {
                'calorias_totais': f'~{total_items * 120} kcal',
                'proteinas_totais': f'~{total_items * 8}g',
                'carboidratos_totais': f'~{total_items * 15}g',
                'gorduras_totais': f'~{total_items * 5}g'
            }
        }
        
    except Exception as e:
        logger.error(f"[HÍBRIDO] Erro na identificação: {e}")
        return {
            'ok': False,
            'error': str(e)
        }
