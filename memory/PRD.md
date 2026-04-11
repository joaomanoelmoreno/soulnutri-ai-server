# SoulNutri - Product Requirements Document

## Visao Geral
SoulNutri e um agente de nutricao virtual para o restaurante Cibi Sana. Identifica pratos via foto usando IA (CLIP/ONNX para Cibi Sana, Gemini para locais externos) e fornece informacoes nutricionais personalizadas.

## Versao Atual: V2.7

## Arquitetura
```
/app
├── backend/
│   ├── ai/               # OpenCLIP embedder (ONNX deploy / PyTorch dev)
│   ├── services/
│   │   ├── gemini_flash_service.py  # Fast scan + enrich
│   │   ├── tts_service.py          # gTTS (gratuito, pt-BR nativo)
│   │   └── alerts_service.py       # Alertas LLM via /ai/enrich
│   ├── scripts/          # export_onnx.py (build-time)
│   └── server.py         # FastAPI (~5700 linhas)
├── frontend/
│   ├── public/           # sw.js, manifest.json, icons
│   └── src/
│       ├── App.js        # React Principal (~4000 linhas)
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

### V2.7 (11/Abr/2026)
- CLIP speed: 384ms sem premium, ~500ms com premium (era 8-9s)
- TTS: Trocado OpenAI por gTTS (gratuito, voz brasileira nativa, sem sotaque)
- Trial Premium: 7 dias gratis para novos usuarios, expiracao automatica
- Admin Premium: Liberar/Bloquear permanente via /admin/premium/
- Admin endpoints usam update_many para lidar com duplicatas
- Nutrition data carrega via /ai/enrich em background (nao bloqueia CLIP)

### V2.6 (11/Abr/2026)
- Resposta lenta /ai/identify corrigida (LLM movido para /ai/enrich)
- Login Premium travado corrigido (localStorage limpo automaticamente)
- Alertas/Noticias gerados via /ai/enrich (fix has_alert)
- Feedback 500 corrigido (mkdir /app/datasets/organized)
- TTS expandido (beneficios, riscos, ingredientes, alertas, curiosidades, noticias)
- Regex whitespace-tolerant para nomes com espaco no DB
- Fix send_message_async -> send_message

### Anteriores
- Deploy Render ONNX fp16 (300MB RAM)
- PWA instalavel, Camera Crop, Modo Demo
- OpenAI TTS original (substituido por gTTS)

## Endpoints Principais
- POST /ai/identify - Fast scan (<500ms Cibi Sana, <2s Gemini)
- POST /ai/enrich - Enrichment Premium background (beneficios, riscos, alertas, nutrition, noticias)
- POST /ai/tts - Text-to-Speech (gTTS pt-BR, gratuito)
- POST /ai/feedback - Feedback de calibracao
- POST /premium/login - Login Premium (verifica trial 7 dias)
- GET /admin/premium/users - Lista usuarios com status premium
- POST /admin/premium/liberar - Libera premium permanente
- POST /admin/premium/bloquear - Bloqueia premium

## Backlog

### P0 - Nenhum

### P1 - Proximo
- Landing page premium (aguardando mockup)
- Integracao Stripe para assinaturas
- Fichas nutricionais para 4 pratos faltantes (Feijao Branco, Gelatina de Uva, Guacamole, Jilo Empanado)

### P2 - Futuro
- Revisao nutricional F-J: ingredientes para 28 pratos (usuario fara manualmente)
- Limpeza de imagens contaminadas: Jilo Empanado (usuario fara manualmente)
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5700 linhas) e App.js (~4000 linhas)

## Problemas Conhecidos
- Jilo Empanado: fotos contaminadas com Quiabo (limpeza manual pendente)
- Feijao do Chef: apenas 1 embedding
- Gelatina de Uva: apenas 3 embeddings
- Google API Key pode estar 403 (fallback Emergent LLM Key funciona)
- 3 usuarios duplicados "Joao Manoel" no DB (update_many mitiga)
