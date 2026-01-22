#!/usr/bin/env python3
"""
SoulNutri - Treinamento YOLOv8 em Background
Executa automaticamente no servidor da Emergent
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
log_file = "/app/ml/training.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def train():
    logger.info("=" * 50)
    logger.info("🚀 INICIANDO TREINAMENTO YOLOV8")
    logger.info("=" * 50)
    
    try:
        from ultralytics import YOLO
        
        # Caminhos
        dataset_path = "/app/ml/datasets_augmented"
        output_dir = "/app/ml/models"
        os.makedirs(output_dir, exist_ok=True)
        
        # Verificar dataset
        train_path = os.path.join(dataset_path, "train")
        if not os.path.exists(train_path):
            logger.error(f"❌ Dataset não encontrado em {train_path}")
            return False
        
        # Contar classes
        classes = [d for d in os.listdir(train_path) if os.path.isdir(os.path.join(train_path, d))]
        logger.info(f"📊 Dataset: {len(classes)} classes")
        
        # Carregar modelo pré-treinado
        logger.info("📦 Carregando modelo base YOLOv8n...")
        model = YOLO('yolov8n-cls.pt')
        
        # Treinar (CPU - mais lento mas funciona)
        logger.info("🏋️ Iniciando treinamento (CPU)...")
        logger.info("⏳ Isso vai levar algumas horas. Relaxe!")
        
        results = model.train(
            data=dataset_path,
            epochs=50,           # Reduzido para CPU
            imgsz=224,
            batch=16,            # Menor batch para CPU
            patience=15,
            device='cpu',
            workers=2,
            project='/app/ml',
            name='soulnutri_model',
            exist_ok=True,
            pretrained=True,
            optimizer='AdamW',
            lr0=0.001,
            verbose=True
        )
        
        # Copiar melhor modelo para local padrão
        best_model_src = "/app/ml/soulnutri_model/weights/best.pt"
        best_model_dst = "/app/ml/models/best.pt"
        
        if os.path.exists(best_model_src):
            import shutil
            shutil.copy(best_model_src, best_model_dst)
            logger.info(f"✅ Modelo salvo em: {best_model_dst}")
            
            # Testar modelo
            logger.info("🧪 Testando modelo...")
            test_model = YOLO(best_model_dst)
            metrics = test_model.val()
            logger.info(f"📊 Acurácia Top-1: {metrics.top1:.2%}")
            logger.info(f"📊 Acurácia Top-5: {metrics.top5:.2%}")
        
        logger.info("=" * 50)
        logger.info("🎉 TREINAMENTO CONCLUÍDO!")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no treinamento: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    train()
