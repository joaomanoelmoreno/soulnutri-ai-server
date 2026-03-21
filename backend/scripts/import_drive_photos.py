#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download de fotos do Google Drive e organização no dataset.
- Baixa todas as subpastas
- Identifica pratos pelo nome da subpasta ou do arquivo
- Evita duplicatas comparando por nome e tamanho
- Salva log detalhado
"""
import os, re, shutil, hashlib, json, time
from pathlib import Path

DRIVE_URL = "https://drive.google.com/drive/folders/17B4NVT-KMVpV82cWOeTxiFYmAOp_mwMc"
DATASET_DIR = Path("/app/datasets/organized")
TEMP_DIR = Path("/tmp/drive_full_download")
LOG_FILE = "/tmp/drive_import.log"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def file_hash(filepath):
    """Hash rápido do arquivo para detectar duplicatas."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read(8192))  # Primeiros 8KB
    return h.hexdigest()

def get_existing_hashes(dish_folder):
    """Retorna set de hashes das imagens existentes numa pasta."""
    hashes = set()
    if dish_folder.exists():
        for f in dish_folder.iterdir():
            if f.is_file() and f.suffix.lower() in IMAGE_EXT:
                hashes.add(file_hash(f))
    return hashes

def normalize_name(name):
    """Normaliza nome removendo espaços, acentos, underscore."""
    return name.lower().replace(" ", "").replace("_", "").replace("-", "").replace("(", "").replace(")", "")

def find_matching_folder(dish_name):
    """Encontra pasta do dataset que melhor corresponde ao nome."""
    norm = normalize_name(dish_name)
    
    # Map de aliases conhecidos
    ALIASES = {
        "feijoada": "Feijao do Chef",
        "feijao": "Feijao do Chef",
        "feijaodochef": "Feijao do Chef",
    }
    if norm in ALIASES:
        return ALIASES[norm]
    
    best = None
    best_score = 0
    
    for folder in DATASET_DIR.iterdir():
        if not folder.is_dir():
            continue
        fnorm = normalize_name(folder.name)
        
        if fnorm == norm:
            return folder.name
        
        # Partial match
        if norm in fnorm or fnorm in norm:
            score = min(len(norm), len(fnorm)) / max(len(norm), len(fnorm))
            if score > best_score:
                best_score = score
                best = folder.name
    
    if best and best_score > 0.5:
        return best
    return None

def process_directory(source_dir, stats):
    """Processa recursivamente um diretório de imagens baixadas."""
    source = Path(source_dir)
    
    for item in sorted(source.iterdir()):
        if item.is_dir():
            # Subpasta = nome do prato OU pasta de data
            folder_name = item.name
            
            # Verifica se é pasta de data (ex: 21032026, 2026-10-02(sub))
            is_date_folder = bool(re.match(r"^(\d{8}|\d{4}-\d{2}-\d{2})", folder_name))
            
            if is_date_folder:
                # Pasta de data: processar recursivamente
                log(f"  [DATA] {folder_name} - processando subpastas...")
                process_directory(item, stats)
            else:
                # Pasta de prato: mapear e copiar
                match = find_matching_folder(folder_name)
                if match:
                    copy_images_to_dish(item, match, stats)
                else:
                    log(f"  [SKIP] Pasta '{folder_name}' - sem correspondencia no dataset")
                    stats["unmatched"].append(folder_name)
        
        elif item.is_file() and item.suffix.lower() in IMAGE_EXT:
            # Imagem solta - tentar identificar pelo nome do arquivo
            name_without_ext = item.stem
            # Remove números, datas do nome
            clean_name = re.sub(r"\d{8}_\d{6}|\d{14}|\d+$", "", name_without_ext).strip("_- ")
            
            if clean_name and len(clean_name) > 3:
                match = find_matching_folder(clean_name)
                if match:
                    copy_single_image(item, match, stats)
                else:
                    stats["unmatched_files"].append(item.name)

def copy_images_to_dish(source_folder, dish_name, stats):
    """Copia imagens de source_folder para a pasta do prato, evitando duplicatas."""
    dest = DATASET_DIR / dish_name
    dest.mkdir(parents=True, exist_ok=True)
    
    existing_hashes = get_existing_hashes(dest)
    existing_names = {f.name.lower() for f in dest.iterdir() if f.is_file()}
    
    copied = 0
    skipped = 0
    
    for img in sorted(source_folder.iterdir()):
        if not img.is_file() or img.suffix.lower() not in IMAGE_EXT:
            if img.is_dir():
                # Sub-subpasta dentro de prato
                process_directory(img, stats)
            continue
        
        # Check duplicate by name
        if img.name.lower() in existing_names:
            skipped += 1
            continue
        
        # Check duplicate by hash
        h = file_hash(img)
        if h in existing_hashes:
            skipped += 1
            continue
        
        # Copy
        shutil.copy2(img, dest / img.name)
        existing_hashes.add(h)
        existing_names.add(img.name.lower())
        copied += 1
    
    if copied > 0:
        log(f"  [+{copied}] {dish_name} (skip: {skipped} duplicatas)")
        stats["copied"] += copied
    elif skipped > 0:
        stats["skipped"] += skipped

def copy_single_image(img_file, dish_name, stats):
    """Copia uma imagem individual para a pasta do prato."""
    dest = DATASET_DIR / dish_name
    dest.mkdir(parents=True, exist_ok=True)
    
    existing_hashes = get_existing_hashes(dest)
    existing_names = {f.name.lower() for f in dest.iterdir() if f.is_file()}
    
    if img_file.name.lower() in existing_names:
        stats["skipped"] += 1
        return
    
    h = file_hash(img_file)
    if h in existing_hashes:
        stats["skipped"] += 1
        return
    
    shutil.copy2(img_file, dest / img_file.name)
    stats["copied"] += 1

def main():
    import gdown
    
    log(f"\n{'='*60}")
    log(f"IMPORT GOOGLE DRIVE - {time.strftime('%Y-%m-%d %H:%M')}")
    log(f"{'='*60}")
    
    # Clean temp
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    TEMP_DIR.mkdir(parents=True)
    
    # Download
    log("\n1. Baixando do Google Drive...")
    try:
        files = gdown.download_folder(
            DRIVE_URL, output=str(TEMP_DIR), 
            quiet=False, use_cookies=False, remaining_ok=True
        )
        log(f"   Baixados: {len(files) if files else 0} items")
    except Exception as e:
        log(f"   ERRO no download: {e}")
        return
    
    # Process
    log("\n2. Processando imagens...")
    stats = {"copied": 0, "skipped": 0, "unmatched": [], "unmatched_files": []}
    
    # Find the actual download directory
    dl_dir = TEMP_DIR
    for item in TEMP_DIR.iterdir():
        if item.is_dir():
            dl_dir = item
            break
    
    process_directory(dl_dir, stats)
    
    # Summary
    summary = f"""
{'='*60}
RESULTADO
{'='*60}
Novas fotos copiadas: {stats['copied']}
Duplicatas ignoradas: {stats['skipped']}
Pastas sem correspondencia: {len(stats['unmatched'])}
  {', '.join(stats['unmatched'][:20]) if stats['unmatched'] else 'Nenhuma'}
Arquivos sem correspondencia: {len(stats['unmatched_files'])}
{'='*60}
"""
    log(summary)
    
    # Clean temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    
    # Save status
    with open("/tmp/drive_import_status.json", "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
