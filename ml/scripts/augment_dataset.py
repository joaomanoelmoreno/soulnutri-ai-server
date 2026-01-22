"""
SoulNutri - Data Augmentation para YOLOv8
Multiplica dataset existente por ~5x usando transformações clássicas
SEM uso de IA - 100% gratuito
"""

import os
import random
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import shutil

# Diretórios
SOURCE_DIR = Path("/app/datasets/organized")
OUTPUT_DIR = Path("/app/ml/datasets_augmented")

# Configurações
AUGMENTATIONS_PER_IMAGE = 4  # Gera 4 variações por imagem original
MIN_IMAGES_PER_CLASS = 5     # Classes com menos que isso são ignoradas


def augment_image(img: Image.Image, seed: int) -> Image.Image:
    """Aplica transformações aleatórias baseadas no seed"""
    random.seed(seed)
    
    # Garantir RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 1. Rotação leve (-15 a +15 graus)
    if random.random() > 0.3:
        angle = random.uniform(-15, 15)
        img = img.rotate(angle, fillcolor=(0, 0, 0), expand=False)
    
    # 2. Espelhamento horizontal (50% chance)
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    
    # 3. Ajuste de brilho (0.7 a 1.3)
    if random.random() > 0.4:
        factor = random.uniform(0.7, 1.3)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(factor)
    
    # 4. Ajuste de contraste (0.8 a 1.2)
    if random.random() > 0.4:
        factor = random.uniform(0.8, 1.2)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(factor)
    
    # 5. Ajuste de saturação (0.8 a 1.3)
    if random.random() > 0.4:
        factor = random.uniform(0.8, 1.3)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(factor)
    
    # 6. Zoom/Crop aleatório (10-20% das bordas)
    if random.random() > 0.5:
        w, h = img.size
        crop_pct = random.uniform(0.05, 0.15)
        left = int(w * crop_pct)
        top = int(h * crop_pct)
        right = int(w * (1 - crop_pct))
        bottom = int(h * (1 - crop_pct))
        img = img.crop((left, top, right, bottom))
        img = img.resize((w, h), Image.LANCZOS)
    
    # 7. Leve blur (simula foco diferente)
    if random.random() > 0.8:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.0)))
    
    return img


def process_class(class_dir: Path, output_class_dir: Path) -> dict:
    """Processa todas as imagens de uma classe"""
    
    images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.jpeg")) + list(class_dir.glob("*.png"))
    
    if len(images) < MIN_IMAGES_PER_CLASS:
        return {"skipped": True, "reason": f"apenas {len(images)} imagens"}
    
    output_class_dir.mkdir(parents=True, exist_ok=True)
    
    count_original = 0
    count_augmented = 0
    
    for img_path in images:
        try:
            img = Image.open(img_path)
            
            # Redimensionar para tamanho padrão (224x224 para YOLOv8 classificação)
            img = img.resize((224, 224), Image.LANCZOS)
            
            # Salvar original
            original_name = f"{img_path.stem}_orig.jpg"
            img.save(output_class_dir / original_name, "JPEG", quality=90)
            count_original += 1
            
            # Gerar augmentations
            for i in range(AUGMENTATIONS_PER_IMAGE):
                seed = hash(f"{img_path.name}_{i}") % (2**32)
                aug_img = augment_image(img.copy(), seed)
                aug_name = f"{img_path.stem}_aug{i+1}.jpg"
                aug_img.save(output_class_dir / aug_name, "JPEG", quality=85)
                count_augmented += 1
                
        except Exception as e:
            print(f"  ⚠️ Erro em {img_path.name}: {e}")
    
    return {
        "skipped": False,
        "original": count_original,
        "augmented": count_augmented,
        "total": count_original + count_augmented
    }


