"""Script de build: exporta modelo CLIP para ONNX float16 (legacy exporter)"""
import torch
import open_clip
import onnx
import os
from onnxruntime.transformers import float16

print("[BUILD] Baixando modelo ViT-B-16...")
model, _, _ = open_clip.create_model_and_transforms(
    "ViT-B-16", pretrained="datacomp_xl_s13b_b90k"
)
model.eval()

print("[BUILD] Exportando para ONNX (legacy exporter, opset 14)...")
dummy = torch.randn(1, 3, 224, 224)

# FORÇAR legacy exporter (não dynamo) - compatível com onnxruntime em qualquer CPU
torch.onnx.export(
    model.visual,
    dummy,
    "/app/clip_visual_fp32.onnx",
    input_names=["image"],
    output_names=["embedding"],
    opset_version=14,
    dynamo=False,
)

print("[BUILD] Convertendo para float16...")
m = onnx.load("/app/clip_visual_fp32.onnx", load_external_data=True)
m16 = float16.convert_float_to_float16(m, keep_io_types=True)
onnx.save(m16, "/app/clip_visual_fp16.onnx")

# Limpar arquivos temporarios
os.remove("/app/clip_visual_fp32.onnx")
data_file = "/app/clip_visual_fp32.onnx.data"
if os.path.exists(data_file):
    os.remove(data_file)

size_mb = os.path.getsize("/app/clip_visual_fp16.onnx") / 1024 / 1024
print(f"[BUILD] Modelo ONNX fp16 salvo: {size_mb:.1f} MB")
