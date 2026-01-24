#!/usr/bin/env python3
"""
Script para normalizar o dataset:
1. Remover acentos e caracteres especiais dos nomes
2. Consolidar pratos duplicados
3. Atualizar dish_info.json
"""
import os
import re
import json
import shutil
from pathlib import Path
from unicodedata import normalize, category

def remove_accents(text: str) -> str:
    """Remove acentos e caracteres especiais"""
    # Normaliza para forma decomposta (NFD) e remove marcas diacríticas
    normalized = normalize('NFD', text)
    without_accents = ''.join(c for c in normalized if category(c) != 'Mn')
    return without_accents

def normalize_name(name: str) -> str:
    """Normaliza nome de prato para slug"""
    # Remove acentos
    name = remove_accents(name)
    # Converte para minúsculas
    name = name.lower()
    # Remove "unknown" prefix
    if name.startswith('unknown'):
        name = name[7:]
    # Substitui caracteres especiais por underscore
    name = re.sub(r'[^a-z0-9]+', '_', name)
    # Remove underscores duplicados e nas pontas
    name = re.sub(r'_+', '_', name).strip('_')
    return name

def get_display_name(slug: str) -> str:
    """Gera nome de exibição a partir do slug"""
    # Substitui underscores por espaços e capitaliza
    name = slug.replace('_', ' ')
    return name.title()

def consolidate_datasets(base_dir: str = "/app/datasets/organized"):
    """Consolida datasets com nomes similares"""
    base_path = Path(base_dir)
    
    # Mapear nomes normalizados para pastas originais
    normalized_map = {}  # normalized_name -> [original_folders]
    
    for folder in base_path.iterdir():
        if not folder.is_dir():
            continue
        
        original_name = folder.name
        normalized = normalize_name(original_name)
        
        if normalized not in normalized_map:
            normalized_map[normalized] = []
        normalized_map[normalized].append(original_name)
    
    print(f"📊 Total de pastas originais: {sum(len(v) for v in normalized_map.values())}")
    print(f"📊 Total de pratos únicos (após normalização): {len(normalized_map)}")
    
    # Encontrar duplicados
    duplicates = {k: v for k, v in normalized_map.items() if len(v) > 1}
    print(f"📊 Pratos com duplicados: {len(duplicates)}")
    
    if duplicates:
        print("\n🔄 Consolidando duplicados...")
        for normalized_name, folders in duplicates.items():
            print(f"\n  {normalized_name}:")
            for f in folders:
                print(f"    - {f}")
    
    # Processar cada grupo
    changes = []
    for normalized_name, folders in normalized_map.items():
        if len(folders) == 1:
            # Verificar se precisa renomear
            original = folders[0]
            if original != normalized_name:
                changes.append((original, normalized_name, 'rename'))
        else:
            # Consolidar múltiplas pastas
            primary = sorted(folders, key=lambda x: len(x))[0]  # Pega o nome mais curto
            for folder in folders:
                if folder != primary:
                    changes.append((folder, primary, 'merge'))
    
    return normalized_map, changes

def apply_changes(changes: list, base_dir: str = "/app/datasets/organized", dry_run: bool = True):
    """Aplica as mudanças (renomear/consolidar)"""
    base_path = Path(base_dir)
    
    if dry_run:
        print("\n🔍 DRY RUN - Nenhuma mudança será aplicada")
    
    stats = {'renamed': 0, 'merged': 0, 'images_moved': 0}
    
    for original, target, action in changes:
        original_path = base_path / original
        target_path = base_path / target
        
        if not original_path.exists():
            continue
        
        if action == 'rename':
            if original_path == target_path:
                continue
            
            print(f"  📝 Renomear: {original} → {target}")
            if not dry_run:
                if target_path.exists():
                    # Mesclar se já existe
                    for f in original_path.iterdir():
                        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                            dest = target_path / f.name
                            if not dest.exists():
                                shutil.copy2(f, dest)
                                stats['images_moved'] += 1
                    shutil.rmtree(original_path)
                else:
                    original_path.rename(target_path)
                stats['renamed'] += 1
                
        elif action == 'merge':
            print(f"  🔗 Mesclar: {original} → {target}")
            if not dry_run:
                if not target_path.exists():
                    target_path.mkdir(parents=True)
                
                # Copiar imagens
                for f in original_path.iterdir():
                    if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        dest = target_path / f.name
                        if not dest.exists():
                            shutil.copy2(f, dest)
                            stats['images_moved'] += 1
                
                # Remover pasta original
                shutil.rmtree(original_path)
                stats['merged'] += 1
    
    return stats

def update_dish_info_files(base_dir: str = "/app/datasets/organized"):
    """Atualiza os arquivos dish_info.json com nomes corretos"""
    base_path = Path(base_dir)
    updated = 0
    
    for folder in base_path.iterdir():
        if not folder.is_dir():
            continue
        
        info_file = folder / "dish_info.json"
        slug = folder.name
        display_name = get_display_name(slug)
        
        # Carregar ou criar info
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            except:
                info = {}
        else:
            info = {}
        
        # Atualizar campos
        info['slug'] = slug
        if 'nome' not in info or not info['nome']:
            info['nome'] = display_name
        
        # Salvar
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        updated += 1
    
    return updated

def main():
    print("=" * 60)
    print("🍽️  NORMALIZAÇÃO DO DATASET SOULNUTRI")
    print("=" * 60)
    
    # Fase 1: Análise
    print("\n📊 FASE 1: Análise do dataset...")
    normalized_map, changes = consolidate_datasets()
    
    # Mostrar resumo
    print(f"\n📋 RESUMO DAS MUDANÇAS:")
    renames = sum(1 for c in changes if c[2] == 'rename')
    merges = sum(1 for c in changes if c[2] == 'merge')
    print(f"  - Renomeações: {renames}")
    print(f"  - Mesclagens: {merges}")
    
    if not changes:
        print("  ✅ Nenhuma mudança necessária!")
    else:
        # Fase 2: Dry run
        print("\n📊 FASE 2: Simulação (dry run)...")
        apply_changes(changes, dry_run=True)
        
        # Fase 3: Aplicar
        print("\n📊 FASE 3: Aplicando mudanças...")
        stats = apply_changes(changes, dry_run=False)
        print(f"\n✅ Mudanças aplicadas:")
        print(f"  - Pastas renomeadas: {stats['renamed']}")
        print(f"  - Pastas mescladas: {stats['merged']}")
        print(f"  - Imagens movidas: {stats['images_moved']}")
    
    # Fase 4: Atualizar dish_info.json
    print("\n📊 FASE 4: Atualizando dish_info.json...")
    updated = update_dish_info_files()
    print(f"  ✅ {updated} arquivos atualizados")
    
    # Contagem final
    base_path = Path("/app/datasets/organized")
    final_count = len([d for d in base_path.iterdir() if d.is_dir()])
    print(f"\n📊 RESULTADO FINAL:")
    print(f"  - Total de pratos: {final_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
