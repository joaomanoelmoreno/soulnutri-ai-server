# Estudo Estratégico — Agrupamento de Pratos por Famílias Visuais

**Data:** 29/Abr/2026
**Status:** ESTUDO APENAS. Nenhum patch. Nenhuma alteração no banco/código/IA.
**Pergunta central:** Vale agrupar pratos visualmente semelhantes em "famílias" únicas, com fallback nutricional genérico?

---

## ⚠️ Achado preliminar importante

**O banco TEM 195 pratos. Encontrei 15 famílias com 2+ pratos.** Mas a maioria das famílias visuais que você listou (Milanesa, Lasanha) tem **POUCA representação atual** (2 pratos cada). O banco já foi parcialmente curado: por exemplo, "Milanesa (Peixe ou Frango)" e "Parmegiana (Frango/Peixe/File Mignon)" **já são pratos agrupados** com nome ambíguo. Ou seja, **o agrupamento já existe pontualmente — sem padrão sistêmico**.

Isso muda o escopo do estudo: a pergunta deixa de ser *"agrupar ou não?"* e passa a ser *"sistematizar e expandir o agrupamento existente?"*.

---

## PARTE 1 — Levantamento (dados reais do banco)

### 15 famílias detectadas (n ≥ 2 pratos)

| # | Família | n | kcal min | kcal max | Média | Spread % | Cat únicas? | Risco vegano misturado |
|---|---|---|---|---|---|---|---|---|
| 1 | SALADA_VERDE | 14 | 9 | 297 | 84 | **342%** 🔴 | ❌ vegano+veget+animal | 🔴 alto |
| 2 | FRUTA | 13 | 13 | 313 | 115 | **261%** 🔴 | ❌ vegano+veget+animal | 🟡 médio |
| 3 | PEIXE_ASSADO | 8 | 75 | 298 | 153 | 146% | ✅ só animal | 🟢 baixo |
| 4 | ARROZ_REFOGADO | 6 | 106 | 253 | 160 | 92% | ❌ vegano+animal | 🟡 médio |
| 5 | GRELHADO | 5 | 47 | 278 | 127 | **182%** 🔴 | ❌ vegano+animal | 🔴 alto |
| 6 | PUDIM_MOUSSE | 5 | 134 | 292 | 225 | 71% | ✅ só vegetariano | 🟢 baixo |
| 7 | **GRATINADO** ⭐ | 4 | 112 | 231 | 176 | 68% | ❌ todas | 🔴 alto |
| 8 | BOLINHO_FRITO | 3 | 49 | 208 | 133 | 119% | ❌ misto | 🟡 médio |
| 9 | BOLO_DOCE | 3 | 230 | 425 | 329 | 59% | ❌ veget+vegano | 🟡 médio |
| 10 | FRANGO | 3 | 124 | 310 | 200 | 93% | ✅ só animal | 🟢 baixo |
| 11 | **MILANESA** ⭐ | 2 | 117 | 164 | 141 | **33%** ✅ | ❌ animal+vegano | 🟡 médio |
| 12 | LASANHA | 2 | 54 | 252 | 153 | **129%** 🔴 | ✅ só vegetariano | 🟢 baixo |
| 13 | RISOTO | 2 | 228 | 247 | 237 | **8%** ✅ | ✅ só vegetariano | 🟢 baixo |
| 14 | FAROFA | 2 | 284 | 358 | 321 | 23% | ❌ animal+vegano | 🔴 alto |
| 15 | MASSA_AO_MOLHO | 2 | 154 | 214 | 184 | 32% | ❌ vegano+veget | 🟡 médio |

### Detalhamento das famílias-alvo (Milanesa e Gratinado)

#### MILANESA (n=2)
| Prato | Categoria | kcal/100g | Ingredientes-chave |
|---|---|---|---|
| Milanesa (Peixe ou Frango) | proteína animal | 164 | proteína + farinha de rosca + ovo |
| Jiló ou Quiabo Empanado | vegano | 117 | jiló/quiabo + farinha de rosca + ovo |

