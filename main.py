import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

APP_NAME = "SoulNutri AI Server"

# Render costuma passar PORT no start command; DATA_DIR pode ser ajustado por env
DATA_DIR = os.getenv("DATA_DIR", "data")

app = FastAPI(title=APP_NAME)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/ai/status")
def ai_status():
    """
    Status leve e seguro para Render (512Mi).
    Não carrega modelo pesado aqui.
    """
    disabled = os.getenv("SOULNUTRI_EMB_DISABLED", "").strip().lower() in ("1", "true", "yes", "on")

    # Tentativa segura de verificar se EmbIndex existe sem derrubar o server
    emb_ok = False
    try:
        from ai.emb_index import EmbIndex  # noqa: F401
        emb_ok = True
    except Exception:
        emb_ok = False

    return {
        "ok": True,
        "service": APP_NAME,
        "mode": os.getenv("MODE", "render"),
        "data_dir": DATA_DIR,
        "embeddings_disabled": disabled,
        "emb_module_import_ok": emb_ok,
    }


@app.post("/ai/reindex")
def reindex():
    """
    Reindex pode consumir RAM/CPU. No Render 512Mi, mantenha embeddings desabilitados.
    """
    disabled = os.getenv("SOULNUTRI_EMB_DISABLED", "").strip().lower() in ("1", "true", "yes", "on")
    if disabled:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "Embeddings desabilitados (SOULNUTRI_EMB_DISABLED=1). Reindex deve rodar fora do Render 512Mi."},
        )

    try:
        from ai.emb_index import EmbIndex

        if not os.path.isdir(DATA_DIR):
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": f"DATA_DIR not found or not a directory: {DATA_DIR}"},
            )

        emb_index = EmbIndex(data_dir=DATA_DIR)

        count_folders = 0
        for name in sorted(os.listdir(DATA_DIR)):
            p = os.path.join(DATA_DIR, name)
            if os.path.isdir(p):
                count_folders += 1
                emb_index.build_from_folder(p)

        items = getattr(emb_index, "items", None)
        return {"ok": True, "indexed_folders": count_folders, "items": len(items) if items else 0}

    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    """
    Endpoint mínimo para manter o serviço vivo e testável.
    (Reconhecimento completo a gente liga depois, com RAM adequada ou pipeline separado.)
    """
    try:
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
