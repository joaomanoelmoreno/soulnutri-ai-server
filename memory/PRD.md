# SoulNutri - Product Requirements Document

## Original Problem Statement
Construir o **SoulNutri**, um aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens com alta precisão, com feed de notícias gerado por IA, sistema de gamificação e fluxo seguro de feedback com moderação pelo admin.

## Architecture
- **Frontend**: React + ShadCN/UI (porta 3000)
- **Backend**: FastAPI + Python (porta 8001)
- **Database**: MongoDB Atlas
- **Storage**: Emergent Object Storage (S3-compatible)
- **AI**: HuggingFace CLIP + Google Gemini (via emergentintegrations)

## What's Been Implemented

### Core Features
- Reconhecimento de imagem com CLIP + Gemini fallback
- Feed de Notícias (Nutri News) com IA e fontes verificáveis
- Sistema Premium de Engajamento (conquistas, XP, streaks, relatórios semanais)
- Redesign visual "Gourmet Dark Mode"
- Migração completa para Object Storage (S3)

### Fluxo de Feedback Seguro (2026-03-23)
- Removido campo de texto livre para usuários digitarem nomes de pratos
- Botões simplificados: "Sim, está correto", "Não, tentar novamente", "Voltar"
- Fila de moderação no Admin com ações: Aprovar, Rejeitar, Corrigir
- Endpoints: POST /api/feedback/moderation-queue, GET/POST /api/admin/moderation-*
- Testado com testing_agent: 16/16 testes passaram (100% backend, 100% frontend)

## Key DB Collections
- `dishes`, `dish_storage`, `news_items`, `achievements`, `daily_logs`
- `moderation_queue` (NOVO): { original_dish, original_dish_display, confidence, score, source, image_path, status, created_at, resolved_at, correction }

## Pending Issues
- (P1) Resultados insatisfatórios nos testes do buffet - BLOQUEADO (aguardando análise do usuário)
- (P2) Revisão de dados nutricionais potencialmente contaminados - AGUARDANDO lista do usuário

## Upcoming Tasks
- (P1) Notificações push personalizadas (máx 1/dia) com referências e links
- (P1) Referências e links clicáveis na tela de resultado da identificação

## Backlog/Future
- (P1) Refatorar server.py e App.js em módulos menores
- (P2) Integração com Stripe para premium
- (P2) Endpoint para admin upload de ZIP com fotos
- (P2) Não salvar nova versão até autorização do usuário

## Integrations
- Emergent Object Storage (S3), Emergent LLM Key (emergentintegrations/Gemini)
- USDA FoodData Central, Open Food Facts, TACO (dados nutricionais)
- HuggingFace CLIP (reconhecimento de imagem)

## Credentials
- Admin: joaomanoelmoreno / Pqlamz0192
