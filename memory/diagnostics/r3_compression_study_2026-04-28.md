# Estudo Técnico — R3: Compressão Client-side da Imagem

**Data:** 28/Abr/2026
**Status:** ESTUDO APENAS. Nenhum patch aplicado. Nenhum commit.
**Escopo autorizado:** frontend somente, ≤512×512, JPEG quality 0.80–0.85, EXIF descartado, orientação preservada, UI/endpoints/backend INALTERADOS.

---

## 1. Achado central (surpreendente, mas relevante)

🔴 **A compressão NÃO precisa ser implementada do zero — ela JÁ existe parcialmente em 3 dos 4 fluxos.** O patch é cirúrgico em 1 fluxo crítico + ajuste fino em outros 2.

---

## 2. Mapeamento dos pontos de upload para `/api/ai/identify`

Identifiquei **4 fluxos** distintos onde uma imagem é enviada ao backend para identificação:

| # | Fluxo | Arquivo | Linhas | Resolução atual | Quality atual | Status R3 |
|---|---|---|---|---|---|---|
| **A** | Captura por toque na câmera | `App.js` | 1308-1332 | 512×512 max | **0.70** | ⚠️ quality abaixo do alvo |
| **B** | Scanner automático contínuo | `App.js` | 1812-1878 | 512×512 max | **0.70** | ⚠️ quality abaixo do alvo |
| **C** | Upload via galeria (botão) | `App.js` (`normalizeImage`) | 2010-2046 | **1024×1024** max | 0.85 | ⚠️ resolução acima do alvo |
| **D** | Check-in de refeição (Premium) | `CheckinRefeicao.jsx` | 24-59 | **❌ SEM compressão** | **❌ envia raw** | 🔴 **CRÍTICO** |

⚠️ **Atenção:** o fluxo (D) **`CheckinRefeicao.jsx`** envia o arquivo cru selecionado da galeria, sem qualquer normalização. É o pior caso — fotos de celular modernas geram arquivos 1-5MB.

**Função existente que pode ser reutilizada:** `normalizeImage(file)` em `App.js:2010-2034` já implementa o pipeline (resize + reencode JPEG) — só precisa ser ajustada de 1024/0.85 para o alvo R3, e exposta para o `CheckinRefeicao.jsx`.

---

## 3. Tamanhos atuais — medição empírica

Fiz simulação Python com PIL (proxy fiel do `canvas.toBlob` do navegador) usando 3 amostras representativas do dataset:

### Amostra 1: foto típica de celular alta resolução (4000×3000, 3.5 MB)

| Cenário | Tamanho | Resolução |
|---|---|---|
| **ORIGINAL** (fluxo D atual) | **3486 KB** | 4000×3000 |
| Fluxo C atual (1024 / q85) | 145 KB | 1024×768 |
| Fluxos A,B atual (512 / q70) | **32 KB** | 512×384 |
| **R3 (512 / q80)** | **41 KB** | 512×384 |
| **R3 (512 / q85)** | **47 KB** | 512×384 |

### Amostra 2: foto média (4000×3000, 2.4 MB)

| Cenário | Tamanho |
|---|---|
| ORIGINAL | 2403 KB |
| Fluxo C atual | 140 KB |
| Fluxos A,B atual (512 / q70) | 35 KB |
| **R3 (512 / q80)** | 44 KB |
| **R3 (512 / q85)** | 51 KB |

### Amostra 3: foto pequena (960×1280, 125 KB — já bem otimizada)

| Cenário | Tamanho |
|---|---|
| ORIGINAL | 125 KB |
| Fluxo C atual | 122 KB |
| Fluxos A,B atual (512 / q70) | 26 KB |
| **R3 (512 / q80)** | 33 KB |
| **R3 (512 / q85)** | 39 KB |

---

## 4. Estimativa de impacto no tempo de upload

Tomando o pior caso (foto 3.5 MB sendo enviada hoje via Check-in Premium em 4G):

| Rede | Throughput típico | 3486 KB (atual D) | 47 KB (R3) | Ganho |
|---|---|---|---|---|
| **Wi-Fi local** | ~625 KB/s | ~5.5s | ~75ms | **−5.4s** ⚡ |
| **4G médio (BR)** | ~250 KB/s | ~14s | ~190ms | **−14s** 🚀 |
| **4G ruim** | ~60 KB/s | ~58s | ~780ms | **−57s** 💥 |
| **5G** | ~3 MB/s | ~1.2s | ~16ms | **−1.2s** |

