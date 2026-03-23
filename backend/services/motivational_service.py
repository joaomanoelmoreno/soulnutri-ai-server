# -*- coding: utf-8 -*-
"""
SoulNutri - Servico Motivacional
Badges, streaks, conquistas e mensagens motivacionais.
"""
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# Definicao de badges/conquistas
BADGES = [
    {
        "id": "first_meal",
        "nome": "Primeira Refeicao",
        "descricao": "Registrou sua primeira refeicao",
        "icone": "utensils",
        "cor": "#22c55e",
        "criterio": {"tipo": "total_refeicoes", "valor": 1}
    },
    {
        "id": "streak_3",
        "nome": "Constante",
        "descricao": "3 dias seguidos registrando refeicoes",
        "icone": "flame",
        "cor": "#f59e0b",
        "criterio": {"tipo": "streak", "valor": 3}
    },
    {
        "id": "streak_7",
        "nome": "Dedicado",
        "descricao": "7 dias seguidos! Uma semana completa",
        "icone": "trophy",
        "cor": "#eab308",
        "criterio": {"tipo": "streak", "valor": 7}
    },
    {
        "id": "streak_14",
        "nome": "Disciplinado",
        "descricao": "14 dias seguidos de registro",
        "icone": "medal",
        "cor": "#f97316",
        "criterio": {"tipo": "streak", "valor": 14}
    },
    {
        "id": "streak_30",
        "nome": "Habito Formado",
        "descricao": "30 dias seguidos! Voce criou um habito",
        "icone": "crown",
        "cor": "#a855f7",
        "criterio": {"tipo": "streak", "valor": 30}
    },
    {
        "id": "variety_10",
        "nome": "Explorador",
        "descricao": "Experimentou 10 pratos diferentes",
        "icone": "compass",
        "cor": "#06b6d4",
        "criterio": {"tipo": "variedade", "valor": 10}
    },
    {
        "id": "variety_25",
        "nome": "Aventureiro",
        "descricao": "25 pratos diferentes! Paladar diversificado",
        "icone": "globe",
        "cor": "#3b82f6",
        "criterio": {"tipo": "variedade", "valor": 25}
    },
    {
        "id": "variety_50",
        "nome": "Gourmet",
        "descricao": "50 pratos diferentes!",
        "icone": "star",
        "cor": "#ec4899",
        "criterio": {"tipo": "variedade", "valor": 50}
    },
    {
        "id": "score_70",
        "nome": "Alimentacao Nota A",
        "descricao": "Score semanal acima de 70",
        "icone": "award",
        "cor": "#22c55e",
        "criterio": {"tipo": "score", "valor": 70}
    },
    {
        "id": "score_85",
        "nome": "Nutricao Excelente",
        "descricao": "Score semanal acima de 85! Parabens!",
        "icone": "zap",
        "cor": "#10b981",
        "criterio": {"tipo": "score", "valor": 85}
    },
    {
        "id": "veggie_5",
        "nome": "Amigo Verde",
        "descricao": "5 refeicoes vegetarianas/veganas na semana",
        "icone": "leaf",
        "cor": "#16a34a",
        "criterio": {"tipo": "veggie_count", "valor": 5}
    },
    {
        "id": "balanced_3",
        "nome": "Equilibrista",
        "descricao": "3 dias com macros equilibrados",
        "icone": "scale",
        "cor": "#8b5cf6",
        "criterio": {"tipo": "balanced_days", "valor": 3}
    }
]

# Mensagens motivacionais baseadas no contexto
MOTIVATIONAL_MESSAGES = {
    "streak_growing": [
        "Cada dia conta! Voce esta construindo um habito incrivel.",
        "Sua consistencia e inspiradora! Continue assim.",
        "Voce esta no caminho certo! Persistencia transforma."
    ],
    "score_high": [
        "Sua alimentacao esta excelente! Seu corpo agradece.",
        "Parabens! Voce e um exemplo de nutricao equilibrada.",
        "Nota A+! Continue cuidando de si com tanto carinho."
    ],
    "score_improving": [
        "Voce esta melhorando a cada dia! Progresso e o que importa.",
        "A mudanca comeca com pequenos passos. Voce ja esta caminhando!",
        "Cada escolha saudavel conta. Voce esta evoluindo!"
    ],
    "needs_variety": [
        "Que tal experimentar um prato diferente hoje?",
        "A variedade e a chave da nutricao completa. Explore novos sabores!",
        "Seu paladar merece aventura! Tente algo novo no buffet."
    ],
    "needs_protein": [
        "Sua proteina esta abaixo do ideal. Que tal incluir mais leguminosas?",
        "Proteina e fundamental para sua energia. Vamos equilibrar?"
    ],
    "needs_veggies": [
        "Inclua mais vegetais na proxima refeicao. Cores no prato = saude!",
        "Vegetais sao aliados poderosos. Quanto mais colorido, melhor!"
    ],
    "general_positive": [
        "Voce esta cuidando do que mais importa: sua saude!",
        "Nutrir-se bem e um ato de amor proprio.",
        "Cada refeicao e uma oportunidade de nutrir corpo e alma."
    ]
}


