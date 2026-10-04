# syntax=docker/dockerfile:1

# ══════════════════════════════════════════
# SoulNutri - Dockerfile para Render Deploy
# ══════════════════════════════════════════
FROM python:3.11-slim AS base

# Instalar Node.js para build do frontend
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ffmpeg libgomp1 && \
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

# ── Baixar e validar o modelo CLIP ONNX sem persistir credenciais ──
RUN --mount=type=secret,id=r2_model_credentials_json,dst=/run/secrets/r2_model_credentials.json,required=true \
    pip install --no-cache-dir boto3 && \
    python3 - <<'PY'
import hashlib
import json
import sys

import boto3

MODEL_PATH = "/app/clip_visual_fp16.onnx"
EXPECTED_SHA256 = "8a97817ddd9947f9e1ddc43c85e7c6d0c65c55d9c7f47b81bf20e265a0fcd0da"

try:
    with open("/run/secrets/r2_model_credentials.json", encoding="utf-8") as handle:
        credentials = json.load(handle)

    required_fields = ("endpoint_url", "access_key_id", "secret_access_key")
    if any(
        not isinstance(credentials.get(field), str) or not credentials[field].strip()
        for field in required_fields
    ):
        raise RuntimeError

    r2 = boto3.client(
        "s3",
        endpoint_url=credentials["endpoint_url"].strip(),
        aws_access_key_id=credentials["access_key_id"].strip(),
        aws_secret_access_key=credentials["secret_access_key"].strip(),
        region_name="auto",
    )
    r2.download_file(
        "soulnutri-images",
        "models/clip_visual_fp16.onnx",
        MODEL_PATH,
    )

    with open(MODEL_PATH, "rb") as model_file:
        actual_sha256 = hashlib.file_digest(model_file, "sha256").hexdigest()

    if actual_sha256 != EXPECTED_SHA256:
        raise RuntimeError
except Exception:
    print("[BUILD FAIL] Modelo ONNX indisponivel ou invalido", file=sys.stderr)
    raise SystemExit(1)

print("[ONNX VALIDATE] SHA-256 confirmado")
PY

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
