# RELATÓRIO TÉCNICO CONSOLIDADO — SoulNutri
**Data:** 13/Abril/2026 | **Versão código:** v3.2

---

## 1. ESTRUTURA PRINCIPAL DO PROJETO

```
/app
├── Dockerfile                    # Build para Render (baixa modelo ONNX do R2, sem torch)
├── render.yaml                   # Config do serviço Render
├── backend/
│   ├── server.py                 # API FastAPI — 5922 linhas (MONOLITO — refatorar)
│   ├── .env                      # Variáveis: MONGO_URL, EMERGENT_LLM_KEY, OPENAI_API_KEY, R2_*, ADMIN_SECRET_KEY
│   ├── requirements.txt          # Dependências Python
│   ├── ai/
│   │   ├── embedder.py           # Carrega e executa ONNX (OpenCLIP ViT-B-16)
│   │   ├── index.py              # Busca por similaridade cosine no índice local
│   │   ├── policy.py             # Regras de decisão (score, confiança)
│   │   └── families.py           # Famílias de pratos (agrupamento)
│   ├── services/
│   │   ├── gemini_flash_service.py  # Enrich premium (Gemini 2.5 Flash Lite)
│   │   ├── tts_service.py           # TTS: OpenAI Shimmer (premium) + gTTS (fallback)
│   │   ├── notification_service.py  # Notificações rotativas (14 dicas)
│   │   ├── cache_service.py         # Cache em memória para respostas
│   │   └── r2_service.py            # Upload/download Cloudflare R2
│   ├── data/
│   │   └── taco_database.py      # Tabela TACO + cálculo nutricional com proporções comerciais
│   └── scripts/
│       └── export_onnx.py        # Export ONNX (NÃO usado no deploy — modelo vem do R2)
├── frontend/
│   ├── .env                      # REACT_APP_BACKEND_URL
│   ├── public/
│   │   ├── sw.js                 # Service Worker v10 MINIMAL (sem cache, sem fetch)
│   │   ├── manifest.json         # PWA manifest
│   │   └── index.html            # Template HTML (emergent-main.js condicional)
│   └── src/
│       ├── App.js                # App principal — 4421 linhas (MONOLITO — refatorar)
│       ├── Admin.js              # Painel admin — 3633 linhas
│       ├── index.js              # Entry point, registro do SW
│       ├── Premium.jsx           # Login/registro premium
│       ├── PremiumProfile.jsx    # Perfil nutricional do usuário
│       ├── NotificationPanel.jsx # Painel de notificações
│       ├── I18nContext.js        # Internacionalização (pt/en/es)
│       └── Demo.jsx              # Página demo
└── datasets/
    ├── dish_index.json           # Índice: nomes dos 191 pratos
    ├── dish_index_embeddings.npy # Embeddings CLIP (2994 vetores, 512 dim)
    ├── descriptions.json         # Descrições dos pratos
    └── dish_name_mapping.json    # Mapeamento slug→nome
```

**Entry points:**
- Backend: `backend/server.py` → Uvicorn porta 10000 (Render) ou 8001 (dev)
- Frontend: `frontend/src/index.js` → React → `App.js`
- Admin: `frontend/src/Admin.js` → rota `/admin`

---

## 2. FLUXOS PRINCIPAIS DO APP

### 2.1 Câmera/Captura
```
App.js:startCamera() (linha ~899)
→ navigator.mediaDevices.getUserMedia()
→ stream atribuído ao <video> ref
→ Toque na tela → App.js:handleCameraTouch() (linha ~1019, useCallback)
→ Canvas captura frame → blob → identifyImage(blob)
```

### 2.2 Reconhecimento
```
App.js:identifyImage(blob) (linha ~1102)
→ POST /api/ai/identify (FormData: file, restaurant, pin, nome)
→ server.py linha ~637:
  SE restaurant=cibi_sana → CLIP/ONNX (embedder.py + index.py)
    + MongoDB query para ingredientes/nutrition (adicionado 13/04)
  SE restaurant=external → Gemini Flash Lite (gemini_flash_service.py)
→ Resposta: {ok, identified, dish_display, nutrition, ingredientes, alergenos, alertas}
```

### 2.3 Montagem do Prato/Refeição
```
App.js:addItemToPlate() (linha ~1268)
→ Captura result atual → adiciona a plateItems (state)
→ Dedup: verifica se dish_display já existe no array
→ setResult(null) → setViewMode('mesa')

App.js:finishPlate() (linha ~1390)
→ Mesmo que addItemToPlate mas vai direto para mesa view

plateConsolidated (useMemo, linha ~1680)
→ Consolida todos os itens: nutrition, ingredientes, benefícios, riscos, etc.
```

### 2.4 Fluxo Gratuito
```
Scan → Identify → Resultado (nome, nutrição básica, ingredientes, alertas)
→ Adicionar ao prato → Mesa view (consolidado nutricional)
Sem: benefícios detalhados, curiosidades, combinações, notícias, mito/verdade, TTS premium
```

