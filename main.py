from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SoulNutri AI Server", version="1.1")

# CORS (libera chamadas do front)
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

# ✅ ENDPOINT CORRETO PARA IMAGEM
@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "status": "received"
    }
