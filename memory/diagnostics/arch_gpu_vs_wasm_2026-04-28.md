# Estudo Arquitetural — GPU no Backend vs CLIP no Navegador

**Data:** 28/Abr/2026
**Status:** ESTUDO APENAS. Nenhuma implementação. Nenhuma decisão final.
**Contexto:** Backend CLIP em CPU do Render Standard 1GB, ~1300-1500ms de inferência (gargalo principal). Meta <500ms não atingida com R3.

---

## 1. Estado atual (baseline)

```
celular ──Wi-Fi/4G──> Render (CPU 1GB) ──CLIP ONNX──> ~1500ms
                                          + outros 600ms (rede + framework)
                                          ─────────────────
                                          TOTAL ~2100ms
```

- 75% do tempo é inferência CLIP em CPU
- Meta crítica: scan <500ms
- Cenário primário: buffet Cibi Sana (Wi-Fi local moderado)
- Cenário secundário: usuários fora do Cibi Sana (4G/5G)

---

## 2. Caminho A — GPU no Backend

### 2.1 O que muda

Mover o backend (ou ao menos o módulo de inferência CLIP) para infraestrutura com GPU dedicada. Mantém arquitetura split atual: frontend Vercel chama backend GPU.

**Variantes técnicas:**
- **A1.** Render Pro com instância GPU dedicada (T4/L4)
- **A2.** Modal Labs (serverless GPU pay-per-second)
- **A3.** Replicate (modelo hospedado, API simples)
- **A4.** Híbrido: Render mantém endpoints CRUD/nutrição, CLIP roda em Modal via webhook

### 2.2 Métricas estimadas

| Métrica | Valor estimado | Fonte |
|---|---|---|
| **Inferência CLIP GPU T4** | **30-80ms** | OpenAI CLIP benchmarks; ONNX Runtime CUDA |
| **Inferência CLIP GPU A10G** | 15-40ms | idem |
| **Latência total end-to-end (Cibi Sana Wi-Fi)** | **~250-450ms** ✅ | TTFB 50ms + upload 50ms + inferência 50ms + framework 100ms + download 50ms |
| **Latência total end-to-end (4G)** | ~600-900ms | mesmas fases, com TTFB+upload maiores |
| **Cold start Modal (após inatividade)** | 5-15s no 1º request | Documentação Modal |
| **Cold start Render Pro persistente** | <2s | container always-on |

### 2.3 Custo mensal estimado

Premissa: 1.000 scans/dia × 30 dias = **30.000 scans/mês**.

| Variante | Custo unitário | Custo/30k scans | Custo total estimado |
|---|---|---|---|
| **A1.** Render Pro GPU T4 | always-on $0,59/h × 720h | ~$425/mês | **ALTO ~$425/mês** |
| **A2.** Modal T4 serverless | $0,000164/s × ~0,5s = $0,000082/scan | ~$2,46/mês | **BAIXO ~$5-15/mês** *(considerando overhead)* |
| **A3.** Replicate T4 | $0,000225/s × ~0,5s = $0,000113/scan | ~$3,39/mês | **BAIXO ~$10-25/mês** |
| **A4.** Híbrido (Render + Modal) | Render Standard $25 + Modal $5 | ~$30/mês | **BAIXO-MÉDIO ~$30-40/mês** |

**Custo atual Render Standard:** ~$25/mês (já pago).

**Vencedor de custo:** **A4 (Híbrido Render + Modal)** ou **A2 (Modal puro)**. Pay-per-second elimina ociosidade de GPU sem demanda.

### 2.4 Complexidade de implementação

| Etapa | Variante A4 (recomendada) |
|---|---|
| Setup Modal account + token | 30 min |
| Empacotar `image_embedding_from_bytes` em função Modal | ~2-3h |
| Mover embeddings index e similaridade pra função Modal (ou mantê-los no Render?) | 4-6h |
| Wiring: backend Render chama Modal via HTTPS interno | ~1h |
| Testes A/B (CLIP CPU vs Modal GPU) | ~2h |
| Deploy + monitoramento de cold-start | ~2h |
| **Total** | **~12-16 horas** |