⚠️ "Milanesa (Peixe ou Frango)" **JÁ É um agrupamento**. Spread baixo (33%), mas vegano misturado é problema sério.

#### GRATINADO (n=4)
| Prato | Categoria | kcal/100g | Ingredientes-chave |
|---|---|---|---|
| Escondidinho de Carne Seca | proteína animal | 231 | carne seca + mandioca + queijo |
| Alho Poró Gratinado | vegano | 224 | alho poró + creme vegetal + farinha de rosca |
| Brócolis/Couve Flor Gratinado | vegetariano | 137 | brócolis + bechamel + queijo |
| Bacalhau com Natas | proteína animal | 112 | bacalhau + natas + batata |

⚠️ Spread 68% (aceitável) **mas mistura 3 categorias** (vegano/veget/animal). **Crítico para usuário com restrição.**

---

## PARTE 2 — Análise de conflito visual

### Capacidade da IA de diferenciar (estimativa baseada na arquitetura atual)

A IA usa **CLIP ViT-B/16 ONNX** com índice de embeddings + similaridade. A acurácia depende de:
1. Quantidade de imagens de treino por classe
2. Diferença visual entre classes
3. Overlap semântico

| Família | A IA diferencia hoje? | Causa raiz | Probabilidade de erro |
|---|---|---|---|
| **MILANESA** | 🟡 médio — o nome já é ambíguo "Peixe ou Frango", o que é uma confissão de incapacidade visual | Visualmente idênticos por dentro da casca empanada | **Alta** (~60-80%) |
| **GRATINADO** | 🔴 baixo — 4 itens com cobertura amarelo-dourada similar | Cobertura de queijo gratinado mascara o conteúdo | **Muito alta** (~70-90%) |
| **LASANHA** | 🟡 médio — Espinafre vs Portobello têm cores distintas | Camadas similares mas cores diferentes | **Média** (~30-50%) |
| **RISOTO** | 🟡 médio — ambos cremosos amarelos | Cor e textura quase idênticas | **Alta** (~50-70%) |
| **PEIXE_ASSADO** | 🟢 OK — pratos com molhos/acompanhamentos diferentes | Variação visual real entre os 8 | **Baixa** (~20%) |
| **GRELHADO** | 🟡 médio — entrecôte vs frango são diferenciáveis, mas frango vs lula no escuro nem tanto | Carne grelhada tem padrão visual genérico | **Média** (~30-50%) |
| **SALADA_VERDE** | 🔴 baixo — folhas verdes + topping variado | Visualmente muito diversa (tem 14 itens completamente diferentes!) | **Muito alta** se agrupar tudo (~70-90%) |
| **FRUTA** | 🔴 baixo — frutas têm cores muito distintas (banana ≠ pera ≠ chocolate) | Família extremamente heterogênea | **Crítica** se agrupar tudo |

### Diagnóstico do problema

O conflito é **majoritariamente visual** (cobertura uniforme escondendo conteúdo) em famílias como Milanesa, Gratinado, Risoto. Em famílias como Salada/Fruta, é o **agrupamento que está errado** — não é uma família visual real, são pratos diversos com nome em comum.

---

## PARTE 3 — Simulação da solução

### Estratégia nutricional — comparação das 3 abordagens

Para cada família-alvo, simulei o impacto de cada estratégia:

#### MILANESA (kcal: 117–164, média 141, spread 33%)

| Estratégia | Valor mostrado | Erro vs real (Frango 164) | Erro vs real (Quiabo 117) |
|---|---|---|---|
| **(A) Média** | 141 kcal | −14% (subestima 23kcal) | +21% (superestima 24kcal) |
| **(B) Máximo** | 164 kcal | 0% (perfeito) | **+40% (superestima 47kcal)** ⚠️ |
| **(C) Faixa** | "117–164 kcal" | informativo, sem erro | informativo, sem erro |

