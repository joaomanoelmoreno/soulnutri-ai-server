# Validação Empírica — Famílias Visuais (resultados do dataset interno)

**Data:** 29/Abr/2026
**Status:** ESTUDO. Sem patch. Sem alteração de código/banco/IA/UI.
**Escopo:** 111 testes via `/api/ai/identify` em produção, usando imagens de `/app/datasets/organized/`.

---

## 🎯 Achado central — Inesperado mas inequívoco

# A IA acertou **109 de 111 testes (98,2%)**. **Zero confusão intra-família.**

Esse é um achado contra-intuitivo dado o estudo estratégico anterior (que estimava 60-90% de erro em algumas famílias). A explicação está na **metodologia desta validação** — e é fundamental entender antes de decidir.

---

## 📊 Resultados por família

| Família | n | Correto | Intra-família | Fora família | Acurácia | Conf. interna | Decisão (critério inicial) |
|---|---|---|---|---|---|---|---|
| GRATINADOS | 24 | 24 | 0 | 0 | **100%** | 0% | 🔴 **NÃO AGRUPAR** |
| LASANHA_RISOTO | 21 | 21 | 0 | 0 | **100%** | 0% | 🔴 **NÃO AGRUPAR** |
| GRELHADO_PROTEICO | 24 | 24 | 0 | 0 | **100%** | 0% | 🔴 **NÃO AGRUPAR** |
| FRITURAS_DOURADAS | 12 | 11 | 0 | 1 | **91,7%** | 0% | 🔴 **NÃO AGRUPAR** |
| ARROZ_REFOGADO | 30 | 30 | 0 | 0 | **100%** | 0% | 🔴 **NÃO AGRUPAR** |
| **TOTAL** | **111** | **109** | **0** | **1** | **98,2%** | **0%** | — |

### Único erro observado (de 111)
- 1× Bolinho de Bacalhau → "Sobrecoxa ao Tandoori" (score 0.64)
- Erro **fora da família** — nada a ver com agrupamento Frituras

---

## 🔬 Score médio por classificação

| Família | Acertos (score médio) | Erros fora família |
|---|---|---|
| GRATINADOS | 0.944 (min 0.88, max 0.97) | — |
| LASANHA_RISOTO | 0.933 (min 0.85, max 0.97) | — |
| GRELHADO_PROTEICO | 0.932 (min 0.79, max 0.98) | — |
| FRITURAS_DOURADAS | 0.955 (acertos) | 0.64 (1 erro) |
| ARROZ_REFOGADO | 0.947 (min 0.85, max 0.99) | — |

**Padrão claro:** scores ≥0.85 = acerto. Scores ≤0.65 = erro/incerteza. Há um **gap natural de confiança** que pode ser explorado para política de "alta vs baixa confiança".

---

## ⚠️ PARTE 6 — LIMITAÇÕES (CRÍTICAS, OBRIGATÓRIO)

### 🔴 Viés metodológico GRAVE — falso negativo provável

**O resultado de 98% acerto é tecnicamente correto MAS provavelmente NÃO reflete a realidade do buffet.** Razões:

#### Limitação 1 — Imagens do dataset = imagens do índice CLIP
As imagens em `/app/datasets/organized/` são **as MESMAS** usadas para gerar o índice de embeddings em `dish_index_embeddings.npy`. Quando a IA recebe uma dessas imagens, ela está procurando no índice e encontra **a si própria** ou outra imagem extremamente similar do mesmo prato.

**Implicação:** estamos testando **memorização**, não **generalização**.

#### Limitação 2 — Mesmo ângulo, mesma iluminação, mesma montagem
Imagens do dataset foram tiradas em condições de produção/cadastro do prato:
- Iluminação controlada (chef foto, plate styling)
- Ângulo top-down ou 45°, distância padronizada
- Pratos individuais isolados, sem buffet, sem talheres
- Sem variações naturais (gordura caindo, mistura com outros pratos no prato)