### 2.5 Risco de regressão

| Risco | Severidade | Mitigação |
|---|---|---|
| Cold-start Modal (5-15s no 1º request após idle de 5-10min) | 🟡 médio | Keepalive (cron pinging endpoint a cada 4 min) ou Modal `keep_warm=True` |
| Acurácia divergir entre ONNX CPU e GPU | 🟢 baixo | Mesmo modelo ONNX, mesmos pesos. Diferença numérica <0,001 |
| Latência adicional Render→Modal (HTTP interno) | 🟡 médio | ~50-100ms adicionais. Aceitável (ainda <500ms total) |
| Custo escalar não-linearmente com volume | 🟢 baixo | Pay-per-second escala bem; 100k scans/mês ≈ $25 |
| Falha do Modal indisponibiliza scan | 🔴 alto | Implementar fallback para CLIP CPU local OU mostrar erro elegante |

### 2.6 Impacto no usuário

| Aspecto | Impacto |
|---|---|
| **Celular** | 🟢 melhora — UX igual, scan mais rápido |
| **4G** | 🟢 melhora — backend menor cobre o gargalo |
| **Wi-Fi Cibi Sana** | 🟢 grande melhora — chega próximo da meta <500ms |
| **Bateria** | 🟢 neutro — processamento continua server-side |
| **Bundle frontend** | 🟢 zero mudança |
| **Compatibilidade** | 🟢 funciona em qualquer device (mesma arq atual) |
| **iOS Safari** | 🟢 sem dependência client-side |
| **Android antigo** | 🟢 sem dependência client-side |

### 2.7 Resumo Caminho A

✅ **Vantagens:** Mantém arquitetura, baixo custo (Modal), funciona em qualquer device, atinge meta em Wi-Fi.
⚠️ **Desvantagens:** Cold-start Modal (mitigável), custo escala com uso (mas barato), depende de rede.
🎯 **Atinge <500ms?** ✅ **SIM em Wi-Fi.** No 4G fica em ~600-900ms (limitado pela rede, fora do controle).

---

## 3. Caminho B — CLIP no Navegador (WebAssembly/WebGPU)

### 3.1 O que muda

Embarcar o modelo CLIP ONNX dentro do PWA. O frontend Vercel baixa o modelo (uma vez, cacheado pelo SW) e roda inferência local no celular do usuário. Backend Render só serve nutrição/Premium/dados.

**Stack técnica:**
- `@huggingface/transformers` (transformers.js) com backend `wasm` (universal) ou `webgpu` (rápido em devices novos)
- Modelo CLIP ViT-B/16 quantizado (Xenova/clip-vit-base-patch16) ou ViT-B/32 menor

### 3.2 Métricas estimadas

Dados empíricos (pesquisa transformers.js / WJARR-2025 / Xenova benchmarks):

| Métrica | Valor estimado | Fonte |
|---|---|---|
| **Inferência WASM (sem GPU) — CLIP ViT-B/16** | **3-8s no mobile médio** | transformers.js blogs 2025 |
| **Inferência WebGPU — iPhone 15+ ou Snapdragon 8 Gen 3** | 100-400ms | WJARR 2025 (mobilenet 4.7ms × ~50× para CLIP) |
| **Inferência WebGPU — iPhone 13/14, Android meio** | 400-1500ms | varia por GPU |
| **Latência total end-to-end (qualquer rede)** | igual à inferência (zero rede) | offline-capable |
| **Cold start (download 1ª vez)** | 30-90s (50-150MB modelo) | depende de rede |
| **Cold start (cache hit)** | 1-3s (carregar modelo do cache do SW) | conhecido |

### 3.3 Compatibilidade WebGPU em mobile (estado em 2026)

