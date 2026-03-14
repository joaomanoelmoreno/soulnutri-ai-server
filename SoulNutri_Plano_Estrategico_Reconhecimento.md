# SoulNutri — Plano Estratégico de Evolução do Reconhecimento de Pratos

## Documento de Decisão e Diretrizes para Desenvolvimento

**Versão:** 1.0
**Data:** 10 de Março de 2026
**Projeto:** SoulNutri — Agente de Nutrição Virtual
**Restaurante Piloto:** Cibi Sana

---

## 1. CONTEXTO E DIAGNÓSTICO

### 1.1 Situação Atual (v1.2 + Fase 1)

O SoulNutri utiliza o modelo OpenCLIP ViT-B-32 para identificar pratos a partir de fotos tiradas pelos clientes no buffet. O sistema possui:

- **203 pratos cadastrados** no índice CLIP
- **1.505 embeddings** (vetores de 512 dimensões)
- **2.585 imagens** organizadas em 205 pastas
- **Normalização de imagem** (autocontraste + equalização LAB) aplicada na Fase 1
- **Query-time augmentation** com 5 variações por consulta

### 1.2 Resultados dos Testes Reais no Buffet (10 de Março de 2026)

Em testes reais no buffet do Cibi Sana com dois dispositivos:

| Métrica | iPhone (antigo) | Samsung S25 |
|---|---|---|
| Reconhecimento correto | ~75-80% | ~50-60% |
| Falsos positivos com alta confiança (>90%) | Frequentes | Muito frequentes |
| Pratos não cadastrados | Comportamento adequado | Comportamento adequado |

**Problemas críticos identificados:**
1. O sistema afirma "92% de confiança" para pratos completamente errados (ex: Berinjela ao Limão → Espetinho de Legumes)
2. Pratos cadastrados não são reconhecidos corretamente mesmo com fotos boas
3. Diferença significativa de precisão entre dispositivos (câmeras diferentes)
4. 64 pratos possuem menos de 5 imagens no dataset — insuficiente para o CLIP
5. O CLIP genérico não foi treinado em culinária brasileira autoral

### 1.3 O que Funciona Bem

- Reconhecimento via **Gemini Flash** fora do Cibi Sana: ~100% de acerto em lojas de alimentação comuns
- Pratos com muitas fotos no dataset (20+) são reconhecidos com boa precisão
- O sistema de fallback (CLIP → Gemini) funciona corretamente fora do restaurante
- A interface e experiência do usuário são fluidas e estáveis

### 1.4 Por que o Gemini Não é Usado no Cibi Sana

O Gemini Flash é excelente para pratos mundiais e comerciais (pizza, sushi, hambúrguer). Porém, a culinária do Cibi Sana é autoral — pratos como "Sobrecoxa ao Tandoori", "Mechouia Tunisia" ou "Ceviche de Banana da Terra" não existem em nenhum dataset público. O Gemini confundia sistematicamente esses pratos com versões comerciais conhecidas, gerando mais erros do que acertos. Por isso foi desativado dentro do perímetro do restaurante.

---

## 2. DECISÃO ESTRATÉGICA

### 2.1 Abordagem Adotada: Evolução Incremental com Fine-Tuning

Após análise detalhada de duas propostas técnicas (Documento "Integração de Datasets" e "Análise de Dataset via Script Python"), a decisão é combinar o melhor de ambas as abordagens:

- **Evolução passo a passo** (cada etapa testada e validada no buffet real antes de avançar)
- **Backup obrigatório** a cada versão estável (v1.3, v1.4, v1.5, etc.)
- **Rollback imediato** se qualquer etapa degradar a precisão
- **Destino final:** modelo especializado nos pratos do Cibi Sana via Fine-Tuning + CNN

### 2.2 Justificativa

O CLIP genérico (ViT-B-32) atingiu seu teto de performance para culinária autoral brasileira. Um raw score de 0.85 é o máximo que ele consegue na maioria dos pratos, e esse valor é insuficiente para distinguir pratos visualmente semelhantes (berinjela vs. espetinho, risoni vs. salada oriental).

