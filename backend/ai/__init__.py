# SoulNutri AI Module
# IMPORTANTE: Forçar modo CPU ANTES de qualquer import do PyTorch
# Isso evita o erro "libcublas.so not found" em ambientes sem GPU

import os

# Desabilitar CUDA completamente - ambiente de produção não tem GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["CUDA_HOME"] = ""
os.environ["TORCH_CUDA_ARCH_LIST"] = ""

# Forçar PyTorch a usar apenas CPU
os.environ["USE_CUDA"] = "0"
os.environ["FORCE_CPU"] = "1"
