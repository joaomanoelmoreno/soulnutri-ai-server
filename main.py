import os
import io
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image


APP_NAME = "SoulNutri AI Server"
APP_VERSION = "1.2.0"

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DATA_DIR = Path(os.getenv("SOULNUTRI_DATA_DIR", str(DEFAULT_DATA_DIR))).resolve()

VISUAL_INDEX_PATH = DATA_DIR / "visual_index.json"
HASH_INDEX_PATH = DATA_DIR / "hash_index.json"  # índice gerado por este main.py

ALLOWED_EXTS = {".jpeg", ".jpg", ".png", ".webp"}

# Pasta de capturas para revisão (não entra no índice)
CANDIDATES_DIRNAME = "candidates"
CANDIDATES_DIR = DATA_DIR / CANDIDATES_DIRNAME
CANDIDATES_META_PATH = CANDIDATES_DIR / "meta.jsonl"

# Limite de upload (bytes). Pode ajustar via env.
MAX_UPLOAD_BYTES = int(os.getenv("SOULNUTRI_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))  # 10MB

# Política de decisão (evita rotular errado)
IDENTIFY_MIN_CONF = float(os.getenv("SOULNUTRI_IDENTIFY_MIN_CONF", "0.85"))
IDENTIFY_MAX_DIST = int(os.getenv("SOULNUTRI_IDENTIFY_MAX_DIST", "12"))
RETURN_SUGGESTION_WHEN_NOT_IDENTIFIED = os.getenv("SOULNUTRI_RETURN_SUGGESTION", "true").lower() == "true"


def now_ts() -> float:
    return time.time()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def sha256_16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def safe_list_dirs(p: Path) -> List[Path]:
    if not p.exists() or not p.is_dir():
        return []
    return sorted([x for x in p.iterdir() if x.is_dir()])


def safe_list_images(p: Path) -> List[Path]:
    if not p.exists() or not p.is_dir():
        return []
    imgs: List[Path] = []
    for ext in ALLOWED_EXTS:
        imgs.extend(p.glob(f"*{ext}"))
        imgs.extend(p.glob(f"*{ext.upper()}"))
    return sorted(imgs)


def slug_to_title(slug: str) -> str:
    parts = slug.replace("-", "_").split("_")
    small = {"de", "da", "do", "das", "dos", "ao", "aos", "a", "e", "com", "sem"}
    out = []
    for i, w in enumerate(parts):
        if not w:
            continue
        lw = w.lower()
        if i > 0 and lw in small:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:])
    return " ".join(out)


# -----------------------------
# Hash perceptual (aHash 8x8)
# -----------------------------
def ahash64(img: Image.Image) -> int:
    g = img.convert("L").resize((8, 8))
    px = list(g.getdata())
    avg = sum(px) / 64.0
    bits = 0
    for i, v in enumerate(px):
        if v >= avg:
            bits |= (1 << i)
    return bits


