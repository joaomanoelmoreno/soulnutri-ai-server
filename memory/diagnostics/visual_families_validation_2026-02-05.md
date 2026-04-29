# Validação Estratégica — Famílias Visuais SoulNutri
**Data:** 05/Fev/2026
**Status:** DOCUMENTO DE VALIDAÇÃO. Zero patches. Zero alterações no banco/código/IA.
**Gerado por:** Análise do codebase completo (`server.py`, `ai/families.py`, `ai/policy.py`, `ai/index.py`, `/app/datasets/organized/`)

---

## PARTE 1 — LISTA FINAL DE FAMÍLIAS APROVADAS

### Resumo Executivo das 5 Famílias

| # | family_id | Nome Canônico | Categoria | kcal_range | Estimado? | Dropdown Obrigatório? |
|---|---|---|---|---|---|---|
| 1 | `fam_milanesa_animal` | Milanesa (Frango/Peixe/Filé Mignon) | proteína animal | 150–200 | ✅ sim | ✅ sim |
| 2 | `fam_parmegiana_animal` | Parmegiana (Frango/Peixe/Filé Mignon) | proteína animal | 160–185 | ⚠️ parcial | ✅ sim |
| 3 | `fam_lasanha_vegetariano` | Lasanha | vegetariano | 230–230 | ✅ sim | ✅ sim |
| 4 | `fam_risoto_vegetariano` | Risoto | vegetariano | 220–260 | ✅ sim | ✅ sim |
| 5 | `fam_gratinado_animal` | Gratinado Animal | proteína animal | 112–231 | ❌ não | ✅ sim |

**NÃO CRIADAS (monoitem):**
- Gratinado Vegano → "Alho Poro Gratinado" (1 prato apenas) — manter como dish individual, registrar como candidato futuro.

---

## PARTE 2 — JSON COMPLETO DA COLLECTION `families`