As melhorias incrementais (normalização, augmentation) ajudam marginalmente mas não resolvem o problema fundamental: **o modelo não conhece esses pratos**. A solução definitiva requer ensinar o modelo especificamente sobre os pratos do Cibi Sana.

---

## 3. ETAPAS DO PLANO

### ETAPA 1 — Ajustes de Calibração e UX (v1.3)
**Status:** Aprovada para implementação imediata
**Risco:** Baixo (não mexe no modelo nem no índice)
**Prazo estimado:** 1 sessão

**Objetivo:** Eliminar falsos positivos com alta confiança e melhorar a honestidade do sistema.

**Alterações:**

1. **Calibração conservadora dos thresholds:**
   - Alta confiança: somente raw >= 0.92 E gap > 0.08 entre 1º e 2º colocado
   - Média confiança: raw 0.85-0.92 — exibe "Parece ser [PRATO], verifique" com 2 alternativas
   - Baixa confiança: raw < 0.85 — exibe "Não reconheço este prato" SEM alternativas

2. **Limitar alternativas:**
   - Alta confiança: 0 alternativas (identificação direta)
   - Média confiança: 2 alternativas máximo
   - Baixa confiança: 0 alternativas

3. **Sincronizar nomes do Admin com a tela:**
   - Correção arquitetural: nomes editados no painel Admin devem aparecer na tela do cliente
   - Exemplo: "Brócolis Gratinado" renomeado para "Brócolis ao Alho" no Admin deve refletir no resultado

**Fundamento:** Não resolve o reconhecimento em si, mas elimina o problema mais grave — mentir para o usuário com alta confiança. É melhor dizer "não sei" do que afirmar o errado.

**Métrica de sucesso:** Zero falsos positivos com confiança acima de 85%. Todo erro deve ser classificado como "incerto" ou "não reconhecido".

---

### ETAPA 2 — Pipeline por Categoria (v1.4)
**Status:** Planejada
**Risco:** Baixo-Médio (adiciona camada de filtragem, não substitui o CLIP)
**Prazo estimado:** 1-2 sessões

**Objetivo:** Reduzir erros absurdos (ex: berinjela → espetinho) classificando primeiro a CATEGORIA do prato.

**Como funciona:**

```
Foto do cliente
    ↓
[CATEGORIA] → "É uma proteína? Salada? Massa? Sobremesa? Legume?"
    ↓
[CLIP filtrado] → Busca apenas entre pratos DA MESMA CATEGORIA
    ↓
Resultado final
```

**Categorias propostas:**
- Proteína Animal (carnes, peixes, frango)
- Massas (espaguete, risoni, canelone, lasanha, ravioli)
- Saladas e Folhas
- Legumes e Vegetais Cozidos
- Sobremesas e Doces
- Acompanhamentos (arroz, feijão, farofa, purê)
- Frutas

**Implementação:** Usar o próprio CLIP com prompts de texto (zero-shot classification):
- "a photo of a meat dish"
- "a photo of a pasta dish"
- "a photo of a salad"
- etc.

O CLIP é BOM para categorias genéricas (ele conhece "meat", "pasta", "salad"). Ele falha nos pratos específicos do Cibi Sana, não nas categorias.

**Fundamento:** Se o sistema sabe que a foto é de um "legume", ele não vai comparar com espetinhos de carne ou massas. O universo de candidatos cai de 203 para ~20-30 pratos, reduzindo drasticamente erros entre categorias.

**Métrica de sucesso:** Eliminação completa de erros entre categorias diferentes (carne confundida com salada, massa confundida com legume, etc.).

---

### ETAPA 3 — Enriquecimento do Dataset (v1.5)
**Status:** Planejada
**Risco:** Baixo (apenas adiciona mais dados)
**Prazo estimado:** 1-2 sessões + trabalho do proprietário

