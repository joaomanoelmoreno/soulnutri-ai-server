# Auditoria Completa do Dataset — SoulNutri
**Data:** 2026  
**Status:** SOMENTE LEITURA — aguardando aprovação para limpeza

---

## 1. FONTES DE IMAGEM

| Fonte | Status | Detalhes |
|---|---|---|
| `organized/` (local) | Ativa | 191 pastas / 4389 imagens — única fonte do build_index |
| MongoDB `dish_storage` | Presente | 194 docs (campos vazios no sample — verificar) |
| MongoDB `dishes.imagem` | Ausente | 0/195 dishes têm campo `imagem` |
| R2 (Cloudflare) | Externo | URLs não rastreáveis localmente |
| `/app/backups/v1.23/` | Backup | Index antigo, não usado no build atual |

**Fonte canônica proposta:** `organized/` é a única fonte do build_index.  
R2/Admin = fonte oficial de imagens de exibição. `organized/` deve ser gerado exclusivamente a partir de R2.

---

## 2. RESUMO DE CONTAMINAÇÃO

| Categoria | Total |
|---|---|
| Arquivos MD5 duplicados entre pastas diferentes | **36** |
| Pares de pastas com contaminação | **8 pares** |
| Pastas 100% contaminadas no index | **1 (Ceviche)** |
| Pastas parcialmente contaminadas no index | **3 (Hamburguer Vegano, Muqueca, Sobrecoxa Limao)** |
| Pastas com fotos de outro prato por nome | **3 (Maminha Madeira, Sobrecoxa Limao, Arroz Integral)** |
| Pastas faltando (mencionadas, não existentes) | **3** |
| Pratos com < 5 fotos no index | **5** |

---

## 3. DUPLICATAS MD5 ENTRE PASTAS (36 arquivos)

### Par 1: Ceviche de Banana da Terra ↔ Muqueca de Banana da Terra — 20 arquivos
🔴 CRÍTICO — Ceviche 10/10 no index são fotos de moqueca

| MD5 | Arquivo em Ceviche | Arquivo em Muqueca |
|---|---|---|
| 1bff9093 | cevichedebananadaterra024.jpeg | moquecadebanadaterra07.jpeg |
| 5387cb03 | cevichedebananadaterra019.jpeg | moquecadebanadaterra02.jpeg |
| 236fab4a | cevichedebananadaterra034.jpeg | moquecadebanadaterra17.jpeg |
| dba54b64 | moquecadebanadaterra16.jpeg | moquecadebanadaterra16.jpeg |
| b0b18b71 | moquecadebanadaterra04.jpeg | moquecadebanadaterra04.jpeg |
| e3e81092 | moquecadebanadaterra05.jpeg | moquecadebanadaterra05.jpeg |
| 39bc5179 | moquecadebanadaterra08.jpeg | moquecadebanadaterra08.jpeg |
| 780b9fe8 | moquecadebanadaterra11.jpeg | moquecadebanadaterra11.jpeg |
| 48ed6311 | moquecadebanadaterra12.jpeg | moquecadebanadaterra12.jpeg |
| d396a523 | moquecadebanadaterra15.jpeg | moquecadebanadaterra15.jpeg |
| 20912dce | moquecadebanadaterra20.jpeg | moquecadebanadaterra20.jpeg |
| 58b0f0f1 | moquecadebanadaterra01.jpeg | moquecadebanadaterra01.jpeg |
| 8ca5ffd9 | moquecadebanadaterra03.jpeg | moquecadebanadaterra03.jpeg |
| 6cc69120 | cevichedebananadaterra023.jpeg | moquecadebanadaterra06.jpeg |
| 7afdd438 | cevichedebananadaterra026.jpeg | moquecadebanadaterra09.jpeg |
| 704d28c2 | cevichedebananadaterra027.jpeg | moquecadebanadaterra10.jpeg |
| e06c3050 | cevichedebananadaterra030.jpeg | moquecadebanadaterra13.jpeg |
| f29e6b74 | cevichedebananadaterra031.jpeg | moquecadebanadaterra14.jpeg |
| cc60c867 | cevichedebananadaterra035.jpeg | moquecadebanadaterra18.jpeg |
| 663dabc2 | muqueca_de_banana_da_terra_vegana_*.jpg | muquecadebananadaterra37.jpg |