```json
[
  {
    "family_id": "fam_milanesa_animal",
    "family_name": "Milanesa (Frango/Peixe/Filé Mignon)",
    "category": "proteína animal",
    "kcal_min": 150,
    "kcal_max": 200,
    "kcal_estimated": true,
    "kcal_estimation_note": "Faixa provisória. Recalcular após criar ficha nutricional do Filé Mignon à Milanesa.",
    "require_confirmation": true,
    "dish_ids": [
      "Peixe a Milanesa"
    ],
    "dish_ids_pending_creation": [
      "Frango a Milanesa",
      "File Mignon a Milanesa"
    ],
    "alergenos_consolidados": ["gluten", "ovo", "peixe"],
    "alergenos_note": "Política conservadora: alergênico presente se QUALQUER subitem contiver. Filé Mignon não contém peixe, mas Peixe à Milanesa sim.",
    "created_at": null,
    "status": "pendente_dishes_faltando"
  },
  {
    "family_id": "fam_parmegiana_animal",
    "family_name": "Parmegiana (Frango/Peixe/Filé Mignon)",
    "category": "proteína animal",
    "kcal_min": 160,
    "kcal_max": 185,
    "kcal_estimated": false,
    "kcal_estimation_note": "Baseado no Filé de Frango à Parmegiana (~174 kcal). Expandir ao incluir Peixe e Filé Mignon.",
    "require_confirmation": true,
    "dish_ids": [
      "Filé de Frango à Parmegiana"
    ],
    "dish_ids_pending_creation": [
      "Peixe a Parmegiana",
      "File Mignon a Parmegiana"
    ],
    "alergenos_consolidados": ["gluten", "ovo", "lactose", "peixe"],
    "alergenos_note": "Política conservadora: peixe incluído pois Peixe à Parmegiana estará na família futuramente.",
    "created_at": null,
    "status": "pendente_dishes_faltando"
  },
  {
    "family_id": "fam_lasanha_vegetariano",
    "family_name": "Lasanha",
    "category": "vegetariano",
    "kcal_min": 230,
    "kcal_max": 230,
    "kcal_estimated": true,
    "kcal_estimation_note": "VALOR PROVISÓRIO. Lasanha de Espinafre tem 54 kcal cadastrada — ERRO GRAVE. Lasanha de Portobello tem 252 kcal. Usando 230 kcal/100g como provisório até revisão nutricional completa.",
    "require_confirmation": true,
    "dish_ids": [
      "Lasanha de Espinafre",
      "Lasanha de Portobello"
    ],
    "dish_ids_pending_creation": [],
    "alergenos_consolidados": ["gluten", "lactose"],
    "alergenos_note": "Ambas as lasanhas contêm glúten (massa) e lactose (queijo/molho branco). Sem diferença de alergênicos entre subitens.",
    "dish_flags": {
      "Lasanha de Espinafre": {
        "nutricao_suspeita": true,
        "motivo": "kcal cadastrada = 54 kcal/100g (impossível para lasanha com massa+queijo+molho branco). Pendente revisão nutricional.",
        "acao_recomendada": "Revisar ficha nutricional via admin ou rodar batch_force_taco.py com force=True"
      }
    },
    "created_at": null,
    "status": "ativo_provisorio"
  },
  {
    "family_id": "fam_risoto_vegetariano",
    "family_name": "Risoto",
    "category": "vegetariano",
    "kcal_min": 220,
    "kcal_max": 260,
    "kcal_estimated": true,
    "kcal_estimation_note": "Faixa provisória baseada em Risoto de Alho Poró (228 kcal) e Risoto de Pera e Gorgonzola (247 kcal). Risoto Milanês é placeholder sem ficha nutricional.",
    "require_confirmation": true,
    "dish_ids": [
      "Risoto de Alho Poro",
      "Risoto de Pera e Gorgonzola"
    ],
    "dish_ids_pending_creation": [
      "Risoto Milanes"
    ],
    "dish_placeholder": {
      "Risoto Milanes": {
        "image_url": null,
        "kcal_estimado": 240,
        "status": "pendente_foto_e_revisao",
        "nota": "Criar como dish no MongoDB com status=placeholder. Não incluir no índice CLIP até ter imagens."
      }
    },
    "alergenos_consolidados": ["lactose"],
    "alergenos_note": "Risoto de Pera e Gorgonzola contém lactose (gorgonzola). Risoto de Alho Poró pode conter lactose (manteiga). Política conservadora: marcar lactose para toda a família.",
    "created_at": null,
    "status": "ativo_provisorio"
  },
  {
    "family_id": "fam_gratinado_animal",
    "family_name": "Gratinado Animal",
    "category": "proteína animal",
    "kcal_min": 112,
    "kcal_max": 231,
    "kcal_estimated": false,
    "kcal_estimation_note": "Dados reais: Escondidinho de Carne Seca = 231 kcal/100g. Bacalhau com Natas = 112 kcal/100g. Spread de 68% — ALTO. Confirmação obrigatória.",
    "require_confirmation": true,
    "dish_ids": [
      "Escondidinho de Carne Seca",
      "Bacalhau com Natas"
    ],
    "dish_ids_pending_creation": [],
    "alergenos_consolidados": ["lactose", "peixe"],
    "alergenos_note": "Bacalhau com Natas: peixe + lactose. Escondidinho: lactose. Política conservadora: peixe marcado para toda família.",
    "created_at": null,
    "status": "ativo_provisorio",
    "conflito_critico": "Ver PARTE 4, Conflito 3: 'Bacalhau com Natas' existe na policy.py mas o FOLDER do dataset é 'Bacalhau a Bras' (prato diferente). Requer confirmação antes de vincular dish_id."
  }
]
```

---

## PARTE 3 — DISHES QUE RECEBERÃO `family_id` (COM STATUS)

### 3.1 Dishes existentes no dataset (`/app/datasets/organized/`)

