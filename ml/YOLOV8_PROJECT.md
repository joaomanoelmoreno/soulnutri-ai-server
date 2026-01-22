# SoulNutri - Projeto YOLOv8 para Identificação de Alimentos

## Objetivo
Treinar modelo YOLOv8 customizado para identificar alimentos em tempo real (~50-100ms) no dispositivo do cliente.

## Vantagens
- **Velocidade**: ~50-100ms vs ~3-5s do Gemini
- **Custo**: Zero após treinamento (roda local)
- **Offline**: Funciona sem internet
- **Privacidade**: Imagens não saem do dispositivo

## Fases do Projeto

### Fase 1: Coleta de Dados (Semana 1)
- [ ] Coletar 500+ imagens por categoria de prato
- [ ] Priorizar pratos brasileiros comuns
- [ ] Usar imagens do dataset existente em `/app/datasets/organized/`
- [ ] Aumentar dataset com data augmentation

### Fase 2: Preparação (Semana 1-2)
- [ ] Anotar imagens no formato YOLO (bounding boxes)
- [ ] Dividir: 80% treino, 10% validação, 10% teste
- [ ] Configurar ambiente de treinamento (GPU)

### Fase 3: Treinamento (Semana 2-3)
- [ ] Treinar YOLOv8n (nano) para classificação
- [ ] Fine-tuning com dataset de alimentos
- [ ] Validar métricas: mAP > 85%, recall > 80%

### Fase 4: Integração (Semana 3-4)
- [ ] Exportar modelo para ONNX/TensorFlow.js
- [ ] Integrar no backend como Nível 1.5
- [ ] Testes A/B com usuários reais

## Estrutura de Diretórios

```
/app/ml/
├── datasets/
│   ├── train/
│   ├── val/
│   └── test/
├── models/
│   └── yolov8_food.pt
├── scripts/
│   ├── prepare_dataset.py
│   ├── train.py
│   └── export.py
└── config/
    └── food_classes.yaml
```

## Classes Prioritárias (50 pratos brasileiros)

1. Arroz branco
2. Feijão
3. Feijoada
4. Bife
5. Frango grelhado
6. Salada verde
7. Farofa
8. Batata frita
9. Macarrão
10. Pizza
... (expandir com pratos do Cibi Sana)

## Requisitos de Hardware

Para treinamento:
- GPU: NVIDIA RTX 3080+ ou Google Colab Pro
- RAM: 16GB+
- Storage: 50GB+

Para inferência (produção):
- CPU moderna ou GPU básica
- ~100MB de memória

## Comandos Base

```bash
# Instalar ultralytics
pip install ultralytics

# Treinar modelo
yolo task=classify mode=train model=yolov8n-cls.pt data=/app/ml/datasets epochs=100

# Validar
yolo task=classify mode=val model=/app/ml/models/yolov8_food.pt

# Exportar para ONNX
yolo export model=/app/ml/models/yolov8_food.pt format=onnx
```

## Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| Acurácia Top-1 | > 85% |
| Acurácia Top-5 | > 95% |
| Tempo inferência | < 100ms |
| Tamanho modelo | < 20MB |

## Próximos Passos Imediatos

1. Criar estrutura de diretórios
2. Inventariar imagens existentes
3. Script de preparação de dataset
4. Configurar ambiente de treinamento