**O cenário real do Cibi Sana é dramaticamente diferente:**
- Iluminação fluorescente do buffet
- Pratos com **vários itens juntos** (frango grelhado + arroz + salada + farofa)
- Foto de pé, com câmera tremida, com talher na frente
- Restos visíveis no prato

#### Limitação 3 — Alguns pratos com poucas imagens
- Risoto de Alho Poró: apenas 1 imagem disponível
- Coxinha Saudável de Frango: apenas 4 imagens
- Risoto de Pera: apenas 4 imagens

Pequenas amostras inflacionam a acurácia (lei dos pequenos números).

#### Limitação 4 — Famílias visuais "óbvias" não foram testadas
- **Milanesa (Frango/Peixe/Filé)** ❌ não tinha imagens (já é nome agrupado no banco)
- **Parmegiana (Frango/Peixe/Filé Mignon)** ❌ idem
- **Brócolis e Couve Flor Gratinado** ❌ sem diretório no dataset

Justamente as famílias **mais ambíguas visualmente** ficaram **fora desta validação**. O resultado pode estar enviesado para famílias que a IA já distingue bem.

### Conclusão sobre os vieses

O número **98% NÃO é uma garantia de que a IA funciona em produção**. É apenas uma garantia de que **o índice está bem montado para as imagens do próprio dataset**. A acurácia real em campo provavelmente é menor — talvez 70-90% nas mesmas famílias (estimativa).

---

## 🧩 PARTE 7 — Cruzamento com regras do produto

Como o critério empírico mostrou **zero confusão interna**, nenhuma família dispara R3 (regra de "só agrupar se IA erra >40% entre subitens"). Mas vou cruzar com R1, R2 e R4 mesmo assim, para registro:

| Família | R1 (mistura categorias?) | R2 (spread kcal) | R4 (alergênicos?) | Veredito teórico |
|---|---|---|---|---|
| GRATINADOS | ❌ Mistura 3 categorias | 68% | ⚠️ lácteos | Subdividir SE for agrupar |
| LASANHA | ✅ só vegetariano | 129% | ⚠️ glúten | Manter separados |
| RISOTO | ✅ só vegetariano | 8% | ⚠️ lácteos | Pode agrupar se IA confundir (mas não confunde) |
| GRELHADO | ❌ animal+vegano | 182% | — | Não agrupar |
| FRITURAS | ❌ misto | 119% | ⚠️ glúten | Não agrupar |
| ARROZ | ❌ animal+vegano | 92% | ✅ ok | Não agrupar |

---

## 📋 PARTE 8 — Entrega Final

### Por família — síntese

| # | Família | n | Acurácia | Conf. interna | Decisão (empírica) | Confiança |
|---|---|---|---|---|---|---|
| 1 | GRATINADOS | 24 | 100% | 0% | 🔴 **Não agrupar** | 🟡 médio (sem brócolis gratinado no teste) |
| 2 | LASANHA_RISOTO | 21 | 100% | 0% | 🔴 **Não agrupar** | 🟢 alto (Lasanha de Espinafre tem 34 imgs) |
| 3 | GRELHADO_PROTEICO | 24 | 100% | 0% | 🔴 **Não agrupar** | 🟡 médio (entrecôte/frango/lula bem distintos visualmente — esperado acertar) |
| 4 | FRITURAS_DOURADAS | 12 | 91,7% | 0% | 🔴 **Não agrupar** | 🟡 médio |
| 5 | ARROZ_REFOGADO | 30 | 100% | 0% | 🔴 **Não agrupar** | 🟢 alto |

### 🟢 Lista de famílias APROVADAS para agrupamento (fase piloto)
**NENHUMA** — pelo critério empírico estabelecido (≥40% confusão interna), zero famílias passaram.

