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
        
        # Se confiança baixa ou não identificado, tentar IA genérica
        if decision['confidence'] == 'baixa' or not decision['identified'] or decision['score'] < 0.5:
            try:
                from services.generic_ai import identify_unknown_dish
                
                logger.info("Confiança baixa no índice local, usando IA genérica...")
                generic_result = await identify_unknown_dish(content)
                
                if generic_result.get('ok') and generic_result.get('nome'):
                    # Usar resultado da IA genérica
                    decision = {
                        'identified': True,
                        'dish': 'unknown_' + generic_result.get('nome', '').lower().replace(' ', '_'),
                        'dish_display': generic_result.get('nome', 'Prato Desconhecido'),
                        'confidence': generic_result.get('confianca', 'baixa'),
                        'score': generic_result.get('score', 0.5),
                        'message': f"Identificado por IA genérica: {generic_result.get('nome')}",
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
                        'source': 'generic_ai'
                    }
                    logger.info(f"IA genérica identificou: {decision['dish_display']}")
            except Exception as e:
                logger.warning(f"Erro na IA genérica: {e}")
        
        # Calcular tempo total
        elapsed_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Identificação: {decision.get('dish')} ({decision.get('confidence')}) em {elapsed_ms:.0f}ms")
        
        # Preparar nutrition como objeto
        nutrition_data = decision.get('nutrition')
        nutrition_obj = NutritionInfo(**nutrition_data) if nutrition_data else None
        
        return IdentifyResponse(
            ok=True,
            identified=decision['identified'],
            dish=decision.get('dish'),
            dish_display=decision.get('dish_display'),
            confidence=decision['confidence'],
            score=decision['score'],
            message=decision['message'],
            category=decision.get('category'),
            category_emoji=decision.get('category_emoji'),
            nutrition=nutrition_obj,
            descricao=decision.get('descricao'),
            ingredientes=decision.get('ingredientes'),
            tecnica=decision.get('tecnica'),
            beneficios=decision.get('beneficios'),
            riscos=decision.get('riscos'),
            aviso_cibi_sana=decision.get('aviso_cibi_sana'),
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
