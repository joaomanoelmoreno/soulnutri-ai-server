# SoulNutri — Changelog

---

## 2026-05-02 — Fix P0: Cache de identificação separado por `restaurant`

**Arquivos:** `backend/services/cache_service.py` + `backend/server.py` (2 call sites)

### Problema
`get_cached_result()` usava `MD5(image_bytes)` como chave — sem incluir `restaurant`. Um resultado Gemini gerado com `restaurant=external` era retornado diretamente para `restaurant=cibi_sana` como cache hit, antes da bifurcação ONNX/Gemini (linha 920 do `server.py`). O Gemini era usado dentro do Cibi Sana mesmo com GPS correto.

### Fix aplicado
```python
# cache_service.py — chave agora inclui restaurant normalizado
def get_image_hash(image_bytes: bytes, restaurant: str = '') -> str:
    restaurant_key = (restaurant or '').strip().lower()
    return hashlib.md5(image_bytes + restaurant_key.encode()).hexdigest()

# server.py — 2 call sites atualizados
cached = get_cached_result(content, restaurant=restaurant or '')
cache_result(content, response_data, restaurant=restaurant or '', ttl_seconds=3600)
```

### Validação (curl com imagem real do dataset)
| Teste | restaurant | source | from_cache | Resultado |
|-------|-----------|--------|------------|-----------|
| 1 | external | gemini_flash | False | Gemini chamado, cache salvo ✅ |
| 2 | cibi_sana (mesma imagem) | local_index | False | **Sem cache external, ONNX executado** ✅ |
| 3 | cibi_sana (2º scan) | local_index_cached | True | Cache cibi_sana usado ✅ |
| 4 | external (repetido) | gemini_flash_cached | True | Cache external preservado ✅ |

---

## 2026-05-02 — Fix P0: GPS travado por `soulnutri_location_manual`

**Arquivo:** `frontend/src/App.js`, linhas 613-633

### Problema
No callback `watchPosition`, havia um `return` prematuro quando `soulnutri_location_manual === 'true'`, executado ANTES do cálculo de distância. Isso impedia que o GPS corrigisse o modo mesmo quando o usuário estava fisicamente dentro do Cibi Sana.

### Causa raiz
A flag de override manual foi criada para preservar escolhas manuais do usuário (ex: selecionar "external" quando dentro do restaurante). Porém o `return` incondicional bloqueava também o caminho legítimo `external → cibi_sana`, impedindo a correção automática quando o usuário entrava no restaurante após uma seleção manual anterior.

### Fix aplicado
```javascript
// ANTES — return prematuro bloqueava tudo
if (localStorage.getItem('soulnutri_location_manual') === 'true') {
  setPermissionsStatus(prev => ({ ...prev, location: 'granted' }));
  return;  // ← bloqueava mesmo dentro do Cibi Sana
}
// cálculo de distância vinha depois...

// DEPOIS — distância calculada ANTES, trava só bloqueia external → external
const dist = haversineDistance(...);
// ... cálculo ...
const newRestaurant = isInsideCibiSanaZone ? 'cibi_sana' : 'external';

const isManual = localStorage.getItem('soulnutri_location_manual') === 'true';
if (isManual) {
  if (newRestaurant === 'cibi_sana') {
    // GPS confirma presença no Cibi Sana → remove trava e corrige
    localStorage.removeItem('soulnutri_location_manual');
    setDetectedRestaurant('cibi_sana');
    localStorage.setItem('soulnutri_restaurant', 'cibi_sana');
  }
  return;  // ← fora do Cibi Sana: mantém escolha manual
}
```

### Resultado
- Impossível ficar travado em "external" dentro do Cibi Sana
- GPS corrige automaticamente na próxima leitura de posição
- Gemini nunca mais acionado dentro do restaurante por causa desta trava
- Raio, cálculo de distância e backend: **inalterados**

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
