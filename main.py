from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SoulNutri AI Server", version="1.0")

# CORS (permite o site chamar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # depois podemos travar para seu domínio
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

    return {
        "identified": False,
        "possible_dishes": [
            "Carne ao molho",
            "Molho cremoso com carne",
            "Estrogonofe genérico"
        ],
        "confidence": 0.45,
        "level": "baixa",
        "warning": "Confirme ingredientes. Pode conter lactose."
    }
