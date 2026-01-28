# 🍽️ SoulNutri - Guia de Treinamento YOLOv8

## Para Iniciantes - Passo a Passo

---

## 📥 PASSO 1: Baixar os Arquivos

### Opção A: Pelo Preview (mais fácil)
1. Acesse: https://soulnutri-1.preview.emergentagent.com
2. Os arquivos estão no servidor, peça ao agente para disponibilizar um link de download

### Opção B: Pela Emergent Platform
1. Acesse seu projeto na Emergent
2. Clique em "Download Code" ou "Save to GitHub"
3. Os arquivos estarão em `/app/ml/`:
   - `dataset.zip` (148 MB) - as imagens
   - `SoulNutri_YOLOv8_Training.ipynb` - o notebook

---

## 🌐 PASSO 2: Abrir o Google Colab

1. Acesse: **https://colab.research.google.com**
2. Faça login com sua conta Google (é grátis)
3. Clique em **Arquivo → Upload notebook**
4. Selecione o arquivo `SoulNutri_YOLOv8_Training.ipynb`

---

## ⚡ PASSO 3: Configurar GPU Gratuita

1. No menu, clique em **Runtime** (ou "Ambiente de execução")
2. Clique em **Change runtime type** (ou "Alterar tipo de ambiente")
3. Em "Hardware accelerator", selecione **GPU**
4. Em "GPU type", selecione **T4** (gratuito)
5. Clique em **Save**

---

## ▶️ PASSO 4: Executar o Treinamento

1. Clique em **Runtime → Run all** (ou "Executar tudo")
2. O Colab vai executar célula por célula
3. **Quando pedir upload**: arraste o arquivo `dataset.zip`
4. Aguarde ~1-2 horas (pode deixar rodando e fazer outras coisas)
5. No final, o modelo será baixado automaticamente

---

## 📦 PASSO 5: Após o Treinamento

Você receberá um arquivo `soulnutri_model.zip` contendo:
- `best.pt` - modelo PyTorch (principal)
- `best.onnx` - modelo ONNX (alternativo)

**Guarde esses arquivos!** Você precisará enviá-los para o agente no próximo chat.

---

## ❓ Problemas Comuns

### "GPU não disponível"
- O Colab tem limite de uso gratuito
- Tente novamente em algumas horas
- Ou use a opção "CPU" (mais lento, ~4-6 horas)

### "Sessão desconectou"
- Normal se ficar muito tempo parado
- Clique em "Reconectar" e execute novamente
- O progresso é salvo a cada época

### "Erro de memória"
- Reduza o `batch_size` de 32 para 16
- Na célula de treinamento, mude o valor

---

## 📊 O Que Esperar

| Métrica | Meta |
|---------|------|
| Tempo de treino | ~1-2 horas |
| Acurácia esperada | ~85-90% |
| Tamanho do modelo | ~10-20 MB |
| Velocidade inferência | ~50-100ms |

---

## 🔄 Próximo Passo

Após ter o `best.pt`, volte ao chat da Emergent e diga:

> "Terminei o treinamento do YOLOv8. Tenho o arquivo best.pt pronto para integrar."

O agente vai ajudar a fazer o upload e ativar o modelo.

---

*SoulNutri - Seu agente de nutrição virtual*
