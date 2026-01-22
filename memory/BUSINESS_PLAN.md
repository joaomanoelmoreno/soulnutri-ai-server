# SoulNutri - Business Plan & Análise de Mercado

**Data**: Janeiro 2026
**Versão**: Draft para discussão

---

## 1. 📊 ANÁLISE DE CONCORRENTES E PREÇOS

### Apps Internacionais (Referência)

| App | Modelo | Mensal | Anual | Por mês (anual) |
|-----|--------|--------|-------|-----------------|
| **MyFitnessPal** | Freemium | $19.99 (~R$120) | $79.99 (~R$480) | ~R$40/mês |
| **MyFitnessPal+** | Premium+ | $24.99 (~R$150) | $99.99 (~R$600) | ~R$50/mês |
| **Yuka** | Sliding scale | - | $10-20 (~R$60-120) | ~R$5-10/mês |
| **Lose It** | Freemium | - | $39.99 (~R$240) | ~R$20/mês |
| **Noom** | Coaching | ~$70/mês | ~$209/ano | ~R$100/mês |

### Apps Brasil

| App | Público | Preço |
|-----|---------|-------|
| **Dietbox** (B2B) | Nutricionistas | R$59-879/mês |
| **TecnoNutri** | Consumidores | ~R$15-30/mês (estimado) |

### Insights
- **Yuka** (mais similar ao SoulNutri) cobra apenas R$60-120/ANO
- **MyFitnessPal** é caro: R$40-50/mês
- **Mercado Brasil** ainda é subexplorado
- **Diferencial SoulNutri**: Identificação por imagem em tempo real + local físico (CibiSana)

---

## 2. 💰 SUGESTÃO DE PREÇOS - SOULNUTRI

### Modelo Recomendado: Freemium + Assinatura

| Plano | Preço | Conversão USD |
|-------|-------|---------------|
| **Free** | R$0 | - |
| **Premium Mensal** | R$14,90/mês | ~$2.50 |
| **Premium Anual** | R$99,90/ano | ~$16.70 |
| **Premium Anual (por mês)** | R$8,33/mês | - |

### Por que esses valores?
- **Mais barato que MyFitnessPal** (R$40/mês) → competitivo
- **Similar ao Yuka** (R$60-120/ano) → referência de mercado
- **Acessível para brasileiro** → maior conversão
- **Desconto anual de 44%** → incentiva fidelização

### Promoção de Lançamento (sugestão)
- **3 primeiros meses**: R$9,90/mês
- **Clientes CibiSana**: 1 mês grátis

---

## 3. 📦 RECURSOS POR PLANO

### FREE
- ✅ Identificação de pratos (ilimitada)
- ✅ Nome, categoria, ingredientes
- ✅ Alérgenos básicos
- ✅ Modo multi-item
- ❌ Limite: Sem histórico, sem alertas personalizados

### PREMIUM (R$14,90/mês ou R$99,90/ano)
- ✅ Tudo do Free +
- ✅ Contador calorias/macros diário
- ✅ Alertas personalizados em tempo real
- ✅ Perfil nutricional (alergias, restrições)
- ✅ "Você Sabia?" - Curiosidades científicas
- ✅ Combinações inteligentes de alimentos
- ✅ Substituições saudáveis
- ✅ **Histórico semanal com gráficos** ⏳
- ✅ **Educação nutricional contínua** ⏳
- ✅ **Verdade ou Mito** ⏳
- ✅ **Interação com medicamentos** ⏳
- ✅ **Timing nutricional** (melhor hora p/ comer) ⏳

⏳ = A implementar

---

## 4. 🏗️ ESTRUTURA DE CUSTOS

### Custos Fixos Mensais

| Item | Custo/mês | Notas |
|------|-----------|-------|
| **Emergent Platform** | ~R$200-500 | Hospedagem + deploy |
| **Emergent LLM Key** | ~R$100-500 | Depende do uso (Gemini Vision) |
| **Domínio** | ~R$3 | R$40/ano |
| **MongoDB** | R$0 | Incluso no Emergent |
| **Apple Developer** | ~R$50 | $99/ano |
| **Google Play** | ~R$10 | $25 único (diluído) |
| **Subtotal Infra** | **~R$400-1.100/mês** | |

### Custos Variáveis (por identificação)

| Item | Custo/uso | Volume 1000/dia |
|------|-----------|-----------------|
| **Gemini Vision** | ~$0.001/imagem | ~R$180/mês |
| **Cache** | R$0 | Reduz 50%+ das chamadas |
| **YOLOv8 local** | R$0 | Após implementado |

### Custos de Pessoal

| Função | Custo/mês | Dedicação |
|--------|-----------|-----------|
| **Desenvolvedor IA** | R$8.000-15.000 | Parcial/Full |
| **Funcionário operacional** | R$2.000-3.000 | Balança/Suporte |
| **Subtotal Pessoal** | **R$10.000-18.000/mês** | |

### Custo Total Estimado

| Cenário | Custo/mês |
|---------|-----------|
| **Mínimo** (você + 1 funcionário) | ~R$3.000-5.000 |
| **Operação Leve** (+ dev parcial) | ~R$8.000-12.000 |
| **Operação Completa** | ~R$15.000-25.000 |

---

## 5. 📈 PROJEÇÃO DE RECEITA

### Premissas Base CibiSana

| Métrica | Valor | Notas |
|---------|-------|-------|
| Clientes/dia CibiSana | ~150-200 | Estimativa |
| Clientes/mês únicos | ~1.000-1.500 | |
| Taxa download app | 30% | 300-450 downloads/mês |
| Taxa conversão Free→Premium | 5-10% | Benchmark mercado |
| Assinantes Premium/mês | 15-45 | Novos |