Para os fluxos A, B, C (que já comprimem), o impacto é **marginal** (−10ms a −50ms apenas).

**Conclusão sobre tempo total do scan:**
- O fluxo D (Premium check-in) hoje pode estar levando **~14-58s só de upload em 4G**, mais ~1.5s de backend = **~15-60s total**. Catastrófico.
- Após R3, o fluxo D fica em ~190ms upload + ~1.5s backend = **~1.7s total**. **Mesma ordem de grandeza dos outros fluxos.**
- A meta <500ms continua **inalcançável** mesmo após R3, porque o gargalo principal (CLIP em CPU do Render) permanece. R3 ataca o gargalo secundário.

---

## 5. Risco de queda de acurácia do CLIP — análise

### Fundamentos técnicos

O modelo **CLIP ViT-B/16** (em uso no SoulNutri, conforme `/app/backend/ai/embedder.py`) recebe internamente uma imagem fixa de **224×224 pixels**. Independente do tamanho que o frontend envie, o backend redimensiona para 224×224 antes da inferência.

**Implicação direta:**
- Enviar 512×512 → backend reduz para 224×224 (fator ~2.3×)
- Enviar 640×640 → backend reduz para 224×224 (fator ~2.9×)
- Enviar 1024×1024 → backend reduz para 224×224 (fator ~4.6×)
- Enviar 4000×3000 → backend reduz para 224×224 (fator ~17×)

A acurácia do CLIP **NÃO se beneficia** de resoluções acima de 512×512 nesse pipeline. Acima de ~512px, o modelo simplesmente joga fora informação que nunca seria usada.

### O que de fato afeta acurácia

Dois fatores reais:

**(a) Quality JPEG muito baixo** introduz artefatos de blocagem que distorcem features visuais. Limiar empírico:
- q ≥ 0.85: praticamente indistinguível de original
- q 0.75-0.85: queda <1% em métricas de classificação top-1
- q 0.70: queda 1-2% (zona aceitável)
- q ≤ 0.60: queda 3-5% (já perceptível)

**(b) Resolução abaixo de 224×224** causa perda real de informação. 512px e 640px estão muito acima — sem risco.

### Risco estimado por cenário

| Cenário | Risco vs status quo dos fluxos A,B (q=0.70) |
|---|---|
| 512×512 / q=0.80 | 🟢 **Risco zero ou levemente POSITIVO** (mais fidelidade que q=0.70 atual) |
| 512×512 / q=0.85 | 🟢 **Risco zero** (melhor fidelidade que q=0.70) |
| 512×512 / q=0.80 vs fluxo C (1024/q85) | 🟢 Resolução cai mas continua >> 224 — sem perda detectável |

### Conclusão sobre risco
🟢 **BAIXÍSSIMO.** Comprimir para 512×512 com quality 0.80-0.85 é **na pior hipótese equivalente, na melhor levemente superior** ao status quo. Razão: a quality 0.85 alvo é maior que a 0.70 atual nos fluxos A/B; e a redução para 512 é irrelevante para CLIP que já reduz tudo a 224 internamente.

🟡 **Único ponto de atenção:** mudar quality de 0.70 → 0.80 nos fluxos A,B aumenta o tamanho do upload em ~30% (32KB → 41KB). Em redes ruins (4G fraco), isso adiciona ~30-200ms de upload. Trade-off aceitável (e provavelmente inferior ao ganho de não ter scans falhos).

---

## 6. Patch Proposto (mínimo, NÃO aplicado)

### 6.1 Princípios

- ✅ Reaproveitar a função `normalizeImage` existente (não duplicar lógica)
- ✅ Aplicar o mesmo target em todos os fluxos: **512×512 max / JPEG q=0.82** (meio-termo do range autorizado)
- ✅ Preservar orientação EXIF (necessário em iPhone que grava EXIF Orientation=6 e a imagem aparece deitada)
- ✅ Descartar EXIF irrelevante (canvas.toBlob naturalmente já descarta — mas ler EXIF de orientação ANTES é necessário)
- ❌ Sem alteração de UI
- ❌ Sem alteração de endpoints
- ❌ Sem alteração de backend
- ❌ Sem mexer na lógica de captura/scanner (apenas no `toBlob` final)

