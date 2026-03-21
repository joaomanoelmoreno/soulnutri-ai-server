# SoulNutri - Food Scanning Core Logic: Mermaid Diagrams

## 1. Complete End-to-End Flow (Frontend to Backend to Response)

```mermaid
flowchart TD
    START["User taps screen<br/>(App.js:836)"] --> DEBOUNCE{"Last tap<br/>< 1 second ago?"}
    DEBOUNCE -->|Yes| IGNORE["Ignored<br/>(debounce)"]
    DEBOUNCE -->|No| CAPTURE["Capture video frame to canvas<br/>max 800px, JPEG quality 0.7<br/>(App.js:844-874)"]
    
    CAPTURE --> FORMDATA["Build FormData:<br/>file=photo.jpg<br/>country=BR or OTHER"]
    
    FORMDATA --> GPS{"GPS says user<br/>at Cibi Sana?<br/>(atCibiSanaRef)"}
    GPS -->|Yes| ADD_REST["Append restaurant=cibi_sana"]
    GPS -->|No| SKIP_REST["No restaurant param"]
    
    ADD_REST --> PREMIUM_CHECK{"localStorage has<br/>pin + nome?"}
    SKIP_REST --> PREMIUM_CHECK
    
    PREMIUM_CHECK -->|Yes, not multiMode| ADD_CREDS["Append pin + nome"]
    PREMIUM_CHECK -->|No| SKIP_CREDS["No credentials"]
    
    ADD_CREDS --> MODE_CHECK{"multiMode<br/>enabled?"}
    SKIP_CREDS --> MODE_CHECK
    
    MODE_CHECK -->|Yes| MULTI_EP["POST /api/ai/identify-multi"]
    MODE_CHECK -->|No| SINGLE_EP["POST /api/ai/identify<br/>(App.js:934)"]
    
    SINGLE_EP --> BACKEND["Backend: identify_image()<br/>(server.py:493)"]
    MULTI_EP --> MULTI_BACKEND["Backend: identify_multiple_items()<br/>(server.py:2340)"]
    
    BACKEND --> CORE_FLOW["Core Identification Flow<br/>(see Diagram 2)"]
    
    CORE_FLOW --> RESPONSE["JSON Response"]
    
    RESPONSE --> FE_RESULT["Frontend receives result<br/>(App.js:949)"]
    FE_RESULT --> SAVE_GALLERY{"identified == true?"}
    SAVE_GALLERY -->|Yes| GALLERY["Save photo to gallery"]
    SAVE_GALLERY -->|No| SHOW_ERROR["Show error/unrecognized"]
    
    GALLERY --> RADAR["Fetch /radar/alimentos/{dish}<br/>for science facts"]
    RADAR --> DISPLAY["Display result overlay<br/>with nutrition + alerts"]
```

## 2. Core Backend Identification Logic (server.py:492-982)

This is the heart of the system - the cascading AI pipeline.

