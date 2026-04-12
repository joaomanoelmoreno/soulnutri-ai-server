"""Script de build: exporta modelo CLIP para ONNX float32 (sem FP16)"""
import torch
import open_clip
import os

print("[BUILD] Baixando modelo ViT-B-16...")
model, _, _ = open_clip.create_model_and_transforms(
    "ViT-B-16", pretrained="datacomp_xl_s13b_b90k"
)
model.eval()

print("[BUILD] Exportando para ONNX FP32 (legacy exporter)...")
dummy = torch.randn(1, 3, 224, 224)

torch.onnx.export(
    model.visual,
    dummy,
    "/app/clip_visual_fp16.onnx",
    input_names=["image"],
    output_names=["embedding"],
    opset_version=14,
    dynamo=False,
)

size_mb = os.path.getsize("/app/clip_visual_fp16.onnx") / 1024 / 1024
print(f"[BUILD] Modelo ONNX FP32 salvo: {size_mb:.1f} MB")
