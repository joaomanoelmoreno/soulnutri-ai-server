"""
SoulNutri AI Server
====================
Sistema inteligente de identificacao de pratos.
Analogia: Como o Waze para alimentacao - mostra o melhor caminho em 100ms.

Endpoints:
- GET  /health              - Health check para Kubernetes
- GET  /api/health          - Status do servidor
- GET  /api/ai/status       - Status do indice de IA
- POST /api/ai/reindex      - Reconstroi o indice
- POST /api/ai/identify     - Identifica um prato por imagem
"""

# IMPORTANTE: Forcar CPU ANTES de qualquer import que possa carregar PyTorch
import os
import sys
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["CUDA_HOME"] = ""
os.environ["USE_CUDA"] = "0"
os.environ["FORCE_CPU"] = "1"

# Limpar newlines/espacos de TODAS as env vars (problema comum ao colar no Render)
for key in ['MONGO_URL', 'DB_NAME', 'EMERGENT_LLM_KEY', 'GOOGLE_API_KEY', 'CORS_ORIGINS',
            'USDA_API_KEY', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT', 'R2_BUCKET']:
    val = os.environ.get(key)
    if val:
        os.environ[key] = val.replace('\n', '').replace('\r', '').strip()

from datetime import datetime, timedelta, timezone
import json
import asyncio
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form, Request, Query
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import time
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List

# Carregar configuracoes
ROOT_DIR = Path(__file__).resolve().parent
# Garantir que modulos locais (ai/, services/) sejam encontrados
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / '.env')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import re

def format_dish_name(name: str) -> str:
    """Formata nome do prato usando o mapeamento do policy.py.
    Prioriza nomes definidos no DISH_NAMES (que refletem renomeacoes do Admin).
    Se nao encontra, retorna o nome original formatado.
    """
    if not name:
        return name
    
    # Tentar lookup no policy.py (tem os nomes corretos/renomeados)
    try:
        from ai.policy import DISH_NAMES
        slug = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        if slug in DISH_NAMES:
            return DISH_NAMES[slug]
    except Exception:
        pass
    
    # Fallback: retornar o nome original (ja vem formatado do indice)
    return name


def get_confidence_level_message(score: float, confidence: str) -> str:
    """
    Gera mensagem descritiva para o nivel de confianca.
    v1.3: Sistema de 3 niveis com honestidade radical.
    - Alta (>= 90%): Identificacao precisa
    - Media (50-89%): "Parece ser" com alternativas
    - Baixa (< 50%): "Nao reconheco" sem alternativas
    """
    if score >= 0.90 or confidence == 'alta':
        return "Alta confianca - Identificacao precisa"
    elif score >= 0.50 or confidence == 'media':
        return "Media confianca - Verifique se o prato esta correto"
    else:
        return "Baixa confianca - Prato nao reconhecido"


# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
if mongo_url:
    mongo_url = mongo_url.replace('\n', '').replace('\r', '').strip()
if not mongo_url:
    mongo_url = 'mongodb://localhost:27017'
    logger.warning("[MongoDB] MONGO_URL nao definido, usando localhost (apenas para dev)")
client = AsyncIOMotorClient(mongo_url)
db_name = os.environ.get('DB_NAME', 'soulnutri')
db = client[db_name]
logger.info(f"[MongoDB] Conectando a {mongo_url[:30]}... DB: {db_name}")

# FastAPI app
app = FastAPI(
    title="SoulNutri AI Server",
    description="Sistema inteligente de identificacao de pratos - Como o Waze para alimentacao",
    version="1.0.0"
)

# Health check endpoint na RAIZ (para Kubernetes)
@app.get("/health")
async def health_check():
    """Health check para Kubernetes - responde rapidamente"""
    return {"status": "healthy", "service": "soulnutri-backend"}

# Router com prefixo /api
api_router = APIRouter(prefix="/api")

# Função auxiliar de configuração
async def get_setting(key: str):
    """Retorna configuração do banco ou False como default (com cache)"""
    if not hasattr(get_setting, '_cache'):
        get_setting._cache = {}
        get_setting._cache_time = {}
    
    import time as _time
    now = _time.time()
    # Cache por 60 segundos
    if key in get_setting._cache and (now - get_setting._cache_time.get(key, 0)) < 60:
        return get_setting._cache[key]
    
    try:
        doc = await db.settings.find_one({"key": key}, {"_id": 0})
        val = doc.get("value", False) if doc else False
        get_setting._cache[key] = val
        get_setting._cache_time[key] = now
        return val
    except Exception:
        return False