```mermaid
flowchart TD
    ENTRY["POST /api/ai/identify<br/>Params: file, pin, nome,<br/>country, restaurant<br/>(server.py:492)"] --> READ_IMG["Read image bytes<br/>(server.py:519)"]
    
    READ_IMG --> EMPTY{"Image empty?<br/>(server.py:521)"}
    EMPTY -->|Yes| ERR_EMPTY["Return: ok=false<br/>Arquivo de imagem vazio"]
    EMPTY -->|No| CACHE_CHECK

    subgraph CACHE ["STEP 1: Cache Check (server.py:533)"]
        CACHE_CHECK["get_cached_result(content)<br/>Key = MD5 of raw bytes"] --> CACHE_HIT{"Cache hit?"}
        CACHE_HIT -->|Yes| CACHE_RETURN["Return cached result<br/>+ source=xxx_cached<br/>~1-5ms"]
    end
    
    CACHE_HIT -->|No| CLIP_SEARCH

    subgraph CLIP ["STEP 2: CLIP Local Index (server.py:562-593)"]
        CLIP_SEARCH["index.search(content, top_k=5)<br/>Cosine similarity on 512-dim<br/>OpenCLIP ViT-B-32 embeddings<br/>(ai/index.py)"] --> ANALYZE["analyze_result(results)<br/>(ai/policy.py:1105)"]
        
        ANALYZE --> GAP_CHECK{"Top1 - Top2 < 0.02?<br/>(policy.py:1153)"}
        GAP_CHECK -->|"Yes (CLIP confused)"| CLIP_REJECT["identified=false<br/>score=low<br/>Prato nao reconhecido"]
        GAP_CHECK -->|No| SCORE_HIGH{"score >= 0.85?<br/>(policy.py:1173)"}
        
        SCORE_HIGH -->|Yes| CLIP_ALTA["identified=true<br/>confidence=alta<br/>+ nutrition, ingredients,<br/>benefits, risks"]
        SCORE_HIGH -->|No| SCORE_MED{"score >= 0.50?<br/>(policy.py:1193)"}
        
        SCORE_MED -->|Yes| CLIP_MEDIA["identified=true<br/>confidence=media<br/>+ up to 3 alternatives"]
        SCORE_MED -->|No| CLIP_BAIXA["identified=false<br/>confidence=baixa"]
    end
    
    CLIP_ALTA --> SERVER_SCORE{"server.py score >= 0.90?<br/>(server.py:578)"}
    CLIP_MEDIA --> SERVER_SCORE
    CLIP_BAIXA --> SERVER_SCORE
    CLIP_REJECT --> SERVER_SCORE
    
    SERVER_SCORE -->|"Yes (>= 0.90 & identified)"| ACCEPT_CLIP["decision = CLIP result<br/>source = local_index<br/>CLIP confiante - aceito"]
    
    SERVER_SCORE -->|No| IS_CIBI{"restaurant == cibi_sana?<br/>(server.py:584)"}
    
    IS_CIBI -->|Yes| CIBI_RESULT["decision = CLIP result<br/>source = local_index<br/>Gemini LOCKED<br/>Even if low confidence"]
    
    IS_CIBI -->|No| GEMINI_FLOW

    subgraph GEMINI ["STEP 3: Gemini Flash Fallback (server.py:598-659)"]
        GEMINI_FLOW["CLIP uncertain, not Cibi Sana<br/>Calling Gemini..."] --> GEMINI_AVAIL{"is_gemini_flash_available()?<br/>Checks EMERGENT_API_KEY<br/>or GOOGLE_API_KEY"}
        
        GEMINI_AVAIL -->|No| FALLBACK_CLIP{"CLIP index ready?"}
        FALLBACK_CLIP -->|Yes| USE_CLIP_ANYWAY["decision = CLIP result<br/>(even if low confidence)"]
        FALLBACK_CLIP -->|No| ERR_NO_AI["Return: ok=false<br/>Servico de IA indisponivel"]
        
        GEMINI_AVAIL -->|Yes| LOAD_PROFILE["Load user profile<br/>from MongoDB (if pin+nome)"]
        LOAD_PROFILE --> CALL_GEMINI["identify_dish_gemini_flash()<br/>(gemini_flash_service.py:108)"]
        
        CALL_GEMINI --> GEMINI_DETAIL["(see Diagram 3<br/>for Gemini internals)"]
        GEMINI_DETAIL --> GEMINI_OK{"result.ok == true?"}
        
        GEMINI_OK -->|Yes| ACCEPT_GEMINI["decision = Gemini result<br/>source = gemini_flash<br/>score = 0.90 (hardcoded)"]
        GEMINI_OK -->|No| GEMINI_FAIL{"CLIP index ready<br/>& has clip_decision?"}
        GEMINI_FAIL -->|Yes| USE_CLIP_FALLBACK["decision = CLIP result<br/>(graceful degradation)"]
        GEMINI_FAIL -->|No| ERR_BOTH_FAIL["Return: ok=false<br/>Nao foi possivel identificar"]
    end
    
    ACCEPT_CLIP --> CONFIDENCE
    CIBI_RESULT --> CONFIDENCE
    USE_CLIP_ANYWAY --> CONFIDENCE
    ACCEPT_GEMINI --> CONFIDENCE
    USE_CLIP_FALLBACK --> CONFIDENCE

    subgraph POSTPROCESS ["STEP 4: Post-Processing (server.py:661-968)"]
        CONFIDENCE["Apply confidence levels<br/>(server.py:664-687)"]
        CONFIDENCE --> CONF_HIGH{"score >= 0.90?"}
        CONF_HIGH -->|Yes| MSG_HIGH["confidence=alta<br/>Identificado: {name}<br/>0 alternatives"]
        CONF_HIGH -->|No| CONF_MED{"score >= 0.50?"}
        CONF_MED -->|Yes| MSG_MED["confidence=media<br/>Parece ser: {name}<br/>max 2 alternatives"]
        CONF_MED -->|No| MSG_LOW["confidence=baixa<br/>Nao foi possivel identificar<br/>0 alternatives"]
        
        MSG_HIGH --> ADMIN_SYNC
        MSG_MED --> ADMIN_SYNC
        MSG_LOW --> ADMIN_SYNC
        
        ADMIN_SYNC["Admin Name Sync<br/>Check MongoDB dishes<br/>for renamed dishes<br/>(server.py:693-721)"]
        
        ADMIN_SYNC --> IS_PREMIUM{"pin + nome provided<br/>AND user exists in DB?<br/>(server.py:738-745)"}
        
        IS_PREMIUM -->|No| NUTRITION
        IS_PREMIUM -->|Yes| SCIENTIFIC["Load scientific data<br/>1. MongoDB dishes collection<br/>2. Fallback: local_dish_updater.py<br/>(server.py:750-786)"]
        
        SCIENTIFIC --> ALERTS["Generate premium alerts:<br/>- Allergen alerts (profile)<br/>- History alerts (weekly)<br/>- Combination suggestions<br/>- Healthy substitutions<br/>- Novidades/news<br/>(server.py:791-837)"]
        
        ALERTS --> MITO["Myth or Truth card<br/>mitos_verdades.py<br/>(server.py:848-864)"]
        
        MITO --> NUTRITION
        
        NUTRITION["Enrich nutrition:<br/>1. lookup_nutrition_sheet(name)<br/>   from MongoDB nutrition_sheets<br/>2. Fallback: policy.py generic data<br/>(server.py:866-892)"]
        
        NUTRITION --> BUILD["Build response JSON<br/>~40 fields<br/>(server.py:901-946)"]
        
        BUILD --> CACHE_WRITE{"identified == true?<br/>(server.py:951)"}
        CACHE_WRITE -->|Yes| SAVE_CACHE["Cache result<br/>TTL = 1 hour"]
        CACHE_WRITE -->|No| SKIP_CACHE["Skip cache"]
        
        SAVE_CACHE --> METRICS
        SKIP_CACHE --> METRICS
        
        METRICS["Log processing metrics<br/>(if ENABLE_PROCESSING_METRICS)<br/>(server.py:957-967)"]
    end
    
    METRICS --> FINAL["Return JSON response<br/>(server.py:969)"]
```