**Boa notícia (atualização 2025-2026):**
- ✅ Safari iOS 26+ suporta WebGPU desde Set/2025 (Apple lançou no iOS 26 → exige iPhone com iOS 26+)
- ✅ Chrome Android suporta WebGPU desde 2024
- ❌ Safari iOS 17 e 18 (anteriores ao 26) **não suportam** WebGPU — fallback obrigatório para WASM (lento)

**Distribuição realista do público SoulNutri (estimativa):**
- iPhones com iOS 26+ (lançado Set/2025): ~50-60% dos usuários iOS em Abr/2026
- iPhones com iOS 17/18 ainda: ~30-40% — vão sofrer com WASM puro (3-8s)
- Android moderno (2022+): ~60-70% suportam WebGPU
- Android antigo: 30-40% só WASM (lento)

### 3.4 Custo mensal estimado

| Item | Custo |
|---|---|
| Hospedagem do modelo no R2 (já existe) | ~$0,01/mês |
| Bandwidth de download do modelo (50MB × 1.000 instalações novas/mês) | ~$5-10/mês |
| Backend Render Standard (mantido para outros endpoints) | $25/mês |
| **Total** | **~$30-35/mês** ⚡ MUITO BAIXO escalando |

**Vantagem brutal de custo em escala:** com 1 milhão de scans/mês, o custo NÃO sobe (o trabalho é feito no celular do usuário). Caminho A escalaria para ~$50-100/mês no Modal.

### 3.5 Complexidade de implementação

| Etapa | Estimativa |
|---|---|
| Setup `@huggingface/transformers` no frontend | 1-2h |
| Download e quantização do CLIP ViT-B/16 (Xenova/clip já tem versão quantizada INT8 ~50MB) | 2-4h |
| Wiring: frontend gera embedding, envia ao backend que faz só similaridade + categoria | 4-6h |
| Detecção de WebGPU vs WASM com fallback | 2-3h |
| Service Worker cache do modelo (50MB) | 2-3h |
| UX: progress bar do download inicial | 2-3h |
| Testes em iPhone 13/14/15, Android variado | 4-8h |
| **Total** | **~20-30 horas** |

### 3.6 Risco de regressão

| Risco | Severidade | Mitigação |
|---|---|---|
| **Bundle size estoura** (50-150MB modelo) | 🔴 alto | SW cache + lazy load + carregar só na 1ª vez |
| **iPhone com iOS <26 ficam com 3-8s** (WASM) | 🔴 alto | Fallback para backend Render (rota dupla) ou exigir iOS 26+ |
| **Android low-end roda WASM lento** | 🟡 médio | Mesma estratégia de fallback |
| **Acurácia diverge** entre CLIP int8 quantizado vs FP32 atual | 🟡 médio | Validar com 30+ pratos antes de migrar |
| **Memória do navegador** (50-150MB pode ser despejado em celular com pressão) | 🟡 médio | Recarregar modelo se cache morre |
| **Bateria do celular** | 🟡 médio | Inferência GPU consome bateria — usuários podem reclamar |
| **Service Worker conflito** com PWA atual | 🟡 médio | Migração coordenada do SW |
| **Acessibilidade reduzida** (usuário com celular antigo fica de fora) | 🔴 alto | Manter rota backend como sempre-disponível |

### 3.7 Impacto no usuário

| Aspecto | Impacto |
|---|---|
| **Celular high-end (iPhone 15+, Galaxy S24+)** | 🟢 melhora drasticamente — <500ms atingível |
| **Celular médio (iPhone 13/14, Galaxy A54)** | 🟡 melhora marginal ou neutro (WebGPU OK ~400ms) |
| **Celular antigo (iPhone 11, Android 2020-)** | 🔴 piora drasticamente — WASM 3-8s |
| **4G** | 🟢 nada muda na rede (tudo local) |
| **5G** | 🟢 nada muda na rede |
| **Wi-Fi Cibi Sana** | 🟢 nada muda na rede |
| **Bateria** | 🔴 piora — inferência GPU/CPU local consome ~5-10% por sessão de uso |
| **Bundle frontend** | 🔴 piora — +50-150MB (download inicial) |
| **Compatibilidade Safari iOS** | 🔴 piora — só funciona em iOS 26+ |
| **Compatibilidade Android** | 🟡 mistura — moderno OK, antigo ruim |

