# Auditoria de Rollback — SoulNutri V3.6 Famílias Visuais
**Data da auditoria:** 05/Fev/2026 (job atual)
**Arquivo de referência:** `/app/memory/diagnostics/rollback_audit_2026-02-05.md`
**Status:** SOMENTE MAPEAMENTO. Zero alterações aplicadas.

---

## PARTE 1 — TODOS OS COMMITS (27/Abr até hoje)

Legenda: `[CODE]` = altera código fonte | `[DOC]` = apenas documentação | `[META]` = apenas .emergent/.gitignore

| # | Hash | Data/Hora (UTC) | Tipo | Arquivos alterados | Famílias? |
|---|------|-----------------|------|--------------------|-----------|
| 1 | `05f8004` | 29/Abr 13:56 | META | .emergent/emergent.yml, .gitignore | NÃO |
| 2 | `f1b460f` | 29/Abr 13:22 | **CODE** | **server.py, App.js, ai/families.py, ai/policy.py, scripts/migrate_families_v1.py, PRD.md** | ⚠️ **SIM — ORIGEM** |
| 3 | `72b01a7` | 29/Abr 12:56 | DOC | memory/diagnostics/visual_families_validation_2026-02-05.md, PRD.md | NÃO |
| 4 | `a484b41` | 29/Abr 12:37 | DOC | .emergent/summary.txt, RELATORIO*.txt, backend/tests/*.py (apenas 2 linhas em cada) | NÃO |
| 5 | `80d2b5d` | 29/Abr 11:55 | DOC | memory/diagnostics/family_validation_empirical_2026-04-29.md | NÃO |
| 6 | `45984fb` | 29/Abr 11:24 | DOC | memory/diagnostics/family_grouping_study_2026-04-29.md | NÃO |
| 7 | `1a014ef` | 28/Abr 20:31 | META | .emergent/emergent.yml, .gitignore | NÃO |
| 8 | `6df6e6e` | 28/Abr 20:31 | META | .emergent/emergent.yml, .gitignore | NÃO |
| 9 | `a929526` | 28/Abr 20:28 | **CODE** | **server.py** (adicionou /api/debug/version) | NÃO |
| 10 | `86f0af6` | 28/Abr 20:17 | META | .emergent/emergent.yml, .gitignore | NÃO |
| 11 | `01768a3` | 28/Abr 20:10 | **CODE** | **ai/embedder.py** (gc.collect flags), **server.py** (-49 debug prints) | NÃO |
| 12 | `a633500` | 28/Abr 19:27 | META | .emergent/emergent.yml, .gitignore | NÃO |
| 13 | `183eaf1` | 28/Abr 19:24 | **CODE** | **ai/index.py** (+2/-1), **server.py** (-49 debug prints Fase 1) | NÃO |
| 14 | `d61e097` | 28/Abr 19:16 | DOC | memory/diagnostics/regressions_analysis_2026-04-28.md | NÃO |
| 15 | `66f4ca2` | 28/Abr 19:04 | DOC | memory/diagnostics/arch_gpu_vs_wasm, bug_camera | NÃO |
| 16 | `9e1abf7` | 28/Abr 11:10 | META | .emergent/emergent.yml | NÃO |
| 17 | `31e42b1` | 28/Abr 11:07 | **CODE** | **App.js** (R3: 82%/512px), **CheckinRefeicao.jsx** (R3 normalizeImage) | NÃO |
| 18 | `5cc7b09` | 28/Abr 11:00 | DOC | memory/diagnostics/r3_compression_study_2026-04-28.md | NÃO |
| 19 | `c59a862` | 28/Abr 10:55 | META | .emergent/emergent.yml | NÃO |
| 20 | `e3c4185` | 28/Abr 10:49 | DOC | memory/diagnostics/perf_scan_2026-04-28.md | NÃO |
| 21 | `13b3848` | 28/Abr 10:40 | **CODE** | **WeeklyReport.jsx** (+renderTextSafe), **NotificationPanel.jsx** (+renderTextSafe), PRD.md | NÃO |
| 22 | `c308304` | 28/Abr 10:33 | DOC | memory/stable-2026-04-27-vercel-frontend-render-backend-taco-v2.md (criação) | NÃO |
| 23 | `3d3c049` | 28/Abr 09:42 | DOC | memory/PRD.md | NÃO |
| 24 | `747d210` | 27/Abr 17:10 | META | .emergent/emergent.yml, .gitignore | NÃO |
| 25 | `33e86d9` | 27/Abr 17:06 | **CODE** | **taco_database.py** (fixos), **services/usda_fallback.py** (novo serviço USDA) | NÃO |
| 26 | `35cf013` | 27/Abr 16:34 | **CODE** | **taco_database.py** (correções TACO v2) | NÃO |
| 27 | `adbafaf` | 27/Abr 15:46 | **CODE** | **taco_database.py** (correções TACO v2) | NÃO |

**Deploy status:** O Render relata `RENDER_GIT_COMMIT = 05f8004` → último deploy inclui `f1b460f` (Famílias Visuais).

---

## PARTE 2 — VERSÕES SALVAS NO EMERGENT

O Emergent não mantém um histórico de "versões nomeadas" acessível via API — apenas o arquivo `.emergent/emergent.yml` que registra apenas o job_id e data do job atual. As "versões" são os commits no GitHub.

**Referências encontradas no codebase:**
- `memory/stable-2026-04-27-vercel-frontend-render-backend-taco-v2.md` — documento de referência criado em `c308304` (28/Abr 10:33), documenta o estado estável de 27/Abr.

**Versões funcionais documentadas:**
| Tag informal | Commit mais próximo | Descrição | Contém Famílias? |
|---|---|---|---|
| `stable-2026-04-27` | `33e86d9` | TACO v2 + USDA fallback, Vercel+Render | NÃO |
| `react-31-fix` | `31e42b1` | R3 compressão + React Error #31 (App.js) | NÃO |
| `fase1-performance` | `183eaf1` | Remove debug prints, latência <800ms | NÃO |
| `fase2-performance` | `01768a3` | gc.collect flags (embedder.py) | NÃO |
| `debug-version` | `a929526` | /api/debug/version adicionado | NÃO |
| **`v3.6-familias`** | `f1b460f` | **FAMÍLIAS VISUAIS — origem dos problemas** | **SIM** |

---

## PARTE 3 — CANDIDATOS DE ROLLBACK

### Candidato A — Último estável antes das Famílias (RECOMENDADO)
**Commit:** `a929526` (28/Abr 20:28)

**Contém:**
- ✅ Arquitetura Vercel + Render (desde muito antes)
- ✅ TACO v2 corrigido (`adbafaf`, `35cf013`, `33e86d9`)
- ✅ USDA fallback service (`33e86d9`)
- ✅ React Error #31 corrigido (WeeklyReport, NotificationPanel via `13b3848`)
- ✅ R3 compressão client-side (App.js 82%/512px via `31e42b1`, CheckinRefeicao via `31e42b1`)
- ✅ Fase 1 performance (remove debug prints — `183eaf1`)
- ✅ Fase 2 performance (gc.collect condicional — `01768a3`)
- ✅ /api/debug/version (próprio commit)
- ❌ NÃO contém Famílias Visuais
- ❌ NÃO contém family_match no identify

---

### Candidato B — Fase 2 Performance (sem debug/version)
**Commit:** `01768a3` (28/Abr 20:10)

**Contém:** Igual ao A, exceto que não tem /api/debug/version
**Perde:** endpoint de auditoria de deploy (pode ser recriado facilmente)
**Recomendação:** Inferior ao candidato A. Preferir A.

---

### Candidato C — R3 + React #31 base
**Commit:** `31e42b1` (28/Abr 11:07)

**Contém:**
- ✅ Arquitetura Vercel + Render
- ✅ TACO v2 + USDA fallback
- ✅ React Error #31 parcial (App.js + CheckinRefeicao, mas WeeklyReport/NotificationPanel via `13b3848` ainda não aplica)
- ✅ R3 compressão
- ❌ SEM React #31 em WeeklyReport/NotificationPanel (esse fix veio em `13b3848` antes de `31e42b1`... aguarda verificação)

**Nota:** `13b3848` (10:40) é ANTERIOR a `31e42b1` (11:07). Portanto `31e42b1` JÁ inclui o fix de WeeklyReport/NotificationPanel. Candidato C está OK em React #31.
**Perde:** Fase 1, Fase 2 performance, /api/debug/version
**Recomendação:** Inferior ao Candidato A.

---

### Candidato D — stable-2026-04-27-vercel-frontend-render-backend-taco-v2
**Commit:** `33e86d9` ou `747d210` (27/Abr 17:06-17:10)

**Contém:**
- ✅ Arquitetura Vercel + Render
- ✅ TACO v2 + USDA fallback
- ❌ SEM React Error #31 fix (veio em Apr 28)
- ❌ SEM R3 compressão (veio em Apr 28)
- ❌ SEM Fase 1 e Fase 2 performance
- ❌ SEM /api/debug/version
**Recomendação:** O mais conservador, mas perde 3 dias de melhorias. Usar apenas se A falhar.

---

## PARTE 4 — ANÁLISE DETALHADA DOS CANDIDATOS

| Critério | A (`a929526`) | B (`01768a3`) | C (`31e42b1`) | D (`33e86d9`) |
|---|---|---|---|---|
| Arquitetura Vercel+Render | ✅ | ✅ | ✅ | ✅ |
| TACO v2 | ✅ | ✅ | ✅ | ✅ |
| USDA fallback | ✅ | ✅ | ✅ | ✅ |
| React Error #31 | ✅ | ✅ | ✅ | ❌ |
| R3 compressão | ✅ | ✅ | ✅ | ❌ |
| Fase 1 performance | ✅ | ✅ | ❌ | ❌ |
| Fase 2 performance | ✅ | ❌ | ❌ | ❌ |
| /api/debug/version | ✅ | ❌ | ❌ | ❌ |
| **Famílias Visuais** | ❌ | ❌ | ❌ | ❌ |
| family_match no identify | ❌ | ❌ | ❌ | ❌ |
| FamilyConfirmationModal | ❌ | ❌ | ❌ | ❌ |
| Precisa redeploy Render | SIM | SIM | SIM | SIM |
| Precisa redeploy Vercel | SIM | SIM | SIM | SIM |
| Mexe no MongoDB | ❌ | ❌ | ❌ | ❌ |
| **Risco** | **BAIXO** | BAIXO | MÉDIO | MÉDIO-ALTO |

**O código rollback NÃO reverte o MongoDB.** MongoDB precisa de script separado (Parte 5).

---

## PARTE 5 — ESTADO ATUAL DO MONGODB E ROLLBACK DE BANCO

### O que a migration inseriu/alterou

**Collection `families` (NOVA — criada do zero):**
```
Total: 5 documentos
- fam_milanesa_animal  → dish_ids: [peixe_a_milanesa, frango_a_milanesa, file_mignon_a_milanesa]
- fam_parmegiana_animal → dish_ids: [file_de_frango_a_parmegiana, peixe_a_parmegiana, file_mignon_a_parmegiana]
- fam_lasanha_vegetariano → dish_ids: [lasanha_de_espinafre, lasanha_de_portobello]
- fam_risoto_vegetariano → dish_ids: [risoto_de_alho_poro, risoto_de_pera_e_gorgonzola, risoto_milanes]
- fam_gratinado_animal → dish_ids: [escondidinho_de_carne_seca, bacalhau_com_natas]
```

**Collection `dishes` — campo `family_id` ADICIONADO em 7 documentos existentes:**
```
[normal] peixe-a-milanesa → fam_milanesa_animal
[normal] lasanha-de-espinafre → fam_lasanha_vegetariano
[normal] lasanha-de-portobello → fam_lasanha_vegetariano
[normal] risoto-de-pera-e-gorgonzola → fam_risoto_vegetariano
[normal] risoto-de-alho-poro → fam_risoto_vegetariano
[normal] escondidinho-de-carne-seca → fam_gratinado_animal
[normal] bacalhau-com-natas → fam_gratinado_animal
```

**Collection `dishes` — 5 documentos NOVOS inseridos (placeholders):**
```
frango_a_milanesa / Frango à Milanesa (status=placeholder)
file_mignon_a_milanesa / Filé Mignon à Milanesa (status=placeholder)
peixe_a_parmegiana / Peixe à Parmegiana (status=placeholder)
file_mignon_a_parmegiana / Filé Mignon à Parmegiana (status=placeholder)
risoto_milanes / Risoto Milanês (status=placeholder)
```

**Collection `nutrition_sheets` — 1 documento MODIFICADO:**
```
Lasanha de Espinafre: { nutricao_suspeita: true, motivo_suspeita: "kcal=54 é erro" }
```

### Script de Rollback MongoDB (idempotente, seguro)

```javascript
// Executar via MongoDB Compass, Atlas Shell ou mongosh
// ROLLBACK COMPLETO DAS FAMÍLIAS VISUAIS v1

// 1. Remover collection families inteira (criada do zero — sem dados originais)
db.families.drop();

// 2. Remover campo family_id de dishes existentes (não apaga o dish, apenas remove o campo)
db.dishes.updateMany(
  { family_id: { $exists: true }, status: { $ne: "placeholder" } },
  { $unset: { family_id: "" } }
);

// 3. Apagar placeholder dishes (criados do zero — não existiam antes)
db.dishes.deleteMany({ status: "placeholder" });

// 4. Remover flag de suspeita nutricional (campo adicionado, não altera kcal original)
db.nutrition_sheets.updateMany(
  { nutricao_suspeita: true },
  { $unset: { nutricao_suspeita: "", motivo_suspeita: "" } }
);

// VERIFICAÇÃO:
db.families.countDocuments();       // deve retornar 0
db.dishes.countDocuments({ family_id: { $exists: true } }); // deve retornar 0
db.dishes.countDocuments({ status: "placeholder" });         // deve retornar 0
```

**Garantias do script:**
- ✅ NÃO altera kcal, ingredientes ou fichas nutricionais originais
- ✅ NÃO apaga dishes originais (apenas remove o campo `family_id`)
- ✅ Idempotente (rodar 2x não causa dano)
- ✅ Reversível (a migration pode ser re-executada depois)

---

## PARTE 6 — RECOMENDAÇÃO FINAL

### Melhor ponto de rollback: `a929526` (Candidato A)

**Por quê?**
- É o commit mais recente que NÃO contém código de Famílias Visuais
- Preserva TUDO que o usuário listou: Fase 1, Fase 2, R3, React #31, TACO v2, Vercel+Render
- Inclui o endpoint /api/debug/version que é crítico para auditoria de deploy
- Risco BAIXO — apenas reverte 4 commits de código (`f1b460f` que é o único com código relevante)

---

### Plano de Rollback em Etapas

**ATENÇÃO: Não executar até receber confirmação explícita.**

#### ETAPA 1 — Rollback de código (via plataforma Emergent)
```
Usar o botão "Rollback" na interface Emergent, selecionando o checkpoint:
  → commit: a929526 (28/Abr 20:28 UTC)
  → OU usar "Save to Github" para reverter manualmente
```
- Render vai receber webhook → auto-redeploy
- Vercel vai receber webhook → auto-redeploy
- Estimativa: 3-8 minutos

#### ETAPA 2 — Verificar deploy (OBRIGATÓRIO antes do passo 3)
```bash
curl https://soulnutri-v3wd.onrender.com/api/debug/version
# Esperado: git_commit deve ser a929526xxxxxx
# NUNCA avançar para Etapa 3 sem confirmar que o commit no ar é o correto
```

#### ETAPA 3 — Rollback do MongoDB (apenas após confirmar Etapa 2)
Executar o script da Parte 5 via MongoDB Compass ou Atlas Shell.

#### ETAPA 4 — Validação pós-rollback
1. ✅ `/api/debug/version` retorna commit `a929526` ou anterior
2. ✅ `/api/ai/identify` retorna resultado SEM campo `family_match`
3. ✅ Frontend (Vercel) não mostra `FamilyConfirmationModal`
4. ✅ Scan de prato funciona e adiciona ao diário (fluxo Premium)
5. ✅ `db.families.countDocuments()` = 0
6. ✅ `db.dishes.countDocuments({family_id: {$exists: true}})` = 0

---

## PARTE 7 — RISCOS E OBSERVAÇÕES

### Risco 1 — Cache BuildKit do Render (RECORRENTE)
Mesmo após rollback de código, o Render pode continuar servindo o código antigo (V3.6) devido ao bug de cache Docker. **Verificação mandatória:** `/api/debug/version` deve retornar o hash correto. Se não retornar, usar "Clear build cache & deploy" no dashboard do Render.

### Risco 2 — MongoDB independente do código
O rollback de código NÃO reverte o MongoDB. O campo `family_id` em dishes continuará existindo após o rollback de código. O código de `a929526` NÃO usa `family_id` (não tem a lógica de family_match), então os campos extras no MongoDB são **inofensivos** — não causam erro, apenas são ignorados. Porém, os 5 placeholder dishes aparecem no admin panel e podem confundir. Executar o script MongoDB é recomendado.

### Risco 3 — Script MongoDB no Atlas (prod)
Se o usuário não tem acesso ao MongoDB Compass/Atlas Shell, o script pode ser executado via um endpoint temporário de admin (criado e deletado em seguida). Não executar direto em prod sem confirmar o ambiente de conexão.

### Risco 4 — family_id em dishes "normais" é inofensivo
Os 7 dishes normais (lasanha, risoto, etc.) que receberam `family_id` continuarão funcionando normalmente após rollback de código. O código em `a929526` simplesmente ignora o campo. Não há risco de regressão nutricional.

---

## RESUMO EXECUTIVO

```
SITUAÇÃO ATUAL: V3.6 com Famílias Visuais deployado no Render
PROBLEMAS RELATADOS: "Vários problemas nos testes"
ROLLBACK RECOMENDADO: commit a929526 (28/Abr 20:28 UTC)
PRESERVE: Fase 1+2, R3, React #31, TACO v2, USDA, debug/version, Vercel+Render
REVERTE: family_match, FamilyConfirmationModal, migrate_families_v1.py, policy quiabo fix, families.py Strogonoff fix
MONGODB: Requer script de limpeza separado (5 minutos)
RISCO GERAL: BAIXO — apenas 1 commit de código relevante a reverter (f1b460f)
TEMPO ESTIMADO: 10-15 minutos (rollback + redeploy + verificação)
```