## 3. Gemini Flash Service Internals (gemini_flash_service.py)

```mermaid
flowchart TD
    ENTRY["identify_dish_gemini_flash()<br/>(gemini_flash_service.py:108)"] --> OPTIMIZE["Image optimization:<br/>PIL open -> resize to 384px max<br/>-> convert RGB -> JPEG quality 65<br/>(lines 132-146)"]
    
    OPTIMIZE --> HAS_GOOGLE{"GOOGLE_API_KEY<br/>set?<br/>(line 167)"}
    
    HAS_GOOGLE -->|Yes| CALL_GOOGLE["Google API direct call:<br/>genai.Client(api_key)<br/>model=gemini-2.0-flash-lite<br/>contents=[prompt, image]<br/>(lines 171-184)"]
    
    CALL_GOOGLE --> GOOGLE_OK{"Success?"}
    GOOGLE_OK -->|Yes| GOT_RESPONSE["response_text = response.text<br/>source = google_api<br/>~200-500ms"]
    
    GOOGLE_OK -->|"No (429/quota/error)"| CHECK_EMERGENT
    HAS_GOOGLE -->|No| CHECK_EMERGENT
    
    CHECK_EMERGENT{"EMERGENT_LLM_KEY<br/>set?<br/>(line 199)"} -->|Yes| CALL_EMERGENT["Emergent LLM call:<br/>Save image to temp file<br/>LlmChat().with_model(gemini)<br/>send_message(image + prompt)<br/>(lines 202-235)"]
    
    CALL_EMERGENT --> EMERGENT_OK{"Success?"}
    EMERGENT_OK -->|Yes| GOT_RESPONSE_E["response_text = response<br/>source = emergent_fallback<br/>~3-8 seconds"]
    EMERGENT_OK -->|No| BOTH_FAIL["Return: ok=false<br/>Todos os servicos<br/>de IA indisponiveis"]
    
    CHECK_EMERGENT -->|No| BOTH_FAIL
    
    GOT_RESPONSE --> PARSE
    GOT_RESPONSE_E --> PARSE
    
    PARSE["Parse JSON response:<br/>Strip markdown fences<br/>json.loads()<br/>(lines 251-271)"] --> PARSE_OK{"Valid JSON?"}
    
    PARSE_OK -->|No| PARSE_ERR["Return: ok=false<br/>Erro ao processar<br/>resposta da IA"]
    
    PARSE_OK -->|Yes| EXPAND["Expand compact format:<br/>cat:p -> proteina animal<br/>cat:v -> vegano<br/>cat:veg -> vegetariano<br/>score hardcoded to 0.90<br/>(lines 277-301)"]
    
    EXPAND --> ALLERGENS["Convert allergen list to dict:<br/>[gluten,lactose] -><br/>{gluten:true, lactose:true,<br/> ovo:false, ...}<br/>(lines 296-299)"]
    
    ALLERGENS --> HAS_PROFILE{"user_profile<br/>provided?<br/>(line 323)"}
    
    HAS_PROFILE -->|Yes| ALERTS["gerar_alertas_personalizados():<br/>Cross-reference user restricoes<br/>with detected alergenos<br/>(lines 338-350)"]
    HAS_PROFILE -->|No| RETURN
    
    ALERTS --> RETURN["Return result:<br/>{ok:true, nome, categoria,<br/>score:0.90, nutricao,<br/>alergenos, alertas,<br/>tempo_processamento_ms}"]
```