| Dish (nome do folder) | family_id a vincular | Status no sistema | Observações |
|---|---|---|---|
| `Peixe a Milanesa` | `fam_milanesa_animal` | ✅ CLIP index + pasta | Único membro atual da família Milanesa |
| `Filé de Frango à Parmegiana` | `fam_parmegiana_animal` | ✅ policy.py (`filedefrangoaparmegiana`) | Único membro atual da família Parmegiana |
| `Lasanha de Espinafre` | `fam_lasanha_vegetariano` | ✅ CLIP index + pasta | ⚠️ FICHA NUTRICIONAL SUSPEITA (54 kcal) |
| `Lasanha de Portobello` | `fam_lasanha_vegetariano` | ✅ CLIP index + pasta | Valor nutricional OK (252 kcal) |
| `Risoto de Alho Poro` | `fam_risoto_vegetariano` | ✅ CLIP index + pasta | Valor OK (228 kcal) |
| `Risoto de Pera e Gorgonzola` | `fam_risoto_vegetariano` | ✅ CLIP index + pasta | Nome completo: "Pera e Gorgonzola" (não só "Pera") |
| `Escondidinho de Carne Seca` | `fam_gratinado_animal` | ✅ CLIP index + pasta | Valor OK (231 kcal) |
| `Bacalhau com Natas` | `fam_gratinado_animal` | ⚠️ CONFLITO — ver Parte 4 | Existe em policy.py, mas folder é "Bacalhau a Bras" |

### 3.2 Dishes a criar (não existem ainda)

| Dish (novo) | family_id | Tipo | Ação necessária |
|---|---|---|---|
| `Frango a Milanesa` | `fam_milanesa_animal` | dish real | Criar ficha + fotos + ficha nutricional |
| `File Mignon a Milanesa` | `fam_milanesa_animal` | dish real | Criar ficha + fotos + ficha nutricional |
| `Peixe a Parmegiana` | `fam_parmegiana_animal` | dish real | Criar ficha + fotos + ficha nutricional |
| `File Mignon a Parmegiana` | `fam_parmegiana_animal` | dish real | Criar ficha + fotos + ficha nutricional |
| `Risoto Milanes` | `fam_risoto_vegetariano` | placeholder | Criar no MongoDB sem foto (image_url=null) |

### 3.3 Dishes que NÃO receberão family_id

| Dish | Motivo |
|---|---|
| `Alho Poro Gratinado` | Monoitem na categoria vegano — candidato futuro |
| `Berinjela a Parmegiana` | Categoria VEGANO — NÃO pertence à família Parmegiana Animal |
| `Brocolis e ou Couve Flor Gratinado` | Monoitem vegetariano — candidato futuro |
| `Strogonoff (Frango Carne ou Vegano)` | Viola R1 (mistura vegano+animal) — pendente revisão |
| `Bacalhau a Bras` | Prato diferente de "Bacalhau com Natas" — ver Conflito 3 |
| `Jiló Empanado` | Vegetariano, categoria diferente da Milanesa Animal |
| `Quiabo Empanado` | Ver Conflito 5 (erro de categoria na policy.py) |

---

## PARTE 4 — IDENTIFICAÇÃO DE CONFLITOS

### Conflito 1 — CRÍTICO: Spread extremo em Gratinado Animal (68%)

**Problema:** kcal varia de 112 (Bacalhau com Natas) a 231 (Escondidinho de Carne Seca) — diferença de 106%.
- Se usuário não confirmar subtipo: valor padrão deveria ser a MÉDIA (171 kcal), não o máximo nem o mínimo.
- Se usuário Premium adicionar ao diário sem confirmar: erro de até 106% no registro calórico.

**Impacto:** ALTO para usuários Premium com contagem calórica rigorosa.
**Mitigação:** `require_confirmation: true` + bloquear salvamento sem dropdown selecionado.
**Ação na UI:** Exibir obrigatoriamente: "Este prato tem variação calórica significativa (112–231 kcal). Confirme o subtipo antes de salvar."

---

### Conflito 2 — ALTO: Lasanha de Espinafre com 54 kcal/100g

**Problema:** Valor nutricional obviamente incorreto. Uma lasanha típica com massa+queijo+molho branco tem 250–350 kcal/100g. O valor de 54 kcal/100g indica falha no cálculo proporcional do `calcular_nutricao_prato()` (possivelmente ingrediente ausente ou proporção errada).

