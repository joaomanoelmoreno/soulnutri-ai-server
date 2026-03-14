#!/usr/bin/env python3
"""
Script para baixar imagens do Google Drive e organizar no dataset
"""

import os
import re
import gdown
import shutil
from pathlib import Path
from typing import List, Tuple

DRIVE_FOLDER_ID = "1iqLoWUst64FO-G4wjME00hg4Bvp1ZN4v"
DATASET_DIR = "/app/datasets/organized"
TEMP_DIR = "/tmp/drive_download"

def normalize_dish_name(filename: str) -> str:
    """
    Extrai o nome do prato do nome do arquivo.
    Ex: 'aboboraaocurry02.jpeg' -> 'aboboraaocurry'
    """
    # Remove extensão
    name = os.path.splitext(filename)[0]
    
    # Remove números no final
    name = re.sub(r'\d+$', '', name)
    
    # Remove underscores e hífens extras no final
    name = name.rstrip('_-')
    
    return name.lower()

def find_matching_folder(dish_name: str) -> str:
    """
    Encontra a pasta correspondente ao nome do prato.
    Tenta match exato primeiro, depois parcial.
    """
    # Lista todas as pastas existentes
    existing_folders = []
    for d in os.listdir(DATASET_DIR):
        if os.path.isdir(os.path.join(DATASET_DIR, d)):
            existing_folders.append(d)
    
    # Normaliza o nome do prato
    dish_normalized = dish_name.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    # 1. Match exato
    for folder in existing_folders:
        if folder.lower() == dish_name:
            return folder
    
    # 2. Match normalizado
    for folder in existing_folders:
        folder_normalized = folder.lower().replace(' ', '').replace('_', '').replace('-', '')
        if folder_normalized == dish_normalized:
            return folder
    
    # 3. Match parcial (contém)
    for folder in existing_folders:
        folder_normalized = folder.lower().replace(' ', '').replace('_', '').replace('-', '')
        if dish_normalized in folder_normalized or folder_normalized in dish_normalized:
            return folder
    
    # 4. Se não encontrou, cria uma nova pasta
    return dish_name

def download_folder(folder_id: str, output_dir: str) -> List[str]:
    """
    Baixa todos os arquivos de uma pasta do Google Drive.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    
    try:
        downloaded = gdown.download_folder(url, output=output_dir, quiet=False, use_cookies=False)
        return downloaded if downloaded else []
    except Exception as e:
        print(f"Erro ao baixar pasta: {e}")
        return []

def organize_images(source_dir: str) -> Tuple[int, int, List[str]]:
    """
    Organiza as imagens baixadas nas pastas corretas do dataset.
    Retorna: (total_processadas, total_novas, lista_de_erros)
    """
    processed = 0
    new_images = 0
    errors = []
    
    # Extensões de imagem válidas
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    
    for filename in os.listdir(source_dir):
        filepath = os.path.join(source_dir, filename)
        
        # Pula se não for arquivo ou não for imagem
        if not os.path.isfile(filepath):
            continue
        
        ext = os.path.splitext(filename)[1].lower()
        if ext not in valid_extensions:
            continue
        
        try:
            # Extrai nome do prato
            dish_name = normalize_dish_name(filename)
            
            if not dish_name:
                errors.append(f"Nome inválido: {filename}")
                continue
            
            # Encontra pasta de destino
            target_folder = find_matching_folder(dish_name)
            target_dir = os.path.join(DATASET_DIR, target_folder)
            
            # Cria pasta se não existir
            os.makedirs(target_dir, exist_ok=True)
            
            # Copia arquivo
            target_path = os.path.join(target_dir, filename)
            
            if not os.path.exists(target_path):
                shutil.copy2(filepath, target_path)
                new_images += 1
                print(f"  + {filename} -> {target_folder}/")
            else:
                print(f"  = {filename} (já existe)")
            
            processed += 1
            
        except Exception as e:
            errors.append(f"{filename}: {e}")
    
    return processed, new_images, errors

def main():
    print("=" * 60)
    print("DOWNLOAD DE IMAGENS DO GOOGLE DRIVE - SoulNutri")
    print("=" * 60)
    
    # Limpa diretório temporário
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    print(f"\n1. Baixando arquivos do Google Drive...")
    print(f"   Folder ID: {DRIVE_FOLDER_ID}")
    print(f"   Destino temporário: {TEMP_DIR}")
    
    # Baixa a pasta
    downloaded = download_folder(DRIVE_FOLDER_ID, TEMP_DIR)
    
    if not downloaded:
        print("❌ Nenhum arquivo baixado!")
        return
    
    print(f"\n2. Arquivos baixados: {len(downloaded)}")
    
    # Encontra o diretório onde os arquivos foram salvos
    # gdown cria uma subpasta com o nome da pasta do Drive
    source_dir = TEMP_DIR
    for item in os.listdir(TEMP_DIR):
        item_path = os.path.join(TEMP_DIR, item)
        if os.path.isdir(item_path):
            source_dir = item_path
            break
    
    print(f"   Diretório fonte: {source_dir}")
    
    # Lista arquivos baixados
    files = os.listdir(source_dir)
    image_files = [f for f in files if os.path.splitext(f)[1].lower() in {'.jpg', '.jpeg', '.png', '.webp'}]
    zip_files = [f for f in files if f.endswith('.zip')]
    
    print(f"   Imagens: {len(image_files)}")
    print(f"   ZIPs: {len(zip_files)}")
    
    print(f"\n3. Organizando imagens no dataset...")
    processed, new_images, errors = organize_images(source_dir)
    
    print(f"\n" + "=" * 60)
    print("RESULTADO:")
    print(f"  - Imagens processadas: {processed}")
    print(f"  - Novas imagens adicionadas: {new_images}")
    print(f"  - Erros: {len(errors)}")
    
    if errors:
        print("\nErros encontrados:")
        for err in errors[:10]:  # Mostra apenas os 10 primeiros
            print(f"  - {err}")
    
    # Limpa temporários
    print(f"\n4. Limpando arquivos temporários...")
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    
    print(f"\n✅ Download concluído!")
    print(f"   Próximo passo: executar rebuild_index.py para reindexar")
    print("=" * 60)

if __name__ == "__main__":
    main()