**Objetivo:** Aumentar a quantidade e diversidade de imagens por prato para melhorar a robustez do CLIP.

**Ações:**

1. **Upload das 15.000 fotos** que o proprietário possui para as pastas correspondentes
2. **Mínimo de 12 imagens por prato** (atualmente 64 pratos têm menos de 5)
3. **Diversidade obrigatória** em cada pasta:
   - Fotos com diferentes celulares (iPhone, Samsung, etc.)
   - Diferentes ângulos (de cima, lateral, 45 graus)
   - Diferentes porções (travessa cheia, meia, quase vazia)
   - Diferentes iluminações (natural, artificial, mista)
4. **Augmentação automática no índice:** cada imagem gera 5 embeddings com variações de brilho, contraste, cor e crop. Resultado: ~7.500+ embeddings no índice
5. **Otimização de resolução:** redimensionar imagens para 512x512 antes do processamento (CLIP usa 224x224)

**Fundamento:** A análise do dataset confirma que 64 pratos com menos de 5 imagens é insuficiente. A recomendação técnica é mínimo 12, ideal 20+ imagens por prato. Com as 15.000 fotos disponíveis, é possível atingir esse patamar para a maioria dos pratos.

**Métrica de sucesso:** Todos os pratos com no mínimo 12 imagens. Precisão no buffet real acima de 80% no Cibi Sana.

---

### ETAPA 4 — Fine-Tuning do OpenCLIP em Comida (v1.6)
**Status:** Planejada
**Risco:** Médio (troca o modelo, requer reindexação)
**Prazo estimado:** 2-3 sessões

**Objetivo:** Criar um modelo CLIP especializado em comida, substituindo o genérico.

**Como funciona:**

1. **Ponto de partida:** modelo OpenCLIP ViT-B-32 pré-treinado (o atual)
2. **Fase A — Treinamento em dataset público de comida:**
   - Datasets: Food-101 (101 categorias, 101.000 imagens) e/ou Food2K (2.000 categorias)
   - Método: contrastive learning (image-text pairs)
   - Objetivo: ensinar o modelo a gerar embeddings mais "centrados em comida" — melhor separação entre texturas, cores e formas alimentares
3. **Fase B — Especialização no Cibi Sana:**
   - Dataset: todas as imagens do Cibi Sana (~15.000 fotos)
   - Método: fine-tuning curto (few-shot) com as categorias específicas do restaurante
   - Objetivo: o modelo aprende que "Sobrecoxa ao Tandoori" é visualmente diferente de "Sobrecoxa ao Limão"
4. **Exportação e deploy:** substituir os pesos do modelo no servidor
5. **Reindexação:** recalcular todos os embeddings do dataset com o novo modelo

**O que NÃO muda:**
- A API permanece idêntica (mesmos endpoints)
- O pipeline de busca permanece idêntico (embedding → busca vetorial → top-k → calibração)
- O frontend permanece inalterado

**O que muda:**
- A QUALIDADE dos embeddings — mais precisos para comida
- A SEPARAÇÃO entre pratos visualmente similares
- A ROBUSTEZ contra variações de câmera e iluminação

**Fundamento:** O documento "Integração de Datasets" explica que fine-tuning não aumenta latência e mantém a arquitetura existente. A mudança é apenas nos pesos (weights) do modelo. O treinamento em Food-101/Food2K ensina o modelo a "pensar em comida" antes de aprender os pratos específicos. É como ensinar alguém a cozinhar antes de ensinar as receitas do Cibi Sana.

**Métrica de sucesso:** Precisão no buffet real acima de 90% no Cibi Sana. Redução de falsos positivos para menos de 5%.

---

### ETAPA 5 — CNN Classificadora Dedicada (v1.7)
**Status:** Planejada
**Risco:** Médio (adiciona segundo modelo em paralelo)
**Prazo estimado:** 2-3 sessões

