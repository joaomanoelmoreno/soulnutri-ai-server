#!/usr/bin/env python3
"""
Script para organizar imagens extraídas nas pastas corretas do dataset
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

SOURCE_DIR = "/tmp/drive_zip/extracted3/2025-20-12"
DATASET_DIR = "/app/datasets/organized"

def normalize_dish_name(filename: str) -> str:
    """
    Extrai o nome do prato do nome do arquivo.
    Ex: 'aboboraaocurry02.jpeg' -> 'aboboraaocurry'
    """
    # Remove extensão
    name = os.path.splitext(filename)[0]
    
    # Remove números no final
    name = re.sub(r'[0-9]+$', '', name)
    
    # Remove underscores e hífens extras no final
    name = name.rstrip('_- ')
    
    return name.lower()

def find_best_matching_folder(dish_name: str, existing_folders: list) -> str:
    """
    Encontra a pasta correspondente ao nome do prato.
    """
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
    
    # 4. Se não encontrou, usa o nome normalizado
    return dish_name

def main():
    print("=" * 60)
    print("ORGANIZANDO IMAGENS NO DATASET")
    print("=" * 60)
    
    # Lista pastas existentes
    existing_folders = []
    for d in os.listdir(DATASET_DIR):
        if os.path.isdir(os.path.join(DATASET_DIR, d)):
            existing_folders.append(d)
    
    print(f"Pastas existentes: {len(existing_folders)}")
    
    # Extensões válidas
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # Contadores
    processed = 0
    new_images = 0
    skipped = 0
    dish_counts = defaultdict(int)
    
    # Lista arquivos
    files = os.listdir(SOURCE_DIR)
    image_files = [f for f in files if os.path.splitext(f)[1].lower() in valid_extensions]
    
    print(f"Imagens para processar: {len(image_files)}")
    print("-" * 60)
    
    for filename in sorted(image_files):
        filepath = os.path.join(SOURCE_DIR, filename)
        
        try:
            # Extrai nome do prato
            dish_name = normalize_dish_name(filename)
            
            if not dish_name or dish_name == 'img_':
                skipped += 1
                continue
            
            # Encontra pasta de destino
            target_folder = find_best_matching_folder(dish_name, existing_folders)
            target_dir = os.path.join(DATASET_DIR, target_folder)
            
            # Cria pasta se não existir
            os.makedirs(target_dir, exist_ok=True)
            
            # Adiciona à lista de pastas se for nova
            if target_folder not in existing_folders:
                existing_folders.append(target_folder)
            
            # Copia arquivo
            target_path = os.path.join(target_dir, filename)
            
            if not os.path.exists(target_path):
                shutil.copy2(filepath, target_path)
                new_images += 1
                dish_counts[target_folder] += 1
            else:
                skipped += 1
            
            processed += 1
            
            # Progress
            if processed % 500 == 0:
                print(f"  Processadas: {processed} ({new_images} novas)")
                
        except Exception as e:
            print(f"  Erro em {filename}: {e}")
    
    print("-" * 60)
    print("RESULTADO:")
    print(f"  - Total processadas: {processed}")
    print(f"  - Novas imagens adicionadas: {new_images}")
    print(f"  - Já existentes (ignoradas): {skipped}")
    print(f"  - Pratos atualizados: {len(dish_counts)}")
    
    print("\nPratos com mais imagens novas:")
    sorted_dishes = sorted(dish_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    for dish, count in sorted_dishes:
        print(f"  - {dish}: +{count}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