## 4. CLIP Policy Decision Logic (ai/policy.py:1105-1233)

```mermaid
flowchart TD
    ENTRY["analyze_result(results)<br/>(policy.py:1105)"] --> HAS_RESULTS{"results empty<br/>or has error?<br/>(line 1110)"}
    
    HAS_RESULTS -->|Yes| NO_RESULT["Return:<br/>identified=false<br/>score=0.0<br/>Nao foi possivel identificar"]
    
    HAS_RESULTS -->|No| EXTRACT["Extract top result:<br/>score = results[0].score<br/>dish = results[0].dish<br/>(lines 1123-1125)"]
    
    EXTRACT --> LOOKUP["Lookup dish metadata:<br/>dish_display = get_dish_name(dish)<br/>category = get_category(dish)<br/>nutrition = get from dish_info<br/>   or fallback to generic type<br/>(lines 1127-1137)"]
    
    LOOKUP --> GAP{"len(results) >= 2<br/>AND<br/>top1 - top2 < 0.02?<br/>(lines 1149-1153)"}
    
    GAP -->|"Yes (CLIP confused)"| REJECT["Return:<br/>identified=false<br/>confidence=baixa<br/>Prato nao reconhecido<br/>com seguranca<br/>alternatives=[]"]
    
    GAP -->|No| HIGH{"score >= 0.85?<br/>(line 1173)"}
    
    HIGH -->|Yes| ACCEPT_HIGH["Return:<br/>identified=true<br/>confidence=alta<br/>Prato identificado<br/>+ full dish info<br/>alternatives=[]"]
    
    HIGH -->|No| MED{"score >= 0.50?<br/>(line 1193)"}
    
    MED -->|Yes| ACCEPT_MED["Return:<br/>identified=true<br/>confidence=media<br/>Provavel identificacao<br/>+ full dish info<br/>alternatives=[results 2-4]"]
    
    MED -->|No| REJECT_LOW["Return:<br/>identified=false<br/>confidence=baixa<br/>Identificacao incerta<br/>alternatives=[all top 5]"]
    
    style REJECT fill:#ffcccc
    style REJECT_LOW fill:#ffcccc
    style ACCEPT_HIGH fill:#ccffcc
    style ACCEPT_MED fill:#ffffcc
```

