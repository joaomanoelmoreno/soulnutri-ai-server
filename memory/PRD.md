# SoulNutri - Product Requirements Document

## Versao Atual: V3.5 (Arquitetura Split Vercel + Render + TACO v2 + USDA Fallback)

## Stack
- Frontend: React (PWA) — **hospedado na Vercel** | Backend: FastAPI, Motor (MongoDB async) — **hospedado no Render Standard**
- IA: OpenCLIP ViT-B-16 (ONNX pré-otimizado R2) | Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: gTTS (GRATUITO, pt-BR) — REGRA IMUTÁVEL | DB: MongoDB Atlas

## Arquitetura de Produção (27/Abr/2026)
```
soulnutri.app.br  →  Vercel (React PWA, SSL Let's Encrypt)
                       │
                       └─→ https://soulnutri-v3wd.onrender.com (FastAPI + MongoDB)
```
- DNS: Registro.br (NS: a/b/c.sec.dns.br)
- Apex `soulnutri.app.br`: `A @ 216.198.79.1` → Vercel
- `www.soulnutri.app.br`: `CNAME www 4440d38797346d1a.vercel-dns-017.com.` → Vercel
- Backend Render custom domain `soulnutri.app.br` mantido como rollback (não removido)
- SSL válido até Jul/2026 (auto-renew Let's Encrypt via Vercel)

## REGRAS IMUTÁVEIS → /app/memory/REGRAS_IMUTAVEIS.md

## Implementado

### V3.5.1 (28/Abr/2026) — Fix React Error #31
- `renderTextSafe` aplicado em `WeeklyReport.jsx` (16 pontos: ai.nota_geral, ai.titulo, periodo, dias_registrados, analise.detalhe, pontos_positivos, alertas, dicas, curiosidade, mensagem_motivacional, level.nome/xp/proximo_nivel, motivational_messages, next.nome/descricao, badges unlocked/locked)
- `renderTextSafe` aplicado em `NotificationPanel.jsx` (6 pontos: n.title, n.message, n.date, ref.source, ref.title, dishes_context)
- Função `renderTextSafe` declarada localmente em cada arquivo (mesmo padrão de App.js/DashboardPremium.jsx/Premium.jsx)
- Lint ESLint OK em ambos os arquivos
- Layout, lógica e estrutura de componentes inalterados
- Aguardando deploy (push manual do usuário → auto-deploy Vercel)

### V3.5 (27/Abr/2026) — Migração DNS para arquitetura Split (Vercel + Render)
- **Frontend migrado para Vercel** (`soulnutri-ai-server`), backend permanece no Render (`soulnutri-v3wd`)
- DNS `soulnutri.app.br` repontado do Render para Vercel (A 216.198.79.1 / CNAME 4440d38797346d1a.vercel-dns-017.com)
- SSL Let's Encrypt emitido automaticamente pela Vercel (válido 27/Abr/2026 → 26/Jul/2026)
- CORS no backend Render validado para Origins `https://soulnutri.app.br` e `https://www.soulnutri.app.br`
- Render custom domain mantido (rollback instantâneo se necessário)
- Frontend bundle (`main.16845801.js`) com 10 chamadas para `https://soulnutri-v3wd.onrender.com` (REACT_APP_BACKEND_URL injetada em build time)
- Backup DNS anterior: `A @ 216.24.57.1` / `CNAME www soulnutri-v3wd.onrender.com.`
- Fluxos validados pelo usuário: identificação de prato, nutrição, ingredientes, alertas, categoria

### V3.4.1 (27/Abr/2026) — Auditoria Nutricional Sistêmica + Fallback USDA
- **taco_database.py refatorado**: loop de proporções migrado de substring match para token exact match (evita `"sal"` puxar valores de `"salmão"`)
- **usda_fallback.py criado**: serviço que consulta USDA FoodData Central API quando ingrediente não está no TACO (pratos internacionais)
- Dicionário `TRADUCAO_PT_EN` inicial para pratos internacionais (expandir conforme demanda)
- Novos ingredientes/aliases adicionados ao TACO: maionese, lula, entrecote, gelatina preparada, etc.
- Script `batch_force_taco.py` rodado em lote sobre os 188 pratos em `nutrition_sheets` — valores recalculados
- Validação em produção: Frango Grelhado 143.7 kcal / Molho Tártaro 174.1 kcal (antes estavam com 53 kcal / 5 kcal respectivamente)
- Deploy Render estava preso em cache Docker BuildKit — resolvido com "Clear Cache" no dashboard

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
- (nenhum item P0 pendente no momento — migração DNS + auditoria nutricional concluídas em 27/Abr/2026)

### P1 - Próximo
- React Error #31 em WeeklyReport.jsx e NotificationPanel.jsx (aplicar `renderTextSafe` — BLOQUEADO pelo usuário até autorização)
- Substituir EMERGENT LLM KEY por chaves locais fornecidas pelo usuário
- Expandir dicionário TRADUCAO_PT_EN em usda_fallback.py (culinárias asiática/árabe)
- Atualizar prompt Gemini para retornar macros estimados (Camada 3 de fallback nutricional)
- Verificação geral de ingredientes e tabela nutricional em todos os pratos
- Landing page premium com trial (aguardando mockup do usuário)
- Integração Stripe para cobrança de assinaturas
- Fichas nutricionais em lote via admin (dados TACO/USDA, sem custo IA)

### P2 - Importante
- Revisão ingredientes/descrição pratos F-Z (usuário inserindo via admin)
- Melhorar tempo CLIP de 2s para <500ms
- Notificações push: verificar rotação diária
- Migração final das imagens do Admin para Cloudflare R2 (erro 500 no upload em produção)
- Remover custom domain `soulnutri.app.br` do Render **somente após** 7 dias de estabilidade Vercel (rollback seguro)

### P3 - Futuro
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5900 linhas) e App.js (~4400 linhas)
- Limpeza imagens Jiló Empanado (fotos contaminadas com Quiabo)

## Problemas Conhecidos
- Gemini pode gerar nomes de fontes imprecisos
- 3+ usuários duplicados "Joao Manoel" no DB (update_many mitiga)
- Tempo CLIP no Render: ~2s (acima do ideal de 500ms, ORT_DISABLE_ALL necessário)
- Câmera pode travar no mobile após limpeza de prato (ciclo de vida do stream)
