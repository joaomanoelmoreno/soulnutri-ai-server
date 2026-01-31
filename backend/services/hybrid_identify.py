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
    
    Estratégia SIMPLIFICADA:
    1. Zoom central → Busca item principal no índice local
    2. Gemini → Identifica todos os componentes com precisão
    
    Returns:
        Dict com item principal e acompanhamentos
    """
    from ai.index import get_index
    from ai.policy import get_dish_name, get_category
    
    try:
        index = get_index()
        
        # ═══════════════════════════════════════════════════════════════════════
        # PASSO 1: Zoom Central - Tentar identificar item principal localmente
        # ═══════════════════════════════════════════════════════════════════════
        zoomed_image = apply_center_zoom(image_bytes, zoom_factor=0.5)
        
        # Buscar no índice local
        results_principal = index.search(zoomed_image, top_k=3)
        
        principal = None
        principal_from_local = False
        
        # Apenas usar índice local se confiança for MUITO alta (>75%)
        if results_principal and results_principal[0]['score'] > 0.75:
            principal = {
                'nome': get_dish_name(results_principal[0]['dish']),
                'slug': results_principal[0]['dish'],
                'score': results_principal[0]['score'],
                'categoria': get_category(results_principal[0]['dish']),
                'source': 'local_index_zoom'
            }
            principal_from_local = True
            logger.info(f"[HÍBRIDO] Principal via zoom local: {principal['nome']} ({principal['score']:.0%})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # PASSO 2: Usar Gemini para identificar TODOS os componentes
        # ═══════════════════════════════════════════════════════════════════════
        acompanhamentos = []
        gemini_principal = None
        
        try:
            from services.generic_ai import identify_multiple_items
            gemini_result = await identify_multiple_items(image_bytes)
            
            if gemini_result.get('ok'):
                gemini_items = gemini_result.get('itens', [])
                
                # Se não encontrou principal local, usar do Gemini
                if not principal and gemini_items:
                    # Priorizar proteínas
                    proteinas = [i for i in gemini_items if i.get('categoria') == 'proteína animal']
                    first_item = proteinas[0] if proteinas else gemini_items[0]
                    principal = {
                        'nome': first_item.get('nome', 'Prato'),
                        'slug': 'gemini_' + first_item.get('nome', '').lower().replace(' ', '_'),
                        'score': 0.85,
                        'categoria': first_item.get('categoria', 'outros'),
                        'source': 'gemini'
                    }
                    gemini_principal = first_item
                    logger.info(f"[HÍBRIDO] Principal via Gemini: {principal['nome']}")
                
                # Adicionar acompanhamentos do Gemini
                for item in gemini_items:
                    nome = item.get('nome', '')
                    
                    # Pular se for o principal (do local ou gemini)
                    if principal and nome.lower() == principal['nome'].lower():
                        continue
                    if gemini_principal and nome.lower() == gemini_principal.get('nome', '').lower():
                        continue
                    
                    acompanhamentos.append({
                        'nome': nome,
                        'slug': 'gemini_' + nome.lower().replace(' ', '_'),
                        'score': 0.80,
                        'categoria': item.get('categoria', 'vegano'),
                        'source': 'gemini'
                    })
                
                logger.info(f"[HÍBRIDO] {len(acompanhamentos)} acompanhamentos via Gemini")
                        
        except Exception as e:
            logger.warning(f"[HÍBRIDO] Erro no Gemini: {e}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # RESULTADO FINAL
        # ═══════════════════════════════════════════════════════════════════════
        
        # Limitar a 6 acompanhamentos
        acompanhamentos = acompanhamentos[:6]
        
        total_items = 1 + len(acompanhamentos) if principal else len(acompanhamentos)
        local_count = 1 if principal_from_local else 0
        
        # Calcular nutrição baseado nos itens
        proteinas_count = sum(1 for a in acompanhamentos if a.get('categoria') == 'proteína animal')
        if principal and principal.get('categoria') == 'proteína animal':
            proteinas_count += 1
        
        return {
            'ok': True,
            'principal': principal,
            'acompanhamentos': acompanhamentos,
            'total_itens': total_items,
            'itens_do_buffet': local_count,
            'metodo': 'hibrido_gemini',
            'resumo_nutricional': {
                'calorias_totais': f'~{total_items * 120} kcal',
                'proteinas_totais': f'~{proteinas_count * 20 + (total_items - proteinas_count) * 5}g',
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
