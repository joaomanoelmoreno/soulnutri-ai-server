# SoulNutri - Food Scanning API: Comprehensive Technical Documentation

> Complete reference for the image-based food identification system.
> Last updated: 2026-03-20

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [API Endpoints Reference](#2-api-endpoints-reference)
3. [Primary Identification Flow: POST /api/ai/identify](#3-primary-identification-flow)
4. [AI Engine Pipeline (Cascading Architecture)](#4-ai-engine-pipeline)
5. [CLIP Local Index System](#5-clip-local-index-system)
6. [Gemini Flash Service](#6-gemini-flash-service)
7. [Generic AI Service (Gemini Vision)](#7-generic-ai-service)
8. [Safety Validation Layer](#8-safety-validation-layer)
9. [Cache System](#9-cache-system)
10. [Nutrition Data Pipeline](#10-nutrition-data-pipeline)
11. [Premium Enrichment Layer](#11-premium-enrichment-layer)
12. [Multi-Item Identification](#12-multi-item-identification)
13. [Supporting Endpoints](#13-supporting-endpoints)
14. [Frontend-to-API Integration](#14-frontend-to-api-integration)
15. [Data Models and Response Schemas](#15-data-models-and-response-schemas)
16. [Configuration and Environment Variables](#16-configuration-and-environment-variables)
17. [Performance Characteristics](#17-performance-characteristics)
18. [Inactive/Available Services (Not in Main Flow)](#18-inactiveavailable-services)

---

## 1. System Overview

SoulNutri is a food recognition web application that identifies dishes from photos. The backend is a **FastAPI** application (`/app/backend/server.py`, ~4450 lines) connected to **MongoDB** via the async Motor driver. The core scanning logic uses a **cascading AI pipeline** with multiple recognition engines and fallback layers.

### Architecture Summary

```
User Camera --> Frontend (React) --> POST /api/ai/identify --> Backend (FastAPI)
                                                                   |
                                          +------------------------+------------------------+
                                          |                        |                        |
                                     Cache Layer            CLIP Local Index          Gemini Flash
                                     (MD5 hash)          (cosine similarity)        (Google API)
                                          |                        |                        |
                                          +------------------------+------------------------+
                                                                   |
                                                          Safety Validator
                                                      (category + allergens)
                                                                   |
                                                       Nutrition Enrichment
                                                    (TACO + MongoDB sheets)
                                                                   |
                                                       Premium Enrichment
                                                  (alerts, combos, myths)
                                                                   |
                                                          JSON Response
```

### Key Design Decisions

- **Restaurant-aware routing**: When GPS detects the user at "Cibi Sana" restaurant, the system uses ONLY the local CLIP index (Gemini is locked) to guarantee zero API cost.
- **Cost optimization**: Local CLIP model handles known dishes at zero cost. Gemini is called only when CLIP confidence is below 90% AND the user is NOT at Cibi Sana.
- **Safety-first**: Every AI result passes through a post-processing safety validator that corrects food category misclassifications using ingredient keyword analysis.
- **Premium tiering**: Basic users get identification + nutrition. Premium users get scientific data, allergen alerts, food combination suggestions, and myth-busting education.

---

## 2. API Endpoints Reference

### Image Identification Endpoints

| Endpoint | Method | Purpose | Cost | Source File:Line |
|----------|--------|---------|------|-----------------|
| `/api/ai/identify` | POST | **Primary** - Cascading identification | CLIP=Free, Gemini=Free tier | `server.py:492` |
| `/api/ai/identify-with-ai` | POST | Direct Gemini Vision (on-demand) | Credits consumed | `server.py:985` |
| `/api/ai/identify-flash` | POST | Direct Gemini Flash | Free tier | `server.py:1664` |
| `/api/ai/identify-multi` | POST | Multi-item plate analysis | Hybrid | `server.py:2339` |

### Index Management Endpoints

| Endpoint | Method | Purpose | Source File:Line |
|----------|--------|---------|-----------------|
| `/api/ai/status` | GET | Index readiness and stats | `server.py:221` |
| `/api/ai/reindex` | POST | Rebuild embeddings index (blocking) | `server.py:335` |
| `/api/ai/reindex-background` | POST | Rebuild index in background | `server.py:357` |
| `/api/ai/reindex-status` | GET | Check background rebuild progress | `server.py:382` |
| `/api/ai/add-to-index` | POST | Add new dish photo to dataset | `server.py:426` |
| `/api/ai/clear-cache` | POST | Clear identification cache | `server.py:313` |

### Utility Endpoints

| Endpoint | Method | Purpose | Source File:Line |
|----------|--------|---------|-----------------|
| `/api/ai/flash-status` | GET | Gemini Flash availability | `server.py:1735` |
| `/api/ai/google-quota-status` | GET | Google API quota check | `server.py:1742` |
| `/api/nutrition/{dish_name}` | GET | Nutrition sheet lookup | `server.py:303` |
| `/api/nutrition/list` | GET | List all nutrition sheets | `server.py:294` |
| `/health` | GET | Kubernetes health check | `server.py:104` |
| `/api/health` | GET | Server health check | `server.py:216` |

---

## 3. Primary Identification Flow

**Endpoint**: `POST /api/ai/identify`
**File**: `server.py:492-982`

### Request

```
Content-Type: multipart/form-data

Parameters:
  file:       UploadFile (required) - JPEG/PNG image of the food
  pin:        string (optional)     - User PIN for Premium features
  nome:       string (optional)     - User name for Premium features
  country:    string (optional)     - "BR" (default) or "OTHER"
  restaurant: string (optional)     - "cibi_sana" or null
```

### Processing Steps (in order)

```
Step 1: Read image bytes
    |
Step 2: Cache lookup (MD5 hash of raw bytes)
    |-- HIT --> Return cached result immediately
    |-- MISS --> Continue
    |
Step 3: CLIP Local Index search (cosine similarity, top-5)
    |
Step 4: Policy analysis (score thresholds + gap analysis)
    |-- Score >= 90% --> ACCEPT as final result
    |-- Cibi Sana restaurant --> USE CLIP ONLY (Gemini locked)
    |-- Score < 90% (non-Cibi Sana) --> Continue to Step 5
    |
Step 5: Gemini Flash identification (Level 2)
    |-- Google API (200-500ms) preferred
    |-- Emergent Key (3-8s) as fallback
    |-- Both fail --> Fall back to CLIP result
    |
Step 6: Confidence level assignment
    |-- >= 90% --> "alta" (high) - "Identificado: [name]"
    |-- 50-89% --> "media" - "Parece ser: [name]" + max 2 alternatives
    |-- < 50%  --> "baixa" (low) - "Nao foi possivel identificar"
    |
Step 7: Admin name synchronization (MongoDB dishes collection)
    |
Step 8: Premium user check (PIN + nome --> db.users lookup)
    |
Step 9: Scientific data enrichment (MongoDB or local templates)
    |
Step 10: Premium alerts generation
    |-- Allergen alerts (profile-based)
    |-- Consumption history alerts (weekly)
    |-- Food combination suggestions
    |-- Healthy substitutions
    |-- Myth or Truth education
    |
Step 11: Nutrition enrichment
    |-- lookup_nutrition_sheet() from MongoDB nutrition_sheets
    |-- Fallback to policy.py generic nutrition by dish type
    |
Step 12: Build final response
    |
Step 13: Cache write (1h TTL, only if identified=true)
    |
Step 14: Metrics logging (if ENABLE_PROCESSING_METRICS setting is on)
    |
Step 15: Return JSON response
```

### Response

```json
{
    "ok": true,
    "identified": true,
    "dish": "frango_grelhado",
    "dish_display": "Frango Grelhado",
    "confidence": "alta",
    "confidence_level": "Alta confianca - Identificacao precisa",
    "aviso_confianca": null,
    "score": 0.92,
    "message": "Identificado: Frango Grelhado",
    "category": "proteina animal",
    "category_emoji": "...",
    "nutrition": {
        "calorias": "165 kcal",
        "proteinas": "31.0g",
        "carboidratos": "0.0g",
        "gorduras": "3.6g",
        "fibras": "0.0g",
        "sodio": "74mg",
        "calorias_kcal": 165.0,
        "proteinas_g": 31.0,
        "carboidratos_g": 0.0,
        "gorduras_g": 3.6,
        "fonte": "Ficha Nutricional Cibi Sana"
    },
    "descricao": "Frango preparado de forma saudavel.",
    "ingredientes": ["frango", "sal", "temperos"],
    "tecnica": "Grelhado ou assado",
    "beneficios": ["Proteina magra de alta qualidade", "Rico em vitaminas B"],
    "riscos": ["Verificar procedencia"],
    "alternatives": [],
    "search_time_ms": 342.5,
    "source": "local_index",
    "alergenos": {},
    "alertas_personalizados": [],
    "beneficio_principal": "Rico em proteina...",
    "curiosidade_cientifica": "Estudo de Harvard...",
    "referencia_pesquisa": "Journal of Nutrition, 2024",
    "alerta_saude": null,
    "mito_verdade": { "pergunta": "...", "resposta": "...", "fonte": "..." },
    "premium": {
        "alertas_alergenos": [],
        "alertas_historico": [],
        "combinacoes_sugeridas": [],
        "substituicoes": [],
        "novidade": null,
        "is_premium": true
    },
    "is_premium": true,
    "tempo_ia_ms": 340.0,
    "ia_disponivel": false,
    "family_name": null,
    "family_candidates": [],
    "family_candidates_detail": []
}
```

---

## 4. AI Engine Pipeline (Cascading Architecture)

The identification uses a **2-level cascade**:

### Level 1: CLIP Local Index (Zero Cost)

```
Image bytes
    --> OpenCLIP ViT-B-32 (CPU) generates 512-dim embedding
    --> Cosine similarity against pre-computed dish embeddings
    --> Top-5 results ranked by score
    --> policy.analyze_result() applies decision logic
```

**Decision Logic** (`ai/policy.py:1105-1233`):
1. **Gap analysis**: If `top1_score - top2_score < 0.02`, CLIP is confused --> reject (identified=false)
2. **Score >= 0.85** --> `alta` confidence, dish identified
3. **Score 0.50-0.84** --> `media` confidence, identified with up to 3 alternatives
4. **Score < 0.50** --> `baixa` confidence, not identified

### Level 2: Gemini Flash (Free Tier / Low Cost)

Triggered ONLY when:
- CLIP score < 90% AND
- Restaurant is NOT "cibi_sana"

**Priority order**:
1. **Google API direct** (`GOOGLE_API_KEY`): gemini-2.0-flash-lite, ~200-500ms, 1500 req/day free
2. **Emergent LLM Key** (`EMERGENT_LLM_KEY`): Same model via proxy, ~3-8s, backup

### Routing Logic Summary

```
if CLIP >= 90%:
    return CLIP result                      # Fast, free

elif restaurant == "cibi_sana":
    return CLIP result (even if low)        # Gemini LOCKED for cost

elif Gemini available:
    result = call_gemini_flash()
    if result.ok:
        return Gemini result                # Better accuracy
    else:
        return CLIP result (fallback)       # Graceful degradation

else:
    return CLIP result                      # No AI available
```

---

## 5. CLIP Local Index System

### Components

| File | Purpose |
|------|---------|
| `ai/embedder.py` (317 lines) | Generates 512-dim image embeddings using OpenCLIP ViT-B-32 |
| `ai/index.py` (314 lines) | Manages the dish index: build, load, search |
| `ai/policy.py` (1239 lines) | Interprets search results into confidence decisions |

### Embedder (`ai/embedder.py`)

- **Model**: OpenCLIP ViT-B-32 (pretrained on OpenAI CLIP weights)
- **Device**: Forced CPU (CUDA explicitly disabled via environment variables)
- **Threads**: `torch.set_num_threads(8)`
- **Output**: 512-dimensional L2-normalized float32 embedding
- **HuggingFace API**: Disabled (`_USE_HF_API = False`) to save credits
- **Fallback chain**: Local model --> (disabled) HF API --> Gemini name-based lookup --> None

When the local model cannot load (e.g., deploy without GPU libs), the system still works for **searches** using the pre-computed index. Only creation of **new** embeddings becomes unavailable.

### Index (`ai/index.py` - `DishIndex` class)

- **Data directory**: `/app/datasets/organized/` (one subfolder per dish, containing JPEG images)
- **Index file**: `/app/datasets/dish_index.json` (dish names, metadata, dish-to-index mapping)
- **Embeddings file**: `/app/datasets/dish_index_embeddings.npy` (numpy array of all embeddings)
- **Max images per dish**: 10 (configurable via `max_per_dish`)
- **Search algorithm**: `np.dot(embeddings, query_embedding)` (cosine similarity since embeddings are L2-normalized)
- **Aggregation**: For each dish, takes the best score across all its images
- **Returns**: Top-K results sorted by score

### Policy (`ai/policy.py`)

Contains:
- `DISH_NAMES`: Mapping of slug --> display name (reflects admin renames)
- `DISH_INFO`: Per-dish metadata (category, ingredients, nutrition, benefits, risks, allergens)
- `DISH_NUTRITION`: Generic nutrition by food type (carboidrato, proteina, vegetal, etc.)
- `PRATOS_COM_GLUTEN`: Set of dishes containing gluten
- `analyze_result()`: Core decision function (score thresholds + gap analysis)
- `get_dish_info()`, `get_dish_name()`, `get_category()`: Lookup helpers

### Building the Index

**Endpoint**: `POST /api/ai/reindex`

```
1. Scan /app/datasets/organized/ for dish subfolders
2. For each dish folder:
   a. Find JPEG/PNG/WebP images (max 10 per dish)
   b. For each image: generate 512-dim embedding via OpenCLIP
   c. Store embedding + dish name mapping
3. Save dish_index.json + dish_index_embeddings.npy
4. Return stats (total dishes, total images, elapsed time)
```

**Background variant**: `POST /api/ai/reindex-background` spawns a subprocess and writes progress to `/tmp/rebuild_index.log`.

### Adding New Dishes

**Endpoint**: `POST /api/ai/add-to-index`

```
Parameters:
  file:         UploadFile (required) - Image of the dish
  dish_name:    string (required)     - "Frango Grelhado"
  weight_grams: int (optional)        - Weight in grams

Process:
  1. Normalize dish name to slug (lowercase, underscores)
  2. Create /app/datasets/organized/{slug}/ if needed
  3. Save image with timestamp + hash suffix
  4. Return success (NOTE: user must call /api/ai/reindex to update the index)
```

---

## 6. Gemini Flash Service

**File**: `services/gemini_flash_service.py` (351 lines)

### Overview

- **Model**: `gemini-2.0-flash-lite`
- **Performance**: Google API ~200-500ms, Emergent fallback ~3-8s
- **Cost**: Google API has 1,500 free requests/day; ~$0.075/1M tokens input
- **Image preprocessing**: Resize to max 384px, JPEG quality 65%

### Function: `identify_dish_gemini_flash(image_bytes, user_profile, restaurant)`

**Process**:
1. **Image optimization**: Open with PIL, resize to 384px max, convert to RGB, JPEG at quality 65
2. **Build prompt**: System prompt instructs the model to return compact JSON with name, category (v/veg/p), calories, macros, allergens, confidence score
3. **Call Google API** (preferred):
   - `genai.Client(api_key=GOOGLE_API_KEY)`
   - `client.models.generate_content(model='gemini-2.0-flash-lite', contents=[prompt, image])`
   - On 429/quota error: fall through to Emergent
4. **Call Emergent LLM** (fallback):
   - Uses `emergentintegrations` library
   - `LlmChat(...).with_model("gemini", "gemini-2.0-flash-lite")`
   - Saves image to temp file, sends as `FileContentWithMimeType`
5. **Parse JSON response**: Strip markdown code fences, parse JSON
6. **Expand compact format**: `{cat: "p"}` --> `{categoria: "proteina animal"}`
7. **Convert allergen list to dict**: `["gluten", "lactose"]` --> `{gluten: true, lactose: true, ...}`
8. **Add confidence/category emojis**
9. **Generate personalized alerts** (if Premium user profile provided):
   - Cross-reference detected allergens with user's `restricoes` list

### System Prompt (Compact)

The prompt asks Gemini to return minimal JSON to reduce token cost:
```json
{"nome":"Name","cat":"v|veg|p","kcal":XXX,"prot":XX,"carb":XX,"gord":XX,"alerg":["gluten"],"score":0.9}
```

Values are per ~150g serving portion.

### Personalized Alerts (`gerar_alertas_personalizados`)

Simple rule-based function (line 338-350):
- Iterates user's `restricoes` list (e.g., ["gluten", "lactose"])
- Checks if any match the detected `alergenos` dict
- Returns list of warning strings

---

## 7. Generic AI Service (Gemini Vision)

**File**: `services/generic_ai.py` (706 lines)

This is a more detailed identification service used for on-demand identification, enriching dish information, fixing/correcting dish data, and batch corrections.

### Functions

| Function | Model | Purpose |
|----------|-------|---------|
| `identify_unknown_dish(image_bytes)` | gemini-2.0-flash-lite | Full identification with ingredients, benefits, risks, scientific facts |
| `identify_multiple_items(image_bytes)` | gemini-2.0-flash | Multi-item plate analysis |
| `enrich_dish_info(dish_name, ingredients)` | gpt-4o-mini | Add scientific data to existing dish |
| `search_ingredient_news(ingredient)` | gpt-4o-mini | Research recent studies about an ingredient |
| `fix_dish_data_with_ai(image_bytes, current_info)` | gemini-2.0-flash | Correct/complete dish data from image |
| `regenerate_dish_info_from_name(dish_name)` | gemini-2.0-flash | Generate full dish profile from name only |
| `batch_fix_dishes(slugs)` | gemini-2.0-flash | Fix multiple dishes in parallel batches |

### Image Optimization

`identify_unknown_dish()` resizes to max 512px, JPEG quality 60 (vs 384px/65 in flash service).

### Safety Integration

After JSON parsing, calls `safety_validator.validar_resultado_ia(result)` to correct category misclassifications before returning.

### Prompt Design (`SYSTEM_PROMPT_IDENTIFY`)

The system prompt includes:
- Brazilian buffet context (common dishes listed)
- Strict category rules (vegano vs vegetariano vs proteina animal)
- Vegan ingredient disambiguation (leite de coco = vegano, NOT animal)
- Required JSON output schema: nome, categoria, confianca, score, ingredientes_provaveis, beneficio_principal, curiosidade_cientifica, riscos, descricao

### Multi-Item Prompt (`SYSTEM_PROMPT_MULTI_ITEM`)

Returns:
```json
{
    "total_itens": 3,
    "itens": [
        {"nome": "Arroz", "categoria": "vegano", "ingredientes": ["arroz"], "calorias": "~150kcal"},
        {"nome": "Feijao", "categoria": "vegano", "ingredientes": ["feijao"], "calorias": "~100kcal"}
    ],
    "calorias_totais": "~500kcal",
    "alertas": ["Alergeno: X"]
}
```

### Enrichment Prompt (`SYSTEM_PROMPT_ENRICH`)

Used via `enrich_dish_info()` to add scientific data to existing dishes. Anti-fake-news rules:
- Only cite OMS, ANVISA, FDA, EFSA, PubMed, peer-reviewed journals
- Never cite blogs, social media, sensationalist sites
- Always include year and institution name
- Clearly state if evidence is consensus vs preliminary

---

## 8. Safety Validation Layer

**File**: `services/safety_validator.py` (519 lines)

### Purpose

Post-processes EVERY AI result to ensure food categories are correct. This is critical for users with dietary restrictions (vegans, vegetarians, allergy sufferers).

### Ingredient Databases

| Database | Count | Purpose |
|----------|-------|---------|
| `PROTEINA_ANIMAL` | ~110 terms | Meats, fish, shellfish, processed meats, offal |
| `DERIVADOS_ANIMAIS` | ~60 terms | Eggs, dairy, honey, mayonnaise |
| `VERSOES_VEGANAS` | ~35 terms | Vegan cheese, plant milks, vegan mayo |
| `IGNORAR_CONTEXTO` | ~15 terms | Decoration, garnish, serving suggestions |
| `ALERGENOS` | 9 categories | Gluten, lactose, egg, crustaceans, fish, peanut, nuts, soy, sesame |

### Validation Rules

```
Rule 1: If PROTEINA_ANIMAL detected in name/ingredients/description
        --> Force category = "proteina animal"
        (Even if AI said "vegano" or "vegetariano")

Rule 2: If DERIVADOS_ANIMAIS detected (and NOT a vegan version)
        --> Force category = "vegetariano"
        (Even if AI said "vegano")

Rule 3: If nothing animal detected
        --> Keep AI's original classification

Special: Vegan versions checked BEFORE applying Rule 2
         "queijo vegano", "leite de coco" etc. are NOT flagged
Special: Decoration context ignored
         "decorado com queijo" does NOT change category
```

### Core Function: `validar_resultado_ia(resultado)`

1. Extract: nome, categoria, ingredientes, descricao from result
2. Call `gerar_alertas_seguranca()` which runs:
   - `validar_categoria()` - detects animal proteins, dairy, vegan alternatives
   - `detectar_alergenos()` - scans for 9 allergen categories
3. If category was corrected: update `categoria`, `category`, `category_emoji`
4. Append allergen alerts to `riscos` list
5. Add `_seguranca` metadata block with validation details

### Text Analysis Details

- `normalizar_texto()`: lowercase, strip accents (a/e/i/o/u/c)
- Regex word boundaries prevent false positives (e.g., "decoracao" != "coracao")
- Multi-word ingredients: substring matching
- Single-word ingredients: word boundary regex matching
- `verificar_versao_vegana()`: checks patterns like "{ingrediente} vegano/vegana/de coco/de soja/de castanha/plant-based"
- `esta_em_contexto_ignorado()`: checks patterns like "decoracao de {ingrediente}" or "{ingrediente} para decorar"

---

## 9. Cache System

**File**: `services/cache_service.py` (118 lines)

### Architecture

- **Type**: In-memory LRU (Least Recently Used) cache
- **Implementation**: Python `OrderedDict`
- **Max size**: 500 entries
- **TTL**: 1 hour (3600 seconds) per entry
- **Key**: MD5 hash of raw image bytes
- **Scope**: Only successful identifications (`ok=True AND identified=True`)

### Functions

| Function | Purpose |
|----------|---------|
| `get_image_hash(image_bytes)` | MD5 hex digest of raw bytes |
| `get_cached_result(image_bytes)` | Lookup by image hash, returns result or None |
| `cache_result(image_bytes, result, ttl)` | Store result (skips errors/unidentified) |
| `get_cache_stats()` | Returns size, hits, misses, hit_rate |
| `clear_cache()` | Flush all entries + reset counters |

### Cache Behavior

- On **cache hit**: Returns result with `source` appended with `_cached` and `from_cache: true`
- On **set**: Removes expired entries first, then evicts oldest if at capacity
- On **server restart**: Cache is lost (in-memory only)
- **Clearing**: `POST /api/ai/clear-cache` flushes all entries (useful after correcting a dish in admin)

### Limitations

- Same dish photographed from different angles = different hash = cache miss
- Resized/recompressed image of same photo = different hash = cache miss
- Not shared across server instances (single-process only)
- Not persisted to disk

---

## 10. Nutrition Data Pipeline

### Primary Source: MongoDB `nutrition_sheets` Collection

**Function**: `lookup_nutrition_sheet(dish_display)` (`server.py:247-291`)

Search order (stops at first match):
1. Exact match on `nome` field
2. Match on `slug` field
3. Match in `nomes_alternativos` array
4. Case-insensitive regex on `nome`

Returns precise numeric values:
```json
{
    "calorias_kcal": 165.0,
    "proteinas_g": 31.0,
    "carboidratos_g": 0.0,
    "gorduras_g": 3.6,
    "fibras_g": 0.0,
    "sodio_mg": 74.0,
    "calcio_mg": 12.0,
    "ferro_mg": 0.9,
    "potassio_mg": 256.0,
    "zinco_mg": 1.0,
    "fonte": "Ficha Nutricional Cibi Sana"
}
```

### Fallback Source: policy.py `DISH_NUTRITION`

If MongoDB has no sheet, uses generic nutrition by food type:
- `carboidrato` (rice, pasta), `proteina` (chicken, fish), `vegetal` (salad), `sobremesa` (dessert), etc.

### External Source: `nutrition_3sources.py` (248 lines)

Pipeline for creating nutrition sheets from 3 sources:
1. **TACO** (local) - Brazilian food composition table, ingredient-based decomposition
2. **USDA FNDDS** (Survey) - US Department of Agriculture, dish-name search in English
3. **Open Food Facts** - Global database, category search

Method: Average across sources that return data, with outlier exclusion.

### TACO Integration (`/api/admin/revisar-prato-taco`)

Zero-cost endpoint that calculates nutrition from the local TACO database:
- Takes dish name + ingredients list
- Looks up each ingredient in the TACO table
- Calculates weighted nutrition per 100g
- Detects category based on ingredient keywords

---

## 11. Premium Enrichment Layer

Premium users are identified by `pin` + `nome` matching a record in `db.users`.

### Authentication Flow (within /api/ai/identify)

```python
# server.py:738-748
pin_hash = hash_pin(pin)          # SHA-256 of the PIN
user_profile = await db.users.find_one(
    {"pin_hash": pin_hash, "nome": {"$regex": f"^{nome}$", "$options": "i"}},
    {"_id": 0}
)
is_premium = user_profile is not None
```

### Scientific Data (`server.py:750-786`)

Sources (in priority order):
1. **MongoDB `dishes` collection**: Pre-stored scientific data per dish slug
2. **Local templates** (`services/local_dish_updater.py`, 987 lines): Hardcoded dish database with ingredients, nutrition, benefits, risks, allergens, glycemic index, digestion time, food combinations, etc.

Fields provided: `beneficio_principal`, `curiosidade_cientifica`, `referencia_pesquisa`, `alerta_saude`, `voce_sabia`, `dica_chef`

### Real-Time Alerts (`server.py:791-842`)

From `services/alerts_service.py` (327 lines):

| Alert Type | Function | Description |
|------------|----------|-------------|
| Allergen alerts | `verificar_alergenos_perfil()` | Cross-references dish ingredients with user's registered allergies |
| History alerts | `gerar_alertas_tempo_real()` | Analyzes weekly consumption from MongoDB to detect repetition |
| Combinations | `gerar_combinacoes_sugeridas()` | Suggests beneficial food pairings |
| Substitutions | `gerar_substituicoes()` | Recommends healthier alternatives |
| News/novelties | MongoDB `novidades` collection | Active news items linked to specific dishes |

### Myth or Truth (`server.py:846-864`)

From `services/mitos_verdades.py`:
- Returns a "Myth or Truth" nutritional education card based on dish ingredients and category
- Example: "Myth: Eating eggs raises cholesterol. Truth: Studies show..."

---

## 12. Multi-Item Identification

**Endpoint**: `POST /api/ai/identify-multi`
**File**: `server.py:2339-2406`

### Strategy (Hybrid V5)

Uses `services/hybrid_identify_v5.py`:

1. **Zoom central (50%)**: Crops the center of the image to identify the main item using local CLIP index
2. **Region analysis**: Divides the image into regions to find side dishes by similarity matching against buffet dishes
3. **Gemini fallback**: For unrecognized items

### Response Format

```json
{
    "ok": true,
    "principal": {
        "nome": "Frango Grelhado",
        "categoria": "proteina animal",
        "score": 0.85,
        "source": "local"
    },
    "acompanhamentos": [
        {"nome": "Arroz", "categoria": "vegano", "score": 0.78, "source": "local"},
        {"nome": "Feijao", "categoria": "vegano", "score": 0.72, "source": "local"}
    ],
    "itens": [
        {"nome": "Frango Grelhado", "categoria": "proteina animal", "score": 0.85, "source": "local"},
        {"nome": "Arroz", "categoria": "vegano", "score": 0.78, "source": "local"},
        {"nome": "Feijao", "categoria": "vegano", "score": 0.72, "source": "local"}
    ],
    "itens_do_buffet": 3,
    "search_time_ms": 890.5
}
```

The `itens` array is a flattened version (principal + acompanhamentos) formatted for frontend compatibility.

---

## 13. Supporting Endpoints

### POST /api/ai/identify-with-ai (`server.py:985-1066`)

Direct Gemini Vision identification. **Consumes credits** (explicitly user-requested only).

**Important implementation detail**: This endpoint reads and `exec()`s the file `/app/backend/services/generic_ai.py.BACKUP_COM_IA` at runtime to create a temporary module. This avoids using the standard generic_ai.py (which may have been modified for cost savings).

```
Request:  file (image), pin (string), nome (string)
Response: {ok, identified, dish_display, category, confidence, score,
           ingredientes, beneficios, descricao, source: "gemini_ai",
           creditos_usados: true}
```

### POST /api/ai/identify-flash (`server.py:1664-1732`)

Direct Gemini Flash call. Supports Premium user profiles for personalized allergen alerts.

```
Request:  file (image), pin (optional), nome (optional)
Response: Full Gemini Flash result with nutrition, allergens, confidence,
          total_time_ms
```

### GET /api/ai/google-quota-status (`server.py:1742`)

Tests the Google API with a minimal text request ("Diga apenas: OK") to check if the free quota has been exhausted (429 error). Returns recommendation on whether to use Google API or Emergent fallback.

```json
// Quota available:
{"ok": true, "google_api_available": true, "response_time_ms": 250, "model": "gemini-2.0-flash-lite"}

// Quota exhausted:
{"ok": true, "google_api_available": false, "error": "RESOURCE_EXHAUSTED",
 "recommendation": "Aguarde renovacao (~24h) ou use Emergent Key como fallback"}
```

### POST /api/ai/clear-cache (`server.py:313-332`)

Clears the in-memory identification cache. Returns count of items cleared.

```json
{"ok": true, "message": "Cache limpo com sucesso", "items_cleared": 42}
```

---

## 14. Frontend-to-API Integration

**File**: `frontend/src/App.js` (3464 lines)

### Camera Initialization (`startCamera`, line 730)

```javascript
// Fallback chain for camera access:
1. getUserMedia({ video: { facingMode: "environment" } })   // rear camera
2. getUserMedia({ video: true })                             // any camera
3. getUserMedia({ video: {} })                               // basic
```

Handles `NotAllowedError` (permission denied) and generic camera errors. Pauses camera when app goes to background, resumes on foreground.

### Image Capture (`handleCameraTouch`, line 836)

```javascript
// On screen tap:
1. Debounce check (1 second minimum between captures)
2. Check video is ready (videoWidth > 0)
3. Draw video frame to canvas (max 800px, preserving aspect ratio)
4. canvas.toBlob(blob => identifyImage(blob), 'image/jpeg', 0.7)
5. Clear canvas after blob creation
```

### API Call (`identifyImage`, line 877)

```javascript
const fd = new FormData();
fd.append("file", blob, "photo.jpg");
fd.append("country", userLocation?.country || 'BR');

// GPS geofencing: Cibi Sana detection
if (atCibiSanaRef.current) {
    fd.append("restaurant", "cibi_sana");   // Forces CLIP-only mode on backend
}

// Premium credentials from localStorage
const pin = localStorage.getItem('soulnutri_pin');
const nome = localStorage.getItem('soulnutri_nome');
if (pin && nome && !multiMode) {
    fd.append("pin", pin);
    fd.append("nome", nome);
}

// Endpoint selection
const endpoint = multiMode
    ? `${API}/ai/identify-multi`
    : `${API}/ai/identify`;

const res = await fetch(endpoint, {
    method: "POST",
    body: fd,
    signal: abortController.signal   // Timeout via AbortController
});
```

### Post-Identification (line 951-981)

On successful single-item identification:
1. Set result state with timing: `{ ...data, totalTime: Date.now() - t }`
2. Save photo to local gallery if identified
3. Fetch "Radar de Noticias" (`GET /radar/alimentos/{dish}?ingredientes=...`) for additional science facts
4. Display result overlay

### Scanner Modes

- **Photo mode** (default, active): Tap screen to capture one frame
- **Continuous scanner** (line 274): State exists but **disabled** (`scannerMode = false`)
- **Multi-mode**: Toggle to identify all items on a plate separately (`/api/ai/identify-multi`)

### Image Sizes Through the Pipeline

```
Camera capture:     device native resolution (variable)
Frontend canvas:    max 800px, JPEG quality 0.7
--> sent to API as multipart/form-data
Gemini Flash:       resized to max 384px, JPEG quality 0.65
Generic AI:         resized to max 512px, JPEG quality 0.60
CLIP embedding:     model's native preprocessing (224x224 via OpenCLIP transforms)
```

---

## 15. Data Models and Response Schemas

### IdentifyResponse (Pydantic model, `server.py:163-189`)

```python
class IdentifyResponse(BaseModel):
    ok: bool
    identified: bool
    dish: Optional[str]                  # slug: "frango_grelhado"
    dish_display: Optional[str]          # display: "Frango Grelhado"
    confidence: str                      # "alta" | "media" | "baixa"
    confidence_level: Optional[str]      # descriptive message
    aviso_confianca: Optional[str]       # confidence warning
    score: float                         # 0.0 - 1.0
    message: str                         # user-facing message
    category: Optional[str]              # "vegano" | "vegetariano" | "proteina animal"
    category_emoji: Optional[str]
    nutrition: Optional[NutritionInfo]
    descricao: Optional[str]
    ingredientes: Optional[List[str]]
    tecnica: Optional[str]
    beneficios: Optional[List[str]]
    riscos: Optional[List[str]]
    aviso_cibi_sana: Optional[str]
    alternatives: List[str]              # max 2 for "media", 0 for alta/baixa
    search_time_ms: Optional[float]
    source: Optional[str]                # "local_index" | "gemini_flash" | "gemini_ai"
    beneficio_principal: Optional[str]   # Premium only
    curiosidade_cientifica: Optional[str] # Premium only
    referencia_pesquisa: Optional[str]   # Premium only
    alerta_saude: Optional[str]          # Premium only
```

### NutritionInfo (Pydantic model, `server.py:143-161`)

```python
class NutritionInfo(BaseModel):
    # String format (display)
    calorias: Optional[str]              # "165 kcal"
    proteinas: Optional[str]             # "31.0g"
    carboidratos: Optional[str]          # "0.0g"
    gorduras: Optional[str]              # "3.6g"
    fibras: Optional[str]               # "0.0g"
    sodio: Optional[str]                # "74mg"
    # Numeric format (precise, from nutrition_sheets)
    calorias_kcal: Optional[float]
    proteinas_g: Optional[float]
    carboidratos_g: Optional[float]
    gorduras_g: Optional[float]
    fibras_g: Optional[float]
    sodio_mg: Optional[float]
    calcio_mg: Optional[float]
    ferro_mg: Optional[float]
    potassio_mg: Optional[float]
    zinco_mg: Optional[float]
    fonte: Optional[str]                # data source name
```

### Confidence Level System

| Score Range | Confidence | User Message | Alternatives | Warning |
|-------------|-----------|--------------|--------------|---------|
| >= 0.90 | `alta` | "Identificado: {name}" | 0 | None |
| 0.50-0.89 | `media` | "Parece ser: {name}" | Up to 2 | "Verifique se o prato esta correto" |
| < 0.50 | `baixa` | "Nao foi possivel identificar" | 0 | "Tente outra foto ou consulte o atendente" |

### Category System

| Category | Meaning | Emoji |
|----------|---------|-------|
| `vegano` | Zero animal products | (plant) |
| `vegetariano` | Has egg/dairy/honey, no meat/fish | (vegetable) |
| `proteina animal` | Contains meat/fish/poultry | (meat) |

---

## 16. Configuration and Environment Variables

### Required

| Variable | Purpose | Used By |
|----------|---------|---------|
| `MONGO_URL` | MongoDB connection string | `server.py:87` |
| `DB_NAME` | Database name (default: `soulnutri`) | `server.py:92` |

### AI Service Keys (at least one needed for Gemini)

| Variable | Purpose | Used By |
|----------|---------|---------|
| `GOOGLE_API_KEY` | Google Gemini API (fast, preferred) | `gemini_flash_service.py:167` |
| `EMERGENT_LLM_KEY` | Emergent Integrations API (fallback) | `generic_ai.py:123`, `gemini_flash_service.py:199` |

### Optional

| Variable | Purpose | Default |
|----------|---------|---------|
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `*` |
| `USDA_API_KEY` | USDA nutrition API | `DEMO_KEY` |
| `USE_LOCAL_MODEL` | Force local CLIP model | `false` |
| `CUDA_VISIBLE_DEVICES` | GPU (forced empty) | `""` |
| `FORCE_CPU` | Force CPU mode | `1` |

### Feature Flags (MongoDB `settings` collection)

| Key | Purpose |
|-----|---------|
| `ENABLE_PROCESSING_METRICS` | Log processing time/engine to `processing_metrics` collection |

---

## 17. Performance Characteristics

### Response Times (Approximate)

| Scenario | Time | Engine |
|----------|------|--------|
| Cache hit | ~1-5ms | Cache |
| CLIP high confidence (>= 90%) | ~100-300ms | Local CPU |
| CLIP + Gemini Google API | ~400-800ms | Local + Google |
| CLIP + Gemini Emergent fallback | ~3-8s | Local + Emergent |
| Direct Gemini Flash | ~200-500ms | Google API |

### Cost Per Request

| Engine | Cost |
|--------|------|
| Cache hit | $0 |
| CLIP local | $0 |
| Gemini Flash (Google API) | ~$0.000075/request (within 1,500/day free tier) |
| Gemini Flash (Emergent) | Credits consumed |
| Generic AI (on-demand) | Credits consumed |

### Resource Usage

- **CPU**: OpenCLIP model uses 8 threads on CPU; no GPU required
- **Memory**: CLIP model + 500-entry cache + embedding index in RAM
- **Storage**: `dish_index.json` + `dish_index_embeddings.npy` on disk
- **Network**: Gemini calls require internet; CLIP is fully offline

---

## 18. Inactive/Available Services (Not in Main Flow)

These services are coded and importable but are NOT wired into the main `/api/ai/identify` cascade:

| Service | File | Model/API | Accuracy | Free Tier | Status |
|---------|------|-----------|----------|-----------|--------|
| Clarifai | `clarifai_service.py` | food-item-recognition (547+ foods) | Good | 1K/month | Unused |
| FatSecret | `fatsecret_service.py` | RapidAPI image-recognition/v2 | Good | 150K/month | Unused |
| YOLO | `yolo_service.py` | Custom YOLOv8 (`best.pt`) | ~50-100ms | Unlimited (local) | Unused |
| HuggingFace | `huggingface_service.py` | nateraw/food (Food-101) | 89% | Unlimited | API disabled |
| LogMeal | `logmeal_service.py` | LogMeal v2 | 93-98% | Limited | Unused |
| Google Vision | `google_vision_service.py` | Label detection | Generic | 1K/month | Unused |

---

## Appendix A: MongoDB Collections Used

| Collection | Purpose |
|------------|---------|
| `dishes` | Admin-managed dish data (name, category, ingredients, scientific data) |
| `nutrition_sheets` | Precise nutritional data per dish (from TACO/USDA/OFF pipeline) |
| `users` | Premium user profiles (pin_hash, nome, allergies, restrictions, caloric goals) |
| `novidades` | News/novelties linked to specific dishes |
| `processing_metrics` | Performance logging (timestamp, time_ms, dish, score, engine) |
| `settings` | Feature flags (e.g., ENABLE_PROCESSING_METRICS) |

## Appendix B: Complete File Map

```
backend/
  server.py                          # FastAPI app, all endpoints (4450 lines)
  ai/
    embedder.py                      # OpenCLIP ViT-B-32 embedding generation (317 lines)
    index.py                         # DishIndex: build, load, search (314 lines)
    policy.py                        # Decision logic, dish metadata (1239 lines)
  services/
    gemini_flash_service.py          # Gemini 2.0 Flash identification (351 lines)
    generic_ai.py                    # Gemini Vision + enrichment (706 lines)
    safety_validator.py              # Category correction + allergen detection (519 lines)
    cache_service.py                 # LRU in-memory cache (118 lines)
    alerts_service.py                # Premium real-time alerts (327 lines)
    profile_service.py               # User profile + caloric goals (247 lines)
    local_dish_updater.py            # Hardcoded dish database (987 lines)
    nutrition_3sources.py            # TACO + USDA + OFF pipeline (248 lines)
    nutrition_generator.py           # Nutrition generation utilities
    nutrition_premium_service.py     # Premium nutrition features
    mitos_verdades.py                # Myth or Truth education
    translation_service.py           # Multi-language support
    dish_service.py                  # Dish CRUD operations
    audit_service.py                 # Audit logging
    clarifai_service.py              # (inactive) Clarifai food recognition
    fatsecret_service.py             # (inactive) FatSecret identification
    yolo_service.py                  # (inactive) YOLOv8 local model
    huggingface_service.py           # (inactive) HuggingFace Food-101
    logmeal_service.py               # (inactive) LogMeal API
    google_vision_service.py         # (inactive) Google Vision labels

frontend/
  src/
    App.js                           # Main app: camera, scanner, API calls (3464 lines)
    CheckinRefeicao.jsx              # Meal check-in component
    DashboardPremium.jsx             # Premium dashboard
    Premium.jsx                      # Premium features
    Admin.js                         # Admin panel
    I18nContext.js                    # Internationalization
```
