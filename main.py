from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SoulNutri AI Server", version="1.1")

# CORS liberado (ok para fase de testes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ==========================
# ENDPOINT PRINCIPAL — IMAGEM
# ==========================
@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    filename = file.filename.lower()

    # 🔹 STUB (simulação controlada)
    if "abobora" in filename:
        return {
            "identified": True,
            "dish": "Abóbora ao Curry",
            "confidence": 0.88,
            "level": "alta"
        }

    if "tomate" in filename:
        return {
            "identified": True,
            "dish": "Umami de Tomate",
            "confidence": 0.82,
            "level": "media"
        }

    return {
        "identified": False,
        "dish": None,
        "confidence": 0.0,
        "level": "baixa",
        "message": "Prato não reconhecido"
    }
