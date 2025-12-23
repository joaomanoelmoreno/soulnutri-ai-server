import os
import io
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

# Pillow (PIL) é usado para ler imagens e calcular hash perceptual
from PIL import Image


APP_NAME = "SoulNutri AI Server"
APP_VERSION = "1.1.1"

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DATA_DIR = Path(os.getenv("SOULNUTRI_DATA_DIR", str(DEFAULT_DATA_DIR))).resolve()

VISUAL_INDEX_PATH = DATA_DIR / "visual_index.json"
HASH_INDEX_PATH = DATA_DIR / "hash_index.json"  # índice gerado por este main.py

ALLOWED_EXTS = {".jpeg", ".jpg", ".png", ".webp"}


def now_ts() -> float:
    return time.time()


def sha256_16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def safe_list_dirs(p: Path) -> List[Path]:
    if not p.exists() or not p.is_dir():
        return []
    return sorted([x for x in p.iterdir() if x.is_dir()])


def safe_list_images(p: Path) -> List[Path]:
    if not p.exists() or not p.is_dir():
        return []
    imgs = []
    for ext in ALLOWED_EXTS:
        imgs.extend(p.glob(f"*{ext}"))
        imgs.extend(p.glob(f"*{ext.upper()}"))
    return sorted(imgs)


def slug_to_title(slug: str) -> str:
    # "pudim_de_leite" -> "Pudim de Leite"
    parts = slug.replace("-", "_").split("_")
    small = {"de", "da", "do", "das", "dos", "ao", "aos", "à", "às", "e", "com", "sem"}
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
    # converte para 8x8 grayscale e compara com média -> 64 bits
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
    # 0 (igual) -> 1.0 | 64 (totalmente diferente) -> 0.0
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


def identified_from_conf(conf: float) -> bool:
    return conf >= 0.50


# -----------------------------
# Indexação (hash_index.json)
# -----------------------------
def build_hash_index(data_dir: Path) -> Dict[str, Any]:
    """
    Gera um índice simples baseado em hash perceptual das imagens.
    Estrutura:
    {
      "ok": true,
      "data_dir": "...",
      "generated_at": <ts>,
      "dishes": {
         "<slug>": {
            "title": "...",
            "images": [
               {"file": "x.jpg", "hash64": 123456789, "bytes": 12345}
            ]
         }
      }
    }
    """
    idx: Dict[str, Any] = {
        "ok": True,
        "data_dir": str(data_dir),
        "generated_at": now_ts(),
        "allowed_exts": sorted(list(ALLOWED_EXTS)),
        "dishes": {}
    }

    for dish_dir in safe_list_dirs(data_dir):
        slug = dish_dir.name
        images = safe_list_images(dish_dir)
        if not images:
            continue

        recs = []
        for fp in images:
            try:
                with fp.open("rb") as f:
                    raw = f.read()
                img = Image.open(io.BytesIO(raw))
                h = ahash64(img)
                recs.append({
                    "file": fp.name,
                    "hash64": int(h),
                    "bytes": len(raw),
                })
            except Exception:
                # Se alguma imagem estiver corrompida, apenas ignora
                continue

        if recs:
            idx["dishes"][slug] = {
                "title": slug_to_title(slug),
                "images": recs,
            }

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
    """
    Retorna (dish_slug, confidence, best_dist).
    """
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
        return None, 0.2, 999  # fallback controlado

    conf = confidence_from_dist(best_dist)
    return best_slug, conf, best_dist


# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title=APP_NAME, version=APP_VERSION)


@app.on_event("startup")
def startup_load_indexes() -> None:
    # Carrega visual_index.json (se existir) apenas para diagnóstico
    app.state.visual_index = load_json(VISUAL_INDEX_PATH)

    # Carrega hash_index.json (principal para matching)
    hash_idx = load_json(HASH_INDEX_PATH)
    if not hash_idx:
        # Se não existir, tenta gerar automaticamente (isso resolve “dish null 0.2”)
        try:
            if DATA_DIR.exists():
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
    # Mostra também contagem do índice principal (hash)
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
    }


@app.get("/ai/index-status")
def index_status():
    # Diagnóstico objetivo
    v = getattr(app.state, "visual_index", None)
    h = getattr(app.state, "hash_index", None)

    v_exists = VISUAL_INDEX_PATH.exists()
    h_exists = HASH_INDEX_PATH.exists()

    # visual_index é só informativo (não sabemos o schema antigo)
    v_size = VISUAL_INDEX_PATH.stat().st_size if v_exists else 0

    h_dishes, h_images = count_hash_index(h)

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
        "ts": now_ts(),
    }


@app.post("/ai/reindex")
def reindex():
    # Reconstrói índice baseado nas imagens em /data
    if not DATA_DIR.exists():
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": f"DATA_DIR not found: {DATA_DIR}"}
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

    received = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(raw),
        "sha256_16": sha256_16(raw),
        "hint": None,
    }

    # valida extensão (quando disponível)
    ext = (Path(file.filename).suffix or "").lower()
    if ext and ext not in ALLOWED_EXTS:
        # Não bloqueia totalmente (pois capture.jpg vem sem extensão em alguns fluxos),
        # mas registra.
        received["ext_warning"] = f"extension {ext} not in allowed {sorted(list(ALLOWED_EXTS))}"

    # Carrega imagem
    try:
        img = Image.open(io.BytesIO(raw))
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "received": received, "error": f"invalid image: {e}"}
        )

    img_hash = ahash64(img)

    hash_idx = getattr(app.state, "hash_index", None)
    if not hash_idx:
        # tenta carregar do disco
        hash_idx = load_json(HASH_INDEX_PATH)
        app.state.hash_index = hash_idx

    if not hash_idx:
        # fallback controlado (mas explicitamente sinalizado)
        return {
            "ok": True,
            "received": received,
            "identified": False,
            "dish": None,
            "confidence": 0.2,
            "level": "baixa",
            "note": "hash_index not loaded; run POST /ai/reindex",
        }

    slug, conf, dist = best_match(hash_idx, img_hash)
    title = slug_to_title(slug) if slug else None
    level = level_from_conf(conf)
    identified = identified_from_conf(conf)

    return {
        "ok": True,
        "received": received,
        "identified": identified,
        "dish": title if identified else (title if title else None),
        "dish_slug": slug,
        "confidence": conf,
        "level": level,
        "debug": {"best_dist": dist},
    }


@app.post("/ai/identify-dish")
def identify_dish(payload: Dict[str, Any]):
    """
    Endpoint auxiliar (mantido para compatibilidade).
    Exemplo payload: {"dish_slug":"pudim_de_leite"}
    """
    slug = (payload or {}).get("dish_slug")
    if not slug:
        return JSONResponse(status_code=400, content={"ok": False, "error": "dish_slug is required"})

    dish_dir = DATA_DIR / slug
    exists = dish_dir.exists() and dish_dir.is_dir()
    imgs = safe_list_images(dish_dir) if exists else []

    return {
        "ok": True,
        "dish_slug": slug,
        "dish": slug_to_title(slug),
        "exists_in_data": exists,
        "images_in_folder": len(imgs),
        "sample_images": [p.name for p in imgs[:10]],
        "ts": now_ts(),
    }