**Impacto:** Se qualquer lógica usar o valor individual da Lasanha de Espinafre, o usuário recebe dado gravemente incorreto.

**Decisão do usuário:** Usar 230 kcal/100g como provisório para a família inteira.
**Ação necessária (FUTURA):** 
1. Verificar a ficha em `nutrition_sheets` via endpoint `/admin/dishes/lasanha_de_espinafre`
2. Revisar ingredientes e proporções em `taco_database.py`
3. Rodar `batch_force_taco.py` com `force=True` para este prato específico

**Flag a criar no document de dishes:**
```json
{
  "slug": "lasanha_de_espinafre",
  "nutricao_suspeita": true,
  "motivo": "kcal = 54 kcal/100g (valor impossível)",
  "revisao_pendente": true
}
```

---

### Conflito 3 — CRÍTICO: "Bacalhau com Natas" vs "Bacalhau a Bras"

**Problema:** 
- `DISH_FAMILIES` em `families.py` (linha 30) cita "Bacalhau com Natas"
- `DISH_INFO` em `policy.py` (linha 39) tem slug `bacalhaucomnatas` → 'Bacalhau com Natas'
- **MAS** o folder em `/app/datasets/organized/` é `Bacalhau a Bras` (prato completamente diferente)

**"Bacalhau com Natas"** = bacalhau desfiado + batata + creme de leite (gratinado)
**"Bacalhau à Brás"** = bacalhau desfiado + batata palha + ovos mexidos (frito/refogado, NÃO gratinado)

**Impacto na Família Gratinado Animal:**
- Se vincularmos `bacalhau_a_bras` à família Gratinado Animal → ERRO CONCEITUAL (Brás não é gratinado)
- Se vincularmos `bacalhau_com_natas` → o dish existe na policy.py mas NÃO tem imagens no CLIP index

**Decisão requerida:** Antes de implementar, confirmar com o usuário:
> "O dataset tem 'Bacalhau a Bras' (Brás). Para a família Gratinado Animal, você quer usar o 'Bacalhau com Natas' (gratinado) — que existe em policy.py mas não tem pasta com imagens — ou reclassificar 'Bacalhau a Bras' como o representante da família?"

---

### Conflito 4 — MÉDIO: Alergênicos cruzados por política conservadora

**Problema:** A política de "marcar alergênico se qualquer subitem contiver" impõe falsos positivos para alguns usuários.

Exemplo: Família Milanesa Animal
- Peixe à Milanesa → contém peixe
- Frango à Milanesa → NÃO contém peixe
- Filé Mignon à Milanesa → NÃO contém peixe

Se marcarmos "peixe" para toda a família, um usuário com restrição a peixe vai receber alerta mesmo escolhendo "Frango à Milanesa" no dropdown.

**Solução proposta (FUTURA):** Alergênicos devem ser POR SUBITEM, não por família.
Na fase de implementação, o payload do dropdown deve retornar:
```json
{
  "subitem": "Frango a Milanesa",
  "alergenos": ["gluten", "ovo"],
  "alergenos_ausentes_na_familia": ["peixe"]
}
```

**Para a fase atual (MVP):** Usar alerta de família consolidado com nota: "Alergênicos variam por subtipo. Confirme para ver detalhes."

---

### Conflito 5 — MÉDIO: Erro de categoria em `policy.py`

**Problema:** `policy.py` linha 228:
```python
'quiaboempanado': 'proteína animal',
```
Quiabo Empanado é um VEGETAL empanado. Categoria correta: `vegetariano` (contém ovo e glúten) ou `vegano` (se sem ovo). A política.py atualmente mistura vegetariano (`jiloempanado`) com animal (`quiaboempanado`) para pratos empanados da mesma natureza.

**Impacto:** Usuários veganos/vegetarianos que filtram por categoria podem ver Quiabo Empanado como "proteína animal".

**Ação futura:** Corrigir `'quiaboempanado': 'vegetariano'` em policy.py (aguarda autorização do usuário para patch).

---

