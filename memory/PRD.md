# SoulNutri - Product Requirements Document
## Versao 2.0 — ViT-B-16 Stable (2026-04-05)

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

## Regra de Negocio Critica: Hard Lock Cibi Sana
- Cibi Sana: APENAS OpenCLIP. Gemini HARD LOCK.

## Layout Premium Obsidian / Black Card (2026-04-06)
Paleta coerente em TODAS as telas premium:
- Fundo: #080808 (preto puro Obsidian)
- Primary gold: #d4af37 (dourado fosco)
- Light gold: #e8d48b (champagne)
- Dark gold: #b8960f (ouro escuro)
- Medium gold: #c5a028 (ouro medio)
- PROIBIDO em premium: #3b82f6 (azul), #22c55e (verde), #f59e0b (amber)
- Vermelho #ef4444 PERMITIDO apenas para alertas de perigo

Telas cobertas:
- Scan (main screen): badge PREMIUM, botoes Foto/Gallery/Limpar gold, sino gold
- Dieta (counter): tabs Hoje/Semana/Perfil/Dashboard todos em gold, anel calorico gold
- Dashboard Premium: tabs, periodo selector, cards, alertas - tudo em gold sobre preto
- Perfil: botao Editar gold, form com bordas gold
- Formulario registro/login: inputs, labels, botoes gold

Versao Gratuita: Fundo azul navy #0f172a, sem badge, sem sino, cores padrao

## Calibracao CLIP
- DELETE /api/ai/calibration/clear-all: zerar TODAS amostras
- Botao "Zerar Tudo" no Admin

## Notificacoes Push (VALIDADO)
- Endpoints: generate, list, mark-read
- NotificationPanel.jsx com referencias clicaveis

## Upload Fotos (FIX 2026-04-06)
- Nomes em Title Case (fix get_all_dishes_stats)
- Slug underscore corrigido, 3 duplicatas mescladas
- 196 pratos no dish_storage

## Pratos com Poucas Fotos (<=5) - 19 pratos
- [SEM FOTOS] Ceviche de Banana da Terra: 0
- [CRITICO] Beringela a Parmegiana, Espaguete Abobrinha Pesto, Polenta Ragu, Risoto Alho Poro: 1
- [BAIXO] Maminha Gorgonzola: 2
- [BAIXO] Carne Moida Ovo, Doce Banana Vegano, Gelatina Uva: 3
- [ALERTA] 10 pratos com 4 fotos cada

## Estado Atual
- 196 pratos, embeddings ViT-B-16
- 4389+ fotos R2, 255 mapeamentos TACO
- Precisao: 100% (20/20, 0 falsos positivos)

## Upcoming Tasks
- (P0) Testar fotos reais no buffet com ViT-B-16
- (P2) Revisao nutricional pratos F-Z

## Future/Backlog
- (P1) Landing page de onboarding premium (trial 7 dias)
- (P1) Comercializacao Apple Store / Google Play
- (P1) Integracao Stripe
- (P2) Refatorar server.py (5K+) e Admin.js (3K+)

## REGRA CRITICA: LOCK ViT-B-16
- embedder.py, index.py, dish_index.json, embeddings.npy: NAO ALTERAR

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt
- Usar xhrGet/xhrPost/xhrDelete no Admin.js
- Storage: Cloudflare R2 | Cibi Sana: CLIP ONLY
