"""
SoulNutri AI Server
====================
Sistema inteligente de identificação de pratos.
Analogia: Como o Waze para alimentação - mostra o melhor caminho em 100ms.

Endpoints:
- GET  /health              - Health check para Kubernetes
- GET  /api/health          - Status do servidor
- GET  /api/ai/status       - Status do índice de IA
- POST /api/ai/reindex      - Reconstrói o índice
- POST /api/ai/identify     - Identifica um prato por imagem
"""

# IMPORTANTE: Forçar CPU ANTES de qualquer import que possa carregar PyTorch
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["CUDA_HOME"] = ""
os.environ["USE_CUDA"] = "0"
os.environ["FORCE_CPU"] = "1"

from datetime import datetime
import json
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
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

import re

def format_dish_name(name: str) -> str:
    """Formata nome do prato: substitui underscores e capitaliza
    Ex: 'abobora_assada' -> 'Abóbora Assada'
    """
    if not name:
        return name
    
    # Substituir underscores por espaços
    name = name.replace('_', ' ')
    
    # Adicionar espaço antes de letras maiúsculas (camelCase)
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    
    # Capitalizar cada palavra
    words = name.split()
    formatted = ' '.join(word.capitalize() for word in words)
    
    return formatted

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

# Health check endpoint na RAIZ (para Kubernetes)
@app.get("/health")
async def health_check():
    """Health check para Kubernetes - responde rapidamente"""
    return {"status": "healthy", "service": "soulnutri-backend"}

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