### 2.5 Fluxo Premium
```
Scan → Identify → Resultado básico (mesmo que gratuito)
→ useEffect ENRICH (linha ~623): detecta result.ok + premiumUser
  → POST /api/ai/enrich (Gemini) — background, 4-14s
  → Retorna: benefícios+fonte, riscos+fonte, curiosidade, combinações, notícias+fonte, mito/verdade+fonte
  → Atualiza result E plateItems (se já adicionou ao prato)
→ TTS: OpenAI Shimmer (scan + prato completo)
→ Mesa view com conteúdo completo premium
```

---

## 3. LOCALIZAÇÃO DOS PONTOS CRÍTICOS

### Onde o prato/refeição é armazenado
- **State:** `App.js:plateItems` (useState, linha 273) — array de itens do prato
- **Persistência:** `localStorage('soulnutri_plate')` (useEffect, linha 296)
- **MongoDB:** `meal_logs` collection (POST /api/premium/log-meal)

### Onde o botão corrigir/confirmar é tratado
- **"Sim, correto":** `App.js:sendFeedbackCorrect()` linha ~1811 → POST /api/ai/feedback
- **"Não, corrigir":** `App.js:sendToModerationQueue()` linha ~1851 → POST /api/feedback/moderation-queue
- **Renderização:** App.js linhas ~3700-3730

### Onde o premium é carregado
- **Login:** `App.js:checkPremiumSession()` linha ~632 → POST /api/premium/login
- **Enrich:** `App.js useEffect` linha ~623 → POST /api/ai/enrich → gemini_flash_service.py
- **State:** `premiumUser` (useState, linha 378)
- **Ref:** `premiumUserRef` (useRef, linha 379) — para uso em callbacks

### Onde a câmera é controlada
- **Iniciar:** `App.js:startCamera()` linha ~899
- **Parar:** `App.js:stopCameraInternal()` linha ~1009
- **Captura:** `App.js:handleCameraTouch()` linha ~1019 (useCallback)
- **Video element:** App.js linha ~2508 `<video ref={videoRef}>`
- **Stream state:** `stream` (useState, linha 254) + `streamRef` (useRef, linha 255)

### Onde OpenCLIP e Gemini são escolhidos
- **server.py linha ~637:** `is_cibi_sana = (restaurant == 'cibi_sana')`
- **SE cibi_sana:** `embedder.get_image_embedding()` + `index.search()` (linhas 640-850)
- **SE external:** `gemini_flash_service.identify_dish_gemini()` (linhas 730-790)
- **REGRA:** Cibi Sana = CLIP ONLY. External = Gemini ONLY. Nunca misturar.

---

## 4. BUG ATUAL

### Sintomas
1. Câmera trava após primeira captura (não reinicia para novo scan)
2. Botão "Adicionar mais itens" não responde
3. Botão "Sim está correto" travado

### Causa mais provável
**Câmera:** No mobile, `getUserMedia()` só funciona em resposta a gesto do usuário (click/tap). As tentativas de fix usaram `useEffect` para reiniciar a câmera, mas useEffect NÃO é gesto do usuário → browser bloqueia. Última tentativa colocou `startCamera()` nos onClick dos botões, mas pode haver conflito com o estado do stream que não é limpo corretamente.

**Botões:** `sendFeedbackCorrect()` fazia return silencioso quando `lastImageBlob` era null (câmera parada = blob perdido). Fix parcial aplicado (setFeedbackSent antes do return), mas pode não ter sido deployado no Render.

### O que já foi tentado
- useEffect para restart de câmera quando result=null → Não funciona no mobile (não é gesto)
- startCamera() direto nos onClick → Melhor, mas stream anterior pode não estar limpo
- setFeedbackSent(true) antes da verificação de blob → Fix correto mas precisa deploy

### O que mudou (sessão 12-13/04 que introduziu o bug)
- Adição do useEffect de enrich premium (linha 623) — muda quando result é setado
- Adição de MongoDB query no identify cibi_sana — pode mudar timing do response
- Múltiplas alterações em handlers de botões (clearResult, setViewMode, startCamera)

### Por que ainda não resolveu
O código foi alterado muitas vezes em sequência sem teste incremental no dispositivo real. As mudanças no fluxo de state (result, viewMode, stream) interagem entre si. A câmera no mobile é particularmente frágil com getUserMedia e precisa de gestão cuidadosa do stream lifecycle.

### Versão estável para rollback
**Render Dashboard → soulnutri-v3wd → Events → Deploy de 11/Abril/2026**
Essa versão: app abre, modo externo (Gemini) funciona, premium login funciona, câmera funciona. NÃO tem: enrich useEffect, TTS Shimmer, fontes, mito/verdade, alertas nutricionais, auth admin.