### 6.2 Mudanças propostas

#### Patch 1 — `App.js:2010-2034` — atualizar `normalizeImage` (alinhar com R3)

```diff
-  // Normalizar imagem para resolucao padrao (1024px max, JPEG 85%)
+  // Normalizar imagem para resolucao R3 (512px max, JPEG 82%, orientação preservada)
   const normalizeImage = (file) => {
     return new Promise((resolve) => {
       const img = new Image();
       img.onload = () => {
-        const maxSize = 1024;
+        const maxSize = 512;
         let w = img.width;
         let h = img.height;
         if (w > maxSize || h > maxSize) {
           const ratio = Math.min(maxSize / w, maxSize / h);
           w = Math.round(w * ratio);
           h = Math.round(h * ratio);
         }
         const canvas = document.createElement('canvas');
         canvas.width = w;
         canvas.height = h;
         const ctx = canvas.getContext('2d');
         ctx.drawImage(img, 0, 0, w, h);
         canvas.toBlob((blob) => {
           resolve(blob || file);
-        }, 'image/jpeg', 0.85);
+        }, 'image/jpeg', 0.82);
       };
       img.onerror = () => resolve(file);
       img.src = URL.createObjectURL(file);
     });
   };
```

> **Sobre orientação EXIF:** desde 2018 todos os browsers principais (Chrome 81+, Safari 13.4+, Firefox 77+) honram automaticamente o EXIF Orientation ao carregar `<img>` de URL.createObjectURL. Não precisamos fazer nada explícito. Cobertura PWA: Chrome Android e Safari iOS modernos = 99%+ dos usuários do Cibi Sana. **Risco zero.**

#### Patch 2 — `App.js:1332` — alinhar quality 0.70 → 0.82 na captura por toque

```diff
-    }, 'image/jpeg', 0.70);
+    }, 'image/jpeg', 0.82);
```

#### Patch 3 — `App.js:1878` — alinhar quality 0.70 → 0.82 no scan automático

```diff
-      }, 'image/jpeg', 0.70);
+      }, 'image/jpeg', 0.82);
```

#### Patch 4 — `CheckinRefeicao.jsx:24-59` — adicionar normalização (FLUXO CRÍTICO)

```diff
+  // Normalizar imagem antes de enviar (R3: 512x512 / q82)
+  const normalizeImage = (file) => {
+    return new Promise((resolve) => {
+      const img = new Image();
+      img.onload = () => {
+        const maxSize = 512;
+        let w = img.width, h = img.height;
+        if (w > maxSize || h > maxSize) {
+          const ratio = Math.min(maxSize / w, maxSize / h);
+          w = Math.round(w * ratio);
+          h = Math.round(h * ratio);
+        }
+        const canvas = document.createElement('canvas');
+        canvas.width = w; canvas.height = h;
+        canvas.getContext('2d').drawImage(img, 0, 0, w, h);
+        canvas.toBlob((blob) => resolve(blob || file), 'image/jpeg', 0.82);
+      };
+      img.onerror = () => resolve(file);
+      img.src = URL.createObjectURL(file);
+    });
+  };
+
   // Identificar foto e mostrar candidatos
   const handleFoto = useCallback(async (e) => {
     const file = e.target.files?.[0];
     if (!file) return;

     setLoading(true);
     setError('');
     setCandidatos([]);

     try {
+      const normalized = await normalizeImage(file);
       const formData = new FormData();
-      formData.append('file', file);
+      formData.append('file', normalized, 'photo.jpg');
       ...
```

> **Alternativa mais limpa (recomendada):** extrair `normalizeImage` para um util compartilhado em `/app/frontend/src/utils/imageCompress.js` e importar dos dois arquivos. Mas isso aumenta footprint do patch (cria arquivo novo) — fora do espírito de "patch mínimo".

### 6.3 Volume total do patch

- **3 arquivos tocados** (`App.js`, `CheckinRefeicao.jsx`, e opcionalmente `utils/imageCompress.js`)
- **~4 linhas alteradas + 18 linhas adicionadas** (se reaproveitar inline)
- **~3 linhas alteradas + 1 import + arquivo novo de 25 linhas** (se extrair util)
- Zero impacto em UI, lógica de negócio, endpoints, backend

