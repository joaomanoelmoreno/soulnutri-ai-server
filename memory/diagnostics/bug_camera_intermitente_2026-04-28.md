# Bug Intermitente — Erro de Câmera no Celular

**Data do registro:** 28/Abr/2026
**Status:** REGISTRADO. Sem patch. Sem alteração de código.
**Prioridade:** P2 (intermitente, não reproduzível, sem impacto recorrente)

---

## 1. Resumo do bug

> *"Erro ocasional de câmera em celular, não reproduzido no Mac, sem erro no DevTools"*

### Sintomas observados
- ✅ Mac: vários testes consecutivos sem erro
- ⚠️ Celular: erro apareceu **1 vez** em múltiplos testes consecutivos
- ❌ Não reproduzível sob demanda
- ❌ DevTools (Console + Network) não mostraram erro JS nem falha de request

### Hipóteses iniciais (a confirmar)
1. **Race condition** com o ciclo de vida do `MediaStream` (parar/reiniciar câmera entre scans)
2. **Stream zombie** — `videoRef.srcObject` ainda ativo enquanto novo `getUserMedia` é chamado
3. **PWA service worker** servindo HTML em estado intermediário (cache antigo + bundle novo)
4. **iOS Safari** revogando permissão de câmera silenciosamente após inatividade
5. **React Error #31** disparando o `CameraErrorBoundary` de forma indireta (já mitigado pelo patch anterior, mas pode haver caso residual)
6. **Memória do dispositivo** — celular em estado de pressão de RAM rejeitando `getUserMedia`

### Sintoma fica mascarado por design
O app tem um **`CameraErrorBoundary`** que captura **qualquer crash** de componente filho da árvore da câmera e exibe "Erro na câmera". Isso significa que o usuário vê "Erro na câmera" mesmo quando o problema real está em **outro componente** (ex: WeeklyReport, NotificationPanel, render de objeto). Sem instrumentação fina, não dá para distinguir entre:
- Câmera real com problema
- Componente irmão crashando e o boundary do nível acima absorvendo o erro

---

## 2. Plano leve de diagnóstico (SEM implementar)

### 2.1 Dados a coletar quando o erro reaparecer

Quando o usuário reportar/reproduzir o bug, capturar:

| Campo | O que registrar | Como |
|---|---|---|
| 🔴 **Mensagem exata do erro** | String literal do `Error.message` + `Error.name` | Ler do `errorInfo` do ErrorBoundary |
| 🔴 **Stack trace** | `Error.stack` (primeiras 10 linhas) | Mesmo lugar |
| 🔴 **componentStack** | Em qual componente disparou | `errorInfo.componentStack` (React) |
| 🟡 **Modelo do dispositivo** | iPhone 14 Pro / Galaxy S23 / etc. | `navigator.userAgent` (parse) |
| 🟡 **Navegador + versão** | Chrome iOS 132 / Safari 17.5 / etc. | `navigator.userAgent` |
| 🟡 **Sistema operacional + versão** | iOS 18.2 / Android 14 / etc. | `navigator.userAgent` |
| 🟡 **Tipo de rede** | Wi-Fi / 4G / 5G / offline | `navigator.connection.effectiveType` |
| 🟡 **Velocidade efetiva** | downlink em Mbps | `navigator.connection.downlink` |
| 🟢 **Momento do erro** | Antes/durante/depois do scan | timestamp + estado do `scanningRef` |
| 🟢 **Trocou de tela?** | Veio de Premium/Admin/Settings? | `document.referrer` interno + history |
| 🟢 **Reabriu câmera?** | Quantos `getUserMedia` foram chamados na sessão | contador local |
| 🟢 **Tamanho da última imagem** | KB do último blob enviado | já existe em `lastImageBlob.size` |
| 🟢 **Status da permissão** | `granted` / `denied` / `prompt` | `navigator.permissions.query({name:'camera'})` |
| 🟢 **Tempo desde abertura** | ms desde `mountedRef = true` | timestamp delta |
| 🟢 **Estado da página** | `visible` / `hidden` (background?) | `document.visibilityState` |
| 🟢 **Tem stream ativo?** | bool | `!!videoRef.current?.srcObject` |
| 🟢 **Tracks ativos do stream** | nº + estado (`live`/`ended`) | `stream.getTracks().map(t=>t.readyState)` |
| 🟢 **Memória JS disponível** | MB (Chrome only) | `performance.memory.jsHeapSizeLimit` |

🔴 = essencial (sem isso, diagnóstico impossível)
🟡 = importante (correlaciona com hipóteses)
🟢 = útil (refinamento)

### 2.2 Onde plantar o log (sem implementar)

#### Ponto de coleta ideal — `CameraErrorBoundary.componentDidCatch`

Esse é o ponto único de **interceptação garantida** de qualquer crash da árvore da câmera. O React passa `(error, errorInfo)` automaticamente. Adicionar lá um `try/catch` que:

1. Monta um payload com os campos da Seção 2.1
2. Chama um endpoint dedicado (NOVO, não existe ainda) tipo `POST /api/diagnostics/camera-error`
3. **Falha silenciosa**: se o POST falhar, nem tenta retry — não deve impactar UX

#### Ponto de coleta complementar — wrapper de `getUserMedia`

`getUserMedia` é chamado em ~5 lugares no `App.js` (linhas 1121-1155). Cada chamada é envolta em try/catch, mas o catch **só faz console.warn**. Esses warnings se perdem.

Sugestão: criar um helper único `safeGetUserMedia(constraints)` que:
- Chama `navigator.mediaDevices.getUserMedia(constraints)`
- Em caso de erro, captura `error.name` (NotAllowedError, NotFoundError, OverconstrainedError, NotReadableError, AbortError…)
- Loga payload mínimo via `POST /api/diagnostics/camera-error`
- Re-lança o erro normalmente (não muda comportamento)

**Tipos de erro do MediaStream que importa distinguir:**
- `NotAllowedError`: usuário negou permissão
- `NotReadableError`: hardware ocupado por outro app (pior caso — comum em iOS)
- `OverconstrainedError`: constraints (resolução, facingMode) não suportados
- `AbortError`: usuário fechou o prompt
- `NotFoundError`: sem câmera detectável
- `SecurityError`: contexto não-HTTPS

### 2.3 Como capturar erro SEM impactar UX

#### Princípios obrigatórios
- ✅ **Falha silenciosa**: log nunca deve atrasar UI ou bloquear render
- ✅ **Não-bloqueante**: usar `fetch(...).catch(() => {})` — sem await, sem feedback
- ✅ **Throttle**: máximo 1 log por sessão por tipo de erro (evita spam ao backend)
- ✅ **Sem PII**: zero dados pessoais (PIN, nome, foto). Apenas metadados técnicos.
- ✅ **Tamanho do payload**: <2 KB (rápido em qualquer rede)
- ✅ **Endpoint dedicado**: NOVO endpoint `POST /api/diagnostics/camera-error`. Salva em coleção MongoDB `diagnostic_logs` com TTL de 30 dias.
- ✅ **Sem dependência externa**: NÃO usar Sentry/Datadog/LogRocket nesta fase (custo + privacy + complexidade adicional)

#### Diagrama do fluxo proposto

```
ERRO CAPTURADO (boundary OU getUserMedia)
        │
        ▼
[montar payload] ── não bloqueia UI
        │
        ▼
[fetch POST /api/diagnostics/camera-error]
        │  (timeout 3s, sem retry, sem await)
        ▼
   .catch(() => {})  ← falha silenciosa
        │
        ▼
[continuar render normal] ← UI imune
```

### 2.4 Análise de logs — workflow (futuro)

Quando 5+ ocorrências forem coletadas:

1. Query MongoDB `diagnostic_logs` agrupando por `error.name`, dispositivo, navegador
2. Identificar padrão dominante:
   - `NotReadableError` em iPhone X/11/12 → hipótese: outra aba/PWA com câmera ativa
   - `AbortError` após troca de tela → hipótese: navegação rápida cortando stream
   - `OverconstrainedError` em Android específico → hipótese: resolução pedida não suportada
3. Decidir patch direcionado — só **depois** de termos amostra estatística.

---

## 3. Custo de implementar este plano (estimativa, NÃO executar)

| Etapa | Esforço | Impacto |
|---|---|---|
| Endpoint backend `POST /api/diagnostics/camera-error` | ~30 min | Adicionar 1 endpoint + 1 collection MongoDB |
| Helper `safeGetUserMedia` | ~20 min | 1 arquivo novo + 5 substituições no App.js |
| Adicionar payload no `CameraErrorBoundary.componentDidCatch` | ~15 min | Modificação localizada |
| Total | **~1h** | Footprint mínimo, sem impacto em UX |

**Risco de regressão:** quase zero — o helper **mantém comportamento original** e só adiciona log. O endpoint é novo (não toca nenhum existente).

---

## 4. Recomendação

🟡 **NÃO implementar agora.** Aguardar:
- Bug reaparecer 2-3 vezes (confirma que é recorrente, não acidente)
- OU aumentar volume de usuários (mais reports → maior chance de captura)

**Quando implementar, fazer apenas após autorização explícita** seguindo a Seção 2.4 (workflow de análise).

---

## 5. Resumo Executivo

| Item | Status |
|---|---|
| Bug registrado formalmente | ✅ Este documento |
| Patch aplicado | ❌ NÃO (decisão tua) |
| Plano de diagnóstico | ✅ Documentado (Seções 2.1–2.3) |
| Custo estimado | ✅ ~1h de implementação quando autorizado |
| Risco de espera | 🟡 Baixo. Bug intermitente raro, não bloqueia uso normal |

**Próximo gatilho:** observar reaparecimento. Se ocorrer 2+ vezes em 14 dias, escalar prioridade para P1.

---

**FIM DO REGISTRO. Nenhuma alteração de código. Nenhum deploy.**
