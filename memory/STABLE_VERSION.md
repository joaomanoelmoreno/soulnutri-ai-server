# SoulNutri — Versão Estável de Referência

> **LEIA ISTO PRIMEIRO** se o app apresentar bug de travamento, regressão no Premium ou comportamento inesperado após qualquer patch.

---

## Versão Estável Atual

| Campo | Valor |
|-------|-------|
| **Commit** | `5b03399` (2026-05-01 13:14:08 UTC) |
| **DEPLOY_PHASE** | `phase_2` |
| **Frontend bundle** | `main.944778e3.js` (Vercel) |
| **Backend URL** | `https://soulnutri-v3wd.onrender.com` |
| **Marcado estável em** | 2026-05-01 |

---

## O que está na versão estável

### Bug crítico corrigido nesta versão
**`premiumCycleBusyRef` preso em `true` após scan com falha**
- Arquivo: `frontend/src/App.js`, linha 1592
- Sintoma: após qualquer scan que falha (timeout, AbortError, rede, HTTP !ok), todos os scans seguintes são bloqueados silenciosamente pelo GATE (L.1463). App parece congelado.
- Fix: `premiumCycleBusyRef.current = false;` adicionado ao `finally` de `identifyImage`
- RCA completo em: `/app/memory/CHANGELOG.md` (entrada 2026-05-01)

### Funcionalidades ativas e testadas
- Scan ONNX/CLIP (modo `cibi_sana`) → responde em ~1.8s no Render ✅
- Scan Gemini (modo `external`) → responde em ~1.1s no Render ✅
- Login Premium (`/api/premium/login`) → responde em ~0.5s ✅
- CORS configurado para `soulnutri.app.br` e `www.soulnutri.app.br` ✅
- 191 pratos indexados, 2994 embeddings ✅

---

## Como verificar se o Render está na versão estável

```bash
# 1. Versão e fase
curl -s https://soulnutri-v3wd.onrender.com/api/debug/version | python3 -m json.tool
# Esperado: "phase": "phase_2"

# 2. Saúde geral
curl -s https://soulnutri-v3wd.onrender.com/api/health
# Esperado: {"ok":true,"service":"SoulNutri AI Server"}

# 3. Premium login
curl -s -X POST https://soulnutri-v3wd.onrender.com/api/premium/login -F "pin=2212" -F "nome=Joao Manoel"
# Esperado: {"ok":true,"user":{...},"message":"Ola, Joao Manoel !"}

# 4. Confirmar fix no código
grep -n "premiumCycleBusyRef.current = false" /app/frontend/src/App.js
# Esperado: 3 linhas — 952, 1592, 1609
# A linha 1592 (dentro do finally de identifyImage) é o fix crítico
```

---

## Problemas conhecidos NESTA versão (ainda não corrigidos)

### P0 — Google API Key comprometida (`.env` local)
- Chave `AIzaSyBZAwyEEJFqzh6y8b0BmOZsXk_9s7y7PEk` retorna `403 PERMISSION_DENIED: key reported as leaked`
- **Não afeta o Render diretamente** (Render tem sua própria key no dashboard)
- Mas afeta testes locais/preview que usam Gemini — cai no fallback Emergent (3-5s mais lento)
- **Ação necessária**: gerar nova key em https://console.cloud.google.com e atualizar `/app/backend/.env` E o dashboard do Render

### P1 — Render RAM em 94%
- `rss_mb: 1874` de ~2000 MB disponíveis no plano Standard
- OOM Kill possível → reinício automático do Render (cold start 15-30s)
- O cold start + Bug premiumCycleBusyRef (já corrigido) era o combo que travava o app
- **Cold start ainda acontece** mas agora o app se recupera sem travar

### P1 — REQUEST_TIMEOUT de 15s muito curto
- `App.js`: `const REQUEST_TIMEOUT = 15000;`
- Durante fallback Emergent (Google Key comprometida), chamadas reais podem passar de 15s
- Recomendação: aumentar para `25000` ms

### P2 — Render cold start (Render Standard dorme após ~15min de inatividade)
- Primeiro acesso após inatividade: 15-30s de latência
- `checkPremiumSession` tem timeout de 5s → não carrega premium na primeira abertura
- Usuário precisa aguardar e tentar novamente (app não trava mais graças ao fix)
- Solução definitiva: upgrade para Render Pro (sempre ligado) ou keep-alive via Service Worker

---

## Regras para próximos agentes

### ANTES de aplicar qualquer patch
1. Confirmar que o Render está respondendo: `curl https://soulnutri-v3wd.onrender.com/api/health`
2. Confirmar que premium login funciona: `curl -X POST .../api/premium/login -F "pin=2212" -F "nome=Joao Manoel"`
3. Confirmar que a linha 1592 de App.js ainda tem `premiumCycleBusyRef.current = false`

### Se o app travar novamente no Premium
1. Verificar se `premiumCycleBusyRef.current = false` ainda está no `finally` (L.1592)
2. Verificar se o Render está vivo (pode estar em cold start)
3. Verificar RAM do Render: `curl .../api/debug/memory` — se `rss_mb > 1900`, risco de OOM Kill

### Se precisar rollback
- Commit estável: `5b03399`
- Usar a feature "Rollback" da plataforma Emergent ou `git checkout 5b03399 -- frontend/src/App.js`

### Ambientes
| Ambiente | URL | Observação |
|----------|-----|------------|
| Preview (este fork) | `https://nutri-familia.preview.emergentagent.com` | Descarte a cada novo fork |
| Produção Frontend | `https://soulnutri.app.br` | Vercel — auto-deploy via GitHub push |
| Produção Backend | `https://soulnutri-v3wd.onrender.com` | Render — auto-deploy via GitHub push |
| MongoDB | via `MONGO_URL` no `.env` | Atlas — compartilhado entre local e produção |

---

## Arquitetura resumida (para contexto rápido)

```
Android/Browser (soulnutri.app.br)
    │
    ├── Dentro do Cibi Sana (GPS) → restaurant=cibi_sana → ONNX/CLIP local (~1.8s)
    └── Fora do Cibi Sana        → restaurant=external  → Google Gemini API (~1-3s)
                                                            └── fallback: Emergent LLM Key (~3-8s)

Premium Flow:
  checkPremiumSession (5s timeout) → POST /api/premium/login → PIN + nome
  identifyImage → POST /api/ai/identify com pin+nome → resposta enriquecida
  enrich useEffect → POST /api/ai/enrich → dados premium adicionais
```
