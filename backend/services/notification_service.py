# -*- coding: utf-8 -*-
"""
SoulNutri - Servico de Notificacoes Push Personalizadas
Gera max 1 notificacao/dia baseada no consumo real do usuario.
Todas as notificacoes incluem referencias e links verificaveis.
"""
import os
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# Fontes confiaveis para referenciar nas notificacoes
REFERENCE_SOURCES = {
    "nutricao_br": {
        "TACO/UNICAMP": "https://www.cfn.org.br/wp-content/uploads/2017/03/taco_4_edicao_ampliada_e_revisada.pdf",
        "ANVISA": "https://www.gov.br/anvisa/pt-br",
        "Ministerio da Saude": "https://www.gov.br/saude/pt-br",
        "Guia Alimentar Brasileiro": "https://bvsms.saude.gov.br/bvs/publicacoes/guia_alimentar_populacao_brasileira_2ed.pdf",
    },
    "nutricao_intl": {
        "WHO": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
        "Harvard Nutrition Source": "https://www.hsph.harvard.edu/nutritionsource/",
        "Mayo Clinic": "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating",
        "FDA": "https://www.fda.gov/food/nutrition-education-resources-materials",
    },
    "ciencia": {
        "PubMed": "https://pubmed.ncbi.nlm.nih.gov/",
        "The Lancet": "https://www.thelancet.com/",
        "Nutrients Journal": "https://www.mdpi.com/journal/nutrients",
    }
}

# Templates de notificacoes por tipo de insight
NOTIFICATION_TEMPLATES = {
    "high_sodium": {
        "title": "Atencao ao Sodio",
        "icon": "alert-triangle",
        "priority": "high"
    },
    "low_fiber": {
        "title": "Aumente suas Fibras",
        "icon": "leaf",
        "priority": "medium"
    },
    "good_protein": {
        "title": "Proteinas em Dia",
        "icon": "check-circle",
        "priority": "low"
    },
    "calorie_alert": {
        "title": "Balanco Calorico",
        "icon": "flame",
        "priority": "medium"
    },
    "vitamin_tip": {
        "title": "Dica de Vitaminas",
        "icon": "sun",
        "priority": "low"
    },
    "hydration": {
        "title": "Hidratacao",
        "icon": "droplets",
        "priority": "medium"
    },
    "streak_celebration": {
        "title": "Parabens pela Sequencia",
        "icon": "trophy",
        "priority": "low"
    },
    "weekly_insight": {
        "title": "Resumo da Semana",
        "icon": "bar-chart",
        "priority": "medium"
    }
}


async def generate_personalized_notification(db, user_pin: str, user_name: str = "") -> dict:
    """
    Gera uma notificacao personalizada baseada no consumo recente do usuario.
    Maximo 1 notificacao por dia por usuario.
    Sempre inclui referencias e links.
    """
    try:
        # Verificar se ja enviou notificacao hoje
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        existing = await db.notifications.find_one({
            "user_pin": user_pin,
            "date": today
        })
        if existing:
            return {"ok": False, "reason": "already_sent_today"}

        # Buscar consumo recente (ultimos 7 dias)
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        recent_meals = []
        async for log in db.daily_logs.find({
            "user_pin": user_pin,
            "timestamp": {"$gte": week_ago}
        }).sort("timestamp", -1).limit(30):
            recent_meals.append(log)

        # Se nao tem consumo registrado, enviar dica generica
        if not recent_meals:
            notification = _generate_generic_notification()
        else:
            notification = _analyze_and_generate(recent_meals, user_name)

        # Salvar notificacao
        notification["user_pin"] = user_pin
        notification["user_name"] = user_name
        notification["date"] = today
        notification["created_at"] = datetime.now(timezone.utc).isoformat()
        notification["read"] = False

        await db.notifications.insert_one(notification)

        # Remover _id antes de retornar
        notification.pop("_id", None)

        return {"ok": True, "notification": notification}

    except Exception as e:
        logger.error(f"[NOTIFICATION] Erro ao gerar: {e}")
        return {"ok": False, "error": str(e)}


async def get_user_notifications(db, user_pin: str, limit: int = 20) -> list:
    """Retorna as notificacoes do usuario."""
    notifications = []
    async for n in db.notifications.find(
        {"user_pin": user_pin},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit):
        notifications.append(n)
    return notifications


async def mark_notification_read(db, user_pin: str, date: str) -> bool:
    """Marca uma notificacao como lida."""
    result = await db.notifications.update_one(
        {"user_pin": user_pin, "date": date},
        {"$set": {"read": True}}
    )
    return result.modified_count > 0


