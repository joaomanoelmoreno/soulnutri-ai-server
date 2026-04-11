# SoulNutri - Product Requirements Document

## Visao Geral
SoulNutri e um agente de nutricao virtual para o restaurante Cibi Sana. Identifica pratos via foto usando IA (CLIP para Cibi Sana, Gemini para locais externos) e fornece informacoes nutricionais personalizadas.

## Versao Atual: V2.6

## Arquitetura
```
/app
├── backend/
│   ├── ai/               # OpenCLIP embedder (NAO ALTERAR logica CLIP)
│   │   ├── embedder.py   # Hibrido: ONNX (deploy) / PyTorch (dev)
│   │   ├── index.py      # Busca por similaridade (Top-K) + timing logs
│   │   └── policy.py     # Analise de resultados CLIP
│   ├── services/
│   │   ├── gemini_flash_service.py  # Fast scan + enrich (fix: send_message)
│   │   ├── tts_service.py          # OpenAI TTS (Alloy/Onyx) - EXPANDIDO
│   │   └── alerts_service.py       # Alertas LLM (agora via /ai/enrich)
│   ├── scripts/          # export_onnx.py (build-time ONNX export)
│   └── server.py         # Endpoints FastAPI (~5700 linhas) + timing logs
├── frontend/
│   ├── public/           # sw.js (PWA), manifest.json, icons
│   └── src/
│       ├── App.js        # Core app (~4000 linhas)
│       ├── Demo.jsx      # Modo Demo (/demo)
│       └── index.js      # Rotas: /, /admin, /demo
├── datasets/             # Embeddings pre-calculados (2994 itens, 191 pratos)
└── Dockerfile            # Build unificado para Render (ONNX export)
```

## Stack Tecnica
- Frontend: React (PWA), Service Worker com cache network-first
- Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX Runtime no deploy, PyTorch no dev)
- IA Externa: Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: OpenAI TTS (vozes Alloy/Onyx, via Emergent LLM Key)
- DB: MongoDB Atlas
- Deploy: Render.com ($8/mes Starter, 512MB RAM)
- Dominio: soulnutri.app.br

## Regras Criticas (HARD LOCK)
1. CLIP ONLY no Cibi Sana - Gemini PROIBIDO para identificacao local
2. NAO ALTERAR embedder.py/index.py logica de reconhecimento sem autorizacao
3. ViT-B-16 DataComp XL travado - nao mudar modelo

## O que foi implementado

### Deploy Render
- [x] Fix yarn.lock, emergentintegrations, memoria RAM (ONNX Runtime)
- [x] Modelo ONNX fp16 (165MB), MONGO_URL strip

### PWA Instalavel
- [x] manifest.json, icones 192/512, SW funcional, cache headers

### Camera Crop Fix
- [x] Captura recorta apenas area da guide-frame (55% x 90%)

### OpenAI TTS (Acessibilidade)
- [x] Endpoint POST /ai/tts (gera MP3 via OpenAI TTS)
- [x] Servico tts_service.py (texto descritivo EXPANDIDO do prato)
- [x] Botao "Ouvir" no resultado do prato (verde, grande, acessivel)
- [x] Vozes testadas: Alloy e Onyx (melhores em portugues)
- [x] Stop/Play toggle, loading state
- [x] TTS expandido: beneficios, riscos, ingredientes, alertas, curiosidades, noticias, verdade/mito

### Modo Demo
- [x] Pagina /demo com 3 pratos de exemplo
- [x] Detalhe do prato com nutricao, alergenos, ingredientes, beneficios
- [x] TTS funcional no demo (botao "Ouvir")
- [x] CTA para instalar o app

### Correcoes V2.6 (11/Abr/2026)
- [x] P0: Resposta lenta /ai/identify (8-9s -> <2s) - LLM movido para /ai/enrich background
- [x] P0: Login Premium travado com PIN obsoleto - localStorage limpo automaticamente
- [x] P1: Alertas/Noticias nao gerados - corrigido has_alert bug, alertas movidos para /ai/enrich
- [x] P1: Feedback 500 (/app/datasets/organized) - diretorio criado programaticamente
- [x] P2: TTS expandido com conteudo completo
- [x] Fix: regex whitespace-tolerant para nomes com espaco no DB
- [x] Fix: send_message_async -> send_message em gemini_flash_service.py

### Revisao Nutricional F-J
- [x] INICIADA - Verificacao de fotos
- [x] CONTAMINACAO ENCONTRADA: Jilo Empanado mostra fotos de Quiabo Empanado
- [x] PAUSADA conforme instrucao do usuario (ele revisara fotos manualmente)

## Endpoints Principais
- POST /ai/identify - Fast scan (CLIP ou Gemini) - retorno rapido <2s
- POST /ai/enrich - Enrichment Premium em background (beneficios, riscos, alertas, noticias)
- POST /ai/tts - Text-to-Speech (OpenAI TTS, vozes alloy/onyx)
- POST /ai/feedback - Feedback de calibracao (salva imagem + MongoDB)
- POST /premium/login - Login Premium (PIN + Nome)
- GET /ai/status - Status do indice

## Credenciais
- Premium User: pin=2212, nome=Joao Manoel (espaco no final no DB)
- Admin: joaomanoelmoreno / Pqlamz0192

## Backlog

### P1 - Proximo
- Landing page premium (aguardando mockup do usuario)
- Integracao Stripe para assinaturas
- Revisao nutricional F-J (usuario revisara fotos primeiro)

### P2 - Futuro
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5700 linhas) e App.js (~4000 linhas)

## Problemas Conhecidos
- Jilo Empanado: fotos contaminadas (mostra Quiabo Empanado)
- Feijoada e Frango a Milanesa: sem fotos no dataset
- Feijao do Chef: apenas 1 embedding (pouca confiabilidade)
- Maioria dos pratos F-J sem ingredientes/nutricao no MongoDB
- Google API Key pode estar expirada (403) - fallback via Emergent LLM Key funciona
