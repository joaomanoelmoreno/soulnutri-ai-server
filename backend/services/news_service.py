# -*- coding: utf-8 -*-
"""
SoulNutri - Servico de Noticias e Curiosidades Nutricionais
Gera conteudo educativo verificado com fontes confiaveis.
"""
import os
import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Fontes confiaveis aprovadas
TRUSTED_SOURCES = {
    "saude_oficial": ["WHO (OMS)", "FDA", "ANVISA", "Ministerio da Saude (Brasil)", "EMA (Europa)", "NHS (UK)"],
    "ciencia_medica": ["The Lancet", "NEJM", "Nature", "PubMed", "BMJ", "JAMA", "Nutrients Journal", "American Journal of Clinical Nutrition"],
    "midia_premium": ["BBC", "CNN", "Reuters", "Estadao", "UOL", "VEJA", "SuperInteressante", "National Geographic", "The Guardian", "El Pais", "Deutsche Welle"],
    "nutricao": ["Harvard T.H. Chan School of Public Health", "Mayo Clinic", "Cleveland Clinic", "Sociedade Brasileira de Nutricao", "Academy of Nutrition and Dietetics"]
}

BLOCKED_SOURCES = ["Fox News", "Breitbart", "InfoWars", "Facebook", "Twitter/X", "Instagram", "TikTok", "Reddit", "WhatsApp", "Telegram"]

CATEGORIES = [
    {"id": "curiosidade", "label": "Curiosidade", "icon": "lightbulb", "color": "#f59e0b"},
    {"id": "alerta", "label": "Alerta de Saude", "icon": "alert-triangle", "color": "#ef4444"},
    {"id": "dica", "label": "Dica Pratica", "icon": "heart", "color": "#22c55e"},
    {"id": "ciencia", "label": "Ciencia", "icon": "flask-conical", "color": "#6366f1"},
    {"id": "tendencia", "label": "Tendencia", "icon": "trending-up", "color": "#06b6d4"},
    {"id": "mito_vs_fato", "label": "Mito vs Fato", "icon": "scale", "color": "#ec4899"}
]

TONES = ["otimista", "realista"]


def _get_db():
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
    import pymongo
    client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
    return client[os.environ.get("DB_NAME", "soulnutri")]


async def generate_news_batch(count: int = 6) -> list:
    """
    Gera um lote de noticias/curiosidades nutricionais usando IA.
    Balanceia entre categorias e tons (otimista/realista).
    Verifica fontes antes de publicar.
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return []
    
    fontes_str = "\n".join([
        f"- {cat}: {', '.join(fontes)}" 
        for cat, fontes in TRUSTED_SOURCES.items()
    ])
    
    bloqueadas_str = ", ".join(BLOCKED_SOURCES)
    
    prompt = f"""Voce e um jornalista cientifico especializado em nutricao e saude alimentar.

TAREFA: Gere exatamente {count} noticias/curiosidades nutricionais VERIFICAVEIS e REAIS.

REGRAS CRITICAS:
1. Cada item DEVE ser baseado em informacao REAL e VERIFICAVEL
2. Cite a FONTE ORIGINAL (estudo, organizacao ou midia confiavel)
3. Inclua o ANO da publicacao/descoberta quando possivel
4. Alterne entre tons OTIMISTAS (beneficios, descobertas positivas) e REALISTAS (alertas, riscos, desmistificacoes)
5. NAO invente dados, porcentagens ou estudos
6. Se nao tem certeza de um fato, NAO inclua
7. Verifique se a informacao NAO e fake news antes de incluir

FONTES CONFIAVEIS (use APENAS estas):
{fontes_str}

FONTES BLOQUEADAS (NUNCA cite):
{bloqueadas_str}

CATEGORIAS (distribua igualmente):
- curiosidade: Fatos surpreendentes sobre alimentos
- alerta: Alertas de saude baseados em evidencia
- dica: Dicas praticas de nutricao
- ciencia: Descobertas cientificas recentes
- tendencia: Tendencias em alimentacao saudavel
- mito_vs_fato: Desmistificacao de crencas populares

