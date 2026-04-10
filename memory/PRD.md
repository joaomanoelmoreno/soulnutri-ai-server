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
│   ├── services/         # gemini_flash_service.py (fast scan + enrich)
│   ├── scripts/          # export_onnx.py (build-time ONNX export)
│   └── server.py         # Endpoints FastAPI (~5700 linhas) + timing logs
├── frontend/
│   ├── public/           # sw.js (PWA), manifest.json, icons
│   └── src/
│       └── App.js        # Core app (~4000 linhas)
├── datasets/             # Embeddings pre-calculados (2994 itens, 191 pratos)
└── Dockerfile            # Build unificado para Render (ONNX export)
```

## Stack Tecnica
- Frontend: React (PWA), Service Worker com cache network-first
- Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX Runtime no deploy, PyTorch no dev)
- IA Externa: Gemini 2.5 Flash Lite (Emergent LLM Key)
- DB: MongoDB Atlas
- Deploy: Render.com ($8/mes Starter, 512MB RAM)
- Dominio: soulnutri.app.br

## Regras Criticas (HARD LOCK)
1. CLIP ONLY no Cibi Sana - Gemini PROIBIDO para identificacao local
2. NAO ALTERAR embedder.py/index.py logica de reconhecimento sem autorizacao
3. ViT-B-16 DataComp XL travado - nao mudar modelo

## O que foi implementado

### Deploy Render (Abril 2026)
- [x] Fix yarn.lock nao rastreado pelo Git
- [x] Fix emergentintegrations (extra-index-url no pip)
- [x] Fix memoria RAM: ONNX Runtime substitui PyTorch no deploy (300MB vs 610MB+)
- [x] Script export_onnx.py para conversao durante Docker build
- [x] Modelo ONNX fp16 (165MB) - embeddings identicos ao PyTorch (cosine=0.9999)
- [x] Fix MONGO_URL com newline (.replace + .strip)
- [x] Variaveis de ambiente configuradas no Render
- [x] Git history limpo (arquivos grandes removidos)

### PWA Instalavel
- [x] manifest.json com name, short_name, start_url, display=standalone
- [x] Icones corretos: 192x192 e 512x512 (quadrados, gerados do logo)
- [x] Service Worker funcional (network-first + cache)
- [x] index.js registra SW (antes estava desregistrando)
- [x] Cache headers: sw.js e manifest.json com no-cache

### Bug Fix: Camera Crop (Abril 2026)
- [x] Captura agora faz CROP real baseado na guide-frame (55% x 90%)
- [x] Calcula object-fit:cover para converter coordenadas do video
- [x] Aplica tanto no toque manual quanto no scanner continuo
- [x] Evita capturar pratos vizinhos fora da moldura

### Timing Logs para Diagnostico CLIP
- [x] Log de upload/read time + tamanho da imagem
- [x] Log de embedding time (ONNX ou PyTorch)
- [x] Log de similaridade time
- [x] Log de CLIP search total

### Otimizacoes (Sessao anterior)
- [x] Gemini Fast Scan (~1.1s) + Enrichment em background
- [x] CLIP otimizado: canvas 512px, queries MongoDB paralelas (~1.5s)
- [x] GPS fix: localStorage como fonte de verdade
- [x] Persistencia de refeicao (localStorage)
- [x] Clear-Site-Data middleware para PWA cache

## Endpoints Principais
- POST /ai/identify - Fast scan (CLIP ou Gemini) com timing logs
- POST /ai/identify-with-ai - Enrichment Premium (background)
- GET /ai/status - Status do indice

## DB Schema
- users: {pin_hash, premium_ativo, restricoes}
- meal_history: Historico de pratos consumidos

## Credenciais
- Premium User: pin=1234, nome=Teste
- Admin: joaomanoelmoreno / Pqlamz0192

## Backlog

### P0 - Imediato
- Investigar velocidade CLIP no Cibi Sana (2-3s) — logs de timing adicionados, aguardando teste real do usuario no Render para ver breakdown
- Testar crop da camera no celular (fix da moldura guia)

### P1 - Proximo
- OpenAI TTS modo acessibilidade (vozes Alloy/Onyx selecionadas pelo usuario)
  - Botao "Ouvir" (nao automatico)
  - Facil de encontrar para deficientes visuais
- Landing page premium (aguardando mockup do usuario)
- Revisao nutricional pratos F-J (com verificacao de contaminacao)

### P2 - Futuro
- Stripe para assinatura Premium
- Modo demo na landing page
- Publicacao Google Play (TWA) e Apple Store (Capacitor)
- Refatorar server.py (~5700 linhas) e App.js (~4000 linhas)

## Integracoes 3rd Party
- OpenCLIP ViT-B-16 (HuggingFace, local/ONNX)
- Gemini 2.5 Flash Lite (Emergent LLM Key)
- OpenAI TTS (testado: Alloy e Onyx melhores em portugues - HD model)