### Conflito 6 — BAIXO: Strogonoff viola Regra R1

**Problema:** `families.py` linha 93-96:
```python
"Strogonoffs": [
    "Estrogonofe de File Mignon",
    "Strogonoff Vegano",
    "Strogonoff de File Mignon",
],
```
Esta família mistura "proteína animal" com "vegano" — viola diretamente a R1 (nunca misturar categorias nutricionais).

**Impacto:** Usuários veganos que escaneiam Strogonoff Vegano podem receber dados de proteína animal (ou vice-versa).

**Ação futura:** Separar em duas famílias:
- "Strogonoffs Animais" → [Estrogonofe de File Mignon, Strogonoff de File Mignon]
- "Strogonoff Vegano" → dish individual (sem família, monoitem)

---

## PARTE 5 — IMPACTO ESPERADO NO BACKEND (`/api/ai/identify`)

### 5.1 Situação atual

O endpoint já possui os campos de resposta preparados para famílias:
```python
# server.py linhas 1194-1197
"family_name": decision.get('family_name'),
"family_candidates": decision.get('family_candidates', []),
"family_candidates_detail": decision.get('family_candidates_detail', []),
```
O `families.py` já tem `detect_family_ambiguity()` que detecta quando top-K resultados do CLIP pertencem à mesma família.

### 5.2 O que precisa ser adicionado (FUTURA IMPLEMENTAÇÃO)

**Passo A — Consulta MongoDB para família:**
Após o CLIP retornar o top-1, buscar se o prato tem `family_id` na coleção `dishes`:
```python
# PSEUDOCÓDIGO (não implementar ainda)
dish_doc = await db.dishes.find_one({"name": dish_display_name}, {"_id": 0, "family_id": 1})
if dish_doc and dish_doc.get("family_id"):
    family = await db.families.find_one({"family_id": dish_doc["family_id"]}, {"_id": 0})
```

**Passo B — Formato de resposta com família:**
```python
# PSEUDOCÓDIGO
"family_match": {
    "family_id": family["family_id"],
    "family_name": family["family_name"],
    "kcal_range": f"{family['kcal_min']}–{family['kcal_max']} kcal/100g",
    "kcal_estimated": family["kcal_estimated"],
    "require_confirmation": family["require_confirmation"],
    "subitems": [
        {
            "dish_id": d,
            "display_name": <nome_formatado>,
            "alergenos": <alergenos_do_subitem>
        }
        for d in family["dish_ids"]
    ]
}
```

**Passo C — Lógica de bloqueio:**
O backend NÃO deve salvar no diário Premium se `require_confirmation=true` e nenhum subitem foi confirmado.
O frontend é responsável pela UX do dropdown, mas o backend deve VALIDAR antes de salvar:
```python
# PSEUDOCÓDIGO — endpoint de salvar no diário
if dish_has_family and require_confirmation and not confirmed_subitem_id:
    raise HTTPException(422, "Confirme o subtipo do prato antes de salvar")
```

**Latência esperada:** +5–15ms por query adicional ao MongoDB (família + alergênicos). Aceitável.

**Modo Cibi Sana vs Externo:**
- Cibi Sana (CLIP): detecção de família pelo índice + query MongoDB → retorna `family_match`
- Externo (Gemini): Gemini não conhece as famílias do Cibi Sana → `family_match=null` (sem família)

---

## PARTE 6 — IMPACTO ESPERADO NO FRONTEND

### 6.1 Novo componente: `FamilyConfirmationCard`

**Trigger:** Quando `identify` retorna `family_match != null` E `require_confirmation=true`

**Comportamento:**
```
┌─────────────────────────────────────────────────────┐
│  ⚠️  Identificado: Prato Gratinado                  │
│                                                     │
│  Variação calórica: 112–231 kcal/100g               │
│  Para registrar corretamente, confirme o subtipo:   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  [Selecione o prato]                    ▼   │   │
│  │  ○ Escondidinho de Carne Seca (231 kcal)    │   │
│  │  ○ Bacalhau com Natas (112 kcal)            │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  [Cancelar]              [Confirmar e Salvar] 🔒    │
│                                                     │
│  🔒 Botão bloqueado até selecionar subtipo          │
└─────────────────────────────────────────────────────┘
```