## 5. Decision Cascade Summary (Simplified)

```mermaid
flowchart LR
    IMG["Image"] --> CACHE{"Cache?"}
    CACHE -->|HIT| R1["Return cached<br/>~1ms"]
    CACHE -->|MISS| CLIP["CLIP Index<br/>~100-300ms"]
    
    CLIP --> S1{"Score<br/>>= 90%?"}
    S1 -->|Yes| R2["Return CLIP<br/>HIGH confidence"]
    S1 -->|No| LOC{"At Cibi<br/>Sana?"}
    
    LOC -->|Yes| R3["Return CLIP<br/>Gemini BLOCKED"]
    LOC -->|No| GEMINI["Gemini Flash"]
    
    GEMINI --> G1{"Google API<br/>available?"}
    G1 -->|Yes| GOOGLE["Google API<br/>~200-500ms"]
    G1 -->|No/Fail| EMERGENT["Emergent Key<br/>~3-8s"]
    
    GOOGLE --> GOK{"Success?"}
    GOK -->|Yes| R4["Return Gemini<br/>score=0.90"]
    GOK -->|No| EMERGENT
    
    EMERGENT --> EOK{"Success?"}
    EOK -->|Yes| R4
    EOK -->|No| R5["Fallback to CLIP<br/>or error"]
    
    style R1 fill:#e6f3ff
    style R2 fill:#ccffcc
    style R3 fill:#ffffcc
    style R4 fill:#ccffcc
    style R5 fill:#ffcccc
```

## 6. Safety Validation Flow (safety_validator.py)

Applied to every Gemini result before returning.

```mermaid
flowchart TD
    ENTRY["validar_resultado_ia(resultado)<br/>(safety_validator.py:411)"] --> EXTRACT["Extract: nome, categoria,<br/>ingredientes, descricao"]
    
    EXTRACT --> CONCAT["Concatenate all text:<br/>nome + ingredientes + descricao"]
    
    CONCAT --> DETECT_PROTEIN["Scan for PROTEINA_ANIMAL<br/>(~110 terms: frango, peixe,<br/>carne, bacon, camarao...)"]
    
    DETECT_PROTEIN --> FILTER_DECOR["Filter out decoration context:<br/>'decorado com queijo'<br/>does NOT count"]
    
    FILTER_DECOR --> DETECT_DAIRY["Scan for DERIVADOS_ANIMAIS<br/>(~60 terms: ovo, queijo,<br/>leite, manteiga, mel...)"]
    
    DETECT_DAIRY --> FILTER_VEGAN["Filter vegan versions:<br/>'queijo vegano' = NOT dairy<br/>'leite de coco' = NOT dairy"]
    
    FILTER_VEGAN --> HAS_MEAT{"Animal protein<br/>found?"}
    
    HAS_MEAT -->|Yes| FORCE_MEAT["FORCE category =<br/>proteina animal<br/>(even if AI said vegano)"]
    
    HAS_MEAT -->|No| HAS_DAIRY{"Dairy/egg<br/>found?"}
    HAS_DAIRY -->|Yes| FORCE_VEG["FORCE category =<br/>vegetariano<br/>(even if AI said vegano)"]
    HAS_DAIRY -->|No| KEEP["Keep AI's original<br/>classification"]
    
    FORCE_MEAT --> ALLERGENS
    FORCE_VEG --> ALLERGENS
    KEEP --> ALLERGENS
    
    ALLERGENS["Detect 9 allergen categories:<br/>gluten, lactose, ovo,<br/>crustaceos, peixe, amendoim,<br/>nozes, soja, gergelim"]
    
    ALLERGENS --> RETURN["Return corrected result<br/>+ _seguranca metadata block"]
    
    style FORCE_MEAT fill:#ffcccc
    style FORCE_VEG fill:#ffffcc
    style KEEP fill:#ccffcc
```