Retorne APENAS um JSON valido com esta estrutura:
{{
  "items": [
    {{
      "titulo": "Titulo conciso e atrativo (max 80 chars)",
      "resumo": "Resumo informativo em 2-3 frases (max 200 chars)",
      "conteudo": "Texto completo com detalhes, dados e contexto (200-400 chars)",
      "categoria": "curiosidade|alerta|dica|ciencia|tendencia|mito_vs_fato",
      "tom": "otimista|realista",
      "fonte_nome": "Nome da fonte (ex: Harvard Health, WHO, The Lancet)",
      "fonte_ano": "2024 ou 2025",
      "fonte_url_referencia": "URL de referencia ou descricao do estudo",
      "verificado": true,
      "nivel_confianca": "alto|medio",
      "tags": ["nutriente", "alimento", "saude"],
      "relevancia_brasil": true
    }}
  ]
}}"""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"news-gen-{int(datetime.now().timestamp())}",
            system_message="Voce e um verificador de fatos e jornalista cientifico. Retorne APENAS JSON valido."
        ).with_model("gemini", "gemini-2.0-flash")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse response
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        if clean.endswith("```"):
            clean = clean[:-3]
        
        data = json.loads(clean.strip())
        items = data.get("items", [])
        
        # Verificar e salvar cada item
        db = _get_db()
        saved = []
        
        for item in items:
            # Gerar ID unico
            content_hash = hashlib.md5(item.get("titulo", "").encode()).hexdigest()[:12]
            
            # Verificar se ja existe
            existing = db.nutrition_news.find_one({"content_hash": content_hash})
            if existing:
                continue
            
            # Verificacao basica de qualidade
            if not item.get("fonte_nome") or item.get("nivel_confianca") == "baixo":
                logger.warning(f"[NEWS] Descartado por baixa confianca: {item.get('titulo', '')[:50]}")
                continue
            
            # Verificar se a fonte nao esta na lista bloqueada
            fonte = item.get("fonte_nome", "").lower()
            is_blocked = any(b.lower() in fonte for b in BLOCKED_SOURCES)
            if is_blocked:
                logger.warning(f"[NEWS] Fonte bloqueada: {fonte}")
                continue
            
            news_doc = {
                "titulo": item.get("titulo", ""),
                "resumo": item.get("resumo", ""),
                "conteudo": item.get("conteudo", ""),
                "categoria": item.get("categoria", "curiosidade"),
                "tom": item.get("tom", "otimista"),
                "fonte_nome": item.get("fonte_nome", ""),
                "fonte_ano": item.get("fonte_ano", ""),
                "fonte_url": item.get("fonte_url_referencia", ""),
                "verificado": item.get("verificado", False),
                "nivel_confianca": item.get("nivel_confianca", "medio"),
                "tags": item.get("tags", []),
                "relevancia_brasil": item.get("relevancia_brasil", True),
                "content_hash": content_hash,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "published",
                "likes": 0,
                "views": 0
            }
            
            db.nutrition_news.insert_one(news_doc)
            news_doc.pop("_id", None)
            saved.append(news_doc)
            logger.info(f"[NEWS] Publicado: {news_doc['titulo'][:50]}...")
        
        return saved
        
    except Exception as e:
        logger.error(f"[NEWS] Erro ao gerar noticias: {e}")
        return []


async def verify_single_news(titulo: str, conteudo: str, fonte: str) -> dict:
    """
    Verifica se uma noticia especifica e confiavel usando IA.
    """
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return {"verificado": False, "motivo": "Chave AI nao disponivel"}
    
    prompt = f"""Analise a seguinte informacao nutricional e verifique sua veracidade:

TITULO: {titulo}
CONTEUDO: {conteudo}
FONTE CITADA: {fonte}

Responda em JSON:
{{
  "verificado": true/false,
  "nivel_confianca": "alto|medio|baixo",
  "motivo": "Explicacao breve",
  "fonte_confiavel": true/false,
  "possivel_fake_news": true/false,
  "sugestao_correcao": "Se necessario, como corrigir"
}}"""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"verify-{int(datetime.now().timestamp())}",
            system_message="Voce e um verificador de fatos especializado em nutricao. Seja rigoroso."
        ).with_model("gemini", "gemini-2.0-flash-lite")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        if clean.endswith("```"):
            clean = clean[:-3]
        
        return json.loads(clean.strip())
    except Exception as e:
        logger.error(f"[NEWS] Erro ao verificar: {e}")
        return {"verificado": False, "motivo": str(e)}


def get_news_feed(limit: int = 20, categoria: str = None, skip: int = 0) -> list:
    """Retorna o feed de noticias do MongoDB."""
    db = _get_db()
    
    query = {"status": "published"}
    if categoria:
        query["categoria"] = categoria
    
    cursor = db.nutrition_news.find(
        query, 
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    return list(cursor)


def get_news_stats() -> dict:
    """Retorna estatisticas do feed de noticias."""
    db = _get_db()
    
    total = db.nutrition_news.count_documents({"status": "published"})
    
    by_category = {}
    for cat in CATEGORIES:
        count = db.nutrition_news.count_documents({"status": "published", "categoria": cat["id"]})
        by_category[cat["id"]] = count
    
    by_tone = {
        "otimista": db.nutrition_news.count_documents({"status": "published", "tom": "otimista"}),
        "realista": db.nutrition_news.count_documents({"status": "published", "tom": "realista"})
    }
    
    return {
        "total": total,
        "by_category": by_category,
        "by_tone": by_tone,
        "categories": CATEGORIES
    }


def increment_news_view(content_hash: str):
    """Incrementa o contador de visualizacoes."""
    db = _get_db()
    db.nutrition_news.update_one(
        {"content_hash": content_hash},
        {"$inc": {"views": 1}}
    )


def toggle_news_like(content_hash: str) -> int:
    """Incrementa likes de uma noticia."""
    db = _get_db()
    result = db.nutrition_news.find_one_and_update(
        {"content_hash": content_hash},
        {"$inc": {"likes": 1}},
        return_document=True,
        projection={"_id": 0, "likes": 1}
    )
    return result.get("likes", 0) if result else 0