**Regras de UX:**
1. Dropdown obrigatório — `[Confirmar e Salvar]` desabilitado até seleção
2. Ao selecionar, atualizar kcal exibida para o valor do subitem
3. Se `kcal_estimated=true`, exibir badge "estimado" ao lado do valor
4. Após confirmação, salvar `confirmed_dish_id` (não o `family_id`) no diário

### 6.2 Mudanças no fluxo de scan existente

**Fluxo atual:**
```
Foto → CLIP → dish_display → (se Premium) → salvar no diário
```

**Fluxo novo (com família):**
```
Foto → CLIP → dish_display → checar family_match
                                  ├─ family_match=null → fluxo normal (sem mudança)
                                  └─ family_match=presente → mostrar FamilyConfirmationCard
                                                               ├─ usuário confirma → usar confirmed_dish_id
                                                               └─ usuário cancela → manter dish original
```

**Arquivos a modificar (FUTURAMENTE):**
- `App.js`: adicionar lógica de verificação de `family_match` após `identify`
- Novo componente: `FamilyConfirmationCard.jsx`
- Nenhuma mudança no endpoint `identify` existente (compatibilidade retroativa)

---

## PARTE 7 — PLANO DE ROLLBACK COMPLETO

### 7.1 Estratégia de rollback — Princípio dual-write

A implementação usa schema **aditivo**: adiciona campos novos sem remover ou sobrescrever campos existentes.

```
dishes (antes)          dishes (depois)
─────────────────       ─────────────────────────
{ slug, name, ... }  →  { slug, name, ..., family_id }
                                             ↑ NOVO campo opcional
```

**Rollback da collection `families`:**
```javascript
// Para desfazer COMPLETAMENTE:
db.families.drop()
db.dishes.updateMany({}, { $unset: { family_id: "" } })
```
Resultado: sistema volta ao comportamento anterior sem nenhuma regressão.

**Rollback do backend:**
```python
# Remover do endpoint identify:
# "family_match": family_match_data  ← apenas remover esta linha
# Nenhum outro código precisa ser revertido
```

**Rollback do frontend:**
```javascript
// Remover o componente FamilyConfirmationCard
// Remover o check: if (result.family_match) ...
// Resto do App.js inalterado
```

### 7.2 Critérios de rollback

| Evento | Ação |
|---|---|
| Usuário Premium reclama que "kcal está errada" após usar família | Verificar se `kcal_estimated=true` — se sim, é comportamento esperado |
| Dropdown não aparece mas deveria | Verificar se `require_confirmation` está `true` na collection families |
| Dropdown aparece para prato que não deveria ser família | Remover `family_id` do dish específico em dishes |
| Regressão crítica: sistema perde dados de dishes existentes | Impossível — implementação é aditiva. Rollback via `$unset` |
| Cache do Render serve versão antiga do backend | Auditar `/api/debug/version` — se necessário: "Clear build cache & deploy" |

### 7.3 Migração idempotente (script futuro)

```python
# PSEUDOCÓDIGO — migration_families_v1.py
# Executar somente após aprovação do usuário + testes em staging

FAMILIES_TO_CREATE = [
    {
        "family_id": "fam_lasanha_vegetariano",
        "family_name": "Lasanha",
        ...
    },
    # ... outras famílias
]

DISH_FAMILY_MAP = {
    "Lasanha de Espinafre": "fam_lasanha_vegetariano",
    "Lasanha de Portobello": "fam_lasanha_vegetariano",
    ...
}

async def run_migration():
    for family in FAMILIES_TO_CREATE:
        # Idempotente: upsert por family_id
        await db.families.update_one(
            {"family_id": family["family_id"]},
            {"$set": family},
            upsert=True
        )
    
    for dish_name, family_id in DISH_FAMILY_MAP.items():
        # Idempotente: apenas adiciona campo, não sobrescreve outros dados
        await db.dishes.update_one(
            {"$or": [
                {"name": {"$regex": f"^{dish_name}$", "$options": "i"}},
                {"slug": dish_name.lower().replace(" ", "_")}
            ]},
            {"$set": {"family_id": family_id}},
            upsert=False  # NUNCA criar dish se não existir
        )
```

