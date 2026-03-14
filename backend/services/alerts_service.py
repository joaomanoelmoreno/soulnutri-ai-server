# -*- coding: utf-8 -*-
"""
SERVICO DE ALERTAS E COMBINACOES - SoulNutri Premium
Gera alertas baseados em noticias recentes + consumo pessoal,
e sugestoes de combinacoes beneficas entre alimentos.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

FONTES_CONFIAVEIS = [
    "ANVISA", "OMS (Organizacao Mundial da Saude)", "Ministerio da Saude",
    "UNICAMP/NEPA", "USP", "Harvard Medical School", "Nature",
    "The Lancet", "British Medical Journal", "FDA",
    "Embrapa", "Fiocruz", "IBGE"
]


async def generate_food_alert(nome: str, ingredientes: list, db=None, user_nome: str = None) -> dict:
    """
    Gera alertas para um prato:
    1. Alertas de noticias/ciencia (info recente sobre ingredientes)
    2. Alertas de consumo pessoal (se usuario premium fornecido)
    """
    if not EMERGENT_LLM_KEY:
        return None

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        ingredientes_texto = ", ".join(ingredientes) if ingredientes else nome

        prompt = (
            f"Prato: {nome}\n"
            f"Ingredientes: {ingredientes_texto}\n\n"
            "Gere informacoes uteis sobre este prato. Responda em JSON puro:\n"
            "{\n"
            '  "alerta_breve": "frase curta de 10-15 palavras sobre algo relevante deste prato (beneficio ou cuidado)",\n'
            '  "alerta_detalhado": "explicacao completa com 2-3 paragrafos sobre o alerta, citando estudos",\n'
            '  "tipo_alerta": "beneficio" ou "cuidado" ou "neutro",\n'
            '  "fonte": "nome da fonte cientifica real",\n'
            '  "combinacoes": [\n'
            '    {"com": "nome do alimento", "beneficio": "explicacao de por que combinam bem", "nutriente": "qual nutriente e potencializado"}\n'
            '  ],\n'
            '  "voce_sabia": "curiosidade cientifica interessante sobre um dos ingredientes",\n'
            '  "dica_chef": "dica pratica de como aproveitar melhor este prato"\n'
            "}\n"
            "Use APENAS fontes reais e confiaveis. Nao invente estudos.\n"
            "Sem markdown, sem crases, apenas JSON valido."
        )

        llm = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"alert-{nome[:20]}-{datetime.now().strftime('%H%M')}",
            system_message=(
                "Voce e um nutricionista cientifico brasileiro. "
                "Cite APENAS fontes reais e confiaveis: " + ", ".join(FONTES_CONFIAVEIS[:6]) + ". "
                "Responda APENAS JSON puro sem markdown."
            ),
        )
        llm = llm.with_model("gemini", "gemini-2.0-flash-lite")
        response = await llm.send_message(UserMessage(text=prompt))

        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]
        if text.startswith("json"):
            text = text[4:]

        alert_data = json.loads(text.strip())

        # Adicionar alerta de consumo pessoal se tiver usuario
        consumption_alert = None
        if db is not None and user_nome:
            consumption_alert = await _check_consumption_alert(
                db, user_nome, nome, ingredientes
            )

        return {
            "alerta_breve": alert_data.get("alerta_breve", ""),
            "alerta_detalhado": alert_data.get("alerta_detalhado", ""),
            "tipo_alerta": alert_data.get("tipo_alerta", "neutro"),
            "fonte": alert_data.get("fonte", ""),
            "combinacoes": alert_data.get("combinacoes", []),
            "voce_sabia": alert_data.get("voce_sabia", ""),
            "dica_chef": alert_data.get("dica_chef", ""),
            "alerta_consumo": consumption_alert,
        }

    except Exception as e:
        logger.error(f"[ALERT] Erro para {nome}: {e}")
        return None


async def _check_consumption_alert(db, user_nome: str, prato_nome: str, ingredientes: list) -> dict:
    """
    Verifica o consumo recente do usuario e gera alertas inteligentes.
    """
    try:
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

        cursor = db.meal_logs.find({
            "user_nome": {"$regex": f"^{user_nome}$", "$options": "i"},
            "timestamp": {"$gte": seven_days_ago}
        }, {"_id": 0}).sort("timestamp", -1)

        meals = await cursor.to_list(length=100)

        if not meals:
            return None

        user = await db.premium_users.find_one(
            {"nome": {"$regex": f"^{user_nome}$", "$options": "i"}},
            {"_id": 0, "meta_calorica": 1, "perfil": 1}
        )
        meta_calorica_semanal = (user.get("meta_calorica", 2000) if user else 2000) * 7

        total_calorias = 0
        ingredientes_frequentes = {}

        for meal in meals:
            cal = meal.get("calorias_num", 0)
            if isinstance(cal, str):
                try:
                    cal = float(cal.replace("kcal", "").replace("~", "").strip())
                except:
                    cal = 0
            total_calorias += cal

            for ing in meal.get("ingredientes", []):
                ing_lower = ing.lower().strip()
                ingredientes_frequentes[ing_lower] = ingredientes_frequentes.get(ing_lower, 0) + 1

        nutri_sheet = await db.nutrition_sheets.find_one(
            {"nome": {"$regex": f"^{prato_nome}$", "$options": "i"}},
            {"_id": 0, "calorias_kcal": 1, "sodio_mg": 1, "gorduras_g": 1}
        )

        cal_prato = nutri_sheet.get("calorias_kcal", 0) if nutri_sheet else 0
        alerts = []

        pct_meta = (total_calorias / meta_calorica_semanal * 100) if meta_calorica_semanal > 0 else 0
        if pct_meta > 85 and cal_prato > 200:
            alerts.append({
                "tipo": "calorias",
                "icone": "🔥",
                "texto": f"Voce ja consumiu {total_calorias:.0f} kcal esta semana ({pct_meta:.0f}% da meta). Este prato tem {cal_prato:.0f} kcal."
            })

        for ing in ingredientes:
            ing_lower = ing.lower().strip()
            freq = ingredientes_frequentes.get(ing_lower, 0)
            if freq >= 4:
                alerts.append({
                    "tipo": "repeticao",
                    "icone": "🔄",
                    "texto": f"Voce ja consumiu '{ing}' {freq}x esta semana. Que tal variar?"
                })

        if nutri_sheet and nutri_sheet.get("sodio_mg", 0) > 400:
            alerts.append({
                "tipo": "sodio",
                "icone": "🧂",
                "texto": f"Este prato tem {nutri_sheet['sodio_mg']:.0f}mg de sodio (alto). Atencao se tem restricao."
            })

        if not alerts:
            return None

        return {"alerts": alerts, "total_calorias_semana": total_calorias, "meta_semanal": meta_calorica_semanal, "refeicoes_semana": len(meals)}

    except Exception as e:
        logger.error(f"[CONSUMPTION-ALERT] Erro: {e}")
        return None


async def generate_weekly_report(db, user_nome: str) -> dict:
    """Gera relatorio semanal de consumo com motivacional."""
    try:
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

        cursor = db.meal_logs.find({
            "user_nome": {"$regex": f"^{user_nome}$", "$options": "i"},
            "timestamp": {"$gte": seven_days_ago}
        }, {"_id": 0}).sort("timestamp", -1)
        meals = await cursor.to_list(length=200)

        if not meals:
            return {"ok": False, "message": "Nenhuma refeicao registrada esta semana"}

        user = await db.premium_users.find_one(
            {"nome": {"$regex": f"^{user_nome}$", "$options": "i"}},
            {"_id": 0, "meta_calorica": 1, "nome": 1, "perfil": 1}
        )
        meta_diaria = user.get("meta_calorica", 2000) if user else 2000

        dias = {}
        total_cal = 0
        total_prot = 0
        total_carb = 0
        total_gord = 0
        total_fibra = 0
        pratos_consumidos = []
        categorias = {}

        for meal in meals:
            dia = meal.get("timestamp", "")[:10]
            if dia not in dias:
                dias[dia] = {"calorias": 0, "refeicoes": 0, "pratos": []}

            cal = meal.get("calorias_num", 0)
            if isinstance(cal, str):
                try:
                    cal = float(cal.replace("kcal", "").replace("~", "").strip())
                except:
                    cal = 0

            dias[dia]["calorias"] += cal
            dias[dia]["refeicoes"] += 1
            dias[dia]["pratos"].append(meal.get("prato_nome", ""))

            total_cal += cal
            pratos_consumidos.append(meal.get("prato_nome", ""))

            cat = meal.get("categoria", "outro")
            categorias[cat] = categorias.get(cat, 0) + 1

            prato = meal.get("prato_nome", "")
            if prato:
                nutri = await db.nutrition_sheets.find_one(
                    {"nome": {"$regex": f"^{prato}$", "$options": "i"}},
                    {"_id": 0, "proteinas_g": 1, "carboidratos_g": 1, "gorduras_g": 1, "fibras_g": 1}
                )
                if nutri:
                    total_prot += nutri.get("proteinas_g", 0)
                    total_carb += nutri.get("carboidratos_g", 0)
                    total_gord += nutri.get("gorduras_g", 0)
                    total_fibra += nutri.get("fibras_g", 0)

        num_dias = len(dias)
        media_cal_dia = total_cal / num_dias if num_dias > 0 else 0
        pct_meta = (media_cal_dia / meta_diaria * 100) if meta_diaria > 0 else 0

        motivacional = _generate_motivacional(pct_meta, total_fibra, len(meals), categorias)

        return {
            "ok": True,
            "periodo": f"{num_dias} dias",
            "total_refeicoes": len(meals),
            "resumo": {
                "calorias_total": round(total_cal, 0),
                "calorias_media_dia": round(media_cal_dia, 0),
                "meta_diaria": meta_diaria,
                "pct_meta": round(pct_meta, 1),
                "proteinas_total": round(total_prot, 1),
                "carboidratos_total": round(total_carb, 1),
                "gorduras_total": round(total_gord, 1),
                "fibras_total": round(total_fibra, 1),
            },
            "por_dia": {dia: info for dia, info in sorted(dias.items())},
            "categorias": categorias,
            "pratos_mais_consumidos": _top_items(pratos_consumidos, 5),
            "motivacional": motivacional,
        }

    except Exception as e:
        logger.error(f"[WEEKLY-REPORT] Erro: {e}")
        return {"ok": False, "error": str(e)}


def _generate_motivacional(pct_meta: float, fibras: float, refeicoes: int, categorias: dict) -> dict:
    """Gera mensagem motivacional baseada no desempenho."""
    messages = []
    score = 0

    if 85 <= pct_meta <= 110:
        messages.append("Parabens! Voce manteve suas calorias dentro da meta!")
        score += 3
    elif pct_meta < 85:
        messages.append(f"Voce consumiu {pct_meta:.0f}% da sua meta calorica. Fique atento para nao comer de menos!")
        score += 1
    else:
        messages.append(f"Voce ultrapassou sua meta em {pct_meta - 100:.0f}%. Tente equilibrar nos proximos dias!")

    meta_fibra_semanal = 25 * 7
    if fibras >= meta_fibra_semanal * 0.8:
        messages.append("Otimo consumo de fibras! Seu intestino agradece!")
        score += 2
    elif fibras > 0:
        messages.append(f"Fibras: {fibras:.0f}g consumidas. Tente incluir mais legumes e graos integrais!")
        score += 1

    vegano = categorias.get("vegano", 0)
    animal = categorias.get("proteina animal", categorias.get("proteína animal", 0))
    if vegano > 0 and animal > 0:
        messages.append("Bom equilibrio entre proteinas vegetais e animais!")
        score += 2

    if refeicoes >= 14:
        messages.append("Voce registrou muitas refeicoes! Consistencia e a chave!")
        score += 2

    if score >= 7:
        emoji, titulo = "🏆", "Semana Excelente!"
    elif score >= 4:
        emoji, titulo = "👍", "Boa semana!"
    else:
        emoji, titulo = "💪", "Continue melhorando!"

    return {"emoji": emoji, "titulo": titulo, "mensagens": messages, "score": score}


def _top_items(items: list, n: int) -> list:
    freq = {}
    for item in items:
        if item:
            freq[item] = freq.get(item, 0) + 1
    return sorted(freq.items(), key=lambda x: -x[1])[:n]
