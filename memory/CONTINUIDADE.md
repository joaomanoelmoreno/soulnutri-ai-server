# SoulNutri - Documento de Continuidade

**Data**: Janeiro 2026
**Projeto**: SoulNutri - Agente de Nutrição Virtual
**URL**: https://clip-enrich-fix.preview.emergentagent.com

---

## 🎯 ESTADO ATUAL DO PROJETO

### ✅ Funcionando
- App completo (React + FastAPI + MongoDB)
- Identificação de pratos por imagem
- Sistema Premium com login Nome+PIN
- Contador nutricional diário
- Alertas personalizados
- Cache de imagens (~0ms para repetidos)
- Seção "Você Sabia?" com visual melhorado
- Proteção anti-fake news em notícias
- **🛡️ SISTEMA DE SEGURANÇA** - Valida e corrige classificações erradas

### ⏳ Em Andamento
- **Treinamento YOLOv8**: Rodando em background (~Época 10/50, ~99% accuracy)

### 🛡️ Sistema de Segurança (NOVO)
- Arquivo: `/app/backend/services/safety_validator.py`
- Detecta proteínas animais em pratos classificados como veganos
- Detecta derivados (ovo/leite) em pratos classificados como veganos
- Corrige automaticamente a categoria
- Detecta 9 tipos de alérgenos
- Gera alertas de segurança

### 🔴 Limitação Conhecida
- Pratos não cadastrados levam ~3-5s (Gemini Vision)
- Será resolvido com YOLOv8 (~50-100ms)

---

## 📁 ARQUIVOS IMPORTANTES

### Para Treinamento YOLOv8
```
/app/ml/
├── dataset.zip                    # 148 MB - Dataset com 8.145 imagens
├── SoulNutri_YOLOv8_Training.ipynb # Notebook para Google Colab
├── GUIA_TREINAMENTO_YOLOV8.md     # Guia passo a passo
├── YOLOV8_PROJECT.md              # Documentação técnica
├── datasets_augmented/            # Dataset expandido (train/val/test)
├── models/                        # Pasta para best.pt (vazia)
└── scripts/
    ├── augment_dataset.py         # Script de data augmentation
    └── prepare_dataset.py         # Script de preparação
```

### Backend
```
/app/backend/
├── server.py                      # API principal (cascata de identificação)
└── services/
    ├── yolo_service.py            # Serviço YOLOv8 (aguardando modelo)
    ├── generic_ai.py              # Gemini Vision (fallback)
    ├── cache_service.py           # Cache de imagens
    ├── alerts_service.py          # Alertas Premium
    └── profile_service.py         # Perfis de usuário
```

### Frontend
```
/app/frontend/src/
├── App.js                         # Componente principal
├── App.css                        # Estilos (inclui "Você Sabia?")
├── Premium.jsx                    # Interface Premium
└── Premium.css                    # Estilos Premium
```

---

## 🔄 TAREFAS PENDENTES (por prioridade)

### P0 - Crítico
1. **Integrar modelo YOLOv8 após treinamento**
   - Usuário vai treinar no Colab
   - Receberá arquivo `best.pt`
   - Fazer upload para `/app/ml/models/best.pt`
   - O sistema detecta automaticamente

### P2 - Importante
2. **Notícias recentes na UI Premium**
   - Endpoint já existe: `/api/ai/ingredient-research/{ingrediente}`
   - Falta integrar no frontend

3. **Melhorar alertas visuais**
   - Combinações de alimentos
   - Substituições saudáveis

### P3 - Backlog
4. Histórico semanal com gráficos
5. Receitas saudáveis
6. Gamificação

---

## 🏗️ ARQUITETURA DE IDENTIFICAÇÃO

```
┌─────────────────────────────────────────────────────────┐
│           CASCATA DE IDENTIFICAÇÃO                       │
├─────────────────────────────────────────────────────────┤
│ 0. CACHE       │ Hash MD5 da imagem   │ ~0ms            │
│ 1. OpenCLIP    │ Pratos cadastrados   │ ~200-300ms      │
│ 1.5 YOLOv8     │ Modelo local (⏳)    │ ~50-100ms       │
│ 2. Gemini      │ Fallback universal   │ ~3-5s           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 CREDENCIAIS

### Para testar Premium
- Criar novo usuário pelo app, ou
- Nome: (criar via registro)
- PIN: 4-6 dígitos

### APIs
- Gemini Vision: Usa Emergent LLM Key (já configurada)
- MongoDB: Configurado via MONGO_URL no .env

---

## 📝 INSTRUÇÕES PARA O PRÓXIMO AGENTE

### Se usuário disser "Tenho o best.pt pronto":
1. Pedir para fazer upload do arquivo
2. Mover para `/app/ml/models/best.pt`
3. Reiniciar backend: `sudo supervisorctl restart backend`
4. Testar identificação - deve mostrar `source: yolov8`

### Se usuário quiser continuar desenvolvimento:
1. Ler este documento
2. Ver PRD.md para visão geral
3. Prioridades: P0 → P2 → P3

### Se usuário tiver problemas com Colab:
1. Ver `/app/ml/GUIA_TREINAMENTO_YOLOV8.md`
2. Problemas comuns documentados lá

---

## 📊 MÉTRICAS DO DATASET

- **Classes processadas**: 125
- **Imagens originais**: 1.629
- **Imagens após augmentation**: 8.145 (5x)
- **Divisão**: 80% train / 10% val / 10% test

---

## 🚀 COMANDO RÁPIDO PARA TESTAR

```bash
# Testar identificação
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
curl -X POST "$API_URL/api/ai/identify" -F "file=@/tmp/test_image.jpg"

# Verificar se YOLOv8 está disponível
ls -la /app/ml/models/

# Ver logs do backend
tail -f /var/log/supervisor/backend.err.log
```

---

*Documento criado em Janeiro 2026 para garantir continuidade do projeto SoulNutri*