def calculate_achievements(user_data: dict) -> dict:
    """
    Calcula badges, streak e mensagens motivacionais para o usuario.
    user_data deve conter: streak, total_refeicoes, pratos_unicos, score, logs
    """
    import random
    
    streak = user_data.get("streak", 0)
    total_refeicoes = user_data.get("total_refeicoes", 0)
    pratos_unicos = user_data.get("pratos_unicos", 0)
    score = user_data.get("score", 0)
    veggie_count = user_data.get("veggie_count", 0)
    balanced_days = user_data.get("balanced_days", 0)
    prev_score = user_data.get("prev_score", 0)
    
    # Calcular badges desbloqueados
    unlocked = []
    locked = []
    
    for badge in BADGES:
        criterio = badge["criterio"]
        achieved = False
        progress = 0
        
        if criterio["tipo"] == "total_refeicoes":
            achieved = total_refeicoes >= criterio["valor"]
            progress = min(total_refeicoes / criterio["valor"], 1.0)
        elif criterio["tipo"] == "streak":
            achieved = streak >= criterio["valor"]
            progress = min(streak / criterio["valor"], 1.0)
        elif criterio["tipo"] == "variedade":
            achieved = pratos_unicos >= criterio["valor"]
            progress = min(pratos_unicos / criterio["valor"], 1.0)
        elif criterio["tipo"] == "score":
            achieved = score >= criterio["valor"]
            progress = min(score / criterio["valor"], 1.0)
        elif criterio["tipo"] == "veggie_count":
            achieved = veggie_count >= criterio["valor"]
            progress = min(veggie_count / criterio["valor"], 1.0)
        elif criterio["tipo"] == "balanced_days":
            achieved = balanced_days >= criterio["valor"]
            progress = min(balanced_days / criterio["valor"], 1.0)
        
        badge_data = {**badge, "achieved": achieved, "progress": round(progress, 2)}
        if achieved:
            unlocked.append(badge_data)
        else:
            locked.append(badge_data)
    
    # Selecionar mensagens motivacionais
    messages = []
    
    if streak >= 3:
        messages.append(random.choice(MOTIVATIONAL_MESSAGES["streak_growing"]))
    
    if score >= 70:
        messages.append(random.choice(MOTIVATIONAL_MESSAGES["score_high"]))
    elif score > prev_score and score > 0:
        messages.append(random.choice(MOTIVATIONAL_MESSAGES["score_improving"]))
    
    if pratos_unicos < 5 and total_refeicoes > 3:
        messages.append(random.choice(MOTIVATIONAL_MESSAGES["needs_variety"]))
    
    if not messages:
        messages.append(random.choice(MOTIVATIONAL_MESSAGES["general_positive"]))
    
    # Proximo badge a desbloquear
    next_badge = locked[0] if locked else None
    
    return {
        "badges_unlocked": unlocked,
        "badges_locked": locked,
        "total_badges": len(unlocked),
        "total_possible": len(BADGES),
        "streak": streak,
        "next_badge": next_badge,
        "motivational_messages": messages,
        "level": calculate_level(len(unlocked), streak, score)
    }


def calculate_level(badges_count: int, streak: int, score: int) -> dict:
    """Calcula o nivel do usuario baseado em seus achievements."""
    xp = badges_count * 100 + streak * 10 + score * 2
    
    levels = [
        {"nivel": 1, "nome": "Iniciante", "xp_min": 0, "cor": "#6b7280"},
        {"nivel": 2, "nome": "Aprendiz", "xp_min": 100, "cor": "#22c55e"},
        {"nivel": 3, "nome": "Praticante", "xp_min": 300, "cor": "#3b82f6"},
        {"nivel": 4, "nome": "Dedicado", "xp_min": 600, "cor": "#8b5cf6"},
        {"nivel": 5, "nome": "Expert", "xp_min": 1000, "cor": "#f59e0b"},
        {"nivel": 6, "nome": "Mestre Nutri", "xp_min": 1500, "cor": "#ec4899"},
        {"nivel": 7, "nome": "Lenda SoulNutri", "xp_min": 2500, "cor": "#ef4444"}
    ]
    
    current_level = levels[0]
    next_level = levels[1] if len(levels) > 1 else None
    
    for i, level in enumerate(levels):
        if xp >= level["xp_min"]:
            current_level = level
            next_level = levels[i + 1] if i + 1 < len(levels) else None
    
    progress_to_next = 0
    if next_level:
        range_xp = next_level["xp_min"] - current_level["xp_min"]
        progress_to_next = (xp - current_level["xp_min"]) / range_xp if range_xp > 0 else 1.0
    
    return {
        "nivel": current_level["nivel"],
        "nome": current_level["nome"],
        "cor": current_level["cor"],
        "xp": xp,
        "xp_proximo": next_level["xp_min"] if next_level else current_level["xp_min"],
        "progresso": round(min(progress_to_next, 1.0), 2),
        "proximo_nivel": next_level["nome"] if next_level else "Nivel Maximo!"
    }
