# -*- coding: utf-8 -*-
"""
SERVIÇO DE NUTRIÇÃO PREMIUM - Rastreamento Completo
SoulNutri - Contador expandido com vitaminas, minerais e alertas

ZERO CRÉDITOS DE IA - 100% LOCAL (usa Tabela TACO)
"""

import sys
sys.path.insert(0, '/app/backend')

from data.taco_database import TACO_DATABASE, buscar_dados_taco, calcular_nutricao_prato, VDR, calcular_percentual_vdr
from data.radar_noticias import gerar_alerta_radar, buscar_fatos_prato
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

# Metas diárias personalizadas por perfil
def calcular_metas_personalizadas(perfil: dict) -> dict:
    """
    Calcula metas nutricionais personalizadas baseadas no perfil do usuário.
    """
    peso = float(perfil.get('peso', 70))
    altura = float(perfil.get('altura', 170))
    idade = int(perfil.get('idade', 30))
    sexo = perfil.get('sexo', 'M')
    nivel = perfil.get('nivel_atividade', 'moderado')
    objetivo = perfil.get('objetivo', 'manter')
    
    # Calcular TMB (Taxa Metabólica Basal) - Fórmula de Mifflin-St Jeor
    if sexo == 'M':
        tmb = 10 * peso + 6.25 * altura - 5 * idade + 5
    else:
        tmb = 10 * peso + 6.25 * altura - 5 * idade - 161
    
    # Fator de atividade
    fatores = {
        'sedentario': 1.2,
        'leve': 1.375,
        'moderado': 1.55,
        'intenso': 1.725,
        'muito_intenso': 1.9
    }
    fator = fatores.get(nivel, 1.55)
    
    # GET (Gasto Energético Total)
    get = tmb * fator
    
    # Ajustar por objetivo
    if objetivo == 'perder':
        calorias = get - 500  # Déficit de 500 kcal
    elif objetivo == 'ganhar':
        calorias = get + 300  # Superávit de 300 kcal
    else:
        calorias = get
    
    # Macros baseados em % das calorias
    # Proteína: 25% / Carbs: 50% / Gordura: 25%
    proteinas = (calorias * 0.25) / 4  # 4 kcal/g
    carboidratos = (calorias * 0.50) / 4
    gorduras = (calorias * 0.25) / 9  # 9 kcal/g
    
    return {
        "calorias": round(calorias),
        "proteinas": round(proteinas),
        "carboidratos": round(carboidratos),
        "gorduras": round(gorduras),
        "fibras": 25 if sexo == 'F' else 30,
        "sodio": 2000,  # Recomendação mais conservadora
        "calcio": 1000,
        "ferro": 18 if sexo == 'F' else 8,  # Mulheres precisam mais
        "vitamina_a": 700 if sexo == 'F' else 900,
        "vitamina_c": 75 if sexo == 'F' else 90,
        "vitamina_b12": 2.4,
        "potassio": 4700,
        "zinco": 8 if sexo == 'F' else 11,
        "acucar": 25  # OMS recomenda máximo
    }


