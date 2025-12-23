from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import hashlib
from PIL import Image
import imagehash

# ======================================================
# CONFIGURAÇÕES
# ======================================================

DATA_DIR = "data"
SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".webp")

# Limites de confiança
CONF_HIGH = 0.85
CONF_MED = 0.50

# ======================================================
# APP
# ======================================================

app = FastAPI(
    title="SoulNutri AI Server",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # depois podemos travar no domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# UTILIDADES
# ======================================================

def sha256_16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def compute_phash(img: Image.Image):
    return imagehash.phash(img)


def load_dataset():
    """
    Lê todas as imagens em /data/<prato>/*.jpg
    Calcula o pHash e retorna uma lista indexada
    """
    dataset = []

    if not os.path.isdir(DATA_DIR):
        return dataset

    for dish in os.listdir(DATA_DIR):
        dish_path = os.path.join(DATA_DIR, dish)
        if not os.path.isdir(dish_path):
            continue

        for fname in os.listdir(dish_path):
            if not fname.lower().endswith(SUPPORTED_EXTS):
                continue

            fpath = os.path.join(dish_path, fname)
            try:
                img = Image.open(fpath).convert("RGB")
                ph = compute_phash(img)
                dataset.append({
                    "dish": dish,
                    "path": fpath,
                    "phash": ph
                })
            except Exception:
                pass

    return dataset


DATASET = load_dataset()

# ======================================================
# ENDPOINTS BÁSICOS
# ======================================================

@app.get("/")
def root():
    return {
        "service": "SoulNutri AI Server",
        "status": "online",
        "pratos": len(set(d["dish"] for d in DATASET)),
        "imagens": len(DATASET)
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ======================================================
# IDENTIFICAÇÃO POR IMAGEM
# ======================================================

@app.post("/ai/identify-image")
async def identify_image(
    file: UploadFile = File(...),
    hint: Optional[str] = Form(None)
):
    content = await file.read()
    sha = sha256_16(content)

    try:
        img = Image.open(file.file).convert("RGB")
    except Exception:
        return {
            "ok": False,
            "error": "imagem inválida"
        }

    query_hash = compute_phash(img)

    best = None
    best_dist = 999

    for item in DATASET:
        dist = query_hash - item["phash"]
        if dist < best_dist:
            best_dist = dist
            best = item

    if best is None:
        return {
            "ok": True,
            "received": {
                "filename": file.filename,
                "size": len(content),
                "sha256_16": sha,
                "hint": hint
            },
            "identified": False,
            "dish": None,
            "confidence": 0.0,
            "level": "baixa"
        }

    # Conversão simples de distância em confiança
    confidence = max(0.0, min(1.0, 1 - (best_dist / 20)))

    if confidence >= CONF_HIGH:
        level = "alta"
    elif confidence >= CONF_MED:
        level = "media"
    else:
        level = "baixa"

    return {
        "ok": True,
        "received": {
            "filename": file.filename,
            "size": len(content),
            "sha256_16": sha,
            "hint": hint
        },
        "identified": confidence >= CONF_MED,
        "dish": best["dish"],
        "confidence": round(confidence, 2),
        "level": level,
        "matched_path": best["path"],
        "dist": best_dist
    }
