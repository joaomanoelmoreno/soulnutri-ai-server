from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SoulNutri AI Server",
    version="1.1"
)

# CORS (libera chamadas do front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# ROOT & HEALTH
# ======================

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "SoulNutri AI Server",
        "https": True
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# ======================
# OCR / TEXTO (SECUNDÁRIO)
# ======================

@app.post("/ai/identify-dish")
def identify_dish(payload: dict):
    dish = (payload.get("dish") or "").lower()

    if "strogonoff" in dish:
        return {
            "identified": True,
            "dish": "Strogonoff de Filé Mignon",
            "confidence": 0.92,
            "level": "alta"
        }

    return {
        "identified": False,
        "confidence": 0.0,
        "level": "baixa"
    }

# ======================
# IMAGEM (MÉTODO PRINCIPAL)
# ======================

@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    """
    Endpoint principal:
    - Recebe imagem multipart
    - No momento faz mock (fase 1)
    """

    contents = await file.read()

    # Log mínimo (para debug)
    print({
        "filename": file.filename,
        "size": len(contents),
        "type": file.content_type
    })

    # ===== MOCK DE RECONHECIMENTO =====
    name = file.filename.lower()

    if "abobora" in name:
        return {
            "identified": True,
            "dish": "Abóbora ao Curry",
            "confidence": 0.85,
            "level": "alta"
        }

    if "atum" in name:
        return {
            "identified": True,
            "dish": "Atum Selado em Crosta de Gergelim",
            "confidence": 0.88,
            "level": "alta"
        }

    if "tomate" in name:
        return {
            "identified": True,
            "dish": "Umami de Tomate",
            "confidence": 0.80,
            "level": "media"
        }

    return {
        "identified": False,
        "confidence": 0.30,
        "level": "baixa"
    }
