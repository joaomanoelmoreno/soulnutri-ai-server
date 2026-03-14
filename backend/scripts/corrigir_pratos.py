#!/usr/bin/env python3
"""
Script de correção em massa dos pratos - SoulNutri
Corrige nomes, categorias, alergenos e calorias básicas
SEM USAR IA - apenas regras locais
"""

import os
import json
import re
from pathlib import Path

BASE_DIR = Path("/app/datasets/organized")

# Ingredientes que indicam alergenos
ALERGENOS = {
    'crustaceo': ['camarão', 'camarao', 'lagosta', 'caranguejo', 'siri', 'marisco'],
    'peixe': ['peixe', 'atum', 'salmão', 'salmao', 'bacalhau', 'tilapia', 'sardinha', 'anchova'],
    'lactose': ['leite', 'queijo', 'creme de leite', 'nata', 'manteiga', 'iogurte', 'requeijão', 'parmesão', 'parmesao', 'mussarela', 'cream cheese', 'chantilly'],
    'gluten': ['trigo', 'farinha', 'pão', 'pao', 'massa', 'macarrão', 'macarrao', 'espaguete', 'lasanha', 'torta', 'empanado', 'milanesa', 'folhado', 'folhada'],
    'ovo': ['ovo', 'ovos', 'gema', 'clara de ovo', 'maionese'],
    'castanhas': ['amendoim', 'castanha', 'nozes', 'amêndoas', 'amendoas', 'avelã', 'pistache'],
    'soja': ['soja', 'tofu', 'shoyu', 'molho de soja', 'edamame'],
}

# Ingredientes calóricos - indicam que calorias devem ser altas
INGREDIENTES_CALORICOS = {
    'muito_alto': ['bacon', 'creme de leite', 'massa folhada', 'manteiga', 'parmesão', 'fritura', 'frito', 'empanado', 'milanesa', 'cream cheese', 'chantilly', 'chocolate'],
    'alto': ['queijo', 'maionese', 'azeite', 'óleo', 'batata', 'arroz', 'macarrão', 'pão'],
    'moderado': ['frango', 'carne', 'peixe', 'ovo'],
    'baixo': ['salada', 'legumes', 'verduras', 'tomate', 'alface']
}

def formatar_nome(slug):
    """Formata o slug para nome legível"""
    nome = slug
    
    # Substituições comuns
    subs = [
        ('aocurry', ' ao Curry'), ('aomolho', ' ao Molho'), ('aobalsamico', ' ao Balsâmico'),
        ('aoiogurte', ' ao Iogurte'), ('aolimao', ' ao Limão'), ('aomilanesa', ' à Milanesa'),
        ('aparmegiana', ' à Parmegiana'), ('comcarne', ' com Carne'), ('semcarne', ' sem Carne'),
        ('combatata', ' com Batata'), ('comlegumes', ' com Legumes'), ('comqueijo', ' com Queijo'),
        ('defrango', ' de Frango'), ('depeixe', ' de Peixe'), ('deatum', ' de Atum'),
        ('debacalhau', ' de Bacalhau'), ('decarne', ' de Carne'), ('dechocolate', ' de Chocolate'),
        ('demorango', ' de Morango'), ('decereja', ' de Cereja'), ('delimao', ' de Limão'),
        ('deovos', ' de Ovos'), ('dequinoa', ' de Quinoa'), ('deespinafre', ' de Espinafre'),
        ('decamarao', ' de Camarão'), ('deabobora', ' de Abóbora'), ('detapioca', ' de Tapioca'),
        ('grelhado', ' Grelhado'), ('grelhada', ' Grelhada'), ('gratinado', ' Gratinado'),
        ('empanado', ' Empanado'), ('assado', ' Assado'), ('cozido', ' Cozido'),
        ('refogado', ' Refogado'), ('recheado', ' Recheado'), ('integral', ' Integral'),
        ('vegano', ' Vegano'), ('branco', ' Branco'), ('preto', ' Preto'),
        ('mediterranea', ' Mediterrânea'), ('marroquino', ' Marroquino'),
        ('cestinha', 'Cestinha'), ('bolinho', 'Bolinho'), ('file', 'Filé'),
        ('pure', 'Purê'), ('pao', 'Pão'),
    ]
    
    nome_lower = nome.lower()
    for pattern, replacement in subs:
        if pattern in nome_lower:
            idx = nome_lower.find(pattern)
            nome = nome[:idx] + replacement + nome[idx+len(pattern):]
            nome_lower = nome.lower()
    
    # Adicionar espaços antes de maiúsculas
    nome = re.sub(r'([a-z])([A-Z])', r'\1 \2', nome)
    
    # Limpar espaços duplos
    nome = re.sub(r'\s+', ' ', nome).strip()
    
    # Capitalizar
    palavras = nome.split()
    preposicoes = ['de', 'do', 'da', 'dos', 'das', 'com', 'ao', 'à', 'e', 'em', 'sem', 'a']
    resultado = []
    for i, p in enumerate(palavras):
        if i == 0:
            resultado.append(p.capitalize())
        elif p.lower() in preposicoes:
            resultado.append(p.lower())
        else:
            resultado.append(p.capitalize())
    
    return ' '.join(resultado)


