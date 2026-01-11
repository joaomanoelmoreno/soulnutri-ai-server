import os
import io
import time
import json
import hashlib
import tempfile
import traceback
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image

from ai.emb_index import EmbeddingIndex
from ai.policy import confidence_level


# =========================================================
# Logging
# =========================================================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("soulnutri")


# =========================================================
# Config
# =========================================================

APP_VERSION = "1.2.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))

VISUAL_INDEX_PATH = os.path.join(DATA_DIR, "visual_index.json")
HASH_INDEX_PATH = os.path.join(DATA_DIR, "hash_index.json")

CANDIDATES_DIR = os.path.join(DATA_DIR, "candidates")
CANDIDATES_META_PATH = os.path.join(CANDIDATES_DIR, "meta.jsonl")

ALLOWED_EXTS = {".jpeg", ".jpg", ".png", ".webp"}

# Modo:
# - embeddings: usa CLIP (Servidor B)
# - hash: reservado (compatibilidade)
RECO_MODE = os.getenv("RECO_MODE", "embeddings").lower().strip()


# =========================================================
# App
# =========================================================

app = FastAPI(title="SoulNutri AI Server", version=APP_VERSION)

_emb_index: Optional[EmbeddingIndex] = None


# =========================================================
# Utils
# =========================================================

def _now_ts() -> float:
    return time.time()


def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CANDIDATES_DIR, exist_ok=True)


def _safe_ext(filename: str) -> str:
    _, ext = os.path.splitext((filename or "").lower())
    return ext


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_16(b: bytes) -> str:
    return _sha256_bytes(b)[:16]


def _read_upload_as_jpeg_bytes(file: UploadFile) -> bytes:
    """
    Normaliza qualquer upload para JPEG (para consistência).
    """
    raw = file.file.read()
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def _init_indexes_if_needed():
    """
    Carrega/instancia o índice de embeddings.

    IMPORTANTE:
    - só chamamos isso em endpoints que REALMENTE precisam do modelo/índice
      (identify e reindex), para não "puxar" peso/modelo à toa.
    """
    global _emb_index
    if _emb_index is None:
        log.info("Inicializando EmbeddingIndex (pode carregar modelo/pesos)...")
        _emb_index = EmbeddingIndex(index_path=VISUAL_INDEX_PATH)
    return _emb_index


def _dish_dirs() -> List[str]:
    """
    Retorna slugs de pratos (pastas) em data/, ignorando candidates.
    """
    if not os.path.isdir(DATA_DIR):
        return []
    out = []
    for name in os.listdir(DATA_DIR):
        p = os.path.join(DATA_DIR, name)
        if name == "candidates":
            continue
        if os.path.isdir(p):
            out.append(name)
    return sorted(out)


def _count_images_in_data() -> int:
    total = 0
    for dish in _dish_dirs():
        dish_path = os.path.join(DATA_DIR, dish)
        try:
            for f in os.listdir(dish_path):
                if _safe_ext(f) in ALLOWED_EXTS:
                    total += 1
        except Exception:
            # se alguma pasta tiver problema de permissão, não derruba tudo
            continue
    return total


