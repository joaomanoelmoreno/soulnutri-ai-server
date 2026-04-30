# RELATÓRIO TÉCNICO — BUG ANDROID SCAN: 3 TENTATIVAS / 3 FALHAS

**Data:** Fev 2026  
**Componente afetado:** `App.js` — função `identifyImage` + useEffect Enrich  
**Sintoma:** Scans alternados falham no Android Chrome com "Tempo limite excedido" ou "Erro de conexão". iPhone OK.  
**Status:** ABERTO — Rollback em avaliação

---

## AMBIENTE

| Item | Valor |
|---|---|
| Frontend | React (PWA) — Vercel |
| Backend | FastAPI — Render Standard |
| Endpoint | POST `/api/ai/identify` (ONNX) + POST `/api/ai/enrich` (Gemini) |
| Dispositivos afetados | Android Chrome (PWA instalado e Chrome direto) |
| Dispositivos OK | iPhone Safari / iOS Chrome |
| Padrão de falha | Scan 1 OK → Scan 2 FALHA → Scan 3 OK → Scan 4 FALHA (alternado) |

---

## TENTATIVA 1 — Android Fix 2.1 (sessão anterior ao fork)

### Hipótese
O `premiumCycleBusyRef` travava em `true` após o 1º scan, bloqueando o 2º scan indefinidamente.

### Mudanças aplicadas
```
App.js — identifyImage():
  + Reset defensivo: se premiumCycleBusyRef travado por >10s, libera
  + Watchdog: setTimeout 8s → libera premiumCycleBusyRef automaticamente

App.js — useEffect Enrich:
  + AbortController com timeout duro de 10s (enrichCtrl)
  + enrichCtrl.abort() no timeout — libera conexão TCP
```

### Resultado
**Bug persistiu.** O usuário reportou 2/4 scans falhando. O erro mudou de "Tempo limite excedido" para "Erro de conexão" em algumas execuções.

### Por que falhou
O watchdog libera o gate (`premiumCycleBusyRef`) em 8s, mas o enrich do scan anterior continua retendo a conexão TCP até seu próprio timeout de 10s. A hipótese inicial do gate travado estava **parcialmente correta** mas não era a causa raiz.

---

## TENTATIVA 2 — Instrumentação Diagnóstica (esta sessão)

### Objetivo
Descobrir com precisão SE o build estava ativo no Android e ONDE o abort estava sendo disparado.

### Mudanças aplicadas
```
App.js — top level:
  + BUILD_STAMP: constante com ISO timestamp do build (visível no console)

App.js — identifyImage():
  + [ANDROID_DBG] logs em 8 pontos:
    - entry: premiumBusy, elapsedSinceLast, loadingRef
    - gate check: BLOCKED / PASSED
    - prevController: existência e estado de abort
    - FETCH START: endpoint + timestamp
    - FETCH RESPONSE: status + elapsed
    - IDENTIFY OK: dish + score + totalTime
    - ABORT ERROR: timeoutFired + signal.reason + refMatchesLocal
    - FINALLY: premiumBusy state

App.js — AbortController (fix latente):
  + Timeout callback migrado de abortControllerRef.current.abort()
    para _localCtrl.abort('timeout')  ← fecha bug de abort cruzado entre scans
  + _timeoutFired flag para distinguir timeout real de abort externo

App.js — Enrich useEffect:
  + [ANDROID_DBG] logs: TIMEOUT, ABORT reason, FINALLY before/after
```