def _analyze_and_generate(meals: list, user_name: str) -> dict:
    """Analisa o consumo recente e gera uma notificacao relevante."""

    # Calcular medias
    total_cals = 0
    total_protein = 0
    total_sodium = 0
    total_fiber = 0
    meal_count = 0
    dishes_eaten = []

    for meal in meals:
        nutri = meal.get("nutrition", meal.get("nutricao", {}))
        if nutri:
            total_cals += nutri.get("calorias_kcal", nutri.get("calorias", 0)) or 0
            total_protein += nutri.get("proteinas_g", nutri.get("proteinas", 0)) or 0
            total_sodium += nutri.get("sodio_mg", nutri.get("sodio", 0)) or 0
            total_fiber += nutri.get("fibras_g", nutri.get("fibras", 0)) or 0
            meal_count += 1

        dish = meal.get("dish_name", meal.get("prato", ""))
        if dish and dish not in dishes_eaten:
            dishes_eaten.append(dish)

    if meal_count == 0:
        return _generate_generic_notification()

    avg_cals = total_cals / meal_count
    avg_sodium = total_sodium / meal_count
    avg_fiber = total_fiber / meal_count
    avg_protein = total_protein / meal_count

    greeting = f"{user_name}, " if user_name else ""

    # Priorizar alertas por importancia
    if avg_sodium > 800:
        return {
            "type": "high_sodium",
            "title": "Atencao ao Sodio",
            "message": f"{greeting}nos ultimos dias, seu consumo medio de sodio foi de {avg_sodium:.0f}mg por refeicao. "
                       f"A OMS recomenda no maximo 2.000mg/dia (cerca de 5g de sal). "
                       f"Considere reduzir temperos prontos e alimentos processados.",
            "icon": "alert-triangle",
            "priority": "high",
            "references": [
                {
                    "source": "WHO",
                    "title": "Reducao da ingestao de sodio",
                    "url": "https://www.who.int/news-room/fact-sheets/detail/salt-reduction"
                },
                {
                    "source": "Guia Alimentar Brasileiro",
                    "title": "Guia Alimentar para a Populacao Brasileira",
                    "url": "https://bvsms.saude.gov.br/bvs/publicacoes/guia_alimentar_populacao_brasileira_2ed.pdf"
                }
            ],
            "dishes_context": dishes_eaten[:3]
        }

    if avg_fiber < 3:
        return {
            "type": "low_fiber",
            "title": "Aumente suas Fibras",
            "message": f"{greeting}sua media de fibras por refeicao foi de {avg_fiber:.1f}g. "
                       f"O ideal e consumir pelo menos 25g/dia. "
                       f"Frutas, verduras, legumes e graos integrais sao otimas fontes.",
            "icon": "leaf",
            "priority": "medium",
            "references": [
                {
                    "source": "Harvard Nutrition Source",
                    "title": "Fiber: Start Roughing It!",
                    "url": "https://www.hsph.harvard.edu/nutritionsource/carbohydrates/fiber/"
                },
                {
                    "source": "Ministerio da Saude",
                    "title": "Alimentacao saudavel",
                    "url": "https://www.gov.br/saude/pt-br/assuntos/saude-brasil/eu-quero-me-alimentar-melhor"
                }
            ],
            "dishes_context": dishes_eaten[:3]
        }

    if avg_protein > 25:
        return {
            "type": "good_protein",
            "title": "Proteinas em Dia!",
            "message": f"{greeting}excelente! Sua media de proteinas foi de {avg_protein:.1f}g por refeicao. "
                       f"Isso ajuda na manutencao muscular e saciedade. Continue assim!",
            "icon": "check-circle",
            "priority": "low",
            "references": [
                {
                    "source": "Mayo Clinic",
                    "title": "How much protein do you need?",
                    "url": "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/protein/art-20048314"
                }
            ],
            "dishes_context": dishes_eaten[:3]
        }

    # Notificacao calorica
    if avg_cals > 600:
        return {
            "type": "calorie_alert",
            "title": "Balanco Calorico",
            "message": f"{greeting}sua media calorica por refeicao foi de {avg_cals:.0f}kcal. "
                       f"Para uma dieta equilibrada de 2.000kcal/dia, o ideal e distribuir entre 3-5 refeicoes.",
            "icon": "flame",
            "priority": "medium",
            "references": [
                {
                    "source": "ANVISA",
                    "title": "Rotulagem Nutricional",
                    "url": "https://www.gov.br/anvisa/pt-br/assuntos/alimentos/rotulagem"
                },
                {
                    "source": "FDA",
                    "title": "Using the Nutrition Facts Label",
                    "url": "https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label"
                }
            ],
            "dishes_context": dishes_eaten[:3]
        }

    # Dica generica com base no que comeu
    return {
        "type": "vitamin_tip",
        "title": "Dica Nutricional",
        "message": f"{greeting}que tal variar o cardapio? Nos ultimos dias voce consumiu "
                   f"{len(dishes_eaten)} pratos diferentes. A variedade alimentar e fundamental "
                   f"para garantir todos os nutrientes que o corpo precisa.",
        "icon": "sun",
        "priority": "low",
        "references": [
            {
                "source": "Guia Alimentar Brasileiro",
                "title": "Guia Alimentar para a Populacao Brasileira",
                "url": "https://bvsms.saude.gov.br/bvs/publicacoes/guia_alimentar_populacao_brasileira_2ed.pdf"
            },
            {
                "source": "Harvard Nutrition Source",
                "title": "Healthy Eating Plate",
                "url": "https://www.hsph.harvard.edu/nutritionsource/healthy-eating-plate/"
            }
        ],
        "dishes_context": dishes_eaten[:3]
    }


def _generate_generic_notification() -> dict:
    """Gera uma notificacao generica quando nao ha dados de consumo."""
    return {
        "type": "hydration",
        "title": "Lembre-se de se Hidratar",
        "message": "Beber agua suficiente e essencial para a saude. "
                   "A recomendacao geral e de pelo menos 2 litros por dia, "
                   "mas pode variar conforme atividade fisica e clima.",
        "icon": "droplets",
        "priority": "medium",
        "references": [
            {
                "source": "Mayo Clinic",
                "title": "Water: How much should you drink every day?",
                "url": "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256"
            },
            {
                "source": "WHO",
                "title": "Drinking-water",
                "url": "https://www.who.int/news-room/fact-sheets/detail/drinking-water"
            }
        ],
        "dishes_context": []
    }
