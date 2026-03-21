#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download fotos do Google Drive via curl (bypassa rate limit do gdown).
1. Usa gdown para LISTAR arquivos (fail fast OK)
2. Usa curl para BAIXAR cada arquivo
3. Converte HEIC -> JPEG
4. Copia para pasta correta, evitando duplicatas
"""
import os, re, sys, json, shutil, subprocess, hashlib, time
from pathlib import Path
from io import BytesIO

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

DATASET_DIR = Path("/app/datasets/organized")
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}
LOG_FILE = "/tmp/drive_curl_import.log"

def log(msg):
    print(msg, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def file_hash(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read(8192))
    return h.hexdigest()

def normalize(name):
    return name.lower().replace(" ", "").replace("_", "").replace("-", "").replace("(", "").replace(")", "")

ALIASES = {
    "feijoada": "Feijao do Chef",
    "feijao": "Feijao do Chef",
    "feijaodochef": "Feijao do Chef",
    "puredeabobora": "Pure de Abobora",
    "ravioli": "Ravioli",
}

def find_dish_folder(name):
    norm = normalize(name)
    if norm in ALIASES:
        return ALIASES[norm]
    for folder in DATASET_DIR.iterdir():
        if not folder.is_dir():
            continue
        if normalize(folder.name) == norm:
            return folder.name
    # Partial match
    best, best_score = None, 0
    for folder in DATASET_DIR.iterdir():
        if not folder.is_dir():
            continue
        fnorm = normalize(folder.name)
        if norm in fnorm or fnorm in norm:
            score = min(len(norm), len(fnorm)) / max(len(norm), len(fnorm))
            if score > best_score:
                best_score = score
                best = folder.name
    return best if best and best_score > 0.5 else None

def download_file(file_id, output_path):
    """Download via curl (bypassa rate limit do gdown)."""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    result = subprocess.run(
        ["curl", "-L", "-s", "-o", str(output_path), url, "--max-time", "30"],
        capture_output=True, timeout=60
    )
    return output_path.exists() and output_path.stat().st_size > 1000

def convert_heic_to_jpeg(heic_path, jpeg_path):
    """Converte HEIC para JPEG."""
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        from PIL import Image
        img = Image.open(heic_path)
        img.save(jpeg_path, "JPEG", quality=85)
        return True
    except Exception as e:
        log(f"    ERRO conversao HEIC: {e}")
        return False

def list_drive_folder(folder_url):
    """Usa gdown para listar arquivos (vai falhar no download, mas lista OK)."""
    result = subprocess.run(
        ["python3", "-c", f"""
import gdown
try:
    gdown.download_folder("{folder_url}", output="/tmp/drive_list_tmp", quiet=False, use_cookies=False, remaining_ok=True)
except:
    pass
"""],
        capture_output=True, text=True, timeout=120
    )
    
    output = result.stdout + result.stderr
    
    # Parse output
    files = []
    current_folder = "root"
    
    for line in output.split("\n"):
        fm = re.match(r"Retrieving folder (\S+) (.+)", line)
        if fm:
            current_folder = fm.group(2).strip()
        
        pm = re.match(r"Processing file (\S+) (.+)", line)
        if pm:
            fid = pm.group(1)
            fname = pm.group(2).strip()
            files.append({"id": fid, "name": fname, "folder": current_folder})
    
    # Clean temp
    shutil.rmtree("/tmp/drive_list_tmp", ignore_errors=True)
    
    return files

def process_drive_folder(folder_url):
    """Processo principal."""
    log(f"\n{'='*60}")
    log(f"IMPORT GOOGLE DRIVE - {time.strftime('%Y-%m-%d %H:%M')}")
    log(f"URL: {folder_url}")
    log(f"{'='*60}")
    
    # 1. Listar arquivos
    log("\n1. Listando arquivos no Drive...")
    files = list_drive_folder(folder_url)
    log(f"   {len(files)} arquivos encontrados")
    
    if not files:
        log("   NENHUM arquivo encontrado!")
        return
    
    # 2. Agrupar por pasta/prato
    folders = {}
    for f in files:
        folder = f["folder"]
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(f)
    
    log(f"   {len(folders)} pastas/pratos")
    
    # 3. Baixar e processar
    log("\n2. Baixando e processando...")
    stats = {"copied": 0, "skipped": 0, "failed": 0, "converted": 0, "unmatched": []}
    
    tmp_dir = Path("/tmp/drive_downloads")
    tmp_dir.mkdir(exist_ok=True)
    
    for folder_name, folder_files in sorted(folders.items()):
        # Encontrar pasta do dataset
        dish_name = find_dish_folder(folder_name)
        
        if not dish_name:
            log(f"  [?] '{folder_name}' ({len(folder_files)} fotos) - SEM CORRESPONDENCIA")
            stats["unmatched"].append({"name": folder_name, "count": len(folder_files)})
            continue
        
        dest = DATASET_DIR / dish_name
        dest.mkdir(parents=True, exist_ok=True)
        
        # Get existing hashes
        existing_hashes = set()
        existing_names = set()
        for ef in dest.iterdir():
            if ef.is_file() and ef.suffix.lower() in IMAGE_EXT | {".jpg", ".jpeg"}:
                existing_hashes.add(file_hash(ef))
                existing_names.add(ef.name.lower())
        
        copied = 0
        for finfo in folder_files:
            fname = finfo["name"]
            fid = finfo["id"]
            
            # Skip non-image files
            ext = Path(fname).suffix.lower()
            if ext not in IMAGE_EXT:
                continue
            
            # Download
            tmp_file = tmp_dir / fname
            if not download_file(fid, tmp_file):
                stats["failed"] += 1
                continue
            
            # Convert HEIC to JPEG
            if ext == ".heic":
                jpeg_name = Path(fname).stem + ".jpg"
                jpeg_path = tmp_dir / jpeg_name
                if convert_heic_to_jpeg(tmp_file, jpeg_path):
                    tmp_file.unlink()
                    tmp_file = jpeg_path
                    fname = jpeg_name
                    stats["converted"] += 1
                else:
                    tmp_file.unlink()
                    stats["failed"] += 1
                    continue
            
            # Check duplicate by name
            if fname.lower() in existing_names:
                tmp_file.unlink()
                stats["skipped"] += 1
                continue
            
            # Check duplicate by hash
            h = file_hash(tmp_file)
            if h in existing_hashes:
                tmp_file.unlink()
                stats["skipped"] += 1
                continue
            
            # Copy to dataset
            shutil.move(str(tmp_file), str(dest / fname))
            existing_hashes.add(h)
            existing_names.add(fname.lower())
            copied += 1
        
        if copied > 0:
            log(f"  [+{copied}] {dish_name}")
            stats["copied"] += copied
    
    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)
    
    # Summary
    summary = f"""
{'='*60}
RESULTADO
{'='*60}
Novas fotos copiadas: {stats['copied']}
HEIC convertidos:     {stats['converted']}
Duplicatas ignoradas: {stats['skipped']}
Falhas download:      {stats['failed']}
Sem correspondencia:  {len(stats['unmatched'])}
"""
    if stats["unmatched"]:
        summary += "  Pastas sem match:\n"
        for u in stats["unmatched"]:
            summary += f"    - {u['name']} ({u['count']} fotos)\n"
    summary += "=" * 60
    log(summary)
    
    with open("/tmp/drive_import_status.json", "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2, default=str)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://drive.google.com/drive/folders/1FIwiftKTt0nuJlU6cLY9xmD6HdyVVt8D"
    process_drive_folder(url)
