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
# Instalar torch CPU-only (necessario para exportar modelo ONNX durante build)
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir onnx onnxscript onnxruntime && \
    grep -v -E "^(torch==|torchvision==)" backend/requirements.txt > backend/requirements-deploy.txt && \
    pip install --no-cache-dir --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ -r backend/requirements-deploy.txt

# ── Exportar modelo CLIP para ONNX float16 (feito no build, que tem mais RAM) ──
RUN python3 -c "\
import torch, open_clip, onnx, os; \
from onnxruntime.transformers import float16; \
print('[BUILD] Baixando modelo ViT-B-16...'); \
model, _, _ = open_clip.create_model_and_transforms('ViT-B-16', pretrained='datacomp_xl_s13b_b90k'); \
model.eval(); \
print('[BUILD] Exportando para ONNX...'); \
dummy = torch.randn(1, 3, 224, 224); \
torch.onnx.export(model.visual, dummy, '/app/clip_visual_fp32.onnx', \
    input_names=['image'], output_names=['embedding'], opset_version=17, \
    dynamic_axes={'image': {0: 'batch'}, 'embedding': {0: 'batch'}}); \
print('[BUILD] Convertendo para float16...'); \
m = onnx.load('/app/clip_visual_fp32.onnx', load_external_data=True); \
m16 = float16.convert_float_to_float16(m, keep_io_types=True); \
onnx.save(m16, '/app/clip_visual_fp16.onnx'); \
os.remove('/app/clip_visual_fp32.onnx'); \
for f in ['/app/clip_visual_fp32.onnx.data']: \
    os.path.exists(f) and os.remove(f); \
print(f'[BUILD] Modelo ONNX fp16 salvo: {os.path.getsize(\"/app/clip_visual_fp16.onnx\")/1024/1024:.1f} MB'); \
"

# Remover torch apos export (economiza ~1.5GB de espaco em disco no container)
RUN pip uninstall -y torch torchvision onnx onnxscript 2>/dev/null; true

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
