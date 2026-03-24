# SoulNutri - Product Requirements Document

## Original Problem Statement
Construir o **SoulNutri**, um app de nutrição virtual que identifica pratos por imagem com alta precisão.

## Architecture
- **Frontend**: React (porta 3000)
- **Backend**: FastAPI + Python (porta 8001)
- **Database**: MongoDB Atlas
- **Storage**: Emergent Object Storage (S3)
- **AI**: HuggingFace CLIP + Gemini

## What's Been Implemented

### Core Features
- Reconhecimento de imagem CLIP + Gemini fallback
- Nutri News (feed IA com fontes verificáveis)
- Sistema Premium (conquistas, XP, streaks, relatórios semanais)
- Redesign visual "Gourmet Dark Mode"
- Migração para Object Storage (S3)

### Fluxo Feedback Seguro (2026-03-23)
- Botões: "Sim, está correto", "Não, tentar novamente", "Voltar"
- Fila moderação no Admin (aprovar/rejeitar/corrigir)

### Correção Admin (2026-03-24)
- Criados endpoints faltantes: settings, premium/users, api-usage, processing-metrics

### Correção Definitiva Admin (2026-03-25)
- Causa raiz: `Admin.js` usava URL absoluta (`process.env.REACT_APP_BACKEND_URL/api/...`) que era interceptada por scripts da plataforma Emergent
- Fix: `const API = '/api'` (URL relativa) — o `setupProxy.js` redireciona corretamente para o backend
- Sem wrappers, sem XMLHttpRequest, sem hacks — apenas fetch padrão com URL relativa

### Notificações Push (2026-03-24)
- Max 1/dia, baseadas no consumo real
- Referências e links verificáveis (WHO, TACO, Harvard, Mayo Clinic)
- Botão sino no header, painel lateral slide-in

### Referências na Identificação (2026-03-24)
- Links TACO, USDA, Open Food Facts na tela de resultado

### Pipeline Seguro de Nutrição (2026-03-24)
- Preview/dry-run, update individual com backup, rollback, audit log
- NUNCA toca em imagens, slugs ou estrutura

## Key DB Collections
- dishes, dish_storage, news_items, achievements, daily_logs
- moderation_queue, notifications, nutrition_audit_log
- admin_settings, premium_users

## Pending Issues
- (P1) Resultados insatisfatórios nos testes do buffet (aguardando análise)
- (P2) Revisão de dados nutricionais contaminados (aguardando lista)

## Upcoming Tasks
- (P1) Refatorar server.py e App.js em módulos menores

## Backlog
- (P2) Integração Stripe para premium
- (P2) Upload ZIP pelo admin
- (P2) Não salvar nova versão até autorização

## Credentials
- Admin: joaomanoelmoreno / Pqlamz0192