### 3.8 Resumo Caminho B

✅ **Vantagens:** Custo escala perfeitamente, zero rede, offline-capable, latência teórica baixíssima em devices novos.
⚠️ **Desvantagens:** Bundle gigante, fragmentação de UX (depende do device), bateria, complexidade alta.
🎯 **Atinge <500ms?** 🟡 **SIM em iPhone 15+ / Snapdragon 8 Gen 3+. NÃO em devices médios/antigos.**

---

## 4. Comparativo lado-a-lado

| Critério | A. GPU Backend (Modal) | B. CLIP no Navegador |
|---|---|---|
| **Tempo inferência** | 30-80ms | 100ms - 8s (varia muito) |
| **Latência total Wi-Fi Cibi Sana** | 250-450ms ✅ | 100-1500ms (device-dep) |
| **Latência total 4G** | 600-900ms | 100-1500ms (device-dep) |
| **Custo mensal estimado (30k scans)** | $30-40 (BAIXO) | $30-35 (BAIXO) |
| **Custo escalando (1M scans)** | ~$50-100 | $30-35 (constante) |
| **Complexidade implementação** | ~12-16h | ~20-30h |
| **Risco de regressão** | 🟡 médio (cold start) | 🔴 alto (fragmentação) |
| **Impacto bundle** | 🟢 zero | 🔴 +50-150MB |
| **Impacto bateria** | 🟢 zero | 🔴 maior consumo |
| **Compatibilidade universal** | 🟢 100% (qualquer device) | 🔴 fragmentada |
| **Atinge meta <500ms?** | 🟢 sim em Wi-Fi | 🟡 sim em devices premium |
| **Funciona em iPhone iOS 17/18** | 🟢 sim | 🔴 muito lento (WASM) |
| **Funciona offline** | 🔴 não | 🟢 sim (após 1ª carga) |
| **Tempo para entrega em produção** | 1-2 semanas | 4-6 semanas |
| **Reversibilidade** | 🟢 alta (rollback simples) | 🔴 baixa (PWA cache complica) |

---

## 5. Análise específica para SoulNutri

### Cenário de uso primário (Cibi Sana, hoje)
- Usuários no buffet, Wi-Fi razoável
- Volume estimado atual: dezenas a algumas centenas de scans/dia
- Maioria dos usuários: smartphones recentes (Cibi Sana = clientela com poder aquisitivo)

**Implicação:** Em Wi-Fi local + smartphones modernos, **AMBOS os caminhos atingiriam a meta**. A questão é o "fora do Cibi Sana".

### Cenário de uso secundário (fora do Cibi Sana)
- 4G/5G variável
- Devices variados (incluindo antigos)
- Volume estimado: muito menor que Cibi Sana

**Implicação:** Caminho A garante UX consistente independente de device. Caminho B fragmenta — usuário com iPhone antigo terá experiência ruim.

### Custo no horizonte de 12 meses

Premissa de crescimento: 30k scans/mês hoje → 100k em 12 meses.

| Caminho | Hoje | 6 meses (60k) | 12 meses (100k) |
|---|---|---|---|
| A. Modal GPU | ~$35/mês | ~$45/mês | ~$60/mês |
| B. WASM/WebGPU | ~$32/mês | ~$33/mês | ~$33/mês |

**Diferença em 12 meses:** ~$300 acumulados. Não é fator decisivo.

---

## 6. Recomendação Objetiva

# 🥇 Recomendação: COMEÇAR PELO CAMINHO A (GPU no Backend, variante A4 — Híbrido Render + Modal)

