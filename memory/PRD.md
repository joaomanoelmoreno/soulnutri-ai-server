# SoulNutri - Product Requirements Document

## Versao Atual: V2.9

## Visao Geral
SoulNutri e um agente de nutricao virtual para o restaurante Cibi Sana.

## Stack
- Frontend: React (PWA)
- Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX Runtime)
- IA Externa: Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: gTTS 1.35x (gratuito, voz nativa pt-BR)
- DB: MongoDB Atlas
- Deploy: Render.com (Starter, 512MB RAM)

## Implementado

### V2.9 (11/Abr/2026)
- TTS acelerado para 1.35x via pydub (usuario aprovou)
- Notificacoes rotativas: 14 dicas com links, rotacao por dia do ano (nunca repete no mesmo dia)
- Alertas alergenos com destaque visual na tela de captura (scanner overlay) e resultado
- Alertas de historico com destaque no resultado
- Noticias com links clicaveis (suporta string e {texto, url})
- Botao de perfil premium sempre visivel (fallback quando mini-counter nao aparece)

### V2.8 (11/Abr/2026)
- Admin revertido para 200 pratos (CLIP index nao mais injetado)

### V2.7 (11/Abr/2026)
- CLIP speed: 384ms sem premium, ~500ms com premium
- TTS: gTTS gratuito, voz brasileira nativa
- Trial Premium: 7 dias gratis, expiracao automatica
- Admin Premium: Liberar/Bloquear permanente

### V2.6 (11/Abr/2026)
- Resposta lenta corrigida, Login Premium corrigido
- Alertas/Noticias via /ai/enrich, Feedback 500 corrigido
- TTS expandido, regex whitespace

## Endpoints Principais
- POST /ai/identify - Fast scan (<500ms Cibi Sana)
- POST /ai/enrich - Enrichment background (beneficios, riscos, alertas, nutrition, noticias)
- POST /ai/tts - gTTS pt-BR 1.35x (gratuito)
- POST /notifications/generate - Notificacao rotativa do dia
- GET /notifications/{pin} - Lista notificacoes do usuario
- POST /premium/login - Login Premium (trial 7 dias)
- GET /admin/premium/users - Lista usuarios premium
- POST /admin/premium/liberar / bloquear - Gestao premium

## Backlog

### P1
- Landing page premium (aguardando mockup)
- Integracao Stripe para assinaturas
- Fichas nutricionais 4 pratos faltantes

### P2
- Revisao nutricional F-Z (usuario fara pelo admin)
- Limpeza imagens Jilo Empanado
- Google Play / Apple Store
- Refatorar server.py e App.js
