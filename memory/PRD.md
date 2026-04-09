# SoulNutri - Product Requirements Document
## Versao 2.3 — Premium Features Fix (2026-04-09)

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

## Fluxo Premium (ATUALIZADO 2026-04-09)
### Fase Buffet/Servindo (resposta rapida):
- Identificacao do prato + alertas criticos (alergenos, ingredientes)
- Resposta em <0.5s

### Fase Mesa (refeicao finalizada):
- Todas as features Premium: beneficios, riscos, noticias, curiosidades, combinacoes
- Ingredientes detalhados, beneficio principal, alerta saude
- Mito/Verdade educacional, dica do chef
- Alertas personalizados baseados no perfil

## Bifurcacao GPS V2.2
- Coordenadas Cibi Sana: -23.0373642, -46.9767934
- Raio: 100m + margem GPS 50m
- GPS CONTINUO via watchPosition (atualiza em tempo real)

## Meal Tracking V2.2
- finishPlate() registra no historico Premium
- addItemToPlate() e finishPlate() incluem campo source (clip/gemini_flash)
- Backend log-meal aceita source parameter

## Confidence Scores
- ALTA: >= 90% (0.90)
- MEDIA: 50% a 89% (0.50 a 0.89)
- BAIXA: < 50% (0.50)

## Deploy Unificado
- SPAStaticFiles serve React build com fallback index.html
- Render: soulnutri-v3wd.onrender.com (live)
- Dominio: soulnutri.app.br (configuracao pendente DNS)

## Completed
- [x] Deploy unificado no Render (SPAStaticFiles)
- [x] Bifurcacao GPS: Cibi Sana (CLIP) vs Externo (Gemini)
- [x] GPS continuo (watchPosition)
- [x] finishPlate() registra no historico (bug fix)
- [x] Campo source (clip/gemini) no meal tracking
- [x] Documento SOULNUTRI_CONFIGURACOES.docx para engenharia
- [x] Tema Obsidian Black Card
- [x] Notificacoes Push Premium
- [x] Fontes Nutricionais TACO/USDA
- [x] **FIX P0**: Features Premium na UI (ingredientes, beneficios, riscos, curiosidade, combinacoes) — 2026-04-09
  - Gemini Flash prompt agora retorna dados ricos (ing, benef, riscos, curios, combo)
  - Backend mapeia todos os campos para a response API
  - Frontend armazena dados Premium nos plateItems
  - Mesa view exibe todas as secoes Premium consolidadas
  - Alertas de alergenos corrigidos para funcionar sem funcoes faltantes

## Upcoming Tasks
- (P0) Sincronizar codigo para GitHub/Render (instruir usuario: "Save to GitHub")
- (P0) Testar fluxo completo no Render com fotos reais
- (P0) Configurar dominio soulnutri.app.br no Render + Cloudflare DNS

## Future/Backlog
- (P1) Landing page onboarding premium (trial 7 dias)
- (P1) Stripe + App Store/Google Play
- (P2) Revisao nutricional pratos F-Z
- (P2) Endpoint upload ZIP admin
- (P3) Refatorar server.py e Admin.js

## LOCK ViT-B-16 — NAO ALTERAR embedder.py, index.py