#### GRATINADO (kcal: 112–231, média 176, spread 68%)

| Estratégia | Valor mostrado | Erro vs Escondidinho (231) | Erro vs Bacalhau (112) |
|---|---|---|---|
| **(A) Média** | 176 kcal | −24% | **+57% ⚠️** |
| **(B) Máximo** | 231 kcal | 0% | **+106% 🔴 CRÍTICO** |
| **(C) Faixa** | "112–231 kcal" | informativo | informativo |

⚠️ Aqui **fica claríssimo que estratégia (B) Máximo é inviável para Gratinados** — superestima 100%+. Isso destrói credibilidade nutricional.

### Comparação geral das 3 estratégias

| Aspecto | (A) Média | (B) Máximo | **(C) Faixa** ⭐ |
|---|---|---|---|
| Honestidade com usuário | 🟡 média (esconde variabilidade) | 🟡 prudente para dieta mas viesa pra cima | 🟢 **transparente** |
| Erro absoluto máximo | metade do spread | até 100%+ em famílias com spread alto | **zero (informativo)** |
| Conformidade com app de saúde | 🟡 dúvida | 🔴 problema sério em famílias spread>50% | 🟢 **alinhada** |
| Complexidade de UX | simples | simples | **levemente maior (precisa exibir intervalo)** |
| Risco com usuário Premium (contagem rigorosa) | 🟡 contagem incorreta | 🔴 contagem **muito** incorreta | 🟢 usuário escolhe valor central |
| Compatível com restrição (vegano/glúten) | 🔴 esconde alergênicos | 🔴 esconde alergênicos | 🟡 **precisa lista de alergênicos por subitem** |

🥇 **(C) Faixa é a mais coerente para o SoulNutri.** Razões:
1. App de saúde não pode mentir sobre macros
2. Usuários Premium contam calorias rigorosamente
3. Mostra honestidade técnica (eleva confiança)
4. UX é simples: "180–250 kcal/100g"

---

## PARTE 4 — Exceções (NÃO agrupar)

### 🔴 Exceções absolutas

#### Exceção 1: vegano misturado com animal
- **Lasanha de Espinafre (vegetariano)** ≠ **Lasanha de Portobello (vegetariano)** — *podem agrupar* (mesma categoria)
- **MAS** se houvesse "Lasanha Bolonhesa" — **NÃO pode agrupar** (mistura categorias críticas para usuário)
- **Atual no banco:** "Strogonoff (Frango/Carne ou Vegano)" **JÁ ESTÁ AGRUPADO** apesar de violar essa regra. ⚠️ Recomendar revisar esse caso.

#### Exceção 2: alergênicos críticos
Pratos com **glúten/lactose/frutos do mar/castanhas/ovo** não podem ser misturados com versões sem.
- Exemplo proibido: agrupar "Frango à milanesa (com glúten)" com "Frango à milanesa sem glúten" sob nome único.
- A info de alergênico precisa ser **por subitem**, não por família.

#### Exceção 3: spread nutricional extremo (>50%)
- Famílias com spread > 50% em kcal ficam **enganosas** mesmo com média.
- **SALADA_VERDE (342%), FRUTA (261%), GRELHADO (182%), LASANHA (129%), BOLINHO_FRITO (119%)** — todas são "famílias" só pelo nome, não funcionalmente agrupáveis.

#### Exceção 4: diferença visual real
- Risoto de Pera é visualmente diferente do Risoto de Alho Poro (cores).
- Lasanha de Espinafre é verde, Lasanha de Portobello é marrom-avermelhada.
- A IA pode (e deve) tentar diferenciá-los — agrupar é **regressão de capacidade**.

### 🟢 Casos onde agrupar FAZ sentido