### Cenários de Receita (Apenas CibiSana)

| Cenário | Assinantes | Ticket médio | Receita/mês |
|---------|------------|--------------|-------------|
| **Pessimista** | 50 | R$12 | R$600 |
| **Realista** | 150 | R$12 | R$1.800 |
| **Otimista** | 300 | R$12 | R$3.600 |

### Escala: Múltiplos Restaurantes

| Restaurantes | Assinantes | Receita/mês |
|--------------|------------|-------------|
| 1 (CibiSana) | 150 | R$1.800 |
| 5 | 750 | R$9.000 |
| 10 | 1.500 | R$18.000 |
| 50 | 7.500 | R$90.000 |

### Escala: App Público (sem restaurante)

| Downloads | Conversão 5% | Receita/mês |
|-----------|--------------|-------------|
| 10.000 | 500 | R$6.000 |
| 50.000 | 2.500 | R$30.000 |
| 100.000 | 5.000 | R$60.000 |
| 500.000 | 25.000 | R$300.000 |

---

## 6. 💹 ANÁLISE DE MARGEM

### Cenário: 500 Assinantes Premium

| Item | Valor |
|------|-------|
| Receita mensal | R$6.000 |
| (-) Custos infra | R$1.000 |
| (-) Custos API IA | R$500 |
| **Margem bruta** | **R$4.500 (75%)** |
| (-) Pessoal (parcial) | R$3.000 |
| **Lucro operacional** | **R$1.500 (25%)** |

### Break-even (Ponto de Equilíbrio)

| Cenário Custo | Assinantes p/ Break-even |
|---------------|--------------------------|
| Mínimo (R$3.000) | ~250 assinantes |
| Leve (R$8.000) | ~670 assinantes |
| Completo (R$15.000) | ~1.250 assinantes |

---

## 7. 📣 PLANO DE MARKETING - DRAFT

### Fase 1: Lançamento CibiSana (Semanas 1-4)

**Objetivo**: 100 downloads, 10 assinantes Premium

| Ação | Responsável | Custo |
|------|-------------|-------|
| QR codes nas mesas | Você | R$50 (impressão) |
| Treinamento garçons | Você | R$0 |
| Post Instagram CibiSana | Você | R$0 |
| Promoção: 1 mês grátis | - | R$0 |

**Táticas**:
- Garçom apresenta: *"Conhece o SoulNutri? Tira foto do prato e vê as calorias na hora"*
- Cliente experimenta → "Uau!" → Compartilha
- Oferta: *"Premium grátis por 1 mês para clientes CibiSana"*

### Fase 2: Boca a Boca (Meses 2-3)

**Objetivo**: 500 downloads, 50 assinantes

| Ação | Custo |
|------|-------|
| Programa indicação: "Indique e ganhe 1 mês" | R$0 |
| Depoimentos em vídeo de clientes | R$0 |
| Parceria com nutricionistas locais | R$0 |
| Posts educativos (Verdade ou Mito) | R$0 |

### Fase 3: Expansão (Meses 4-6)

**Objetivo**: Outros restaurantes saudáveis

| Ação | Custo |
|------|-------|
| Pitch para 5 restaurantes similares | R$0 |
| Modelo white-label ou parceria | A definir |
| Ads Instagram/Facebook (teste) | R$500-1.000 |

### Fase 4: Escala (Meses 6-12)

**Objetivo**: App stores + Público geral

| Ação | Custo |
|------|-------|
| Publicar na Apple Store | $99/ano |
| Publicar na Google Play | $25 único |
| Influenciadores fitness/nutrição | R$1.000-5.000 |
| Assessoria de imprensa | R$2.000-5.000 |

---

## 8. 🎯 METAS E TARGETS

### Ano 1

| Trimestre | Downloads | Assinantes | Receita |
|-----------|-----------|------------|---------|
| Q1 | 500 | 50 | R$600/mês |
| Q2 | 2.000 | 200 | R$2.400/mês |
| Q3 | 5.000 | 500 | R$6.000/mês |
| Q4 | 10.000 | 1.000 | R$12.000/mês |
| **Total Ano 1** | **10.000** | **1.000** | **~R$60.000** |

### Ano 2 (com app stores)

| Meta | Valor |
|------|-------|
| Downloads | 50.000 |
| Assinantes | 5.000 |
| Receita anual | R$600.000 |

### Ano 3 (escala)

| Meta | Valor |
|------|-------|
| Downloads | 200.000 |
| Assinantes | 20.000 |
| Receita anual | R$2.400.000 |

---

## 9. ✅ PRÓXIMOS PASSOS

### Imediato (Esta semana)
- [ ] Testar fotos na balança
- [ ] Validar reconhecimento de imagem
- [ ] Definir preço final Premium
- [ ] Criar QR code para mesas

### Curto prazo (2-4 semanas)
- [ ] Implementar recursos Premium faltantes
- [ ] Soft launch no CibiSana
- [ ] Coletar feedback primeiros usuários
- [ ] Ajustar produto

### Médio prazo (1-3 meses)
- [ ] Lançamento oficial CibiSana
- [ ] Primeira campanha de indicação
- [ ] Prospectar outros restaurantes
- [ ] Deploy produção + domínio próprio

---

## 10. ❓ DECISÕES PENDENTES

1. **Preço Premium**: R$14,90/mês OK ou ajustar?
2. **Promoção lançamento**: Quanto tempo de gratuidade?
3. **Funcionário balança**: Treinar atual ou contratar?
4. **Desenvolvedores**: Continuar com Emergent ou contratar?
5. **Investimento inicial**: Quanto disponível para mktg?

---

*Documento preparado para discussão - SoulNutri Business Plan v1*