## Por quê?

### 1. Garantia de UX consistente
Caminho A entrega melhoria **para 100% dos usuários** independente do device. Caminho B beneficia desproporcionalmente quem já tem celular caro e prejudica quem tem celular antigo. Para um app de buffet que mistura clientela, isso é problemático.

### 2. Tempo até produção
- Caminho A: **1-2 semanas** (12-16h de dev + testes)
- Caminho B: **4-6 semanas** (20-30h dev + ciclo longo de testes em N devices)

Em ciclo de melhoria contínua, A entrega ROI 3-4× mais rápido.

### 3. Risco controlado e reversível
A4 (Híbrido) permite **rollback instantâneo**: se Modal falhar/cair, basta um feature flag para o backend voltar a usar CLIP CPU local. Caminho B é difícil de reverter por causa do PWA cache do modelo (50MB cacheado nos celulares dos usuários).

### 4. Custo previsível e baixo
$30-40/mês para 30k scans é desprezível. Mesmo com 100k scans, ~$60/mês. Não precisa otimização agressiva.

### 5. Não fecha portas
Caminho A **não impede** Caminho B no futuro. Se o produto crescer para 1M+ scans/mês ou se quisermos modo offline (ex: apresentação em local sem Wi-Fi), B vira o segundo passo natural — mas com base sólida já em produção.

## Riscos do Caminho A escolhido

| Risco | Mitigação concreta |
|---|---|
| **Cold start Modal** (5-15s no 1º request após idle) | Implementar `keep_warm=True` ou cron de keepalive de 4min |
| **Falha de rede entre Render e Modal** | Manter CLIP CPU como fallback no Render (já existe — basta feature flag) |
| **Acurácia divergir GPU vs CPU** | Validação A/B obrigatória com 30+ pratos antes do switch 100% |
| **Vendor lock-in com Modal** | Modal usa stack ONNX padrão; migrável para Replicate/RunPod em <1 dia se necessário |

## Critérios de sucesso para validar A em produção

1. **Latência p50 (mediana) <500ms** em scans pelo Wi-Fi do Cibi Sana
2. **Latência p99 (worst case) <1500ms** mesmo com cold start ocasional
3. **Acurácia top-1 mantida ou melhor** em sample de 30 pratos vs baseline atual
4. **Custo mensal <$50** com 30k scans
5. **Zero regressão** nos endpoints não-CLIP (nutrição, Premium, Admin, etc.)

## Quando passar para o Caminho B (gatilho futuro)

Considerar B somente se 1+ dos seguintes ocorrer:
- Volume de scans >500k/mês (custo Modal escalar a >$100/mês)
- Demanda real de modo offline em locais sem Wi-Fi
- Safari iOS 26+ adoção >85% no público real do app
- Redução de latência de rede crítica que A não resolva (ex: 4G muito ruim)

---

## 7. Decisão pendente

⏸️ **Aguardando autorização explícita para iniciar Caminho A.**

Se autorizar, próximos passos seriam:
1. Setup Modal account + reservar GPU (você fornece credenciais)
2. POC: empacotar `image_embedding_from_bytes` como função Modal
3. Wiring: backend Render chama Modal com feature flag (default OFF)
4. Validação A/B controlada (10% do tráfego)
5. Switch 100% após validação dos 5 critérios da Seção 6

**Tempo estimado total até produção 100%:** **2 semanas** (assumindo dev focado).

---

## 8. Restrições mantidas integralmente

- ❌ Nenhum código alterado neste estudo
- ❌ Nenhum deploy
- ❌ Backend não modificado
- ❌ Frontend não modificado
- ❌ Modelo CLIP não modificado
- ❌ Endpoints não modificados
- ❌ Infraestrutura não modificada
- ✅ Apenas estudo técnico documentado

---

**FIM DO ESTUDO. Decisão arquitetural protegida com base técnica.**