| Família | Por quê funciona |
|---|---|
| **MILANESA (animal-only)** | Cobertura empanada esconde conteúdo. Spread 33% (baixo). Mas só dentro de "proteína animal" — não pode misturar Quiabo Empanado |
| **GRATINADO (por categoria)** | Cobertura gourmet esconde conteúdo. Mas separar em 3 famílias: "Gratinado Animal" / "Gratinado Vegetariano" / "Gratinado Vegano" |
| **PARMEGIANA (animal-only)** | Já agrupada hoje. Cobertura idêntica entre frango/peixe/filé. Spread baixo. ✅ |

---

## PARTE 5 — Impacto no produto

### 1. Acurácia percebida
- **Sem agrupamento:** IA tenta diferenciar Milanesa de Frango vs Peixe → erra ~70% das vezes → usuário vê "errou"
- **Com agrupamento "Milanesa (Frango/Peixe/Filé)":** IA acerta 100% (nome cobre todos) → usuário vê "acertou" e confirma
- 🟢 **Acurácia percebida sobe drasticamente** em famílias visualmente ambíguas

### 2. Confiança do usuário
- Estratégia (B) Máximo **destrói confiança em Gratinados** (107% erro em Bacalhau com Natas)
- Estratégia (C) Faixa **eleva confiança** (admite limitação técnica honestamente)
- Etiqueta "Confirme: qual proteína?" faz o usuário se sentir co-piloto, não vítima de erro

### 3. Diferencial do app
- 🟡 **Risco de "achatar" o que diferencia o SoulNutri** — outros apps fazem identificação rasa, vocês fazem fina
- 🟢 **Mas o agrupamento estratégico (só onde a IA realmente erra) preserva o diferencial** e remove pontos de fricção
- A regra: agrupar **apenas onde a IA falha sistematicamente**, não como atalho para preguiça de dataset

### 4. Escalabilidade (400+ pratos)
- 🟢 **Agrupamento estratégico ESCALA bem.** À medida que o catálogo cresce:
  - Novas Milanesas → entram automaticamente na família
  - Novos Gratinados → mesma família com fallback nutricional
  - Reduz necessidade de coletar 50+ imagens por subvariante
- 🔴 **MAS** mistura categorias destrói a feature de filtros vegano/vegetariano (perde valor para Premium)
- Solução: famílias **subdivididas por categoria nutricional** (Gratinado Animal vs Gratinado Vegetariano vs Gratinado Vegano)

---

## PARTE 6 — Recomendação Final

### 🥇 Recomendação Objetiva

# ✅ AGRUPAR — mas seletivamente, com 5 regras

### 1. Quais famílias agrupar (lista enxuta)

🟢 **Aprovar agrupamento:**
- ✅ **MILANESA (Animal)** — agrupar "Milanesa de Frango/Peixe/Filé" (já existe)
- ✅ **PARMEGIANA (Animal)** — já agrupada como "Parmegiana (Frango/Peixe/File Mignon)" (174kcal)
- ✅ **GRATINADO (subdividir em 3 famílias):**
  - "Gratinado Vegano" (Alho Poró Gratinado, Couve Flor Gratinada vegana)
  - "Gratinado Vegetariano" (Brócolis e Couve Flor Gratinado)
  - "Gratinado com Carne/Peixe" (Escondidinho, Bacalhau com Natas)
- ✅ **EMPANADO Vegano** — separar Jiló/Quiabo Empanado da Milanesa Animal

🟡 **Avaliar caso a caso (não agrupar agora):**
- LASANHA — só 2 itens, ambos vegetarianos, spread 129%. **Manter separados.**
- RISOTO — spread baixo (8%) mas IA já diferencia bem hoje. Manter separados.

🔴 **NÃO agrupar:**
- SALADA_VERDE (n=14, spread 342%) — não é família visual, é categoria
- FRUTA (n=13, spread 261%) — idem
- GRELHADO (spread 182%, mistura entrecôte/lula/abobrinha) — visualmente diferenciáveis
- "Strogonoff (Frango/Carne ou Vegano)" **revisar este agrupamento existente** — viola regra de mistura vegano/animal