def save_processing_metrics(data: dict):
    """Salva métricas de processamento no banco"""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(db.processing_metrics.insert_one(data))
    except Exception:
        pass

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para controle de cache (produção-ready)
@app.middleware("http")
async def cache_control_middleware(request, call_next):
    response = await call_next(request)
    # HTML nunca deve ser cacheado (garante que o user sempre pega a versão nova)
    # Assets estáticos (JS/CSS) já têm hash no nome (ex: main.abc123.js) e podem ser cacheados
    if response.headers.get("content-type", "").startswith("text/html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # Service Worker nunca deve ser cacheado (garante atualização do PWA)
    if request.url.path.endswith("sw.js") or request.url.path.endswith("manifest.json"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# =====================
# MODELS
# =====================

class NutritionInfo(BaseModel):
    calorias: Optional[str] = None
    proteinas: Optional[str] = None
    carboidratos: Optional[str] = None
    gorduras: Optional[str] = None
    fibras: Optional[str] = None
    sodio: Optional[str] = None
    # Campos precisos da nutrition_sheets (por 100g)
    calorias_kcal: Optional[float] = None
    proteinas_g: Optional[float] = None
    carboidratos_g: Optional[float] = None
    gorduras_g: Optional[float] = None
    fibras_g: Optional[float] = None
    sodio_mg: Optional[float] = None
    calcio_mg: Optional[float] = None
    ferro_mg: Optional[float] = None
    potassio_mg: Optional[float] = None
    zinco_mg: Optional[float] = None
    fonte: Optional[str] = None

class IdentifyResponse(BaseModel):
    ok: bool
    identified: bool
    dish: Optional[str] = None
    dish_display: Optional[str] = None
    confidence: str  # 'alta', 'media', 'baixa'
    confidence_level: Optional[str] = None  # Mensagem descritiva para o usuario
    aviso_confianca: Optional[str] = None  # Aviso baseado no nivel de confianca
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
    source: Optional[str] = "local_index"  # "local_index", "google_vision" ou "generic_ai"
    # Novos campos cientificos
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
        "description": "Como o Waze para alimentacao - mostra o melhor caminho em tempo real"
    }

@api_router.get("/health")
async def health():
    """Health check do servidor"""
    return {"ok": True, "service": "SoulNutri AI Server"}

@api_router.get("/ai/status", response_model=StatusResponse)
async def ai_status():
    """Status do indice de IA"""
    try:
        from ai.index import get_index
        index = get_index()
        stats = index.get_stats()
        
        return StatusResponse(
            ok=True,
            ready=stats['ready'],
            total_dishes=stats['total_dishes'],
            total_embeddings=stats['total_embeddings'],
            message="Índice pronto para buscas" if stats['ready'] else "Índice nao carregado. Execute /ai/reindex"
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


async def lookup_nutrition_sheet(dish_display: str) -> dict:
    """
    Busca ficha nutricional precisa na colecao nutrition_sheets.
    Usa uma unica query $or para evitar round-trips sequenciais.
    """
    if not dish_display:
        return {}
    try:
        sheet = await db.nutrition_sheets.find_one(
            {"$or": [
                {"nome": dish_display},
                {"slug": dish_display},
                {"nomes_alternativos": dish_display},
                {"nome": {"$regex": f"^{dish_display}$", "$options": "i"}}
            ]},
            {"_id": 0}
        )
        if sheet:
            return {
                "calorias_kcal": sheet.get("calorias_kcal"),
                "proteinas_g": sheet.get("proteinas_g"),
                "carboidratos_g": sheet.get("carboidratos_g"),
                "gorduras_g": sheet.get("gorduras_g"),
                "fibras_g": sheet.get("fibras_g"),
                "sodio_mg": sheet.get("sodio_mg"),
                "calcio_mg": sheet.get("calcio_mg"),
                "ferro_mg": sheet.get("ferro_mg"),
                "potassio_mg": sheet.get("potassio_mg"),
                "zinco_mg": sheet.get("zinco_mg"),
                "fonte": sheet.get("fonte_principal", "Ficha Nutricional Cibi Sana"),
            }
    except Exception as e:
        logger.error(f"[NUTRITION] Erro ao buscar ficha: {e}")
    return {}


@api_router.get("/nutrition/list")
async def list_nutrition_sheets():
    """Lista todas as fichas nutricionais (metodo media_3_fontes)."""
    sheets = []
    async for doc in db.nutrition_sheets.find({}, {"_id": 0}):
        sheets.append(doc)
    return {"ok": True, "count": len(sheets), "sheets": sheets}


@api_router.get("/nutrition/{dish_name}")
async def get_nutrition_sheet(dish_name: str):
    """Busca ficha nutricional de um prato por nome."""
    data = await lookup_nutrition_sheet(dish_name)
    if data:
        return {"ok": True, "data": data}
    return {"ok": False, "message": f"Ficha nutricional nao encontrada para: {dish_name}"}



# ═══════════════════════════════════════════════════════════════
# TTS - Text-to-Speech para acessibilidade
# ═══════════════════════════════════════════════════════════════
@api_router.post("/ai/tts")
async def text_to_speech(request: Request):
    """Gera audio MP3 descrevendo o prato identificado"""
    from services.tts_service import generate_dish_audio
    from fastapi.responses import Response
    
    try:
        body = await request.json()
        dish_data = body.get("dish_data", {})
        voice = body.get("voice", "alloy")
        
        if voice not in ("alloy", "onyx"):
            voice = "alloy"
        
        if not dish_data.get("dish_display") and not dish_data.get("nome"):
            return {"ok": False, "message": "Dados do prato nao fornecidos"}
        
        audio_bytes = await generate_dish_audio(dish_data, voice=voice)
        
        if audio_bytes:
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=soulnutri-audio.mp3"}
            )
        else:
            return {"ok": False, "message": "Erro ao gerar audio"}
    
    except Exception as e:
        logger.error(f"[TTS] Erro: {e}")
        return {"ok": False, "message": "Erro interno no servico de audio"}



@api_router.post("/ai/clear-cache")
async def clear_ai_cache():
    """
    Limpa o cache de identificacoes.
    Útil apos corrigir um prato para forcar re-identificacao.
    """
    try:
        from services.cache_service import clear_cache, get_cache_stats
        
        stats_before = get_cache_stats()
        clear_cache()
        
        return {
            "ok": True,
            "message": "Cache limpo com sucesso",
            "items_cleared": stats_before.get("size", 0)
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/ai/reindex")
async def reindex(max_per_dish: int = 10):
    """Reconstroi o indice de embeddings."""
    try:
        from ai.index import get_index
        logger.info("Iniciando reindexacao...")
        index = get_index()
        stats = index.build_index(max_per_dish=max_per_dish)
        if 'error' in stats:
            return JSONResponse(status_code=400, content={"ok": False, "error": stats['error']})
        return {
            "ok": True,
            "total_dishes": stats['total_dishes'],
            "total_images": stats['total_images'],
            "elapsed_seconds": stats['elapsed_seconds'],
            "message": f"Indice reconstruido com {stats['total_dishes']} pratos"
        }
    except Exception as e:
        logger.error(f"Erro na reindexacao: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@api_router.post("/ai/reindex-background")
async def reindex_background(max_per_dish: int = 10):
    """Inicia reconstrucao do indice em BACKGROUND."""
    import subprocess
    try:
        log_file = "/tmp/rebuild_index.log"
        status_file = "/tmp/rebuild_index_status.json"
        if os.path.exists(log_file):
            os.remove(log_file)
        if os.path.exists(status_file):
            os.remove(status_file)
        script_path = "/app/backend/rebuild_index.py"
        cmd = f"cd /app/backend && /root/.venv/bin/python {script_path} {max_per_dish} &"
        subprocess.Popen(cmd, shell=True)
        logger.info(f"[REINDEX-BG] Iniciado em background com max_per_dish={max_per_dish}")
        return {
            "ok": True,
            "message": "Reconstrucao iniciada em background",
            "max_per_dish": max_per_dish
        }
    except Exception as e:
        logger.error(f"Erro ao iniciar reindexacao em background: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@api_router.get("/ai/reindex-status")
async def reindex_status():
    """Verifica o status da reconstrucao do indice em background"""
    import json
    
    log_file = "/tmp/rebuild_index.log"
    status_file = "/tmp/rebuild_index_status.json"
    
    result = {
        "in_progress": False,
        "completed": False,
        "log_file": log_file,
        "status_file": status_file
    }
    
    # Verificar se existe arquivo de status (conclusao)
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
            result["completed"] = True
            result["status"] = status
        except:
            pass
    
    # Verificar log para progresso
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
            
            # Verificar se esta em progresso
            if "INICIANDO RECONSTRUÇÃO" in log_content and "CONCLUÍDA" not in log_content:
                result["in_progress"] = True
            
            # Extrair ultimas linhas
            lines = log_content.strip().split('\n')
            result["last_lines"] = lines[-10:] if len(lines) > 10 else lines
        except:
            pass
    
    return result


@api_router.post("/ai/add-to-index")
async def add_to_index(
    file: UploadFile = File(...),
    dish_name: str = Form(...),
    weight_grams: Optional[int] = Form(None)
):
    """
    Adiciona uma nova foto ao indice local para reconhecimento rapido.
    Use apos identificar um prato na balanca.
    
    Args:
        file: Imagem do prato
        dish_name: Nome do prato (ex: "Frango Grelhado")
        weight_grams: Peso em gramas (opcional)
    
    Returns:
        Confirmacao e tempo estimado de reconhecimento futuro
    """
    import hashlib
    from datetime import datetime
    
    try:
        content = await file.read()
        
        # Normalizar nome do prato para diretorio
        dish_slug = dish_name.lower().strip()
        dish_slug = dish_slug.replace(" ", "_").replace("-", "_")
        dish_slug = ''.join(c for c in dish_slug if c.isalnum() or c == '_')
        
        # Gerar nome unico para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(content).hexdigest()[:8]
        filename = f"{dish_slug}_{timestamp}_{hash_suffix}.jpg"
        
        # Salvar imagem no S3 + MongoDB + local
        from services.image_service import save_dish_image, get_dish_image_count
        save_dish_image(dish_slug, filename, content)
        
        existing_images = get_dish_image_count(dish_slug)
        
        logger.info(f"[ADD-INDEX] Foto adicionada: {dish_name} ({existing_images} fotos)")
        
        return {
            "ok": True,
            "dish_name": dish_name,
            "dish_slug": dish_slug,
            "filename": filename,
            "total_images": existing_images,
            "weight_grams": weight_grams,
            "message": f"Foto adicionada! {dish_name} agora tem {existing_images} foto(s).",
            "nota": "Execute /api/ai/reindex para atualizar o indice e ter reconhecimento em ~200ms"
        }
        
    except Exception as e:
        logger.error(f"Erro ao adicionar foto: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )

@api_router.post("/ai/identify")
async def identify_image(
    file: UploadFile = File(...),
    pin: Optional[str] = Form(None),
    nome: Optional[str] = Form(None),
    country: Optional[str] = Form("BR"),  # Pais do usuario: BR ou OTHER
    restaurant: Optional[str] = Form(None)  # Restaurante: cibi_sana ou None/outro
):
    """
    Identifica um prato a partir de uma imagem.
    Se PIN e nome forem fornecidos, retorna dados Premium.
    
    LÓGICA DE RECONHECIMENTO:
    - Cibi Sana (restaurant=cibi_sana): CLIP local APENAS (Gemini TRAVADO, custo zero)
    - Brasil outros (country=BR, restaurant!=cibi_sana): Gemini primeiro
    - Internacional (country!=BR): Gemini primeiro
    
    Returns:
        IdentifyResponse com o prato identificado e nivel de confianca
    """
    start_time = time.time()
    perf_start = time.perf_counter()
    
    logger.info(f"[IDENTIFY] Iniciando identificacao - restaurant={restaurant}, country={country}")
    
    try:
        # Ler imagem
        t0 = time.perf_counter()
        content = await file.read()
        t_upload = (time.perf_counter() - t0) * 1000
        logger.info(f"[TIMING] Upload/Read: {t_upload:.0f}ms ({len(content)//1024}KB)")
        
        if len(content) == 0:
            return IdentifyResponse(
                ok=False,
                identified=False,
                confidence="baixa",
                score=0.0,
                message="Arquivo de imagem vazio"
            )
        
        # ═══════════════════════════════════════════════════════════════════════
        # CACHE: Verificar se ja identificamos esta imagem antes
        # ═══════════════════════════════════════════════════════════════════════
        from services.cache_service import get_cached_result, cache_result
        cached = get_cached_result(content)
        if cached:
            elapsed_ms = (time.time() - start_time) * 1000
            cached['search_time_ms'] = round(elapsed_ms, 2)
            logger.info(f"[CACHE] ⚡ Resposta do cache em {elapsed_ms:.0f}ms")
            if await get_setting("ENABLE_PROCESSING_METRICS"):
                total_ms = (time.perf_counter() - perf_start) * 1000
                source = cached.get('source', '')
                engine = "GEMINI" if source == 'gemini_flash' else "CLIP"
                save_processing_metrics({
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_ms": round(total_ms, 2),
                    "dish_name": cached.get('dish_display', ''),
                    "confidence_score": cached.get('score', 0),
                    "engine_used": f"{engine} (cache)"
                })
            return cached
        
        # ═══════════════════════════════════════════════════════════════════════
        # SISTEMA DE IDENTIFICAÇÃO - V2.1 (Bifurcacao por localizacao)
        # ═══════════════════════════════════════════════════════════════════════
        # Cibi Sana (GPS): CLIP ONLY (Gemini HARD LOCK, pratos calibrados)
        # Fora Cibi Sana: GEMINI ONLY (CLIP desligado, pratos genericos)
        # ═══════════════════════════════════════════════════════════════════════
        
        decision = None
        is_cibi_sana = (restaurant or '').strip().lower() == 'cibi_sana'
        
        if is_cibi_sana:
            # ══════════════════════════════════════════════════════════════════
            # MODO CIBI SANA: CLIP ONLY (HARD LOCK - Gemini bloqueado)
            # ══════════════════════════════════════════════════════════════════
            from ai.index import get_index
            from ai.policy import analyze_result
            
            index = get_index()
            
            if index.is_ready():
                t_clip = time.perf_counter()
                results = index.search(content, top_k=5)
                t_clip_ms = (time.perf_counter() - t_clip) * 1000
                logger.info(f"[TIMING] CLIP search total: {t_clip_ms:.0f}ms")
                clip_decision = analyze_result(results)
                clip_score = clip_decision.get('score', 0.0)
                
                logger.info(f"[CIBI SANA | CLIP] {clip_decision.get('dish_display', 'N/A')} - Score: {clip_score:.2%}")
                
                decision = clip_decision
                decision['source'] = 'local_index'
            else:
                return IdentifyResponse(
                    ok=False,
                    identified=False,
                    confidence="baixa",
                    score=0.0,
                    message="Prato nao identificado. Tente com outra foto."
                )
        else:
            # ══════════════════════════════════════════════════════════════════
            # MODO EXTERNO: GEMINI ONLY (CLIP desligado - evita pratos Cibi Sana)
            # ══════════════════════════════════════════════════════════════════
            logger.info(f"[EXTERNO] Usando Gemini (CLIP desligado para evitar pratos Cibi Sana)")
            
            from services.gemini_flash_service import (
                identify_dish_gemini_flash,
                is_gemini_flash_available
            )
            
            if not is_gemini_flash_available():
                return IdentifyResponse(
                    ok=False,
                    identified=False,
                    confidence="baixa",
                    score=0.0,
                    message="Servico de IA indisponivel. Ative a localizacao para usar o modo Cibi Sana."
                )
            
            flash_profile = None
            if pin and nome:
                from services.profile_service import hash_pin
                pin_hash = hash_pin(pin)
                flash_profile = await db.users.find_one(
                    {"pin_hash": pin_hash, "nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
                    {"_id": 0}
                )
            
            flash_result = await identify_dish_gemini_flash(content, flash_profile, restaurant=restaurant)
            
            if flash_result.get('ok'):
                decision = {
                    'identified': True,
                    'dish': flash_result.get('nome', '').lower().replace(' ', '_'),
                    'dish_display': flash_result.get('nome'),
                    'score': flash_result.get('score', 0.90),
                    'source': 'gemini_flash',
                    'category': flash_result.get('categoria'),
                    'category_emoji': {"vegano": "🌱", "vegetariano": "🥬", "proteina animal": "🍖"}.get(flash_result.get('categoria', ''), '🍽️'),
                    'nutrition': flash_result.get('nutricao'),
                    'alergenos': flash_result.get('alergenos', {}),
                    'alertas_personalizados': flash_result.get('alertas_personalizados', []),
                    'tempo_ia_ms': flash_result.get('tempo_processamento_ms', 0),
                    'ingredientes': flash_result.get('ingredientes', []),
                    'beneficios': flash_result.get('beneficios', []),
                    'riscos': flash_result.get('riscos', []),
                    'curiosidade': flash_result.get('curiosidade', ''),
                    'combinacoes': flash_result.get('combinacoes', []),
                    'noticias': flash_result.get('noticias', []),
                }
                logger.info(f"[EXTERNO | GEMINI] {decision.get('dish_display', 'N/A')} - Score: {decision.get('score', 0):.2%}")
            else:
                return IdentifyResponse(
                    ok=False,
                    identified=False,
                    confidence="baixa",
                    score=0.0,
                    message="Nao foi possivel identificar o prato."
                )
        
        # ══════════════════════════════════════════════════════════════════════
        # APLICAR NÍVEIS DE CONFIANÇA - v1.3
        # ══════════════════════════════════════════════════════════════════════
        score = decision.get('score', 0.0)
        
        # Se ja foi rejeitado na cascata (identified=False), preservar a mensagem
        if decision.get('identified') is False and decision.get('message'):
            decision['aviso_confianca'] = decision.get('message')
            decision['alternatives'] = []  # Baixa = 0 alternativas
        elif score >= 0.90:
            decision['confidence'] = 'alta'
            decision['message'] = f"Identificado: {decision.get('dish_display', 'Prato')}"
            decision['aviso_confianca'] = None
            decision['alternatives'] = []  # Alta = 0 alternativas
        elif score >= 0.50:
            decision['confidence'] = 'media'
            dish_name = decision.get('dish_display', 'Prato')
            decision['message'] = f"Parece ser: {dish_name}"
            decision['aviso_confianca'] = "Verifique se o prato esta correto"
            # Media = maximo 2 alternativas (ja definido na decisao)
            if 'alternatives' in decision:
                decision['alternatives'] = decision['alternatives'][:2]
        else:
            decision['confidence'] = 'baixa'
            decision['message'] = "Nao foi possivel identificar o prato"
            decision['aviso_confianca'] = "Tente outra foto ou consulte o atendente"
            decision['alternatives'] = []
        
        # ══════════════════════════════════════════════════════════════════════
        # POST-CLIP: RESPOSTA RAPIDA para Cibi Sana (<500ms)
        # MongoDB queries delegadas para /ai/enrich (background)
        # ══════════════════════════════════════════════════════════════════════
        decision['ia_disponivel'] = False
        decision['ok'] = True
        
        is_premium = False
        user_profile = None
        premium_data = {}
        dish_display_name = format_dish_name(decision.get('dish_display', ''))
        
        # Para Cibi Sana: retorno imediato SEM queries MongoDB (velocidade <500ms)
        # Para modo externo (Gemini): queries rapidas em paralelo
        if is_cibi_sana:
            # CLIP retorna rapido - nutrition e premium virao pelo /ai/enrich
            nutrition_data = decision.get('nutrition') or {}
            
            # Check premium apenas se credenciais enviadas (unica query)
            if pin and nome:
                import asyncio as _asyncio
                from services.profile_service import hash_pin
                pin_hash = hash_pin(pin)
                user_profile = await db.users.find_one(
                    {"pin_hash": pin_hash, "nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
                    {"_id": 0}
                )
                is_premium = user_profile is not None
                if is_premium:
                    alertas_alergenos = []
                    restricoes = user_profile.get("restricoes", [])
                    alergenos_detectados = decision.get('alergenos', {})
                    for restricao in restricoes:
                        r_lower = restricao.lower().replace(" ", "_")
                        if alergenos_detectados.get(r_lower):
                            alertas_alergenos.append({
                                "tipo": "alergia", "severidade": "alta",
                                "mensagem": f"Contém {restricao} - restrição registrada!",
                                "icone": "🚫"
                            })
                    premium_data = {
                        "alertas_alergenos": alertas_alergenos,
                        "alertas_historico": [],
                        "combinacoes_sugeridas": decision.get('combinacoes', []),
                        "is_premium": True, "enrichment_pending": True
                    }
        else:
            # Modo externo (Gemini): queries em paralelo
            import asyncio as _asyncio
            parallel_tasks = {}
            
            if decision.get('identified') and dish_display_name:
                parallel_tasks['nutrition'] = lookup_nutrition_sheet(dish_display_name)
            if pin and nome:
                from services.profile_service import hash_pin
                pin_hash = hash_pin(pin)
                parallel_tasks['user'] = db.users.find_one(
                    {"pin_hash": pin_hash, "nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
                    {"_id": 0}
                )
            
            if parallel_tasks:
                task_keys = list(parallel_tasks.keys())
                results = await _asyncio.gather(*parallel_tasks.values(), return_exceptions=True)
                resolved = dict(zip(task_keys, results))
            else:
                resolved = {}
            
            sheet_data = resolved.get('nutrition') if not isinstance(resolved.get('nutrition'), Exception) else None
            user_profile = resolved.get('user') if not isinstance(resolved.get('user'), Exception) else None
            is_premium = user_profile is not None
            
            nutrition_data = decision.get('nutrition') or {}
            if sheet_data:
                nutrition_data = {**nutrition_data, **sheet_data}
                if sheet_data.get('calorias_kcal') is not None:
                    nutrition_data['calorias'] = f"{sheet_data['calorias_kcal']:.0f} kcal"
                if sheet_data.get('proteinas_g') is not None:
                    nutrition_data['proteinas'] = f"{sheet_data['proteinas_g']:.1f}g"
                if sheet_data.get('carboidratos_g') is not None:
                    nutrition_data['carboidratos'] = f"{sheet_data['carboidratos_g']:.1f}g"
                if sheet_data.get('gorduras_g') is not None:
                    nutrition_data['gorduras'] = f"{sheet_data['gorduras_g']:.1f}g"
                if sheet_data.get('fibras_g') is not None:
                    nutrition_data['fibras'] = f"{sheet_data['fibras_g']:.1f}g"
                if sheet_data.get('sodio_mg') is not None:
                    nutrition_data['sodio'] = f"{sheet_data['sodio_mg']:.0f}mg"
            
            if is_premium:
                alertas_alergenos = []
                restricoes = user_profile.get("restricoes", [])
                alergenos_detectados = decision.get('alergenos', {})
                for restricao in restricoes:
                    r_lower = restricao.lower().replace(" ", "_")
                    if alergenos_detectados.get(r_lower):
                        alertas_alergenos.append({
                            "tipo": "alergia", "severidade": "alta",
                            "mensagem": f"Contém {restricao} - restrição registrada!",
                            "icone": "🚫"
                        })
                premium_data = {
                    "alertas_alergenos": alertas_alergenos,
                    "alertas_historico": [],
                    "combinacoes_sugeridas": decision.get('combinacoes', []),
                    "is_premium": True, "enrichment_pending": True
                }
        
        nutrition_obj = NutritionInfo(**nutrition_data) if nutrition_data else None
        
        # Calcular tempo total
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Identificacao: {decision.get('dish')} ({decision.get('confidence')}) em {elapsed_ms:.0f}ms")
        
        # Gerar mensagem de confianca em 3 niveis
        confidence_level_msg = get_confidence_level_message(
            decision['score'], 
            decision['confidence']
        )
        
        # Montar resposta base
        response_data = {
            "ok": True,
            "identified": decision['identified'],
            "dish": decision.get('dish'),
            "dish_display": dish_display_name,
            "confidence": decision['confidence'],
            "confidence_level": confidence_level_msg,  # NOVO: Mensagem descritiva
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
            "alternatives": [format_dish_name(a) for a in decision.get('alternatives', [])],
            "search_time_ms": round(elapsed_ms, 2),
            "source": decision.get('source', 'local_index'),
            # Dados cientificos - movidos para /ai/enrich (velocidade)
            "beneficio_principal": None,
            "curiosidade_cientifica": None,
            "referencia_pesquisa": None,
            "alerta_saude": None,
            "voce_sabia": None,
            "dica_chef": None,
            "mito_verdade": None,
            # Dados Premium extras
            "premium": premium_data if is_premium else None,
            "is_premium": is_premium,
            # Flag para indicar se IA poderia melhorar o resultado (sem gastar creditos automaticamente)
            "ia_disponivel": decision.get('ia_disponivel', False),
            # Novos campos do Gemini Flash
            "alergenos": decision.get('alergenos', {}),
            "dica_nutricional": decision.get('dica_nutricional'),
            "alertas_personalizados": decision.get('alertas_personalizados', []),
            "tempo_ia_ms": decision.get('tempo_ia_ms'),
            # Curiosidade e combinacoes (Gemini ou local)
            "curiosidade": decision.get('curiosidade') if is_premium else None,
            "combinacoes": decision.get('combinacoes', []) if is_premium else [],
            # Noticias e alertas sobre ingredientes (Gemini)
            "noticias": decision.get('noticias', []) if is_premium else [],
            # Familias de Pratos - honestidade
            "family_name": decision.get('family_name'),
            "family_candidates": decision.get('family_candidates', []),
            "family_candidates_detail": decision.get('family_candidates_detail', []),
        }
        
        # ═══════════════════════════════════════════════════════════════════════
        # CACHE: Salvar resultado para futuras consultas
        # ═══════════════════════════════════════════════════════════════════════
        if response_data.get('identified'):
            cache_result(content, response_data, ttl_seconds=3600)  # 1 hora de cache
        
        # ═══════════════════════════════════════════════════════════════════════
        # MÉTRICAS DE PROCESSAMENTO (condicional)
        # ═══════════════════════════════════════════════════════════════════════
        if await get_setting("ENABLE_PROCESSING_METRICS"):
            total_ms = (time.perf_counter() - perf_start) * 1000
            source = response_data.get('source', '')
            engine = "GEMINI" if source == 'gemini_flash' else "CLIP"
            save_processing_metrics({
                "timestamp": datetime.now().isoformat(),
                "processing_time_ms": round(total_ms, 2),
                "dish_name": response_data.get('dish_display', ''),
                "confidence_score": response_data.get('score', 0),
                "engine_used": engine
            })
        
        return response_data
        
    except Exception as e:
        logger.error(f"Erro na identificacao: {e}")
        elapsed_ms = (time.time() - start_time) * 1000
        
        return IdentifyResponse(
            ok=False,
            identified=False,
            confidence="baixa",
            score=0.0,
            message=f"Erro ao processar imagem: {str(e)}",
            search_time_ms=round(elapsed_ms, 2)
        )



# ═══════════════════════════════════════════════════════════════════════════════
# ENRIQUECIMENTO PREMIUM (background - chamado pelo frontend após scan rápido)
# ═══════════════════════════════════════════════════════════════════════════════
@api_router.post("/ai/enrich")
async def enrich_dish(request: Request):
    """Enriquece um prato com dados Premium (benefícios, riscos, curiosidades, alertas, etc.)
    Chamado pelo frontend em BACKGROUND após o Fast Scan retornar."""
    import asyncio as _asyncio
    try:
        body = await request.json()
        nome = body.get("nome", "")
        ingredientes = body.get("ingredientes", [])
        pin = body.get("pin", "")
        user_nome = body.get("user_nome", "")
        
        if not nome:
            return {"ok": False, "error": "Nome do prato é obrigatório"}
        
        # Verificar se é Premium
        is_premium = False
        if pin:
            import hashlib
            pin_hash = hashlib.sha256(pin.encode()).hexdigest()
            user = await db.users.find_one(
                {"pin_hash": pin_hash, "premium_ativo": True},
                {"_id": 0}
            )
            is_premium = user is not None
        
        if not is_premium:
            return {"ok": False, "error": "Acesso Premium necessário"}
        
        # Executar enrichment Gemini + alertas LLM + nutrition em paralelo
        from services.gemini_flash_service import enrich_dish_gemini
        from services.alerts_service import generate_food_alert
        
        logger.info(f"[Enrich] Chamando enrich + alertas + nutrition em paralelo para '{nome}'")
        
        enrich_task = enrich_dish_gemini(nome, ingredientes)
        alert_task = generate_food_alert(nome, ingredientes, db=db, user_nome=user_nome)
        nutrition_task = lookup_nutrition_sheet(nome)
        
        enrichment, alert_data, nutrition_sheet = await _asyncio.gather(
            enrich_task, alert_task, nutrition_task, return_exceptions=True
        )
        
        # Tratar exceções do gather
        if isinstance(enrichment, Exception):
            logger.warning(f"[Enrich] Gemini erro: {enrichment}")
            enrichment = {}
        if isinstance(alert_data, Exception):
            logger.warning(f"[Enrich] Alertas erro: {alert_data}")
            alert_data = None
        if isinstance(nutrition_sheet, Exception):
            logger.warning(f"[Enrich] Nutrition erro: {nutrition_sheet}")
            nutrition_sheet = None
        
        # Montar alertas de histórico
        alertas_historico = []
        if alert_data and isinstance(alert_data, dict):
            alertas_historico.append(alert_data)
        
        # Formatar nutrition
        nutrition_formatted = {}
        if nutrition_sheet and isinstance(nutrition_sheet, dict):
            if nutrition_sheet.get('calorias_kcal') is not None:
                nutrition_formatted['calorias'] = f"{nutrition_sheet['calorias_kcal']:.0f} kcal"
            if nutrition_sheet.get('proteinas_g') is not None:
                nutrition_formatted['proteinas'] = f"{nutrition_sheet['proteinas_g']:.1f}g"
            if nutrition_sheet.get('carboidratos_g') is not None:
                nutrition_formatted['carboidratos'] = f"{nutrition_sheet['carboidratos_g']:.1f}g"
            if nutrition_sheet.get('gorduras_g') is not None:
                nutrition_formatted['gorduras'] = f"{nutrition_sheet['gorduras_g']:.1f}g"
            if nutrition_sheet.get('fibras_g') is not None:
                nutrition_formatted['fibras'] = f"{nutrition_sheet['fibras_g']:.1f}g"
            if nutrition_sheet.get('sodio_mg') is not None:
                nutrition_formatted['sodio'] = f"{nutrition_sheet['sodio_mg']:.0f}mg"
        
        logger.info(f"[Enrich] Enrichment: {list(enrichment.keys()) if enrichment else 'vazio'}, Alertas: {len(alertas_historico)}, Nutrition: {bool(nutrition_formatted)}")
        
        return {
            "ok": bool(enrichment) or bool(alertas_historico) or bool(nutrition_formatted),
            "beneficios": enrichment.get("beneficios", []),
            "riscos": enrichment.get("riscos", []),
            "curiosidade": enrichment.get("curiosidade", ""),
            "combinacoes": enrichment.get("combinacoes", []),
            "noticias": enrichment.get("noticias", []),
            "alertas_historico": alertas_historico,
            "nutrition": nutrition_formatted
        }
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"[Enrich] Erro: {e}\n{tb}")
        return {"ok": False, "error": str(e)}

@api_router.post("/ai/identify-with-ai")
async def identify_with_ai(
    file: UploadFile = File(...),
    pin: str = Form(""),
    nome: str = Form(""),
    restaurant: Optional[str] = Form(None)
):
    """
    Identificacao usando Gemini Vision - CONSOME CRÉDITOS!
    HARD LOCK: Bloqueado quando restaurant=cibi_sana.
    """
    # HARD LOCK: Cibi Sana -> Gemini totalmente bloqueado
    is_cibi_sana = (restaurant or '').strip().lower() == 'cibi_sana'
    if is_cibi_sana:
        logger.info("[HARD LOCK] identify-with-ai BLOQUEADO - Cibi Sana")
        return {
            "ok": False,
            "error": "Gemini nao disponivel dentro do Cibi Sana. Use o reconhecimento local.",
            "blocked_by": "cibi_sana_hard_lock"
        }
    
    start_time = time.time()
    try:
        content = await file.read()
        
        # Restaurar temporariamente o generic_ai original
        import importlib
        import sys
        
        # Carregar o backup com IA
        backup_path = "/app/backend/services/generic_ai.py.BACKUP_COM_IA"
        
        import os
        if not os.path.exists(backup_path):
            return {
                "ok": False,
                "error": "Servico de IA nao disponivel no momento",
                "message": "Use o reconhecimento local ou corrija manualmente"
            }
        
        # Ler e executar o codigo do backup
        with open(backup_path, 'r') as f:
            backup_code = f.read()
        
        # Criar modulo temporario
        import types
        temp_module = types.ModuleType("generic_ai_temp")
        exec(compile(backup_code, backup_path, 'exec'), temp_module.__dict__)
        
        # Chamar a funcao de identificacao
        result = await temp_module.identify_unknown_dish(content)
        
        if result.get('ok'):
            logger.info(f"[IA SOLICITADA] Gemini identificou: {result.get('nome')} (creditos usados)")
            response = {
                "ok": True,
                "identified": True,
                "dish_display": result.get('nome'),
                "category": result.get('categoria'),
                "category_emoji": result.get('category_emoji', '🍽️'),
                "confidence": result.get('confianca', 'media'),
                "score": result.get('score', 0.7),
                "ingredientes": result.get('ingredientes_provaveis', []),
                "beneficios": result.get('beneficios', []),
                "descricao": result.get('descricao', ''),
                "source": "gemini_ai",
                "creditos_usados": True,
                "message": "Identificado com IA (creditos consumidos)"
            }
            if await get_setting("ENABLE_PROCESSING_METRICS"):
                total_ms = (time.time() - start_time) * 1000
                save_processing_metrics({
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_ms": round(total_ms, 2),
                    "dish_name": response.get('dish_display', ''),
                    "confidence_score": response.get('score', 0),
                    "engine_used": "GEMINI"
                })
            return response
        else:
            return {
                "ok": False,
                "error": result.get('error', 'Erro na identificacao'),
                "creditos_usados": False
            }
            
    except Exception as e:
        logger.error(f"[IA SOLICITADA] Erro: {e}")
        return {
            "ok": False,
            "error": str(e),
            "creditos_usados": False
        }


@api_router.post("/admin/revisar-prato-taco")
async def revisar_prato_com_taco(request: Request):
    """
    Busca informacoes nutricionais usando a Tabela TACO.
    ZERO CRÉDITOS - 100% LOCAL
    """
    try:
        from data.taco_database import buscar_dados_taco, calcular_nutricao_prato, search_taco
        
        data = await request.json()
        nome = data.get('nome', '')
        ingredientes = data.get('ingredientes', [])
        
        if not ingredientes:
            return {"ok": False, "error": "Ingredientes sao obrigatorios"}
        
        # Calcular nutricao baseada nos ingredientes
        nutricao = calcular_nutricao_prato(ingredientes, 100)  # por 100g
        
        # Detectar categoria baseada nos ingredientes
        ing_texto = ' '.join(ingredientes).lower()
        
        # Ingredientes de origem animal
        animais = ['frango', 'carne', 'boi', 'porco', 'bacon', 'peixe', 'camarao', 
                   'atum', 'salmao', 'bacalhau', 'costela', 'linguica', 'presunto']
        vegetarianos = ['ovo', 'leite', 'queijo', 'manteiga', 'creme de leite', 'iogurte']
        
        # Excluir versoes veganas
        veganos_ok = ['leite de coco', 'leite de soja', 'queijo vegano', 'manteiga vegetal']
        
        categoria = 'vegano'  # assume vegano
        for ing in animais:
            if ing in ing_texto:
                categoria = 'proteina animal'
                break
        
        if categoria == 'vegano':
            for ing in vegetarianos:
                if ing in ing_texto:
                    # Verificar se nao e versao vegana
                    is_vegano = False
                    for v in veganos_ok:
                        if v in ing_texto:
                            is_vegano = True
                            break
                    if not is_vegano:
                        categoria = 'vegetariano'
                        break
        
        # Detectar alergenos
        alergenos = {
            "gluten": any(x in ing_texto for x in ['farinha', 'pao', 'massa', 'trigo']),
            "lactose": any(x in ing_texto for x in ['leite', 'queijo', 'creme']) and 'coco' not in ing_texto,
            "ovo": 'ovo' in ing_texto,
            "frutos_do_mar": any(x in ing_texto for x in ['camarao', 'peixe', 'atum', 'salmao', 'lula']),
            "oleaginosas": any(x in ing_texto for x in ['castanha', 'nozes', 'amendoim', 'amendoa'])
        }
        
        # Formatar resultado
        resultado = {
            "ok": True,
            "fonte": "TACO (zero creditos)",
            "categoria": categoria,
            "nutricao": {
                "calorias": f"{nutricao.get('calorias', 0):.0f} kcal",
                "proteinas": f"{nutricao.get('proteinas', 0):.1f}g",
                "carboidratos": f"{nutricao.get('carboidratos', 0):.1f}g",
                "gorduras": f"{nutricao.get('gorduras', 0):.1f}g",
                "fibras": f"{nutricao.get('fibras', 0):.1f}g",
                "sodio": f"{nutricao.get('sodio', 0):.0f}mg",
                "calcio": f"{nutricao.get('calcio', 0):.0f}mg"
            },
            "alergenos": alergenos,
            "contem_gluten": alergenos["gluten"],
            "contem_lactose": alergenos["lactose"],
            "contem_ovo": alergenos["ovo"],
            "contem_frutos_mar": alergenos["frutos_do_mar"],
            "contem_castanhas": alergenos["oleaginosas"]
        }
        
        logger.info(f"[TACO] {nome}: {categoria} - {nutricao.get('calorias', 0):.0f} kcal (ZERO CRÉDITOS)")
        return resultado
        
    except Exception as e:
        logger.error(f"[TACO] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/revisar-prato-ia")
async def revisar_prato_com_ia(request: Request):
    """
    Usa Gemini Flash para analisar ingredientes e sugerir:
    - Categoria (vegano/vegetariano/proteina animal)
    - Ficha nutricional (por 100g)
    - Beneficios nutricionais
    - Riscos e alergenos
    
    Custo: 1 chamada Gemini (~R$0.001)
    """
    try:
        from services.gemini_flash_service import is_gemini_flash_available
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import os
        
        data = await request.json()
        nome = data.get('nome', '')
        ingredientes = data.get('ingredientes', [])
        
        if not nome or not ingredientes:
            return {"ok": False, "error": "Nome e ingredientes sao obrigatorios"}
        
        if not is_gemini_flash_available():
            return {"ok": False, "error": "Gemini Flash nao disponivel"}
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Prompt otimizado para analise nutricional COMPLETA
        prompt_sistema = """Voce e um nutricionista especialista em alimentacao brasileira.
Analise os ingredientes do prato e retorne APENAS JSON valido com:

1. categoria: "vegano", "vegetariano" ou "proteina animal"
2. nutricao: valores por 100 GRAMAS do prato pronto (nao por porcao!)
   - calorias: numero em kcal (ex: "280 kcal")
   - proteinas: em gramas (ex: "18g")
   - carboidratos: em gramas (ex: "12g")
   - gorduras: em gramas (ex: "15g")
   - fibras: em gramas (ex: "2g")
3. beneficios: lista de 3-4 beneficios reais
4. riscos: lista de alertas (alergenos, alto teor de algo, etc)
5. alergenos: {gluten, lactose, ovo, frutos_do_mar, oleaginosas} true/false

REGRAS DE CATEGORIA:
- Carne, peixe, frango, bacon, camarao = "proteina animal"
- Ovo, leite, queijo (sem carne) = "vegetariano"
- 100% vegetal = "vegano" (leite de coco e vegano)

REGRAS NUTRICIONAIS (por 100g):
- Bacalhau com natas: ~180-220 kcal (tem creme)
- Bacalhau a bras: ~250-300 kcal (batata palha + ovos)
- Arroz branco: ~130 kcal
- Feijao: ~77 kcal
- Carnes grelhadas: ~150-200 kcal
- Frituras/empanados: +50-100 kcal extra
- Pratos com creme/queijo: adicionar ~50 kcal

Responda APENAS JSON valido."""
        
        ingredientes_texto = ", ".join(ingredientes) if isinstance(ingredientes, list) else ingredientes
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"revisar-{int(time.time())}",
            system_message=prompt_sistema
        ).with_model("gemini", "gemini-2.0-flash-lite")
        
        response = await chat.send_message(UserMessage(
            text=f"Prato: {nome}\nIngredientes: {ingredientes_texto}\n\nRetorne a ficha nutricional POR 100 GRAMAS."
        ))
        
        # Parse JSON
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        
        import json
        resultado = json.loads(response_clean.strip())
        
        logger.info(f"[REVISAR-IA] {nome}: {resultado.get('categoria')} - {resultado.get('nutricao', {}).get('calorias', 'N/A')}")
        
        return {
            "ok": True,
            "nome": nome,
            "sugestoes": resultado
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"[REVISAR-IA] Erro JSON: {e}")
        return {"ok": False, "error": "Erro ao processar resposta da IA"}
    except Exception as e:
        logger.error(f"[REVISAR-IA] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/revisar-lote-ia")
async def revisar_pratos_em_lote(request: Request):
    """
    Revisa multiplos pratos com IA Gemini Flash em lote.
    Ideal para corrigir fichas nutricionais de uma vez.
    
    Body:
    {
        "slugs": ["slug1", "slug2", ...],  // Lista de slugs para revisar
        "max_pratos": 10  // Limite por chamada (para nao travar)
    }
    
    Retorno:
    {
        "ok": true,
        "revisados": 8,
        "falhas": 2,
        "resultados": [...]
    }
    """
    try:
        from services.gemini_flash_service import is_gemini_flash_available
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import os
        import json
        
        data = await request.json()
        slugs = data.get('slugs', [])
        max_pratos = min(data.get('max_pratos', 10), 20)  # Maximo 20 por vez
        
        if not slugs:
            return {"ok": False, "error": "Nenhum slug fornecido"}
        
        if not is_gemini_flash_available():
            return {"ok": False, "error": "Gemini Flash nao disponivel"}
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        resultados = []
        revisados = 0
        falhas = 0
        
        # Processar cada prato
        for slug in slugs[:max_pratos]:
            try:
                # Carregar info do prato do MongoDB
                dish_info = await db.dishes.find_one({"slug": slug}, {"_id": 0})
                if not dish_info:
                    # Tentar com slug normalizado
                    norm_slug = slug.lower().replace(' ', '_')
                    dish_info = await db.dishes.find_one({"slug": norm_slug}, {"_id": 0})
                
                if not dish_info:
                    resultados.append({"slug": slug, "status": "erro", "msg": "Prato nao encontrado"})
                    falhas += 1
                    continue
                
                nome = dish_info.get('nome', slug)
                ingredientes = dish_info.get('ingredientes', [])
                
                if not ingredientes or len(ingredientes) == 0:
                    resultados.append({"slug": slug, "status": "pulado", "msg": "Sem ingredientes"})
                    continue
                
                # Prompt para revisao
                prompt_sistema = """Voce e um nutricionista especialista em alimentacao brasileira.
Analise os ingredientes do prato e retorne APENAS JSON valido com:

1. categoria: "vegano", "vegetariano" ou "proteina animal"
2. nutricao: valores por 100 GRAMAS do prato pronto (nao por porcao!)
   - calorias: numero em kcal (ex: "280 kcal")
   - proteinas: em gramas (ex: "18g")
   - carboidratos: em gramas (ex: "12g")
   - gorduras: em gramas (ex: "15g")
   - fibras: em gramas (ex: "2g")
3. beneficios: lista de 3-4 beneficios reais
4. riscos: lista de alertas (alergenos, alto teor de algo, etc)
5. alergenos: {gluten, lactose, ovo, frutos_do_mar, oleaginosas} true/false

REGRAS:
- Carne/peixe/frango = "proteina animal"
- Ovo/leite/queijo (sem carne) = "vegetariano"
- 100% vegetal = "vegano"

Responda APENAS JSON valido."""
                
                ingredientes_texto = ", ".join(ingredientes) if isinstance(ingredientes, list) else ingredientes
                
                chat = LlmChat(
                    api_key=api_key,
                    session_id=f"lote-{slug}-{int(time.time())}",
                    system_message=prompt_sistema
                ).with_model("gemini", "gemini-2.0-flash-lite")
                
                response = await chat.send_message(UserMessage(
                    text=f"Prato: {nome}\nIngredientes: {ingredientes_texto}\n\nRetorne a ficha nutricional POR 100 GRAMAS."
                ))
                
                # Parse JSON
                response_clean = response.strip()
                if response_clean.startswith("```"):
                    response_clean = response_clean.split("```")[1]
                    if response_clean.startswith("json"):
                        response_clean = response_clean[4:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                sugestoes = json.loads(response_clean.strip())
                
                # Atualizar dish_info
                dish_info['categoria'] = sugestoes.get('categoria', dish_info.get('categoria'))
                dish_info['nutricao'] = sugestoes.get('nutricao', dish_info.get('nutricao'))
                dish_info['beneficios'] = sugestoes.get('beneficios', dish_info.get('beneficios'))
                dish_info['riscos'] = sugestoes.get('riscos', dish_info.get('riscos'))
                
                # Alergenos
                alergenos = sugestoes.get('alergenos', {})
                dish_info['contem_gluten'] = alergenos.get('gluten', False)
                dish_info['contem_lactose'] = alergenos.get('lactose', False)
                dish_info['contem_ovo'] = alergenos.get('ovo', False)
                dish_info['contem_frutos_mar'] = alergenos.get('frutos_do_mar', False)
                dish_info['contem_castanhas'] = alergenos.get('oleaginosas', False)
                
                # Salvar no MongoDB
                dish_info['slug'] = slug
                await db.dishes.update_one(
                    {"slug": slug},
                    {"$set": dish_info},
                    upsert=True
                )
                
                resultados.append({
                    "slug": slug, 
                    "status": "ok", 
                    "categoria": dish_info['categoria'],
                    "calorias": dish_info.get('nutricao', {}).get('calorias', 'N/A')
                })
                revisados += 1
                
                logger.info(f"[LOTE-IA] ✅ {slug}: {dish_info.get('nutricao', {}).get('calorias', 'N/A')}")
                
                # Pequena pausa para nao sobrecarregar
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"[LOTE-IA] Erro em {slug}: {e}")
                resultados.append({"slug": slug, "status": "erro", "msg": str(e)})
                falhas += 1
        
        return {
            "ok": True,
            "revisados": revisados,
            "falhas": falhas,
            "total_solicitados": len(slugs),
            "processados": len(resultados),
            "resultados": resultados
        }
        
    except Exception as e:
        logger.error(f"[LOTE-IA] Erro geral: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/ai/dishes")
async def list_dishes_combined():
    """Lista todos os pratos: indice IA + MongoDB (lista completa)."""
    try:
        from ai.index import get_index
        from ai.policy import get_dish_name, get_category, get_category_emoji
        
        index = get_index()
        seen_slugs = set()
        dishes = []
        
        # 1. Pratos do indice de IA
        for dish_slug, data in index.metadata.items():
            dishes.append({
                'slug': dish_slug,
                'name': get_dish_name(dish_slug),
                'category': get_category(dish_slug),
                'category_emoji': get_category_emoji(get_category(dish_slug)),
                'image_count': data.get('image_count', 0)
            })
            seen_slugs.add(dish_slug.lower().replace(' ', '_').replace('-', '_'))
        
        # 2. Pratos do MongoDB que nao estao no indice
        async for doc in db.dishes.find({}, {"_id": 0, "slug": 1, "nome": 1, "name": 1, "categoria": 1, "category_emoji": 1}):
            slug = doc.get("slug", "")
            if not slug:
                continue
            norm_slug = slug.lower().replace(' ', '_').replace('-', '_')
            if norm_slug in seen_slugs:
                continue
            seen_slugs.add(norm_slug)
            name = doc.get("nome") or doc.get("name") or slug.replace("_", " ").title()
            dishes.append({
                "slug": slug,
                "name": name,
                "category": doc.get("categoria", "outros"),
                "category_emoji": doc.get("category_emoji", "")
            })
        
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
    
    O prato sera adicionado a pasta de datasets e podera ser
    incorporado ao indice no proximo reindex.
    
    Args:
        dish_name: Nome do prato (sera convertido em slug)
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
                content={"ok": False, "error": "Nome do prato invalido"}
            )
        
        content = await file.read()
        
        # Gerar nome do arquivo
        from services.image_service import save_dish_image, get_dish_image_count
        existing = get_dish_image_count(slug)
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        new_filename = f"{slug}{existing + 1:02d}.{ext}"
        
        # Salvar no S3 + MongoDB + local
        save_dish_image(slug, new_filename, content)
        
        logger.info(f"Nova imagem salva: {slug}/{new_filename}")
        
        return {
            "ok": True,
            "message": f"Imagem do prato '{dish_name}' salva com sucesso!",
            "dish_slug": slug,
            "file_saved": new_filename,
            "total_images": existing + 1,
            "note": "Execute /api/ai/reindex para incorporar ao indice"
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar prato: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.post("/upload/photos")
async def upload_photos(
    dish_name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Upload de fotos para um prato existente. Apenas ADICIONA, nunca modifica ou deleta."""
    import re
    try:
        from services.image_service import save_dish_image, find_dish_slug_match, get_dish_image_count
        
        dish_name = dish_name.strip()
        
        # Buscar prato existente no MongoDB
        target_slug = find_dish_slug_match(dish_name)
        
        if not target_slug:
            return JSONResponse(status_code=400, content={"ok": False, "error": f"Prato nao encontrado: {dish_name}"})
        
        logger.info(f"[UPLOAD] Match: '{dish_name}' -> '{target_slug}'")
        
        saved = 0
        errors = []
        
        for file in files:
            try:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                if ext not in ('jpg', 'jpeg', 'png', 'webp'):
                    errors.append(f"{file.filename}: formato nao suportado")
                    continue
                
                content = await file.read()
                if len(content) < 1000:
                    errors.append(f"{file.filename}: arquivo muito pequeno")
                    continue
                
                # Gerar nome seguro
                safe_name = re.sub(r'[^\w\.\-]', '_', file.filename)
                
                # Salvar no S3 + MongoDB + local
                save_dish_image(target_slug, safe_name, content)
                saved += 1
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
        
        total = get_dish_image_count(target_slug)
        logger.info(f"[UPLOAD] {dish_name}: +{saved} fotos (total: {total})")
        
        return {"ok": True, "dish": dish_name, "saved": saved, "total_images": total, "errors": errors}
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@api_router.post("/upload/zip")
async def upload_zip(file: UploadFile = File(...)):
    """TRAVADO - Fotos protegidas."""
    return {"ok": False, "error": "Upload de fotos esta travado para preservar integridade do dataset."}


@api_router.get("/upload/status")
async def upload_status():
    """Retorna estatisticas do dataset atual usando MongoDB dish_storage."""
    from services.image_service import get_all_dishes_stats
    return get_all_dishes_stats()


@api_router.get("/ai/unknown")
async def check_unknown(file: UploadFile = File(...)):
    """
    Verifica se um prato e desconhecido (nao esta no indice).
    Útil para identificar pratos que precisam ser cadastrados.
    """
    try:
        from ai.index import get_index
        
        index = get_index()
        if not index.is_ready():
            return {"ok": False, "message": "Índice nao carregado"}
        
        content = await file.read()
        results = index.search(content, top_k=1)
        
        if results and results[0].get('score', 0) < 0.50:
            return {
                "ok": True,
                "is_unknown": True,
                "best_match": results[0].get('dish'),
                "score": results[0].get('score'),
                "message": "Prato nao reconhecido. Considere cadastra-lo via /api/ai/learn"
            }
        else:
            return {
                "ok": True,
                "is_unknown": False,
                "best_match": results[0].get('dish') if results else None,
                "score": results[0].get('score') if results else 0,
                "message": "Prato reconhecido no indice"
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.post("/ai/identify-flash")
async def identify_with_gemini_flash(
    file: UploadFile = File(...),
    pin: Optional[str] = Form(None),
    nome: Optional[str] = Form(None),
    restaurant: Optional[str] = Form(None)
):
    """
    Identificacao DIRETA usando Gemini Flash.
    HARD LOCK: Bloqueado quando restaurant=cibi_sana.
    """
    # HARD LOCK: Cibi Sana -> Gemini totalmente bloqueado
    is_cibi_sana = (restaurant or '').strip().lower() == 'cibi_sana'
    if is_cibi_sana:
        logger.info("[HARD LOCK] identify-flash BLOQUEADO - Cibi Sana")
        return JSONResponse(
            status_code=403,
            content={"ok": False, "error": "Gemini nao disponivel dentro do Cibi Sana.", "blocked_by": "cibi_sana_hard_lock"}
        )
    
    start_time = time.time()
    
    try:
        from services.gemini_flash_service import (
            identify_dish_gemini_flash,
            is_gemini_flash_available,
            get_gemini_flash_status
        )
        
        if not is_gemini_flash_available():
            return JSONResponse(
                status_code=503,
                content={"ok": False, "error": "Gemini Flash nao configurado"}
            )
        
        content = await file.read()
        
        if len(content) == 0:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "Arquivo de imagem vazio"}
            )
        
        # Buscar perfil do usuario para alertas personalizados
        user_profile = None
        if pin and nome:
            from services.profile_service import hash_pin
            pin_hash = hash_pin(pin)
            user_profile = await db.users.find_one(
                {"pin_hash": pin_hash, "nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
                {"_id": 0}
            )
        
        # Chamar Gemini Flash
        result = await identify_dish_gemini_flash(content, user_profile)
        
        elapsed_ms = (time.time() - start_time) * 1000
        result["total_time_ms"] = round(elapsed_ms, 2)
        
        if result.get("ok"):
            logger.info(f"[Gemini Flash] ✅ {result.get('nome')} em {elapsed_ms:.0f}ms")
            if await get_setting("ENABLE_PROCESSING_METRICS"):
                save_processing_metrics({
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_ms": round(elapsed_ms, 2),
                    "dish_name": result.get('nome', ''),
                    "confidence_score": result.get('score', 0),
                    "engine_used": "GEMINI"
                })
        else:
            logger.warning(f"[Gemini Flash] ❌ Erro: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"[Gemini Flash] Erro: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.get("/ai/flash-status")
async def gemini_flash_status():
    """Status do servico Gemini Flash"""
    from services.gemini_flash_service import get_gemini_flash_status
    return get_gemini_flash_status()


@api_router.get("/ai/google-quota-status")
async def google_quota_status():
    """
    Verifica se a cota do Google API esta disponivel.
    Faz um teste rapido com texto simples (custo minimo).
    Útil para saber quando a cota gratuita foi renovada.
    """
    import time
    from google import genai
    
    google_key = os.environ.get('GOOGLE_API_KEY')
    
    if not google_key:
        return {
            "ok": False,
            "google_api_available": False,
            "message": "GOOGLE_API_KEY nao configurada",
            "recommendation": "Configure a chave em backend/.env"
        }
    
    try:
        client = genai.Client(api_key=google_key)
        
        start = time.time()
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents='Diga apenas: OK'
        )
        elapsed_ms = (time.time() - start) * 1000
        
        return {
            "ok": True,
            "google_api_available": True,
            "message": "✅ Cota do Google disponivel! API funcionando.",
            "response_time_ms": round(elapsed_ms, 2),
            "model": "gemini-2.0-flash-lite",
            "recommendation": "Sistema usando Google API (mais rapido e barato)"
        }
        
    except Exception as e:
        error_str = str(e)
        
        if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
            return {
                "ok": True,
                "google_api_available": False,
                "message": "❌ Cota do Google esgotada (429)",
                "error": "RESOURCE_EXHAUSTED",
                "recommendation": "Aguarde renovacao (~24h) ou use Emergent Key como fallback",
                "check_quota_url": "https://aistudio.google.com/"
            }
        else:
            return {
                "ok": False,
                "google_api_available": False,
                "message": f"Erro na API: {error_str[:100]}",
                "error": error_str[:200],
                "recommendation": "Verifique a configuracao da GOOGLE_API_KEY"
            }


@api_router.post("/ai/create-dish")
async def create_new_dish(
    file: UploadFile = File(...),
    dish_name: str = Form("")
):
    """
    Cria um novo prato usando IA para gerar todas as informacoes.
    Salva a foto e adiciona ao banco de dados.
    REGRA: Se ja existe prato similar no banco, adiciona foto ao existente ao inves de criar novo.
    """
    try:
        import uuid
        from datetime import datetime
        from pathlib import Path
        from difflib import SequenceMatcher
        from services.generic_ai import identify_unknown_dish
        
        if not dish_name.strip():
            return {"ok": False, "error": "Nome do prato e obrigatorio"}
        
        content = await file.read()
        
        # Gerar slug do nome fornecido
        slug = dish_name.lower().strip()
        slug = ''.join(c for c in slug if c.isalnum() or c == ' ')
        slug = slug.replace(' ', '_')
        
        # VERIFICAR SE JÁ EXISTE PRATO SIMILAR NO BANCO (MongoDB)
        existing_match = None
        
        async for dish_doc in db.dishes.find({}, {"_id": 0, "slug": 1, "nome": 1}):
            existing_name = dish_doc.get('nome', '').lower()
            existing_slug = dish_doc.get('slug', '')
            similarity = SequenceMatcher(None, dish_name.lower(), existing_name).ratio()
            if similarity > 0.85 or existing_slug == slug:
                existing_match = existing_slug
                logger.info(f"[CREATE] Prato similar encontrado: {existing_match} ({similarity:.0%})")
                break
        
        # Se encontrou match, adiciona foto ao prato existente E atualiza informacoes com IA
        if existing_match:
            from services.image_service import save_dish_image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{existing_match}_{timestamp}_{unique_id}.jpg"
            
            # Salvar no S3 + MongoDB + local
            save_dish_image(existing_match, filename, content)
            
            # CHAMAR IA para atualizar informacoes do prato
            try:
                from services.generic_ai import fix_dish_data_with_ai
                
                # Carregar info atual do MongoDB
                current_info = await db.dishes.find_one({"slug": existing_match}, {"_id": 0}) or {}
                
                # Atualizar nome se o usuario digitou diferente (correcao)
                if dish_name.strip() and dish_name.strip().lower() != current_info.get('nome', '').lower():
                    current_info['nome'] = dish_name.strip()
                    logger.info(f"[CREATE] Nome atualizado: {current_info.get('nome')} -> {dish_name.strip()}")
                
                # Chamar IA para completar informacoes faltantes
                ai_result = await fix_dish_data_with_ai(content, current_info)
                
                if ai_result.get('ok'):
                    # Mesclar informacoes (IA complementa o que esta faltando)
                    updated_info = {**current_info}
                    for key, value in ai_result.items():
                        if key == 'ok':
                            continue
                        if key == 'nutricao':
                            nut = updated_info.get('nutricao', {})
                            ai_nut = value or {}
                            for nk, nv in ai_nut.items():
                                if not nut.get(nk) and nv:
                                    nut[nk] = nv
                            updated_info['nutricao'] = nut
                        elif not updated_info.get(key) and value:
                            updated_info[key] = value
                    
                    if dish_name.strip():
                        updated_info['nome'] = dish_name.strip()
                    
                    updated_info['slug'] = existing_match
                    
                    # Salvar no MongoDB
                    await db.dishes.update_one(
                        {"slug": existing_match},
                        {"$set": updated_info},
                        upsert=True
                    )
                    
                    logger.info(f"[CREATE] Informacoes atualizadas com IA para: {existing_match}")
            except Exception as e:
                logger.error(f"[CREATE] Erro ao atualizar com IA: {e}")
            
            return {
                "ok": True,
                "message": f"✅ Prato '{dish_name}' salvo! Foto e informacoes atualizadas.",
                "slug": existing_match,
                "action": "updated_existing"
            }
        
        # Usar IA para gerar informacoes do prato
        logger.info(f"Gerando informacoes para novo prato: {dish_name}")
        ai_result = await identify_unknown_dish(content)
        
        # Preparar informacoes do prato
        dish_info = {
            "nome": dish_name.strip(),
            "slug": slug,
            "categoria": ai_result.get("categoria", "outros"),
            "category_emoji": ai_result.get("category_emoji", "🍽️"),
            "descricao": ai_result.get("descricao", f"{dish_name} - prato cadastrado pelo usuario"),
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
            "contem_gluten": any("gluten" in r.lower() for r in ai_result.get("riscos", [])),
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
        
        # Criar diretorio e salvar imagem no S3 + MongoDB + local
        from services.image_service import save_dish_image
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{slug}_{timestamp}_{unique_id}.jpg"
        
        save_dish_image(slug, filename, content)
        
        logger.info(f"Novo prato criado: {dish_name} -> {slug}")
        
        return {
            "ok": True,
            "message": f"Prato '{dish_name}' criado com sucesso!",
            "dish_slug": slug,
            "dish_name": dish_name,
            "dish_info": dish_info,
            "file_saved": filename,
            "note": "Execute /api/ai/reindex para incorporar ao indice de busca"
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar prato: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.post("/ai/create-dish-local")
async def create_dish_local(
    file: UploadFile = File(...),
    dish_name: str = Form("")
):
    """
    Cria/corrige um prato usando APENAS dados LOCAIS, SEM chamar IA, SEM gastar creditos.
    Usa o local_dish_updater para preencher os dados baseado no nome.
    """
    try:
        import uuid
        import json
        from datetime import datetime
        from pathlib import Path
        from difflib import SequenceMatcher
        from services.local_dish_updater import atualizar_prato_local, encontrar_tipo_prato, PRATOS_COMPLETOS
        from services.local_dish_updater import detectar_categoria_basica, detectar_alergenos_por_nome
        
        if not dish_name.strip():
            return {"ok": False, "error": "Nome do prato e obrigatorio"}
        
        content = await file.read()
        
        # Gerar slug do nome fornecido
        slug = dish_name.lower().strip()
        slug = ''.join(c for c in slug if c.isalnum() or c == ' ')
        slug = slug.replace(' ', '_')
        
        # VERIFICAR SE JÁ EXISTE PRATO SIMILAR NO BANCO (MongoDB)
        existing_match = None
        
        async for dish_doc in db.dishes.find({}, {"_id": 0, "slug": 1, "nome": 1}):
            existing_name = dish_doc.get('nome', '').lower()
            existing_slug = dish_doc.get('slug', '')
            similarity = SequenceMatcher(None, dish_name.lower(), existing_name).ratio()
            if similarity > 0.85 or existing_slug == slug:
                existing_match = existing_slug
                logger.info(f"[CREATE-LOCAL] Prato similar encontrado: {existing_match} ({similarity:.0%})")
                break
        
        # Se encontrou match, adiciona foto ao prato existente E atualiza com dados locais
        if existing_match:
            from services.image_service import save_dish_image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{existing_match}_correct_{timestamp}_{unique_id}.jpg"
            
            # Salvar no S3 + MongoDB + local
            save_dish_image(existing_match, filename, content)
            
            # Usar local_dish_updater para preencher dados faltantes
            result = atualizar_prato_local(existing_match, novo_nome=dish_name.strip())
            
            return {
                "ok": True,
                "message": f"Correcao salva! '{dish_name}' atualizado SEM usar creditos.",
                "slug": existing_match,
                "action": "updated_existing_local",
                "credits_used": 0
            }
        
        # CRIAR NOVO PRATO com dados LOCAIS
        from services.image_service import save_dish_image
        
        # Salvar imagem no S3 + MongoDB + local
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{slug}_{timestamp}_{unique_id}.jpg"
        
        save_dish_image(slug, filename, content)
        
        # Gerar dados usando regras LOCAIS
        tipo = encontrar_tipo_prato(dish_name)
        categoria = detectar_categoria_basica(dish_name)
        alergenos = detectar_alergenos_por_nome(dish_name)
        
        # Pegar template se existir
        dados_template = PRATOS_COMPLETOS.get(tipo, {})
        
        # Emoji baseado na categoria
        emoji_map = {"vegano": "🌱", "vegetariano": "🥚", "proteina animal": "🍖"}
        
        dish_info = {
            "nome": dish_name.strip(),
            "slug": slug,
            "categoria": categoria,
            "category_emoji": emoji_map.get(categoria, "🍽️"),
            "descricao": dados_template.get('descricao', f"{dish_name} - prato do Cibi Sana"),
            "ingredientes": dados_template.get('ingredientes', []),
            "beneficios": dados_template.get('beneficios', []),
            "riscos": dados_template.get('riscos', []),
            "tecnica": dados_template.get('tecnica', ''),
            "nutricao": dados_template.get('nutricao', {"calorias": "~150 kcal", "proteinas": "~8g", "carboidratos": "~20g", "gorduras": "~5g"}),
            "contem_gluten": alergenos.get('contem_gluten', False),
            "contem_lactose": alergenos.get('contem_lactose', False),
            "contem_ovo": alergenos.get('contem_ovo', False),
            "contem_castanhas": alergenos.get('contem_castanhas', False),
            "contem_frutos_mar": alergenos.get('contem_frutos_mar', False),
            "contem_soja": alergenos.get('contem_soja', False),
            "indice_glicemico": dados_template.get('indice_glicemico', 'moderado'),
            "tempo_digestao": dados_template.get('tempo_digestao', '2-3 horas'),
            "melhor_horario": dados_template.get('melhor_horario', 'Almoco'),
            "combina_com": dados_template.get('combina_com', []),
            "evitar_com": dados_template.get('evitar_com', []),
            "origem": "user_created_local"
        }
        
        # Salvar no MongoDB em vez de dish_info.json local
        await db.dishes.update_one(
            {"slug": slug},
            {"$set": dish_info},
            upsert=True
        )
        
        logger.info(f"[CREATE-LOCAL] Novo prato criado SEM IA: {dish_name} -> {slug}")
        
        return {
            "ok": True,
            "message": f"✅ Prato '{dish_name}' criado com sucesso SEM usar creditos!",
            "dish_slug": slug,
            "dish_name": dish_name,
            "dish_info": dish_info,
            "file_saved": filename,
            "credits_used": 0,
            "note": "Dados gerados localmente. Execute Atualizar na auditoria para completar."
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar prato local: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)}
        )


@api_router.get("/ai/ingredient-research/{ingredient}")
async def get_ingredient_research(ingredient: str):
    """
    Busca pesquisas cientificas recentes sobre um ingrediente.
    Retorna informacoes da OMS, ANVISA, estudos cientificos, etc.
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
    original_dish: str = Form(""),
    score: str = Form("0"),
    confidence: str = Form(""),
    source: str = Form("")
):
    """
    Recebe feedback sobre reconhecimento de prato.
    - Se correto: salva a foto no dataset do prato
    - Se incorreto: salva no prato correto informado pelo usuario
    - Salva score/confidence para calibracao via Youden's J
    """
    try:
        import uuid
        from datetime import datetime
        
        # Garantir que diretorio base existe
        os.makedirs("/app/datasets/organized", exist_ok=True)
        
        content = await file.read()
        is_correct_bool = is_correct.lower() == "true"
        
        if not dish_slug:
            return {"ok": False, "message": "dish_slug e obrigatorio"}
        
        # Salvar imagem no S3 + MongoDB + local via image_service
        from services.image_service import save_dish_image, find_dish_slug_match
        
        # Encontrar slug real do prato
        target_slug = find_dish_slug_match(dish_slug) or dish_slug
        
        # Gerar nome unico para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        feedback_type = "correct" if is_correct_bool else "corrected"
        filename = f"{target_slug}_{feedback_type}_{timestamp}_{unique_id}.jpg"
        
        # Salvar imagem no S3 + MongoDB + local
        save_dish_image(target_slug, filename, content)
        
        # Parse score to float
        try:
            score_float = float(score)
        except (ValueError, TypeError):
            score_float = 0.0
        
        # Log no MongoDB para analise posterior e calibracao
        feedback_doc = {
            "dish_slug": dish_slug,
            "target_slug": target_slug,
            "original_dish": original_dish if not is_correct_bool else dish_slug,
            "is_correct": is_correct_bool,
            "score": score_float,
            "confidence": confidence,
            "source": source,
            "file_path": f"s3://soulnutri/dishes/{target_slug}/{filename}",
            "created_at": datetime.utcnow()
        }
        await db.feedback.insert_one(feedback_doc)
        
        # LIMPAR CACHE para forcar re-identificacao
        from services.cache_service import clear_cache
        clear_cache()
        
        logger.info(f"Feedback salvo: {feedback_type} para {dish_slug} -> {filename}")
        
        return {
            "ok": True,
            "message": f"Feedback registrado! Foto salva para {target_slug}",
            "file_saved": filename,
            "is_correct": is_correct_bool,
            "note": "Execute /api/ai/reindex para incorporar ao indice"
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
    Retorna estatisticas dos feedbacks recebidos.
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


@api_router.post("/ai/calibration/log")
async def log_calibration_sample(
    dish_clip: str = Form(""),
    dish_real: str = Form(""),
    is_correct: str = Form("true"),
    score: str = Form("0"),
    confidence: str = Form(""),
    source: str = Form("")
):
    """
    Registra uma amostra de calibracao (sem upload de imagem).
    Chamado automaticamente pelo app quando usuario confirma ou corrige um prato.
    """
    try:
        from datetime import datetime
        
        is_correct_bool = is_correct.lower() == "true"
        try:
            score_float = float(score)
        except (ValueError, TypeError):
            score_float = 0.0
        
        if score_float < 0:
            return {"ok": False, "message": "Score invalido"}
        
        doc = {
            "dish_clip": dish_clip,
            "dish_real": dish_real if not is_correct_bool else dish_clip,
            "is_correct": is_correct_bool,
            "score": score_float,
            "confidence": confidence,
            "source": source,
            "created_at": datetime.utcnow()
        }
        result = await db.calibration_log.insert_one(doc)
        
        logger.info(f"[CALIBRATION] {dish_clip} -> {'OK' if is_correct_bool else 'ERRADO (real: ' + dish_real + ')'} score={score_float:.2%}")
        
        return {
            "ok": True,
            "id": str(result.inserted_id),
            "message": "Amostra registrada"
        }
    except Exception as e:
        logger.error(f"Erro ao registrar calibracao: {e}")
        return {"ok": False, "error": str(e)}


@api_router.delete("/ai/calibration/clear-all")
async def clear_all_calibration(confirm: bool = False):
    """Zera todas as amostras de calibracao. Requer confirm=true."""
    if not confirm:
        count = await db.calibration_log.count_documents({})
        return {"ok": False, "message": f"Tem certeza? Existem {count} amostras. Envie confirm=true para confirmar.", "current_count": count}
    try:
        result = await db.calibration_log.delete_many({})
        logger.info(f"[CALIBRATION] Todas as amostras zeradas: {result.deleted_count} removidas")
        return {"ok": True, "deleted_count": result.deleted_count, "message": f"{result.deleted_count} amostras removidas"}
    except Exception as e:
        logger.error(f"Erro ao zerar calibracao: {e}")
        return {"ok": False, "error": str(e)}


@api_router.delete("/ai/calibration/{sample_id}")
async def delete_calibration_sample(sample_id: str):
    """Deleta uma amostra de calibracao pelo ID."""
    try:
        from bson import ObjectId
        result = await db.calibration_log.delete_one({"_id": ObjectId(sample_id)})
        if result.deleted_count > 0:
            return {"ok": True, "message": "Amostra deletada"}
        return {"ok": False, "message": "Amostra nao encontrada"}
    except Exception as e:
        logger.error(f"Erro ao deletar amostra: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/ai/calibration")
async def get_calibration_data():
    """
    Retorna dados de calibracao da colecao calibration_log.
    Estatisticas, distribuicao de scores e calculo de Youden's J.
    """
    try:
        # Buscar todas as amostras
        pipeline_samples = [
            {"$project": {
                "_id": {"$toString": "$_id"},
                "dish_clip": 1,
                "dish_real": 1,
                "is_correct": 1,
                "score": 1,
                "confidence": 1,
                "source": 1,
                "created_at": 1
            }},
            {"$sort": {"created_at": -1}}
        ]
        samples = await db.calibration_log.aggregate(pipeline_samples).to_list(1000)
        
        # Estatisticas gerais
        total = len(samples)
        correct_samples = [s for s in samples if s.get('is_correct')]
        incorrect_samples = [s for s in samples if not s.get('is_correct')]
        
        correct_scores = [s['score'] for s in correct_samples if s.get('score', 0) > 0]
        incorrect_scores = [s['score'] for s in incorrect_samples if s.get('score', 0) > 0]
        
        stats = {
            "total_samples": total,
            "correct_count": len(correct_samples),
            "incorrect_count": len(incorrect_samples),
            "correct_scores": {
                "min": round(min(correct_scores), 4) if correct_scores else None,
                "max": round(max(correct_scores), 4) if correct_scores else None,
                "avg": round(sum(correct_scores) / len(correct_scores), 4) if correct_scores else None,
                "median": round(sorted(correct_scores)[len(correct_scores)//2], 4) if correct_scores else None
            },
            "incorrect_scores": {
                "min": round(min(incorrect_scores), 4) if incorrect_scores else None,
                "max": round(max(incorrect_scores), 4) if incorrect_scores else None,
                "avg": round(sum(incorrect_scores) / len(incorrect_scores), 4) if incorrect_scores else None,
                "median": round(sorted(incorrect_scores)[len(incorrect_scores)//2], 4) if incorrect_scores else None
            }
        }
        
        # Calculo de Youden's J para threshold otimo
        youden_result = None
        if len(correct_scores) >= 5 and len(incorrect_scores) >= 5:
            all_scores = correct_scores + incorrect_scores
            thresholds = sorted(set([round(s, 2) for s in all_scores]))
            
            best_j = -1
            best_threshold = 0.85
            best_sensitivity = 0
            best_specificity = 0
            
            for t in thresholds:
                # Sensibilidade: % corretos aceitos (score >= t)
                tp = sum(1 for s in correct_scores if s >= t)
                sensitivity = tp / len(correct_scores) if correct_scores else 0
                
                # Especificidade: % incorretos rejeitados (score < t)
                tn = sum(1 for s in incorrect_scores if s < t)
                specificity = tn / len(incorrect_scores) if incorrect_scores else 0
                
                j = sensitivity + specificity - 1
                if j > best_j:
                    best_j = j
                    best_threshold = t
                    best_sensitivity = sensitivity
                    best_specificity = specificity
            
            youden_result = {
                "optimal_threshold": round(best_threshold, 4),
                "j_index": round(best_j, 4),
                "sensitivity": round(best_sensitivity, 4),
                "specificity": round(best_specificity, 4),
                "interpretation": f"Com threshold {best_threshold:.2%}: aceita {best_sensitivity:.0%} dos corretos, rejeita {best_specificity:.0%} dos errados"
            }
        
        # Distribuicao de scores por faixa
        distribution = {
            "0.90_1.00": {"correct": 0, "incorrect": 0},
            "0.85_0.90": {"correct": 0, "incorrect": 0},
            "0.80_0.85": {"correct": 0, "incorrect": 0},
            "0.75_0.80": {"correct": 0, "incorrect": 0},
            "0.70_0.75": {"correct": 0, "incorrect": 0},
            "0.65_0.70": {"correct": 0, "incorrect": 0},
            "0.60_0.65": {"correct": 0, "incorrect": 0},
            "0.50_0.60": {"correct": 0, "incorrect": 0},
            "0.00_0.50": {"correct": 0, "incorrect": 0}
        }
        
        for s in samples:
            score_val = s.get('score', 0)
            is_correct_val = s.get('is_correct', False)
            key = "correct" if is_correct_val else "incorrect"
            
            if score_val >= 0.90: distribution["0.90_1.00"][key] += 1
            elif score_val >= 0.85: distribution["0.85_0.90"][key] += 1
            elif score_val >= 0.80: distribution["0.80_0.85"][key] += 1
            elif score_val >= 0.75: distribution["0.75_0.80"][key] += 1
            elif score_val >= 0.70: distribution["0.70_0.75"][key] += 1
            elif score_val >= 0.65: distribution["0.65_0.70"][key] += 1
            elif score_val >= 0.60: distribution["0.60_0.65"][key] += 1
            elif score_val >= 0.50: distribution["0.50_0.60"][key] += 1
            else: distribution["0.00_0.50"][key] += 1
        
        # Thresholds atuais
        current_thresholds = {
            "alta": 0.90,
            "media": 0.50,
            "rejeicao": 0.50
        }
        
        # Converter datetime para string nos samples
        for s in samples:
            if 'created_at' in s and hasattr(s['created_at'], 'isoformat'):
                s['created_at'] = s['created_at'].isoformat()
        
        return {
            "ok": True,
            "stats": stats,
            "distribution": distribution,
            "youden": youden_result,
            "current_thresholds": current_thresholds,
            "samples": samples[:200]
        }
    except Exception as e:
        logger.error(f"Erro ao buscar dados de calibracao: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/ai/identify-multi")
async def identify_multiple_items(
    file: UploadFile = File(...),
    restaurant: Optional[str] = Form(None)
):
    """
    Identifica MÚLTIPLOS itens em uma imagem de refeicao.
    HARD LOCK: Cibi Sana -> Apenas CLIP local, Gemini bloqueado.
    """
    start_time = time.time()
    
    # HARD LOCK: Cibi Sana -> bloquear Gemini no multi também
    is_cibi_sana = (restaurant or '').strip().lower() == 'cibi_sana'
    if is_cibi_sana:
        logger.info("[HARD LOCK] identify-multi Cibi Sana - Gemini BLOQUEADO, usando CLIP only")
    
    try:
        from services.hybrid_identify_v5 import identify_multi_v5
        
        content = await file.read()
        
        if len(content) == 0:
            return {"ok": False, "error": "Arquivo de imagem vazio"}
        
        logger.info("[v5] Identificacao com busca ampla e filtragem inteligente...")
        result = await identify_multi_v5(content)
        
        elapsed_ms = (time.time() - start_time) * 1000
        result['search_time_ms'] = round(elapsed_ms, 2)
        
        if result.get('ok'):
            principal = result.get('principal', {})
            acomp_count = len(result.get('acompanhamentos', []))
            local_count = result.get('itens_do_buffet', 0)
            logger.info(f"[MULTI-HÍBRIDO] {principal.get('nome', 'N/A')} + {acomp_count} acomp. ({local_count} do buffet) em {elapsed_ms:.0f}ms")
        else:
            logger.warning(f"[MULTI-HÍBRIDO] Erro: {result.get('error')}")
        
        # Formatar para compatibilidade com frontend
        if result.get('ok'):
            # Converter para formato esperado pelo frontend
            itens = []
            if result.get('principal'):
                itens.append({
                    'nome': result['principal']['nome'],
                    'categoria': result['principal'].get('categoria', 'proteina animal'),
                    'score': result['principal'].get('score', 0.7),
                    'source': result['principal'].get('source', 'local')
                })
            
            for acomp in result.get('acompanhamentos', []):
                itens.append({
                    'nome': acomp['nome'],
                    'categoria': acomp.get('categoria', 'vegano'),
                    'score': acomp.get('score', 0.6),
                    'source': acomp.get('source', 'local')
                })
            
            result['itens'] = itens
        
        return result
        
    except Exception as e:
        logger.error(f"Erro na identificacao multipla hibrida: {e}")
        return {
            "ok": False,
            "error": str(e),
            "search_time_ms": round((time.time() - start_time) * 1000, 2)
        }


# ═══════════════════════════════════════════════════════════════════════
# FEED DE NOTICIAS E CURIOSIDADES NUTRICIONAIS
# ═══════════════════════════════════════════════════════════════════════

@api_router.get("/news/feed")
async def get_news_feed_endpoint(limit: int = 20, categoria: str = None, skip: int = 0):
    """Retorna feed de noticias/curiosidades nutricionais verificadas."""
    try:
        from services.news_service import get_news_feed, get_news_stats
        
        items = get_news_feed(limit=limit, categoria=categoria, skip=skip)
        stats = get_news_stats()
        
        return {
            "ok": True,
            "items": items,
            "total": stats["total"],
            "categories": stats["categories"],
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Erro ao buscar feed: {e}")
        return {"ok": False, "error": str(e), "items": []}


@api_router.post("/news/generate")
async def generate_news_endpoint(count: int = 6):
    """Gera novas noticias/curiosidades com IA (verificadas). Admin only."""
    try:
        from services.news_service import generate_news_batch
        
        items = await generate_news_batch(count=count)
        
        return {
            "ok": True,
            "generated": len(items),
            "items": items,
            "message": f"{len(items)} noticias geradas e verificadas"
        }
    except Exception as e:
        logger.error(f"Erro ao gerar noticias: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/news/like/{content_hash}")
async def like_news_endpoint(content_hash: str):
    """Incrementa like de uma noticia."""
    try:
        from services.news_service import toggle_news_like
        likes = toggle_news_like(content_hash)
        return {"ok": True, "likes": likes}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_router.post("/news/view/{content_hash}")
async def view_news_endpoint(content_hash: str):
    """Registra visualizacao de uma noticia."""
    try:
        from services.news_service import increment_news_view
        increment_news_view(content_hash)
        return {"ok": True}
    except Exception as e:
        return {"ok": False}


@api_router.get("/news/categories")
async def get_news_categories():
    """Retorna categorias disponiveis de noticias."""
    from services.news_service import CATEGORIES
    return {"ok": True, "categories": CATEGORIES}


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
    Registra um novo usuario Premium com PIN local.
    Calcula automaticamente a meta calorica sugerida.
    """
    try:
        from services.profile_service import hash_pin, calcular_tmb, calcular_meta_calorica
        from datetime import datetime, timezone
        
        # Validacoes
        if len(pin) < 4 or len(pin) > 6:
            return {"ok": False, "error": "PIN deve ter entre 4 e 6 digitos"}
        
        if not pin.isdigit():
            return {"ok": False, "error": "PIN deve conter apenas numeros"}
        
        # Calcular meta calorica
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
            "premium_ativo": True,
            "is_trial": True,
            "premium_trial_start": datetime.now(timezone.utc).isoformat(),
            "premium_expira_em": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Salvar no MongoDB
        result = await db.users.insert_one(perfil)
        user_id = str(result.inserted_id)
        
        logger.info(f"[PREMIUM] Novo usuario registrado: {nome}")
        
        return {
            "ok": True,
            "user_id": user_id,
            "nome": nome,
            "meta_calorica": meta_info,
            "message": f"Bem-vindo ao SoulNutri Premium, {nome}!"
        }
        
    except Exception as e:
        logger.error(f"Erro ao registrar usuario: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/premium/login")
async def login_user(pin: str = Form(...), nome: str = Form(...)):
    """
    Login com Nome + PIN.
    Verifica tambem se o Premium esta liberado pelo admin.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime
        
        pin_hash = hash_pin(pin)
        # Buscar por nome E pin_hash
        user = await db.users.find_one(
            {"pin_hash": pin_hash, "nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
            {"_id": 0, "pin_hash": 0}
        )
        
        if not user:
            return {"ok": False, "error": "Nome ou PIN incorreto"}
        
        # Verificar se Premium esta ativo e nao expirou (trial de 7 dias)
        premium_ativo = user.get("premium_ativo", False)
        premium_expira_em = user.get("premium_expira_em")
        is_trial = user.get("is_trial", False)
        
        if premium_expira_em and premium_ativo:
            try:
                expiracao = datetime.fromisoformat(premium_expira_em.replace('Z', '+00:00'))
                agora = datetime.now(timezone.utc)
                if agora > expiracao:
                    premium_ativo = False
                    await db.users.update_one(
                        {"nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
                        {"$set": {"premium_ativo": False, "premium_expirado": True, "trial_expirado": True}}
                    )
                    logger.info(f"[PREMIUM] Trial expirado para {user.get('nome')}")
            except Exception as e:
                logger.warning(f"[PREMIUM] Erro ao verificar expiracao: {e}")
        
        user["premium_ativo"] = premium_ativo
        user["is_trial"] = is_trial
        
        # Calcular dias restantes do trial
        dias_restantes = None
        if premium_ativo and premium_expira_em:
            try:
                expiracao = datetime.fromisoformat(premium_expira_em.replace('Z', '+00:00'))
                dias_restantes = max(0, (expiracao - datetime.now(timezone.utc)).days)
            except:
                pass
        user["dias_restantes_trial"] = dias_restantes
        
        if not premium_ativo:
            msg = f"Ola, {user['nome']}! "
            if user.get("trial_expirado") or user.get("premium_expirado"):
                msg += "Seu periodo de teste expirou. Entre em contato para ativar o Premium."
            else:
                msg += "Seu acesso Premium ainda nao foi liberado. Entre em contato para ativacao."
            return {
                "ok": True,
                "user": user,
                "premium_bloqueado": True,
                "message": msg
            }
        
        # Buscar consumo do dia
        hoje = datetime.now().strftime("%Y-%m-%d")
        daily_log = await db.daily_logs.find_one(
            {"user_nome": user["nome"], "data": hoje},
            {"_id": 0}
        )
        
        return {
            "ok": True,
            "user": user,
            "daily_log": daily_log,
            "message": f"Ola, {user['nome']}!"
        }
        
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return {"ok": False, "error": str(e)}


class PerfilUsuario(BaseModel):
    peso: Optional[float] = None
    altura: Optional[float] = None
    idade: Optional[int] = None
    sexo: Optional[str] = None
    nivel_atividade: Optional[str] = None
    restricoes: List[str] = []


class ProfileRequest(BaseModel):
    nome: str
    pin: str
    perfil: PerfilUsuario


@api_router.get("/premium/get-profile")
async def get_user_profile(pin: str, nome: str):
    """
    Obtem o perfil completo do usuario Premium para edicao.
    """
    try:
        from services.profile_service import hash_pin
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one(
            {"pin_hash": pin_hash, "nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
            {"_id": 0, "pin_hash": 0}
        )
        
        if not user:
            return {"ok": False, "error": "Usuario nao encontrado"}
        
        return {
            "ok": True,
            "profile": {
                "nome": user.get("nome"),
                "peso": user.get("peso"),
                "altura": user.get("altura"),
                "idade": user.get("idade"),
                "sexo": user.get("sexo"),
                "nivel_atividade": user.get("nivel_atividade"),
                "objetivo": user.get("objetivo"),
                "restricoes": user.get("restricoes", []),
                "alergias": user.get("alergias", []),
                "meta_calorica": user.get("meta_calorica")
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter perfil: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/premium/update-profile")
async def update_user_profile(
    pin: str = Form(...),
    nome: str = Form(...),
    peso: float = Form(...),
    altura: float = Form(...),
    idade: int = Form(...),
    sexo: str = Form(...),
    nivel_atividade: str = Form("moderado"),
    objetivo: str = Form("manter"),
    restricoes: str = Form("")
):
    """
    Atualiza o perfil do usuario Premium existente.
    Recalcula a meta calorica com os novos dados.
    """
    try:
        from services.profile_service import hash_pin, calcular_tmb, calcular_meta_calorica
        from datetime import datetime, timezone
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one(
            {"pin_hash": pin_hash, "nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}}
        )
        
        if not user:
            return {"ok": False, "error": "Usuario nao encontrado"}
        
        # Recalcular meta calorica
        tmb = calcular_tmb(peso, altura, idade, sexo)
        meta_info = calcular_meta_calorica(tmb, nivel_atividade, objetivo)
        
        # Preparar dados de atualizacao
        update_data = {
            "peso": peso,
            "altura": altura,
            "idade": idade,
            "sexo": sexo,
            "nivel_atividade": nivel_atividade,
            "objetivo": objetivo,
            "restricoes": [r.strip() for r in restricoes.split(",") if r.strip()],
            "meta_calorica": meta_info,
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Atualizar no MongoDB
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
        
        logger.info(f"[PREMIUM] Perfil atualizado: {nome}")
        
        return {
            "ok": True,
            "nome": nome,
            "meta_calorica": meta_info,
            "message": f"Perfil atualizado com sucesso, {nome}!"
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/premium/profile")
async def save_premium_profile(request: ProfileRequest):
    """
    Salva o perfil do usuario Premium para personalizacao das dicas.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime, timezone
        
        pin_hash = hash_pin(request.pin)
        user = await db.users.find_one(
            {"pin_hash": pin_hash, "nome": {"$regex": f"^{request.nome}$", "$options": "i"}}
        )
        
        if not user:
            return {"ok": False, "error": "Usuario nao encontrado"}
        
        # Converter para dict e adicionar timestamp
        perfil_dict = request.perfil.dict()
        perfil_dict['atualizado_em'] = datetime.now(timezone.utc)
        
        # Calcular TMB (Taxa Metabolica Basal) se tiver dados suficientes
        if perfil_dict.get('peso') and perfil_dict.get('altura') and perfil_dict.get('idade') and perfil_dict.get('sexo'):
            peso = perfil_dict['peso']
            altura = perfil_dict['altura']
            idade = perfil_dict['idade']
            sexo = perfil_dict['sexo']
            
            if sexo == 'masculino':
                tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
            else:
                tmb = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade)
            
            # Ajustar por nivel de atividade
            fatores = {'sedentario': 1.2, 'leve': 1.375, 'moderado': 1.55, 'intenso': 1.725}
            fator = fatores.get(perfil_dict.get('nivel_atividade', 'sedentario'), 1.2)
            
            perfil_dict['tmb'] = round(tmb, 0)
            perfil_dict['calorias_diarias'] = round(tmb * fator, 0)
        
        # Atualizar perfil no banco
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"perfil": perfil_dict}}
        )
        
        logger.info(f"[PREMIUM] Perfil atualizado: {request.nome}")
        
        return {
            "ok": True,
            "message": "Perfil salvo com sucesso",
            "perfil": perfil_dict
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar perfil: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/premium/log-meal")
async def log_meal(
    pin: str = Form(...),
    prato_nome: str = Form(...),
    calorias: float = Form(...),
    proteinas: float = Form(0),
    carboidratos: float = Form(0),
    gorduras: float = Form(0),
    porcao: str = Form("1 porcao"),
    source: str = Form("clip")
):
    """
    Registra uma refeicao no contador diario.
    source: 'clip' (Cibi Sana) ou 'gemini' (externo)
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime, timezone
        
        # Verificar usuario
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
            "hora": agora.strftime("%H:%M"),
            "source": source
        }
        
        # Atualizar ou criar log diario
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
        
        # Gerar alerta se necessario
        alerta = None
        if percentual >= 100:
            alerta = {"tipo": "limite", "mensagem": "🚨 Voce atingiu sua meta calorica diaria!"}
        elif percentual >= 90:
            alerta = {"tipo": "aviso", "mensagem": f"⚠️ Voce esta a {restante:.0f} kcal da sua meta!"}
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
        logger.error(f"Erro ao registrar refeicao: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/daily-summary")
async def get_daily_summary(pin: str):
    """
    Retorna resumo do consumo diario.
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
    Retorna historico de consumo dos ultimos X dias.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime, timedelta
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        # Buscar logs dos ultimos dias
        data_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
        
        cursor = db.daily_logs.find(
            {"user_nome": user["nome"], "data": {"$gte": data_inicio}},
            {"_id": 0}
        ).sort("data", -1)
        
        historico = await cursor.to_list(length=dias)
        
        # Calcular media
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
        logger.error(f"Erro ao buscar historico: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/weekly-analysis")
async def get_weekly_analysis(pin: str):
    """
    Retorna analise semanal completa com vitaminas, minerais e tendencias.
    NOVO: Contador Premium expandido.
    """
    try:
        from services.profile_service import hash_pin
        from services.nutrition_premium_service import analisar_consumo_semanal, analisar_consumo_diario
        from datetime import datetime, timedelta
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        # Buscar logs dos ultimos 7 dias
        data_inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        cursor = db.daily_logs.find(
            {"user_nome": user["nome"], "data": {"$gte": data_inicio}},
            {"_id": 0}
        )
        
        logs_semana = await cursor.to_list(length=100)
        
        # Converter logs para o formato esperado
        refeicoes_semana = []
        for log in logs_semana:
            for prato in log.get("pratos", []):
                refeicoes_semana.append({
                    "nome": prato.get("nome", ""),
                    "data": log.get("data", ""),
                    "hora": prato.get("hora", "12:00"),
                    "nutricao": {
                        "calorias": prato.get("calorias", 0),
                        "proteinas": prato.get("proteinas", 0),
                        "carboidratos": prato.get("carboidratos", 0),
                        "gorduras": prato.get("gorduras", 0)
                    },
                    "ingredientes": prato.get("ingredientes", [])
                })
        
        # Perfil do usuario
        perfil = user.get("perfil", {})
        if not perfil:
            perfil = {
                "peso": 70,
                "altura": 170,
                "idade": 30,
                "sexo": "M",
                "nivel_atividade": "moderado",
                "objetivo": "manter",
                "restricoes": []
            }
        
        # Analise semanal
        analise = analisar_consumo_semanal(refeicoes_semana, perfil)
        
        return {
            "ok": True,
            "nome": user["nome"],
            "periodo": f"{data_inicio} a {datetime.now().strftime('%Y-%m-%d')}",
            "analise": analise
        }
        
    except Exception as e:
        logger.error(f"Erro ao analisar semana: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/daily-full")
async def get_daily_full_analysis(pin: str):
    """
    Retorna analise diaria COMPLETA com vitaminas, minerais e alertas.
    NOVO: Contador Premium expandido.
    """
    try:
        from services.profile_service import hash_pin
        from services.nutrition_premium_service import analisar_consumo_diario
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
        
        # Converter log para lista de refeicoes
        refeicoes = []
        if daily_log:
            for prato in daily_log.get("pratos", []):
                refeicoes.append({
                    "nome": prato.get("nome", ""),
                    "hora": prato.get("hora", "12:00"),
                    "nutricao": {
                        "calorias": prato.get("calorias", 0),
                        "proteinas": prato.get("proteinas", 0),
                        "carboidratos": prato.get("carboidratos", 0),
                        "gorduras": prato.get("gorduras", 0)
                    },
                    "ingredientes": prato.get("ingredientes", [])
                })
        
        # Perfil do usuario
        perfil = user.get("perfil", {})
        if not perfil:
            perfil = {
                "peso": 70,
                "altura": 170,
                "idade": 30,
                "sexo": "M",
                "nivel_atividade": "moderado",
                "objetivo": "manter",
                "restricoes": []
            }
        
        # Analise completa
        analise = analisar_consumo_diario(refeicoes, perfil)
        
        return {
            "ok": True,
            "nome": user["nome"],
            "data": hoje,
            "analise": analise
        }
        
    except Exception as e:
        logger.error(f"Erro ao analisar dia: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/dashboard")
async def get_dashboard_premium(pin: str, periodo: str = "semana"):
    """
    Dashboard consolidado para usuarios Premium.
    Periodos: dia, semana, mes, ano
    Retorna: consumo de hoje, graficos, historico, alertas e estatisticas.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime, timedelta
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        # Definir periodo em dias
        periodos_dias = {"dia": 1, "semana": 7, "mes": 30, "ano": 365}
        dias = periodos_dias.get(periodo, 7)
        
        data_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
        hoje_str = datetime.now().strftime("%Y-%m-%d")
        
        # Buscar logs do periodo (limite maior para ano)
        limite_logs = 400 if periodo == "ano" else 100
        cursor = db.daily_logs.find(
            {"user_nome": user["nome"], "data": {"$gte": data_inicio}},
            {"_id": 0}
        ).sort("data", -1)
        
        logs = await cursor.to_list(length=limite_logs)
        
        # Consumo de hoje
        log_hoje = next((l for l in logs if l.get("data") == hoje_str), None)
        hoje = {
            "calorias": log_hoje.get("calorias_total", 0) if log_hoje else 0,
            "proteinas": log_hoje.get("proteinas_total", 0) if log_hoje else 0,
            "carboidratos": log_hoje.get("carboidratos_total", 0) if log_hoje else 0,
            "gorduras": log_hoje.get("gorduras_total", 0) if log_hoje else 0
        }
        
        # Dados para graficos baseados no periodo
        dias_grafico = []
        
        if periodo == "dia":
            # Para dia, mostrar as refeicoes individuais
            if log_hoje and log_hoje.get("pratos"):
                for i, prato in enumerate(log_hoje.get("pratos", [])[:10]):
                    dias_grafico.append({
                        "dia": prato.get("nome", f"Item {i+1}")[:15],
                        "data": hoje_str,
                        "calorias": prato.get("calorias", 0),
                        "proteinas": prato.get("proteinas", 0),
                        "carboidratos": prato.get("carboidratos", 0),
                        "gorduras": prato.get("gorduras", 0)
                    })
        elif periodo == "semana":
            # Últimos 7 dias
            dias_nomes = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
            for i in range(7):
                data = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
                dia_semana = (datetime.now() - timedelta(days=6-i)).weekday()
                log_dia = next((l for l in logs if l.get("data") == data), None)
                dias_grafico.append({
                    "dia": dias_nomes[dia_semana],
                    "data": data,
                    "calorias": log_dia.get("calorias_total", 0) if log_dia else 0,
                    "proteinas": log_dia.get("proteinas_total", 0) if log_dia else 0,
                    "carboidratos": log_dia.get("carboidratos_total", 0) if log_dia else 0,
                    "gorduras": log_dia.get("gorduras_total", 0) if log_dia else 0
                })
        elif periodo == "mes":
            # Agrupar por semana (4 semanas)
            for semana in range(4):
                inicio_semana = 28 - (semana + 1) * 7
                fim_semana = 28 - semana * 7
                calorias_semana = 0
                proteinas_semana = 0
                carboidratos_semana = 0
                gorduras_semana = 0
                for i in range(inicio_semana, fim_semana):
                    data = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                    log_dia = next((l for l in logs if l.get("data") == data), None)
                    if log_dia:
                        calorias_semana += log_dia.get("calorias_total", 0)
                        proteinas_semana += log_dia.get("proteinas_total", 0)
                        carboidratos_semana += log_dia.get("carboidratos_total", 0)
                        gorduras_semana += log_dia.get("gorduras_total", 0)
                dias_grafico.append({
                    "dia": f"Sem {4-semana}",
                    "calorias": calorias_semana / 7,  # Media diaria da semana
                    "proteinas": proteinas_semana / 7,
                    "carboidratos": carboidratos_semana / 7,
                    "gorduras": gorduras_semana / 7
                })
        elif periodo == "ano":
            # Agrupar por mes (12 meses)
            meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            hoje = datetime.now()
            for i in range(12):
                mes_data = hoje - timedelta(days=30 * (11 - i))
                mes_nome = meses_nomes[mes_data.month - 1]
                mes_str = mes_data.strftime("%Y-%m")
                
                logs_mes = [l for l in logs if l.get("data", "").startswith(mes_str)]
                dias_com_dados = len([l for l in logs_mes if l.get("calorias_total", 0) > 0])
                
                calorias_mes = sum(l.get("calorias_total", 0) for l in logs_mes)
                proteinas_mes = sum(l.get("proteinas_total", 0) for l in logs_mes)
                carboidratos_mes = sum(l.get("carboidratos_total", 0) for l in logs_mes)
                gorduras_mes = sum(l.get("gorduras_total", 0) for l in logs_mes)
                
                dias_grafico.append({
                    "dia": mes_nome,
                    "calorias": calorias_mes / max(dias_com_dados, 1),  # Media diaria
                    "proteinas": proteinas_mes / max(dias_com_dados, 1),
                    "carboidratos": carboidratos_mes / max(dias_com_dados, 1),
                    "gorduras": gorduras_mes / max(dias_com_dados, 1),
                    "dias_registrados": dias_com_dados
                })
        
        # Estatisticas
        dias_com_log = len([l for l in logs if l.get("calorias_total", 0) > 0])
        total_calorias = sum(l.get("calorias_total", 0) for l in logs)
        total_proteinas = sum(l.get("proteinas_total", 0) for l in logs)
        total_carboidratos = sum(l.get("carboidratos_total", 0) for l in logs)
        total_gorduras = sum(l.get("gorduras_total", 0) for l in logs)
        total_pratos = sum(len(l.get("pratos", [])) for l in logs)
        
        # Calcular streak (dias seguidos)
        streak = 0
        for i in range(min(dias, 365)):
            data = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if any(l.get("data", "") == data for l in logs):
                streak += 1
            else:
                break
        
        # Metas do usuario
        metas_default = {
            "calorias": 2000, 
            "proteinas": 50, 
            "carboidratos": 250, 
            "gorduras": 65
        }
        
        # Prioridade: metas > meta_calorica (se tiver estrutura correta) > default
        metas = user.get("metas")
        if not metas or "calorias" not in metas:
            meta_cal = user.get("meta_calorica", {})
            if "calorias" in meta_cal:
                metas = meta_cal
            else:
                # meta_calorica tem estrutura antiga, usar meta_sugerida
                metas = metas_default.copy()
                if "meta_sugerida" in meta_cal:
                    metas["calorias"] = int(meta_cal["meta_sugerida"])
        
        # Alertas inteligentes
        alertas = []
        if dias_com_log > 0:
            media_calorias = total_calorias / dias_com_log
            media_proteinas = total_proteinas / dias_com_log
            
            # Alerta de calorias
            if media_calorias < metas.get("calorias", 2000) * 0.7:
                alertas.append({"tipo": "warning", "msg": f"Consumo calorico baixo: media de {media_calorias:.0f} kcal/dia"})
            elif media_calorias > metas.get("calorias", 2000) * 1.2:
                alertas.append({"tipo": "danger", "msg": f"Consumo calorico alto: media de {media_calorias:.0f} kcal/dia"})
            else:
                alertas.append({"tipo": "success", "msg": "Consumo calorico dentro da meta!"})
            
            # Alerta de proteinas
            if media_proteinas < metas.get("proteinas", 50) * 0.8:
                alertas.append({"tipo": "warning", "msg": f"Proteinas abaixo da meta: {media_proteinas:.0f}g/dia"})
            
            # Alerta de streak
            if streak >= 7:
                alertas.append({"tipo": "success", "msg": f"Parabens! {streak} dias seguidos registrando!"})
        
        # Historico formatado (ultimas 30 entradas para periodo longo)
        limite_historico = 30 if periodo in ["mes", "ano"] else 10
        historico = []
        for log in logs[:limite_historico]:
            historico.append({
                "data": log.get("data", ""),
                "pratos": log.get("pratos", []),
                "calorias_total": log.get("calorias_total", 0),
                "proteinas_total": log.get("proteinas_total", 0),
                "carboidratos_total": log.get("carboidratos_total", 0),
                "gorduras_total": log.get("gorduras_total", 0)
            })
        
        return {
            "ok": True,
            "hoje": hoje,
            "grafico": dias_grafico,
            "semana": dias_grafico,  # Compatibilidade
            "historico": historico,
            "stats": {
                "dias_registrados": dias_com_log,
                "media_calorias": total_calorias / dias_com_log if dias_com_log > 0 else 0,
                "media_proteinas": total_proteinas / dias_com_log if dias_com_log > 0 else 0,
                "media_carboidratos": total_carboidratos / dias_com_log if dias_com_log > 0 else 0,
                "media_gorduras": total_gorduras / dias_com_log if dias_com_log > 0 else 0,
                "total_calorias": total_calorias,
                "total_pratos": total_pratos,
                "streak": streak
            },
            "metas": metas,
            "alertas": alertas,
            "periodo": periodo
        }
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/premium/metas")
async def update_user_metas(pin: str, request: Request):
    """
    Atualiza as metas nutricionais do usuario Premium.
    Body: {metas: {calorias, proteinas, carboidratos, gorduras}}
    """
    try:
        from services.profile_service import hash_pin
        
        body = await request.json()
        metas = body.get("metas", body)
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        # Validar metas
        metas_validadas = {
            "calorias": max(1000, min(5000, int(metas.get("calorias", 2000)))),
            "proteinas": max(20, min(300, int(metas.get("proteinas", 50)))),
            "carboidratos": max(50, min(500, int(metas.get("carboidratos", 250)))),
            "gorduras": max(20, min(200, int(metas.get("gorduras", 65))))
        }
        
        # Atualizar no banco
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"metas": metas_validadas}}
        )
        
        logger.info(f"[METAS] Atualizadas para {user['nome']}: {metas_validadas}")
        
        return {
            "ok": True,
            "metas": metas_validadas,
            "msg": "Metas atualizadas com sucesso!"
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar metas: {e}")
        return {"ok": False, "error": str(e)}



@api_router.get("/premium/report")
async def get_premium_report(pin: str, periodo: str = "semana"):
    """
    Relatorio Premium com Score de Dieta (0-100).
    Calcula qualidade da alimentacao baseado em:
    - Aderencia as metas de macros (40 pts)
    - Consistencia/streak (20 pts)
    - Variedade de pratos (20 pts)
    - Equilibrio macro (20 pts)
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime, timedelta

        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        if not user:
            return {"ok": False, "error": "PIN incorreto"}

        periodos_dias = {"dia": 1, "semana": 7, "mes": 30, "ano": 365}
        dias = periodos_dias.get(periodo, 7)
        data_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

        logs = await db.daily_logs.find(
            {"user_nome": user["nome"], "data": {"$gte": data_inicio}},
            {"_id": 0}
        ).sort("data", -1).to_list(length=400)

        # Metas
        metas = user.get("metas")
        if not metas or "calorias" not in metas:
            meta_cal = user.get("meta_calorica", {})
            metas = {"calorias": 2000, "proteinas": 50, "carboidratos": 250, "gorduras": 65}
            if "meta_sugerida" in meta_cal:
                metas["calorias"] = int(meta_cal["meta_sugerida"])

        dias_com_log = [l for l in logs if l.get("calorias_total", 0) > 0]
        n_dias = len(dias_com_log)

        if n_dias == 0:
            return {
                "ok": True,
                "score": 0,
                "classificacao": {"texto": "Sem dados", "emoji": "--", "cor": "#718096"},
                "componentes": {"aderencia": 0, "consistencia": 0, "variedade": 0, "equilibrio": 0},
                "resumo": {"dias_registrados": 0, "total_pratos": 0},
                "periodo": periodo,
                "detalhes": []
            }

        # === COMPONENTE 1: Aderencia as metas (0-40 pts) ===
        media_cal = sum(l.get("calorias_total", 0) for l in dias_com_log) / n_dias
        media_prot = sum(l.get("proteinas_total", 0) for l in dias_com_log) / n_dias
        media_carb = sum(l.get("carboidratos_total", 0) for l in dias_com_log) / n_dias
        media_gord = sum(l.get("gorduras_total", 0) for l in dias_com_log) / n_dias

        def aderencia_macro(atual, meta):
            if meta == 0:
                return 1.0
            ratio = atual / meta
            if 0.85 <= ratio <= 1.15:
                return 1.0
            elif 0.7 <= ratio <= 1.3:
                return 0.7
            elif 0.5 <= ratio <= 1.5:
                return 0.4
            return 0.1

        ad_cal = aderencia_macro(media_cal, metas["calorias"])
        ad_prot = aderencia_macro(media_prot, metas["proteinas"])
        ad_carb = aderencia_macro(media_carb, metas["carboidratos"])
        ad_gord = aderencia_macro(media_gord, metas["gorduras"])
        pts_aderencia = ((ad_cal * 0.4 + ad_prot * 0.3 + ad_carb * 0.15 + ad_gord * 0.15) * 40)

        # === COMPONENTE 2: Consistencia (0-20 pts) ===
        streak = 0
        for i in range(min(dias, 365)):
            data = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if any(l.get("data") == data and l.get("calorias_total", 0) > 0 for l in logs):
                streak += 1
            else:
                break
        taxa_registro = n_dias / max(dias, 1)
        pts_consistencia = min(taxa_registro * 15 + min(streak / 7, 1) * 5, 20)

        # === COMPONENTE 3: Variedade (0-20 pts) ===
        todos_pratos = set()
        for l in dias_com_log:
            for p in l.get("pratos", []):
                todos_pratos.add(p.get("nome", "").lower())
        n_pratos_unicos = len(todos_pratos)
        pts_variedade = min(n_pratos_unicos / max(dias * 0.5, 1) * 20, 20)

        # === COMPONENTE 4: Equilibrio macro (0-20 pts) ===
        total_macro = media_prot * 4 + media_carb * 4 + media_gord * 9
        if total_macro > 0:
            pct_prot = (media_prot * 4) / total_macro
            pct_carb = (media_carb * 4) / total_macro
            pct_gord = (media_gord * 9) / total_macro
            # Ideal: 15-25% prot, 45-65% carb, 20-35% gord
            eq_prot = 1.0 if 0.15 <= pct_prot <= 0.25 else 0.5
            eq_carb = 1.0 if 0.45 <= pct_carb <= 0.65 else 0.5
            eq_gord = 1.0 if 0.20 <= pct_gord <= 0.35 else 0.5
            pts_equilibrio = ((eq_prot + eq_carb + eq_gord) / 3) * 20
        else:
            pts_equilibrio = 0
            pct_prot = pct_carb = pct_gord = 0

        score = round(pts_aderencia + pts_consistencia + pts_variedade + pts_equilibrio)
        score = max(0, min(100, score))

        # Classificacao
        if score >= 85:
            classif = {"texto": "Excelente", "emoji": "A+", "cor": "#10b981"}
        elif score >= 70:
            classif = {"texto": "Muito Bom", "emoji": "A", "cor": "#22c55e"}
        elif score >= 55:
            classif = {"texto": "Bom", "emoji": "B", "cor": "#f59e0b"}
        elif score >= 40:
            classif = {"texto": "Regular", "emoji": "C", "cor": "#f97316"}
        else:
            classif = {"texto": "Precisa Melhorar", "emoji": "D", "cor": "#ef4444"}

        # Detalhes dia a dia
        detalhes = []
        for l in dias_com_log[:15]:
            detalhes.append({
                "data": l.get("data", ""),
                "calorias": round(l.get("calorias_total", 0)),
                "proteinas": round(l.get("proteinas_total", 0)),
                "carboidratos": round(l.get("carboidratos_total", 0)),
                "gorduras": round(l.get("gorduras_total", 0)),
                "pratos": len(l.get("pratos", []))
            })

        return {
            "ok": True,
            "score": score,
            "classificacao": classif,
            "componentes": {
                "aderencia": round(pts_aderencia, 1),
                "consistencia": round(pts_consistencia, 1),
                "variedade": round(pts_variedade, 1),
                "equilibrio": round(pts_equilibrio, 1)
            },
            "resumo": {
                "dias_registrados": n_dias,
                "streak": streak,
                "total_pratos": sum(len(l.get("pratos", [])) for l in dias_com_log),
                "pratos_unicos": n_pratos_unicos,
                "media_calorias": round(media_cal),
                "media_proteinas": round(media_prot),
                "media_carboidratos": round(media_carb),
                "media_gorduras": round(media_gord),
                "distribuicao": {
                    "proteinas_pct": round(pct_prot * 100, 1),
                    "carboidratos_pct": round(pct_carb * 100, 1),
                    "gorduras_pct": round(pct_gord * 100, 1)
                }
            },
            "metas": metas,
            "detalhes": detalhes,
            "periodo": periodo,
            "nome": user.get("nome", ""),
            "data_relatorio": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erro no relatorio: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/achievements")
async def get_achievements(pin: str):
    """Retorna badges, streak, nivel e mensagens motivacionais do usuario."""
    try:
        from services.profile_service import hash_pin
        from services.motivational_service import calculate_achievements
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        # Buscar dados dos ultimos 30 dias
        data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        logs = await db.daily_logs.find(
            {"user_nome": user["nome"], "data": {"$gte": data_inicio}},
            {"_id": 0}
        ).sort("data", -1).to_list(length=100)
        
        # Calcular streak
        streak = 0
        for i in range(365):
            data = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if any(l.get("data") == data and l.get("calorias_total", 0) > 0 for l in logs):
                streak += 1
            else:
                break
        
        # Calcular dados para achievements
        total_refeicoes = sum(len(l.get("pratos", [])) for l in logs)
        
        pratos_set = set()
        veggie_count = 0
        balanced_days = 0
        
        for l in logs:
            for p in l.get("pratos", []):
                nome = p.get("nome", "").lower()
                pratos_set.add(nome)
                cat = p.get("categoria", "").lower()
                if "vegan" in cat or "vegetarian" in cat:
                    veggie_count += 1
            
            # Verificar equilibrio macro do dia
            cal = l.get("calorias_total", 0)
            if cal > 0:
                prot = l.get("proteinas_total", 0) * 4
                carb = l.get("carboidratos_total", 0) * 4
                gord = l.get("gorduras_total", 0) * 9
                total = prot + carb + gord
                if total > 0:
                    pct_p = prot / total
                    pct_c = carb / total
                    pct_g = gord / total
                    if 0.15 <= pct_p <= 0.30 and 0.40 <= pct_c <= 0.65 and 0.20 <= pct_g <= 0.40:
                        balanced_days += 1
        
        # Score atual (simplificado)
        metas = user.get("metas", {"calorias": 2000})
        dias_com_log = [l for l in logs if l.get("calorias_total", 0) > 0]
        score = 0
        if dias_com_log:
            media_cal = sum(l.get("calorias_total", 0) for l in dias_com_log) / len(dias_com_log)
            meta_cal = metas.get("calorias", 2000)
            ratio = media_cal / meta_cal if meta_cal > 0 else 0
            score = max(0, min(100, int(100 - abs(1 - ratio) * 100)))
        
        user_data = {
            "streak": streak,
            "total_refeicoes": total_refeicoes,
            "pratos_unicos": len(pratos_set),
            "score": score,
            "veggie_count": veggie_count,
            "balanced_days": balanced_days,
            "prev_score": 0
        }
        
        result = calculate_achievements(user_data)
        result["ok"] = True
        result["nome"] = user.get("nome", "")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao buscar achievements: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/premium/weekly-report-ai")
async def get_weekly_report_ai(pin: str):
    """Gera relatorio semanal educativo com IA incluindo excessos, faltas e recomendacoes."""
    try:
        from services.profile_service import hash_pin
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        pin_hash = hash_pin(pin)
        user = await db.users.find_one({"pin_hash": pin_hash})
        if not user:
            return {"ok": False, "error": "PIN incorreto"}
        
        # Buscar logs da semana
        data_inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        logs = await db.daily_logs.find(
            {"user_nome": user["nome"], "data": {"$gte": data_inicio}},
            {"_id": 0}
        ).sort("data", -1).to_list(length=50)
        
        dias_com_log = [l for l in logs if l.get("calorias_total", 0) > 0]
        
        if not dias_com_log:
            return {
                "ok": True,
                "has_data": False,
                "message": "Sem dados suficientes esta semana. Registre suas refeicoes!"
            }
        
        # Compilar resumo
        total_cal = sum(l.get("calorias_total", 0) for l in dias_com_log)
        total_prot = sum(l.get("proteinas_total", 0) for l in dias_com_log)
        total_carb = sum(l.get("carboidratos_total", 0) for l in dias_com_log)
        total_gord = sum(l.get("gorduras_total", 0) for l in dias_com_log)
        n_dias = len(dias_com_log)
        
        pratos_list = []
        for l in dias_com_log:
            for p in l.get("pratos", []):
                pratos_list.append(p.get("nome", "Desconhecido"))
        
        perfil = user.get("perfil", {})
        metas = user.get("metas", {"calorias": 2000, "proteinas": 50, "carboidratos": 250, "gorduras": 65})
        
        resumo = f"""
Perfil: {perfil.get('sexo','M')}, {perfil.get('idade',30)} anos, {perfil.get('peso',70)}kg, objetivo: {perfil.get('objetivo','manter')}
Dias registrados: {n_dias}/7
Medias diarias: {total_cal/n_dias:.0f} kcal, {total_prot/n_dias:.0f}g prot, {total_carb/n_dias:.0f}g carb, {total_gord/n_dias:.0f}g gord
Metas: {metas.get('calorias',2000)} kcal, {metas.get('proteinas',50)}g prot, {metas.get('carboidratos',250)}g carb, {metas.get('gorduras',65)}g gord
Pratos consumidos: {', '.join(set(pratos_list))}
"""
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        prompt = f"""Voce e um nutricionista educativo do app SoulNutri. Gere um relatorio semanal PERSONALIZADO e MOTIVADOR.

DADOS DO USUARIO:
{resumo}

REGRAS:
1. Seja POSITIVO primeiro, depois aponte melhorias
2. Use linguagem SIMPLES e ACESSIVEL
3. Nao use termos tecnicos sem explicar
4. Inclua 1-2 curiosidades nutricionais relevantes
5. Termine com uma mensagem motivacional

Retorne um JSON:
{{
  "titulo": "Resumo semanal personalizado (ex: Semana equilibrada!)",
  "nota_geral": "A/B/C/D",
  "pontos_positivos": ["Lista de 2-3 pontos positivos"],
  "alertas": ["Lista de 1-2 alertas sobre excessos ou faltas"],
  "dicas": ["Lista de 2-3 dicas praticas para melhorar"],
  "curiosidade": "Uma curiosidade nutricional relacionada ao consumo do usuario",
  "mensagem_motivacional": "Frase motivacional personalizada",
  "analise_macros": {{
    "calorias": {{"status": "ok/excesso/deficit", "detalhe": "Explicacao breve"}},
    "proteinas": {{"status": "ok/excesso/deficit", "detalhe": "Explicacao breve"}},
    "carboidratos": {{"status": "ok/excesso/deficit", "detalhe": "Explicacao breve"}},
    "gorduras": {{"status": "ok/excesso/deficit", "detalhe": "Explicacao breve"}}
  }}
}}"""

        chat = LlmChat(
            api_key=api_key,
            session_id=f"weekly-report-{int(datetime.now().timestamp())}",
            system_message="Voce e um nutricionista educativo. Retorne APENAS JSON valido."
        ).with_model("gemini", "gemini-2.0-flash")
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        if clean.endswith("```"):
            clean = clean[:-3]
        
        import json
        ai_report = json.loads(clean.strip())
        
        return {
            "ok": True,
            "has_data": True,
            "nome": user.get("nome", ""),
            "periodo": f"{data_inicio} a {datetime.now().strftime('%Y-%m-%d')}",
            "dias_registrados": n_dias,
            "medias": {
                "calorias": round(total_cal / n_dias),
                "proteinas": round(total_prot / n_dias),
                "carboidratos": round(total_carb / n_dias),
                "gorduras": round(total_gord / n_dias)
            },
            "metas": metas,
            "pratos_unicos": len(set(pratos_list)),
            "total_pratos": len(pratos_list),
            "ai_report": ai_report
        }
        
    except Exception as e:
        logger.error(f"Erro no relatorio semanal AI: {e}")
        return {"ok": False, "error": str(e)}
async def get_radar_alimentos(nome_prato: str, ingredientes: str = None):
    """
    Retorna alertas do Radar sobre um alimento/prato.
    Informacoes em tempo real sobre nutricao.
    
    ZERO CRÉDITOS - 100% LOCAL
    """
    try:
        from data.radar_noticias import gerar_alerta_radar, buscar_fatos_prato
        
        # Parse de ingredientes se fornecidos
        lista_ingredientes = []
        if ingredientes:
            lista_ingredientes = [i.strip() for i in ingredientes.split(",")]
        
        # Buscar alertas do radar
        alerta = gerar_alerta_radar(nome_prato, lista_ingredientes)
        
        # Buscar fatos detalhados
        fatos = buscar_fatos_prato(nome_prato, lista_ingredientes)
        
        return {
            "ok": True,
            "prato": nome_prato,
            "radar": alerta,
            "fatos_detalhados": fatos
        }
        
    except Exception as e:
        logger.error(f"Erro no radar: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/nutricao/taco/{ingrediente}")
async def get_nutricao_taco(ingrediente: str):
    """
    Retorna dados nutricionais de um ingrediente da Tabela TACO.
    
    ZERO CRÉDITOS - 100% LOCAL
    """
    try:
        from data.taco_database import buscar_dados_taco, calcular_percentual_vdr, VDR
        
        dados = buscar_dados_taco(ingrediente)
        
        if not dados:
            return {
                "ok": False,
                "error": f"Ingrediente '{ingrediente}' nao encontrado na Tabela TACO",
                "sugestao": "Tente um termo mais generico (ex: 'frango' em vez de 'peito de frango grelhado')"
            }
        
        # Calcular percentuais do VDR
        percentuais = {}
        for nutriente in ["calorias", "proteinas", "carboidratos", "gorduras", "fibras", "sodio", "calcio", "ferro", "vitamina_a", "vitamina_c", "vitamina_b12", "potassio", "zinco"]:
            valor = dados.get(nutriente, 0)
            percentuais[nutriente] = round(calcular_percentual_vdr(nutriente, valor), 1)
        
        return {
            "ok": True,
            "ingrediente": ingrediente,
            "dados": dados,
            "percentuais_vdr": percentuais,
            "fonte": "Tabela TACO - UNICAMP/NEPA"
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar TACO: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN - Endpoints de administracao do banco de dados
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/admin/dishes")
async def admin_list_dishes():
    """Lista todos os pratos com informacoes detalhadas para admin."""
    try:
        dishes = []
        
        # Helper to normalize slugs for matching
        def norm(s): return s.lower().replace(' ', '_').replace('-', '_')
        
        # Pre-fetch all image counts from dish_storage in one query
        image_counts = {}  # normalized_slug -> count
        storage_slug_map = {}  # normalized_slug -> original slug
        async for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1, "count": 1}):
            slug = doc.get("slug", "")
            n = norm(slug)
            image_counts[n] = doc.get("count", 0)
            storage_slug_map[n] = slug
        
        # Buscar pratos do MongoDB dishes collection
        seen_normalized = set()
        async for dish_doc in db.dishes.find({}, {"_id": 0}):
            slug = dish_doc.get("slug", dish_doc.get("index_name", ""))
            if not slug:
                continue
            
            n = norm(slug)
            if n in seen_normalized:
                continue
            seen_normalized.add(n)
            
            # Use storage slug for image endpoint compatibility
            display_slug = storage_slug_map.get(n, slug)
            
            dish_data = {
                "slug": display_slug,
                "nome": dish_doc.get("nome", dish_doc.get("name", slug.replace("_", " ").title())),
                "categoria": dish_doc.get("categoria", dish_doc.get("category", "")),
                "category_emoji": dish_doc.get("category_emoji", ""),
                "ingredientes": dish_doc.get("ingredientes", []),
                "descricao": dish_doc.get("descricao", ""),
                "image_count": image_counts.get(n, 0)
            }
            dishes.append(dish_data)
        
        # Adicionar pratos do dish_storage que não estejam em dishes
        for n, orig_slug in storage_slug_map.items():
            if n not in seen_normalized:
                seen_normalized.add(n)
                dish_data = {
                    "slug": orig_slug,
                    "nome": orig_slug.replace("_", " ").title(),
                    "categoria": "",
                    "category_emoji": "🍽️",
                    "ingredientes": [],
                    "descricao": "",
                    "image_count": image_counts.get(n, 0)
                }
                dishes.append(dish_data)
        
        dishes.sort(key=lambda d: d["nome"])
        return {"ok": True, "dishes": dishes, "total": len(dishes)}
        
    except Exception as e:
        logger.error(f"Erro ao listar pratos admin: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/dishes-full")
async def admin_list_dishes_full():
    """Lista todos os pratos com informacoes para admin.
    Fonte de verdade: dish_storage (imagens) + dishes (metadados).
    Apos migracao para Object Storage, nao depende mais do disco local.
    """
    try:
        dishes = []

        # 1. Carregar metadados de imagens do dish_storage (somente contagem e first_image)
        storage_by_slug = {}
        async for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1, "name": 1, "count": 1, "images": {"$slice": 5}}):
            slug = doc.get("slug", "")
            imgs = doc.get("images", [])
            # Choose first representative image (prefer larger files over tiny thumbnails)
            first_img = None
            for img in imgs:
                if img.get("size", 0) > 5000:
                    first_img = img.get("filename", "")
                    break
            if not first_img and imgs:
                first_img = imgs[0].get("filename", "")
            
            storage_by_slug[slug] = {
                "name": doc.get("name", ""),
                "count": doc.get("count", len(imgs)),
                "first_image": first_img,
            }

        # 2. Carregar metadados dos pratos do dishes collection
        dishes_by_slug = {}
        async for doc in db.dishes.find({}, {"_id": 0}):
            slug = doc.get("slug", "")
            if slug:
                dishes_by_slug[slug] = doc

        # 3. Unir os dados - dish_storage como base (tem os slugs limpos)
        seen = set()
        for slug, img_data in storage_by_slug.items():
            seen.add(slug)
            meta = dishes_by_slug.get(slug, {})

            # Ler campos com nomes em ingles (schema real) + fallback portugues (compatibilidade)
            nome = meta.get("name", meta.get("nome", img_data["name"] or slug.replace("-", " ").title()))
            categoria = meta.get("category", meta.get("categoria", []))
            if isinstance(categoria, list):
                categoria = ", ".join(categoria) if categoria else ""
            ingredientes = meta.get("ingredients", meta.get("ingredientes", []))
            nutricao = meta.get("nutrition", meta.get("nutricao", {})) or {}

            dish_data = {
                "slug": slug,
                "nome": nome,
                "categoria": categoria,
                "category_emoji": meta.get("category_emoji", ""),
                "ingredientes": ingredientes,
                "descricao": meta.get("descricao", meta.get("description", "")),
                "beneficios": meta.get("beneficios", []),
                "riscos": meta.get("riscos", []),
                "nutricao": nutricao,
                "contem_gluten": meta.get("has_gluten", meta.get("contem_gluten", None)),
                "contem_lactose": meta.get("contem_lactose", None),
                "contem_ovo": meta.get("contem_ovo", None),
                "contem_castanhas": meta.get("contem_castanhas", None),
                "contem_frutos_mar": meta.get("contem_frutos_mar", None),
                "contem_soja": meta.get("contem_soja", None),
                "contem_peixe": meta.get("contem_peixe", None),
                "is_vegan": meta.get("is_vegan", None),
                "tecnica": meta.get("tecnica", ""),
                "image_count": img_data["count"],
                "first_image": img_data["first_image"],
            }
            dishes.append(dish_data)

        # 4. Adicionar pratos do dishes que nao tem imagens no storage
        for slug, meta in dishes_by_slug.items():
            if slug not in seen:
                seen.add(slug)
                nome = meta.get("name", meta.get("nome", slug.replace("-", " ").title()))
                categoria = meta.get("category", meta.get("categoria", []))
                if isinstance(categoria, list):
                    categoria = ", ".join(categoria) if categoria else ""
                dishes.append({
                    "slug": slug,
                    "nome": nome,
                    "categoria": categoria,
                    "category_emoji": meta.get("category_emoji", ""),
                    "ingredientes": meta.get("ingredients", meta.get("ingredientes", [])),
                    "descricao": meta.get("descricao", ""),
                    "nutricao": meta.get("nutrition", meta.get("nutricao", {})) or {},
                    "contem_gluten": meta.get("has_gluten", None),
                    "is_vegan": meta.get("is_vegan", None),
                    "image_count": 0,
                    "first_image": None,
                })

        dishes.sort(key=lambda d: d.get("nome", ""))
        return {"ok": True, "dishes": dishes, "total": len(dishes)}
        
    except Exception as e:
        logger.error(f"Erro ao listar pratos admin full: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/dish-images-list/{slug}")
async def admin_dish_images_list(slug: str):
    """Retorna a lista de nomes de imagens de um prato. Usado ao abrir Editar."""
    try:
        doc = await db.dish_storage.find_one({"slug": slug}, {"_id": 0, "images": 1, "count": 1})
        if doc:
            names = [img.get("filename", "") for img in doc.get("images", [])]
            return {"ok": True, "images": names, "count": len(names)}
        return {"ok": True, "images": [], "count": 0}
    except Exception as e:
        return {"ok": False, "error": str(e)}



@api_router.get("/admin/dish-image/{slug}")
async def admin_get_dish_image(slug: str, img: str = None, thumb: int = 0):
    """Retorna uma imagem de um prato. thumb=1 para thumbnail comprimido (rápido)."""
    from fastapi.responses import Response, FileResponse
    from services.image_service import _find_local_folder
    import asyncio
    
    try:
        # Fast path: serve directly from local disk (no MongoDB needed)
        local_folder = await asyncio.to_thread(_find_local_folder, slug)
        target_file = None
        
        if local_folder:
            if img:
                target = local_folder / img
                if target.exists():
                    target_file = target
            else:
                # Find first image > 5KB (skip tiny thumbnails)
                for ext in ("*.jpg", "*.jpeg", "*.png"):
                    for f in sorted(local_folder.glob(ext)):
                        if f.stat().st_size > 5000:
                            target_file = f
                            break
                    if target_file:
                        break
                # Fallback to any image
                if not target_file:
                    for ext in ("*.jpg", "*.jpeg", "*.png"):
                        found = sorted(local_folder.glob(ext))
                        if found:
                            target_file = found[0]
                            break
        
        if target_file:
            # Thumbnail mode: compress and resize for fast loading
            if thumb:
                from PIL import Image
                import io
                def make_thumb():
                    with Image.open(target_file) as pil_img:
                        if pil_img.mode in ('RGBA', 'P', 'LA'):
                            pil_img = pil_img.convert('RGB')
                        pil_img.thumbnail((300, 300))
                        buf = io.BytesIO()
                        pil_img.save(buf, format='JPEG', quality=60)
                        return buf.getvalue()
                data = await asyncio.to_thread(make_thumb)
                return Response(content=data, media_type="image/jpeg",
                               headers={"Cache-Control": "public, max-age=3600"})
            else:
                return FileResponse(str(target_file), media_type="image/jpeg",
                                   headers={"Cache-Control": "public, max-age=3600"})
        
        # Slow path: try cloud storage (only if not found locally)
        from services.image_service import get_dish_image_bytes
        data, content_type = await asyncio.to_thread(get_dish_image_bytes, slug, img)
        
        if data is None:
            raise HTTPException(status_code=404, detail="Imagem nao encontrada")
        
        if thumb and data:
            from PIL import Image
            import io
            def make_thumb_from_bytes():
                with Image.open(io.BytesIO(data)) as pil_img:
                    if pil_img.mode in ('RGBA', 'P', 'LA'):
                        pil_img = pil_img.convert('RGB')
                    pil_img.thumbnail((300, 300))
                    buf = io.BytesIO()
                    pil_img.save(buf, format='JPEG', quality=60)
                    return buf.getvalue()
            data = await asyncio.to_thread(make_thumb_from_bytes)
        
        return Response(content=data, media_type=content_type or "image/jpeg",
                       headers={"Cache-Control": "public, max-age=3600"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar imagem: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/admin/dishes/{slug}")
async def admin_update_dish(slug: str, dish_data: dict):
    """Atualiza TODAS as informacoes de um prato no MongoDB."""
    try:
        # Buscar dados existentes do MongoDB
        existing_info = await db.dishes.find_one({"slug": slug}, {"_id": 0}) or {}
        
        # Atualizar TODOS os campos
        cat_value = dish_data.get("categoria", existing_info.get("category", existing_info.get("categoria", "")))
        name_value = dish_data.get("nome", existing_info.get("name", existing_info.get("nome", slug)))
        
        existing_info.update({
            "name": name_value,
            "nome": name_value,
            "slug": slug,
            "category": cat_value,
            "categoria": cat_value,
            "description": dish_data.get("descricao", existing_info.get("description", existing_info.get("descricao", ""))),
            "ingredients": dish_data.get("ingredientes", existing_info.get("ingredients", existing_info.get("ingredientes", []))),
            "beneficios": dish_data.get("beneficios", existing_info.get("beneficios", [])),
            "riscos": dish_data.get("riscos", existing_info.get("riscos", [])),
            "nutrition": dish_data.get("nutricao", existing_info.get("nutrition", existing_info.get("nutricao", {}))),
            "has_gluten": dish_data.get("contem_gluten", existing_info.get("has_gluten", existing_info.get("contem_gluten", False))),
            "contem_lactose": dish_data.get("contem_lactose", existing_info.get("contem_lactose", False)),
            "contem_ovo": dish_data.get("contem_ovo", existing_info.get("contem_ovo", False)),
            "contem_castanhas": dish_data.get("contem_castanhas", existing_info.get("contem_castanhas", False)),
            "contem_frutos_mar": dish_data.get("contem_frutos_mar", existing_info.get("contem_frutos_mar", False)),
            "contem_soja": dish_data.get("contem_soja", existing_info.get("contem_soja", False)),
            "tecnica": dish_data.get("tecnica", existing_info.get("tecnica", ""))
        })
        
        # Definir emoji baseado na categoria
        cat = (existing_info.get("category", "") or "").lower()
        nome_lower = (existing_info.get("name", "") or "").lower()
        
        if "proteina" in cat:
            if any(p in nome_lower for p in ["peixe", "camarao", "bacalhau", "salmao", "atum", "tilapia", "pescador"]):
                existing_info["category_emoji"] = "🐟"
            elif any(p in nome_lower for p in ["frango", "galinha", "sobrecoxa", "peito"]):
                existing_info["category_emoji"] = "🍗"
            else:
                existing_info["category_emoji"] = "🥩"
        elif "vegetariano" in cat:
            existing_info["category_emoji"] = "🥚"
        elif "vegano" in cat:
            existing_info["category_emoji"] = "🥬"
        elif "sobremesa" in cat:
            existing_info["category_emoji"] = "🍰"
        else:
            existing_info["category_emoji"] = "🍽️"
        
        # Salvar no MongoDB
        await db.dishes.update_one(
            {"slug": slug},
            {"$set": existing_info},
            upsert=True
        )
        
        logger.info(f"[ADMIN] Prato atualizado: {slug}")
        return {"ok": True, "message": "Prato atualizado"}
        
    except Exception as e:
        logger.error(f"Erro ao atualizar prato: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/dishes/{slug}/regenerate")
async def admin_regenerate_dish_info(slug: str, data: dict = None):
    """
    Regenera TODAS as informacoes de um prato baseado no nome.
    """
    try:
        from services.generic_ai import regenerate_dish_info_from_name
        
        # Carregar info atual do MongoDB
        current_info = await db.dishes.find_one({"slug": slug}, {"_id": 0}) or {}
        
        # Determinar o nome a usar
        new_name = None
        if data and data.get("new_name"):
            new_name = data["new_name"]
        else:
            new_name = current_info.get("nome", slug)
        
        logger.info(f"[ADMIN] Regenerando ficha do prato '{slug}' com nome: {new_name}")
        
        # Chamar IA para regenerar
        result = await regenerate_dish_info_from_name(new_name, current_info)
        
        if result.get("ok"):
            new_info = {**current_info}
            
            for key in ["nome", "categoria", "descricao", "ingredientes", 
                       "beneficios", "riscos", "nutricao", "contem_gluten",
                       "contem_lactose", "contem_ovo", "contem_castanhas",
                       "contem_frutos_mar", "contem_soja", "tecnica"]:
                if key in result:
                    new_info[key] = result[key]
            
            new_info["slug"] = slug
            new_info["regenerated_at"] = datetime.utcnow().isoformat()
            
            # Definir emoji baseado na categoria
            cat = new_info.get("categoria", "").lower()
            nome_lower = new_info.get("nome", "").lower()
            
            if "proteina" in cat:
                if any(p in nome_lower for p in ["peixe", "camarao", "bacalhau", "salmao", "atum"]):
                    new_info["category_emoji"] = "🐟"
                elif any(p in nome_lower for p in ["frango", "galinha", "sobrecoxa"]):
                    new_info["category_emoji"] = "🍗"
                else:
                    new_info["category_emoji"] = "🥩"
            elif "vegetariano" in cat:
                new_info["category_emoji"] = "🥚"
            elif "vegano" in cat:
                new_info["category_emoji"] = "🥬"
            else:
                new_info["category_emoji"] = "🍽️"
            
            # Salvar no MongoDB
            await db.dishes.update_one(
                {"slug": slug},
                {"$set": new_info},
                upsert=True
            )
            
            logger.info(f"[ADMIN] Ficha regenerada com sucesso: {slug}")
            return {
                "ok": True, 
                "message": f"Ficha de '{new_name}' regenerada com sucesso",
                "new_info": new_info
            }
        else:
            return {"ok": False, "error": result.get("error", "Erro desconhecido")}
        
    except Exception as e:
        logger.error(f"Erro ao regenerar ficha: {e}")
        return {"ok": False, "error": str(e)}


@api_router.delete("/admin/dishes/{slug}")
async def admin_delete_dish(slug: str):
    """Exclui um prato e todas suas fotos do S3, MongoDB e disco local."""
    try:
        import shutil
        from services.image_service import _find_local_folder
        
        # Remover do dish_storage no MongoDB
        await db.dish_storage.delete_one({"slug": slug})
        
        # Remover do dishes no MongoDB
        await db.dishes.delete_one({"slug": slug})
        
        # Remover pasta local (resolve slug vs nome real da pasta)
        import asyncio
        local_folder = await asyncio.to_thread(_find_local_folder, slug)
        if local_folder and local_folder.exists():
            shutil.rmtree(local_folder)
        
        logger.info(f"[ADMIN] Prato excluido: {slug}")
        return {"ok": True, "message": f"Prato {slug} excluido"}
        
    except Exception as e:
        logger.error(f"Erro ao excluir prato: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# ATUALIZAÇÃO LOCAL (SEM IA, SEM CRÉDITOS)
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.post("/admin/dishes/{slug}/update-local")
async def admin_update_dish_local(slug: str, data: dict = None):
    """
    Atualiza prato LOCALMENTE baseado em regras.
    NÃO USA IA, NÃO CONSOME CRÉDITOS!
    
    Body opcional:
    {
        "new_name": "Novo Nome do Prato"
    }
    """
    try:
        from services.local_dish_updater import atualizar_prato_local
        
        novo_nome = data.get("new_name") if data else None
        result = atualizar_prato_local(slug, novo_nome)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao atualizar prato localmente: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/update-all-local")
async def admin_update_all_local():
    """
    Atualiza TODOS os pratos baseado no nome.
    NÃO USA IA, NÃO CONSOME CRÉDITOS!
    Processa instantaneamente.
    """
    try:
        from services.local_dish_updater import atualizar_todos_por_nome
        
        result = atualizar_todos_por_nome()
        logger.info(f"[ADMIN] Atualizacao local em massa: {result['atualizados']}/{result['total']}")
        
        return {"ok": True, **result}
        
    except Exception as e:
        logger.error(f"Erro na atualizacao em massa: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# AUDITORIA - Analise de qualidade dos dados dos pratos
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/admin/audit")
async def admin_audit_dishes():
    """Audita todos os pratos e retorna relatorio de problemas de qualidade"""
    try:
        from services.audit_service import audit_all_dishes
        
        result = audit_all_dishes()
        return {"ok": True, **result}
        
    except Exception as e:
        logger.error(f"Erro na auditoria: {e}")
        return {"ok": False, "error": str(e)}



@api_router.get("/admin/audit/low-photos")
async def admin_dishes_low_photos(max_photos: int = 5):
    """Lista pratos com poucas fotos de referencia no R2 (dish_storage agregado)"""
    import unicodedata
    
    def _normalize(name):
        n = name.lower().replace('-', '').replace('_', '').replace(' ', '').replace('(', '').replace(')', '')
        nfkd = unicodedata.normalize('NFKD', n)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))
    
    # 1. Agregar todas as entradas de dish_storage por slug normalizado
    photo_counts = {}  # norm_slug -> total count
    best_names = {}    # norm_slug -> best name
    async for doc in db.dish_storage.find({}, {"_id": 0, "slug": 1, "name": 1, "count": 1}):
        norm = _normalize(doc.get("slug", ""))
        count = doc.get("count", 0)
        photo_counts[norm] = photo_counts.get(norm, 0) + count
        # Preferir nome sem hifens/underscores
        name = doc.get("name", doc.get("slug", ""))
        if norm not in best_names or ('-' not in name and '_' not in name):
            best_names[norm] = name
    
    # 2. Cruzar com colecao dishes para pegar o nome oficial
    async for doc in db.dishes.find({}, {"_id": 0, "slug": 1, "name": 1, "nome": 1}):
        norm = _normalize(doc.get("slug", ""))
        name = doc.get("name") or doc.get("nome", "")
        if name and norm in photo_counts:
            best_names[norm] = name
    
    # 3. Filtrar pratos com poucas fotos
    results = []
    for norm, count in photo_counts.items():
        if count <= max_photos:
            results.append({
                "name": best_names.get(norm, norm),
                "photo_count": count
            })
    results.sort(key=lambda x: x["photo_count"])
    return {"ok": True, "total": len(results), "max_photos": max_photos, "dishes": results}


@api_router.post("/admin/audit/fix/{slug}")
async def admin_fix_dish_with_ai(slug: str):
    """Usa IA para sugerir correcoes para um prato especifico"""
    try:
        from services.audit_service import fix_dish_with_ai
        
        result = await fix_dish_with_ai(slug)
        return result
        
    except Exception as e:
        logger.error(f"Erro ao corrigir prato {slug}: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/audit/apply/{slug}")
async def admin_apply_ai_suggestions(slug: str, suggestions: dict):
    """Aplica as sugestoes da IA ao prato"""
    try:
        from services.audit_service import apply_ai_suggestions
        
        result = apply_ai_suggestions(slug, suggestions)
        return result
        
    except Exception as e:
        logger.error(f"Erro ao aplicar sugestoes para {slug}: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/audit/fix-single/{slug}")
async def admin_fix_single_dish(slug: str):
    """Usa IA para corrigir dados de um unico prato"""
    try:
        from services.generic_ai import fix_dish_data_with_ai
        from services.image_service import get_dish_image_bytes
        import json
        
        # Carregar info atual do MongoDB
        current_info = {}
        dish_doc = await db.dishes.find_one({"slug": slug}, {"_id": 0})
        if dish_doc:
            current_info = dish_doc
        
        # Buscar imagem do S3
        import asyncio
        image_bytes, _ = await asyncio.to_thread(get_dish_image_bytes, slug)
        if not image_bytes:
            return {"ok": False, "error": "Nenhuma imagem encontrada"}
        
        # Chamar IA
        result = await fix_dish_data_with_ai(image_bytes, current_info)
        
        if result.get("ok"):
            # Mesclar e salvar no MongoDB
            new_info = {**current_info, **result}
            new_info.pop("ok", None)
            new_info["slug"] = slug
            
            await db.dishes.update_one(
                {"slug": slug},
                {"$set": new_info},
                upsert=True
            )
            
            return {"ok": True, "message": f"Prato {slug} corrigido", "data": new_info}
        else:
            return result
        
    except Exception as e:
        logger.error(f"Erro ao corrigir prato {slug}: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/audit/batch-fix")
async def admin_batch_fix_dishes(request: dict):
    """Corrige multiplos pratos em lote usando IA"""
    try:
        from services.generic_ai import batch_fix_dishes
        
        slugs = request.get("slugs", [])
        if not slugs:
            return {"ok": False, "error": "Nenhum slug fornecido"}
        
        # Limitar a 10 por vez para nao sobrecarregar
        slugs = slugs[:10]
        
        result = await batch_fix_dishes(slugs, max_concurrent=2)
        return {"ok": True, **result}
        
    except Exception as e:
        logger.error(f"Erro no batch fix: {e}")
        return {"ok": False, "error": str(e)}


@api_router.delete("/admin/dish-image/{slug}")
async def delete_dish_image(slug: str, img: str = Query(...)):
    """Deleta uma imagem de um prato do S3 e disco local"""
    try:
        from services.image_service import delete_dish_image_from_storage, get_dish_image_count, get_dish_images_from_db
        import asyncio
        # Verificar se a imagem existe antes de deletar
        images = await asyncio.to_thread(get_dish_images_from_db, slug)
        img_exists = any(i.get("filename") == img for i in images)
        if not img_exists:
            # Verificar no disco local também
            from services.image_service import _find_local_folder
            local_folder = await asyncio.to_thread(_find_local_folder, slug)
            if not local_folder or not (local_folder / img).exists():
                return JSONResponse(status_code=404, content={"ok": False, "error": f"Imagem '{img}' nao encontrada no prato '{slug}'"})
        result = await asyncio.to_thread(delete_dish_image_from_storage, slug, img)
        if result.get("ok"):
            remaining = await asyncio.to_thread(get_dish_image_count, slug)
            return {"ok": True, "message": f"Imagem {img} removida", "remaining_images": remaining}
        return JSONResponse(status_code=404, content={"ok": False, "error": result.get("error", "Erro ao remover")})
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@api_router.post("/admin/move-image")
async def move_dish_image(request: Request):
    """Move uma imagem de um prato para outro (S3 + MongoDB + local)"""
    try:
        from services.image_service import get_dish_image_bytes, save_dish_image, delete_dish_image_from_storage, get_dish_image_count
        
        data = await request.json()
        source_dish = data.get("source_dish")
        target_dish = data.get("target_dish")
        image_name = data.get("image_name")
        
        if not source_dish or not target_dish or not image_name:
            return JSONResponse(status_code=400, content={"ok": False, "error": "source_dish, target_dish e image_name sao obrigatorios"})
        
        # Verificar se o prato destino existe no dish_storage
        target_exists = await db.dish_storage.find_one({"slug": target_dish}, {"_id": 0, "slug": 1})
        if not target_exists:
            return JSONResponse(status_code=404, content={"ok": False, "error": f"Prato destino '{target_dish}' nao encontrado"})
        
        # Ler imagem do prato origem
        import asyncio
        image_bytes, content_type = await asyncio.to_thread(get_dish_image_bytes, source_dish, image_name)
        if not image_bytes:
            return JSONResponse(status_code=404, content={"ok": False, "error": "Imagem nao encontrada no prato origem"})
        
        # Salvar no prato destino (local + MongoDB)
        await asyncio.to_thread(save_dish_image, target_dish, image_name, image_bytes)
        
        # Remover do prato origem SOMENTE depois de salvar com sucesso
        await asyncio.to_thread(delete_dish_image_from_storage, source_dish, image_name)
        
        remaining = await asyncio.to_thread(get_dish_image_count, source_dish)
        logger.info(f"[MOVE] Imagem '{image_name}' movida de '{source_dish}' para '{target_dish}'")
        return {"ok": True, "message": f"Imagem movida para {target_dish}", "remaining_in_source": remaining}
    except Exception as e:
        logger.error(f"[MOVE] Erro ao mover imagem: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@api_router.get("/admin/duplicates")
async def get_duplicate_groups():
    """Retorna grupos de pratos duplicados para consolidacao"""
    try:
        from services.audit_service import find_duplicate_groups
        
        grupos = find_duplicate_groups()
        return {"ok": True, "groups": grupos, "total_groups": len(grupos)}
        
    except Exception as e:
        logger.error(f"Erro ao buscar duplicados: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/consolidate")
async def consolidate_dishes(request: dict):
    """Consolida um grupo de pratos duplicados"""
    try:
        from services.audit_service import consolidate_duplicate_dishes
        
        group = request.get("group", [])
        if len(group) < 2:
            return {"ok": False, "error": "Grupo precisa ter pelo menos 2 slugs"}
        
        result = await consolidate_duplicate_dishes(group)
        return result
        
    except Exception as e:
        logger.error(f"Erro ao consolidar: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/consolidate-all")
async def consolidate_all_duplicates():
    """Consolida todos os grupos de duplicados automaticamente"""
    try:
        from services.audit_service import find_duplicate_groups, consolidate_duplicate_dishes
        
        grupos = find_duplicate_groups()
        results = {"consolidated": [], "failed": []}
        
        for group in grupos[:20]:  # Limitar a 20 grupos por vez
            try:
                result = await consolidate_duplicate_dishes(group)
                if result.get("ok"):
                    results["consolidated"].append(result["main_slug"])
                else:
                    results["failed"].append({"group": group, "error": result.get("error")})
            except Exception as e:
                results["failed"].append({"group": group, "error": str(e)})
        
        return {
            "ok": True,
            "consolidated_count": len(results["consolidated"]),
            "failed_count": len(results["failed"]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erro na consolidacao em massa: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNACIONALIZAÇÃO - Suporte a multiplos idiomas (GRATUITO com LibreTranslate)
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/i18n/languages")
async def get_languages():
    """Lista todos os idiomas suportados"""
    try:
        from services.translation_service import get_supported_languages
        languages = get_supported_languages()
        return {
            "ok": True,
            "languages": languages,
            "default": "pt"
        }
    except Exception as e:
        logger.error(f"Erro ao listar idiomas: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/i18n/ui/{lang}")
async def get_ui_translations(lang: str = "pt"):
    """Retorna traducoes da interface para o idioma especificado"""
    try:
        from services.translation_service import get_ui_translations, SUPPORTED_LANGUAGES
        
        if lang not in SUPPORTED_LANGUAGES:
            lang = "pt"
        
        translations = get_ui_translations(lang)
        return {
            "ok": True,
            "lang": lang,
            "translations": translations
        }
    except Exception as e:
        logger.error(f"Erro ao buscar traducoes: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/i18n/translate")
async def translate_text_endpoint(
    text: str = Form(...),
    source: str = Form("pt"),
    target: str = Form("en")
):
    """Traduz texto de um idioma para outro"""
    try:
        from services.translation_service import translate_text
        
        translated = await translate_text(text, source, target)
        return {
            "ok": True,
            "original": text,
            "translated": translated,
            "source": source,
            "target": target
        }
    except Exception as e:
        logger.error(f"Erro na traducao: {e}")
        return {"ok": False, "error": str(e)}



# Evento de shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Evento de startup - pre-carregar modelo
@app.on_event("startup")
async def startup_event():
    logger.info("SoulNutri AI Server iniciando...")
    
    # Pre-carregar o modelo CLIP (importante para performance!)
    try:
        from ai.embedder import preload_model
        preload_model()
        logger.info("Modelo CLIP pre-carregado!")
    except Exception as e:
        logger.warning(f"Nao foi possivel pre-carregar modelo: {e}")
    
    # Tentar pre-carregar o indice (se existir)
    try:
        from ai.index import get_index
        index = get_index()
        if index.is_ready():
            logger.info(f"Índice carregado: {index.get_stats()}")
        else:
            logger.info("Índice nao encontrado. Execute /api/ai/reindex para criar.")
    except Exception as e:
        logger.warning(f"Nao foi possivel carregar indice: {e}")
    
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


@api_router.get("/download/upload-script")
async def download_upload_script():
    """Download do script de upload de fotos para rodar no computador do usuario"""
    from fastapi.responses import FileResponse
    file_path = "/app/scripts/upload_fotos.py"
    return FileResponse(
        path=file_path,
        filename="upload_fotos_soulnutri.py",
        media_type="text/x-python"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# NOVIDADES/NOTÍCIAS PREMIUM - Sistema de alertas em tempo real para o buffet
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/novidades/{dish_slug}")
async def get_dish_novidade(dish_slug: str):
    """
    Retorna novidade/noticia de um prato especifico (se houver).
    Usado na versao Premium para mostrar alertas ao escanear um item.
    """
    try:
        # Buscar novidade do MongoDB
        novidade = await db.novidades.find_one(
            {"dish_slug": dish_slug, "ativa": True},
            {"_id": 0}
        )
        
        if novidade:
            return {
                "ok": True,
                "tem_novidade": True,
                "novidade": novidade
            }
        
        return {
            "ok": True,
            "tem_novidade": False,
            "novidade": None
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar novidade: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/novidades")
async def list_novidades():
    """Lista todas as novidades ativas."""
    try:
        novidades = await db.novidades.find(
            {"ativa": True},
            {"_id": 0}
        ).sort("data_criacao", -1).to_list(100)
        
        return {
            "ok": True,
            "total": len(novidades),
            "novidades": novidades
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar novidades: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/novidades")
async def admin_create_novidade(
    dish_slug: str = Form(...),
    tipo: str = Form(...),  # "info", "alerta", "dica", "estudo"
    titulo: str = Form(...),
    mensagem: str = Form(...),
    emoji: str = Form("📢"),
    severidade: str = Form("info"),  # "info", "warning", "danger"
    ativa: bool = Form(True)
):
    """
    Cria/atualiza uma novidade para um prato.
    Tipos:
    - info: Informacao positiva (ex: "Novo estudo confirma beneficios")
    - alerta: Alerta importante (ex: "Lote com problema")
    - dica: Dica de combinacao ou consumo
    - estudo: Estudo cientifico recente
    """
    from datetime import datetime
    
    try:
        novidade = {
            "dish_slug": dish_slug,
            "tipo": tipo,
            "titulo": titulo,
            "mensagem": mensagem,
            "emoji": emoji,
            "severidade": severidade,
            "ativa": ativa,
            "data_criacao": datetime.now().isoformat(),
            "data_atualizacao": datetime.now().isoformat()
        }
        
        # Upsert - atualiza se existir, insere se nao
        await db.novidades.update_one(
            {"dish_slug": dish_slug},
            {"$set": novidade},
            upsert=True
        )
        
        logger.info(f"[ADMIN] Novidade criada/atualizada: {dish_slug} - {tipo}")
        
        return {
            "ok": True,
            "message": f"Novidade salva para {dish_slug}",
            "novidade": novidade
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar novidade: {e}")
        return {"ok": False, "error": str(e)}


@api_router.delete("/admin/novidades/{dish_slug}")
async def admin_delete_novidade(dish_slug: str):
    """Remove uma novidade."""
    try:
        result = await db.novidades.delete_one({"dish_slug": dish_slug})
        
        if result.deleted_count > 0:
            return {"ok": True, "message": f"Novidade de {dish_slug} removida"}
        else:
            return {"ok": False, "error": "Novidade nao encontrada"}
            
    except Exception as e:
        logger.error(f"Erro ao remover novidade: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# NOTIFICACOES PUSH PERSONALIZADAS
# ═══════════════════════════════════════════════════════════════

@api_router.post("/notifications/generate")
async def generate_notification(request: Request):
    """
    Gera uma notificacao push personalizada para o usuario.
    Max 1 por dia. Baseada no consumo real.
    """
    from services.notification_service import generate_personalized_notification
    try:
        data = await request.json()
        user_pin = data.get("user_pin", "")
        user_name = data.get("user_name", "")
        if not user_pin:
            return {"ok": False, "error": "user_pin obrigatorio"}
        result = await generate_personalized_notification(db, user_pin, user_name)
        return result
    except Exception as e:
        logger.error(f"[NOTIFICATION] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/notifications/{user_pin}")
async def get_notifications(user_pin: str, limit: int = 20):
    """Retorna as notificacoes do usuario."""
    from services.notification_service import get_user_notifications
    try:
        notifications = await get_user_notifications(db, user_pin, limit)
        unread = sum(1 for n in notifications if not n.get("read"))
        return {"ok": True, "notifications": notifications, "unread": unread}
    except Exception as e:
        logger.error(f"[NOTIFICATION] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/notifications/{user_pin}/read")
async def mark_read(user_pin: str, request: Request):
    """Marca uma notificacao como lida."""
    from services.notification_service import mark_notification_read
    try:
        data = await request.json()
        date = data.get("date", "")
        if not date:
            return {"ok": False, "error": "date obrigatorio"}
        success = await mark_notification_read(db, user_pin, date)
        return {"ok": True, "marked": success}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# ADMIN SETTINGS & PREMIUM USERS (stubs para o painel admin)
# ═══════════════════════════════════════════════════════════════

@api_router.get("/admin/settings")
async def get_admin_settings():
    """Retorna configurações do admin."""
    try:
        settings = await db.admin_settings.find_one({}, {"_id": 0})
        if not settings:
            settings = {"ENABLE_PROCESSING_METRICS": False}
        return {"ok": True, **settings}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/settings")
async def save_admin_settings(request: Request):
    """Salva configurações do admin."""
    try:
        data = await request.json()
        await db.admin_settings.update_one({}, {"$set": data}, upsert=True)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/premium/users")
async def get_premium_users():
    """Lista todos os usuarios registrados com status premium e trial."""
    try:
        users = []
        async for u in db.users.find({}, {"_id": 0, "pin_hash": 0}).sort("created_at", -1).limit(100):
            users.append(u)
        return {"ok": True, "users": users}
    except Exception as e:
        return {"ok": False, "error": str(e), "users": []}


@api_router.post("/admin/premium/liberar")
async def liberar_premium(request: Request):
    """Libera acesso premium para um usuario (sem data de expiracao)."""
    try:
        data = await request.json()
        nome = data.get("nome", "").strip()
        if not nome:
            return {"ok": False, "error": "Nome é obrigatório"}
        result = await db.users.update_one(
            {"nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
            {"$set": {
                "premium_ativo": True,
                "is_trial": False,
                "premium_expirado": False,
                "trial_expirado": False,
                "premium_expira_em": None,
                "premium_liberado_por": "admin",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        if result.modified_count == 0:
            return {"ok": False, "error": f"Usuário '{nome}' não encontrado"}
        return {"ok": True, "message": f"Premium liberado permanentemente para {nome}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/premium/bloquear")
async def bloquear_premium(request: Request):
    """Bloqueia acesso premium de um usuario."""
    try:
        data = await request.json()
        nome = data.get("nome", "").strip()
        if not nome:
            return {"ok": False, "error": "Nome é obrigatório"}
        result = await db.users.update_one(
            {"nome": {"$regex": f"^\\s*{nome}\\s*$", "$options": "i"}},
            {"$set": {
                "premium_ativo": False,
                "premium_bloqueado_por": "admin",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        if result.modified_count == 0:
            return {"ok": False, "error": f"Usuário '{nome}' não encontrado"}
        return {"ok": True, "message": f"Premium bloqueado para {nome}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/api-usage")
async def get_api_usage():
    """Retorna estatísticas de uso de APIs."""
    try:
        # Buscar logs de uso
        usage = await db.api_usage.find_one({"type": "summary"}, {"_id": 0})
        if not usage:
            usage = {
                "total_calls": 0,
                "gemini_calls": 0,
                "clip_calls": 0,
                "s3_calls": 0,
                "costs": {"total": 0.0}
            }
        return {"ok": True, **usage}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/processing-metrics")
async def get_processing_metrics(date: str = ""):
    """Retorna métricas de processamento."""
    try:
        query = {}
        if date:
            query["date"] = date
        metrics = []
        async for m in db.processing_metrics.find(query, {"_id": 0}).sort("created_at", -1).limit(50):
            metrics.append(m)
        return {"ok": True, "metrics": metrics}
    except Exception as e:
        return {"ok": False, "error": str(e), "metrics": []}


# ═══════════════════════════════════════════════════════════════
# ATUALIZAÇÃO NUTRICIONAL SEGURA
# ═══════════════════════════════════════════════════════════════

@api_router.post("/admin/nutrition/preview")
async def preview_nutrition_changes(request: Request):
    """
    DRY RUN: Mostra o que mudaria sem alterar nada.
    Body: { "dish_slugs": ["arroz_branco", "feijao"] } ou vazio para 10 primeiros.
    """
    from services.safe_nutrition_updater import preview_nutrition_update
    try:
        data = await request.json()
        slugs = data.get("dish_slugs", None)
        limit = data.get("limit", 5)
        result = await preview_nutrition_update(db, slugs, limit)
        return result
    except Exception as e:
        logger.error(f"[NUTRITION_PREVIEW] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/nutrition/update-single")
async def update_single_nutrition(request: Request):
    """
    Atualiza dados nutricionais de UM prato.
    Body: { "dish_slug": "arroz_branco", "nutrition": {...}, "source": "TACO+USDA" }
    """
    from services.safe_nutrition_updater import safe_update_nutrition
    try:
        data = await request.json()
        slug = data.get("dish_slug", "")
        nutrition = data.get("nutrition", {})
        source = data.get("source", "manual")
        if not slug or not nutrition:
            return {"ok": False, "error": "dish_slug e nutrition obrigatorios"}
        result = await safe_update_nutrition(db, slug, nutrition, source)
        return result
    except Exception as e:
        logger.error(f"[NUTRITION_UPDATE] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/nutrition/rollback")
async def rollback_nutrition_endpoint(request: Request):
    """
    Reverte a última atualização nutricional de um prato.
    Body: { "dish_slug": "arroz_branco" }
    """
    from services.safe_nutrition_updater import rollback_nutrition
    try:
        data = await request.json()
        slug = data.get("dish_slug", "")
        if not slug:
            return {"ok": False, "error": "dish_slug obrigatorio"}
        result = await rollback_nutrition(db, slug)
        return result
    except Exception as e:
        logger.error(f"[NUTRITION_ROLLBACK] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/nutrition/audit-log")
async def get_nutrition_audit_log(slug: str = "", limit: int = 50):
    """Retorna o log de auditoria de alterações nutricionais."""
    try:
        query = {}
        if slug:
            query["dish_slug"] = slug
        logs = []
        async for log in db.nutrition_audit_log.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit):
            logs.append(log)
        return {"ok": True, "logs": logs, "total": len(logs)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# MODERAÇÃO - Fila de moderação para feedback de usuários
# ═══════════════════════════════════════════════════════════════

@api_router.post("/feedback/moderation-queue")
async def submit_to_moderation_queue(
    file: UploadFile = File(...),
    original_dish: str = Form(""),
    original_dish_display: str = Form(""),
    confidence: str = Form(""),
    score: float = Form(0.0),
    source: str = Form("")
):
    """
    Envia uma foto para a fila de moderação do admin.
    O usuário reporta que o reconhecimento está incorreto,
    mas NÃO pode corrigir diretamente - apenas o admin pode.
    """
    try:
        import uuid
        import base64

        content = await file.read()
        if len(content) == 0:
            return {"ok": False, "error": "Arquivo vazio"}

        # Salvar imagem no S3 na pasta de moderação
        from services.storage_service import put_object
        import asyncio as _asyncio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"moderation_{timestamp}_{unique_id}.jpg"
        storage_path = f"soulnutri/moderation/{filename}"
        await _asyncio.to_thread(put_object, storage_path, content, "image/jpeg")

        # Salvar na coleção moderation_queue do MongoDB
        doc = {
            "original_dish": original_dish,
            "original_dish_display": original_dish_display,
            "confidence": confidence,
            "score": score,
            "source": source,
            "image_path": storage_path,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "resolved_at": None,
            "resolved_by": None,
            "correction": None
        }
        result = await db.moderation_queue.insert_one(doc)

        logger.info(f"[MODERATION] Item adicionado à fila: {original_dish_display} (score: {score:.2f})")

        return {
            "ok": True,
            "message": "Reportado com sucesso! O administrador irá revisar.",
            "queue_id": str(result.inserted_id)
        }

    except Exception as e:
        logger.error(f"[MODERATION] Erro: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/moderation-queue")
async def get_moderation_queue(status: str = "pending"):
    """Lista os itens na fila de moderação."""
    try:
        query = {}
        if status != "all":
            query["status"] = status

        items = []
        async for doc in db.moderation_queue.find(query).sort("created_at", -1).limit(100):
            items.append({
                "id": str(doc["_id"]),
                "original_dish": doc.get("original_dish", ""),
                "original_dish_display": doc.get("original_dish_display", ""),
                "confidence": doc.get("confidence", ""),
                "score": doc.get("score", 0),
                "source": doc.get("source", ""),
                "image_path": doc.get("image_path", ""),
                "status": doc.get("status", "pending"),
                "created_at": doc.get("created_at", ""),
                "resolved_at": doc.get("resolved_at"),
                "correction": doc.get("correction")
            })

        pending_count = await db.moderation_queue.count_documents({"status": "pending"})

        return {
            "ok": True,
            "items": items,
            "total": len(items),
            "pending_count": pending_count
        }

    except Exception as e:
        logger.error(f"[MODERATION] Erro ao listar fila: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/moderation-image/{item_id}")
async def get_moderation_image(item_id: str):
    """Retorna a imagem de um item da fila de moderação."""
    from bson import ObjectId
    from fastapi.responses import Response
    import asyncio

    try:
        doc = await db.moderation_queue.find_one({"_id": ObjectId(item_id)})
        if not doc or not doc.get("image_path"):
            return Response(content=b"", media_type="image/jpeg", status_code=404)

        from services.storage_service import get_object
        image_data, content_type = await asyncio.to_thread(get_object, doc["image_path"])
        return Response(content=image_data, media_type=content_type)

    except Exception as e:
        logger.error(f"[MODERATION] Erro ao buscar imagem: {e}")
        return Response(content=b"", media_type="image/jpeg", status_code=500)


@api_router.post("/admin/moderation/{item_id}/approve")
async def approve_moderation_item(item_id: str):
    """Admin aprova o reconhecimento original como correto e salva a foto no dataset."""
    from bson import ObjectId

    try:
        doc = await db.moderation_queue.find_one({"_id": ObjectId(item_id)})
        if not doc:
            return {"ok": False, "error": "Item não encontrado"}

        if doc["status"] != "pending":
            return {"ok": False, "error": "Item já foi processado"}

        # Se tem prato original, salvar imagem no dataset
        if doc.get("original_dish") and doc.get("image_path"):
            from services.storage_service import get_object
            from services.image_service import save_dish_image
            import uuid
            import asyncio as _asyncio

            image_data, _ = await _asyncio.to_thread(get_object, doc["image_path"])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uid = str(uuid.uuid4())[:8]
            filename = f"{doc['original_dish']}_approved_{timestamp}_{uid}.jpg"
            await _asyncio.to_thread(save_dish_image, doc["original_dish"], filename, image_data)

        # Atualizar status
        await db.moderation_queue.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {
                "status": "approved",
                "resolved_at": datetime.now().isoformat(),
                "resolved_by": "admin"
            }}
        )

        # Registrar na calibracao: CLIP acertou (usuario errou ao clicar Nao)
        score_val = doc.get("score", 0)
        try:
            score_val = float(score_val)
        except (ValueError, TypeError):
            score_val = 0.0
        await db.calibration_log.insert_one({
            "dish_clip": doc.get("original_dish", ""),
            "dish_real": doc.get("original_dish", ""),
            "is_correct": True,
            "score": score_val,
            "confidence": doc.get("confidence", ""),
            "source": doc.get("source", "moderation_approved"),
            "created_at": datetime.utcnow()
        })

        logger.info(f"[MODERATION] Aprovado: {doc.get('original_dish_display')} | Score: {score_val} -> CALIBRATION: correto")
        return {"ok": True, "message": "Item aprovado e foto salva no dataset"}

    except Exception as e:
        logger.error(f"[MODERATION] Erro ao aprovar: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/moderation/{item_id}/reject")
async def reject_moderation_item(item_id: str):
    """Admin rejeita o item — FALSO POSITIVO: CLIP identificou algo errado."""
    from bson import ObjectId

    try:
        doc = await db.moderation_queue.find_one({"_id": ObjectId(item_id)})
        if not doc:
            return {"ok": False, "error": "Item não encontrado"}

        if doc["status"] != "pending":
            return {"ok": False, "error": "Item já foi processado"}

        await db.moderation_queue.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {
                "status": "rejected",
                "resolved_at": datetime.now().isoformat(),
                "resolved_by": "admin"
            }}
        )

        # Registrar na calibracao: FALSO POSITIVO (dado critico para Youden)
        score_val = doc.get("score", 0)
        try:
            score_val = float(score_val)
        except (ValueError, TypeError):
            score_val = 0.0
        await db.calibration_log.insert_one({
            "dish_clip": doc.get("original_dish", ""),
            "dish_real": "FALSO_POSITIVO",
            "is_correct": False,
            "score": score_val,
            "confidence": doc.get("confidence", ""),
            "source": doc.get("source", "moderation_rejected"),
            "created_at": datetime.utcnow()
        })

        logger.info(f"[MODERATION] Rejeitado (FALSO POSITIVO): {doc.get('original_dish_display')} | Score: {score_val} -> CALIBRATION: incorreto")
        return {"ok": True, "message": "Item rejeitado (falso positivo registrado na calibracao)"}

    except Exception as e:
        logger.error(f"[MODERATION] Erro ao rejeitar: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/moderation/{item_id}/correct")
async def correct_moderation_item(item_id: str, request: Request):
    """
    Admin corrige o nome do prato e salva a foto no dataset correto.
    Body: { "correct_dish_name": "Nome Correto Do Prato" }
    """
    from bson import ObjectId

    try:
        data = await request.json()
        correct_name = data.get("correct_dish_name", "").strip()

        if not correct_name:
            return {"ok": False, "error": "Nome correto é obrigatório"}

        doc = await db.moderation_queue.find_one({"_id": ObjectId(item_id)})
        if not doc:
            return {"ok": False, "error": "Item não encontrado"}

        if doc["status"] != "pending":
            return {"ok": False, "error": "Item já foi processado"}

        # Gerar slug do nome correto
        import re as _re
        correct_slug = correct_name.lower().strip()
        correct_slug = correct_slug.replace(" ", "_").replace("-", "_")
        correct_slug = ''.join(c for c in correct_slug if c.isalnum() or c == '_')

        # Salvar imagem no dataset do prato correto
        if doc.get("image_path"):
            from services.storage_service import get_object
            from services.image_service import save_dish_image
            import uuid
            import asyncio as _asyncio

            image_data, _ = await _asyncio.to_thread(get_object, doc["image_path"])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uid = str(uuid.uuid4())[:8]
            filename = f"{correct_slug}_corrected_{timestamp}_{uid}.jpg"
            await _asyncio.to_thread(save_dish_image, correct_slug, filename, image_data)

        # Atualizar status
        await db.moderation_queue.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {
                "status": "corrected",
                "resolved_at": datetime.now().isoformat(),
                "resolved_by": "admin",
                "correction": correct_name,
                "correction_slug": correct_slug
            }}
        )

        # Registrar na calibracao: CLIP errou o prato (admin corrigiu)
        score_val = doc.get("score", 0)
        try:
            score_val = float(score_val)
        except (ValueError, TypeError):
            score_val = 0.0
        await db.calibration_log.insert_one({
            "dish_clip": doc.get("original_dish", ""),
            "dish_real": correct_name,
            "is_correct": False,
            "score": score_val,
            "confidence": doc.get("confidence", ""),
            "source": doc.get("source", "moderation_corrected"),
            "created_at": datetime.utcnow()
        })

        logger.info(f"[MODERATION] Corrigido: {doc.get('original_dish_display')} -> {correct_name} | Score: {score_val} -> CALIBRATION: incorreto")
        return {
            "ok": True,
            "message": f"Corrigido para '{correct_name}' e foto salva no dataset",
            "correction": correct_name,
            "correction_slug": correct_slug
        }

    except Exception as e:
        logger.error(f"[MODERATION] Erro ao corrigir: {e}")
        return {"ok": False, "error": str(e)}


# ═════════════════════════════

app.include_router(api_router)

# Endpoint de diagnostico do deploy (temporario)
@app.get("/api/debug/deploy")
async def debug_deploy():
    import os
    backend_dir = Path(__file__).resolve().parent
    base_dir = backend_dir.parent
    build_path = base_dir / "frontend" / "build"
    abs_build = Path("/app/frontend/build")
    
    build_files = []
    for p in [build_path, abs_build]:
        if p.exists():
            try:
                build_files = [str(f.name) for f in p.iterdir()][:10]
            except:
                pass
            break
    
    return {
        "cwd": os.getcwd(),
        "file": str(Path(__file__).resolve()),
        "backend_dir": str(backend_dir),
        "base_dir": str(base_dir),
        "build_relative": str(build_path),
        "build_relative_exists": build_path.exists(),
        "build_absolute": str(abs_build),
        "build_absolute_exists": abs_build.exists(),
        "index_relative": (build_path / "index.html").exists(),
        "index_absolute": (abs_build / "index.html").exists(),
        "build_files": build_files,
        "sys_path": sys.path[:5],
    }

# ═══════════════════════════════════════════════════════
# DEPLOY UNIFICADO: FastAPI serve o React Build (SPA)
# ═══════════════════════════════════════════════════════
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

class SPAStaticFiles(StarletteStaticFiles):
    """Serve arquivos estaticos com fallback para index.html (React SPA)"""
    async def get_response(self, path, scope):
        try:
            response = await super().get_response(path, scope)
            if response.status_code == 404:
                response = await super().get_response("index.html", scope)
            return response
        except Exception:
            return await super().get_response("index.html", scope)

# Detectar build do frontend
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
FRONTEND_BUILD = BASE_DIR / "frontend" / "build"

# Fallback: tentar caminho absoluto (Docker)
if not FRONTEND_BUILD.exists():
    FRONTEND_BUILD = Path("/app/frontend/build")

logger.info(f"[DEPLOY] BACKEND_DIR={BACKEND_DIR}")
logger.info(f"[DEPLOY] BASE_DIR={BASE_DIR}")
logger.info(f"[DEPLOY] FRONTEND_BUILD={FRONTEND_BUILD} (exists={FRONTEND_BUILD.exists()})")

if FRONTEND_BUILD.exists() and (FRONTEND_BUILD / "index.html").exists():
    logger.info(f"[DEPLOY] Frontend build ENCONTRADO - Montando SPA em /")
    app.mount("/", SPAStaticFiles(directory=str(FRONTEND_BUILD), html=True), name="frontend")
else:
    logger.warning(f"[DEPLOY] Frontend build NAO encontrado. Modo API-only.")