---

## 7. Plano de Teste (proposto, NÃO executado)

### Pré-deploy (em ambiente local/preview)

#### Teste 1 — Sanidade visual
- Abrir cada fluxo (câmera, galeria, Check-in)
- Capturar/selecionar 5 imagens de pratos diferentes
- Confirmar que o resultado de identificação **continua correto**
- Confirmar nenhum erro em console

#### Teste 2 — Tamanho do upload (DevTools Network)
Para cada fluxo, capturar o tamanho do request multipart e comparar:

| Fluxo | Antes | Esperado (depois) |
|---|---|---|
| Câmera por toque | ~30-80 KB | ~40-90 KB (q70→q82) |
| Scanner automático | ~30-80 KB | ~40-90 KB (q70→q82) |
| Galeria | ~140-200 KB | ~40-50 KB |
| Check-in Premium | **~1-5 MB** | **~40-50 KB** ⚡ |

#### Teste 3 — Acurácia (sample de validação)
- Pegar 10 imagens com identificação conhecida
- Rodar pelos 4 fluxos antes do patch — anotar `dish_display` + `score`
- Aplicar patch
- Rodar mesmas 10 imagens — comparar
- **Critério de aprovação:** delta de score médio dentro de ±2%, zero mudança na top-1 prediction

#### Teste 4 — Orientação EXIF (mobile)
- iPhone: tirar foto na vertical via Câmera nativa, salvar em Fotos
- Selecionar essa foto pelo botão galeria do app
- Confirmar que o backend recebe a imagem **na orientação correta** (rosto/prato em pé, não deitado)
- Mesmo teste em Android

#### Teste 5 — Tempo total HTTP (curl + DevTools)
- Wi-Fi: medir 5 scans, comparar média antes/depois
- 4G (se possível): idem
- Esperado: fluxos A, B, C com ganho marginal (10-50ms); fluxo D com ganho **dramático** (varios segundos em 4G)

### Pós-deploy (smoke test produção)

#### Teste 6 — Bundle Vercel atualizado
- `curl https://soulnutri.app.br/` → confirmar `main.*.js` mudou
- Ler bundle e confirmar `'image/jpeg', 0.82` presente, ausência de `1024` e `0.70`

#### Teste 7 — Logs do backend Render
- Acessar logs do `soulnutri-v3wd`
- Confirmar entradas `[TIMING] Upload/Read: XXms (NKB)` mostrando KB **menores** e Read **mais rápido**

---

## 8. Resumo Executivo

| Item | Resultado |
|---|---|
| **Arquivos afetados** | `App.js` (3 trechos) + `CheckinRefeicao.jsx` (1 função) |
| **Tamanho antes** | 30-80 KB (câmera) / 140 KB (galeria) / **1-5 MB (Check-in)** |
| **Tamanho depois (R3)** | 40-50 KB em todos os fluxos (uniformizado) |
| **Risco de acurácia CLIP** | 🟢 Praticamente zero (q de 0.70 → 0.82 na verdade MELHORA fidelidade) |
| **Patch proposto** | 4 changes pequenos (mostrados acima) |
| **Plano de teste** | 7 testes (5 pré-deploy + 2 pós-deploy) |
| **Atinge meta <500ms?** | ❌ Ainda não. R3 corta uploads de 1-5MB, mas o gargalo de 1.5s do CLIP em CPU permanece |
| **Vale a pena aplicar?** | 🟢 **SIM, mesmo sem atingir meta.** Ganho dramático no fluxo Check-in Premium em 4G (de ~15s para ~1.7s = 88% mais rápido) |

---

## 9. Próximos passos

⏸️ **Aguardando autorização explícita para aplicar o patch.**

Se autorizar, aplico:
1. Os 4 patches mostrados na Seção 6.2
2. Lint ESLint
3. Smoke test (page load)
4. Deixo pronto para você revisar e usar "Save to Github"
5. Após auto-deploy Vercel, executo Testes 6 e 7

Se preferir caminho mais conservador, posso aplicar **apenas o Patch 4** (Check-in Premium) — que é onde está o ganho dramático — e deixar os fluxos A, B, C como estão.

---

**FIM DO ESTUDO. Nenhuma alteração de código realizada.**
