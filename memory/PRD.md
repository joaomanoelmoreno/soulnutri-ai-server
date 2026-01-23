# SoulNutri - Product Requirements Document

**Última atualização**: Janeiro 2026
**URL**: https://nutridetect-6.preview.emergentagent.com

---

## Visão
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

O SoulNutri é um agente de nutrição virtual que acompanha o cliente em TEMPO REAL durante as refeições, fornecendo informações científicas, alertas personalizados e educação nutricional.

---

## 🚨 TAREFA PENDENTE DO USUÁRIO

**O usuário está treinando o modelo YOLOv8 no Google Colab.**

Quando ele voltar, provavelmente dirá:
- "Terminei o treinamento" → Pedir o arquivo `best.pt` e integrar
- "Tive problemas no Colab" → Ver `/app/ml/GUIA_TREINAMENTO_YOLOV8.md`

**Arquivos para o usuário baixar:**
- `/app/ml/dataset.zip` (148 MB)
- `/app/ml/SoulNutri_YOLOv8_Training.ipynb`

---

## Funcionalidades por Versão

### 🆓 VERSÃO GRATUITA
- Identificação de pratos por imagem
- Nome, categoria e ingredientes do prato
- Alérgenos básicos
- Modo Multi-Item (buffet)

### ⭐ VERSÃO PREMIUM
**Exclusivo Premium - Alertas em Tempo Real:**
- ✅ Informações científicas (curiosidade, benefício, referência)
- ✅ Alertas de alérgenos baseados no PERFIL do usuário
- ✅ Alertas de nutrientes baseados no HISTÓRICO semanal
- ✅ Combinações inteligentes
- ✅ Substituições saudáveis
- ✅ Meta calórica automática (Harris-Benedict)
- ✅ Contador nutricional diário
- ✅ Histórico de consumo

---

## Status Atual

### ✅ Implementado
- [x] Identificação em cascata (Cache → OpenCLIP → YOLOv8 → Gemini)
- [x] Sistema de Cache (~0ms para repetidos)
- [x] Login com Nome + PIN
- [x] Perfil com dados físicos e alergias
- [x] Contador nutricional diário
- [x] Alertas Premium em tempo real
- [x] Seção "Você Sabia?" com visual melhorado
- [x] Proteção anti-fake news
- [x] **Endpoint YOLOv8 configurado** (aguardando modelo)
- [x] **Dataset preparado**: 8.145 imagens (5x augmentation)

### ⏳ Aguardando
- [ ] **Modelo YOLOv8 treinado** (usuário vai treinar no Colab)

### 📋 Próximas Tarefas (após YOLOv8)
| Prioridade | Tarefa |
|------------|--------|
| P2 | Notícias recentes na UI Premium |
| P2 | Melhorar alertas visuais |
| P3 | Histórico semanal com gráficos |
| P3 | Receitas saudáveis |

---

## Arquitetura de Identificação

```
┌─────────────────────────────────────────────────────────┐
│           CASCATA DE IDENTIFICAÇÃO                       │
├─────────────────────────────────────────────────────────┤
│ 0. CACHE       │ Hash MD5            │ ~0ms             │
│ 1. OpenCLIP    │ Pratos cadastrados  │ ~200-300ms       │
│ 1.5 YOLOv8     │ Modelo local (⏳)   │ ~50-100ms        │
│ 2. Gemini      │ Fallback universal  │ ~3-5s            │
└─────────────────────────────────────────────────────────┘
```

### Para ativar YOLOv8:
1. Usuário treina no Colab
2. Faz upload de `best.pt` 
3. Mover para `/app/ml/models/best.pt`
4. Reiniciar backend
5. Automático!

---

## Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `/app/memory/CONTINUIDADE.md` | Documento completo de continuidade |
| `/app/ml/GUIA_TREINAMENTO_YOLOV8.md` | Guia para iniciantes |
| `/app/ml/dataset.zip` | Dataset para treinar |
| `/app/ml/SoulNutri_YOLOv8_Training.ipynb` | Notebook Colab |
| `/app/backend/services/yolo_service.py` | Serviço YOLOv8 |

---

## URL
https://nutridetect-6.preview.emergentagent.com
