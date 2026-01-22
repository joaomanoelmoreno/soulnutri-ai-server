# 🔬 ANÁLISE COMPARATIVA: APIs de Reconhecimento de Alimentos

## RESUMO EXECUTIVO

Pesquisei todas as opções disponíveis no mercado. Aqui está o comparativo completo:

---

## 📊 TABELA COMPARATIVA

| API | Free Tier | Custo Adicional | Velocidade | Precisão |
|-----|-----------|-----------------|------------|----------|
| **Clarifai** ⭐ | Comunidade (limitado) | $0.0012/request | ~500ms | Alta |
| **LogMeal** | 20 img/dia ou 200/mês trial | €144/mês | ~800ms | Alta |
| **Roboflow** ⭐ | 1.000/mês | $0.003/request | ~300ms | Média-Alta |
| **Google Vision** | 1.000/mês | $1.50/1000 (~$0.0015) | ~400ms | Média |
| **FatSecret** ⭐⭐ | 5.000/dia (150k/mês RapidAPI) | Grátis para startups | ~600ms | Média |
| **Hugging Face** | $0.10 crédito | $0.033/hora endpoint | ~1s | Variável |
| **Calorie Mama** | Trial | $0.10/request | ~500ms | Alta |

---

## 🏆 TOP 3 RECOMENDAÇÕES (CUSTO-BENEFÍCIO)

### 1. 🥇 FatSecret API (MELHOR OPÇÃO GRATUITA)
**150.000 requests/mês GRÁTIS no RapidAPI!**

| Aspecto | Detalhe |
|---------|---------|
| Free Tier | 150.000 req/mês |
| Rate Limit | 1.000 req/hora |
| Funcionalidades | Barcode, imagem, NLP, alérgenos |
| Velocidade | ~500-800ms |
| Custo escala | Grátis para startups verificados |

**Prós:**
- 150k requests/mês é MUITO (5.000/dia)
- Inclui reconhecimento de imagem
- Database global de alimentos
- Versão Premier grátis para startups!

**Contras:**
- Precisa atribuição (logo FatSecret)
- Precisão menor que Clarifai

---

### 2. 🥈 Clarifai (MELHOR PRECISÃO)
**$0.0012 por request = $1.20 para 1.000 imagens**

| Aspecto | Detalhe |
|---------|---------|
| Free Tier | Comunidade (limitado) |
| Custo | $0.0012/request |
| Custo 100k users | ~$120/mês |
| Velocidade | ~500ms |
| Precisão | 95%+ |

**Prós:**
- Altíssima precisão
- Modelo treinado com milhares de alimentos
- Muito barato ($0.0012/req)
- API robusta e bem documentada

**Contras:**
- Free tier limitado
- Precisa conta paga para escala

---

### 3. 🥉 Roboflow (MAIS FLEXÍVEL)
**1.000/mês grátis + $0.003/request**

| Aspecto | Detalhe |
|---------|---------|
| Free Tier | 1.000 req/mês |
| Custo | $0.003/request |
| Modelos | Vários modelos de comida disponíveis |
| Velocidade | ~300ms |

**Prós:**
- Vários modelos prontos (Food-101, ingredientes, etc.)
- Pode baixar modelo e rodar LOCAL (grátis!)
- Comunidade ativa
- Fácil integrar

**Contras:**
- Free tier pequeno
- Precisão varia por modelo

---

## 💰 ANÁLISE DE CUSTOS (100.000 usuários/mês)

| API | Custo Mensal | Custo/Request |
|-----|--------------|---------------|
| **FatSecret** | **$0** (grátis!) | $0.00 |
| **Clarifai** | **$120** | $0.0012 |
| **Roboflow** | **$297** | $0.003 |
| **Google Vision** | **$150** | $0.0015 |
| **Calorie Mama** | **$10.000** | $0.10 |

---

## 🎯 PLANO RECOMENDADO

### Fase 1: AGORA (Esta semana)
**Implementar FatSecret via RapidAPI**
- 150.000 requests/mês GRÁTIS
- Suficiente para testar e validar
- Sem custo inicial

### Fase 2: Se precisar mais precisão
**Adicionar Clarifai como fallback**
- Apenas $0.0012/request
- Usar quando FatSecret não reconhecer

### Fase 3: Escala (Paralelo)
**Treinar YOLOv8 próprio**
- Baixar modelo do Roboflow para treinar
- Custo zero quando pronto
- 50ms de resposta

---

## 🔧 ARQUITETURA PROPOSTA

```
[Imagem] 
    │
    ▼
[OpenCLIP Local] ──────── 90%+ confiança ──────► RETORNA (200ms)
    │
    │ < 90%
    ▼
[FatSecret API] ──────── Reconheceu? ──────► CACHEIA + RETORNA (600ms)
    │                         │
    │ Não                     │
    ▼                         ▼
[Clarifai] ──────────── CACHEIA + RETORNA (500ms)
    │
    │ Não reconheceu
    ▼
[Gemini Vision] ─────── Fallback final (3s)
```

**Resultado esperado:**
- 70% resolvido no local: 200ms
- 25% resolvido no FatSecret: 600ms
- 4% resolvido no Clarifai: 500ms
- 1% vai para Gemini: 3s

**Tempo médio: ~350ms** ⚡

---

## 📋 PRÓXIMOS PASSOS

1. **Criar conta RapidAPI** e obter key do FatSecret
2. **Implementar integração** FatSecret como Nível 2
3. **Testar velocidade** e precisão
4. **Se necessário**, adicionar Clarifai como Nível 3

---

## 🔗 LINKS ÚTEIS

- FatSecret RapidAPI: https://rapidapi.com/FatSecret/api/fatsecret4
- Clarifai Food Model: https://clarifai.com/clarifai/main/models/food-item-recognition
- Roboflow Food Models: https://universe.roboflow.com/search?q=food
- LogMeal: https://logmeal.com/api/

---

*Análise atualizada em Janeiro/2026*
