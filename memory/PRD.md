# SoulNutri - Product Requirements Document

## Versao Atual: V2.8

## Visao Geral
SoulNutri e um agente de nutricao virtual para o restaurante Cibi Sana. Identifica pratos via foto usando IA (CLIP/ONNX para Cibi Sana, Gemini para locais externos).

## Arquitetura
```
/app
├── backend/
│   ├── ai/               # embedder.py (ONNX), index.py (CLIP search + get_index_info)
│   ├── services/         # gemini_flash_service.py, tts_service.py (gTTS), alerts_service.py
│   ├── scripts/          # export_onnx.py (build-time)
│   └── server.py         # FastAPI (~5700 linhas)
├── frontend/
│   ├── public/           # sw.js, manifest.json, icons
│   └── src/
│       ├── App.js        # React Principal (~4100 linhas)
│       ├── Admin.js      # Painel Admin (~3600 linhas)
│       ├── Demo.jsx      # Modo Demo
│       └── index.js      # Rotas
├── datasets/             # CLIP index (2994 itens, 191 pratos)
└── Dockerfile            # Build Render (ONNX export)
```

## Stack
- Frontend: React (PWA), Service Worker
- Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX Runtime)
- IA Externa: Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: gTTS (gratuito, voz nativa pt-BR)
- DB: MongoDB Atlas
- Deploy: Render.com (Starter, 512MB RAM)

## Regras Criticas
1. CLIP ONLY no Cibi Sana - Gemini PROIBIDO para identificacao local
2. NAO reinstalar PyTorch no Dockerfile de producao
3. ViT-B-16 DataComp XL travado

## Implementado

### V2.8 (11/Abr/2026)
- Admin: Todos 360 pratos visiveis (CLIP index + DB merged)
- Admin: Filtro "Sem ingredientes" para revisao rapida (168 pratos pendentes)
- Admin: Pratos CLIP-only aparecem no painel para edicao
- Admin: Premium update_many para lidar com duplicatas

### V2.7 (11/Abr/2026)
- CLIP speed: 384ms sem premium, ~500ms com premium (era 8-9s)
- TTS: gTTS gratuito, voz brasileira nativa sem sotaque
- Trial Premium: 7 dias gratis, expiracao automatica
- Admin Premium: Liberar/Bloquear permanente

### V2.6 (11/Abr/2026)
- Resposta lenta /ai/identify corrigida (LLM movido para /ai/enrich)
- Login Premium travado (localStorage limpo)
- Alertas/Noticias via /ai/enrich
- Feedback 500, TTS expandido, regex whitespace

### Anteriores
- Deploy Render ONNX fp16, PWA, Camera Crop, Modo Demo

## Endpoints Principais
- POST /ai/identify - Fast scan (<500ms Cibi Sana, <2s Gemini)
- POST /ai/enrich - Enrichment background (beneficios, riscos, alertas, nutrition, noticias)
- POST /ai/tts - gTTS pt-BR (gratuito)
- POST /ai/feedback - Feedback calibracao
- POST /premium/login - Login Premium (verifica trial 7 dias)
- GET /admin/dishes-full - Lista TODOS pratos (DB + CLIP index)
- GET /admin/premium/users - Lista usuarios premium
- POST /admin/premium/liberar / bloquear - Gestao premium
- POST /admin/revisar-prato-taco - Revisao nutricional gratuita

## Backlog

### P1
- Landing page premium (aguardando mockup)
- Integracao Stripe para assinaturas
- Fichas nutricionais para 4 pratos faltantes (Feijao Branco, Gelatina de Uva, Guacamole, Jilo Empanado)

### P2
- Revisao nutricional F-Z: 168 pratos sem ingredientes (usuario fara pelo admin)
- Limpeza de imagens: Jilo Empanado (usuario fara manualmente)
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py e App.js

## Problemas Conhecidos
- Jilo Empanado: fotos contaminadas com Quiabo
- Feijao do Chef: 1 embedding, Gelatina de Uva: 3 embeddings
- Google API Key 403 (fallback Emergent LLM Key funciona)
- 3 usuarios duplicados "Joao Manoel" no DB
