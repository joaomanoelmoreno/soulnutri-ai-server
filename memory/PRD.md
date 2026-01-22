# SoulNutri - Product Requirements Document

## Visão
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

O SoulNutri é um agente de nutrição virtual que acompanha o cliente em TEMPO REAL durante as refeições, fornecendo informações científicas, alertas personalizados e educação nutricional.

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
  - Ex: "Este prato tem 800mg de sódio. Você já consumiu 1500mg esta semana!"
- ✅ Combinações inteligentes
  - Ex: "Combine feijão com limão para absorver 6x mais ferro!"
- ✅ Substituições saudáveis
  - Ex: "Troque batata frita por batata assada: 70% menos gordura"
- ✅ Meta calórica automática (Harris-Benedict)
- ✅ Contador nutricional diário
- ✅ Histórico de consumo

**Educação Nutricional (implementado no backend):**
- Combinações que melhoram absorção
- Substituições mais saudáveis
- Rastreamento de nutrientes: sódio, açúcar, fibras, proteínas

---

## Status Atual (Janeiro 2026)

### ✅ Implementado
- [x] Identificação em cascata (OpenCLIP + Gemini Vision)
- [x] **Sistema de Cache** - reduz tempo para 0ms em pratos repetidos
- [x] Login com Nome + PIN
- [x] Perfil com dados físicos e alergias
- [x] Meta calórica calculada
- [x] Contador nutricional diário
- [x] **Alertas Premium em tempo real**
- [x] **Combinações inteligentes**
- [x] **Substituições saudáveis**
- [x] **Info científica só para Premium**
- [x] Botão "Início" no dashboard Premium

### 🔴 Limitação Conhecida
- **Pratos não cadastrados**: ~3-5s (Gemini Vision)
- **Causa**: APIs gratuitas do Hugging Face descontinuadas/requerem autenticação paga
- **Mitigação**: Cache reduz tempo para 0ms em pratos já identificados
- **Solução futura**: Modelo YOLOv8 customizado

### 📋 Prioridades (atualizado)
| Prioridade | Tarefa | Status |
|------------|--------|--------|
| P1 | Alertas personalizados Premium | ✅ Feito |
| P1 | "Você sabia..." / Curiosidades | 🔄 Parcial (curiosidade_cientifica) |
| P1 | Combinação de alimentos | ✅ Feito |
| P2 | Notícias recentes sobre ingredientes | ⏳ Pendente |
| P2 | Seção "Você Sabia" destacada na UI | ⏳ Pendente |
| P3 | Histórico semanal com gráficos | ⏳ Pendente |
| P3 | Receitas saudáveis | ⏳ Pendente |
| P4 | Gamificação (conquistas) | ⏳ Backlog |
| P4 | Interações medicamentosas | ⏳ Backlog |

---

## Arquitetura

### Sistema de Identificação
```
┌─────────────────────────────────────────────────────────┐
│               SISTEMA DE IDENTIFICAÇÃO                   │
├─────────────────────────────────────────────────────────┤
│ 0. CACHE       │ Hash da imagem      │ ~0ms (repetidos) │
│ 1. OpenCLIP    │ Pratos cadastrados  │ ~200-300ms       │
│ 2. Gemini      │ Pratos genéricos    │ ~3-5s            │
│ 🔜 YOLOv8      │ Em desenvolvimento  │ ~50-100ms        │
└─────────────────────────────────────────────────────────┘
```

### Projeto YOLOv8 (Em Andamento)
- **Status**: Fase 1 - Preparação de Dataset
- **Dataset**: 229 classes, 1746 imagens (58 classes com 10+ imgs)
- **Documentação**: `/app/ml/YOLOV8_PROJECT.md`
- **Meta**: Inferência < 100ms, Acurácia > 85%

### Backend
- FastAPI + MongoDB
- Serviços: `profile_service.py`, `alerts_service.py`, `generic_ai.py`, `cache_service.py`

### Frontend
- React com componentes Premium
- LocalStorage para sessão (nome + PIN)
- **Seção "Você Sabia?"** destacada com visual premium

### Proteção Anti-Fake News
- Apenas fontes verificadas: OMS, ANVISA, FDA, PubMed
- Nível de evidência indicado (consenso/forte/moderado/preliminar)
- Data e fonte oficial obrigatórias

### Fluxo Premium
1. Usuário faz login (nome + PIN)
2. Ao identificar prato, envia credenciais
3. Backend verifica se é Premium
4. Se sim, retorna dados científicos + alertas personalizados
5. Frontend exibe alertas em tempo real

---

## Endpoints

| Endpoint | Premium? | Descrição |
|----------|----------|-----------|
| `POST /api/ai/identify` | Parcial | Retorna alertas Premium se autenticado |
| `POST /api/premium/register` | - | Criar perfil |
| `POST /api/premium/login` | - | Login nome + PIN |
| `POST /api/premium/log-meal` | Sim | Registrar refeição |
| `GET /api/premium/daily-summary` | Sim | Resumo do dia |
| `GET /api/premium/history` | Sim | Histórico semanal |
| `GET /api/ai/ingredient-research/{ingrediente}` | Sim | Notícias verificadas |

---

## URL
https://plate-radar.preview.emergentagent.com
