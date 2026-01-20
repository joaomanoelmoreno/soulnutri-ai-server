"""SoulNutri AI - Policy (Política de Decisão)

Define a política de decisão a partir do score de similaridade.
Faixas de confiança:
- alta:   >= 0.85 (identificação segura)
- média:  >= 0.50 e < 0.85 (provável, confirmar com atendente)
- baixa:  < 0.50 (incerto, não confiar)

Baseado na analogia Waze: mostrar o melhor caminho em tempo real.
"""

from typing import Dict, List, Optional


def analyze_result(results: List[Dict]) -> Dict:
    """
    Analisa os resultados da busca e decide a resposta.
    
    Retorna uma decisão com:
    - identified: bool - se foi identificado com confiança
    - dish: str - nome do prato identificado
    - confidence: str - nível de confiança
    - message: str - mensagem para o usuário
    - alternatives: list - alternativas se houver dúvida
    """
    
    if not results or 'error' in results[0]:
        return {
            'identified': False,
            'dish': None,
            'confidence': 'baixa',
            'score': 0.0,
            'message': 'Não foi possível identificar o prato. Tente outra foto ou consulte o atendente.',
            'alternatives': []
        }
    
    top_result = results[0]
    score = top_result.get('score', 0)
    dish = top_result.get('dish', '')
    confidence = top_result.get('confidence', 'baixa')
    
    # Calcular gap para o segundo colocado
    gap = 0
    if len(results) > 1:
        gap = score - results[1].get('score', 0)
    
    # REGRA CRÍTICA: Se gap é pequeno, confiança não pode ser alta
    # Isso evita dizer "alta confiança" quando pode estar errado
    if gap < 0.15:
        confidence = 'média' if score >= 0.50 else 'baixa'
    
    # Decisão baseada em confiança e gap
    if confidence == 'alta' and gap >= 0.15:
        # Alta confiança com boa margem
        return {
            'identified': True,
            'dish': dish,
            'dish_display': format_dish_name(dish),
            'confidence': 'alta',
            'score': score,
            'message': f'Prato identificado com alta confiança.',
            'alternatives': []
        }
    
    elif confidence == 'alta' and gap < 0.1:
        # Alta confiança mas pouca margem
        alternatives = [r['dish'] for r in results[1:3]]
        return {
            'identified': True,
            'dish': dish,
            'dish_display': format_dish_name(dish),
            'confidence': 'alta',
            'score': score,
            'message': f'Prato identificado. Verifique se confere.',
            'alternatives': [format_dish_name(a) for a in alternatives]
        }
    
    elif confidence == 'média':
        # Confiança média - mostrar alternativas
        alternatives = [r['dish'] for r in results[1:4]]
        return {
            'identified': True,
            'dish': dish,
            'dish_display': format_dish_name(dish),
            'confidence': 'média',
            'score': score,
            'message': f'Provável identificação. Confirme com o atendente se necessário.',
            'alternatives': [format_dish_name(a) for a in alternatives]
        }
    
    else:
        # Baixa confiança
        alternatives = [r['dish'] for r in results[:5]]
        return {
            'identified': False,
            'dish': dish,
            'dish_display': format_dish_name(dish),
            'confidence': 'baixa',
            'score': score,
            'message': 'Identificação incerta. Consulte o atendente.',
            'alternatives': [format_dish_name(a) for a in alternatives]
        }


def format_dish_name(slug: str) -> str:
    """
    Converte slug para nome legível.
    Ex: beringelaaolimao -> Berinjela ao Limão
    """
    if not slug:
        return ''
    
    # Mapeamento de termos conhecidos
    replacements = {
        'ao': ' ao ',
        'de': ' de ',
        'com': ' com ',
        'sem': ' sem ',
        'graos': ' grãos',
        'grao': ' grão',
        'molho': ' molho ',
        'gratinado': ' gratinado',
        'empanado': ' empanado',
        'grelhado': ' grelhado',
        'assado': ' assado',
        'frito': ' frito',
        'cozido': ' cozido',
        'vegano': ' vegano',
        'integral': ' integral',
    }
    
    name = slug
    
    # Aplicar substituições
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Limpar espaços extras
    name = ' '.join(name.split())
    
    # Capitalizar
    name = name.title()
    
    return name


def get_risk_alert(dish: str, user_restrictions: List[str] = None) -> Optional[str]:
    """
    Verifica se o prato tem riscos para o usuário.
    (Placeholder para funcionalidade Premium)
    """
    # TODO: Implementar cruzamento com base de ingredientes/alergênicos
    return None
