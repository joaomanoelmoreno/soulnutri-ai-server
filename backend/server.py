"""
SoulNutri AI Server
====================
Sistema inteligente de identificação de pratos.
Analogia: Como o Waze para alimentação - mostra o melhor caminho em 100ms.

Endpoints:
- GET  /api/health          - Status do servidor
- GET  /api/ai/status       - Status do índice de IA
- POST /api/ai/reindex      - Reconstrói o índice
- POST /api/ai/identify     - Identifica um prato por imagem
"""

from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import time
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List

# Carregar configurações
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'soulnutri')]

# FastAPI app
app = FastAPI(
    title="SoulNutri AI Server",
    description="Sistema inteligente de identificação de pratos - Como o Waze para alimentação",
    version="1.0.0"
)

# Router com prefixo /api
api_router = APIRouter(prefix="/api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# MODELS
# =====================

class NutritionInfo(BaseModel):
    calorias: str
    proteinas: str
    carboidratos: str
    gorduras: str

class IdentifyResponse(BaseModel):
    ok: bool
    identified: bool
    dish: Optional[str] = None
    dish_display: Optional[str] = None
    confidence: str
    score: float
    message: str
    category: Optional[str] = None
    category_emoji: Optional[str] = None
    nutrition: Optional[NutritionInfo] = None
    descricao: Optional[str] = None
    ingredientes: Optional[List[str]] = None
    tecnica: Optional[str] = None
    beneficios: Optional[List[str]] = None
    riscos: Optional[List[str]] = None
    aviso_cibi_sana: Optional[str] = None
    alternatives: List[str] = []
    search_time_ms: Optional[float] = None
    source: Optional[str] = "local_index"  # "local_index" ou "generic_ai"
    # Novos campos científicos
    beneficio_principal: Optional[str] = None
    curiosidade_cientifica: Optional[str] = None
    referencia_pesquisa: Optional[str] = None
    alerta_saude: Optional[str] = None

class ReindexResponse(BaseModel):
    ok: bool
    total_dishes: int
    total_images: int
    elapsed_seconds: float

class StatusResponse(BaseModel):
    ok: bool
    ready: bool
    total_dishes: int
    total_embeddings: int
    message: str

# =====================
# ENDPOINTS
# =====================

@api_router.get("/")
async def root():
    return {
        "message": "SoulNutri AI Server",
        "version": "1.0.0",
        "description": "Como o Waze para alimentação - mostra o melhor caminho em tempo real"
    }

@api_router.get("/health")
async def health():
    """Health check do servidor"""
    return {"ok": True, "service": "SoulNutri AI Server"}

@api_router.get("/ai/status", response_model=StatusResponse)
async def ai_status():
    """Status do índice de IA"""
    try:
        from ai.index import get_index
        index = get_index()
        stats = index.get_stats()
        
        return StatusResponse(
            ok=True,
            ready=stats['ready'],
            total_dishes=stats['total_dishes'],
            total_embeddings=stats['total_embeddings'],
            message="Índice pronto para buscas" if stats['ready'] else "Índice não carregado. Execute /ai/reindex"
        )
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        return StatusResponse(
            ok=False,
            ready=False,
            total_dishes=0,
            total_embeddings=0,
            message=str(e)
        )

@api_router.post("/ai/reindex")
async def reindex(max_per_dish: int = 10):
    """
    Reconstrói o índice de embeddings.
    
    Args:
        max_per_dish: Máximo de imagens por prato (default: 10)
    """
    try:
        from ai.index import get_index
        
        logger.info("Iniciando reindexação...")
        index = get_index()
        stats = index.build_index(max_per_dish=max_per_dish)
        
        if 'error' in stats:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": stats['error']}
            )
        
        return {
            "ok": True,
            "total_dishes": stats['total_dishes'],
            "total_images": stats['total_images'],
            "elapsed_seconds": stats['elapsed_seconds'],
            "message": f"Índice reconstruído com {stats['total_dishes']} pratos"
        }
        
    except Exception as e:
        logger.error(f"Erro na reindexação: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )

@api_router.post("/ai/identify")
async def identify_image(
    file: UploadFile = File(...),
    pin: Optional[str] = Form(None),
    nome: Optional[str] = Form(None)
):
    """
    Identifica um prato a partir de uma imagem.
    Se PIN e nome forem fornecidos, retorna dados Premium.
    
    Returns:
        IdentifyResponse com o prato identificado e nível de confiança
    """
    start_time = time.time()
    
    try:
        from ai.index import get_index
        from ai.policy import analyze_result
        from services.cache_service import get_cached_result, cache_result
        
        # Verificar se índice está pronto
        index = get_index()
        if not index.is_ready():
            return IdentifyResponse(
                ok=False,
                identified=False,
                confidence="baixa",
                score=0.0,
                message="Índice não carregado. Execute /api/ai/reindex primeiro."
            )
        
        # Ler imagem
        content = await file.read()
        
        if len(content) == 0:
            return IdentifyResponse(
                ok=False,
                identified=False,
                confidence="baixa",
                score=0.0,
                message="Arquivo de imagem vazio"
            )
        
        # ═══════════════════════════════════════════════════════════════════════
        # CACHE: Verificar se já identificamos esta imagem antes
        # ═══════════════════════════════════════════════════════════════════════
        cached = get_cached_result(content)
        if cached:
            elapsed_ms = (time.time() - start_time) * 1000
            cached['search_time_ms'] = round(elapsed_ms, 2)
            logger.info(f"[CACHE] ⚡ Resposta do cache em {elapsed_ms:.0f}ms")
            return cached
        
        # ═══════════════════════════════════════════════════════════════════════
        # SISTEMA DE IDENTIFICAÇÃO EM CASCATA
        # ═══════════════════════════════════════════════════════════════════════
        # 0. CACHE: Verifica se imagem já foi identificada (~0ms)
        # 1. NÍVEL 1: Índice Local (OpenCLIP) - Parceiros cadastrados (~200-300ms)
        # 1.5 NÍVEL 1.5: YOLOv8 Local - Se disponível (~50-100ms)
        # 2. NÍVEL 2: Gemini Vision - Fallback universal (~3-4s)
        # ═══════════════════════════════════════════════════════════════════════
        
        # ─────────────────────────────────────────────────────────────────────
        # NÍVEL 1: Índice Local (OpenCLIP)
        # ─────────────────────────────────────────────────────────────────────
        results = index.search(content, top_k=5)
        decision = analyze_result(results)
        
        nivel1_score = decision.get('score', 0.0)
        nivel1_confidence = decision.get('confidence', 'baixa')
        
        logger.info(f"[NÍVEL 1] OpenCLIP: {decision.get('dish_display', 'N/A')} - {nivel1_confidence} ({nivel1_score:.2%})")
        
        # ═══════════════════════════════════════════════════════════════════════
        # OTIMIZAÇÃO: Threshold 90% para pratos cadastrados (velocidade!)
        # Para pratos do Cibi Sana, 90% já é confiança suficiente
        # ═══════════════════════════════════════════════════════════════════════
        THRESHOLD_LOCAL = 0.90  # 90% para resposta rápida em pratos conhecidos
        
        # Se confiança >= 90% no Nível 1, usar resultado direto (RÁPIDO!)
        if nivel1_score >= THRESHOLD_LOCAL and decision.get('identified'):
            decision['source'] = 'local_index'
            decision['cascade_level'] = 1
            logger.info(f"[CASCATA] ⚡ Resultado RÁPIDO do Nível 1 ({nivel1_score:.0%})")
        
        # ─────────────────────────────────────────────────────────────────────
        # NÍVEL 2: Gemini Vision (Fallback para pratos não cadastrados)
        # NOTA: YOLOv8 desabilitado temporariamente - será reativado com fotos reais do CibiSana
        # ─────────────────────────────────────────────────────────────────────
        elif nivel1_score < THRESHOLD_LOCAL:
            try:
                from services.generic_ai import identify_unknown_dish
                
                logger.info(f"[NÍVEL 2] Consultando Gemini Vision...")
                generic_result = await identify_unknown_dish(content)
                
                if generic_result.get('ok') and generic_result.get('nome'):
                    decision = {
                        'identified': True,
                        'dish': 'unknown_' + generic_result.get('nome', '').lower().replace(' ', '_'),
                        'dish_display': generic_result.get('nome', 'Prato Desconhecido'),
                        'confidence': generic_result.get('confianca', 'média'),
                        'score': generic_result.get('score', 0.7),
                        'message': f"Identificado: {generic_result.get('nome')}",
                        'category': generic_result.get('categoria', 'outros'),
                        'category_emoji': generic_result.get('category_emoji', '🍽️'),
                        'descricao': generic_result.get('descricao', ''),
                        'ingredientes': generic_result.get('ingredientes_provaveis', []),
                        'tecnica': generic_result.get('tecnica_preparo', ''),
                        'beneficios': generic_result.get('beneficios', []),
                        'riscos': generic_result.get('riscos', []),
                        'alternatives': generic_result.get('alternativas', []),
                        'nutrition': {
                            'calorias': '~200 kcal',
                            'proteinas': '~10g',
                            'carboidratos': '~25g',
                            'gorduras': '~8g'
                        },
                        'aviso_cibi_sana': None,
                        'source': 'generic_ai',
                        'cascade_level': 2,
                        # Dados científicos da IA genérica
                        'beneficio_principal': generic_result.get('beneficio_principal'),
                        'curiosidade_cientifica': generic_result.get('curiosidade_cientifica'),
                        'referencia_pesquisa': generic_result.get('referencia_pesquisa'),
                        'alerta_saude': generic_result.get('alerta_saude')
                    }
                    logger.info(f"[CASCATA] Resultado do Gemini Vision")
            except Exception as e:
                logger.warning(f"[NÍVEL 2] Erro no Gemini: {e}")
        
        # Calcular tempo total
        elapsed_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Identificação: {decision.get('dish')} ({decision.get('confidence')}) em {elapsed_ms:.0f}ms")
        
        # ═══════════════════════════════════════════════════════════════════════
        # VERIFICAR SE É USUÁRIO PREMIUM
        # ═══════════════════════════════════════════════════════════════════════
        is_premium = False
        user_profile = None
        premium_data = {}
        
        if pin and nome:
            from services.profile_service import hash_pin
            pin_hash = hash_pin(pin)
            user_profile = await db.users.find_one(
                {"pin_hash": pin_hash, "nome": {"$regex": f"^{nome}$", "$options": "i"}},
                {"_id": 0}
            )
            is_premium = user_profile is not None
            
            if is_premium:
                logger.info(f"[PREMIUM] Usuário {nome} identificado")
        
        # Buscar dados científicos do MongoDB (APENAS PARA PREMIUM)
        scientific_data = {}
        dish_slug = decision.get('dish')
        if dish_slug and decision.get('source') != 'generic_ai':
            # Normalizar slug para busca
            slug_normalized = dish_slug.lower().replace('_', '').replace('-', '').replace(' ', '')
            mongo_dish = await db.dishes.find_one(
                {'$or': [
                    {'slug': slug_normalized},
                    {'slug': dish_slug}
                ]},
                {'_id': 0, 'beneficio_principal': 1, 'curiosidade_cientifica': 1, 
                 'referencia_pesquisa': 1, 'alerta_saude': 1}
            )
            if mongo_dish and is_premium:
                scientific_data = mongo_dish
                logger.info(f"[PREMIUM] Dados científicos liberados para {dish_slug}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # ALERTAS PREMIUM EM TEMPO REAL
        # ═══════════════════════════════════════════════════════════════════════
        if is_premium and user_profile:
            try:
                from services.alerts_service import (
                    gerar_alertas_tempo_real,
                    gerar_combinacoes_sugeridas,
                    gerar_substituicoes,
                    verificar_alergenos_perfil
                )
                
                ingredientes = decision.get('ingredientes', [])
                
                # Alertas de alérgenos baseados no perfil
                alertas_alergenos = verificar_alergenos_perfil(user_profile, ingredientes)
                
                # Alertas baseados no histórico semanal
                alertas_historico = await gerar_alertas_tempo_real(
                    db, nome, decision, ingredientes
                )
                
                # Combinações inteligentes
                combinacoes = gerar_combinacoes_sugeridas(ingredientes)
                
                # Substituições saudáveis
                substituicoes = gerar_substituicoes(ingredientes)
                
                premium_data = {
                    "alertas_alergenos": alertas_alergenos,
                    "alertas_historico": alertas_historico,
                    "combinacoes_sugeridas": combinacoes,
                    "substituicoes": substituicoes,
                    "is_premium": True
                }
                
                logger.info(f"[PREMIUM] {len(alertas_alergenos)} alertas de alérgenos, {len(alertas_historico)} alertas de histórico")
                
            except Exception as e:
                logger.error(f"[PREMIUM] Erro ao gerar alertas: {e}")
        
        # Preparar nutrition como objeto
        nutrition_data = decision.get('nutrition')
        nutrition_obj = NutritionInfo(**nutrition_data) if nutrition_data else None
        
        # Montar resposta base
        response_data = {
            "ok": True,
            "identified": decision['identified'],
            "dish": decision.get('dish'),
            "dish_display": decision.get('dish_display'),
            "confidence": decision['confidence'],
            "score": decision['score'],
            "message": decision['message'],
            "category": decision.get('category'),
            "category_emoji": decision.get('category_emoji'),
            "nutrition": nutrition_obj,
            "descricao": decision.get('descricao'),
            "ingredientes": decision.get('ingredientes'),
            "tecnica": decision.get('tecnica'),
            "beneficios": decision.get('beneficios'),
            "riscos": decision.get('riscos'),
            "aviso_cibi_sana": decision.get('aviso_cibi_sana'),
            "alternatives": decision.get('alternatives', []),
            "search_time_ms": round(elapsed_ms, 2),
            "source": decision.get('source', 'local_index'),
            # Dados científicos - SÓ PREMIUM
            "beneficio_principal": scientific_data.get('beneficio_principal') if is_premium else None,
            "curiosidade_cientifica": scientific_data.get('curiosidade_cientifica') if is_premium else None,
            "referencia_pesquisa": scientific_data.get('referencia_pesquisa') if is_premium else None,
            "alerta_saude": scientific_data.get('alerta_saude') if is_premium else None,
            # Dados Premium extras
            "premium": premium_data if is_premium else None,
            "is_premium": is_premium
        }
        
        # ═══════════════════════════════════════════════════════════════════════
        # CACHE: Salvar resultado para futuras consultas
        # ═══════════════════════════════════════════════════════════════════════
        if response_data.get('identified'):
            cache_result(content, response_data, ttl_seconds=3600)  # 1 hora de cache
        
        return response_data
        
    except Exception as e:
        logger.error(f"Erro na identificação: {e}")
        elapsed_ms = (time.time() - start_time) * 1000
        
        return IdentifyResponse(
            ok=False,
            identified=False,
            confidence="baixa",
            score=0.0,
            message=f"Erro ao processar imagem: {str(e)}",
            search_time_ms=round(elapsed_ms, 2)
        )

@api_router.get("/ai/dishes")
async def list_dishes():
    """Lista todos os pratos no índice"""
    try:
        from ai.index import get_index
        from ai.policy import get_dish_name, get_category, get_category_emoji
        
        index = get_index()
        
        dishes = []
        for dish_slug, data in index.metadata.items():
            dishes.append({
                'slug': dish_slug,
                'name': get_dish_name(dish_slug),
                'category': get_category(dish_slug),
                'category_emoji': get_category_emoji(get_category(dish_slug)),
                'image_count': data.get('image_count', 0)
            })
        
        # Ordenar por nome
        dishes.sort(key=lambda x: x['name'])
        
        return {
            "ok": True,
            "total": len(dishes),
            "dishes": dishes
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.post("/ai/learn")
async def learn_new_dish(
    dish_name: str,
    file: UploadFile = File(...)
):
    """
    Cadastra foto de um novo prato para aprendizado.
    
    O prato será adicionado à pasta de datasets e poderá ser
    incorporado ao índice no próximo reindex.
    
    Args:
        dish_name: Nome do prato (será convertido em slug)
        file: Imagem do prato
    """
    import re
    import shutil
    
    try:
        # Converter nome para slug
        slug = dish_name.lower().strip()
        slug = re.sub(r'[^a-z0-9]+', '', slug)
        
        if not slug:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "Nome do prato inválido"}
            )
        
        # Criar diretório se não existir
        dish_dir = f"/app/datasets/organized/{slug}"
        os.makedirs(dish_dir, exist_ok=True)
        
        # Contar imagens existentes
        existing = len([f for f in os.listdir(dish_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        # Salvar nova imagem
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        new_filename = f"{slug}{existing + 1:02d}.{ext}"
        file_path = os.path.join(dish_dir, new_filename)
        
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Nova imagem salva: {file_path}")
        
        return {
            "ok": True,
            "message": f"Imagem do prato '{dish_name}' salva com sucesso!",
            "dish_slug": slug,
            "file_saved": new_filename,
            "total_images": existing + 1,
            "note": "Execute /api/ai/reindex para incorporar ao índice"
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar prato: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.get("/ai/unknown")
async def check_unknown(file: UploadFile = File(...)):
    """
    Verifica se um prato é desconhecido (não está no índice).
    Útil para identificar pratos que precisam ser cadastrados.
    """
    try:
        from ai.index import get_index
        
        index = get_index()
        if not index.is_ready():
            return {"ok": False, "message": "Índice não carregado"}
        
        content = await file.read()
        results = index.search(content, top_k=1)
        
        if results and results[0].get('score', 0) < 0.50:
            return {
                "ok": True,
                "is_unknown": True,
                "best_match": results[0].get('dish'),
                "score": results[0].get('score'),
                "message": "Prato não reconhecido. Considere cadastrá-lo via /api/ai/learn"
            }
        else:
            return {
                "ok": True,
                "is_unknown": False,
                "best_match": results[0].get('dish') if results else None,
                "score": results[0].get('score') if results else 0,
                "message": "Prato reconhecido no índice"
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.get("/ai/dishes")
async def list_dishes():
    """
    Lista todos os pratos disponíveis para seleção no feedback.
    """
    try:
        from ai.policy import DISH_NAMES, DISH_CATEGORIES, get_category_emoji
        
        dishes = []
        for slug, name in sorted(DISH_NAMES.items(), key=lambda x: x[1]):
            category = DISH_CATEGORIES.get(slug, 'outros')
            dishes.append({
                "slug": slug,
                "name": name,
                "category": category,
                "category_emoji": get_category_emoji(category)
            })
        
        return {
            "ok": True,
            "total": len(dishes),
            "dishes": dishes
        }
    except Exception as e:
        logger.error(f"Erro ao listar pratos: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.post("/ai/create-dish")
async def create_new_dish(
    file: UploadFile = File(...),
    dish_name: str = Form("")
):
    """
    Cria um novo prato usando IA para gerar todas as informações.
    Salva a foto e adiciona ao banco de dados.
    """
    try:
        import uuid
        from datetime import datetime
        from services.generic_ai import identify_unknown_dish
        
        if not dish_name.strip():
            return {"ok": False, "error": "Nome do prato é obrigatório"}
        
        content = await file.read()
        
        # Gerar slug
        slug = dish_name.lower().strip()
        slug = ''.join(c for c in slug if c.isalnum() or c == ' ')
        slug = slug.replace(' ', '_')
        
        # Usar IA para gerar informações do prato
        logger.info(f"Gerando informações para novo prato: {dish_name}")
        ai_result = await identify_unknown_dish(content)
        
        # Preparar informações do prato
        dish_info = {
            "nome": dish_name.strip(),
            "slug": slug,
            "categoria": ai_result.get("categoria", "outros"),
            "category_emoji": ai_result.get("category_emoji", "🍽️"),
            "descricao": ai_result.get("descricao", f"{dish_name} - prato cadastrado pelo usuário"),
            "ingredientes": ai_result.get("ingredientes_provaveis", []),
            "beneficios": ai_result.get("beneficios", []),
            "riscos": ai_result.get("riscos", []),
            "tecnica": ai_result.get("tecnica_preparo", ""),
            "nutricao": {
                "calorias": "~200 kcal",
                "proteinas": "~10g",
                "carboidratos": "~25g",
                "gorduras": "~8g"
            },
            "contem_gluten": any("glúten" in r.lower() for r in ai_result.get("riscos", [])),
            "ativo": True,
            "origem": "user_created",
            "created_at": datetime.utcnow()
        }
        
        # Salvar no MongoDB
        await db.dishes.update_one(
            {"slug": slug},
            {"$set": dish_info},
            upsert=True
        )
        
        # Criar diretório e salvar imagem
        dataset_dir = Path("/app/datasets/organized") / slug
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{slug}_{timestamp}_{unique_id}.jpg"
        file_path = dataset_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Novo prato criado: {dish_name} -> {slug}")
        
        return {
            "ok": True,
            "message": f"Prato '{dish_name}' criado com sucesso!",
            "dish_slug": slug,
            "dish_name": dish_name,
            "dish_info": dish_info,
            "file_saved": filename,
            "note": "Execute /api/ai/reindex para incorporar ao índice de busca"
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar prato: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.get("/ai/ingredient-research/{ingredient}")
async def get_ingredient_research(ingredient: str):
    """
    Busca pesquisas científicas recentes sobre um ingrediente.
    Retorna informações da OMS, ANVISA, estudos científicos, etc.
    """
    try:
        from services.generic_ai import search_ingredient_news
        
        logger.info(f"Buscando pesquisas sobre: {ingredient}")
        result = await search_ingredient_news(ingredient)
        
        if "error" in result:
            return {"ok": False, "error": result["error"]}
        
        return {
            "ok": True,
            "ingredient": ingredient,
            **result
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar pesquisa: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/ai/feedback")
async def submit_feedback(
    file: UploadFile = File(...),
    dish_slug: str = Form(""),
    is_correct: str = Form("true"),
    original_dish: str = Form("")
):
    """
    Recebe feedback sobre reconhecimento de prato.
    - Se correto: salva a foto no dataset do prato
    - Se incorreto: salva no prato correto informado pelo usuário
    
    Isso ajuda a melhorar o modelo com o tempo.
    """
    try:
        import uuid
        from datetime import datetime
        
        content = await file.read()
        is_correct_bool = is_correct.lower() == "true"
        
        if not dish_slug:
            return {"ok": False, "message": "dish_slug é obrigatório"}
        
        # Diretório do dataset
        dataset_dir = Path("/app/datasets/organized")
        
        # Normalizar slug
        slug = dish_slug.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        # Encontrar a pasta correta
        target_dir = None
        for folder in dataset_dir.iterdir():
            if folder.is_dir():
                folder_slug = folder.name.lower().replace('_', '').replace('-', '')
                if folder_slug == slug or slug in folder_slug:
                    target_dir = folder
                    break
        
        if not target_dir:
            # Criar pasta se não existir
            target_dir = dataset_dir / slug
            target_dir.mkdir(parents=True, exist_ok=True)
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        feedback_type = "correct" if is_correct_bool else "corrected"
        filename = f"{slug}_{feedback_type}_{timestamp}_{unique_id}.jpg"
        
        # Salvar imagem
        file_path = target_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Log no MongoDB para análise posterior
        feedback_doc = {
            "dish_slug": dish_slug,
            "original_dish": original_dish if not is_correct_bool else dish_slug,
            "is_correct": is_correct_bool,
            "file_path": str(file_path),
            "created_at": datetime.utcnow()
        }
        await db.feedback.insert_one(feedback_doc)
        
        logger.info(f"Feedback salvo: {feedback_type} para {dish_slug} -> {filename}")
        
        return {
            "ok": True,
            "message": f"Feedback registrado! Foto salva em {target_dir.name}",
            "file_saved": filename,
            "is_correct": is_correct_bool,
            "note": "Execute /api/ai/reindex para incorporar ao índice"
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar feedback: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.get("/ai/feedback/stats")
async def get_feedback_stats():
    """
    Retorna estatísticas dos feedbacks recebidos.
    """
    try:
        total = await db.feedback.count_documents({})
        correct = await db.feedback.count_documents({"is_correct": True})
        incorrect = await db.feedback.count_documents({"is_correct": False})
        
        # Pratos mais corrigidos
        pipeline = [
            {"$match": {"is_correct": False}},
            {"$group": {"_id": "$original_dish", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        most_corrected = await db.feedback.aggregate(pipeline).to_list(10)
        
        return {
            "ok": True,
            "total_feedbacks": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy_rate": (correct / total * 100) if total > 0 else 0,
            "most_corrected": most_corrected
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_router.post("/ai/identify-multi")
async def identify_multiple_items(file: UploadFile = File(...)):
    """
    Identifica MÚLTIPLOS itens em uma imagem de refeição.
    Útil para buffets, pratos compostos ou quando há vários alimentos no prato.
    
    Returns:
        Lista de itens identificados com informações nutricionais individuais e totais.
    """
    start_time = time.time()
    
    try:
        from services.generic_ai import identify_multiple_items as identify_multi
        
        content = await file.read()
        
        if len(content) == 0:
            return {"ok": False, "error": "Arquivo de imagem vazio"}
        
        logger.info("[MULTI-ITEM] Iniciando identificação de múltiplos itens...")
        result = await identify_multi(content)
        
        elapsed_ms = (time.time() - start_time) * 1000
        result['search_time_ms'] = round(elapsed_ms, 2)
        
        if result.get('ok'):
            total_itens = result.get('total_itens', 0)
            logger.info(f"[MULTI-ITEM] {total_itens} itens identificados em {elapsed_ms:.0f}ms")
        else:
            logger.warning(f"[MULTI-ITEM] Erro: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro na identificação múltipla: {e}")
        return {
            "ok": False,
            "error": str(e),
            "search_time_ms": round((time.time() - start_time) * 1000, 2)
        }


# ═══════════════════════════════════════════════════════════════════════
# PREMIUM - PERFIL DO USUÁRIO E CONTADOR NUTRICIONAL
# ═══════════════════════════════════════════════════════════════════════

@api_router.post("/premium/register")
async def register_user(
    pin: str = Form(...),
    nome: str = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    idade: int = Form(...),
    sexo: str = Form(...),
    nivel_atividade: str = Form("moderado"),
    objetivo: str = Form("manter"),
    alergias: str = Form(""),
    restricoes: str = Form("")
):
    """
    Registra um novo usuário Premium com PIN local.
    Calcula automaticamente a meta calórica sugerida.
    """
    try:
        from services.profile_service import hash_pin, calcular_tmb, calcular_meta_calorica
        from datetime import datetime, timezone
        
        # Validações
        if len(pin) < 4 or len(pin) > 6:
            return {"ok": False, "error": "PIN deve ter entre 4 e 6 dígitos"}
        
        if not pin.isdigit():
            return {"ok": False, "error": "PIN deve conter apenas números"}
        
        # Calcular meta calórica
        tmb = calcular_tmb(peso, altura, idade, sexo)
        meta_info = calcular_meta_calorica(tmb, nivel_atividade, objetivo)
        
        # Criar perfil
        perfil = {
            "pin_hash": hash_pin(pin),
            "nome": nome,
            "peso": peso,
            "altura": altura,
            "idade": idade,
            "sexo": sexo,
            "nivel_atividade": nivel_atividade,
            "objetivo": objetivo,
            "alergias": [a.strip() for a in alergias.split(",") if a.strip()],
            "restricoes": [r.strip() for r in restricoes.split(",") if r.strip()],
            "meta_calorica": meta_info,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Salvar no MongoDB
        result = await db.users.insert_one(perfil)
        user_id = str(result.inserted_id)
        
        logger.info(f"[PREMIUM] Novo usuário registrado: {nome}")
        
        return {
            "ok": True,
            "user_id": user_id,
            "nome": nome,
            "meta_calorica": meta_info,
            "message": f"Bem-vindo ao SoulNutri Premium, {nome}!"
        }
        
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/premium/login")
async def login_user(pin: str = Form(...), nome: str = Form(...)):
    """
    Login com Nome + PIN.
    """
    try:
        from services.profile_service import hash_pin
        
        pin_hash = hash_pin(pin)
        # Buscar por nome E pin_hash
        user = await db.users.find_one(
            {"pin_hash": pin_hash, "nome": {"$regex": f"^{nome}$", "$options": "i"}},
            {"_id": 0, "pin_hash": 0}
        )
        
        if not user:
            return {"ok": False, "error": "Nome ou PIN incorreto"}
        
        # Buscar consumo do dia
        from datetime import datetime
        hoje = datetime.now().strftime("%Y-%m-%d")
        daily_log = await db.daily_logs.find_one(
            {"user_nome": user["nome"], "data": hoje},
            {"_id": 0}
        )
        
        return {
            "ok": True,
            "user": user,
            "daily_log": daily_log,
            "message": f"Olá, {user['nome']}!"
        }
        
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/premium/log-meal")
async def log_meal(
    pin: str = Form(...),
    prato_nome: str = Form(...),
    calorias: float = Form(...),
    proteinas: float = Form(0),
    carboidratos: float = Form(0),
    gorduras: float = Form(0),
    porcao: str = Form("1 porção")
):
    """
    Registra uma refeição no contador diário.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime, timezone
        
        # Verificar usuário
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        hoje = datetime.now().strftime("%Y-%m-%d")
        agora = datetime.now(timezone.utc)
        
        # Criar entrada do prato
        prato_entry = {
            "nome": prato_nome,
            "calorias": calorias,
            "proteinas": proteinas,
            "carboidratos": carboidratos,
            "gorduras": gorduras,
            "porcao": porcao,
            "hora": agora.strftime("%H:%M")
        }
        
        # Atualizar ou criar log diário
        result = await db.daily_logs.update_one(
            {"user_nome": user["nome"], "data": hoje},
            {
                "$push": {"pratos": prato_entry},
                "$inc": {
                    "calorias_total": calorias,
                    "proteinas_total": proteinas,
                    "carboidratos_total": carboidratos,
                    "gorduras_total": gorduras
                },
                "$setOnInsert": {"created_at": agora}
            },
            upsert=True
        )
        
        # Buscar totais atualizados
        daily_log = await db.daily_logs.find_one(
            {"user_nome": user["nome"], "data": hoje},
            {"_id": 0}
        )
        
        meta = user.get("meta_calorica", {}).get("meta_sugerida", 2000)
        consumido = daily_log.get("calorias_total", 0)
        restante = meta - consumido
        percentual = (consumido / meta) * 100 if meta > 0 else 0
        
        # Gerar alerta se necessário
        alerta = None
        if percentual >= 100:
            alerta = {"tipo": "limite", "mensagem": "🚨 Você atingiu sua meta calórica diária!"}
        elif percentual >= 90:
            alerta = {"tipo": "aviso", "mensagem": f"⚠️ Você está a {restante:.0f} kcal da sua meta!"}
        elif percentual >= 75:
            alerta = {"tipo": "info", "mensagem": f"📊 75% da meta. Restam {restante:.0f} kcal"}
        
        logger.info(f"[PREMIUM] {user['nome']} registrou: {prato_nome} ({calorias} kcal)")
        
        return {
            "ok": True,
            "daily_log": daily_log,
            "meta": meta,
            "consumido": consumido,
            "restante": restante,
            "percentual": round(percentual, 1),
            "alerta": alerta
        }
        
    except Exception as e:
        logger.error(f"Erro ao registrar refeição: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/daily-summary")
async def get_daily_summary(pin: str):
    """
    Retorna resumo do consumo diário.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        hoje = datetime.now().strftime("%Y-%m-%d")
        daily_log = await db.daily_logs.find_one(
            {"user_nome": user["nome"], "data": hoje},
            {"_id": 0}
        )
        
        meta = user.get("meta_calorica", {}).get("meta_sugerida", 2000)
        consumido = daily_log.get("calorias_total", 0) if daily_log else 0
        
        return {
            "ok": True,
            "nome": user["nome"],
            "data": hoje,
            "meta": meta,
            "consumido": consumido,
            "restante": meta - consumido,
            "percentual": round((consumido / meta) * 100, 1) if meta > 0 else 0,
            "pratos": daily_log.get("pratos", []) if daily_log else [],
            "totais": {
                "calorias": consumido,
                "proteinas": daily_log.get("proteinas_total", 0) if daily_log else 0,
                "carboidratos": daily_log.get("carboidratos_total", 0) if daily_log else 0,
                "gorduras": daily_log.get("gorduras_total", 0) if daily_log else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar resumo: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/history")
async def get_history(pin: str, dias: int = 7):
    """
    Retorna histórico de consumo dos últimos X dias.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime, timedelta
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        # Buscar logs dos últimos dias
        data_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
        
        cursor = db.daily_logs.find(
            {"user_nome": user["nome"], "data": {"$gte": data_inicio}},
            {"_id": 0}
        ).sort("data", -1)
        
        historico = await cursor.to_list(length=dias)
        
        # Calcular média
        if historico:
            media_calorias = sum(d.get("calorias_total", 0) for d in historico) / len(historico)
        else:
            media_calorias = 0
        
        return {
            "ok": True,
            "nome": user["nome"],
            "dias": dias,
            "historico": historico,
            "media_calorias": round(media_calorias, 0),
            "meta": user.get("meta_calorica", {}).get("meta_sugerida", 2000)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return {"ok": False, "error": str(e)}


# Incluir router
app.include_router(api_router)

# Evento de shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Evento de startup - pré-carregar modelo
@app.on_event("startup")
async def startup_event():
    logger.info("SoulNutri AI Server iniciando...")
    
    # Pré-carregar o modelo CLIP (importante para performance!)
    try:
        from ai.embedder import preload_model
        preload_model()
        logger.info("Modelo CLIP pré-carregado!")
    except Exception as e:
        logger.warning(f"Não foi possível pré-carregar modelo: {e}")
    
    # Tentar pré-carregar o índice (se existir)
    try:
        from ai.index import get_index
        index = get_index()
        if index.is_ready():
            logger.info(f"Índice carregado: {index.get_stats()}")
        else:
            logger.info("Índice não encontrado. Execute /api/ai/reindex para criar.")
    except Exception as e:
        logger.warning(f"Não foi possível carregar índice: {e}")
    
    logger.info("SoulNutri AI Server pronto!")

@api_router.get("/download/marketing")
async def download_marketing_doc():
    """Download do documento de marketing Premium"""
    from fastapi.responses import FileResponse
    file_path = "/app/backend/SoulNutri_Premium_Marketing.docx"
    return FileResponse(
        path=file_path,
        filename="SoulNutri_Premium_Marketing.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