@api_router.post("/ai/add-to-index")
async def add_to_index(
    file: UploadFile = File(...),
    dish_name: str = Form(...),
    weight_grams: Optional[int] = Form(None)
):
    """
    Adiciona uma nova foto ao índice local para reconhecimento rápido.
    Use após identificar um prato na balança.
    
    Args:
        file: Imagem do prato
        dish_name: Nome do prato (ex: "Frango Grelhado")
        weight_grams: Peso em gramas (opcional)
    
    Returns:
        Confirmação e tempo estimado de reconhecimento futuro
    """
    import hashlib
    from datetime import datetime
    
    try:
        content = await file.read()
        
        # Normalizar nome do prato para diretório
        dish_slug = dish_name.lower().strip()
        dish_slug = dish_slug.replace(" ", "_").replace("-", "_")
        dish_slug = ''.join(c for c in dish_slug if c.isalnum() or c == '_')
        
        # Criar diretório se não existe
        dish_dir = Path(f"/app/datasets/organized/{dish_slug}")
        dish_dir.mkdir(parents=True, exist_ok=True)
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(content).hexdigest()[:8]
        filename = f"{dish_slug}_{timestamp}_{hash_suffix}.jpg"
        
        # Salvar imagem
        filepath = dish_dir / filename
        with open(filepath, 'wb') as f:
            f.write(content)
        
        # Contar quantas imagens esse prato já tem
        existing_images = len(list(dish_dir.glob("*.jpg")))
        
        logger.info(f"[ADD-INDEX] Foto adicionada: {dish_name} ({existing_images} fotos)")
        
        return {
            "ok": True,
            "dish_name": dish_name,
            "dish_slug": dish_slug,
            "filename": filename,
            "total_images": existing_images,
            "weight_grams": weight_grams,
            "message": f"Foto adicionada! {dish_name} agora tem {existing_images} foto(s).",
            "nota": "Execute /api/ai/reindex para atualizar o índice e ter reconhecimento em ~200ms"
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
        # OTIMIZAÇÃO: Threshold 70% para pratos cadastrados (ECONOMIZAR CRÉDITOS!)
        # Para pratos do Cibi Sana, 70% já é confiança suficiente
        # SEM CHAMAR GEMINI - PRIORIDADE É NÃO GASTAR CRÉDITOS
        # ═══════════════════════════════════════════════════════════════════════
        THRESHOLD_LOCAL = 0.70  # 70% para resposta rápida em pratos conhecidos
        THRESHOLD_MEDIO = 0.50  # 50% ainda usa local com confiança média
        
        # Flag para indicar se IA poderia melhorar o resultado
        ia_disponivel = False
        
        # Se confiança >= 70% no Nível 1, usar resultado direto (RÁPIDO E SEM CRÉDITOS!)
        if nivel1_score >= THRESHOLD_LOCAL and decision.get('identified'):
            decision['source'] = 'local_index'
            decision['cascade_level'] = 1
            logger.info(f"[CASCATA] ⚡ Resultado RÁPIDO do Nível 1 ({nivel1_score:.0%})")
        
        # ─────────────────────────────────────────────────────────────────────
        # NÍVEL 2: Gemini Vision - STAND-BY (só chama se usuário solicitar)
        # ─────────────────────────────────────────────────────────────────────
        elif nivel1_score >= THRESHOLD_MEDIO:
            # Score médio - usa local mas indica que IA poderia ajudar
            decision['source'] = 'local_index'
            decision['cascade_level'] = 1
            decision['confidence'] = 'média'
            ia_disponivel = True  # Marca que IA poderia melhorar
            logger.info(f"[CASCATA] Resultado local médio ({nivel1_score:.0%}) - IA disponível se necessário")
        
        else:
            # Score baixo - usa local mas sugere correção manual
            decision['source'] = 'local_index'
            decision['cascade_level'] = 1
            decision['confidence'] = 'baixa'
            decision['message'] = 'Prato não identificado com certeza. Use o botão de correção.'
            ia_disponivel = True  # Marca que IA poderia ajudar
            logger.info(f"[CASCATA] Score baixo ({nivel1_score:.0%}) - solicitar correção")
        
        # Adicionar flag de IA disponível na decisão
        decision['ia_disponivel'] = ia_disponivel
        
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
        
        # Buscar dados científicos - primeiro MongoDB, depois local
        scientific_data = {}
        mito_verdade = None
        dish_slug = decision.get('dish')
        categoria = decision.get('category', '')
        
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
                logger.info(f"[PREMIUM] Dados científicos do MongoDB para {dish_slug}")
            
            # Se não encontrou no MongoDB, buscar dados Premium LOCAIS (SEM CRÉDITOS)
            if not scientific_data and is_premium:
                try:
                    from services.local_dish_updater import obter_conteudo_premium, encontrar_tipo_prato
                    tipo_prato = encontrar_tipo_prato(dish_slug.replace('_', ' '))
                    premium_local = obter_conteudo_premium(categoria, tipo_prato)
                    scientific_data = {
                        'beneficio_principal': premium_local.get('beneficio_principal'),
                        'curiosidade_cientifica': premium_local.get('curiosidade_cientifica'),
                        'referencia_pesquisa': premium_local.get('referencia_pesquisa'),
                        'alerta_saude': premium_local.get('alerta_saude')
                    }
                    mito_verdade = premium_local.get('mito_verdade')
                    logger.info(f"[PREMIUM] Dados científicos LOCAIS para {dish_slug} (categoria: {categoria})")
                except Exception as e:
                    logger.warning(f"[PREMIUM] Erro ao buscar dados locais: {e}")
        
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
                
                # ═══════════════════════════════════════════════════════════════════
                # NOVIDADES/NOTÍCIAS DO PRATO (PREMIUM)
                # ═══════════════════════════════════════════════════════════════════
                novidade = None
                dish_slug = decision.get('dish')
                if dish_slug:
                    novidade_doc = await db.novidades.find_one(
                        {"dish_slug": dish_slug, "ativa": True},
                        {"_id": 0}
                    )
                    if novidade_doc:
                        novidade = novidade_doc
                        logger.info(f"[PREMIUM] Novidade encontrada para {dish_slug}: {novidade_doc.get('tipo')}")
                
                premium_data = {
                    "alertas_alergenos": alertas_alergenos,
                    "alertas_historico": alertas_historico,
                    "combinacoes_sugeridas": combinacoes,
                    "substituicoes": substituicoes,
                    "novidade": novidade,
                    "is_premium": True
                }
                
                logger.info(f"[PREMIUM] {len(alertas_alergenos)} alertas de alérgenos, {len(alertas_historico)} alertas de histórico")
                
            except Exception as e:
                logger.error(f"[PREMIUM] Erro ao gerar alertas: {e}")
        
        # ═══════════════════════════════════════════════════════════════════════
        # VERDADE OU MITO - EDUCAÇÃO NUTRICIONAL (PREMIUM)
        # ═══════════════════════════════════════════════════════════════════════
        # mito_verdade pode já ter sido definido pelo local_dish_updater
        if is_premium and not mito_verdade:
            try:
                from services.mitos_verdades import get_mito_verdade
                
                ingredientes = decision.get('ingredientes', [])
                categoria = decision.get('category', '')
                
                mito_verdade = get_mito_verdade(
                    ingredientes=ingredientes,
                    categoria=categoria
                )
                
                if mito_verdade:
                    logger.info(f"[PREMIUM] Verdade/Mito: {mito_verdade.get('resposta')}")
                    
            except Exception as e:
                logger.error(f"[PREMIUM] Erro ao buscar mito/verdade: {e}")
        
        # Preparar nutrition como objeto
        nutrition_data = decision.get('nutrition')
        nutrition_obj = NutritionInfo(**nutrition_data) if nutrition_data else None
        
        # Montar resposta base
        response_data = {
            "ok": True,
            "identified": decision['identified'],
            "dish": decision.get('dish'),
            "dish_display": format_dish_name(decision.get('dish_display', '')),
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
            "alternatives": [format_dish_name(a) for a in decision.get('alternatives', [])],
            "search_time_ms": round(elapsed_ms, 2),
            "source": decision.get('source', 'local_index'),
            # Dados científicos - SÓ PREMIUM
            "beneficio_principal": scientific_data.get('beneficio_principal') if is_premium else None,
            "curiosidade_cientifica": scientific_data.get('curiosidade_cientifica') if is_premium else None,
            "referencia_pesquisa": scientific_data.get('referencia_pesquisa') if is_premium else None,
            "alerta_saude": scientific_data.get('alerta_saude') if is_premium else None,
            # Novos campos Premium
            "voce_sabia": scientific_data.get('voce_sabia') if is_premium else None,
            "dica_chef": scientific_data.get('dica_chef') if is_premium else None,
            # Verdade ou Mito - PREMIUM
            "mito_verdade": mito_verdade if is_premium else None,
            # Dados Premium extras
            "premium": premium_data if is_premium else None,
            "is_premium": is_premium,
            # Flag para indicar se IA poderia melhorar o resultado (sem gastar créditos automaticamente)
            "ia_disponivel": decision.get('ia_disponivel', False)
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


@api_router.post("/ai/identify-with-ai")
async def identify_with_ai(
    file: UploadFile = File(...),
    pin: str = Form(""),
    nome: str = Form("")
):
    """
    Identificação usando Gemini Vision - CONSOME CRÉDITOS!
    Usar apenas quando o usuário explicitamente solicitar.
    """
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
                "error": "Serviço de IA não disponível no momento",
                "message": "Use o reconhecimento local ou corrija manualmente"
            }
        
        # Ler e executar o código do backup
        with open(backup_path, 'r') as f:
            backup_code = f.read()
        
        # Criar módulo temporário
        import types
        temp_module = types.ModuleType("generic_ai_temp")
        exec(compile(backup_code, backup_path, 'exec'), temp_module.__dict__)
        
        # Chamar a função de identificação
        result = await temp_module.identify_unknown_dish(content)
        
        if result.get('ok'):
            logger.info(f"[IA SOLICITADA] Gemini identificou: {result.get('nome')} (créditos usados)")
            return {
                "ok": True,
                "identified": True,
                "dish_display": result.get('nome'),
                "category": result.get('categoria'),
                "category_emoji": result.get('category_emoji', '🍽️'),
                "confidence": result.get('confianca', 'média'),
                "score": result.get('score', 0.7),
                "ingredientes": result.get('ingredientes_provaveis', []),
                "beneficios": result.get('beneficios', []),
                "descricao": result.get('descricao', ''),
                "source": "gemini_ai",
                "creditos_usados": True,
                "message": "Identificado com IA (créditos consumidos)"
            }
        else:
            return {
                "ok": False,
                "error": result.get('error', 'Erro na identificação'),
                "creditos_usados": False
            }
            
    except Exception as e:
        logger.error(f"[IA SOLICITADA] Erro: {e}")
        return {
            "ok": False,
            "error": str(e),
            "creditos_usados": False
        }


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
    REGRA: Se já existe prato similar no banco, adiciona foto ao existente ao invés de criar novo.
    """
    try:
        import uuid
        from datetime import datetime
        from pathlib import Path
        from difflib import SequenceMatcher
        from services.generic_ai import identify_unknown_dish
        
        if not dish_name.strip():
            return {"ok": False, "error": "Nome do prato é obrigatório"}
        
        content = await file.read()
        
        # Gerar slug do nome fornecido
        slug = dish_name.lower().strip()
        slug = ''.join(c for c in slug if c.isalnum() or c == ' ')
        slug = slug.replace(' ', '_')
        
        # VERIFICAR SE JÁ EXISTE PRATO SIMILAR NO BANCO
        dataset_dir = Path("/app/datasets/organized")
        existing_match = None
        
        for dish_dir in dataset_dir.iterdir():
            if not dish_dir.is_dir():
                continue
            info_path = dish_dir / "dish_info.json"
            if info_path.exists():
                try:
                    import json
                    with open(info_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        existing_name = info.get('nome', '').lower()
                        # Verificar similaridade > 85%
                        similarity = SequenceMatcher(None, dish_name.lower(), existing_name).ratio()
                        if similarity > 0.85 or dish_dir.name == slug:
                            existing_match = dish_dir.name
                            logger.info(f"[CREATE] Prato similar encontrado: {existing_match} ({similarity:.0%})")
                            break
                except:
                    pass
        
        # Se encontrou match, adiciona foto ao prato existente E atualiza informações com IA
        if existing_match:
            target_dir = dataset_dir / existing_match
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{existing_match}_{timestamp}_{unique_id}.jpg"
            file_path = target_dir / filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # CHAMAR IA para atualizar informações do prato
            try:
                from services.generic_ai import fix_dish_data_with_ai
                
                # Carregar info atual
                info_path = target_dir / "dish_info.json"
                current_info = {}
                if info_path.exists():
                    with open(info_path, 'r', encoding='utf-8') as f:
                        current_info = json.load(f)
                
                # Atualizar nome se o usuário digitou diferente (correção)
                if dish_name.strip() and dish_name.strip().lower() != current_info.get('nome', '').lower():
                    current_info['nome'] = dish_name.strip()
                    logger.info(f"[CREATE] Nome atualizado: {current_info.get('nome')} -> {dish_name.strip()}")
                
                # Chamar IA para completar informações faltantes
                ai_result = await fix_dish_data_with_ai(content, current_info)
                
                if ai_result.get('ok'):
                    # Mesclar informações (IA complementa o que está faltando)
                    updated_info = {**current_info}
                    for key, value in ai_result.items():
                        if key == 'ok':
                            continue
                        # Só atualiza se estava vazio ou é nutrição vazia
                        if key == 'nutricao':
                            nut = updated_info.get('nutricao', {})
                            ai_nut = value or {}
                            for nk, nv in ai_nut.items():
                                if not nut.get(nk) and nv:
                                    nut[nk] = nv
                            updated_info['nutricao'] = nut
                        elif not updated_info.get(key) and value:
                            updated_info[key] = value
                    
                    # Garantir nome corrigido pelo usuário
                    if dish_name.strip():
                        updated_info['nome'] = dish_name.strip()
                    
                    updated_info['slug'] = existing_match
                    
                    with open(info_path, 'w', encoding='utf-8') as f:
                        json.dump(updated_info, f, ensure_ascii=False, indent=2, default=str)
                    
                    logger.info(f"[CREATE] Informações atualizadas com IA para: {existing_match}")
            except Exception as e:
                logger.error(f"[CREATE] Erro ao atualizar com IA: {e}")
            
            return {
                "ok": True,
                "message": f"✅ Prato '{dish_name}' salvo! Foto e informações atualizadas.",
                "slug": existing_match,
                "action": "updated_existing"
            }
        
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
        
        # Salvar dish_info.json na pasta
        import json
        dish_info_for_file = {
            "nome": dish_info["nome"],
            "slug": dish_info["slug"],
            "categoria": dish_info["categoria"],
            "category_emoji": dish_info["category_emoji"],
            "descricao": dish_info["descricao"],
            "ingredientes": dish_info["ingredientes"],
            "beneficios": dish_info["beneficios"],
            "riscos": dish_info["riscos"],
            "tecnica": dish_info["tecnica"],
            "nutricao": dish_info["nutricao"],
            "contem_gluten": dish_info["contem_gluten"]
        }
        dish_info_path = dataset_dir / "dish_info.json"
        with open(dish_info_path, "w", encoding="utf-8") as f:
            json.dump(dish_info_for_file, f, ensure_ascii=False, indent=2)
        
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


@api_router.post("/ai/create-dish-local")
async def create_dish_local(
    file: UploadFile = File(...),
    dish_name: str = Form("")
):
    """
    Cria/corrige um prato usando APENAS dados LOCAIS, SEM chamar IA, SEM gastar créditos.
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
            return {"ok": False, "error": "Nome do prato é obrigatório"}
        
        content = await file.read()
        
        # Gerar slug do nome fornecido
        slug = dish_name.lower().strip()
        slug = ''.join(c for c in slug if c.isalnum() or c == ' ')
        slug = slug.replace(' ', '_')
        
        # VERIFICAR SE JÁ EXISTE PRATO SIMILAR NO BANCO
        dataset_dir = Path("/app/datasets/organized")
        existing_match = None
        
        for dish_dir in dataset_dir.iterdir():
            if not dish_dir.is_dir():
                continue
            info_path = dish_dir / "dish_info.json"
            if info_path.exists():
                try:
                    with open(info_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        existing_name = info.get('nome', '').lower()
                        # Verificar similaridade > 85%
                        similarity = SequenceMatcher(None, dish_name.lower(), existing_name).ratio()
                        if similarity > 0.85 or dish_dir.name == slug:
                            existing_match = dish_dir.name
                            logger.info(f"[CREATE-LOCAL] Prato similar encontrado: {existing_match} ({similarity:.0%})")
                            break
                except:
                    pass
        
        # Se encontrou match, adiciona foto ao prato existente E atualiza com dados locais
        if existing_match:
            target_dir = dataset_dir / existing_match
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{existing_match}_correct_{timestamp}_{unique_id}.jpg"
            file_path = target_dir / filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Usar dados LOCAIS para atualizar informações
            info_path = target_dir / "dish_info.json"
            current_info = {}
            if info_path.exists():
                with open(info_path, 'r', encoding='utf-8') as f:
                    current_info = json.load(f)
            
            # Atualizar nome se diferente
            if dish_name.strip() and dish_name.strip().lower() != current_info.get('nome', '').lower():
                current_info['nome'] = dish_name.strip()
                logger.info(f"[CREATE-LOCAL] Nome corrigido para: {dish_name.strip()}")
            
            # Usar local_dish_updater para preencher dados faltantes
            result = atualizar_prato_local(existing_match, novo_nome=dish_name.strip())
            
            return {
                "ok": True,
                "message": f"✅ Correção salva! '{dish_name}' atualizado SEM usar créditos.",
                "slug": existing_match,
                "action": "updated_existing_local",
                "credits_used": 0
            }
        
        # CRIAR NOVO PRATO com dados LOCAIS
        target_dir = dataset_dir / slug
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar imagem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{slug}_{timestamp}_{unique_id}.jpg"
        file_path = target_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Gerar dados usando regras LOCAIS
        tipo = encontrar_tipo_prato(dish_name)
        categoria = detectar_categoria_basica(dish_name)
        alergenos = detectar_alergenos_por_nome(dish_name)
        
        # Pegar template se existir
        dados_template = PRATOS_COMPLETOS.get(tipo, {})
        
        # Emoji baseado na categoria
        emoji_map = {"vegano": "🌱", "vegetariano": "🥚", "proteína animal": "🍖"}
        
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
            "melhor_horario": dados_template.get('melhor_horario', 'Almoço'),
            "combina_com": dados_template.get('combina_com', []),
            "evitar_com": dados_template.get('evitar_com', []),
            "origem": "user_created_local"
        }
        
        # Salvar dish_info.json
        dish_info_path = target_dir / "dish_info.json"
        with open(dish_info_path, "w", encoding="utf-8") as f:
            json.dump(dish_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[CREATE-LOCAL] Novo prato criado SEM IA: {dish_name} -> {slug}")
        
        return {
            "ok": True,
            "message": f"✅ Prato '{dish_name}' criado com sucesso SEM usar créditos!",
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
    
    ESTRATÉGIA HÍBRIDA:
    1. Zoom central (50%) → Identifica item PRINCIPAL no índice local
    2. Análise por regiões → Busca ACOMPANHAMENTOS por similaridade nos pratos do buffet
    3. Fallback Gemini → Para itens não reconhecidos
    
    Returns:
        Item principal + acompanhamentos reconhecidos do buffet do Cibi Sana
    """
    start_time = time.time()
    
    try:
        from services.hybrid_identify_v5 import identify_multi_v5
        
        content = await file.read()
        
        if len(content) == 0:
            return {"ok": False, "error": "Arquivo de imagem vazio"}
        
        logger.info("[v5] Identificação com busca ampla e filtragem inteligente...")
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
                    'categoria': result['principal'].get('categoria', 'proteína animal'),
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
        logger.error(f"Erro na identificação múltipla híbrida: {e}")
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
    Verifica também se o Premium está liberado pelo admin.
    """
    try:
        from services.profile_service import hash_pin
        from datetime import datetime
        
        pin_hash = hash_pin(pin)
        # Buscar por nome E pin_hash
        user = await db.users.find_one(
            {"pin_hash": pin_hash, "nome": {"$regex": f"^{nome}$", "$options": "i"}},
            {"_id": 0, "pin_hash": 0}
        )
        
        if not user:
            return {"ok": False, "error": "Nome ou PIN incorreto"}
        
        # Verificar se Premium está ativo e não expirou
        premium_ativo = user.get("premium_ativo", False)
        premium_expira_em = user.get("premium_expira_em")
        
        if premium_expira_em:
            try:
                expiracao = datetime.fromisoformat(premium_expira_em)
                if datetime.now() > expiracao:
                    premium_ativo = False
                    # Atualizar no banco
                    await db.users.update_one(
                        {"nome": {"$regex": f"^{nome}$", "$options": "i"}},
                        {"$set": {"premium_ativo": False, "premium_expirado": True}}
                    )
            except:
                pass
        
        # Adicionar status Premium à resposta
        user["premium_ativo"] = premium_ativo
        
        # Se Premium não está ativo, retornar mensagem informativa
        if not premium_ativo:
            return {
                "ok": True,
                "user": user,
                "premium_bloqueado": True,
                "message": f"Olá, {user['nome']}! Seu acesso Premium ainda não foi liberado. Entre em contato para ativação."
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


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN - Endpoints de administração do banco de dados
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/admin/dishes")
async def admin_list_dishes():
    """Lista todos os pratos com informações detalhadas para admin."""
    try:
        import json
        dataset_dir = Path("/app/datasets/organized")
        dishes = []
        
        for dish_dir in sorted(dataset_dir.iterdir()):
            if not dish_dir.is_dir():
                continue
            
            slug = dish_dir.name
            info_file = dish_dir / "dish_info.json"
            
            # Contar imagens
            image_count = len(list(dish_dir.glob("*.jpg"))) + len(list(dish_dir.glob("*.jpeg")))
            
            dish_data = {
                "slug": slug,
                "nome": slug.replace("_", " ").title(),
                "categoria": "",
                "category_emoji": "🍽️",
                "ingredientes": [],
                "descricao": "",
                "image_count": image_count
            }
            
            # Carregar info se existir
            if info_file.exists():
                try:
                    with open(info_file, "r", encoding="utf-8") as f:
                        info = json.load(f)
                        dish_data.update({
                            "nome": info.get("nome", dish_data["nome"]),
                            "categoria": info.get("categoria", ""),
                            "category_emoji": info.get("category_emoji", "🍽️"),
                            "ingredientes": info.get("ingredientes", []),
                            "descricao": info.get("descricao", "")
                        })
                except:
                    pass
            
            dishes.append(dish_data)
        
        return {"ok": True, "dishes": dishes, "total": len(dishes)}
        
    except Exception as e:
        logger.error(f"Erro ao listar pratos admin: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/dishes-full")
async def admin_list_dishes_full():
    """Lista todos os pratos com TODAS as informações para admin."""
    try:
        import json
        dataset_dir = Path("/app/datasets/organized")
        dishes = []
        
        for dish_dir in sorted(dataset_dir.iterdir()):
            if not dish_dir.is_dir():
                continue
            
            slug = dish_dir.name
            info_file = dish_dir / "dish_info.json"
            
            # Contar e listar imagens
            images = list(dish_dir.glob("*.jpg")) + list(dish_dir.glob("*.jpeg"))
            image_count = len(images)
            first_image = images[0].name if images else None
            
            dish_data = {
                "slug": slug,
                "nome": slug.replace("_", " ").title(),
                "categoria": "",
                "category_emoji": "🍽️",
                "ingredientes": [],
                "descricao": "",
                "beneficios": [],
                "riscos": [],
                "nutricao": {},
                "contem_gluten": False,
                "tecnica": "",
                "image_count": image_count,
                "first_image": first_image
            }
            
            # Carregar info completa se existir
            if info_file.exists():
                try:
                    with open(info_file, "r", encoding="utf-8") as f:
                        info = json.load(f)
                        dish_data.update({
                            "nome": info.get("nome", dish_data["nome"]),
                            "categoria": info.get("categoria", ""),
                            "category_emoji": info.get("category_emoji", "🍽️"),
                            "ingredientes": info.get("ingredientes", []),
                            "descricao": info.get("descricao", ""),
                            "beneficios": info.get("beneficios", []),
                            "riscos": info.get("riscos", []),
                            "nutricao": info.get("nutricao", {}),
                            "contem_gluten": info.get("contem_gluten", False),
                            "tecnica": info.get("tecnica", "")
                        })
                except:
                    pass
            
            dishes.append(dish_data)
        
        return {"ok": True, "dishes": dishes, "total": len(dishes)}
        
    except Exception as e:
        logger.error(f"Erro ao listar pratos admin full: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/dish-image/{slug}")
async def admin_get_dish_image(slug: str):
    """Retorna a primeira imagem de um prato."""
    from fastapi.responses import FileResponse
    
    try:
        dataset_dir = Path("/app/datasets/organized") / slug
        
        if not dataset_dir.exists():
            raise HTTPException(status_code=404, detail="Prato não encontrado")
        
        # Buscar primeira imagem
        images = list(dataset_dir.glob("*.jpg")) + list(dataset_dir.glob("*.jpeg"))
        
        if not images:
            raise HTTPException(status_code=404, detail="Sem imagens")
        
        return FileResponse(images[0], media_type="image/jpeg")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar imagem: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/admin/dishes/{slug}")
async def admin_update_dish(slug: str, dish_data: dict):
    """Atualiza TODAS as informações de um prato."""
    try:
        import json
        dataset_dir = Path("/app/datasets/organized") / slug
        
        if not dataset_dir.exists():
            return {"ok": False, "error": "Prato não encontrado"}
        
        info_file = dataset_dir / "dish_info.json"
        
        # Carregar info existente ou criar nova
        existing_info = {}
        if info_file.exists():
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    existing_info = json.load(f)
            except:
                pass
        
        # Atualizar TODOS os campos
        existing_info.update({
            "nome": dish_data.get("nome", existing_info.get("nome", slug)),
            "slug": slug,
            "categoria": dish_data.get("categoria", existing_info.get("categoria", "")),
            "descricao": dish_data.get("descricao", existing_info.get("descricao", "")),
            "ingredientes": dish_data.get("ingredientes", existing_info.get("ingredientes", [])),
            "beneficios": dish_data.get("beneficios", existing_info.get("beneficios", [])),
            "riscos": dish_data.get("riscos", existing_info.get("riscos", [])),
            "nutricao": dish_data.get("nutricao", existing_info.get("nutricao", {})),
            "contem_gluten": dish_data.get("contem_gluten", existing_info.get("contem_gluten", False)),
            "contem_lactose": dish_data.get("contem_lactose", existing_info.get("contem_lactose", False)),
            "contem_ovo": dish_data.get("contem_ovo", existing_info.get("contem_ovo", False)),
            "contem_castanhas": dish_data.get("contem_castanhas", existing_info.get("contem_castanhas", False)),
            "contem_frutos_mar": dish_data.get("contem_frutos_mar", existing_info.get("contem_frutos_mar", False)),
            "contem_soja": dish_data.get("contem_soja", existing_info.get("contem_soja", False)),
            "tecnica": dish_data.get("tecnica", existing_info.get("tecnica", ""))
        })
        
        # Definir emoji baseado na categoria
        cat = existing_info.get("categoria", "").lower()
        nome_lower = existing_info.get("nome", "").lower()
        
        if "proteína" in cat:
            if any(p in nome_lower for p in ["peixe", "camarão", "bacalhau", "salmão", "atum", "tilápia", "pescador"]):
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
        
        # Salvar
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(existing_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[ADMIN] Prato atualizado: {slug}")
        return {"ok": True, "message": "Prato atualizado"}
        
    except Exception as e:
        logger.error(f"Erro ao atualizar prato: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/dishes/{slug}/regenerate")
async def admin_regenerate_dish_info(slug: str, data: dict = None):
    """
    Regenera TODAS as informações de um prato baseado no nome.
    Útil quando o usuário corrige o nome e quer atualizar toda a ficha.
    
    Body opcional:
    {
        "new_name": "Novo Nome do Prato"  // se não fornecido, usa o nome atual
    }
    """
    try:
        from services.generic_ai import regenerate_dish_info_from_name
        
        dataset_dir = Path("/app/datasets/organized") / slug
        
        if not dataset_dir.exists():
            return {"ok": False, "error": "Prato não encontrado"}
        
        info_file = dataset_dir / "dish_info.json"
        
        # Carregar info atual
        current_info = {}
        if info_file.exists():
            try:
                with open(info_file, "r", encoding="utf-8") as f:
                    current_info = json.load(f)
            except:
                pass
        
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
            # Mesclar com dados existentes (manter slug)
            new_info = {**current_info}
            
            # Atualizar todos os campos regenerados
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
            
            if "proteína" in cat:
                if any(p in nome_lower for p in ["peixe", "camarão", "bacalhau", "salmão", "atum"]):
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
            
            # Salvar
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(new_info, f, ensure_ascii=False, indent=2)
            
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
    """Exclui um prato e todas suas fotos."""
    try:
        import shutil
        dataset_dir = Path("/app/datasets/organized") / slug
        
        if not dataset_dir.exists():
            return {"ok": False, "error": "Prato não encontrado"}
        
        # Remover pasta e todos os arquivos
        shutil.rmtree(dataset_dir)
        
        logger.info(f"[ADMIN] Prato excluído: {slug}")
        return {"ok": True, "message": f"Prato {slug} excluído"}
        
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
        logger.info(f"[ADMIN] Atualização local em massa: {result['atualizados']}/{result['total']}")
        
        return {"ok": True, **result}
        
    except Exception as e:
        logger.error(f"Erro na atualização em massa: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# AUDITORIA - Análise de qualidade dos dados dos pratos
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/admin/audit")
async def admin_audit_dishes():
    """Audita todos os pratos e retorna relatório de problemas de qualidade"""
    try:
        from services.audit_service import audit_all_dishes
        
        result = audit_all_dishes()
        return {"ok": True, **result}
        
    except Exception as e:
        logger.error(f"Erro na auditoria: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/audit/fix/{slug}")
async def admin_fix_dish_with_ai(slug: str):
    """Usa IA para sugerir correções para um prato específico"""
    try:
        from services.audit_service import fix_dish_with_ai
        
        result = await fix_dish_with_ai(slug)
        return result
        
    except Exception as e:
        logger.error(f"Erro ao corrigir prato {slug}: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/audit/apply/{slug}")
async def admin_apply_ai_suggestions(slug: str, suggestions: dict):
    """Aplica as sugestões da IA ao prato"""
    try:
        from services.audit_service import apply_ai_suggestions
        
        result = apply_ai_suggestions(slug, suggestions)
        return result
        
    except Exception as e:
        logger.error(f"Erro ao aplicar sugestões para {slug}: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/audit/fix-single/{slug}")
async def admin_fix_single_dish(slug: str):
    """Usa IA para corrigir dados de um único prato"""
    try:
        from services.generic_ai import fix_dish_data_with_ai
        from pathlib import Path
        import json
        
        dataset_dir = Path("/app/datasets/organized")
        dish_dir = dataset_dir / slug
        info_path = dish_dir / "dish_info.json"
        
        # Carregar info atual
        current_info = {}
        if info_path.exists():
            with open(info_path, 'r', encoding='utf-8') as f:
                current_info = json.load(f)
        
        # Buscar imagem
        images = list(dish_dir.glob("*.jpg")) + list(dish_dir.glob("*.jpeg"))
        if not images:
            return {"ok": False, "error": "Nenhuma imagem encontrada"}
        
        # Ler imagem
        with open(images[0], 'rb') as f:
            image_bytes = f.read()
        
        # Chamar IA
        result = await fix_dish_data_with_ai(image_bytes, current_info)
        
        if result.get("ok"):
            # Mesclar e salvar
            new_info = {**current_info, **result}
            new_info.pop("ok", None)
            new_info["slug"] = slug
            
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(new_info, f, ensure_ascii=False, indent=2)
            
            return {"ok": True, "message": f"Prato {slug} corrigido", "data": new_info}
        else:
            return result
        
    except Exception as e:
        logger.error(f"Erro ao corrigir prato {slug}: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/audit/batch-fix")
async def admin_batch_fix_dishes(request: dict):
    """Corrige múltiplos pratos em lote usando IA"""
    try:
        from services.generic_ai import batch_fix_dishes
        
        slugs = request.get("slugs", [])
        if not slugs:
            return {"ok": False, "error": "Nenhum slug fornecido"}
        
        # Limitar a 10 por vez para não sobrecarregar
        slugs = slugs[:10]
        
        result = await batch_fix_dishes(slugs, max_concurrent=2)
        return {"ok": True, **result}
        
    except Exception as e:
        logger.error(f"Erro no batch fix: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/duplicates")
async def get_duplicate_groups():
    """Retorna grupos de pratos duplicados para consolidação"""
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
        logger.error(f"Erro na consolidação em massa: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNACIONALIZAÇÃO - Suporte a múltiplos idiomas (GRATUITO com LibreTranslate)
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
    """Retorna traduções da interface para o idioma especificado"""
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
        logger.error(f"Erro ao buscar traduções: {e}")
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
        logger.error(f"Erro na tradução: {e}")
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


# ═══════════════════════════════════════════════════════════════════════════════
# NOVIDADES/NOTÍCIAS PREMIUM - Sistema de alertas em tempo real para o buffet
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/novidades/{dish_slug}")
async def get_dish_novidade(dish_slug: str):
    """
    Retorna novidade/notícia de um prato específico (se houver).
    Usado na versão Premium para mostrar alertas ao escanear um item.
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
    - info: Informação positiva (ex: "Novo estudo confirma benefícios")
    - alerta: Alerta importante (ex: "Lote com problema")
    - dica: Dica de combinação ou consumo
    - estudo: Estudo científico recente
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
        
        # Upsert - atualiza se existir, insere se não
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
            return {"ok": False, "error": "Novidade não encontrada"}
            
    except Exception as e:
        logger.error(f"Erro ao remover novidade: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN - GERENCIAMENTO DE PREMIUM
# Sistema para liberar/bloquear acesso Premium manualmente
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/admin/premium/users")
async def admin_list_premium_users():
    """Lista todos os usuários Premium cadastrados."""
    try:
        users = await db.users.find(
            {},
            {"_id": 0, "pin_hash": 0}
        ).to_list(500)
        
        return {
            "ok": True,
            "total": len(users),
            "users": users
        }
    except Exception as e:
        logger.error(f"Erro ao listar usuários Premium: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/premium/liberar")
async def admin_liberar_premium(
    nome: str = Form(...),
    dias: int = Form(30)
):
    """
    Libera acesso Premium para um usuário por X dias.
    
    Args:
        nome: Nome do usuário (case insensitive)
        dias: Número de dias de acesso (padrão: 30)
    """
    from datetime import datetime, timedelta
    
    try:
        # Buscar usuário pelo nome
        user = await db.users.find_one(
            {"nome": {"$regex": f"^{nome}$", "$options": "i"}},
            {"_id": 0}
        )
        
        if not user:
            return {"ok": False, "error": f"Usuário '{nome}' não encontrado"}
        
        # Calcular data de expiração
        data_expiracao = datetime.now() + timedelta(days=dias)
        
        # Atualizar status Premium
        await db.users.update_one(
            {"nome": {"$regex": f"^{nome}$", "$options": "i"}},
            {
                "$set": {
                    "premium_ativo": True,
                    "premium_liberado_em": datetime.now().isoformat(),
                    "premium_expira_em": data_expiracao.isoformat(),
                    "premium_dias": dias
                }
            }
        )
        
        logger.info(f"[ADMIN] Premium liberado para {nome} por {dias} dias")
        
        return {
            "ok": True,
            "message": f"Premium liberado para {nome}",
            "nome": nome,
            "dias": dias,
            "expira_em": data_expiracao.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao liberar Premium: {e}")
        return {"ok": False, "error": str(e)}


@api_router.post("/admin/premium/bloquear")
async def admin_bloquear_premium(nome: str = Form(...)):
    """
    Bloqueia/revoga acesso Premium de um usuário.
    
    Args:
        nome: Nome do usuário (case insensitive)
    """
    try:
        result = await db.users.update_one(
            {"nome": {"$regex": f"^{nome}$", "$options": "i"}},
            {
                "$set": {
                    "premium_ativo": False,
                    "premium_bloqueado_em": __import__('datetime').datetime.now().isoformat()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"[ADMIN] Premium bloqueado para {nome}")
            return {"ok": True, "message": f"Premium bloqueado para {nome}"}
        else:
            return {"ok": False, "error": f"Usuário '{nome}' não encontrado"}
            
    except Exception as e:
        logger.error(f"Erro ao bloquear Premium: {e}")
        return {"ok": False, "error": str(e)}


@api_router.get("/admin/premium/status/{nome}")
async def admin_verificar_premium(nome: str):
    """Verifica status Premium de um usuário específico."""
    try:
        user = await db.users.find_one(
            {"nome": {"$regex": f"^{nome}$", "$options": "i"}},
            {"_id": 0, "pin_hash": 0}
        )
        
        if not user:
            return {"ok": False, "error": f"Usuário '{nome}' não encontrado"}
        
        return {
            "ok": True,
            "user": user
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar Premium: {e}")
        return {"ok": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# CHECK-IN DE REFEIÇÃO - Registrar consumo com múltiplos itens
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.post("/premium/checkin")
async def premium_checkin(
    pin: str = Form(...),
    nome: str = Form(...),
    itens: str = Form(...),  # JSON array: [{"nome": "Arroz", "porcao": "media"}, ...]
    foto: Optional[UploadFile] = File(None)
):
    """
    Check-in de refeição Premium - registra múltiplos itens de uma vez.
    
    Args:
        pin: PIN do usuário Premium
        nome: Nome do usuário
        itens: JSON array com itens e porções
        foto: Foto opcional do prato (para histórico)
    
    Returns:
        Resumo nutricional total e atualização do consumo diário
    """
    import json as json_lib
    from datetime import datetime
    from services.profile_service import hash_pin
    
    try:
        # Verificar usuário Premium
        pin_hash = hash_pin(pin)
        user = await db.users.find_one(
            {"pin_hash": pin_hash, "nome": {"$regex": f"^{nome}$", "$options": "i"}},
            {"_id": 0}
        )
        
        if not user:
            return {"ok": False, "error": "Usuário não encontrado"}
        
        # Parse dos itens
        try:
            itens_list = json_lib.loads(itens)
        except:
            return {"ok": False, "error": "Formato de itens inválido"}
        
        # Porções estimadas (g)
        porcoes_g = {
            "pequena": 50,
            "media": 100,
            "grande": 150
        }
        
        # Calcular totais
        total_calorias = 0
        total_proteinas = 0
        total_carboidratos = 0
        total_gorduras = 0
        itens_registrados = []
        
        for item in itens_list:
            nome_item = item.get("nome", "")
            porcao = item.get("porcao", "media")
            gramas = porcoes_g.get(porcao, 100)
            
            # Buscar info nutricional do item
            # Primeiro tenta no índice local, depois usa estimativa
            nutri = {"calorias": 150, "proteinas": 8, "carboidratos": 20, "gorduras": 5}
            
            # Buscar no dataset organizado
            from ai.index import get_index
            index = get_index()
            
            for slug, data in index.metadata.items():
                if nome_item.lower() in data.get('name', '').lower():
                    # Encontrou - buscar info do dish_info.json
                    info_path = Path(f"/app/datasets/organized/{slug}/dish_info.json")
                    if info_path.exists():
                        with open(info_path, "r", encoding="utf-8") as f:
                            dish_info = json_lib.load(f)
                            nutricao = dish_info.get("nutricao", {})
                            if nutricao.get("calorias"):
                                try:
                                    nutri["calorias"] = float(str(nutricao["calorias"]).replace("kcal", "").replace("~", "").strip() or 150)
                                except:
                                    pass
                    break
            
            # Ajustar pela porção
            fator = gramas / 100
            calorias_item = nutri["calorias"] * fator
            proteinas_item = nutri["proteinas"] * fator
            carbos_item = nutri["carboidratos"] * fator
            gorduras_item = nutri["gorduras"] * fator
            
            total_calorias += calorias_item
            total_proteinas += proteinas_item
            total_carboidratos += carbos_item
            total_gorduras += gorduras_item
            
            itens_registrados.append({
                "nome": nome_item,
                "porcao": porcao,
                "gramas": gramas,
                "calorias": round(calorias_item),
                "proteinas": round(proteinas_item, 1),
                "carboidratos": round(carbos_item, 1),
                "gorduras": round(gorduras_item, 1)
            })
        
        # Registrar no histórico diário
        hoje = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M")
        
        # Atualizar ou criar registro do dia
        await db.daily_logs.update_one(
            {"pin_hash": pin_hash, "data": hoje},
            {
                "$inc": {
                    "calorias_total": round(total_calorias),
                    "proteinas_total": round(total_proteinas, 1),
                    "carboidratos_total": round(total_carboidratos, 1),
                    "gorduras_total": round(total_gorduras, 1)
                },
                "$push": {
                    "refeicoes": {
                        "hora": hora,
                        "itens": itens_registrados,
                        "total_calorias": round(total_calorias),
                        "tipo": "checkin"
                    }
                },
                "$setOnInsert": {
                    "nome": nome,
                    "data": hoje
                }
            },
            upsert=True
        )
        
        # Buscar novo total do dia
        daily_log = await db.daily_logs.find_one(
            {"pin_hash": pin_hash, "data": hoje},
            {"_id": 0}
        )
        
        meta = user.get("meta_calorica", {}).get("meta_sugerida", 2000)
        consumido = daily_log.get("calorias_total", 0)
        restante = meta - consumido
        percentual = (consumido / meta) * 100
        
        return {
            "ok": True,
            "message": f"Check-in registrado: {len(itens_registrados)} itens",
            "refeicao": {
                "itens": itens_registrados,
                "total_calorias": round(total_calorias),
                "total_proteinas": round(total_proteinas, 1),
                "total_carboidratos": round(total_carboidratos, 1),
                "total_gorduras": round(total_gorduras, 1)
            },
            "dia": {
                "consumido": round(consumido),
                "meta": meta,
                "restante": round(restante),
                "percentual": round(percentual, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no check-in: {e}")
        return {"ok": False, "error": str(e)}
