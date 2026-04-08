# SoulNutri - Product Requirements Document
## Versao 2.2 — GPS Contínuo + Meal Tracking (2026-04-08)

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
- Deploy: Render (Docker) — Unificado (FastAPI serve React build via SPAStaticFiles)

## Regra de Negocio Critica
- Cibi Sana: APENAS OpenCLIP. Gemini HARD LOCK.
- Externo: APENAS Gemini. CLIP DESLIGADO.

## Bifurcacao GPS V2.2 (ATUALIZADO 2026-04-08)
- Coordenadas Cibi Sana: -23.0373642, -46.9767934
- Raio: 100m + margem GPS 50m
- GPS CONTÍNUO via watchPosition (atualiza em tempo real)
- Ao mudar de local: prato atual limpo automaticamente, nova refeição inicia
- Badge clicável no header para trocar manualmente

## Meal Tracking V2.2 (IMPLEMENTADO 2026-04-08)
- finishPlate() agora registra no histórico Premium (bug fix)
- addItemToPlate() e finishPlate() incluem campo source (clip/gemini_flash)
- Backend log-meal aceita source parameter
- Refeições Gemini: mesmos recursos Premium (alertas, notificações, dicas, etc.)
- Imagens Gemini NÃO salvas no dish_storage/embeddings

## Confidence Scores
- ALTA: >= 90% (0.90)
- MÉDIA: 50% a 89% (0.50 a 0.89)
- BAIXA: < 50% (0.50)

## Deploy Unificado (FUNCIONANDO 2026-04-08)
- SPAStaticFiles serve React build com fallback index.html
- Render: soulnutri-v3wd.onrender.com (live)
- Domínio: soulnutri.app.br (configuração pendente DNS)

## Completed
- [x] Deploy unificado no Render (SPAStaticFiles)
- [x] Bifurcação GPS: Cibi Sana (CLIP) vs Externo (Gemini)
- [x] GPS contínuo (watchPosition) — auto-switch entre locais
- [x] finishPlate() registra no histórico (bug fix)
- [x] Campo source (clip/gemini) no meal tracking
- [x] Documento SOULNUTRI_CONFIGURACOES.docx para engenharia
- [x] Tema Obsidian Black Card
- [x] Notificações Push Premium
- [x] Fontes Nutricionais TACO/USDA

## Upcoming Tasks
- (P0) Configurar domínio soulnutri.app.br no Render + Cloudflare DNS
- (P0) Sincronizar código GPS/bifurcação para o GitHub/Render
- (P0) Testar fluxo completo no Render com fotos reais

## Future/Backlog
- (P1) Landing page onboarding premium (trial 7 dias)
- (P1) Stripe + App Store/Google Play
- (P2) Revisão nutricional pratos F-Z
- (P2) Endpoint upload ZIP admin
- (P3) Refatorar server.py e Admin.js

## LOCK ViT-B-16 — NAO ALTERAR embedder.py, index.py
