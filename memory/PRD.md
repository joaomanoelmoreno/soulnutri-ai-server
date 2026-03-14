# SoulNutri - PRD (Product Requirements Document)

## Problema Original
Aplicativo de agente de nutrição virtual que identifica pratos em tempo real a partir de imagens, com foco em precisão >90% e honestidade (rejeitar pratos desconhecidos).

## Versão Atual: v1.23

## Arquitetura
- **Frontend**: React (CRA + Craco) em /app/frontend, porta 3000
- **Backend**: FastAPI em /app/backend, porta 8001
- **Database**: MongoDB Atlas (soulnutri)
- **AI**: CLIP (openai/clip-vit-base-patch32) local + Gemini Flash (fallback)
- **Nutrição**: Pipeline 3 fontes (TACO + USDA FNDDS + Open Food Facts)

## O que foi implementado

### Reconhecimento de Pratos (v1.2 -> v1.23)
- CLIP local para identificação (zero custo)
- Gap Analysis em policy.py (rejeita se score1 - score2 < 0.02)
- GPS fix no App.js (não força Cibi Sana)
- Gemini fix em server.py (não restringe menu para locais externos)
- Dataset: 188 pratos, 1627 embeddings

### Pipeline Nutricional 3 Fontes v2 (v1.23)
- **TACO**: Tabela Brasileira, 597 alimentos, busca por ingredientes
- **USDA FoodData Central FNDDS**: Busca por NOME DO PRATO (pratos compostos), chave real
- **Open Food Facts**: Busca por categoria (apenas itens simples)
- Método: busca pelo nome do prato (como apps de nutrição fazem), não decomposição de ingredientes
- 5 pratos processados com resultados validados

### Git Corrigido
- Repositório .git reinicializado (de 2.5GB corrompido para 39MB limpo)
- datasets/ no .gitignore (previne crescimento do git)

### Backup v1.23
- Salvo no MongoDB coleção `code_backups` (protegido na nuvem)
- Disponível para push no GitHub (git limpo)

## Coleções MongoDB
- `dishes`: 205 registros (campo `nutricao` atualizado para 5 pratos)
- `nutrition_sheets`: 5 registros (fichas nutricionais 3 fontes v2)
- `code_backups`: 1 registro (backup v1.23)

## Endpoints Chave
- POST /api/ai/identify — identificação de pratos
- GET /api/ai/status — status do índice
- GET /api/nutrition/list — listar fichas nutricionais
- GET /api/nutrition/{dish_name} — buscar ficha por nome
- POST /api/ai/reindex-background — reconstruir índice

## Backlog Priorizado

### P0 - Crítico
- [ ] Expandir fichas nutricionais para todos os ~200 pratos
- [ ] Melhorar mapeamento DISH_USDA_QUERY para mais pratos
- [ ] Validação de reconhecimento no buffet (teste real)

### P1 - Importante
- [ ] Refatorar server.py (4400 linhas)
- [ ] Refatorar Admin para usar nutrition_sheets como fonte da verdade

### P2 - Futuro
- [ ] Integração Stripe
- [ ] Migrar imagens para Object Storage externo
- [ ] App mobile nativo

## Chaves e Credenciais
- USDA_API_KEY em /app/backend/.env (1000 req/hora)
- GOOGLE_API_KEY em /app/backend/.env (Gemini)
- MONGO_URL em /app/backend/.env

## Arquivos de Referência
- /app/backend/services/nutrition_3sources.py — pipeline 3 fontes v2
- /app/backend/server.py — API principal (com lookup_nutrition_sheet)
- /app/backend/ai/index.py — busca CLIP v1.2
- /app/backend/ai/policy.py — gap analysis
- /app/frontend/src/App.js — interface principal