**MD5 cruzado em 3 pastas (Ceviche + Muqueca + Farofa):**
- MD5=28842afd: `cevichedebananadaterra017.jpeg` ≡ `moquecadebanadaterra.jpeg` ≡ `Farofa de Banana da Terra/farofadebananadaterra09.jpeg`

### Par 2: Hamburger Bovino ↔ Hamburguer Vegano — 7 arquivos
🟠 Hamburguer Vegano 7/10 no index são fotos de hambúrguer bovino

| MD5 | Arquivo em Hamburguer Vegano | Arquivo em Hamburger Bovino |
|---|---|---|
| c75e6f6a | hamburguervegano.jpeg / hamburguervegano012.jpeg | hamburgerbovino061.jpeg |
| ffdd74b2 | hamburguervegano016.jpeg / hamburguervegano04.jpeg | hamburgerbovino065.jpeg |
| f8f6eed8 | hamburguervegano03.jpeg / hamburguervegano015.jpeg | hamburgerbovino064.jpeg |
| + 1 mais | hamburguervegano01.jpeg | hamburgerbovino06*.jpeg |

### Par 3: Sobrecoxa ao Limao ↔ Sobrecoxa ao Tandoori — 3 arquivos
🟠 Sobrecoxa ao Limao 3/10 no index são fotos de Tandoori (nomeadas `sobrecoxaaotucupi*`)

- sobrecoxaaotucupi016.jpeg ≡ sobrecoxaaotandoori026.jpeg
- sobrecoxaaotucupi014.jpeg ≡ sobrecoxaaotandoori024.jpeg + sobrecoxaaotucupi03.jpeg
- sobrecoxaaotucupi018.jpeg ≡ sobrecoxaaotucupi01.jpeg ≡ sobrecoxaaotandoori028.jpeg

### Par 4: Arroz 7 Graos ↔ Arroz Integral com Legumes — 2 arquivos
⚠️ Não entram no index (posição > 10) mas risco no rebuild sem limite

- arroz7graos054.jpeg ≡ arrozintegralcomlegumes040.jpeg
- arroz7graos051.jpeg ≡ arrozintegralcomlegumes039.jpeg

### Par 5: Arroz 7 Graos ↔ Arroz com Brocolis e Amendoas — 1 arquivo
- arrozde7graoscomamendoas07.jpeg ≡ arrozcombrocoliseamendoas013.jpeg

### Par 6: Brocolis ao Alho ↔ Brocolis com Parmesao — 1 arquivo
- brocoliscomparmesao05_teste.jpeg ≡ brocoliscomparmesao023.jpeg ≡ brocoliscomparmesao05.jpeg

### Par 7: Risone ao Creme de Limao e Bacon ↔ Risone ao Pesto — 1 arquivo
- risoneaocremedelimao13.jpeg ≡ risoneaopesto019.jpeg

---

## 4. CONTAMINAÇÃO POR NOME

| Pasta | Arquivos com nome de outro prato | Prato do nome |
|---|---|---|
| Maminha Molho Madeira | 18 arquivos `maminhaaomolhomostarda*.jpeg` | Maminha ao Molho Mostarda |
| Arroz Integral | 1 arquivo `arrozbranco026.jpeg` | Arroz Branco |
| Sobrecoxa ao Limao | 3 arquivos `sobrecoxaaotucupi*.jpeg` | Sobrecoxa ao Tucupi (?) |
| Ceviche de Banana da Terra | `muqueca_de_banana_da_terra_vegana_*.jpg` | Muqueca de Banana da Terra |
| Hamburger Bovino | `hamburguerbovino_correct_*.jpg` | ok — nome correto |

---

## 5. STATUS DAS PASTAS CRÍTICAS