**Objetivo:** Treinar uma rede neural convolucional (CNN) ESPECIFICAMENTE para classificar os pratos do Cibi Sana, funcionando como sistema primário ou como validação cruzada do CLIP.

**O que é uma CNN e por que ela é poderosa:**

Uma CNN (Convolutional Neural Network) é uma rede neural que aprende a reconhecer padrões visuais em imagens de forma hierárquica:
- **Camadas iniciais:** detectam bordas, texturas, gradientes de cor
- **Camadas intermediárias:** detectam formas (redondo, alongado, granulado)
- **Camadas finais:** detectam composições complexas (um prato específico com seus ingredientes típicos)

A diferença fundamental entre CLIP e CNN:
- **CLIP:** "essa imagem se PARECE com algo que eu já vi" (comparação por similaridade)
- **CNN treinada:** "essa imagem É [nome do prato]" (classificação direta)

A CNN não compara vetores — ela APRENDE os padrões visuais de cada prato e os classifica diretamente. Por isso é muito mais precisa para um conjunto fechado de pratos (como o cardápio do Cibi Sana).

**Arquitetura proposta:**

- **Modelo base:** EfficientNet-B4 ou ResNet-50 (pré-treinado no ImageNet)
- **Transfer learning:** aproveitar os pesos pré-treinados e adicionar uma camada final de classificação com 203 saídas (uma por prato)
- **Dataset de treinamento:** as 15.000+ fotos do Cibi Sana, divididas em:
  - 80% para treinamento
  - 10% para validação
  - 10% para teste

**Pipeline de uso (duas opções):**

**Opção 1 — CNN como sistema primário:**
```
Foto → CNN → "Ceviche" (97.3% confiança)
         ↓ (se confiança < threshold)
       CLIP → busca por similaridade (fallback)
```

**Opção 2 — CNN + CLIP em consenso (mais seguro):**
```
Foto → CNN → "Ceviche" (97.3%)
Foto → CLIP → "Ceviche" (0.91)
         ↓
Se ambos concordam → Alta confiança
Se discordam → Média confiança (mostrar ambas sugestões)
```

**Vantagens da CNN:**
1. **Precisão superior** para conjunto fechado de classes (os 203 pratos)
2. **Robusta a variações de câmera** — aprende a reconhecer o prato independente do dispositivo
3. **Velocidade:** inferência de uma CNN é tipicamente 50-100ms (mais rápida que CLIP)
4. **Pode detectar "prato desconhecido":** se nenhuma classe atinge confiança mínima, é um prato novo
5. **Melhora contínua:** cada foto nova do buffet pode ser usada para retreinamento

**Considerações:**
- Requer GPU para treinamento (não para inferência — CPU é suficiente)
- O treinamento pode ser feito na nuvem (Google Colab, AWS, etc.) e o modelo exportado
- O modelo treinado ocupa ~50-100MB (leve)
- Não substitui o CLIP para pratos fora do Cibi Sana — o CLIP + Gemini continuam para uso externo

**Fundamento:** A CNN é o padrão da indústria para classificação de imagem em conjunto fechado. Apps como Calorie Mama, Foodvisor e Google Lens usam CNNs treinadas especificamente em comida. Com 15.000 fotos de treino, o modelo terá material mais que suficiente para aprender cada prato com alta precisão. A CNN complementa o CLIP — o CLIP é bom para "o que se parece com isso?" e a CNN é boa para "o que É isso?".

**Métrica de sucesso:** Precisão acima de 95% no buffet real. Zero falsos positivos com alta confiança. Diferença entre dispositivos inferior a 3%.

---

### ETAPA 6 — Descrições Semânticas e Prompt Engineering (v1.8)
**Status:** Planejada (pode ser antecipada)
**Risco:** Baixo
**Prazo estimado:** 1 sessão

**Objetivo:** Criar descrições textuais ricas para cada prato, melhorando a capacidade do CLIP de entender o contexto.

