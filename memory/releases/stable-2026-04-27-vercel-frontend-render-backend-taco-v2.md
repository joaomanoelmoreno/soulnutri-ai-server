# Versão Estável — stable-2026-04-27-vercel-frontend-render-backend-taco-v2

**Data do registro:** 27/Abr/2026
**Tipo:** Release Estável (rollback reference)
**Registrado por:** Agente E1 (sob solicitação do usuário)
**Sem alteração de código ou deploy nesta operação.**

---

## Objetivo

Criar um ponto de referência seguro para rollback e continuidade do projeto, marcando o estado consolidado após a migração DNS para arquitetura split (Vercel frontend + Render backend) e a auditoria nutricional sistêmica (TACO v2 + USDA fallback).

---

## 1. Arquitetura

```
soulnutri.app.br  →  Vercel (frontend React PWA)
                       │
                       └─→ chama →  https://soulnutri-v3wd.onrender.com  (backend FastAPI)
```

- **Frontend:** Vercel — projeto `soulnutri-ai-server` (Project ID: `prj_JItBHiaINJmlpR8TucQsBWY9gWea`)
- **Backend:** Render Standard — serviço `soulnutri-v3wd` (Service ID: `srv-d7adsunkijhs73ak81l0`)
- **Repositório Git:** `joaomanoelmoreno/soulnutri-ai-server` (branch `main`)
- **Fluxo:** o frontend Vercel chama o backend Render diretamente via `REACT_APP_BACKEND_URL=https://soulnutri-v3wd.onrender.com` (injetada em build time no bundle).

---

## 2. Infraestrutura