| Pasta | Status | No index | Contaminados | Observação |
|---|---|---|---|---|
| Ceviche de Banana da Terra | 🔴 100% CONTAMINADO | 10/10 | 10/10 | Nenhuma foto real de ceviche |
| Muqueca de Banana da Terra | 🟠 80% CONTAMINADO | 10/10 | 8/10 | 2 fotos únicas (nova foto + 1 correct) |
| Hamburguer Vegano | 🟠 70% CONTAMINADO | 10/10 | 7/10 | Fotos de hambúrguer bovino |
| Sobrecoxa ao Limao | 🟠 30% CONTAMINADO | 10/10 | 3/10 | Fotos de Tandoori/Tucupi |
| Lasanha de Espinafre | ✅ LIMPO | 10/10 | 0 | |
| File de Peixe ao Misso | ✅ LIMPO | 10/10 | 0 | 4/10 nomeados 'molhomisso' (mesmo prato?) |
| Tortilha Espanhola de Batata | ✅ LIMPO | 8/8 | 0 | Poucas fotos (8), todas do mesmo dia |
| Maminha Molho Madeira | 🟡 NOME ERRADO | 10/10 | 0 (MD5) | 6/10 são fotos de "Mostarda" por nome |
| Arroz Branco | ✅ LIMPO | 10/10 | 0 | 1 outlier (idx=82, não-contaminado por MD5) |
| Arroz Integral | ✅ LIMPO | 6/6 | 0 | 1 arquivo `arrozbranco` fora da seleção |
| Tabule | ✅ LIMPO | 10/10 | 0 | |
| Tabule de Quinoa | ❌ NÃO EXISTE | — | — | Pasta ausente |
| Maminha ao Molho Mostarda | ❌ NÃO EXISTE | — | — | Fotos em "Maminha Molho Madeira" |
| Maminha ao Molho Madeira | ❌ NÃO EXISTE | — | — | Pasta existe como "Maminha Molho Madeira" (sem "ao") |

---

## 6. PRATOS COM FOTOS INSUFICIENTES (< 5 no index)

| Prato | No index | Contaminados | Risco |
|---|---|---|---|
| Espaguete de Abobrinha ao Pesto | 1 | 0 | CRÍTICO |
| Maminha ao Molho Gorgonzola | 2 | 0 | Alto |
| Polenta com Ragu | 2 | 0 | Alto |
| Risoto de Alho Poro | 3 | 0 | Alto |
| Creme de Milho | 4 | 0 | Médio |

---

## 7. COMANDOS PROPOSTOS DE LIMPEZA (NÃO EXECUTAR SEM APROVAÇÃO)

### 7a. Ceviche de Banana da Terra — remover todos os arquivos contaminados (35 → 14 únicos)
```python
# Remove tudo da pasta Ceviche que tem MD5 idêntico à pasta Muqueca
import os, hashlib, collections

organized = "/app/datasets/organized"
def md5(p):
    with open(p,'rb') as f: return hashlib.md5(f.read()).hexdigest()

muqueca_dir = f"{organized}/Muqueca de Banana da Terra"
muqueca_md5s = {md5(f"{muqueca_dir}/{f}") for f in os.listdir(muqueca_dir)
                if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))}

ceviche_dir = f"{organized}/Ceviche de Banana da Terra"
to_remove = []
for f in os.listdir(ceviche_dir):
    if not f.lower().endswith(('.jpg','.jpeg','.png','.webp')): continue
    h = md5(f"{ceviche_dir}/{f}")
    if h in muqueca_md5s:
        to_remove.append(f"{ceviche_dir}/{f}")

print(f"Arquivos a remover de Ceviche: {len(to_remove)}")
for p in sorted(to_remove): print(f"  rm '{p}'")
# Para executar: for p in to_remove: os.remove(p)
```
**Resultado esperado:** 35 → ~14 arquivos (os que têm nomes `cevichedebananadaterra*` e não têm MD5 em Muqueca).  
**ATENÇÃO:** Precisará confirmar visualmente se esses 14 restantes são fotos reais de ceviche.

