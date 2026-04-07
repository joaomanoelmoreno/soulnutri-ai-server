# SoulNutri - Product Requirements Document
## Versao 2.1 — Bifurcacao GPS + Deploy Unificado (2026-04-07)

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao.

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192
- Premium test user: pin=1234, nome=Teste SoulNutri

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-16, DataComp.XL) para embedding de imagens
- Storage: Cloudflare R2 (bucket: soulnutri-images) - 4389 fotos
- DB: MongoDB Atlas
- Deploy: Unificado (FastAPI serve React build via catch-all SPA)

## Regra de Negocio Critica: Hard Lock Cibi Sana
- Cibi Sana: APENAS OpenCLIP. Gemini HARD LOCK.

## Bifurcacao por Localizacao V2.1 (IMPLEMENTADO 2026-04-07)
Coordenadas Cibi Sana: -23.0373642, -46.9767934 (Av Independencia 1222, Vinhedo SP)
Raio de deteccao: 100 metros (+ margem de precisao GPS ate 50m)
- DENTRO Cibi Sana (GPS ou manual): CLIP ONLY - pratos calibrados, Gemini bloqueado
- FORA Cibi Sana: GEMINI ONLY - CLIP desligado (evita poluicao de pratos Cibi Sana)
- GPS negado: Prompt manual "Onde voce esta?" com duas opcoes
- Indicador visual no header: badge dourado (Cibi Sana) ou azul (Externo)
- Badge clicavel para trocar localizacao a qualquer momento
- Backend: server.py linhas 546-640 reestruturado para bifurcacao limpa
- Frontend: 3 pontos de fd.append("restaurant") agora usam getRestaurantValue()

## Layout Premium Obsidian / Black Card (2026-04-06)
Paleta coerente em TODAS as telas premium:
- Fundo: #080808 (preto puro Obsidian)
- Primary gold: #d4af37 (dourado fosco)
- Light gold: #e8d48b (champagne)
- Dark gold: #b8960f (ouro escuro)
- Medium gold: #c5a028 (ouro medio)
- PROIBIDO em premium: #3b82f6 (azul), #22c55e (verde), #f59e0b (amber)
- Vermelho #ef4444 PERMITIDO apenas para alertas de perigo

Versao Gratuita: Fundo azul navy #0f172a, sem badge, sem sino, cores padrao

## Deploy Unificado (IMPLEMENTADO 2026-04-07)
- FastAPI serve React build via catch-all route
- Dockerfile + render.yaml + .dockerignore criados
- DEPLOY_RENDER.md: guia passo-a-passo completo

## Calibracao CLIP
- DELETE /api/ai/calibration/clear-all: zerar TODAS amostras (requer ?confirm=true)

## Notificacoes Push (VALIDADO)
- Endpoints: generate, list, mark-read

## Estado Atual
- 196 pratos, embeddings ViT-B-16
- 4389+ fotos R2, 255 mapeamentos TACO
- Precisao: 100% (20/20, 0 falsos positivos)

## Completed
- [x] Bifurcacao GPS: Cibi Sana (CLIP) vs Externo (Gemini)
- [x] Deploy unificado FastAPI+React (server.py catch-all SPA)
- [x] Dockerfile, render.yaml, .dockerignore
- [x] Tema Obsidian Black Card
- [x] Notificacoes Push Premium
- [x] Fontes Nutricionais TACO/USDA
- [x] Endpoint seguro clear-all (confirm=true)
- [x] 196 pratos unificados no dish_storage

## Upcoming Tasks
- (P0) Fazer push para GitHub e deploy no Render
- (P0) Testar fotos reais no buffet com ViT-B-16 (modo Cibi Sana)
- (P0) Testar reconhecimento Gemini fora do Cibi Sana
- (P2) Revisao nutricional pratos F-Z

## Future/Backlog
- (P1) Landing page de onboarding premium (trial 7 dias)
- (P1) Comercializacao Apple Store / Google Play
- (P1) Integracao Stripe
- (P2) Endpoint upload ZIP no admin
- (P3) Refatorar server.py (5K+) e Admin.js (3K+)

## REGRA CRITICA: LOCK ViT-B-16
- embedder.py, index.py, dish_index.json, embeddings.npy: NAO ALTERAR

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt
- Usar xhrGet/xhrPost/xhrDelete no Admin.js
- Storage: Cloudflare R2 | Cibi Sana: CLIP ONLY