def analisar_consumo_diario(refeicoes: list, perfil: dict) -> dict:
    """
    Analisa o consumo diário e gera alertas personalizados.
    
    Args:
        refeicoes: Lista de pratos consumidos hoje
        perfil: Perfil do usuário Premium
    
    Returns:
        dict com totais, percentuais, alertas e recomendações
    """
    metas = calcular_metas_personalizadas(perfil)
    
    totais = {
        "calorias": 0,
        "proteinas": 0,
        "carboidratos": 0,
        "gorduras": 0,
        "fibras": 0,
        "sodio": 0,
        "calcio": 0,
        "ferro": 0,
        "vitamina_a": 0,
        "vitamina_c": 0,
        "vitamina_b12": 0,
        "potassio": 0,
        "zinco": 0,
        "acucar": 0
    }
    
    pratos_detalhados = []
    
    for refeicao in refeicoes:
        # Se tiver nutrição no prato, usar
        nutricao = refeicao.get('nutricao', {})
        if nutricao:
            totais["calorias"] += _parse_valor(nutricao.get('calorias', 0))
            totais["proteinas"] += _parse_valor(nutricao.get('proteinas', 0))
            totais["carboidratos"] += _parse_valor(nutricao.get('carboidratos', 0))
            totais["gorduras"] += _parse_valor(nutricao.get('gorduras', 0))
            totais["fibras"] += _parse_valor(nutricao.get('fibras', 0))
        
        # Tentar enriquecer com TACO se tiver ingredientes
        ingredientes = refeicao.get('ingredientes', [])
        if ingredientes:
            taco_nutri = calcular_nutricao_prato(ingredientes, 200)
            if taco_nutri:
                # Adicionar micronutrientes do TACO
                totais["sodio"] += taco_nutri.get('sodio', 0)
                totais["calcio"] += taco_nutri.get('calcio', 0)
                totais["ferro"] += taco_nutri.get('ferro', 0)
                totais["vitamina_a"] += taco_nutri.get('vitamina_a', 0)
                totais["vitamina_c"] += taco_nutri.get('vitamina_c', 0)
                totais["vitamina_b12"] += taco_nutri.get('vitamina_b12', 0)
                totais["potassio"] += taco_nutri.get('potassio', 0)
                totais["zinco"] += taco_nutri.get('zinco', 0)
                totais["acucar"] += taco_nutri.get('acucar', 0)
        
        pratos_detalhados.append({
            "nome": refeicao.get('nome', 'Prato'),
            "hora": refeicao.get('hora', '12:00'),
            "calorias": _parse_valor(nutricao.get('calorias', 0))
        })
    
    # Calcular percentuais
    percentuais = {}
    for nutriente, valor in totais.items():
        meta = metas.get(nutriente, VDR.get(nutriente, 100))
        if meta > 0:
            percentuais[nutriente] = round((valor / meta) * 100, 1)
        else:
            percentuais[nutriente] = 0
    
    # Gerar alertas
    alertas = []
    
    # Alertas de excesso
    if percentuais.get("sodio", 0) > 80:
        alertas.append({
            "tipo": "excesso",
            "nivel": "alto" if percentuais["sodio"] > 100 else "moderado",
            "emoji": "🧂",
            "nutriente": "Sódio",
            "mensagem": f"Consumo de sódio em {percentuais['sodio']:.0f}% da meta - atenção com a pressão!",
            "dica": "Evite alimentos muito salgados no restante do dia"
        })
    
    if percentuais.get("acucar", 0) > 80:
        alertas.append({
            "tipo": "excesso",
            "nivel": "alto" if percentuais["acucar"] > 100 else "moderado",
            "emoji": "🍬",
            "nutriente": "Açúcar",
            "mensagem": f"Consumo de açúcar em {percentuais['acucar']:.0f}% do limite - cuidado!",
            "dica": "Prefira frutas se quiser algo doce"
        })
    
    if percentuais.get("gorduras", 0) > 100:
        alertas.append({
            "tipo": "excesso",
            "nivel": "alto",
            "emoji": "🫒",
            "nutriente": "Gorduras",
            "mensagem": f"Meta de gorduras ultrapassada ({percentuais['gorduras']:.0f}%)",
            "dica": "Escolha preparações mais leves"
        })
    
    # Alertas de deficiência (se passar de 50% do dia e estiver baixo)
    hora_atual = datetime.now().hour
    if hora_atual >= 14:  # Depois do almoço
        if percentuais.get("proteinas", 0) < 40:
            alertas.append({
                "tipo": "deficiencia",
                "nivel": "moderado",
                "emoji": "💪",
                "nutriente": "Proteínas",
                "mensagem": f"Proteínas ainda em {percentuais['proteinas']:.0f}% - inclua mais na próxima refeição",
                "dica": "Frango, peixe, ovos ou leguminosas são boas opções"
            })
        
        if percentuais.get("fibras", 0) < 30:
            alertas.append({
                "tipo": "deficiencia",
                "nivel": "leve",
                "emoji": "🥬",
                "nutriente": "Fibras",
                "mensagem": f"Fibras em {percentuais['fibras']:.0f}% - aumente vegetais e legumes",
                "dica": "Saladas, feijão e frutas com casca são ricas em fibras"
            })
        
        if percentuais.get("vitamina_c", 0) < 30:
            alertas.append({
                "tipo": "deficiencia",
                "nivel": "leve",
                "emoji": "🍊",
                "nutriente": "Vitamina C",
                "mensagem": "Vitamina C baixa - inclua frutas cítricas",
                "dica": "Laranja, limão, acerola ou kiwi são excelentes fontes"
            })
    
    # Alertas personalizados por restrições
    restricoes = perfil.get('restricoes', [])
    if isinstance(restricoes, str):
        restricoes = restricoes.split(',')
    
    if 'diabetico' in restricoes or 'diabetes' in restricoes:
        if percentuais.get("carboidratos", 0) > 70:
            alertas.append({
                "tipo": "personalizado",
                "nivel": "alto",
                "emoji": "⚠️",
                "nutriente": "Carboidratos",
                "mensagem": "Atenção diabético: carboidratos em " + f"{percentuais['carboidratos']:.0f}%",
                "dica": "Monitore sua glicemia após a refeição"
            })
    
    if 'hipertenso' in restricoes or 'hipertensao' in restricoes:
        if percentuais.get("sodio", 0) > 60:
            alertas.append({
                "tipo": "personalizado",
                "nivel": "alto",
                "emoji": "❤️",
                "nutriente": "Sódio",
                "mensagem": "Atenção hipertenso: sódio em " + f"{percentuais['sodio']:.0f}%",
                "dica": "Evite sal extra e alimentos processados"
            })
    
    return {
        "totais": totais,
        "metas": metas,
        "percentuais": percentuais,
        "alertas": alertas,
        "pratos": pratos_detalhados,
        "resumo": {
            "calorias_consumidas": round(totais["calorias"]),
            "calorias_meta": metas["calorias"],
            "calorias_restantes": max(0, metas["calorias"] - totais["calorias"]),
            "percentual_calorias": percentuais.get("calorias", 0)
        }
    }


