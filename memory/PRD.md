# SoulNutri - PRD (Product Requirements Document)

## Problema Original
Aplicativo de agente de nutrição virtual que identifica pratos em tempo real a partir de imagens, com foco em precisão >90% e honestidade (rejeitar pratos desconhecidos).

## Versão Atual: v1.23

## Arquitetura
- **Frontend**: React (CRA + Craco) em /app/frontend, porta 3000
- **Backend**: FastAPI em /app/backend, porta 8001
- **Database**: MongoDB Atlas (soulnutri)
- **AI**: CLIP (openai/clip-vit-base-patch32) local + Gemini Flash (fallback)
- **Nutrição**: Pipeline 3 fontes (TACO + USDA + Open Food Facts)

## O que foi implementado

### Reconhecimento de Pratos (v1.2 -> v1.23)
- CLIP local para identificação (zero custo)
- Gap Analysis em policy.py (rejeita se score1 - score2 < 0.02)
- GPS fix no App.js (não força Cibi Sana)
- Gemini fix em server.py (não restringe menu para locais externos)
- Dataset: 188 pratos, 1627 embeddings

### Pipeline Nutricional 3 Fontes (v1.23 - NOVO)
- **TACO**: Tabela Brasileira, 597 alimentos, local
- **USDA FoodData Central**: API gov EUA, 300K+ alimentos, chave real
- **Open Food Facts**: API global, 4M+ produtos, busca por categorias
- Método: média simples das fontes que retornam dados
- Transparência: valores individuais de cada fonte salvos
- 5 pratos processados: Tortinha, Umami, Uva, Vinagrete Lula, Vol Au Vent

### Backup v1.23
- Salvo em /app/backups/v1.23/ (disco local)
- Salvo no MongoDB coleção `code_backups` (nuvem, protegido)

### Proteção do Disco
- datasets/ adicionado ao .gitignore
- Script de limpeza: git gc + rm build + cache

## Coleções MongoDB
- `dishes`: 205 registros (pratos do cardápio)
- `nutrition_sheets`: 5 registros (fichas nutricionais 3 fontes)
- `code_backups`: 1 registro (backup v1.23)
- `users`, `settings`, `processing_metrics`, `daily_logs`, `feedback`, `api_usage`

## Endpoints Chave
- POST /api/ai/identify — identificação de pratos
- GET /api/ai/status — status do índice
- GET /api/nutrition/list — listar fichas nutricionais
- GET /api/nutrition/{dish_name} — buscar ficha por nome
- POST /api/ai/reindex-background — reconstruir índice

## Backlog Priorizado

### P0 - Crítico
- [ ] Expandir fichas nutricionais para todos os ~200 pratos
- [ ] Validação da lógica de reconhecimento (teste real no buffet)

### P1 - Importante
- [ ] Refatorar server.py (4400 linhas — muito grande)
- [ ] Refatorar Admin para usar nutrition_sheets como fonte da verdade

### P2 - Futuro
- [ ] Integração Stripe
- [ ] Migrar imagens para Object Storage externo
- [ ] App mobile nativo

## Chaves e Credenciais
- USDA_API_KEY: Em /app/backend/.env (1000 req/hora)
- GOOGLE_API_KEY: Em /app/backend/.env (Gemini)
- MONGO_URL: Em /app/backend/.env

## Arquivos de Referência
- /app/backend/server.py — API principal
- /app/backend/ai/index.py — busca CLIP v1.2
- /app/backend/ai/policy.py — gap analysis
- /app/backend/services/nutrition_3sources.py — pipeline 3 fontes
- /app/backend/scripts/enrich_usda.py — enriquecimento USDA
- /app/backend/scripts/generate_5_dishes.py — geração batch
- /app/frontend/src/App.js — interface principal
