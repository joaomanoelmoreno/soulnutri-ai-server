# SoulNutri - Product Requirements Document

## Versao Atual: V3.4 (Insights Premium + Admin por PIN)

## Stack
- Frontend: React (PWA) | Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX pré-otimizado R2) | Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: gTTS (GRATUITO, pt-BR) — REGRA IMUTÁVEL | DB: MongoDB Atlas | Deploy: Render Standard 1GB

## REGRAS IMUTÁVEIS → /app/memory/REGRAS_IMUTAVEIS.md

## Implementado

### V3.4 (25/Abr/2026) — Insights Premium + Admin por PIN
- BUG CORRIGIDO: enrichLoading não resetava quando result = null (race condition) — patch `setEnrichLoading(false)` no early return
- BUG CORRIGIDO: is_admin hardcoded como True para todos os Premium — corrigido para ler do MongoDB
- Dashboard Premium redesenhado: 4 blocos de insight (status calórico textual, qualidade nutricional, alertas dedup, sugestões)
- Tab "Hoje": greeting dinâmico ("Hoje você está indo bem 👍"), status calórico sem anel grande, macros em cards inline
- Alertas deduplicados por nutriente (sem repetição de "prato leve 31 kcal")
- Admin via PIN Premium: endpoint GET /premium/admin-token retorna chave ADMIN somente para is_admin=true
- Admin.js — Aba Premium simplificada: só bloqueados aparecem por padrão, busca por nome, botão Deletar, botão Tornar/Revogar Admin
- Novos endpoints backend: DELETE /admin/premium/users/{nome}, POST /admin/premium/toggle-admin, GET /premium/admin-token

### V3.3 (24/Abr/2026) — Estabilização
- BUG CRÍTICO CORRIGIDO: Sessão Premium não é mais destruída por erro de rede transitório
- BUG CRÍTICO CORRIGIDO: Mutação direta do objeto React state no enrich substituída por useRef (enrichedDishesRef)
- Auth Admin completa: tela de login + XHR helpers enviam X-Admin-Key + verify_admin_key reativada no backend
- Reset clearPlate completo: limpa enrichLoading, error, ttsLoading, ttsError, radarInfo, áudio TTS, enrichedDishesRef
- Admin logout adicionado (botão "Sair" no header)

### V3.2 (13/Abr/2026)
- Fontes (instituições reais) em benefícios, riscos, notícias e Verdade/Mito
- Alertas nutricionais automáticos no scan (calorias, proteínas, gorduras, sódio, fibras, alérgenos) — zero créditos
- TTS gTTS em tudo (REGRA: não usar OpenAI TTS)
- Combinações incluídas no áudio TTS
- Anti-duplicata de pratos no prato completo
- Botão remover prato individual (X)
- Bug localização corrigido (GPS watcher parado no modal)
- Proporções nutricionais: fallback 0.10 para ingredientes desconhecidos
- Limpeza de 18 notificações "hidratar" duplicadas do banco
- Textos premium curtos (max 20 palavras)
- Notícias sem URLs falsos (apenas nome da instituição)

### V3.1 (12/Abr/2026)
- ONNX modelo pré-otimizado no R2 (sem re-export no build)
- ORT_DISABLE_ALL (compatível com CPU Render)
- Dockerfile sem torch (build 5min mais rápido)
- HSTS header + HSTS Preload submetido
- emergent-main.js condicional (só no preview)
- Enrich via useEffect (zero stale closure)
- Service Worker v10 minimal
- Health check, mensagens de erro amigáveis

## Endpoints Principais
- POST /ai/identify (CLIP + alertas automáticos)
- POST /ai/enrich (Gemini: benefícios/riscos/curiosidades/combinações/notícias/mito com fontes)
- POST /ai/tts (gTTS gratuito, pt-BR)
- GET /sw.js, /manifest.json (anti-cache)
- GET/POST/PUT/DELETE /admin/* (requer header X-Admin-Key)

## Admin Auth
- Backend: verify_admin_key ativa — compara X-Admin-Key contra ADMIN_SECRET_KEY do .env
- Frontend: tela de login em /admin, todos os helpers XHR (xhrGet, xhrPost, xhrDelete, retryFetch, adminFetch) enviam X-Admin-Key
- Key salva em localStorage sob: soulnutri_admin_key

## Fichas Nutricionais (nutrition_sheets)
- STATUS: **224 fichas já existem no MongoDB** — coleção `nutrition_sheets`
- Lógica proporcional: `calcular_nutricao_prato()` em `taco_database.py` — PROPORCOES por tipo de ingrediente (arroz=50%, frango=30%, alho=2%, etc.)
- CORREÇÃO APLICADA (v3.3): `query_taco()` em `nutrition_3sources.py` agora usa `calcular_nutricao_prato()` (antes usava divisão igual — violava REGRAS_IMUTAVEIS)
- Para regenerar fichas existentes com proporções corretas: rodar `batch_all_nutrition.py` com force=True (TACO é local, sem créditos; USDA usa API key)

## Backlog Priorizado

### P0 - Urgente
- Rodar batch_all_nutrition.py force=True para regenerar as 188 fichas com o algoritmo corrigido (kcal_db estão com valores antigos e bugados no MongoDB)

### P1 - Próximo
- Verificação geral de ingredientes e tabela nutricional em todos os pratos
- Landing page premium com trial (aguardando mockup do usuário)
- Integração Stripe para cobrança de assinaturas
- Fichas nutricionais em lote via admin (dados TACO/USDA, sem custo IA)

### P2 - Importante
- Revisão ingredientes/descrição pratos F-Z (usuário inserindo via admin)
- Melhorar tempo CLIP de 2s para <500ms
- Notificações push: verificar rotação diária

### P3 - Futuro
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5900 linhas) e App.js (~4400 linhas)
- Limpeza imagens Jiló Empanado (fotos contaminadas com Quiabo)

## Problemas Conhecidos
- Gemini pode gerar nomes de fontes imprecisos
- 3+ usuários duplicados "Joao Manoel" no DB (update_many mitiga)
- Tempo CLIP no Render: ~2s (acima do ideal de 500ms, ORT_DISABLE_ALL necessário)
- Câmera pode travar no mobile após limpeza de prato (ciclo de vida do stream)
