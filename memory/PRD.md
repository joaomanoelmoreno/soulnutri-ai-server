# SoulNutri - Product Requirements Document

## Versao Atual: V3.1

## Stack
- Frontend: React (PWA) | Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX) | Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: gTTS 1.35x (gratuito, pt-BR) | DB: MongoDB Atlas | Deploy: Render.com

## Regras Criticas
1. CLIP ONLY no Cibi Sana - Gemini PROIBIDO para identificacao local
2. NAO reinstalar PyTorch no Dockerfile
3. Proporcoes nutricionais: NUNCA dividir igualmente por ingrediente
4. Service Worker MINIMAL - NÃO cacheia nada, NÃO intercepta fetch

## Implementado

### V3.1 (11/Abr/2026)
- P0 FIX: Service Worker reescrito para v10-minimal (sem cache, sem fetch interception)
- P0 FIX: index.js com lifecycle management (hadController, orphan cache cleanup)
- P0 FIX: Backend serve sw.js e manifest.json com no-cache + ETag
- P0 FIX: Middleware reforçado com Pragma: no-cache para HTML

### V3.0 (11/Abr/2026)
- Admin Premium: Liberar/Bloquear funcional (FormData + JSON), com dias de trial
- Admin Premium: Badge Trial/Expirado na lista de usuarios
- TACO proporcoes comerciais reais (nao divide mais por igual)
- 36 fichas nutricionais geradas automaticamente (TACO + proporcoes comerciais)
- Notificacoes rotativas: 14 dicas com links, rotacao por dia do ano
- TTS acelerado 1.35x via pydub
- Alertas alergenos com destaque visual na captura e resultado
- Noticias com links clicaveis
- Botao perfil premium sempre visivel

### V2.7 (11/Abr/2026)
- CLIP <500ms, gTTS gratuito, Trial Premium 7 dias

### V2.6 (11/Abr/2026)
- Resposta lenta corrigida, Login Premium corrigido, Alertas via /ai/enrich

## Endpoints Principais
- POST /ai/identify, /ai/enrich, /ai/tts, /ai/feedback
- POST /premium/login, /notifications/generate
- GET /admin/premium/users
- POST /admin/premium/liberar, /admin/premium/bloquear
- POST /admin/revisar-prato-taco (zero creditos, proporcoes comerciais)
- GET /sw.js (anti-cache, ETag)
- GET /manifest.json (anti-cache)

## Backlog - Tarefas pendentes

### P1
- Landing page premium (aguardando mockup)
- Integracao Stripe para assinaturas

### P2
- Revisao ingredientes/descricao F-Z (usuario fara pelo admin)
- Fichas nutricionais automaticas apos usuario cadastrar ingredientes
- Limpeza imagens Jilo Empanado (usuario fara)
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5700 linhas) e App.js (~4200 linhas)

## Problemas Conhecidos
- Jilo Empanado: fotos contaminadas com Quiabo
- Feijao do Chef: 1 embedding, Gelatina de Uva: 3 embeddings
- 3+ usuarios duplicados "Joao Manoel" no DB (update_many mitiga)