### Resultado
**Bug persistiu.** O usuário não conseguiu abrir DevTools remotas no Android (chrome://inspect não funcionou no link de diagnóstico), portanto os logs não foram capturados.

### Por que falhou
Sem os logs do console Android, a confirmação definitiva da causa raiz não foi possível via esta tentativa. Entretanto, o padrão de falha alternada (2/4 scans) já era suficiente para o diagnóstico — a tentativa 3 foi aplicada com base nisso.

---

## TENTATIVA 3 — Android Fix 3.0 — Abort do Enrich no Início do Scan (esta sessão)

### Hipótese (confirmada pelo padrão alternado)
O enrich do scan N retém a conexão HTTP com o Render. Quando o scan N+1 inicia o `identify`, o Chrome Android não consegue abrir uma segunda conexão simultânea ao mesmo host (ou o Render fecha/recusa), resultando em `TypeError: Failed to fetch` = "Erro de conexão".

**Diferença iOS vs Android:** iOS Safari usa HTTP/2 com multiplexing mais tolerante; Android Chrome é mais restritivo com conexões simultâneas ao mesmo host em modo PWA.

### Mudanças aplicadas
```
App.js — novos refs:
  + enrichAbortCtrlRef = useRef(null)  ← rastreia enrich em andamento globalmente

App.js — useEffect Enrich:
  + enrichAbortCtrlRef.current = enrichCtrl  (logo após criar o AbortController)
  + finally: enrichAbortCtrlRef.current = null  (apenas se ainda for o mesmo ctrl)

App.js — identifyImage() — ANTES de criar o novo AbortController:
  + if (enrichAbortCtrlRef.current) {
      enrichAbortCtrlRef.current.abort('new-scan')  ← libera TCP imediatamente
      enrichAbortCtrlRef.current = null
    }

App.js — addItemToPlate():
  + abort do enrichAbortCtrlRef antes de abort do abortControllerRef

App.js — clearResult():
  + abort do enrichAbortCtrlRef antes de abort do abortControllerRef

App.js — cleanup unmount:
  + abort do enrichAbortCtrlRef
```

### Resultado
**Bug persistiu.** 3 tentativas, 3 falhas confirmadas pelo usuário.

### Por que pode ter falhado
Hipóteses restantes:
1. **Deploy Vercel não ativo** — o push ao GitHub pode não ter disparado o deploy, ou o Vercel pode estar servindo build em cache
2. **O erro "Erro de conexão" é um problema de rede do dispositivo** — não relacionado ao código (ex: Android Doze, switching WiFi/4G, TCP reset pelo provedor)
3. **Render limita conexões por IP** — o Render Standard pode ter rate limiting que rejeita requisições em burst
4. **O `enrichAbortCtrlRef` não está sendo populado no momento certo** — o useEffect do enrich só dispara após `setResult`, que é async; pode haver uma janela de race condition
5. **A build do Vercel usa `REACT_APP_BACKEND_URL` diferente** — se apontar para um backend diferente do esperado, o comportamento pode ser inconsistente

---

## ESTADO DO CÓDIGO (commits desta sessão)

| Arquivo | Mudanças |
|---|---|
| `App.js` | +enrichAbortCtrlRef, logs [ANDROID_DBG], _localCtrl para timeout, abort enrich em 4 pontos |
| Nenhum outro arquivo | — |

---

## O QUE NÃO FOI TENTADO

| Abordagem | Motivo de não implementar |
|---|---|
| Eruda (debugger in-app) | Não autorizado pelo usuário nesta sessão |
| `Connection: close` no header do fetch | Força nova TCP por request — poderia contornar o problema de connection reuse |
| Desabilitar completamente o enrich durante scan | Solução invasiva — enrich é dado premium core |
| Aumentar o `REQUEST_TIMEOUT` de 15s para 30s | Paliativo — não resolve a causa, piora UX |
| Migrar backend para HTTP/2 explícito no Render | Infraestrutura — fora do escopo do frontend |
| Testar sem PWA instalado (Chrome direto) | Não confirmado se o usuário testou neste modo |

---

## RECOMENDAÇÃO PARA AVALIAÇÃO

### Opção A — Rollback
Reverter `App.js` para o commit `a929526` (pré-patches Android) via plataforma Emergent.  
**Impacto:** Remove os logs de diagnóstico e os patches. O bug volta ao estado original.  
**Quando usar:** Se o bug não é bloqueante para o uso principal (usuários premium em iOS não são afetados).

### Opção B — Teste isolado antes do rollback
Antes de reverter, testar UMA hipótese rápida: abrir a URL **no Chrome Android sem PWA instalado** (sem atalho na tela inicial), limpar cache, e testar 5 scans.  
**Objetivo:** Confirmar se o problema está no PWA instalado (cache de app) ou é inerente ao Android Chrome.  
**Tempo:** 10 minutos.

### Opção C — Eruda (debugger visual no próprio app)
Adicionar a biblioteca Eruda (1 linha de script) temporariamente para capturar os logs `[ANDROID_DBG]` diretamente no celular, sem precisar de chrome://inspect.  
**Tempo:** 30 minutos de implementação + 10 minutos de teste.  
**Vantagem:** Com os logs em mãos, a causa real seria confirmada em 100% dos casos.

---

## CONCLUSÃO

Três patches foram aplicados com fundamentação técnica sólida, mas nenhum resolveu o problema. A ausência de logs do console Android impediu a confirmação definitiva da causa raiz. O padrão de falha alternada (scans N+1 sempre falham) aponta fortemente para conflito de conexão TCP entre enrich e identify, mas a hipótese não pôde ser descartada definitivamente.

**Recomendação técnica:** Opção B primeiro (teste sem PWA), depois Opção C (Eruda) — evita rollback desnecessário se o problema for de PWA/cache e não de código.
