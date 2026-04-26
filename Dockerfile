# ══════════════════════════════════════════
# SoulNutri - Dockerfile para Render Deploy
# ══════════════════════════════════════════
FROM python:3.11-slim AS base

# Instalar Node.js para build do frontend
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ffmpeg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g yarn && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies (SEM torch - modelo vem pronto do R2) ──
COPY backend/requirements.txt backend/requirements.txt
RUN grep -v -E "^(torch==|torchvision==)" backend/requirements.txt > backend/requirements-deploy.txt && \
    pip install --no-cache-dir onnxruntime && \
    pip install --no-cache-dir --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ -r backend/requirements-deploy.txt

# ── Baixar modelo CLIP ONNX pre-compilado do R2 (testado e funcionando) ──
RUN pip install --no-cache-dir boto3 && \
    python3 -c "import boto3,os; \
    r2=boto3.client('s3',endpoint_url='https://2723f210eede7a83470abe72ffeaeecb.r2.cloudflarestorage.com', \
    aws_access_key_id='a5a02bd055dfda49dd119c3306473172', \
    aws_secret_access_key='d17b5049f0a518523c00f94fdf229a0528da00eae287a5797739ac1d4aab1314', \
    region_name='auto'); \
    r2.download_file('soulnutri-images','models/clip_visual_fp16.onnx','/app/clip_visual_fp16.onnx'); \
    print(f'Modelo baixado: {os.path.getsize(\"/app/clip_visual_fp16.onnx\")/1024/1024:.1f} MB')"

# ── Frontend build ──
RUN echo "Frontend cache bust v3 - 2026-04-26-late"
COPY frontend/package.json frontend/yarn.lock frontend/
WORKDIR /app/frontend
RUN yarn install --frozen-lockfile --production=false

COPY frontend/ /app/frontend/

# Build com URL vazia = paths relativos (funciona em qualquer dominio)
ENV REACT_APP_BACKEND_URL=""
RUN echo "Cache bust v2 - 2026-04-26" && yarn build && test -f /app/frontend/build/index.html && echo "BUILD OK: index.html exists"

# ── Backend + Datasets ──
WORKDIR /app
COPY backend/ backend/

# Apenas os arquivos de indice (NAO inclui organized/ que tem 3.3GB)
COPY datasets/dish_index.json datasets/dish_index.json
COPY datasets/dish_index_embeddings.npy datasets/dish_index_embeddings.npy
COPY datasets/descriptions.json datasets/descriptions.json
COPY datasets/dish_name_mapping.json datasets/dish_name_mapping.json

# Render usa $PORT (default 8001)
EXPOSE 8001

# Garantir que Python encontre os modulos locais (ai/, services/, etc.)
ENV PYTHONPATH=/app/backend

# Iniciar a partir do diretorio backend (mesmo que dev)
WORKDIR /app/backend
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1
