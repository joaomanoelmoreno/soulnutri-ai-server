# SoulNutri - Product Requirements Document

## Ultima Atualizacao: 2026-03-04

### Status do Projeto: OPERACIONAL

---

## Visao do Produto
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real via camera, fornecendo informacoes nutricionais detalhadas e personalizadas.

## Arquitetura Atual

### Reconhecimento de Imagem (Cascata)
1. **CLIP Local** (custo zero) - Modelo ViT-B-32 com 223 pratos indexados, 1605 embeddings
2. **Gemini Flash** (backup) - Usado quando CLIP nao confiante e fora do Cibi Sana

### Stack
- Frontend: React (src/App.js, src/Admin.js, src/Premium.jsx, src/DashboardPremium.jsx)
- Backend: FastAPI (server.py)
- DB: MongoDB Atlas
- IA: OpenCLIP local + Gemini Flash fallback

---

## O que foi implementado

### Monitoramento de Tempo (2026-03-04)
- Flag persistida `ENABLE_PROCESSING_METRICS` no MongoDB (collection `settings`)
- Medicao com `time.perf_counter()` no endpoint `/api/ai/identify`
- Log JSONL em `/app/logs/processing_metrics.log`
- Endpoint `GET /api/admin/processing-metrics?date=YYYY-MM-DD`
- Endpoints `GET/POST /api/admin/settings` para toggle
- Tab "Metricas" no `/admin` com toggle ON/OFF, seletor de data, resumo e tabela
- Zero impacto quando desativado (verificado)

### Correcoes Anteriores
- Calibracao do CLIP restaurada
- Indice reconstruido: 223 pratos, 1605 imagens
- encodeURIComponent aplicado no Admin.js para pratos com espacos
- Fallback de camera para Mac
- Dashboard Premium V1 (frontend + backend)
- Botao "Nutricao TACO (gratis)" no Admin

---

## Fluxo de Economia de Creditos

| Acao | Custo |
|------|-------|
| Reconhecimento no Cibi Sana | ZERO (CLIP) |
| Reconhecimento fora | Pode usar Gemini |
| Nutricao com TACO | ZERO |
| Nutricao com IA | GASTA creditos |
| "Revisar com IA" no Admin | GASTA creditos |

---

## Tarefas Pendentes

### P0 - Critica
- [ ] Verificar estabilidade do Admin (encodeURIComponent) com usuario

### P1 - Alta Prioridade
- [ ] Finalizar e testar Dashboard Premium (DashboardPremium.jsx)
- [ ] Implementar Relatorios Premium (baseado em COMPARATIVO_CONCORRENTES.md)

### P2 - Media Prioridade
- [ ] Investigar Cloudflare R2 para armazenamento de imagens (disco 88%)
- [ ] Refatorar App.js e server.py (arquivos monoliticos)

### P3 - Backlog
- [ ] Implementar Stripe para assinaturas Premium
- [ ] Integrar API de reconhecimento Nivel 2 (LogMeal)

---

## Credenciais de Teste
- Usuario Premium: `Joao mc`, PIN: `1234`

## Arquivos Principais
- `/app/backend/server.py` - API principal (4590 linhas)
- `/app/backend/ai/index.py` - Logica CLIP e calibracao
- `/app/frontend/src/App.js` - Interface principal
- `/app/frontend/src/Admin.js` - Painel administrativo (com tab Metricas)
- `/app/frontend/src/Admin.css` - Estilos do Admin
- `/app/frontend/src/Premium.jsx` - Portal Premium
- `/app/frontend/src/DashboardPremium.jsx` - Dashboard Premium
- `/app/backend/data/taco_database.py` - Tabela TACO
- `/app/datasets/organized/` - Fotos dos pratos
- `/app/logs/processing_metrics.log` - Log de metricas de processamento

## Integracoes de Terceiros
- Google Gemini (EMERGENT_LLM_KEY)
- Hugging Face (OpenCLIP)
- MongoDB Atlas
