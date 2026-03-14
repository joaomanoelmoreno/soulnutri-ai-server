"""
SoulNutri - Serviço YOLOv8 para Identificação de Alimentos
Modelo local, rápido (~50-100ms) e gratuito
"""

import os
import logging
from pathlib import Path
from typing import Optional
from io import BytesIO

logger = logging.getLogger(__name__)

# Caminho do modelo
MODEL_PATH = Path("/app/ml/models/best.pt")
ONNX_PATH = Path("/app/ml/models/best.onnx")

# Cache do modelo carregado
_model = None
_class_names = None


def load_model():
    """Carrega o modelo YOLOv8 (lazy loading)"""
    global _model, _class_names
    
    if _model is not None:
        return _model
    
    # Verificar se modelo existe
    if not MODEL_PATH.exists() and not ONNX_PATH.exists():
        logger.warning("[YOLOv8] Modelo não encontrado. Execute o treinamento primeiro.")
        return None
    
    try:
        from ultralytics import YOLO
        
        model_file = MODEL_PATH if MODEL_PATH.exists() else ONNX_PATH
        logger.info(f"[YOLOv8] Carregando modelo: {model_file}")
        
        _model = YOLO(str(model_file))
        _class_names = _model.names
        
        logger.info(f"[YOLOv8] ✓ Modelo carregado! {len(_class_names)} classes")
        return _model
        
    except ImportError:
        logger.error("[YOLOv8] Ultralytics não instalado. Execute: pip install ultralytics")
        return None
    except Exception as e:
        logger.error(f"[YOLOv8] Erro ao carregar modelo: {e}")
        return None


def is_available() -> bool:
    """Verifica se o modelo YOLOv8 está disponível"""
    return MODEL_PATH.exists() or ONNX_PATH.exists()


async def identify_with_yolo(image_bytes: bytes) -> dict:
    """
    Identifica alimento usando YOLOv8 local.
    
    Args:
        image_bytes: Imagem em bytes
        
    Returns:
        dict com resultado da identificação
    """
    import time
    start = time.time()
    
    try:
        model = load_model()
        if model is None:
            return {
                "ok": False,
                "error": "Modelo YOLOv8 não disponível",
                "source": "yolov8"
            }
        
        # Converter bytes para imagem PIL
        from PIL import Image
        img = Image.open(BytesIO(image_bytes))
        
        # Garantir RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar para 224x224
        img = img.resize((224, 224), Image.LANCZOS)
        
        # Predição
        results = model.predict(img, verbose=False)
        
        elapsed_ms = (time.time() - start) * 1000
        
        if not results or len(results) == 0:
            return {
                "ok": True,
                "identified": False,
                "message": "Não foi possível identificar",
                "source": "yolov8",
                "search_time_ms": round(elapsed_ms, 2)
            }
        
        # Extrair probabilidades
        probs = results[0].probs
        top_idx = probs.top1
        top_conf = float(probs.top1conf)
        class_name = _class_names[top_idx]
        
        # Top 3 alternativas
        top5_idx = probs.top5[:5]
        top5_conf = probs.top5conf[:5]
        alternatives = [
            {"nome": _class_names[idx], "score": float(conf)}
            for idx, conf in zip(top5_idx[1:4], top5_conf[1:4])
        ]
        
        # Determinar confiança
        if top_conf >= 0.85:
            confidence = "alta"
        elif top_conf >= 0.60:
            confidence = "média"
        else:
            confidence = "baixa"
        
        # Formatar nome para exibição
        display_name = class_name.replace("_", " ").title()
        
        logger.info(f"[YOLOv8] ⚡ {display_name} ({top_conf:.0%}) em {elapsed_ms:.0f}ms")
        
        return {
            "ok": True,
            "identified": True,
            "dish": class_name,
            "dish_display": display_name,
            "confidence": confidence,
            "score": round(top_conf, 4),
            "source": "yolov8",
            "cascade_level": 1.5,
            "alternatives": alternatives,
            "search_time_ms": round(elapsed_ms, 2),
            # Campos para compatibilidade
            "category": None,
            "category_emoji": "🍽️",
            "ingredientes": [],
            "beneficios": [],
            "riscos": [],
            "nutrition": None
        }
        
    except Exception as e:
        elapsed_ms = (time.time() - start) * 1000
        logger.error(f"[YOLOv8] Erro: {e}")
        return {
            "ok": False,
            "error": str(e),
            "source": "yolov8",
            "search_time_ms": round(elapsed_ms, 2)
        }


def get_model_info() -> dict:
    """Retorna informações sobre o modelo"""
    if not is_available():
        return {
            "available": False,
            "message": "Modelo não encontrado. Faça upload de best.pt para /app/ml/models/"
        }
    
    model = load_model()
    if model is None:
        return {"available": False, "message": "Erro ao carregar modelo"}
    
    return {
        "available": True,
        "model_path": str(MODEL_PATH if MODEL_PATH.exists() else ONNX_PATH),
        "num_classes": len(_class_names) if _class_names else 0,
        "classes": list(_class_names.values()) if _class_names else []
    }