---

## 5. INTEGRAÇÃO E DEPLOY

### GitHub
- Repo: `joaomanoelmoreno/soulnutri-ai-server` branch `main`
- Emergent "Save to GitHub" → commit no main
- Modelo ONNX NÃO está no git (está no .gitignore, armazenado no R2)

### Render
- Serviço: **soulnutri-v3wd** (NÃO confundir com "soulnutri" que é outro serviço)
- URL: `soulnutri-v3wd.onrender.com`
- Domínio custom: `soulnutri.app.br` (configurado neste serviço)
- Plano: Standard (1GB RAM)
- Auto-deploy: ativado no branch main

### Como o deploy é disparado
1. Emergent "Save to GitHub" → push no main
2. Render detecta o push → build automático (Dockerfile)
3. Build: instala deps → baixa modelo ONNX do R2 → build React → copia backend
4. Deploy: Uvicorn porta 10000 → ONNX carrega (~0.6s) → "Service live"

### Variáveis críticas no Render (Environment)
| Variável | Uso |
|----------|-----|
| `MONGO_URL` | MongoDB Atlas connection string |
| `DB_NAME` | `soulnutri` |
| `EMERGENT_LLM_KEY` | Gemini enrich (fallback TTS) |
| `OPENAI_API_KEY` | TTS OpenAI Shimmer |
| `GOOGLE_API_KEY` | Gemini direct (backup) |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 storage |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 storage |
| `R2_ENDPOINT` | Cloudflare R2 endpoint |
| `R2_BUCKET` | `soulnutri-images` |
| `ADMIN_SECRET_KEY` | Auth para rotas /admin/* |
| `USDA_API_KEY` | Dados nutricionais USDA |

---

## 6. ARQUIVOS MAIS IMPORTANTES PARA MANUTENÇÃO

| Arquivo | Papel |
|---------|-------|
| `backend/server.py` | **MONOLITO PRINCIPAL** (5922 linhas). Todas as 100+ rotas da API. Precisa ser refatorado em módulos. |
| `frontend/src/App.js` | **MONOLITO FRONTEND** (4421 linhas). Câmera, scan, resultado, prato, premium, tudo. Precisa ser refatorado em componentes. |
| `frontend/src/Admin.js` | Painel admin (3633 linhas). Gestão de pratos, usuários premium, moderação. |
| `backend/ai/embedder.py` | Motor ONNX: carrega modelo, preprocessa imagem, gera embedding. `ORT_DISABLE_ALL` obrigatório no Render. |
| `backend/ai/index.py` | Busca por similaridade cosine no índice local de embeddings. |
| `backend/ai/policy.py` | Regras de decisão: score mínimo, confiança, fallback. |
| `backend/services/gemini_flash_service.py` | Prompt do enrich premium + identify externo. Prompt define formato de benefícios, riscos, fontes. |
| `backend/services/tts_service.py` | TTS dual: OpenAI Shimmer (premium) com fallback gTTS. Monta texto descritivo do prato. |
| `backend/data/taco_database.py` | Cálculo nutricional TACO com proporções comerciais. Fallback 0.10 para ingredientes desconhecidos. |
| `backend/services/notification_service.py` | 14 dicas rotativas por dia do ano. Dedup por user_pin+date. |
| `frontend/src/index.js` | Entry point React. Registro do SW. Limpeza de caches órfãos. |
| `frontend/public/sw.js` | Service Worker v10 MINIMAL. Só skipWaiting + delete caches. NUNCA adicionar cache. |
| `frontend/public/index.html` | Template HTML. emergent-main.js carrega APENAS no preview (condicional). |
| `Dockerfile` | Build sem torch. Baixa modelo do R2. ffmpeg para pydub. |
| `render.yaml` | Config Render. SEM healthCheckPath (causa crash loop com ONNX). |
| `/app/memory/REGRAS_IMUTAVEIS.md` | Regras que NUNCA podem ser violadas (tempos, engines, TTS, SW). |
| `/app/memory/PRD.md` | Product requirements, backlog, histórico de versões. |
| `datasets/dish_index.json` | Índice dos 191 pratos com nomes. |
| `datasets/dish_index_embeddings.npy` | 2994 embeddings CLIP (512 dimensões). |

---

## NOTAS FINAIS

- **server.py e App.js são MONOLITOS críticos.** Qualquer mudança deve ser cirúrgica e testada incrementalmente.
- **O modelo ONNX pré-otimizado está no R2**, não no git. Se perder o R2, precisa re-otimizar localmente e re-upload.
- **O Service Worker NUNCA deve cachear nada.** Qualquer adição de cache causa o problema de "app não abre".
- **Cibi Sana = CLIP. External = Gemini.** Nunca inverter ou misturar.
- **Camera getUserMedia no mobile exige gesto do usuário.** Não chamar de useEffect.