def analisar_consumo_semanal(refeicoes_semana: list, perfil: dict) -> dict:
    """
    Analisa o consumo semanal e gera relatório completo.
    
    Args:
        refeicoes_semana: Lista de todas as refeições da semana
        perfil: Perfil do usuário
    
    Returns:
        dict com análise semanal, tendências e recomendações
    """
    metas = calcular_metas_personalizadas(perfil)
    
    # Totais da semana
    totais_semana = {
        "calorias": 0,
        "proteinas": 0,
        "carboidratos": 0,
        "gorduras": 0,
        "fibras": 0,
        "sodio": 0,
        "calcio": 0,
        "ferro": 0,
        "vitamina_a": 0,
        "vitamina_c": 0,
        "vitamina_b12": 0,
        "potassio": 0,
        "zinco": 0,
        "acucar": 0
    }
    
    dias_com_dados = 0
    
    for refeicao in refeicoes_semana:
        nutricao = refeicao.get('nutricao', {})
        if nutricao:
            totais_semana["calorias"] += _parse_valor(nutricao.get('calorias', 0))
            totais_semana["proteinas"] += _parse_valor(nutricao.get('proteinas', 0))
            totais_semana["carboidratos"] += _parse_valor(nutricao.get('carboidratos', 0))
            totais_semana["gorduras"] += _parse_valor(nutricao.get('gorduras', 0))
    
    # Calcular médias diárias
    dias_com_dados = max(1, len(set(r.get('data', '') for r in refeicoes_semana if r.get('data'))))
    
    medias_diarias = {k: v / dias_com_dados for k, v in totais_semana.items()}
    
    # Metas semanais (7 dias)
    metas_semana = {k: v * 7 for k, v in metas.items()}
    
    # Percentuais semanais
    percentuais_semana = {}
    for nutriente, valor in totais_semana.items():
        meta = metas_semana.get(nutriente, 1)
        if meta > 0:
            percentuais_semana[nutriente] = round((valor / meta) * 100, 1)
    
    # Análise de tendências
    tendencias = []
    
    # Verificar desequilíbrios
    if percentuais_semana.get("proteinas", 0) < 70:
        tendencias.append({
            "tipo": "baixo",
            "emoji": "📉",
            "nutriente": "Proteínas",
            "mensagem": "Consumo de proteínas abaixo do ideal esta semana",
            "impacto": "Pode afetar massa muscular e saciedade",
            "sugestao": "Inclua mais carnes magras, ovos, peixes ou leguminosas"
        })
    
    if percentuais_semana.get("fibras", 0) < 60:
        tendencias.append({
            "tipo": "baixo",
            "emoji": "📉",
            "nutriente": "Fibras",
            "mensagem": "Fibras muito baixas esta semana",
            "impacto": "Pode causar problemas intestinais",
            "sugestao": "Aumente vegetais, frutas com casca e grãos integrais"
        })
    
    if percentuais_semana.get("sodio", 0) > 120:
        tendencias.append({
            "tipo": "alto",
            "emoji": "📈",
            "nutriente": "Sódio",
            "mensagem": "Consumo de sódio elevado esta semana",
            "impacto": "Risco para pressão arterial",
            "sugestao": "Reduza alimentos processados e sal extra"
        })
    
    if percentuais_semana.get("acucar", 0) > 120:
        tendencias.append({
            "tipo": "alto",
            "emoji": "📈",
            "nutriente": "Açúcar",
            "mensagem": "Muito açúcar consumido esta semana",
            "impacto": "Risco para glicemia e peso",
            "sugestao": "Troque doces por frutas, reduza refrigerantes"
        })
    
    # Vitaminas e minerais
    if percentuais_semana.get("vitamina_c", 0) < 50:
        tendencias.append({
            "tipo": "baixo",
            "emoji": "🍊",
            "nutriente": "Vitamina C",
            "mensagem": "Vitamina C muito baixa",
            "impacto": "Afeta imunidade e absorção de ferro",
            "sugestao": "Consuma mais frutas cítricas e vegetais frescos"
        })
    
    if percentuais_semana.get("calcio", 0) < 50:
        tendencias.append({
            "tipo": "baixo",
            "emoji": "🦴",
            "nutriente": "Cálcio",
            "mensagem": "Cálcio abaixo do ideal",
            "impacto": "Importante para ossos e músculos",
            "sugestao": "Inclua laticínios, vegetais verde-escuros ou sardinha"
        })
    
    if percentuais_semana.get("ferro", 0) < 50:
        tendencias.append({
            "tipo": "baixo",
            "emoji": "🩸",
            "nutriente": "Ferro",
            "mensagem": "Ferro baixo esta semana",
            "impacto": "Pode causar fadiga e anemia",
            "sugestao": "Carnes vermelhas, feijão e vegetais verde-escuros"
        })
    
    # Pontuação geral (0-100)
    pontos_bons = 0
    total_nutrientes = 14
    
    for nutriente, perc in percentuais_semana.items():
        if 70 <= perc <= 120:
            pontos_bons += 1
        elif 50 <= perc <= 150:
            pontos_bons += 0.5
    
    pontuacao = round((pontos_bons / total_nutrientes) * 100)
    
    # Classificação
    if pontuacao >= 80:
        classificacao = {"emoji": "🌟", "texto": "Excelente", "cor": "#22c55e"}
    elif pontuacao >= 60:
        classificacao = {"emoji": "👍", "texto": "Bom", "cor": "#3b82f6"}
    elif pontuacao >= 40:
        classificacao = {"emoji": "⚠️", "texto": "Regular", "cor": "#f59e0b"}
    else:
        classificacao = {"emoji": "🔴", "texto": "Precisa melhorar", "cor": "#ef4444"}
    
    return {
        "totais_semana": totais_semana,
        "medias_diarias": medias_diarias,
        "percentuais": percentuais_semana,
        "tendencias": tendencias,
        "dias_registrados": dias_com_dados,
        "pontuacao": pontuacao,
        "classificacao": classificacao,
        "metas_semana": metas_semana
    }


def _parse_valor(valor) -> float:
    """Converte valor para float, tratando strings como '250 kcal'."""
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        # Remove unidades e converte
        numeros = ''.join(c for c in valor if c.isdigit() or c == '.')
        try:
            return float(numeros) if numeros else 0
        except:
            return 0
    return 0