---

## PARTE 8 — CHECKLIST PRÉ-IMPLEMENTAÇÃO

Antes de escrever qualquer código, confirmar com o usuário:

### ❓ Perguntas em aberto (requerem decisão)

1. **Bacalhau a Bras vs Bacalhau com Natas** (BLOQUEANTE para Gratinado Animal)
   - O folder do dataset é "Bacalhau a Bras" (não gratinado)
   - O policy.py tem "Bacalhau com Natas" (gratinado)
   - **Decisão requerida:** Usar "Bacalhau com Natas" (sem fotos no CLIP) ou "Bacalhau a Bras" (não é gratinado)?

2. **Parmegiana Animal tem apenas 1 membro atual**
   - Só existe "Filé de Frango à Parmegiana" no sistema
   - "Peixe à Parmegiana" e "Filé Mignon à Parmegiana" não existem
   - **Decisão requerida:** Criar família com 1 membro (e adicionar outros depois) ou esperar ter os 3?

3. **Milanesa Animal tem apenas 1 membro atual**
   - Só existe "Peixe a Milanesa" no dataset CLIP
   - "Frango à Milanesa" e "Filé Mignon à Milanesa" não existem ainda
   - **Decisão requerida:** Criar família com 1 membro ou esperar ter os 3?

4. **Quiabo Empanado — erro de categoria**
   - policy.py lista como 'proteína animal' (erro)
   - Deveria ser 'vegetariano'
   - **Decisão requerida:** Autoriza corrigir este bug ao mesmo tempo que a implementação?

5. **Strogonoff — violação da R1**
   - families.py mistura "proteína animal" com "vegano"
   - **Decisão requerida:** Corrigir families.py (separar) ao mesmo tempo?

### ✅ Pontos validados (sem decisão pendente)

- [x] Schema da collection `families` (validado neste documento)
- [x] Campo `family_id` como adição opcional em `dishes` (sem breaking change)
- [x] Estratégia nutricional: faixa provisória + `kcal_estimated=true` + valor central como default
- [x] UX: dropdown obrigatório + bloqueio de salvamento sem confirmação
- [x] Rollback: dual-write + `$unset` reverte sem regressão
- [x] Lasanha de Espinafre: ficha marcada como suspeita, usar 230 kcal como provisório
- [x] Risoto Milanês: criar como placeholder (image_url=null)
- [x] Gratinado Vegano (Alho Poró): NÃO criar família (monoitem)

---

## PARTE 9 — RESTRIÇÕES MANTIDAS (CONFIRMAÇÃO)

- ❌ Nenhum patch aplicado ao código
- ❌ Banco de dados não alterado
- ❌ CLIP / IA não tocados
- ❌ Frontend não modificado
- ❌ Endpoints não alterados
- ❌ Lógica nutricional existente não alterada
- ❌ Deploy não realizado
- ✅ Apenas análise + validação + documentação de impacto

---

## REFERÊNCIAS TÉCNICAS

- `families.py` existente: `/app/backend/ai/families.py` (303 linhas)
- `policy.py` (slugs, categorias, alergênicos): `/app/backend/ai/policy.py` (1298 linhas)
- `server.py` (endpoint identify, response model): `/app/backend/server.py` (6183 linhas)
- Campos já presentes em IdentifyResponse: `family_name`, `family_candidates`, `family_candidates_detail` (linhas 1194-1197)
- Dataset folders: `/app/datasets/organized/` (~100+ pratos com imagens CLIP)
- Estudo anterior: `/app/memory/diagnostics/family_grouping_study_2026-04-29.md`

---

**FIM DO DOCUMENTO DE VALIDAÇÃO. Aguardando respostas às 5 questões em aberto (Parte 8) para iniciar implementação.**
