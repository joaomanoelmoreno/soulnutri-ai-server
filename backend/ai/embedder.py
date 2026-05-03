"""SoulNutri AI - Embedder CLIP
Versao hibrida: ONNX Runtime (deploy) / PyTorch (dev local)
"""

import os
import numpy as np
from PIL import Image
import io
import time
import logging

logger = logging.getLogger(__name__)

# Cache global
_MODEL = None
_PREPROCESS = None
_DEVICE = "cpu"
_USE_HF_API = True
_USE_ONNX = False  # True quando modelo ONNX esta disponivel
_ONNX_SESSION = None

# ═══════════════════════════════════════════════════════
# Estado em memoria para diagnostico de performance
# Acessado via get_performance_stats() para /api/debug/performance.
# Zero persistencia. Zero MongoDB. Resetado a cada reboot.
# ═══════════════════════════════════════════════════════
_LAST_INFERENCE_MS = None
_INFERENCE_COUNT = 0
_TOTAL_INFERENCE_MS = 0.0
_ONNX_CONFIG = {
    "onnx_mode": None,
    "inter_op_num_threads": None,
    "intra_op_num_threads": None,
}

# Caminho do modelo ONNX (gerado no Docker build)
ONNX_MODEL_PATH = "/app/clip_visual_fp16.onnx"

# Constantes CLIP ViT-B-16 preprocessing
CLIP_MEAN = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
CLIP_STD = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)


def _preprocess_clip_numpy(img):
    """Preprocessing CLIP ViT-B-16 com PIL + numpy (sem torch)"""
    # Resize shortest side to 224 (bicubic)
    w, h = img.size
    if w < h:
        new_w = 224
        new_h = int(h * 224 / w)
    else:
        new_h = 224
        new_w = int(w * 224 / h)
    img = img.resize((new_w, new_h), Image.BICUBIC)
    
    # Center crop 224x224
    left = (new_w - 224) // 2
    top = (new_h - 224) // 2
    img = img.crop((left, top, left + 224, top + 224))
    
    # To numpy float32 [0, 1]
    arr = np.array(img).astype(np.float32) / 255.0
    
    # Normalize
    arr = (arr - CLIP_MEAN) / CLIP_STD
    
    # HWC -> CHW -> BCHW
    arr = arr.transpose(2, 0, 1)[np.newaxis, ...]
    return arr


def _try_load_onnx_model():
    """Tenta carregar modelo ONNX (deploy - usa ~300MB RAM)"""
    global _ONNX_SESSION, _USE_ONNX, _USE_HF_API
    
    if not os.path.exists(ONNX_MODEL_PATH):
        return False
    
    try:
        import onnxruntime as ort
        
        logger.info("[embedder] Carregando modelo CLIP via ONNX Runtime (deploy)...")
        start = time.time()
        
        # ═══════════════════════════════════════════════════════
        # CRITICAL:
        # Nao alterar para ORT_DISABLE_ALL.
        # Isso causa inferencia de 9-50 segundos no Render.
        # Esta configuracao foi validada em producao em Abr/2026.
        # ═══════════════════════════════════════════════════════
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        opts.inter_op_num_threads = 2
        opts.intra_op_num_threads = 2
        opts.enable_mem_pattern = False
        opts.enable_cpu_mem_arena = False
        
        _ONNX_SESSION = ort.InferenceSession(ONNX_MODEL_PATH, opts)
        _USE_ONNX = True
        _USE_HF_API = False
        
        _ONNX_CONFIG["onnx_mode"] = "ENABLE_BASIC"
        _ONNX_CONFIG["inter_op_num_threads"] = 2
        _ONNX_CONFIG["intra_op_num_threads"] = 2
        
        logger.info("[embedder] ONNX mode: ENABLE_BASIC / threads=2")
        logger.info(f"[embedder] Modelo ONNX carregado em {time.time()-start:.2f}s (~300MB RAM)")
        return True
        
    except Exception as e:
        logger.warning(f"[embedder] ONNX nao disponivel: {e}")
        return False