def _build_hash_index_stub():
    """
    Mantém compatibilidade com a estrutura do status.
    """
    payload = {
        "ok": True,
        "mode": "stub",
        "dishes": len(_dish_dirs()),
        "images": _count_images_in_data(),
        "ts": _now_ts(),
    }
    try:
        with open(HASH_INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        # não derruba o serviço por falha de escrita do stub
        log.exception("Falha ao escrever hash_index stub")


def _append_candidate_meta(meta: Dict[str, Any]):
    os.makedirs(os.path.dirname(CANDIDATES_META_PATH), exist_ok=True)
    with open(CANDIDATES_META_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(meta, ensure_ascii=False) + "\n")


def _list_candidate_images() -> List[str]:
    """
    Lista apenas imagens reais salvas como candidates (ignora arquivos temporários).
    """
    if not os.path.isdir(CANDIDATES_DIR):
        return []
    files = []
    for f in os.listdir(CANDIDATES_DIR):
        if _safe_ext(f) in ALLOWED_EXTS and not f.startswith("tmp_"):
            files.append(f)
    return files


def _safe_write_empty_visual_index():
    """
    Fast-path: quando não existe nenhuma imagem em data/, criamos um índice visual vazio
    sem tentar processar embeddings.

    Observação: isto evita gastar CPU/RAM e, principalmente, evita que o reindex tente
    rodar pipeline pesado "à toa".
    """
    empty_payload = {
        "ok": True,
        "mode": "empty",
        "items": [],
        "ts": _now_ts(),
        "version": APP_VERSION,
    }
    try:
        os.makedirs(os.path.dirname(VISUAL_INDEX_PATH), exist_ok=True)
        with open(VISUAL_INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(empty_payload, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        log.exception("Falha ao escrever visual_index vazio")
        return False


# =========================================================
# Routes
# =========================================================

@app.get("/")
def root():
    return {"ok": True, "service": "SoulNutri AI Server", "version": APP_VERSION}


@app.get("/health")
def health():
    return {"ok": True}


# compat: você estava testando /ai/status e recebia 404
@app.get("/ai/status")
def ai_status():
    return JSONResponse(status_code=404, content={"ok": False, "error": "deprecated: use /ai/index-status"})


@app.get("/ai/index-status")
def index_status():
    """
    IMPORTANTE: NÃO inicializa EmbeddingIndex aqui.
    Esse endpoint deve ser "leve" e não pode puxar modelo/pesos.
    """
    _ensure_dirs()

    visual_exists = os.path.exists(VISUAL_INDEX_PATH)
    visual_bytes = os.path.getsize(VISUAL_INDEX_PATH) if visual_exists else 0

    hash_exists = os.path.exists(HASH_INDEX_PATH)
    hash_loaded = False
    hash_dishes = 0
    hash_images = 0
    if hash_exists:
        try:
            with open(HASH_INDEX_PATH, "r", encoding="utf-8") as f:
                hj = json.load(f)
            hash_loaded = True
            hash_dishes = int(hj.get("dishes", 0))
            hash_images = int(hj.get("images", 0))
        except Exception:
            pass

    candidates_images = len(_list_candidate_images())
    meta_exists = os.path.exists(CANDIDATES_META_PATH)
    meta_bytes = os.path.getsize(CANDIDATES_META_PATH) if meta_exists else 0

    return {
        "ok": True,
        "data_dir": DATA_DIR,
        "visual_index_path": VISUAL_INDEX_PATH,
        "visual_index_exists": visual_exists,
        "visual_index_bytes": visual_bytes,
        # "loaded" aqui significa apenas: o app já inicializou o objeto em memória
        "visual_index_loaded": bool(_emb_index is not None),
        "hash_index_path": HASH_INDEX_PATH,
        "hash_index_exists": hash_exists,
        "hash_index_loaded": hash_loaded,
        "hash_index_dishes": hash_dishes,
        "hash_index_images": hash_images,
        "candidates_dir": CANDIDATES_DIR,
        "candidates_images": candidates_images,
        "candidates_meta_path": CANDIDATES_META_PATH,
        "candidates_meta_exists": meta_exists,
        "candidates_meta_bytes": meta_bytes,
        "ts": _now_ts(),
    }


@app.post("/ai/reindex")
def reindex():
    """
    Reconstrói o índice visual (embeddings) usando apenas data/<dish>/*.jpg
    (ignora data/candidates)

    BLINDAGEM:
    - fast-path quando não há imagens
    - try/except para não derrubar o processo por exceção Python
    - logs úteis para Render
    """
    _ensure_dirs()
    _build_hash_index_stub()

    try:
        total_images = _count_images_in_data()
        total_dishes = len(_dish_dirs())

        log.info(f"REINDEX start | dishes={total_dishes} | images={total_images} | data_dir={DATA_DIR}")

        # FAST PATH: sem imagens -> não roda pipeline pesado
        if total_images == 0:
            ok_empty = _safe_write_empty_visual_index()
            log.info(f"REINDEX fast-path (no images) | wrote_empty_visual={ok_empty}")
            return {
                "ok": True,
                "mode": RECO_MODE,
                "fast_path": True,
                "reason": "no_images_in_data_dir",
                "visual_index_path": VISUAL_INDEX_PATH,
                "visual_index_images": 0,
                "dishes": total_dishes,
                "images": 0,
                "ts": _now_ts(),
            }

        emb = _init_indexes_if_needed()

        # rebuild limpo
        emb.items = []
        emb.matrix = None

        # Blindagem: indexa apenas pastas de prato
        for dish in _dish_dirs():
            dish_path = os.path.join(DATA_DIR, dish)
            log.info(f"REINDEX dish={dish} path={dish_path}")
            emb.build_from_folder(dish_path)

        log.info(f"REINDEX done | indexed_images={len(getattr(emb, 'items', []) or [])}")

        return {
            "ok": True,
            "mode": RECO_MODE,
            "fast_path": False,
            "visual_index_path": VISUAL_INDEX_PATH,
            "visual_index_images": len(emb.items) if getattr(emb, "items", None) is not None else 0,
            "dishes": total_dishes,
            "images": total_images,
            "ts": _now_ts(),
        }

    except Exception as e:
        # Isso impede 502 por exceção Python não tratada (quando NÃO é OOM/SIGKILL)
        tb = traceback.format_exc()
        log.error(f"REINDEX error: {e}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": str(e),
                "where": "reindex",
                "ts": _now_ts(),
            },
        )


@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    """
    Identifica imagem por embeddings (Servidor B).
    """
    _ensure_dirs()
    emb = _init_indexes_if_needed()

    ext = _safe_ext(file.filename or "upload.jpg")
    if ext not in ALLOWED_EXTS:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": f"Extensão não suportada: {ext}", "allowed_exts": sorted(ALLOWED_EXTS)},
        )

    jpeg_bytes = _read_upload_as_jpeg_bytes(file)
    sha16 = _sha256_16(jpeg_bytes)

    request_id = f"{int(_now_ts())}_{sha16}"

    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(prefix=f"soulnutri_{sha16}_", suffix=".jpg")
        os.close(fd)
        with open(tmp_path, "wb") as f:
            f.write(jpeg_bytes)

        results = emb.search(tmp_path, top_k=5)

    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    if not results:
        return {
            "ok": True,
            "request_id": request_id,
            "received": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(jpeg_bytes),
                "sha256_16": sha16,
            },
            "identified": False,
            "dish": None,
            "suggested_dish": None,
            "confidence": 0.0,
            "level": "baixa",
            "matches": [],
        }

    best_dish, best_score = results[0]
    level = confidence_level(float(best_score))
    identified = (level == "alta")

    return {
        "ok": True,
        "request_id": request_id,
        "received": {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(jpeg_bytes),
            "sha256_16": sha16,
        },
        "identified": identified,
        "dish": best_dish if identified else None,
        "suggested_dish": best_dish,
        "confidence": float(best_score),
        "level": level,
        "matches": [{"dish": d, "score": float(s), "level": confidence_level(float(s))} for d, s in results],
    }


