"""SoulNutri - Serviço de Auditoria de Dados dos Pratos
Analisa os dish_info.json e identifica problemas de qualidade
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

DATASET_DIR = Path("/app/datasets/organized")

# Ingredientes que indicam categoria específica
# NOTA: Leite de coco, leite de amêndoas, etc. NÃO são de origem animal
INGREDIENTES_ANIMAL = [
    'frango', 'carne', 'boi', 'porco', 'bacon', 'linguiça', 'salsicha',
    'peixe', 'camarão', 'atum', 'salmão', 'bacalhau', 'tilápia',
    'ovo', 'leite de vaca', 'queijo', 'creme de leite', 'manteiga', 'nata',
    'presunto', 'peito de peru', 'costela', 'maminha', 'picanha',
    'fígado', 'coração', 'moela', 'rabada', 'rabo'
]

# Ingredientes que NÃO são de origem animal (veganos)
INGREDIENTES_VEGANOS = [
    'leite de coco', 'creme de coco', 'óleo de coco',
    'leite de amêndoas', 'leite de soja', 'leite de aveia',
    'leite de arroz', 'leite vegetal', 'tofu', 'tempeh', 'seitan'
]

INGREDIENTES_LACTOSE = [
    'leite de vaca', 'queijo', 'creme de leite', 'manteiga', 'nata',
    'iogurte', 'requeijão', 'cream cheese', 'parmesão', 'mussarela',
    'ricota', 'cottage', 'gorgonzola', 'provolone', 'cheddar'
]

INGREDIENTES_GLUTEN = [
    'farinha de trigo', 'pão', 'massa', 'macarrão', 'espaguete',
    'lasanha', 'torrada', 'biscoito', 'cerveja', 'empanado',
    'milanesa', 'coxinha', 'pastel', 'croissant'
]


def audit_all_dishes() -> Dict[str, Any]:
    """Audita todos os pratos e retorna relatório de problemas"""
    
    problems = {
        'missing_info_file': [],
        'empty_nutrition': [],
        'unknown_names': [],
        'category_conflicts': [],
        'missing_ingredients': [],
        'missing_description': [],
        'allergen_conflicts': []
    }
    
    total_dishes = 0
    dishes_with_issues = 0
    
    for dish_dir in DATASET_DIR.iterdir():
        if not dish_dir.is_dir():
            continue
        
        total_dishes += 1
        slug = dish_dir.name
        info_path = dish_dir / "dish_info.json"
        
        # Verificar se dish_info.json existe
        if not info_path.exists():
            problems['missing_info_file'].append({
                'slug': slug,
                'issue': 'Arquivo dish_info.json não existe',
                'severity': 'high'
            })
            dishes_with_issues += 1
            continue
        
        # Carregar e analisar
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
        except Exception as e:
            problems['missing_info_file'].append({
                'slug': slug,
                'issue': f'Erro ao ler arquivo: {str(e)}',
                'severity': 'high'
            })
            dishes_with_issues += 1
            continue
        
        has_issue = False
        
        # Verificar nome Unknown
        nome = info.get('nome', '')
        if 'unknown' in nome.lower() or not nome:
            problems['unknown_names'].append({
                'slug': slug,
                'nome': nome,
                'issue': 'Nome contém "Unknown" ou está vazio',
                'severity': 'high'
            })
            has_issue = True
        
        # Verificar nutrição vazia
        nutricao = info.get('nutricao', {})
        if not nutricao or not nutricao.get('calorias') or nutricao.get('calorias') == '':
            problems['empty_nutrition'].append({
                'slug': slug,
                'nome': nome,
                'issue': 'Informações nutricionais vazias',
                'severity': 'medium'
            })
            has_issue = True
        
        # Verificar ingredientes
        ingredientes = info.get('ingredientes', [])
        if not ingredientes or len(ingredientes) == 0:
            problems['missing_ingredients'].append({
                'slug': slug,
                'nome': nome,
                'issue': 'Lista de ingredientes vazia',
                'severity': 'medium'
            })
            has_issue = True
        
        # Verificar descrição
        descricao = info.get('descricao', '')
        if not descricao or len(descricao) < 10:
            problems['missing_description'].append({
                'slug': slug,
                'nome': nome,
                'issue': 'Descrição ausente ou muito curta',
                'severity': 'low'
            })
            has_issue = True
        
        # Verificar conflitos de categoria
        categoria = info.get('categoria', '').lower()
        ingredientes_lower = [i.lower() for i in ingredientes]
        ingredientes_text = ' '.join(ingredientes_lower)
        
        # Função para verificar se ingrediente é de origem animal (excluindo versões vegetais)
        def tem_ingrediente_animal(ing, texto):
            # Não considerar "leite de coco", "leite de soja", etc. como leite animal
            if ing == 'leite de vaca':
                # Verifica se tem "leite" mas não é vegetal
                if 'leite' in texto:
                    vegetais = ['leite de coco', 'leite de soja', 'leite de amêndoas', 
                               'leite de aveia', 'leite de arroz', 'leite vegetal']
                    for v in vegetais:
                        if v in texto:
                            return False
                    return True
                return False
            return ing in texto
        
        if categoria == 'vegano':
            for ing in INGREDIENTES_ANIMAL:
                if tem_ingrediente_animal(ing, ingredientes_text):
                    problems['category_conflicts'].append({
                        'slug': slug,
                        'nome': nome,
                        'issue': f'Prato marcado como VEGANO mas contém "{ing}"',
                        'severity': 'high'
                    })
                    has_issue = True
                    break
        
        elif categoria == 'vegetariano':
            for ing in ['frango', 'carne', 'boi', 'porco', 'bacon', 'peixe', 'camarão']:
                if ing in ingredientes_text:
                    problems['category_conflicts'].append({
                        'slug': slug,
                        'nome': nome,
                        'issue': f'Prato marcado como VEGETARIANO mas contém "{ing}"',
                        'severity': 'high'
                    })
                    has_issue = True
                    break
        
        # Verificar conflitos de alérgenos
        contem_gluten = info.get('contem_gluten', False)
        for ing in INGREDIENTES_GLUTEN:
            if ing in ingredientes_text and not contem_gluten:
                problems['allergen_conflicts'].append({
                    'slug': slug,
                    'nome': nome,
                    'issue': f'Contém "{ing}" mas não está marcado como contém glúten',
                    'severity': 'medium'
                })
                has_issue = True
                break
        
        if has_issue:
            dishes_with_issues += 1
    
    # Calcular estatísticas
    return {
        'total_dishes': total_dishes,
        'dishes_with_issues': dishes_with_issues,
        'health_score': round((1 - dishes_with_issues / total_dishes) * 100, 1) if total_dishes > 0 else 0,
        'problems': problems,
        'summary': {
            'missing_info_file': len(problems['missing_info_file']),
            'empty_nutrition': len(problems['empty_nutrition']),
            'unknown_names': len(problems['unknown_names']),
            'category_conflicts': len(problems['category_conflicts']),
            'missing_ingredients': len(problems['missing_ingredients']),
            'missing_description': len(problems['missing_description']),
            'allergen_conflicts': len(problems['allergen_conflicts'])
        }
    }


async def fix_dish_with_ai(slug: str) -> Dict[str, Any]:
    """Usa IA para corrigir/completar informações de um prato"""
    from services.generic_ai import analyze_dish_for_correction
    
    info_path = DATASET_DIR / slug / "dish_info.json"
    
    # Carregar info atual
    current_info = {}
    if info_path.exists():
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                current_info = json.load(f)
        except:
            pass
    
    # Buscar primeira imagem do prato
    dish_dir = DATASET_DIR / slug
    images = list(dish_dir.glob("*.jpg")) + list(dish_dir.glob("*.jpeg"))
    
    if not images:
        return {'ok': False, 'error': 'Nenhuma imagem encontrada para o prato'}
    
    # Ler imagem
    with open(images[0], 'rb') as f:
        image_bytes = f.read()
    
    # Chamar IA para análise
    ai_result = await analyze_dish_for_correction(image_bytes, current_info)
    
    if not ai_result.get('ok'):
        return ai_result
    
    # Mesclar informações (IA complementa o que está faltando)
    suggestions = ai_result.get('suggestions', {})
    
    return {
        'ok': True,
        'slug': slug,
        'current_info': current_info,
        'suggestions': suggestions,
        'changes_needed': ai_result.get('changes_needed', [])
    }


def apply_ai_suggestions(slug: str, suggestions: Dict) -> Dict[str, Any]:
    """Aplica as sugestões da IA ao dish_info.json"""
    
    info_path = DATASET_DIR / slug / "dish_info.json"
    
    # Carregar info atual
    current_info = {}
    if info_path.exists():
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                current_info = json.load(f)
        except:
            pass
    
    # Aplicar sugestões (apenas campos vazios ou marcados para correção)
    updated_info = {**current_info}
    
    for key, value in suggestions.items():
        if key not in current_info or not current_info.get(key):
            updated_info[key] = value
    
    # Garantir slug
    updated_info['slug'] = slug
    
    # Salvar
    try:
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(updated_info, f, ensure_ascii=False, indent=2)
        
        return {'ok': True, 'message': f'Informações de {slug} atualizadas'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
