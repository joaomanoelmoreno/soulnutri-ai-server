from fastapi import FastAPI

app = FastAPI(title="SoulNutri AI Server", version="1.0")

@app.get("/")
def root():
    return {"status": "online", "service": "SoulNutri AI Server", "https": True}

@app.get("/health")
def health():
    return {"status": "ok"}
