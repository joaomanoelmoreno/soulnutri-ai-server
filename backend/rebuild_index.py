#!/usr/bin/env python3
"""
SoulNutri - Script de Reconstrução do Índice CLIP
Executa em background para não bloquear o servidor.

Uso:
    python rebuild_index.py [max_per_dish]
    
Exemplo:
    python rebuild_index.py 15  # Usa até 15 imagens por prato
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configurar ambiente
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["CUDA_HOME"] = ""
os.environ["USE_CUDA"] = "0"
os.environ["FORCE_CPU"] = "1"

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar logging para arquivo
log_file = "/tmp/rebuild_index.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    max_per_dish = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    logger.info("=" * 60)
    logger.info("INICIANDO RECONSTRUÇÃO DO ÍNDICE CLIP")
    logger.info(f"Máximo de imagens por prato: {max_per_dish}")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        # Carregar embedder primeiro (carrega o modelo CLIP)
        logger.info("Carregando modelo CLIP...")
        from ai.embedder import preload_model, get_model_info
        
        preload_model()
        model_info = get_model_info()
        logger.info(f"Modelo: {model_info}")
        
        # Fazer backup do índice atual
        logger.info("Fazendo backup do índice atual...")
        from datetime import datetime
        import shutil
        
        index_file = "/app/datasets/dish_index.json"
        embeddings_file = "/app/datasets/dish_index_embeddings.npy"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.exists(index_file):
            backup_path = f"/app/datasets/dish_index_ANTES_REBUILD_{timestamp}.json"
            shutil.copy(index_file, backup_path)
            logger.info(f"Backup do índice: {backup_path}")
        
        if os.path.exists(embeddings_file):
            backup_path = f"/app/datasets/dish_index_embeddings_ANTES_REBUILD_{timestamp}.npy"
            shutil.copy(embeddings_file, backup_path)
            logger.info(f"Backup dos embeddings: {backup_path}")
        
        # Reconstruir índice
        logger.info("Iniciando reconstrução do índice...")
        from ai.index import DishIndex
        
        index = DishIndex()
        stats = index.build_index(max_per_dish=max_per_dish)
        
        elapsed = time.time() - start_time
        
        if 'error' in stats:
            logger.error(f"ERRO na reconstrução: {stats['error']}")
            return 1
        
        logger.info("=" * 60)
        logger.info("RECONSTRUÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info(f"Total de pratos: {stats['total_dishes']}")
        logger.info(f"Total de imagens: {stats['total_images']}")
        logger.info(f"Dimensão dos embeddings: {stats.get('embedding_dim', 'N/A')}")
        logger.info(f"Tempo total: {elapsed:.2f}s ({elapsed/60:.1f} minutos)")
        logger.info("=" * 60)
        
        # Salvar resultado em arquivo de status
        status_file = "/tmp/rebuild_index_status.json"
        import json
        with open(status_file, 'w') as f:
            json.dump({
                "ok": True,
                "completed_at": datetime.now().isoformat(),
                "stats": stats,
                "elapsed_seconds": elapsed
            }, f, indent=2)
        
        logger.info(f"Status salvo em: {status_file}")
        return 0
        
    except Exception as e:
        logger.error(f"ERRO FATAL: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit(main())