**Exemplo:**
```json
{
  "Ceviche": [
    "a plate of fresh fish ceviche with lime and onions",
    "peruvian ceviche with citrus marinade and cilantro",
    "raw fish dish with colorful vegetables and lemon"
  ],
  "Sobrecoxa ao Tandoori": [
    "tandoori chicken thigh with indian spices",
    "grilled chicken with red tandoori sauce",
    "spiced chicken leg with yogurt marinade"
  ]
}
```

**Fundamento:** O CLIP foi treinado com pares imagem-texto. Descrições semânticas permitem usar AMBOS os encoder (imagem e texto) para melhorar a correspondência. Especialmente útil para pratos com nomes que o CLIP não conhece.

---

## 4. CRONOGRAMA E VERSIONAMENTO

| Versão | Etapa | Foco Principal | Critério de Aprovação |
|---|---|---|---|
| v1.3 | Etapa 1 | Calibração + UX + correções | Zero falsos positivos >85% |
| v1.4 | Etapa 2 | Pipeline por categoria | Zero erros entre categorias |
| v1.5 | Etapa 3 | Enriquecimento do dataset | Todos pratos com 12+ imagens |
| v1.6 | Etapa 4 | Fine-tuning OpenCLIP | Precisão >90% no buffet |
| v1.7 | Etapa 5 | CNN classificadora | Precisão >95% no buffet |
| v1.8 | Etapa 6 | Descrições semânticas | Melhoria incremental |

**Regras de versionamento:**
- Cada versão é salva como backup antes de avançar
- O proprietário testa no buffet real e aprova antes de avançar
- Se qualquer versão degradar a precisão, rollback imediato para a anterior
- As etapas podem ser reordenadas conforme resultados

---

## 5. RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Fine-tuning degradar precisão de pratos que já funcionam | Média | Teste A/B: comparar modelo novo vs. antigo em todos os pratos antes de trocar |
| CNN não atingir 95% com dataset atual | Baixa | Aumentar dataset progressivamente; usar data augmentation |
| Mudanças quebrarem funcionalidades existentes (como ocorreu na v1.2) | Média | Backups obrigatórios; alterações isoladas; testes automatizados |
| Treinamento requerer GPU não disponível | Baixa | Google Colab (gratuito) ou serviços cloud sob demanda |
| Latência aumentar com dois modelos (CLIP + CNN) | Baixa | CNN é mais rápida que CLIP; execução paralela possível |

---

## 6. INFRAESTRUTURA NECESSÁRIA

- **Para Etapas 1-3:** nenhuma infraestrutura adicional
- **Para Etapa 4 (Fine-tuning):** GPU para treinamento (Google Colab gratuito ou similar)
- **Para Etapa 5 (CNN):** GPU para treinamento (mesmo ambiente da Etapa 4)
- **Para deploy:** o servidor atual (CPU) é suficiente para inferência de ambos os modelos

---

## 7. CONCLUSÃO

O sistema atual de reconhecimento atingiu o limite do que o CLIP genérico pode oferecer para culinária autoral. A evolução incremental proposta neste documento — calibração → categorias → dataset → fine-tuning → CNN — permite melhorar a precisão progressivamente, de forma segura e mensurável.

A combinação final de CLIP especializado + CNN classificadora representa o estado da arte em reconhecimento de comida, usado pelos principais apps do mercado (Calorie Mama, Foodvisor, Google Lens). Com o dataset rico do Cibi Sana (15.000+ fotos) e a abordagem incremental, temos todos os ingredientes para atingir precisão acima de 95% no buffet real.

O Gemini Flash continua sendo usado fora do Cibi Sana para pratos comerciais, onde sua performance é excelente. A CNN e o CLIP especializado cuidam exclusivamente do ambiente do restaurante.

---

**Documento aprovado para execução em:** ___/___/2026
**Responsável técnico:** Agente de Desenvolvimento SoulNutri
**Validação:** Proprietário do Cibi Sana
