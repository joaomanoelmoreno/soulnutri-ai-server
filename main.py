cat > main.py <<'PY'
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from ai.emb_index import EmbIndex
from ai.policy import normalize_slug  # se você não tiver isso, me avise e eu ajusto


APP_NAME = "SoulNutri AI Server"

# Diretório de dados (em produção, ideal usar volume persistente)
DATA_DIR = os.getenv("DATA_DIR", "data")

app = FastAPI(title=APP_NAME)

# Índice por embeddings (carrega leve no startup; modelo é lazy)
emb_index = EmbIndex(data_dir=DATA_DIR)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/ai/status")
def ai_status():
    return {
        "ok": True,
        "service": APP_NAME,
        "mode": os.getenv("MODE", "render"),
        "data_dir": DATA_DIR,
        "embeddings_enabled": (os.getenv("SOULNUTRI_EMB_DISABLED", "").strip().lower() not in ("1", "true", "yes", "on")),
        "index_path": getattr(emb_index, "index_path", None),
        "items": len(getattr(emb_index, "items", []) or []),
        "has_matrix": getattr(emb_index, "matrix", None) is not None,
    }


@app.post("/ai/reindex")
def reindex():
    """
    Reindex por embeddings pode consumir muita RAM/CPU.
    Em Render 512Mi, recomenda-se manter SOULNUTRI_EMB_DISABLED=1
    e fazer reindex fora (local ou instância maior).
    """
    try:
        if not os.path.isdir(DATA_DIR):
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": f"DATA_DIR not found or not a directory: {DATA_DIR}"},
            )

        # percorre subpastas (cada prato = uma pasta)
        count_folders = 0
        for name in sorted(os.listdir(DATA_DIR)):
            p = os.path.join(DATA_DIR, name)
            if os.path.isdir(p):
                count_folders += 1
                emb_index.build_from_folder(p)

        return {"ok": True, "indexed_folders": count_folders, "items": len(emb_index.items)}

    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    """
    Endpoint placeholder: depende da sua lógica de match.
    Mantido aqui para não quebrar integração.
    """
    try:
        # Sem matcher aqui (porque seu projeto pode ter outra lógica).
        # Retorna apenas metadados para confirmar upload funcionando.
        content = await file.read()
        return {
            "ok": True,
            "received": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
            },
            "identified": False,
            "dish": None,
            "confidence": 0.0,
            "level": "baixa",
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
PY
