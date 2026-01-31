import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

SOURCE_DIR = "/app/datasets/emergentFotosAppSoulnutri"
DEST_DIR = "/app/datasets/organized"

def normalize_dish_name(filename):
    """Extrai o nome do prato do nome do arquivo"""
    # Remove extensão
    name = os.path.splitext(filename)[0]
    
    # Remove números no final (ex: aboboraaocurry01 -> aboboraaocurry)
    name = re.sub(r'\d+$', '', name)
    
    # Remove sufixos como " - cópia"
    name = re.sub(r'\s*-\s*cópia.*$', '', name, flags=re.IGNORECASE)
    
    # Remove espaços extras e normaliza
    name = name.strip().lower()
    
    # Substitui espaços por underscore
    name = re.sub(r'\s+', '_', name)
    
    # Remove caracteres especiais exceto underscore
    name = re.sub(r'[^a-z0-9_]', '', name)
    
    return name if name else "outros"

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # Mapear arquivos para pratos
    dish_files = defaultdict(list)
    
    for filename in os.listdir(SOURCE_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            dish_name = normalize_dish_name(filename)
            dish_files[dish_name].append(filename)
    
    # Criar pastas e copiar arquivos
    total_files = 0
    for dish_name, files in sorted(dish_files.items()):
        if dish_name in ['img_', 'outros', '']:
            continue  # Ignorar arquivos não identificáveis
            
        dish_dir = os.path.join(DEST_DIR, dish_name)
        os.makedirs(dish_dir, exist_ok=True)
        
        for filename in files:
            src = os.path.join(SOURCE_DIR, filename)
            dst = os.path.join(dish_dir, filename)
            shutil.copy2(src, dst)
            total_files += 1
    
    # Estatísticas
    print(f"\n✅ Organização concluída!")
    print(f"📁 Total de pratos: {len(dish_files)}")
    print(f"📷 Total de fotos organizadas: {total_files}")
    print(f"\nPratos com mais fotos:")
    
    sorted_dishes = sorted(dish_files.items(), key=lambda x: len(x[1]), reverse=True)
    for dish, files in sorted_dishes[:20]:
        if dish not in ['img_', 'outros', '']:
            print(f"  - {dish}: {len(files)} fotos")

if __name__ == "__main__":
    main()