def detectar_alergenos(nome, ingredientes):
    """Detecta alergenos baseado no nome e ingredientes"""
    texto = (nome + ' ' + ' '.join(ingredientes)).lower()
    detectados = {}
    
    for alergeno, keywords in ALERGENOS.items():
        for kw in keywords:
            if kw in texto:
                detectados[alergeno] = True
                break
    
    return detectados


def estimar_calorias(nome, ingredientes):
    """Estima faixa de calorias baseado nos ingredientes"""
    texto = (nome + ' ' + ' '.join(ingredientes)).lower()
    
    # Verificar ingredientes calóricos
    for ing in INGREDIENTES_CALORICOS['muito_alto']:
        if ing in texto:
            return {'min': 250, 'max': 450, 'tipico': 350}
    
    for ing in INGREDIENTES_CALORICOS['alto']:
        if ing in texto:
            return {'min': 150, 'max': 300, 'tipico': 220}
    
    for ing in INGREDIENTES_CALORICOS['moderado']:
        if ing in texto:
            return {'min': 100, 'max': 200, 'tipico': 150}
    
    return {'min': 30, 'max': 100, 'tipico': 60}


def corrigir_prato(folder):
    """Corrige um prato específico"""
    folder_path = BASE_DIR / folder
    info_path = folder_path / "dish_info.json"
    
    if not info_path.exists():
        return None
    
    with open(info_path, 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    modificado = False
    
    # 1. Corrigir nome
    nome_antigo = info.get('nome', '')
    nome_novo = formatar_nome(folder)
    if nome_antigo != nome_novo and ' ' in nome_novo:
        info['nome'] = nome_novo
        modificado = True
    
    # 2. Detectar alergenos
    ingredientes = info.get('ingredientes', [])
    alergenos = detectar_alergenos(folder, ingredientes)
    
    # Atualizar flags de alergenos
    if alergenos.get('crustaceo') and not info.get('contem_frutos_mar'):
        info['contem_frutos_mar'] = True
        modificado = True
    if alergenos.get('peixe') and not info.get('contem_peixe'):
        info['contem_peixe'] = True
        modificado = True
    if alergenos.get('lactose') and not info.get('contem_lactose'):
        info['contem_lactose'] = True
        modificado = True
    if alergenos.get('gluten') and not info.get('contem_gluten'):
        info['contem_gluten'] = True
        modificado = True
    if alergenos.get('ovo') and not info.get('contem_ovo'):
        info['contem_ovo'] = True
        modificado = True
    if alergenos.get('castanhas') and not info.get('contem_castanhas'):
        info['contem_castanhas'] = True
        modificado = True
    if alergenos.get('soja') and not info.get('contem_soja'):
        info['contem_soja'] = True
        modificado = True
    
    # 3. Verificar calorias suspeitas
    calorias_str = info.get('nutricao', {}).get('calorias', '0')
    try:
        calorias_atual = int(re.search(r'\d+', str(calorias_str)).group())
    except:
        calorias_atual = 0
    
    estimativa = estimar_calorias(folder, ingredientes)
    
    # Se calorias muito baixas para ingredientes calóricos, marcar para revisão
    if calorias_atual < estimativa['min'] * 0.5:
        info['_calorias_suspeitas'] = True
        info['_calorias_estimadas'] = estimativa
        modificado = True
    
    if modificado:
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        return info['nome']
    
    return None


# Executar correções
print("🔧 Iniciando correção em massa dos pratos...")
corrigidos = 0
for folder in sorted(os.listdir(BASE_DIR)):
    if not (BASE_DIR / folder).is_dir():
        continue
    resultado = corrigir_prato(folder)
    if resultado:
        print(f"  ✅ {resultado}")
        corrigidos += 1

print(f"\n✅ {corrigidos} pratos corrigidos")