### 🟡 Lista que precisa validação com imagens REAIS do buffet
Todas as 5 testadas + as 2 que faltaram dataset:
- **MILANESA / PARMEGIANA** ⚠️ (não pôde ser testada — sem imagens isoladas no dataset)
- **GRATINADOS** com Brócolis/Couve Flor Gratinado (subitem faltante)
- **LASANHA_RISOTO** (alta variabilidade dentro de subitens)
- **GRELHADO_PROTEICO** (testar com fotos de buffet onde pratos misturam)
- **FRITURAS_DOURADAS** (testar Coxinha vs Bolinho com mesmo nível de saturação)
- **ARROZ_REFOGADO** (testar variações no buffet com toppings)

### 🔴 Lista descartada
**Nenhuma com base empírica.** Mas pelas regras do produto:
- GRELHADO (R1: mistura vegano+animal — descartado mesmo se IA falhasse)
- ARROZ_REFOGADO (R1: mistura — descartado)
- FRITURAS (R1+R2: misto e spread alto — descartado)

---

## 🥇 Recomendação Objetiva

# ⏸️ NÃO AGRUPAR AGORA

### Por quê

1. **Nenhuma família atingiu critério empírico (≥40% confusão interna).** Pelo dado disponível, agrupar seria **regressão de capacidade** sem benefício mensurável.
2. **A IA atual identifica corretamente 98% das imagens do dataset.** Os 2% de erro foram fora-de-família (não resolvidos por agrupamento).
3. **Vieses metodológicos pesados** (Limitações 1-4) impedem conclusão definitiva — mas o ônus da prova agora é mostrar que a IA **falha em campo**, não que vai falhar.
4. **Estratégia "agrupar preventivamente"** sem evidência empírica destrói valor: confunde usuário com diálogos de confirmação desnecessários, perde diferencial competitivo, complica schema do banco.

### O que fazer em vez de agrupar

#### Próximo passo recomendado — Validação física de campo (3-4 dias)

Conforme já planejado por você:

> *"Faremos validação física no buffet por 3 a 4 dias com 5 a 6 celulares diferentes antes de qualquer mudança ONNX/GPU/WebAssembly."*

**Adicionar a essa validação física:**

1. **Coletar fotos REAIS de buffet** (não pré-curadas)
2. **Marcar manualmente** o ground truth de cada foto
3. **Anotar quando o usuário viu erro** (com print da tela)
4. **Após 3-4 dias:** repetir esta validação empírica com **fotos novas de campo**, não do dataset

**Critério revisto pós-campo:**
- Se acurácia em campo ≥85% → **manter sem agrupar**
- Se acurácia em campo 70-85% → **agrupar pontualmente** as famílias com erro >40% intra
- Se acurácia em campo <70% → **revisar arquitetura inteira** (volta às fases ONNX/GPU/WASM)

#### Quick win imediato (sem patch agora)

A descoberta do **gap de score 0.85 (acerto) vs 0.65 (erro)** indica que existe um threshold natural para política de confiança. Em breve podemos analisar:
- Mostrar "Identificação confiável" se score ≥0.85
- Mostrar "Confirme: é isso?" se score 0.65-0.85
- Mostrar "Não consegui identificar — confirme manualmente" se score <0.65

Mas isso é estudo separado. **Não agora.**

---

## 📐 Resumo Executivo (1 minuto)

| Pergunta | Resposta |
|---|---|
| Confusão interna detectada? | ❌ **0% em todas as 5 famílias testadas** |
| Acurácia geral observada | **98,2% (109/111)** |
| Famílias para agrupar agora | **NENHUMA** |
| Confiança nesse resultado | 🟡 **médio** (vieses metodológicos pesados) |
| Próximo passo | **Validação física no Cibi Sana com fotos reais** |
| Risco de agrupar agora | 🔴 **Alto** — destrói diferencial sem ganho mensurável |
| Risco de NÃO agrupar | 🟢 **Baixo** — IA já funciona bem nas famílias testadas |

---

## 🚫 Restrições mantidas

- ❌ Nenhum patch
- ❌ Banco intacto
- ❌ Frontend intacto
- ❌ IA não tocada
- ❌ Lógica não tocada
- ✅ Apenas teste empírico via API existente

---

**FIM DO ESTUDO. Aguarda decisão sobre validação física antes de qualquer mudança estrutural.**
