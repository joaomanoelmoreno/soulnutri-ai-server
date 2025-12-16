from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

app = FastAPI(title="SoulNutri AI Server", version="1.0.0")

# CORS (libera o front do seu domínio chamar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois a gente restringe para seus domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "IA online e respondendo"}

@app.post("/api/recognize")
async def recognize(image: UploadFile = File(...)):
    # valida se é uma imagem de verdade (básico, mas evita lixo)
    content = await image.read()
    try:
        Image.open(io.BytesIO(content)).verify()
    except Exception:
        return {"status": "error", "message": "Arquivo enviado não parece ser uma imagem válida."}

    # Stub por enquanto (depois ligamos no seu matcher)
    return {"status": "ok", "recognized": None, "confidence": 0.0}
