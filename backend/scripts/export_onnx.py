"""Script de build: exporta modelo CLIP para ONNX float16"""
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

print("[BUILD] Exportando para ONNX...")
dummy = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model.visual,
    dummy,
    "/app/clip_visual_fp32.onnx",
    input_names=["image"],
    output_names=["embedding"],
    opset_version=18,
    dynamic_axes={"image": {0: "batch"}, "embedding": {0: "batch"}},
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
