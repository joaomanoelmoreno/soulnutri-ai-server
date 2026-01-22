"""
SoulNutri - Script de Preparação de Dataset para YOLOv8
Converte imagens existentes para formato de treinamento
"""

import os
import shutil
import random
from pathlib import Path

# Diretórios
SOURCE_DIR = Path("/app/datasets/organized")
OUTPUT_DIR = Path("/app/ml/datasets")
TRAIN_DIR = OUTPUT_DIR / "train"
VAL_DIR = OUTPUT_DIR / "val"
TEST_DIR = OUTPUT_DIR / "test"

# Proporções
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

def prepare_dataset():
    """Prepara dataset para treinamento YOLOv8"""
    
    # Criar diretórios
    for d in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    
    stats = {"total": 0, "classes": 0, "train": 0, "val": 0, "test": 0}
    
    # Processar cada classe (pasta)
    for class_dir in SOURCE_DIR.iterdir():
        if not class_dir.is_dir():
            continue
        
        class_name = class_dir.name
        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.jpeg")) + list(class_dir.glob("*.png"))
        
        if len(images) < 5:
            print(f"⚠️ Classe {class_name} tem poucas imagens ({len(images)}), pulando...")
            continue
        
        # Criar diretórios da classe
        (TRAIN_DIR / class_name).mkdir(exist_ok=True)
        (VAL_DIR / class_name).mkdir(exist_ok=True)
        (TEST_DIR / class_name).mkdir(exist_ok=True)
        
        # Shuffle e dividir
        random.shuffle(images)
        n_train = int(len(images) * TRAIN_RATIO)
        n_val = int(len(images) * VAL_RATIO)
        
        train_imgs = images[:n_train]
        val_imgs = images[n_train:n_train + n_val]
        test_imgs = images[n_train + n_val:]
        
        # Copiar imagens
        for img in train_imgs:
            shutil.copy(img, TRAIN_DIR / class_name / img.name)
        for img in val_imgs:
            shutil.copy(img, VAL_DIR / class_name / img.name)
        for img in test_imgs:
            shutil.copy(img, TEST_DIR / class_name / img.name)
        
        stats["total"] += len(images)
        stats["classes"] += 1
        stats["train"] += len(train_imgs)
        stats["val"] += len(val_imgs)
        stats["test"] += len(test_imgs)
        
        print(f"✓ {class_name}: {len(train_imgs)} train, {len(val_imgs)} val, {len(test_imgs)} test")
    
    print(f"\n📊 Resumo:")
    print(f"   Classes: {stats['classes']}")
    print(f"   Total imagens: {stats['total']}")
    print(f"   Train: {stats['train']} ({TRAIN_RATIO*100:.0f}%)")
    print(f"   Val: {stats['val']} ({VAL_RATIO*100:.0f}%)")
    print(f"   Test: {stats['test']} ({TEST_RATIO*100:.0f}%)")
    
    return stats


def inventory_existing():
    """Lista imagens existentes por classe"""
    print("📁 Inventário de imagens existentes:\n")
    
    total = 0
    classes = []
    
    for class_dir in sorted(SOURCE_DIR.iterdir()):
        if not class_dir.is_dir():
            continue
        
        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.jpeg")) + list(class_dir.glob("*.png"))
        count = len(images)
        total += count
        classes.append((class_dir.name, count))
    
    # Ordenar por quantidade
    classes.sort(key=lambda x: x[1], reverse=True)
    
    for name, count in classes:
        bar = "█" * min(count // 2, 20)
        status = "✓" if count >= 10 else "⚠️" if count >= 5 else "❌"
        print(f"{status} {name:30} {count:4} {bar}")
    
    print(f"\n📊 Total: {len(classes)} classes, {total} imagens")
    
    # Recomendações
    low_count = [c for c, n in classes if n < 10]
    if low_count:
        print(f"\n⚠️ Classes com poucas imagens (<10): {', '.join(low_count[:5])}...")
        print("   Recomendação: Coletar mais imagens ou usar data augmentation")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "prepare":
        prepare_dataset()
    else:
        inventory_existing()
        print("\n💡 Execute 'python prepare_dataset.py prepare' para preparar o dataset")