## 7. Nutrition Enrichment Flow (server.py:866-892)

```mermaid
flowchart TD
    ENTRY["Nutrition Enrichment<br/>(server.py:866)"] --> IDENTIFIED{"dish identified?"}
    
    IDENTIFIED -->|No| SKIP["nutrition = null"]
    IDENTIFIED -->|Yes| SHEET1["lookup_nutrition_sheet(dish_display)<br/>MongoDB: nutrition_sheets collection"]
    
    SHEET1 --> FOUND1{"Found by<br/>display name?"}
    FOUND1 -->|Yes| MERGE["Merge precise numeric data<br/>into nutrition object"]
    FOUND1 -->|No| SHEET2["lookup_nutrition_sheet(dish_slug)<br/>Try slug name"]
    
    SHEET2 --> FOUND2{"Found by<br/>slug?"}
    FOUND2 -->|Yes| MERGE
    FOUND2 -->|No| GEMINI_DATA{"Gemini provided<br/>nutrition?"}
    
    GEMINI_DATA -->|Yes| USE_GEMINI["Use Gemini's estimates<br/>(kcal, prot, carb, gord)"]
    GEMINI_DATA -->|No| POLICY["Use policy.py generic data<br/>by food type (carboidrato,<br/>proteina, vegetal, etc.)"]
    
    MERGE --> FORMAT["Format strings:<br/>calorias = '165 kcal'<br/>proteinas = '31.0g'<br/>etc."]
    USE_GEMINI --> FORMAT
    POLICY --> FORMAT
    
    FORMAT --> OBJ["Create NutritionInfo object"]

    subgraph SHEET_LOOKUP ["lookup_nutrition_sheet() search order"]
        direction TB
        L1["1. Exact match: nome"] --> L2["2. Match: slug"]
        L2 --> L3["3. Match in: nomes_alternativos array"]
        L3 --> L4["4. Case-insensitive regex on nome"]
    end
```

## 8. Premium Enrichment Pipeline (server.py:731-864)

```mermaid
flowchart TD
    ENTRY["Premium Check<br/>(server.py:738)"] --> HAS_CREDS{"pin + nome<br/>provided?"}
    
    HAS_CREDS -->|No| NOT_PREMIUM["is_premium = false<br/>Skip all premium features"]
    
    HAS_CREDS -->|Yes| DB_LOOKUP["db.users.find_one()<br/>Match pin_hash + nome"]
    
    DB_LOOKUP --> USER_EXISTS{"User found?"}
    USER_EXISTS -->|No| NOT_PREMIUM
    USER_EXISTS -->|Yes| PREMIUM["is_premium = true"]
    
    PREMIUM --> SCI_MONGO["1. Scientific Data<br/>from MongoDB dishes"]
    SCI_MONGO --> SCI_FOUND{"Found in DB?"}
    SCI_FOUND -->|Yes| SCI_DONE["beneficio_principal<br/>curiosidade_cientifica<br/>referencia_pesquisa<br/>alerta_saude"]
    SCI_FOUND -->|No| SCI_LOCAL["2. Fallback: local_dish_updater.py<br/>obter_conteudo_premium()<br/>Based on category + dish type"]
    SCI_LOCAL --> SCI_DONE
    
    SCI_DONE --> ALERTS["3. Real-Time Alerts"]
    
    ALERTS --> A1["verificar_alergenos_perfil()<br/>User allergies vs dish ingredients"]
    A1 --> A2["gerar_alertas_tempo_real()<br/>Weekly consumption analysis"]
    A2 --> A3["gerar_combinacoes_sugeridas()<br/>Beneficial food pairings"]
    A3 --> A4["gerar_substituicoes()<br/>Healthier alternatives"]
    A4 --> A5["Check db.novidades<br/>for dish-specific news"]
    
    A5 --> MITO["4. Myth or Truth Card<br/>get_mito_verdade()<br/>Based on ingredients + category"]
    
    MITO --> PACKAGE["Package premium_data:<br/>alertas_alergenos<br/>alertas_historico<br/>combinacoes_sugeridas<br/>substituicoes<br/>novidade<br/>mito_verdade"]
```
