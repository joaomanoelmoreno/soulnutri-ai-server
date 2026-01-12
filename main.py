from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import time

from ai.emb_index import EmbeddingIndex
from ai.hash_index import HashIndex

# =========================================================
# APP
# =========================================================
app = FastAPI(title="SoulNutri AI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# ENV
# =========================================================
DATA_DIR = os.environ.get("DATA_DIR", "data")
RECO_MODE = os.environ.get("RECO_MODE", "embeddings")

# =========================================================
# INDEXES
# =========================================================
emb_index = EmbeddingIndex(DATA_DIR)
hash_index = HashIndex(DATA_DIR)

# =========================================================
# HEALTH
# =========================================================
@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "SoulNutri AI Server",
        "ts": time.time(),
    }

# Alias padronizado (DECISÃO DEFINITIVA)
@app.get("/ai/health")
def ai_health():
    return {
        "ok": True,
        "service": "SoulNutri AI Server",
        "ts": time.time(),
    }

# =========================================================
# STATUS
# =========================================================
@app.get("/ai/status")
def ai_status():
    return {
        "ok": False,
        "error": "deprecated: use /ai/index-status",
    }

@app.get("/ai/index-status")
def index_status():
    return emb_index.status() | hash_index.status()

# =========================================================
# REINDEX
# =========================================================
@app.post("/ai/reindex")
def reindex():
    emb_index.load()
    hash_index.load()
    return {"ok": True}

# =========================================================
# IDENTIFY
# =========================================================
@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    if RECO_MODE == "embeddings":
        return emb_index.identify(image_bytes)
    else:
        return hash_index.identify(image_bytes)

# =========================================================
# CANDIDATES
# =========================================================
@app.get("/ai/candidates-status")
def candidates_status():
    return emb_index.candidates_status()

@app.get("/ai/candidates-list")
def candidates_list():
    return emb_index.candidates_list()

@app.get("/ai/candidates-download")
def candidates_download():
    return emb_index.candidates_download()

@app.post("/ai/save-capture")
async def save_capture(file: UploadFile = File(...)):
    image_bytes = await file.read()
    return emb_index.save_capture(image_bytes)
