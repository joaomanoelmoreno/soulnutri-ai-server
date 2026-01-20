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

from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
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

class IdentifyResponse(BaseModel):
    ok: bool
    identified: bool
    dish: Optional[str] = None
    dish_display: Optional[str] = None
    confidence: str
    score: float
    message: str
    alternatives: List[str] = []
    search_time_ms: Optional[float] = None

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

@api_router.post("/ai/identify", response_model=IdentifyResponse)
async def identify_image(file: UploadFile = File(...)):
    """
    Identifica um prato a partir de uma imagem.
    Meta: resposta em 100ms após a foto.
    
    Returns:
        IdentifyResponse com o prato identificado e nível de confiança
    """
    start_time = time.time()
    
    try:
        from ai.index import get_index
        from ai.policy import analyze_result
        
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
        
        # Buscar no índice
        results = index.search(content, top_k=5)
        
        # Analisar resultado e decidir resposta
        decision = analyze_result(results)
        
        # Calcular tempo total
        elapsed_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Identificação: {decision.get('dish')} ({decision.get('confidence')}) em {elapsed_ms:.0f}ms")
        
        return IdentifyResponse(
            ok=True,
            identified=decision['identified'],
            dish=decision.get('dish'),
            dish_display=decision.get('dish_display'),
            confidence=decision['confidence'],
            score=decision['score'],
            message=decision['message'],
            alternatives=decision.get('alternatives', []),
            search_time_ms=round(elapsed_ms, 2)
        )
        
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
        from ai.policy import format_dish_name
        
        index = get_index()
        
        dishes = []
        for dish_slug, data in index.metadata.items():
            dishes.append({
                'slug': dish_slug,
                'name': format_dish_name(dish_slug),
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
