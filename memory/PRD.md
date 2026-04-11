# SoulNutri - Product Requirements Document

## Versao Atual: V3.1

## Stack
- Frontend: React (PWA) | Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX) | Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: gTTS 1.35x (gratuito, pt-BR) | DB: MongoDB Atlas | Deploy: Render.com

## REGRAS IMUTÁVEIS → /app/memory/REGRAS_IMUTAVEIS.md
Arquivo criado com todas as regras que NUNCA podem ser violadas por nenhum agente.

## Implementado

### V3.1 (11/Abr/2026)
- P0 FIX: Service Worker reescrito para v10-minimal (sem cache, sem fetch interception)
- P0 FIX: index.js com lifecycle management (hadController, orphan cache cleanup)
- P0 FIX: Backend serve sw.js e manifest.json com no-cache + ETag
- FIX: Race condition do enrich - callback agora atualiza TANTO result QUANTO plateItems
- FIX: Botao TTS "Ouvir resumo do prato" adicionado ao Prato Completo (mesa view)
- FIX: Indicador visual "Carregando conteudo Premium..." no mesa view
- FIX: setShowPremiumModal corrigido para setShowPremium('login')
- REGRAS_IMUTAVEIS.md criado para proteger requisitos fundamentais

### V3.0 (11/Abr/2026)
- Admin Premium: Liberar/Bloquear funcional (FormData + JSON), com dias de trial
- TACO proporcoes comerciais reais
- 36 fichas nutricionais geradas automaticamente
- Notificacoes rotativas: 14 dicas com links
- TTS acelerado 1.35x via pydub
- Alertas alergenos com destaque visual
- Noticias com links clicaveis

### V2.7 (11/Abr/2026)
- CLIP <500ms, gTTS gratuito, Trial Premium 7 dias

## Endpoints Principais
- POST /ai/identify (CLIP <500ms cibi_sana | Gemini <2.5s externo)
- POST /ai/enrich (background, Gemini, enriquecimento premium)
- POST /ai/tts (gTTS gratuito, 1.35x)
- POST /premium/login
- GET /sw.js, /manifest.json (anti-cache)

## Backlog

### P1
- Landing page premium (aguardando mockup)
- Integracao Stripe para assinaturas

### P2
- Revisao ingredientes/descricao F-Z (usuario fara pelo admin)
- Fichas nutricionais automaticas apos cadastro
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5700 linhas) e App.js (~4300 linhas)

## Problemas Conhecidos
- Jilo Empanado: fotos contaminadas com Quiabo
- 3+ usuarios duplicados "Joao Manoel" no DB (update_many mitiga)