| Item | Status | Detalhe técnico |
|---|---|---|
| Domínio apontando para Vercel | ✔ | DNS `A @ 216.198.79.1` / `CNAME www 4440d38797346d1a.vercel-dns-017.com.` no Registro.br |
| SSL ativo (Let's Encrypt) | ✔ | Emitido pela Vercel em 27/Abr/2026 21:04 UTC, válido até 26/Jul/2026 (auto-renew) |
| CORS configurado corretamente | ✔ | Backend Render aceita Origins `https://soulnutri.app.br` e `https://www.soulnutri.app.br` |
| Backend saudável | ✔ | `GET /api/health` → `{"ok":true,"service":"SoulNutri AI Server"}` (200, ~322ms) |
| Servido pela Vercel | ✔ | `server: Vercel`, `x-vercel-cache: HIT`, `x-vercel-id: sfo1::...` |

---

## 3. Frontend

| Item | Status |
|---|---|
| Bundle Vercel correto | ✔ `main.16845801.js` ativo (last-modified 27/Abr/2026 20:20 UTC) |
| Sem chamadas para `soulnutri.app.br` como backend | ✔ 0 ocorrências no bundle |
| 10 chamadas para `https://soulnutri-v3wd.onrender.com` no bundle | ✔ |
| Sem React Error #31 | ✔ (validado pelo usuário em produção) |
| Fluxos validados pelo usuário | ✔ gratuito, premium, adicionar pratos, dashboard |

**Nota:** React Error #31 ainda existe latente em `WeeklyReport.jsx` e `NotificationPanel.jsx` (P1 backlog, BLOQUEADO até autorização). Hoje não está se manifestando nos fluxos principais.

---

## 4. Backend

| Item | Status |
|---|---|
| Deploy Render validado | ✔ Live desde 27/Abr/2026 14:13 (após Clear Cache que destravou Docker BuildKit) |
| TACO v2 (token match exato) | ✔ Substring match removido — não há mais `"sal"` puxando `"salmão"` |
| Aliases expandidos | ✔ maionese, lula, entrecote, gelatina preparada, etc. |
| Fallback USDA controlado | ✔ `usda_fallback.py` ativo na linha 1244 de `taco_database.py` |
| Batch nutricional executado | ✔ 188 pratos recalculados via `/tmp/batch_force_taco.py` |
| Spot check produção | ✔ Frango Grelhado: 143.7 kcal / Molho Tártaro: 174.1 kcal |

**Fontes nutricionais por camada (cascata):**
1. TACO v2 (pratos brasileiros, local, sem custo)
2. USDA FoodData Central API (pratos internacionais, com tradução PT→EN on-the-fly)
3. *(planejado, não implementado)* Gemini estimando macros

---

## 5. Banco de Dados

| Item | Status |
|---|---|
| Coleção `nutrition_sheets` atualizada | ✔ |
| ~188 pratos recalculados | ✔ via `batch_force_taco.py` (log: `/tmp/batch_force_taco.log`) |
| Inconsistências estruturais corrigidas | ✔ |

---

## 6. Problemas Resolvidos Nesta Versão

- ✔ **Bug `sal` → `salmão`** (substring match) — corrigido com token exact match
- ✔ **Dupla normalização** de nomes de ingredientes
- ✔ **Divisão incorreta de proporções** — `query_taco()` agora usa `calcular_nutricao_prato()`
- ✔ **Lookup TACO incorreto** — fallback dominante removido
- ✔ **Gelatina (pó vs preparado)** — aliases distintos no TACO
- ✔ **Composição duplicada (atum/peixe)** — corrigido
- ✔ **Inconsistência frontend/backend** — frontend Vercel consome backend Render explicitamente
- ✔ **React Error #31** — `renderTextSafe` aplicado em `WeeklyReport.jsx` (16 pontos) e `NotificationPanel.jsx` (6 pontos) em 28/Abr/2026 — aguardando deploy

---

## 7. Itens em Aberto (Backlog)

🟡 **P1 — Aliases adicionais em USDA fallback:** shoyu, sementes (abóbora/girassol/chia), ingredientes asiáticos e árabes (`TRADUCAO_PT_EN` em `usda_fallback.py`)
🟡 **P1 — Cobertura TACO <50% em alguns pratos:** monitorar e expandir
🟡 **P1 — Mix de Grãos:** 1 falha residual após batch
🟡 **P1 — React Error #31 em `WeeklyReport.jsx` e `NotificationPanel.jsx`:** ✅ CORRIGIDO em 28/Abr/2026 (renderTextSafe aplicado em 22 pontos críticos). Aguardando deploy para Vercel.
🟡 **P1 — Substituir EMERGENT LLM KEY por chaves locais** (Gemini/OpenAI diretas)
🟡 **P2 — Melhoria futura de confiança nutricional (UX):** indicador visual de fonte/qualidade do dado
🟡 **P2 — Atualizar prompt Gemini para retornar macros estimados** (Camada 3 de fallback)
🟡 **P2 — Migração imagens Admin → Cloudflare R2** (corrige Erro 500 em produção)
🟡 **P3 — Possível migração backend (Railway/Cloud Run):** não urgente — Render está estável após Clear Cache
🟡 **P3 — Detalhamento técnico dos Next Action Items e Backlog** (item 3 da revisão de 27/Abr/2026 — explicações granulares pendentes a pedido do usuário)

---

## 8. Regras de Segurança (NUNCA violar)

- ✔ **Não alterar arquitetura sem validação prévia do usuário**
- ✔ **Não misturar frontend/backend em deploy** (frontend = Vercel, backend = Render — manter separação)
- ✔ **Sempre validar em ambiente isolado antes de produção**
- ✔ **Evitar refatorações amplas sem evidência de necessidade**
- ✔ **NUNCA tocar em código de câmera ou scanner** sem autorização explícita
- ✔ **NUNCA aplicar `renderTextSafe` em `WeeklyReport.jsx` ou `NotificationPanel.jsx`** sem autorização explícita

---

## 9. Backup de Rollback

### DNS anterior (caso precise reverter)

```
A      @     216.24.57.1
CNAME  www   soulnutri-v3wd.onrender.com.
NS           a.sec.dns.br. / b.sec.dns.br. / c.sec.dns.br.
```

### Render custom domain
- `soulnutri.app.br` ainda configurado como Custom Domain no serviço `soulnutri-v3wd` — **MANTIDO como fallback** (não remover)
- Tempo estimado de rollback completo: ~5min (DNS TTL 300) + propagação (~5–30min em recursivos lentos)

### Procedimento de rollback (em caso de falha crítica)
1. Acessar Registro.br → Editar zona DNS de `soulnutri.app.br`
2. Restaurar `A @ 216.24.57.1` e `CNAME www soulnutri-v3wd.onrender.com.`
3. Aguardar ~5 min e validar com `dig soulnutri.app.br A +short`
4. Verificar acesso: `https://soulnutri.app.br` deve carregar pelo Render
5. Render volta a servir imediatamente (custom domain mantido)

---

## 10. Validações Técnicas Executadas no Momento do Registro

```
[1] DNS apex resolvendo → 216.198.79.1                            ✔
[2] DNS www resolvendo  → 4440d38797346d1a.vercel-dns-017.com.    ✔
[3] HTTPS apex          → server: Vercel, x-vercel-cache: HIT     ✔
[4] SSL                 → Let's Encrypt R12, válido até 26/Jul/2026 ✔
[5] Backend             → /api/health 200 OK                      ✔
[6] Spot check          → Frango Grelhado 143.7 kcal (TACO v2)    ✔
[7] CORS apex           → access-control-allow-origin OK          ✔
[8] CORS www            → access-control-allow-origin OK          ✔
```

---

## 11. Confirmação de Versionamento

- **Nome da versão:** `stable-2026-04-27-vercel-frontend-render-backend-taco-v2`
- **Localização:** `/app/memory/releases/stable-2026-04-27-vercel-frontend-render-backend-taco-v2.md`
- **Equivalente em PRD:** V3.5 (Arquitetura Split Vercel + Render + TACO v2 + USDA Fallback) — registrado em `/app/memory/PRD.md`

---

**FIM DO REGISTRO.**
