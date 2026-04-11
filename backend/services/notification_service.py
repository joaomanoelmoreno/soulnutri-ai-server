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

    # Dica generica com base no que comeu - rotacao diaria
    day = datetime.now(timezone.utc).timetuple().tm_yday
    variety_tips = [
        {
            "type": "vitamin_tip",
            "title": "Variedade Alimentar",
            "message": f"{greeting}nos ultimos dias voce consumiu {len(dishes_eaten)} pratos diferentes. "
                       f"A variedade e fundamental para garantir todos os nutrientes que o corpo precisa.",
        },
        {
            "type": "vitamin_tip",
            "title": "Equilibrio no Prato",
            "message": f"{greeting}tente montar seu prato com 50% vegetais, 25% proteina e 25% carboidrato. "
                       f"Esse equilibrio garante saciedade e nutricao completa.",
        },
        {
            "type": "vitamin_tip",
            "title": "Comer com Atencao",
            "message": f"{greeting}voce registrou {meal_count} refeicoes recentemente. "
                       f"Preste atencao no que come: saborear cada garfada melhora a digestao e saciedade.",
        },
    ]
    tip = variety_tips[day % len(variety_tips)]
    return {
        **tip,
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
    """Gera uma notificacao generica com rotacao diaria (nunca repete no mesmo dia)."""
    from datetime import datetime, timezone
    
    DICAS_POOL = [
        {
            "type": "hydration", "title": "Hidratacao", "icon": "droplets", "priority": "medium",
            "message": "Beber agua suficiente e essencial. A recomendacao e de pelo menos 2 litros por dia, mais se fizer atividade fisica.",
            "references": [{"source": "Mayo Clinic", "title": "How much water?", "url": "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256"}]
        },
        {
            "type": "vitamin_tip", "title": "Vitamina D e Sol", "icon": "sun", "priority": "low",
            "message": "15 minutos de sol pela manha ajudam na producao de vitamina D, essencial para ossos e imunidade.",
            "references": [{"source": "Harvard", "title": "Vitamin D", "url": "https://www.hsph.harvard.edu/nutritionsource/vitamin-d/"}]
        },
        {
            "type": "vitamin_tip", "title": "Cores no Prato", "icon": "leaf", "priority": "low",
            "message": "Quanto mais cores no prato, maior a variedade de nutrientes. Tente incluir pelo menos 3 cores diferentes em cada refeicao.",
            "references": [{"source": "Guia Alimentar", "title": "Guia Alimentar Brasileiro", "url": "https://bvsms.saude.gov.br/bvs/publicacoes/guia_alimentar_populacao_brasileira_2ed.pdf"}]
        },
        {
            "type": "vitamin_tip", "title": "Mastigar Bem", "icon": "check-circle", "priority": "low",
            "message": "Mastigar devagar melhora a digestao e aumenta a saciedade. Tente comer sem pressa, saboreando cada garfada.",
            "references": [{"source": "Harvard", "title": "Mindful Eating", "url": "https://www.hsph.harvard.edu/nutritionsource/mindful-eating/"}]
        },
        {
            "type": "vitamin_tip", "title": "Ferro e Vitamina C", "icon": "leaf", "priority": "medium",
            "message": "Combinacao poderosa: alimentos ricos em ferro (feijao, lentilha) com vitamina C (limao, laranja) aumentam a absorcao de ferro em ate 6x.",
            "references": [{"source": "PubMed", "title": "Iron absorption", "url": "https://pubmed.ncbi.nlm.nih.gov/"}]
        },
        {
            "type": "vitamin_tip", "title": "Omega 3", "icon": "sun", "priority": "low",
            "message": "Peixes como sardinha e salmao sao ricos em omega-3, importante para o cerebro e coracao. Tente incluir peixe pelo menos 2x por semana.",
            "references": [{"source": "WHO", "title": "Healthy diet", "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"}]
        },
        {
            "type": "low_fiber", "title": "Fibras e Intestino", "icon": "leaf", "priority": "medium",
            "message": "Fibras ajudam o intestino a funcionar bem. Aveia, frutas com casca e legumes sao otimas fontes. Meta: 25g por dia.",
            "references": [{"source": "Harvard", "title": "Fiber", "url": "https://www.hsph.harvard.edu/nutritionsource/carbohydrates/fiber/"}]
        },
        {
            "type": "vitamin_tip", "title": "Calcio Alem do Leite", "icon": "check-circle", "priority": "low",
            "message": "Brocolis, couve, gergelim e sardinha sao fontes de calcio para quem nao consome lacteos.",
            "references": [{"source": "Harvard", "title": "Calcium", "url": "https://www.hsph.harvard.edu/nutritionsource/calcium/"}]
        },
        {
            "type": "vitamin_tip", "title": "Acucar Oculto", "icon": "alert-triangle", "priority": "medium",
            "message": "Cuidado com o acucar escondido! Sucos industrializados, molhos prontos e cereais matinais podem ter mais acucar do que voce imagina.",
            "references": [{"source": "ANVISA", "title": "Rotulagem", "url": "https://www.gov.br/anvisa/pt-br/assuntos/alimentos/rotulagem"}]
        },
        {
            "type": "vitamin_tip", "title": "Probioticos Naturais", "icon": "leaf", "priority": "low",
            "message": "Iogurte natural, kefir e kombucha contem probioticos que beneficiam a flora intestinal e a imunidade.",
            "references": [{"source": "Harvard", "title": "Probiotics", "url": "https://www.hsph.harvard.edu/nutritionsource/food-features/fermented-foods/"}]
        },
        {
            "type": "vitamin_tip", "title": "Proteina Vegetal", "icon": "leaf", "priority": "low",
            "message": "Feijao com arroz formam uma proteina completa! A combinacao brasileira tradicional e nutricionalmente perfeita.",
            "references": [{"source": "Guia Alimentar", "title": "Guia Alimentar Brasileiro", "url": "https://bvsms.saude.gov.br/bvs/publicacoes/guia_alimentar_populacao_brasileira_2ed.pdf"}]
        },
        {
            "type": "hydration", "title": "Agua e Disposicao", "icon": "droplets", "priority": "medium",
            "message": "Desidratacao leve (1-2%) ja causa cansaco, dor de cabeca e dificuldade de concentracao. Mantenha uma garrafa por perto!",
            "references": [{"source": "Mayo Clinic", "title": "Dehydration", "url": "https://www.mayoclinic.org/diseases-conditions/dehydration/symptoms-causes/syc-20354086"}]
        },
        {
            "type": "vitamin_tip", "title": "Temperos Naturais", "icon": "sun", "priority": "low",
            "message": "Curcuma, gengibre e canela tem propriedades anti-inflamatorias. Use como tempero para reduzir o sal e ganhar saude.",
            "references": [{"source": "PubMed", "title": "Spices and Health", "url": "https://pubmed.ncbi.nlm.nih.gov/"}]
        },
        {
            "type": "vitamin_tip", "title": "Sono e Alimentacao", "icon": "sun", "priority": "low",
            "message": "Dormir mal aumenta a fome e a vontade de comer doces. Tente jantar leve e evitar cafeina apos as 15h.",
            "references": [{"source": "Harvard", "title": "Sleep and health", "url": "https://www.hsph.harvard.edu/nutritionsource/sleep/"}]
        },
    ]
    
    # Rotacao por dia do ano (nunca repete no mesmo dia)
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    idx = day_of_year % len(DICAS_POOL)
    
    dica = DICAS_POOL[idx]
    return {
        "type": dica["type"],
        "title": dica["title"],
        "message": dica["message"],
        "icon": dica["icon"],
        "priority": dica["priority"],
        "references": dica["references"],
        "dishes_context": []
    }
