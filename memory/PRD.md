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
- Log: [HARD LOCK] nos logs do backend para rastreabilidade

## Funcionalidades Implementadas

### Layout Premium vs Gratuito (NOVO 2026-04-06)
- Classe CSS `premium-active` no container principal quando usuario premium logado
- **Premium**: Badge "PREMIUM" dourado no header, cores gold (#f59e0b, #fbbf24, #d97706) em todo o app
  - Header com borda inferior dourada, menu/pratos/sino em gold
  - Resultado: gradiente gold no nome do prato, borda lateral gold
  - Camera com borda dourada
  - Botao scan gold, mini-counter gold, botao "Dieta" gold
  - Sino de notificacoes com badge gold
- **Gratuito**: Sem badge, sem sino, cores padrao (verde/branco), botao "Premium" (convite)
- Estilos em App.css (overrides .premium-active) e Premium.css

### Calibracao CLIP
- Thresholds: >=0.90 alta, >=0.50 media, <0.50 rejeicao
- Colecao `calibration_log` (registro leve, sem upload de imagem)
- POST /api/ai/calibration/log: registro automatico de amostras
- DELETE /api/ai/calibration/clear-all: zerar TODAS as amostras (2026-04-06)
- DELETE /api/ai/calibration/{id}: deletar amostras individuais
- GET /api/ai/calibration: estatisticas, distribuicao, Youden's J
- Aba "Calibracao CLIP" no Admin com dashboard + botao Deletar + botao "Zerar Tudo"

### Notificacoes Push (VALIDADO 2026-04-06)
- POST /api/notifications/generate: gera notificacao diaria personalizada com referencias
- GET /api/notifications/{user_pin}: lista notificacoes com unread count
- POST /api/notifications/{user_pin}/read: marca como lida
- NotificationPanel.jsx: painel deslizante com icones, prioridades, referencias clicaveis

### Upload Fotos (FIX 2026-04-06)
- Dataset exibe nomes em Title Case (ex: "Abobora ao Curry") nao mais slugs com hifens
- Corrigido `get_all_dishes_stats()` para usar campo `name` ao inves de `slug`
- Corrigido slug com underscore: arroz_7_graos -> arroz-7-graos-c-ou-s-frutas-secas
- Mescladas 3 duplicatas (Bolinho de Bacalhau, Frango ao Creme de Limao, Sobrecoxa ao Tandoori)
- Upload ZIP funcional no admin

### Dados Nutricionais
- 196 pratos com dados nutricionais
- Pratos A-E todos com dados completos
- 2 pratos preenchidos: Ceviche de Banana da Terra, Espaguete de Abobrinha ao Pesto (2026-04-06)
- Fonte: TACO + Gemini Flash

### Outras funcionalidades
- Identificacao de pratos via camera/foto (PWA)
- Ficha nutricional detalhada com dados TACO (255 mapeamentos)
- Sistema premium com pin de acesso
- Nutri News (feed de noticias IA)
- Sistema de engajamento (gamificacao)
- Painel admin completo com moderacao
- Fluxo de feedback com fila de moderacao
- Design "Gourmet Dark Mode"
- Normalizacao iOS/Android (1024px, 85% JPEG)
- Padronizacao de nomes (Title Case)

## Estado Atual
- 196 pratos, todos com embeddings IA (ViT-B-16)
- 4389+ fotos no Cloudflare R2
- 255 mapeamentos TACO
- Precisao teste: 100% (20/20 pratos, 0 falsos positivos)
- Calibracao zerada para novos testes (2026-04-06)
- 23 pratos com poucas fotos (<=5) - necessitam mais fotos

## Pratos com Poucas Fotos (<=5)
- [CRITICO] Ceviche de Banana da Terra: 1
- [CRITICO] Sobrecoxa ao Tandoori: 1+28 (merged)
- [CRITICO] Frango ao Creme de Limao: 2+50 (merged)  
- [BAIXO] Bolinho de Bacalhau: 3+38 (merged)
- ... mais 19 pratos com 0-5 fotos

## Upcoming Tasks
- (P0) Usuario testar fotos reais no buffet com modelo ViT-B-16
- (P2) Revisao nutricional pratos F-Z

## Future Tasks
- (P1) Comercializacao Apple Store / Google Play
- (P1) Integracao Stripe para premium
- (P2) Refatorar server.py (5K+) e Admin.js (3K+)
- (P2) Upload ZIP verificar se esta funcionando

## REGRA CRITICA: LOCK do Pipeline ViT-B-16 (2026-04-05)
- /app/backend/ai/embedder.py — NAO ALTERAR
- /app/backend/ai/index.py — NAO ALTERAR
- /app/datasets/dish_index.json — NAO ALTERAR
- /app/datasets/dish_index_embeddings.npy — NAO ALTERAR
- Modelo: ViT-B-16 DataComp.XL, dimensao 512, validado 100%

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt (iframe bloqueia)
- Imagens 2-4MB - sempre usar thumbnails no admin
- Usar xhrGet/xhrPost/xhrDelete no Admin.js
- Storage definitivo: Cloudflare R2
- Cibi Sana: CLIP ONLY, Gemini HARD LOCK
- Fonte de verdade para fotos: colecao dish_storage (R2), NAO disco local
