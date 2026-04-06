# SoulNutri - Product Requirements Document
## Versao 2.0 — ViT-B-16 Stable (2026-04-05)

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192
- Premium test user: pin=1234, nome=Teste SoulNutri

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-16, DataComp.XL) para embedding de imagens
- Storage: Cloudflare R2 (bucket: soulnutri-images) - 4389 fotos
- DB: MongoDB Atlas

## Regra de Negocio Critica: Hard Lock Cibi Sana
- Dentro do Cibi Sana (restaurant=cibi_sana): APENAS OpenCLIP. Gemini 100% BLOQUEADO.
- Fora do Cibi Sana: Gemini permitido como fallback quando CLIP < 85%.
- Aplicado em 3 endpoints: /ai/identify, /ai/identify-with-ai, /ai/identify-flash

## Funcionalidades Implementadas

### Layout Premium Obsidian / Black Card (2026-04-06)
- Classe CSS `premium-active` diferencia toda a experiencia
- **Premium Obsidian**: Fundo preto puro (#080808), acentos dourado fosco/champagne (#d4af37)
  - Badge "PREMIUM" dourado no header com animacao de brilho
  - Header com borda dourada, menu/pratos/sino em gold fosco
  - Resultado com gradiente champagne no nome do prato
  - Camera com borda dourada sutil
  - Mini-counter e botao "Dieta" com tema obsidian
- **Gratuito**: Fundo azul navy (#0f172a), sem badge, sem sino, cores padrao verde/branco
- Analogia: como cartao de credito basico vs Black Card
- Estilos: App.css (overrides .premium-active) e Premium.css

### Calibracao CLIP
- Thresholds: >=0.90 alta, >=0.50 media, <0.50 rejeicao
- POST /api/ai/calibration/log: registro automatico
- DELETE /api/ai/calibration/clear-all: zerar TODAS as amostras
- DELETE /api/ai/calibration/{id}: deletar individual
- GET /api/ai/calibration: estatisticas + Youden's J
- Aba "Calibracao CLIP" no Admin com botao "Zerar Tudo"

### Notificacoes Push (VALIDADO 2026-04-06)
- POST /api/notifications/generate: gera notificacao diaria com referencias
- GET /api/notifications/{user_pin}: lista com unread count
- POST /api/notifications/{user_pin}/read: marca como lida
- NotificationPanel.jsx com icones, prioridades, referencias clicaveis

### Upload Fotos (FIX 2026-04-06)
- Dataset exibe nomes em Title Case (fix: usa campo name ao inves de slug)
- Corrigido slug com underscore: arroz_7_graos -> arroz-7-graos-c-ou-s-frutas-secas
- Mescladas 3 duplicatas (Bolinho Bacalhau, Frango Creme Limao, Sobrecoxa Tandoori)
- Upload ZIP funcional no admin
- 196 pratos no dish_storage (limpo, sem duplicatas)

### Dados Nutricionais
- Pratos A-E todos com dados completos
- 2 pratos preenchidos: Ceviche Banana da Terra, Espaguete Abobrinha Pesto
- Fonte: TACO + Gemini Flash

### Outras funcionalidades
- Identificacao de pratos via camera/foto (PWA)
- Ficha nutricional detalhada com dados TACO (255 mapeamentos)
- Sistema premium com pin de acesso
- Nutri News, gamificacao, moderacao
- Design "Gourmet Dark Mode"
- Normalizacao iOS/Android (1024px, 85% JPEG)
- Padronizacao de nomes (Title Case)

## Pratos com Poucas Fotos (<=5) - 19 pratos
- [SEM FOTOS] Ceviche de Banana da Terra: 0
- [CRITICO] Beringela a Parmegiana: 1
- [CRITICO] Espaguete de Abobrinha ao Pesto: 1
- [CRITICO] Polenta com Ragu: 1
- [CRITICO] Risoto de Alho Poro: 1
- [BAIXO] Maminha ao Gorgonzola: 2
- [BAIXO] Carne Moida com Ovo Poche: 3
- [BAIXO] Doce de Banana Vegano sem Acucar: 3
- [BAIXO] Gelatina de Uva: 3
- [ALERTA] Almondegas com Especiarias Indiana: 4
- [ALERTA] Carne Seca com Abobora: 4
- [ALERTA] Cogumelos Recheados: 4
- [ALERTA] Coxinha Saudavel de Frango: 4
- [ALERTA] Creme de Banana: 4
- [ALERTA] Creme de Milho: 4
- [ALERTA] Panacota com Frutas Vermelhas: 4
- [ALERTA] Pao de Alho Negro e Cumaru: 4
- [ALERTA] Proteina de Soja ao Sugo: 4
- [ALERTA] Risoto de Pera e Gorgonzola: 4

## Estado Atual
- 196 pratos, todos com embeddings IA (ViT-B-16)
- 4389+ fotos no Cloudflare R2
- 255 mapeamentos TACO
- Precisao: 100% (20/20, 0 falsos positivos)

## Upcoming Tasks
- (P0) Testar fotos reais no buffet com ViT-B-16
- (P2) Revisao nutricional pratos F-Z

## Future/Backlog Tasks
- (P1) Landing page de onboarding premium (trial 7 dias)
- (P1) Comercializacao Apple Store / Google Play
- (P1) Integracao Stripe para premium
- (P2) Refatorar server.py (5K+) e Admin.js (3K+)
- (P2) Verificar Upload ZIP ativo

## REGRA CRITICA: LOCK do Pipeline ViT-B-16
- /app/backend/ai/embedder.py — NAO ALTERAR
- /app/backend/ai/index.py — NAO ALTERAR
- /app/datasets/dish_index.json — NAO ALTERAR
- /app/datasets/dish_index_embeddings.npy — NAO ALTERAR

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt
- Usar xhrGet/xhrPost/xhrDelete no Admin.js
- Storage: Cloudflare R2
- Cibi Sana: CLIP ONLY, Gemini HARD LOCK