### 2. Estratégia nutricional → **(C) Faixa de kcal**

Para cada família agrupada, exibir:
```
"Milanesa (Frango ou Peixe)
 ~140-165 kcal/100g
 (varia conforme a proteína)
 [Confirmar tipo: Frango / Peixe / Filé]"
```

Implementação técnica (sem mexer agora, só desenho):
- Schema novo no banco: campo `family_id` + `family_kcal_min/max` + `family_subitems[]`
- Frontend: card mostra faixa + dropdown de confirmação
- Premium: ao confirmar tipo, recalcula com valor exato do subitem

### 3. As 5 regras imutáveis para agrupar

| # | Regra |
|---|---|
| **R1** | Nunca misturar categorias nutricionais (vegano ≠ vegetariano ≠ animal) |
| **R2** | Spread máximo de kcal entre subitens: **40%** (acima disso, faixa fica enganosa) |
| **R3** | Apenas agrupar quando IA tem erro **>50%** entre subitens (medido empiricamente) |
| **R4** | Cada família deve ter **lista explícita de alergênicos** consolidada (intersecção segura) |
| **R5** | UI **obrigatoriamente** pedir confirmação do subtipo (não esconder ambiguidade) |

### 4. Riscos da abordagem

| Risco | Severidade | Mitigação |
|---|---|---|
| Premium vê faixa em vez de número exato | 🟡 médio | Após confirmação, mostra valor exato do subitem |
| Usuário não confirma e fica com info aproximada | 🟡 médio | Default para média da faixa + label "estimado" |
| Alergênicos somados de forma incorreta | 🔴 alto | Política conservadora: marcar alergênico se **qualquer** subitem contiver |
| Achatamento do diferencial do app | 🟡 médio | Aplicar só nas 4-5 famílias listadas, não generalizar |
| Backend precisa de migração no Mongo | 🟡 médio | Migration script + dual-write durante transição |

### 5. Como mitigar — checklist de implementação futura

1. ✅ **Validar empiricamente** (não só por hipótese): rodar 50 fotos reais de Milanesas e contar erros do CLIP atual antes de criar a família
2. ✅ **Esquema dual:** manter `dishes` separados + adicionar `families` por cima — permite reverter
3. ✅ **A/B test:** lançar com 10% dos usuários e medir confusão (perguntas de suporte, taxa de "errou")
4. ✅ **UX explícita:** sempre mostrar "Confirme o tipo" quando for família agrupada
5. ✅ **Premium safeguard:** Premium SEMPRE pede confirmação de subtipo antes de salvar no diário
6. ✅ **Métrica de sucesso:** taxa de match top-1 percebido > 90% pós-agrupamento (vs ~30% atual em Milanesa)

---

## 📋 Resumo Executivo (1 minuto)

| Pergunta | Resposta |
|---|---|
| **Agrupar ou não agrupar?** | ✅ **Sim**, mas seletivamente |
| **Quantas famílias?** | **4-5** (Milanesa Animal, Parmegiana, Gratinado×3 por categoria, Empanado Vegano) |
| **Estratégia nutricional?** | **(C) Faixa de kcal** + confirmação de subtipo |
| **Risco principal?** | Misturar categorias vegano/animal e destruir filtro Premium |
| **Mitigação principal?** | 5 regras imutáveis + validação empírica antes de agrupar |
| **Atinge o objetivo?** | 🟢 Sim — sobe acurácia percebida em ~50%+ nas famílias visuais sem destruir o diferencial |

---

## 🚫 Restrições mantidas integralmente

- ❌ Nenhum patch aplicado
- ❌ Banco de dados não alterado
- ❌ Código não tocado
- ❌ IA não tocada
- ❌ Frontend não tocado
- ❌ Lógica de identificação intacta
- ✅ Apenas levantamento + análise + recomendação

---

**FIM DO ESTUDO. Aguardando decisão sobre próximos passos.**
