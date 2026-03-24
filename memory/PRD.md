# SoulNutri - Product Requirements Document

## Original Problem Statement
Construir o **SoulNutri**, um aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens com alta precisão, com feed de notícias gerado por IA, sistema de gamificação, fluxo seguro de feedback com moderação pelo admin, notificações push personalizadas e pipeline seguro de atualização nutricional.

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
- Testado: 16/16 testes passaram

### Correção Admin Travado (2026-03-24)
- Criados endpoints faltantes: /api/admin/settings, /api/admin/premium/users, /api/admin/api-usage, /api/admin/processing-metrics
- Adicionado safeFetch wrapper para evitar "body stream already read"
- Adicionado res.ok checks em todas as funções de fetch

### Notificações Push Personalizadas (2026-03-24)
- Sistema de notificações baseadas no consumo real do usuário
- Máximo 1 notificação por dia por usuário
- Todas incluem referências e links verificáveis (WHO, TACO, Harvard, Mayo Clinic, etc.)
- Botão de sino no header para usuários premium
- Painel lateral slide-in com lista de notificações
- Endpoints: POST /api/notifications/generate, GET /api/notifications/{pin}, POST /api/notifications/{pin}/read
- Testado: 100% backend, 100% frontend

### Referências na Tela de Resultado (2026-03-24)
- Links clicáveis para TACO, USDA e Open Food Facts na tela de identificação
- Aparece quando confiança não é "baixa"

### Pipeline Seguro de Nutrição (2026-03-24)
- Preview/dry-run mostra o que mudaria SEM alterar
- Update individual com backup automático
- Rollback para reverter última alteração
- Audit log completo de todas as mudanças
- NUNCA toca em imagens, slugs ou estrutura
- Endpoints: /api/admin/nutrition/preview, update-single, rollback, audit-log
- Testado: 100% passaram

## Key DB Collections
- `dishes`, `dish_storage`, `news_items`, `achievements`, `daily_logs`
- `moderation_queue`: { original_dish, original_dish_display, confidence, score, source, image_path, status, created_at, correction }
- `notifications`: { user_pin, user_name, type, title, message, icon, priority, references, dishes_context, date, created_at, read }
- `nutrition_audit_log`: { dish_slug, dish_nome, old_nutrition, new_nutrition, source_info, timestamp, action }
- `admin_settings`, `premium_users`, `api_usage`, `processing_metrics`

## Pending Issues
- (P1) Resultados insatisfatórios nos testes do buffet - BLOQUEADO (aguardando análise do usuário)
- (P2) Revisão de dados nutricionais potencialmente contaminados - AGUARDANDO lista do usuário

## Upcoming Tasks
- (P1) Refatorar server.py e App.js em módulos menores

## Backlog/Future
- (P2) Integração com Stripe para premium
- (P2) Endpoint para admin upload de ZIP com fotos
- (P2) Não salvar nova versão até autorização do usuário

## Integrations
- Emergent Object Storage (S3), Emergent LLM Key (emergentintegrations/Gemini)
- USDA FoodData Central, Open Food Facts, TACO (dados nutricionais)
- HuggingFace CLIP (reconhecimento de imagem)

## Credentials
- Admin: joaomanoelmoreno / Pqlamz0192