def _try_load_local_model():
    """Tenta carregar modelo PyTorch local (dev - mais RAM disponivel)"""
    global _MODEL, _PREPROCESS, _DEVICE, _USE_HF_API
    
    try:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        os.environ["CUDA_HOME"] = ""
        os.environ["USE_CUDA"] = "0"
        
        import torch
        torch.set_num_threads(4)
        
        if hasattr(torch, 'set_default_device'):
            torch.set_default_device('cpu')
        
        import open_clip
        
        logger.info("[embedder] Carregando modelo OpenCLIP local (CPU)...")
        start = time.time()
        
        _DEVICE = "cpu"
        model, _, preprocess = open_clip.create_model_and_transforms(
            model_name="ViT-B-16",
            pretrained="datacomp_xl_s13b_b90k",
            device=_DEVICE
        )
        model = model.to(_DEVICE)
        model.eval()
        
        for param in model.parameters():
            param.requires_grad = False
        
        _MODEL = model
        _PREPROCESS = preprocess
        _USE_HF_API = False
        
        logger.info(f"[embedder] Modelo PyTorch carregado em {time.time()-start:.2f}s")
        return True
        
    except Exception as e:
        logger.warning(f"[embedder] Modelo PyTorch nao disponivel: {e}")
        _USE_HF_API = True
        return False


def preload_model():
    """Pre-carrega o modelo. Prioridade: ONNX (deploy) > PyTorch (dev)"""
    global _USE_HF_API
    _USE_HF_API = False
    
    # 1. Tentar ONNX (deploy no Render - memoria otimizada)
    if _try_load_onnx_model():
        logger.info("[embedder] Modo ONNX ativo (deploy)")
        return True
    
    # 2. Tentar PyTorch (desenvolvimento local - mais RAM)
    if _try_load_local_model():
        logger.info("[embedder] Modo PyTorch ativo (dev)")
        return True
    
    # 3. Nenhum modelo disponivel
    logger.warning("[embedder] Nenhum modelo disponivel")
    return True


def warmup_inference():
    """Executa uma inferencia dummy para forcar JIT compilation do ONNX Runtime.
    Elimina o delay na primeira requisicao real do usuario.
    Deve ser chamado uma unica vez no startup, apos preload_model().
    """
    global _ONNX_SESSION, _USE_ONNX
    if not (_USE_ONNX and _ONNX_SESSION is not None):
        return False
    try:
        logger.info("[STARTUP] Running warm-up inference (eliminating first-request JIT delay)...")
        start = time.time()
        # Imagem dummy 224x224 RGB (zeros normalizado)
        dummy = np.zeros((1, 3, 224, 224), dtype=np.float32)
        _ONNX_SESSION.run(None, {'image': dummy})
        elapsed = (time.time() - start) * 1000
        logger.info(f"[STARTUP] Warm-up inference complete in {elapsed:.0f}ms — first request will be fast")
        return True
    except Exception as e:
        logger.warning(f"[STARTUP] Warm-up inference failed (non-critical): {e}")
        return False


