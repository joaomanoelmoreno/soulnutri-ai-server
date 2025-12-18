from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="SoulNutri AI Server",
    version="1.1"
)

# =========================
# CORS (libera chamadas do site)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois podemos travar no domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELOS
# =========================
class IdentifyRequest(BaseModel):
    dish: str

# =========================
# ROTAS BÁSICAS
# =========================
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

# =========================
# IDENTIFICAÇÃO POR TEXTO (OCR / nome)
# =========================
@app.post("/ai/identify-dish")
def identify_dish(payload: IdentifyRequest):
    dish_name = (payload.dish or "").strip().lower()

    if "strogonoff" in dish_name:
        return {
            "identified": True,
            "dish": "Strogonoff de Filé Mignon",
            "confidence": 0.92,
            "level": "alta"
        }

    if "arroz" in dish_name:
        return {
            "identified": True,
            "dish": "Arroz Integral",
            "confidence": 0.75,
            "level": "media"
        }

    return {
        "identified": False,
        "dish": None,
        "confidence": 0.0,
        "level": "baixa"
    }

# =========================
# IDENTIFICAÇÃO POR IMAGEM (PRINCIPAL)
# =========================
@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()

    # Simulação inicial baseada no nome do arquivo
    # (etapa seguinte será IA real por imagem)
    if "brocolis" in filename:
        return {
            "identified": True,
            "dish": "Brócolis com Parmesão",
            "confidence": 0.82,
            "level": "media"
        }

    if "strogonoff" in filename:
        return {
            "identified": True,
            "dish": "Strogonoff de Filé Mignon",
            "confidence": 0.90,
            "level": "alta"
        }

    if "berinjela" in filename:
        return {
            "identified": True,
            "dish": "Berinjela ao Forno",
            "confidence": 0.78,
            "level": "media"
        }

    # Caso não reconheça
    return {
        "identified": False,
        "dish": None,
        "confidence": 0.0,
        "level": "baixa"
    }