def hamming64(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def confidence_from_dist(dist: int) -> float:
    c = 1.0 - (dist / 64.0)
    if c < 0:
        c = 0.0
    if c > 1:
        c = 1.0
    return float(round(c, 4))


def level_from_conf(conf: float) -> str:
    if conf >= 0.85:
        return "alta"
    if conf >= 0.50:
        return "média"
    return "baixa"


def safe_ext_from_filename(filename: str) -> str:
    ext = (Path(filename).suffix or "").lower()
    if ext in ALLOWED_EXTS:
        return ext
    return ".jpg"


# -----------------------------
# Indexação (hash_index.json)
# -----------------------------
def build_hash_index(data_dir: Path) -> Dict[str, Any]:
    idx: Dict[str, Any] = {
        "ok": True,
        "data_dir": str(data_dir),
        "generated_at": now_ts(),
        "allowed_exts": sorted(list(ALLOWED_EXTS)),
        "dishes": {},
    }

    for dish_dir in safe_list_dirs(data_dir):
        slug = dish_dir.name

        # ignora a pasta de candidatos
        if slug == CANDIDATES_DIRNAME:
            continue

        images = safe_list_images(dish_dir)
        if not images:
            continue

        recs = []
        for fp in images:
            try:
                raw = fp.read_bytes()
                img = Image.open(io.BytesIO(raw))
                h = ahash64(img)
                recs.append({"file": fp.name, "hash64": int(h), "bytes": len(raw)})
            except Exception:
                continue

        if recs:
            idx["dishes"][slug] = {"title": slug_to_title(slug), "images": recs}

    return idx


def save_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def count_hash_index(hash_idx: Optional[Dict[str, Any]]) -> Tuple[int, int]:
    if not hash_idx or "dishes" not in hash_idx:
        return (0, 0)
    dishes = hash_idx.get("dishes", {})
    dish_count = len(dishes)
    img_count = 0
    for _, v in dishes.items():
        img_count += len(v.get("images", []))
    return dish_count, img_count


def best_match(hash_idx: Dict[str, Any], img_hash: int) -> Tuple[Optional[str], float, int]:
    best_slug = None
    best_dist = 10**9

    dishes = hash_idx.get("dishes", {})
    for slug, meta in dishes.items():
        for rec in meta.get("images", []):
            h = int(rec.get("hash64", 0))
            d = hamming64(img_hash, h)
            if d < best_dist:
                best_dist = d
                best_slug = slug

    if best_slug is None:
        return None, 0.2, 999

    conf = confidence_from_dist(best_dist)
    return best_slug, conf, best_dist


# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title=APP_NAME, version=APP_VERSION)

# CORS (evita "Failed to fetch")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://soulnutri.app.br",
        "https://www.soulnutri.app.br",
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_load_indexes() -> None:
    ensure_dir(DATA_DIR)
    ensure_dir(CANDIDATES_DIR)

    app.state.visual_index = load_json(VISUAL_INDEX_PATH)

    hash_idx = load_json(HASH_INDEX_PATH)
    if not hash_idx:
        try:
            hash_idx = build_hash_index(DATA_DIR)
            save_json(HASH_INDEX_PATH, hash_idx)
        except Exception:
            hash_idx = None

    app.state.hash_index = hash_idx


@app.get("/")
def root():
    return {"ok": True, "service": APP_NAME, "version": APP_VERSION}


@app.get("/health")
def health():
    dish_count, img_count = count_hash_index(getattr(app.state, "hash_index", None))
    return {
        "ok": True,
        "service": APP_NAME,
        "version": APP_VERSION,
        "mode": "render",
        "data_dir": str(DATA_DIR),
        "hash_index_dishes": dish_count,
        "hash_index_images": img_count,
        "ts": now_ts(),
        "allowed_exts": sorted(list(ALLOWED_EXTS)),
        "max_upload_bytes": MAX_UPLOAD_BYTES,
        "policy": {
            "identify_min_conf": IDENTIFY_MIN_CONF,
            "identify_max_dist": IDENTIFY_MAX_DIST,
            "return_suggestion_when_not_identified": RETURN_SUGGESTION_WHEN_NOT_IDENTIFIED,
        },
    }


@app.get("/ai/index-status")
def index_status():
    v = getattr(app.state, "visual_index", None)
    h = getattr(app.state, "hash_index", None)

    v_exists = VISUAL_INDEX_PATH.exists()
    h_exists = HASH_INDEX_PATH.exists()
    v_size = VISUAL_INDEX_PATH.stat().st_size if v_exists else 0

    h_dishes, h_images = count_hash_index(h)

    ensure_dir(CANDIDATES_DIR)
    cand_imgs = safe_list_images(CANDIDATES_DIR)

    meta_exists = CANDIDATES_META_PATH.exists()
    meta_bytes = CANDIDATES_META_PATH.stat().st_size if meta_exists else 0

    return {
        "ok": True,
        "data_dir": str(DATA_DIR),
        "visual_index_path": str(VISUAL_INDEX_PATH),
        "visual_index_exists": v_exists,
        "visual_index_bytes": v_size,
        "visual_index_loaded": bool(v is not None),
        "hash_index_path": str(HASH_INDEX_PATH),
        "hash_index_exists": h_exists,
        "hash_index_loaded": bool(h is not None),
        "hash_index_dishes": h_dishes,
        "hash_index_images": h_images,
        "candidates_dir": str(CANDIDATES_DIR),
        "candidates_images": len(cand_imgs),
        "candidates_meta_path": str(CANDIDATES_META_PATH),
        "candidates_meta_exists": meta_exists,
        "candidates_meta_bytes": meta_bytes,
        "ts": now_ts(),
    }


@app.post("/ai/reindex")
def reindex():
    if not DATA_DIR.exists():
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": f"DATA_DIR not found: {DATA_DIR}"},
        )

    idx = build_hash_index(DATA_DIR)
    save_json(HASH_INDEX_PATH, idx)
    app.state.hash_index = idx

    d, n = count_hash_index(idx)
    return {
        "ok": True,
        "message": "hash_index rebuilt",
        "data_dir": str(DATA_DIR),
        "hash_index_path": str(HASH_INDEX_PATH),
        "dishes": d,
        "images": n,
        "ts": now_ts(),
    }


