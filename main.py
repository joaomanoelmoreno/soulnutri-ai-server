from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import hashlib

app = FastAPI(title="SoulNutri AI Server", version="1.1.0")

# CORS (permite o site chamar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # depois podemos travar para seu domínio
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
# UTILITÁRIOS
# =========================
def _level_from_confidence(conf: float) -> str:
    if conf >= 0.85:
        return "alta"
    if conf >= 0.50:
        return "media"
    return "baixa"


def _normalize_text(s: str) -> str:
    return (s or "").strip().lower()


def _match_dish_by_text(text: str) -> Dict[str, Any]:
    t = _normalize_text(text)

    if "strogonoff" in t:
        conf = 0.92
        return {"identified": True, "dish": "Strogonoff de Filé Mignon", "confidence": conf, "level": _level_from_confidence(conf)}

    # você pode ir adicionando outras regras simples aqui, se quiser
    conf = 0.20
    return {"identified": False, "dish": None, "confidence": conf, "level": _level_from_confidence(conf)}


def _match_dish_by_filename(filename: str) -> Dict[str, Any]:
    """
    Enquanto a IA real não estiver plugada, usamos um fallback
    para validar o pipeline por imagem (upload OK + resposta OK).
    Isso evita 'Field required' e permite testar já com suas fotos nomeadas.
    """
    f = _normalize_text(filename)

    # Regras baseadas nos seus nomes de arquivo (ex.: aboboraacurry07.jpeg, atumaogergelim02.jpeg etc.)
    if "abobora" in f and "curry" in f:
        conf = 0.86
        return {"identified": True, "dish": "Abóbora ao Curry", "confidence": conf, "level": _level_from_confidence(conf)}

    if "atum" in f and ("gergelim" in f or "sesamo" in f):
        conf = 0.86
        return {"identified": True, "dish": "Atum Selado em Crosta de Gergelim", "confidence": conf, "level": _level_from_confidence(conf)}

    if "brocolis" in f and ("parmes" in f or "parmesao" in f):
        conf = 0.80
        return {"identified": True, "dish": "Brócolis com Parmesão", "confidence": conf, "level": _level_from_confidence(conf)}

    if "umami" in f and "tomate" in f:
        conf = 0.75
        return {"identified": True, "dish": "Umami de Tomate", "confidence": conf, "level": _level_from_confidence(conf)}

    # Desconhecido
    conf = 0.20
    return {"identified": False, "dish": None, "confidence": conf, "level": _level_from_confidence(conf)}


# =========================
# ROTAS BÁSICAS
# =========================
@app.get("/")
def root():
    return {"status": "online", "service": "SoulNutri AI Server", "https": True}


@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# OCR / TEXTO
# =========================
@app.post("/ai/identify-dish")
def identify_dish(payload: IdentifyRequest):
    return _match_dish_by_text(payload.dish)


# =========================
# IMAGEM (UPLOAD MULTIPART)
# =========================
@app.post("/ai/identify-image")
async def identify_image(
    file: UploadFile = File(...),
    hint: Optional[str] = Form(None),
):
    """
    Recebe imagem via multipart/form-data com campo 'file'.
    Retorna um JSON de diagnóstico + uma identificação (stub por enquanto).

    Assim que a IA real estiver pronta, aqui será o ponto de integração.
    """
    try:
        content = await file.read()
        size = len(content)
        sha = hashlib.sha256(content).hexdigest()[:16]

        # Identificação provisória (por nome do arquivo)
        result = _match_dish_by_filename(file.filename or "")

        return {
            "ok": True,
            "received": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": size,
                "sha256_16": sha,
                "hint": hint,
            },
            **result,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