@app.post("/ai/save-capture")
async def save_capture(
    file: UploadFile = File(...),
    suggested_dish_slug: Optional[str] = Form(None),
    confidence: Optional[float] = Form(None),
    level: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
):
    """
    Salva uma captura do cliente em data/candidates/
    e registra meta.jsonl (append).
    """
    _ensure_dirs()

    ext = _safe_ext(file.filename or "capture.jpg")
    if ext not in ALLOWED_EXTS:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": f"Extensão não suportada: {ext}", "allowed_exts": sorted(ALLOWED_EXTS)},
        )

    jpeg_bytes = _read_upload_as_jpeg_bytes(file)
    sha16 = _sha256_16(jpeg_bytes)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fname = f"{ts}_{sha16}_capture.jpg"
    out_path = os.path.join(CANDIDATES_DIR, fname)

    with open(out_path, "wb") as f:
        f.write(jpeg_bytes)

    meta = {
        "file": fname,
        "bytes": len(jpeg_bytes),
        "sha256_16": sha16,
        "ts": ts,
        "suggested_dish_slug": suggested_dish_slug,
        "confidence": float(confidence) if confidence is not None else None,
        "level": level,
        "source": source,
        "orig_filename": file.filename,
        "content_type": file.content_type,
        "saved_path": out_path,
    }
    _append_candidate_meta(meta)

    return {"ok": True, "saved": meta}


@app.get("/ai/candidates-status")
def candidates_status():
    _ensure_dirs()
    imgs = _list_candidate_images()

    return {
        "ok": True,
        "candidates_dir": CANDIDATES_DIR,
        "count": len(imgs),
        "meta_path": CANDIDATES_META_PATH,
        "meta_exists": os.path.exists(CANDIDATES_META_PATH),
        "ts": _now_ts(),
    }


@app.get("/ai/candidates-list")
def candidates_list(limit: int = Query(50, ge=1, le=500)):
    _ensure_dirs()

    items = []
    files = _list_candidate_images()
    files_sorted = sorted(
        files,
        key=lambda fn: os.path.getmtime(os.path.join(CANDIDATES_DIR, fn)),
        reverse=True,
    )

    for fn in files_sorted[:limit]:
        p = os.path.join(CANDIDATES_DIR, fn)
        items.append({"file": fn, "bytes": os.path.getsize(p), "mtime": os.path.getmtime(p)})

    return {"ok": True, "count": len(items), "items": items, "ts": _now_ts()}


@app.get("/ai/candidates-download")
def candidates_download(file: str = Query(..., min_length=1, max_length=200)):
    _ensure_dirs()

    file = os.path.basename(file)
    p = os.path.join(CANDIDATES_DIR, file)
    if not os.path.exists(p):
        return JSONResponse(status_code=404, content={"ok": False, "error": "Arquivo não encontrado"})

    return FileResponse(p, media_type="image/jpeg", filename=file)