def run_augmentation():
    """Executa augmentation em todo o dataset"""
    
    print("🔄 SoulNutri Data Augmentation")
    print("=" * 50)
    print(f"Origem: {SOURCE_DIR}")
    print(f"Destino: {OUTPUT_DIR}")
    print(f"Augmentações por imagem: {AUGMENTATIONS_PER_IMAGE}")
    print("=" * 50)
    
    # Limpar diretório de saída
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    
    stats = {
        "classes_processadas": 0,
        "classes_ignoradas": 0,
        "imagens_originais": 0,
        "imagens_augmentadas": 0
    }
    
    classes = sorted([d for d in SOURCE_DIR.iterdir() if d.is_dir()])
    total_classes = len(classes)
    
    for idx, class_dir in enumerate(classes, 1):
        class_name = class_dir.name
        output_class_dir = OUTPUT_DIR / class_name
        
        result = process_class(class_dir, output_class_dir)
        
        if result["skipped"]:
            print(f"[{idx}/{total_classes}] ⏭️  {class_name}: {result['reason']}")
            stats["classes_ignoradas"] += 1
        else:
            print(f"[{idx}/{total_classes}] ✓ {class_name}: {result['original']} → {result['total']} imgs")
            stats["classes_processadas"] += 1
            stats["imagens_originais"] += result["original"]
            stats["imagens_augmentadas"] += result["augmented"]
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO FINAL")
    print("=" * 50)
    print(f"Classes processadas: {stats['classes_processadas']}")
    print(f"Classes ignoradas:   {stats['classes_ignoradas']}")
    print(f"Imagens originais:   {stats['imagens_originais']}")
    print(f"Imagens geradas:     {stats['imagens_augmentadas']}")
    print(f"TOTAL:               {stats['imagens_originais'] + stats['imagens_augmentadas']}")
    print(f"\nMultiplicador: {(stats['imagens_originais'] + stats['imagens_augmentadas']) / max(stats['imagens_originais'], 1):.1f}x")
    print(f"\n✅ Dataset salvo em: {OUTPUT_DIR}")
    
    return stats


def split_dataset(train_ratio=0.8, val_ratio=0.1):
    """Divide dataset augmentado em train/val/test"""
    
    TRAIN_DIR = OUTPUT_DIR / "train"
    VAL_DIR = OUTPUT_DIR / "val"
    TEST_DIR = OUTPUT_DIR / "test"
    
    print("\n🔀 Dividindo dataset em train/val/test...")
    
    for split_dir in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
        split_dir.mkdir(exist_ok=True)
    
    for class_dir in OUTPUT_DIR.iterdir():
        if not class_dir.is_dir() or class_dir.name in ["train", "val", "test"]:
            continue
        
        class_name = class_dir.name
        images = list(class_dir.glob("*.jpg"))
        random.shuffle(images)
        
        n_train = int(len(images) * train_ratio)
        n_val = int(len(images) * val_ratio)
        
        train_imgs = images[:n_train]
        val_imgs = images[n_train:n_train + n_val]
        test_imgs = images[n_train + n_val:]
        
        # Criar diretórios de classe
        (TRAIN_DIR / class_name).mkdir(exist_ok=True)
        (VAL_DIR / class_name).mkdir(exist_ok=True)
        (TEST_DIR / class_name).mkdir(exist_ok=True)
        
        # Mover arquivos
        for img in train_imgs:
            shutil.move(str(img), TRAIN_DIR / class_name / img.name)
        for img in val_imgs:
            shutil.move(str(img), VAL_DIR / class_name / img.name)
        for img in test_imgs:
            shutil.move(str(img), TEST_DIR / class_name / img.name)
        
        # Remover diretório de classe original (agora vazio)
        if class_dir.exists() and not any(class_dir.iterdir()):
            class_dir.rmdir()
    
    # Contar
    train_count = sum(1 for _ in TRAIN_DIR.rglob("*.jpg"))
    val_count = sum(1 for _ in VAL_DIR.rglob("*.jpg"))
    test_count = sum(1 for _ in TEST_DIR.rglob("*.jpg"))
    
    print(f"✓ Train: {train_count} imagens")
    print(f"✓ Val:   {val_count} imagens")
    print(f"✓ Test:  {test_count} imagens")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--split":
        # Apenas dividir (se augmentation já foi feita)
        split_dataset()
    else:
        # Augmentation completo + split
        stats = run_augmentation()
        if stats["classes_processadas"] > 0:
            split_dataset()
            print("\n🎉 Dataset pronto para treinamento!")
            print(f"   Caminho: {OUTPUT_DIR}")
