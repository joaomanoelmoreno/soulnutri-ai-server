# SoulNutri - Product Requirements Document

## Visao Geral
SoulNutri e um agente de nutricao virtual para o restaurante Cibi Sana. Identifica pratos via foto usando IA (CLIP para Cibi Sana, Gemini para locais externos) e fornece informacoes nutricionais personalizadas.

## Versao Atual: V2.5

## Arquitetura
```
/app
├── backend/
│   ├── ai/               # OpenCLIP embedder (NAO ALTERAR logica CLIP)
│   │   ├── embedder.py   # Hibrido: ONNX (deploy) / PyTorch (dev)
│   │   ├── index.py      # Busca por similaridade (Top-K) + timing logs
│   │   └── policy.py     # Analise de resultados CLIP
│   ├── services/
│   │   ├── gemini_flash_service.py  # Fast scan + enrich
│   │   └── tts_service.py          # OpenAI TTS (Alloy/Onyx)
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

## O que foi implementado (Sessao atual - Abril 2026)

### Deploy Render
- [x] Fix yarn.lock, emergentintegrations, memoria RAM (ONNX Runtime)
- [x] Modelo ONNX fp16 (165MB), MONGO_URL strip

### PWA Instalavel
- [x] manifest.json, icones 192/512, SW funcional, cache headers

### Camera Crop Fix
- [x] Captura recorta apenas area da guide-frame (55% x 90%)

### OpenAI TTS (Acessibilidade)
- [x] Endpoint POST /ai/tts (gera MP3 via OpenAI TTS)
- [x] Servico tts_service.py (monta texto descritivo do prato)
- [x] Botao "Ouvir" no resultado do prato (verde, grande, acessivel)
- [x] Vozes testadas: Alloy e Onyx (melhores em portugues)
- [x] Stop/Play toggle, loading state

### Modo Demo
- [x] Pagina /demo com 3 pratos de exemplo
- [x] Detalhe do prato com nutricao, alergenos, ingredientes, beneficios
- [x] TTS funcional no demo (botao "Ouvir")
- [x] CTA para instalar o app

### Revisao Nutricional F-J
- [x] INICIADA - Verificacao de fotos
- [x] CONTAMINACAO ENCONTRADA: Jilo Empanado mostra fotos de Quiabo Empanado
- [x] PAUSADA conforme instrucao do usuario (ele revisara fotos manualmente)
- [x] Pratos sem ingredientes/nutricao no MongoDB (dados faltando)

## Endpoints Principais
- POST /ai/identify - Fast scan (CLIP ou Gemini) com timing logs
- POST /ai/identify-with-ai - Enrichment Premium (background)
- POST /ai/tts - Text-to-Speech (OpenAI TTS, vozes alloy/onyx)
- GET /ai/status - Status do indice

## Credenciais
- Premium User: pin=1234, nome=Teste
- Admin: joaomanoelmoreno / Pqlamz0192

## Backlog

### P0 - Imediato
- Investigar velocidade CLIP (2-3s) — timing logs prontos, aguardando teste do usuario
- Testar crop da camera + TTS no celular

### P1 - Proximo
- Landing page premium (aguardando mockup do usuario)
- Revisao nutricional F-J (usuario revisara fotos primeiro)
- Adicionar dados nutricionais/ingredientes para pratos F-J no MongoDB

### P2 - Futuro
- Stripe para assinatura Premium
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5700 linhas) e App.js (~4000 linhas)

## Problemas Conhecidos
- Jilo Empanado: fotos contaminadas (mostra Quiabo Empanado)
- Feijoada e Frango a Milanesa: sem fotos no dataset
- Feijao do Chef: apenas 1 embedding (pouca confiabilidade)
- Maioria dos pratos F-J sem ingredientes/nutricao no MongoDB