def get_image_embedding(image_bytes: bytes) -> np.ndarray:
    """Gera embedding de uma imagem a partir de bytes"""
    global _MODEL, _PREPROCESS, _USE_HF_API, _ONNX_SESSION, _USE_ONNX
    
    # Fase 2: gc.collect() removido do hot path. Manter atrás de flag para rollback.
    # Se necessário reativar, definir SOULNUTRI_FORCE_GC=1 no ambiente.
    _force_gc = os.environ.get("SOULNUTRI_FORCE_GC") == "1"
    if _force_gc:
        import gc
        gc.collect()
    
    start = time.time()
    
    # ═══ MODO ONNX (deploy) ═══
    if _USE_ONNX and _ONNX_SESSION is not None:
        try:
            from PIL import ImageEnhance, ImageOps
            global _LAST_INFERENCE_MS, _INFERENCE_COUNT, _TOTAL_INFERENCE_MS
            
            # --- t_decode: decodificar bytes -> PIL.Image ---
            t_decode_start = time.time()
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            t_decode = (time.time() - t_decode_start) * 1000
            
            # --- t_preprocess: enhance + resize + normalize (CLIP) ---
            t_preprocess_start = time.time()
            img = ImageOps.autocontrast(img, cutoff=1)
            img = ImageEnhance.Sharpness(img).enhance(1.3)
            img = ImageEnhance.Color(img).enhance(1.1)
            img_np = _preprocess_clip_numpy(img)
            del img
            t_preprocess = (time.time() - t_preprocess_start) * 1000
            
            # --- t_clip_inference: ONNX Runtime forward ---
            t_clip_start = time.time()
            result = _ONNX_SESSION.run(None, {'image': img_np})[0]
            t_clip_inference = (time.time() - t_clip_start) * 1000
            del img_np
            
            # Normalizar embedding (fora do timing de CLIP)
            embedding = result[0].astype(np.float32)
            del result
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            if _force_gc:
                import gc
                gc.collect()
            
            t_total = (time.time() - start) * 1000
            
            # --- Atualiza stats em memoria (para /api/debug/performance) ---
            _LAST_INFERENCE_MS = round(t_clip_inference, 1)
            _INFERENCE_COUNT += 1
            _TOTAL_INFERENCE_MS += t_clip_inference
            
            # --- Log estruturado unico (1 linha por request) ---
            logger.info(
                f"[TIMING] decode={t_decode:.0f}ms preprocess={t_preprocess:.0f}ms "
                f"clip={t_clip_inference:.0f}ms total={t_total:.0f}ms"
            )
            
            # --- Detector de regressao ---
            if t_clip_inference > 15000:
                logger.error("[CRITICAL] inference_timeout_risk")
            elif t_clip_inference > 5000:
                logger.warning("[ALERT] slow_inference >5s")
            
            return embedding
            
        except Exception as e:
            logger.error(f"[embedder] Erro ONNX: {e}")
            if _force_gc:
                import gc
                gc.collect()
            return None
    
    # ═══ MODO PYTORCH (dev local) ═══
    if _MODEL is not None and not _USE_HF_API:
        try:
            import torch
            from PIL import ImageEnhance, ImageOps
            
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img = ImageOps.autocontrast(img, cutoff=1)
            img = ImageEnhance.Sharpness(img).enhance(1.3)
            img = ImageEnhance.Color(img).enhance(1.1)
            
            img_tensor = _PREPROCESS(img).unsqueeze(0).to(_DEVICE)
            
            with torch.no_grad():
                embedding = _MODEL.encode_image(img_tensor)
                embedding = embedding.squeeze(0)
                norm = embedding.norm(dim=-1, keepdim=True)
                if norm.item() > 0:
                    embedding = embedding / norm
                embedding = embedding.cpu().numpy().astype(np.float32)
            
            logger.info(f"[embedder] PyTorch: {(time.time()-start)*1000:.0f}ms (img: {img.size[0]}x{img.size[1]})")
            return embedding
            
        except Exception as e:
            logger.error(f"[embedder] Erro PyTorch: {e}")
            return None
    
    # ═══ NENHUM MODELO ═══
    logger.error("[embedder] ERRO: Nenhum modelo disponivel para gerar embedding")
    return None


# Aliases para compatibilidade com index.py
def image_embedding_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Alias para get_image_embedding"""
    return get_image_embedding(image_bytes)


def image_embedding_from_path(image_path: str) -> np.ndarray:
    """Gera embedding de uma imagem a partir do caminho do arquivo"""
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return get_image_embedding(image_bytes)


def _get_embedding_via_api(image_bytes: bytes) -> np.ndarray:
    """DESABILITADO"""
    logger.error("[embedder] ERRO: API externa desabilitada")
    return None


def get_performance_stats():
    """Retorna stats em memoria para /api/debug/performance.
    
    Zero persistencia, zero MongoDB. Nao quebra se ainda nao houve scan.
    """
    avg = None
    if _INFERENCE_COUNT > 0:
        avg = round(_TOTAL_INFERENCE_MS / _INFERENCE_COUNT, 1)
    return {
        "onnx_mode": _ONNX_CONFIG.get("onnx_mode"),
        "threads": _ONNX_CONFIG.get("inter_op_num_threads"),
        "last_inference_ms": _LAST_INFERENCE_MS,
        "avg_inference_ms": avg,
        "inference_count": _INFERENCE_COUNT,
    }


def get_model_info():
    """Retorna informacoes do modelo em uso"""
    if _USE_ONNX:
        return {
            "model": "ViT-B-16 (ONNX fp16)",
            "provider": "ONNX Runtime (deploy)",
            "local": True,
            "device": "cpu"
        }
    elif _MODEL is not None:
        return {
            "model": "ViT-B-16",
            "provider": "OpenCLIP PyTorch (local)",
            "local": True,
            "device": _DEVICE
        }
    else:
        return {
            "model": "N/A",
            "provider": "Nenhum modelo carregado",
            "local": False,
            "device": "N/A"
        }