@app.post("/ai/identify-image")
async def identify_image(file: UploadFile = File(...)):
    raw = await file.read()

    if len(raw) > MAX_UPLOAD_BYTES:
        return JSONResponse(
            status_code=413,
            content={"ok": False, "error": f"file too large ({len(raw)} bytes)"},
        )

    received = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(raw),
        "sha256_16": sha256_16(raw),
        "hint": None,
    }

    try:
        img = Image.open(io.BytesIO(raw))
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "received": received, "error": f"invalid image: {e}"},
        )

    img_hash = ahash64(img)

    hash_idx = getattr(app.state, "hash_index", None)
    if not hash_idx:
        hash_idx = load_json(HASH_INDEX_PATH)
        app.state.hash_index = hash_idx

    if not hash_idx:
        return {
            "ok": True,
            "received": received,
            "identified": False,
            "dish": None,
            "dish_slug": None,
            "confidence": 0.2,
            "level": "baixa",
            "note": "hash_index not loaded; run POST /ai/reindex",
        }

    slug, conf, dist = best_match(hash_idx, img_hash)

    passes = (conf >= IDENTIFY_MIN_CONF) and (dist <= IDENTIFY_MAX_DIST)

    if passes and slug:
        return {
            "ok": True,
            "received": received,
            "identified": True,
            "dish": slug_to_title(slug),
            "dish_slug": slug,
            "confidence": conf,
            "level": level_from_conf(conf),
            "debug": {"best_dist": dist},
        }

    sug = {"suggested_slug": slug, "suggested_dish": slug_to_title(slug) if slug else None} if RETURN_SUGGESTION_WHEN_NOT_IDENTIFIED else {}

    return {
        "ok": True,
        "received": received,
        "identified": False,
        "dish": None,
        "dish_slug": None,
        "confidence": conf,
        "level": "baixa",
        "debug": {
            "best_dist": dist,
            "policy": {"min_conf": IDENTIFY_MIN_CONF, "max_dist": IDENTIFY_MAX_DIST},
            **sug,
        },
    }


@app.post("/ai/save-capture")
async def save_capture(
    file: UploadFile = File(...),
    suggested_dish_slug: Optional[str] = Form(None),
    confidence: Optional[float] = Form(None),
    level: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
):
    raw = await file.read()

    if len(raw) > MAX_UPLOAD_BYTES:
        return JSONResponse(
            status_code=413,
            content={"ok": False, "error": f"file too large ({len(raw)} bytes)"},
        )

    ensure_dir(CANDIDATES_DIR)

    ext = safe_ext_from_filename(file.filename)
    digest = sha256_16(raw)
    name = f"{utc_stamp()}_{digest}_capture{ext}"
    out_path = CANDIDATES_DIR / name

    try:
        out_path.write_bytes(raw)
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": f"write failed: {e}"})

    meta = {
        "ts": now_ts(),
        "utc": datetime.now(timezone.utc).isoformat(),
        "file": name,
        "bytes": len(raw),
        "content_type": file.content_type,
        "sha256_16": digest,
        "suggested_dish_slug": suggested_dish_slug,
        "confidence": confidence,
        "level": level,
        "source": source,
    }

    meta_saved = True
    try:
        append_jsonl(CANDIDATES_META_PATH, meta)
    except Exception:
        meta_saved = False

    return {"ok": True, "saved": True, "file": name, "path": str(out_path), "meta_saved": meta_saved}


@app.get("/ai/candidates-status")
def candidates_status():
    ensure_dir(CANDIDATES_DIR)
    imgs = safe_list_images(CANDIDATES_DIR)
    meta_exists = CANDIDATES_META_PATH.exists()
    meta_bytes = CANDIDATES_META_PATH.stat().st_size if meta_exists else 0
    return {
        "ok": True,
        "candidates_dir": str(CANDIDATES_DIR),
        "images": len(imgs),
        "meta_path": str(CANDIDATES_META_PATH),
        "meta_exists": meta_exists,
        "meta_bytes": meta_bytes,
        "ts": now_ts(),
    }


@app.get("/ai/candidates-list")
def candidates_list(limit: int = Query(50, ge=1, le=500)):
    ensure_dir(CANDIDATES_DIR)
    imgs = safe_list_images(CANDIDATES_DIR)
    imgs_sorted = sorted(imgs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]

    items = []
    for p in imgs_sorted:
        st = p.stat()
        items.append({"file": p.name, "bytes": st.st_size, "mtime": st.st_mtime})

    return {"ok": True, "count": len(items), "items": items, "ts": now_ts()}


@app.get("/ai/candidates-download")
def candidates_download(file: str = Query(..., min_length=1, max_length=200)):
    if "/" in file or "\\" in file or ".." in file:
        raise HTTPException(status_code=400, detail="invalid file")

    p = CANDIDATES_DIR / file
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="not found")

    ext = p.suffix.lower()
    media = "image/jpeg"
    if ext == ".png":
        media = "image/png"
    elif ext == ".webp":
        media = "image/webp"

    return FileResponse(path=str(p), media_type=media, filename=p.name)