### 7b. Hamburguer Vegano — remover arquivos com MD5 de Hamburger Bovino (18 → ~11)
```python
bovino_dir = f"{organized}/Hamburger Bovino"
bovino_md5s = {md5(f"{bovino_dir}/{f}") for f in os.listdir(bovino_dir)
               if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))}

vegano_dir = f"{organized}/Hamburguer Vegano"
to_remove_veg = []
for f in os.listdir(vegano_dir):
    if not f.lower().endswith(('.jpg','.jpeg','.png','.webp')): continue
    h = md5(f"{vegano_dir}/{f}")
    if h in bovino_md5s:
        to_remove_veg.append(f"{vegano_dir}/{f}")

print(f"A remover de Hamburguer Vegano: {len(to_remove_veg)}")
for p in sorted(to_remove_veg): print(f"  rm '{p}'")
```
**ATENÇÃO:** Após remoção, Hamburguer Vegano terá ~11 fotos. Verificar se são suficientes e realmente de hambúrguer vegano.

### 7c. Sobrecoxa ao Limao — remover arquivos com MD5 de Sobrecoxa ao Tandoori
```python
# 3 arquivos: sobrecoxaaotucupi016, 014, 018
# Os listdir só pega os 10 primeiros — verificar se ainda restam fotos limpas após remoção
```

### 7d. Maminha Molho Madeira — mover/separar fotos de Mostarda
```python
# 18 arquivos 'maminhaaomolhomostarda*.jpeg' estão em 'Maminha Molho Madeira'
# Proposta: criar pasta 'Maminha ao Molho Mostarda' e mover esses 18 arquivos
mostarda_dir = f"{organized}/Maminha ao Molho Mostarda"
madeira_dir  = f"{organized}/Maminha Molho Madeira"
# os.makedirs(mostarda_dir, exist_ok=True)
to_move = [f for f in os.listdir(madeira_dir) if 'mostarda' in f.lower()]
print(f"A mover para Maminha ao Molho Mostarda: {len(to_move)}")
for f in sorted(to_move): print(f"  mv '{madeira_dir}/{f}' '{mostarda_dir}/{f}'")
```
**Resultado:** Cria prato "Maminha ao Molho Mostarda" (18 fotos) e limpa "Maminha Molho Madeira".

### 7e. Arroz Integral — remover arquivo arrozbranco026.jpeg
```bash
rm '/app/datasets/organized/Arroz Integral/arrozbranco026.jpeg'
```

### 7f. Arroz/Brocolis — remover duplicatas menores
```python
# Par 4: arroz7graos054.jpeg ≡ arrozintegralcomlegumes040.jpeg → remover de Arroz 7 Graos
# Par 5: arrozde7graoscomamendoas07.jpeg ≡ arrozcombrocoliseamendoas013.jpeg → verificar qual é o original
# Par 6: brocoliscomparmesao05_teste.jpeg em Brocolis ao Alho → remover (arquivo _teste)
# Par 7: risoneaocremedelimao13.jpeg ≡ risoneaopesto019.jpeg → verificar original
```

---

## 8. PASSOS APÓS APROVAÇÃO E LIMPEZA

1. Executar comandos de limpeza acima
2. Verificar visualmente as fotos remanescentes de `Ceviche de Banana da Terra`
3. Se houver fotos reais de ceviche → manter. Se não → marcar o prato como sem dataset
4. Reconstruir índice: `python /app/backend/rebuild_index.py 10`
5. Validar top-5 por centroide para os pratos afetados
6. Validar lookup de família (patch P0 já aplicado)
7. Só então fazer deploy

---

## 9. PRATOS A ADICIONAR AO INDEX (pastas novas detectadas mas fora do index)

- `uva` (lowercase): 2 fotos — já existe "Uva" no index. Renomear pasta ou ignorar.
- `Tabule de Quinoa`: não existe pasta, não está no index.
- `Maminha ao Molho Mostarda`: não existe pasta — criar após mover fotos (item 7d).
