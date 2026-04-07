# ══════════════════════════════════════════
# SoulNutri - Dockerfile para Render Deploy
# ══════════════════════════════════════════
FROM python:3.11-slim AS base

# Instalar Node.js para build do frontend
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g yarn && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies ──
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Frontend build ──
COPY frontend/package.json frontend/yarn.lock frontend/
WORKDIR /app/frontend
RUN yarn install --frozen-lockfile --production=false

COPY frontend/ /app/frontend/

# Build com URL vazia = paths relativos (funciona em qualquer dominio)
ENV REACT_APP_BACKEND_URL=""
RUN yarn build && test -f /app/frontend/build/index.html && echo "BUILD OK: index.html exists"

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
