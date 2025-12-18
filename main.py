from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SoulNutri AI Server", version="1.1")

# CORS (permite o site chamar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois travamos para soulnutri.app.br
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IdentifyRequest(BaseModel):
    dish: str


@app.get("/")
def root():
    return {"status": "online", "service": "SoulNutri AI Server", "https": True}


@app.get("/health")
def health():
    return {"status": "ok"}


# ==========================
# 1) Identificação por TEXTO
# ==========================
@app.post("/ai/identify-dish")
def identify_dish(payload: IdentifyRequest):
    dish_name = (payload.dish or "").strip().lower()

    # regra básica de teste (você já viu funcionando)
    if "strogonoff" in dish_name:
        return {
            "identified": True,
            "dish": "Strogonoff de Filé Mignon",
            "confidence": 0.92,
            "level": "alta",
            "method": "text"
        }

    # fallback
    return {
        "identified": False,
        "dish": None,
        "confidence": 0.0,
        "level": "baixa",
        "method": "text",
        "candidates": []
    }


# ==========================
# 2) Identificação por IMAGEM
#    (upload multipart)
# ==========================
@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    # Apenas para validar que o upload chegou corretamente:
    filename = (file.filename or "").lower()

    # Lê bytes para garantir que realmente veio conteúdo
    content = await file.read()
    size = len(content)

    if size == 0:
        return {
            "identified": False,
            "dish": None,
            "confidence": 0.0,
            "level": "baixa",
            "method": "image",
            "error": "Arquivo chegou vazio (0 bytes)."
        }

    # Regras temporárias por nome de arquivo (para teste de ponta a ponta)
    # Depois substituímos por IA real.
    if "abobora" in filename and "curry" in filename:
        return {
            "identified": True,
            "dish": "Abóbora ao Curry",
            "confidence": 0.86,
            "level": "alta",
            "method": "image",
            "debug": {"filename": file.filename, "bytes": size}
        }

    if "atum" in filename:
        return {
            "identified": True,
            "dish": "Atum Selado em Crosta de Gergelim",
            "confidence": 0.84,
            "level": "media",
            "method": "image",
            "debug": {"filename": file.filename, "bytes": size}
        }

    if "berinjela" in filename:
        return {
            "identified": True,
            "dish": "Berinjela ao Forno",
            "confidence": 0.80,
            "level": "media",
            "method": "image",
            "debug": {"filename": file.filename, "bytes": size}
        }

    # fallback
    return {
        "identified": False,
        "dish": None,
        "confidence": 0.0,
        "level": "baixa",
        "method": "image",
        "debug": {"filename": file.filename, "bytes": size},
        "candidates": []
    }
