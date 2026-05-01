# SoulNutri — Changelog

---

## 2026-05-01 — Proteção de 3 endpoints admin sem autenticação

**Arquivos:** `backend/server.py` (3 linhas) + `frontend/src/Admin.js` (1 linha)

### Problema
Três endpoints `/admin/*` estavam sem `dependencies=[Depends(verify_admin_key)]`:
- `GET /admin/premium/users` — listava todos os 14 usuários sem auth
- `POST /admin/premium/liberar` — qualquer pessoa podia autopromover-se a premium
- `POST /admin/premium/bloquear` — qualquer pessoa podia bloquear outros usuários

### Fix aplicado
```python
# server.py — adicionado dependencies=[Depends(verify_admin_key)] nos 3 decoradores
@api_router.get("/admin/premium/users", dependencies=[Depends(verify_admin_key)])
@api_router.post("/admin/premium/liberar", dependencies=[Depends(verify_admin_key)])
@api_router.post("/admin/premium/bloquear", dependencies=[Depends(verify_admin_key)])
```
```javascript
// Admin.js linha 590 — liberarPremium() trocou fetch() por adminFetch()
// (adminFetch injeta X-Admin-Key: adminKeyCache automaticamente)
const res = await adminFetch(`${API}/admin/premium/liberar`, { ... });
```

### Validação
- Sem X-Admin-Key: todos retornam **HTTP 401** ✅
- Com X-Admin-Key válido: todos retornam **HTTP 200 + dados corretos** ✅
- Admin.js aba Premium: **carregou 14 usuários, formulários funcionando** ✅

---

## 2026-05-01 — Fix crítico: App congelado no Premium após scan com falha

**Commit:** `5b03399`
**Arquivo:** `frontend/src/App.js`, linha 1592

### Problema
`premiumCycleBusyRef.current` era setado como `true` em `identifyImage` (L.1469) mas **nunca resetado no `finally`** da mesma função. O reset só existia em dois lugares:
- `enrich useEffect .finally()` (L.952) — só roda se `result?.ok && result?.identified`
- `addItemToPlate()` (L.1609) — só roda se o usuário clica em "Adicionar"

Qualquer scan que falhasse (AbortError, timeout, network error, HTTP !ok) encerrava `identifyImage` **sem setar `result`**, então nem o enrich nem o addItemToPlate eram chamados. O ref ficava preso em `true` para sempre na sessão atual.

Na próxima tentativa de scan, o GATE (L.1463) bloqueava silenciosamente: `if (premiumUser && premiumCycleBusyRef.current) { return; }`. Nenhum spinner, nenhuma mensagem, câmera não reagia. App parecia congelado.

### Causa raiz
Design pressupôs que `identifyImage` sempre terminaria por um caminho positivo (sucesso → enrich, ou ação do usuário → addItemToPlate). O caminho de falha pura (sem `result`) não tinha tratamento do guard.

### Fix aplicado
```javascript
// App.js — finally block de identifyImage (linha 1592)
// ADICIONADO:
premiumCycleBusyRef.current = false;
```

### Efeito colateral: nenhum
O ref pode ser setado como `false` de forma segura para qualquer usuário. O GATE só ativa quando `premiumUser && premiumCycleBusyRef.current === true`, logo setar `false` para não-premium não causa efeito.

### Como foi descoberto
RCA sistemático provocado por usuário relatando "app travado" e "Premium não entra". Investigação por provas (sem patches especulativos):
1. Todos os endpoints do Render testados e confirmados funcionando
2. Código local e Render confirmados em sincronia (`phase_2`)
3. `premiumCycleBusyRef` rastreado linha a linha → lacuna no finally identificada

---

## 2026-04-30 — Correção Event Loop bloqueante no warmup

**Arquivo:** `backend/server.py`

Rota `/api/ai/warmup` chamava `load_onnx_index()` sincronicamente dentro de uma função `async`. Isso bloqueava o event loop do FastAPI durante o carregamento do modelo ONNX (~0.26s), impedindo qualquer outra requisição de ser processada.

**Fix:** Substituído por `await loop.run_in_executor(None, load_onnx_index)`.

---

## 2026-04-30 — Troca de Google API Key revogada

**Arquivo:** `backend/.env` e Render Dashboard

A `GOOGLE_API_KEY` anterior estava revogada. Toda chamada à rota Gemini (`restaurant=external`) gerava um fallback para a Emergent Key com latência de 17-50s, causando os timeouts no Android (AbortController de 15s).

**Fix:** Nova key configurada no Render dashboard.

> ⚠️ A nova key (`AIzaSyBZAwyEEJFqzh6y8b0BmOZsXk_9s7y7PEk`) foi posteriormente identificada como **comprometida (leaked)**. Ver `STABLE_VERSION.md` → Problemas conhecidos.
