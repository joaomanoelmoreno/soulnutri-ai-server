# SoulNutri - Documentação Técnica Completa

**Versão:** 1.0  
**Data:** Fevereiro 2026  
**Classificação:** Documento Técnico - Arquitetura de Software

---

# 1. VISÃO GERAL DO APLICATIVO

## 1.1 Objetivo
O **SoulNutri** é um aplicativo de nutrição virtual inteligente que identifica pratos de comida em tempo real através de análise de imagens, fornecendo informações nutricionais detalhadas e personalizadas aos usuários.

## 1.2 Problema de Negócio Resolvido
- Identificação instantânea de pratos em buffets e restaurantes
- Fornecimento de informações nutricionais precisas (calorias, macronutrientes, alergênicos)
- Auxílio no controle alimentar para usuários com restrições (diabéticos, hipertensos, alérgicos)
- Rastreamento de consumo diário para usuários Premium

## 1.3 Principais Funcionalidades
| Funcionalidade | Descrição |
|----------------|-----------|
| Reconhecimento de Pratos | Identificação via IA (CLIP local + Gemini) |
| Informações Nutricionais | Calorias, proteínas, carboidratos, gorduras |
| Alertas Personalizados | Avisos para alérgenos e restrições alimentares |
| Histórico de Refeições | Registro diário de consumo (Premium) |
| Análise Semanal | Relatórios de consumo e metas (Premium) |
| Painel Administrativo | Gestão de pratos, imagens e dados nutricionais |

## 1.4 Tipo de Aplicação
- **Tipo:** Progressive Web App (PWA)
- **Plataformas:** Web (desktop e mobile), compatível com iOS e Android via navegador
- **Modelo:** Freemium (funcionalidades básicas gratuitas, Premium por assinatura)

## 1.5 Perfis de Usuários
| Perfil | Descrição | Funcionalidades |
|--------|-----------|-----------------|
| Usuário Anônimo | Acesso básico sem login | Identificação de pratos, informações nutricionais básicas |
| Usuário Premium | Assinante com perfil | Alertas personalizados, histórico, análise semanal, metas |
| Administrador | Gestão do sistema | CRUD de pratos, gestão de imagens, auditoria |

---

# 2. VISÃO GERAL DA ARQUITETURA

## 2.1 Estilo Arquitetural
**Arquitetura Monolítica Modular** com separação clara de responsabilidades:
- Frontend SPA (Single Page Application)
- Backend API REST
- Banco de dados NoSQL
- Serviços de IA em cascata

## 2.2 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USUÁRIOS                                        │
│                    (Mobile / Desktop / Tablet)                               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES INGRESS                                   │
│                    (Load Balancer / SSL Termination)                         │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────────────────────┐
│      FRONTEND (PWA)       │   │              BACKEND API                   │
│      React 19 + Vite      │   │           FastAPI + Python                 │
│         Port 3000         │   │             Port 8001                      │
│                           │   │                                            │
│  ┌─────────────────────┐  │   │  ┌─────────────────────────────────────┐   │
│  │   Componentes UI    │  │   │  │         API REST (/api/*)           │   │
│  │   (Shadcn/Radix)    │  │   │  │                                     │   │
│  └─────────────────────┘  │   │  │  • /ai/identify                     │   │
│  ┌─────────────────────┐  │   │  │  • /premium/*                       │   │
│  │   Estado Global     │  │   │  │  • /admin/*                         │   │
│  │   (React Hooks)     │  │   │  │  • /radar/*                         │   │
│  └─────────────────────┘  │   │  └─────────────────────────────────────┘   │
│  ┌─────────────────────┐  │   │                    │                       │
│  │   Geolocalização    │  │   │  ┌─────────────────┴─────────────────┐     │
│  │   (GPS/Cibi Sana)   │  │   │  │                                   │     │
│  └─────────────────────┘  │   │  ▼                                   ▼     │
└───────────────────────────┘   │ ┌───────────────┐   ┌───────────────────┐  │
                                │ │  MÓDULO IA    │   │   SERVIÇOS        │  │
                                │ │               │   │                   │  │
                                │ │ • CLIP Local  │   │ • Policy          │  │
                                │ │ • Gemini API  │   │ • Nutrition       │  │
                                │ │ • Embedder    │   │ • Alerts          │  │
                                │ │ • Index       │   │ • Translation     │  │
                                │ └───────┬───────┘   └───────────────────┘  │
                                │         │                                   │
                                └─────────┼───────────────────────────────────┘
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              │                           │                           │
              ▼                           ▼                           ▼
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│   MONGODB ATLAS      │   │   SISTEMA DE         │   │   GOOGLE GEMINI      │
│   (Banco NoSQL)      │   │   ARQUIVOS           │   │   (API Externa)      │
│                      │   │                      │   │                      │
│ • users              │   │ • /datasets/         │   │ • Identificação      │
│ • dishes             │   │   organized/         │   │   de pratos          │
│ • daily_logs         │   │ • Imagens de         │   │ • Informações        │
│ • feedback           │   │   treino CLIP        │   │   nutricionais       │
│ • novidades          │   │ • Índice vetorial    │   │                      │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

## 2.3 Fluxo de Identificação de Pratos (Cascata IA)

```
┌─────────────────┐
│  Usuário tira   │
│     foto        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VERIFICAÇÃO DE LOCALIZAÇÃO                    │
│                                                                  │
│  GPS detecta se usuário está no Cibi Sana (raio 100m)?          │
│  Coordenadas: -23.0373642, -46.9767934                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│    CIBI SANA (Local)    │     │     EXTERNO (Fora do Cibi)      │
│                         │     │                                  │
│  CLIP LOCAL APENAS      │     │  CLIP → Se < 90% → GEMINI       │
│  (Gemini TRAVADO)       │     │  (Cascata normal)               │
│  Custo: ZERO            │     │  Custo: ~$0.000006/req          │
└────────────┬────────────┘     └─────────────────┬───────────────┘
             │                                     │
             └─────────────────┬───────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NÍVEIS DE CONFIANÇA                          │
│                                                                  │
│  >= 85%  → "Identificado" (alta confiança)                      │
│  50-85%  → "Consulte o atendente" (média confiança)             │
│  < 50%   → "Pode não ser o prato" (baixa confiança)             │
└─────────────────────────────────────────────────────────────────┘
```

---

# 3. FRONTEND

## 3.1 Stack Tecnológico

| Categoria | Tecnologia | Versão |
|-----------|------------|--------|
| Framework | React | 19.0.0 |
| UI Components | Radix UI / Shadcn | Últimas |
| Styling | Tailwind CSS | 3.x |
| Build Tool | Create React App (CRACO) | 5.0.1 |
| Routing | React Router DOM | 7.13.0 |
| Forms | React Hook Form + Zod | 7.56.2 / 3.24.4 |
| Charts | Recharts | 3.6.0 |
| Icons | Lucide React | 0.507.0 |

## 3.2 Estrutura de Diretórios

```
frontend/
├── public/
│   ├── images/           # Imagens estáticas
│   ├── qrcodes/          # QR Codes gerados
│   └── fotos_revisar/    # Fotos pendentes de revisão
├── src/
│   ├── components/
│   │   └── ui/           # Componentes Shadcn/Radix
│   ├── hooks/            # Custom React Hooks
│   ├── lib/              # Utilitários
│   ├── App.js            # Componente principal
│   ├── Admin.js          # Painel administrativo
│   ├── PremiumProfile.jsx # Perfil usuário premium
│   └── I18nContext.js    # Internacionalização
└── package.json
```

## 3.3 Componentes Principais

```
┌─────────────────────────────────────────────────────────────────┐
│                          App.js                                  │
│                    (Componente Raiz)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Header     │  │   Camera     │  │   Results Display    │   │
│  │   • Logo     │  │   • Capture  │  │   • Dish Info        │   │
│  │   • Menu     │  │   • Preview  │  │   • Nutrition        │   │
│  │   • Premium  │  │   • Flash    │  │   • Alerts           │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  GeoLocation │  │  Premium     │  │   Feedback Modal     │   │
│  │  • GPS       │  │  • Login     │  │   • Correct/Wrong    │   │
│  │  • Cibi Sana │  │  • Profile   │  │   • Suggestions      │   │
│  │    Detection │  │  • History   │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 3.4 Fluxo de Autenticação (Premium)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Usuário   │────▶│   Login     │────▶│   Backend   │
│   (Nome+PIN)│     │   Form      │     │   /premium/ │
└─────────────┘     └─────────────┘     │   login     │
                                        └──────┬──────┘
                                               │
                          ┌────────────────────┴────────────────────┐
                          │                                         │
                          ▼                                         ▼
                   ┌─────────────┐                           ┌─────────────┐
                   │   Sucesso   │                           │   Falha     │
                   │             │                           │             │
                   │ Salva em    │                           │ Mostra      │
                   │ localStorage│                           │ Erro        │
                   └─────────────┘                           └─────────────┘
```

## 3.5 Comunicação com Backend

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/ai/identify` | POST | Identificação de prato |
| `/api/premium/login` | POST | Login usuário premium |
| `/api/premium/profile` | POST | Atualiza perfil |
| `/api/premium/daily-summary` | GET | Resumo diário |
| `/api/admin/dishes` | GET | Lista pratos (admin) |

## 3.6 Estratégia de Deploy

- **Build:** `yarn build` (Create React App com CRACO)
- **Hosting:** Kubernetes Pod (porta 3000)
- **CDN:** Não aplicável (servido diretamente)
- **Hot Reload:** Habilitado em desenvolvimento

---

# 4. BACKEND (FastAPI / Python)

## 4.1 Stack Tecnológico

| Categoria | Tecnologia | Versão |
|-----------|------------|--------|
| Framework | FastAPI | 0.110.1 |
| Server | Uvicorn | 0.25.0 |
| Database Driver | Motor (async MongoDB) | 3.3.1 |
| Image Processing | Pillow | 12.1.0 |
| ML/AI | OpenCLIP, NumPy | Últimas |
| Validation | Pydantic | 2.6.4 |

## 4.2 Estrutura de Diretórios

```
backend/
├── server.py              # Aplicação principal (monolítico)
├── rebuild_index.py       # Script de reindexação CLIP
├── .env                   # Variáveis de ambiente
├── ai/
│   ├── embedder.py        # Geração de embeddings CLIP
│   ├── index.py           # Índice vetorial e busca
│   └── policy.py          # Política de decisão e nutrição
├── services/
│   ├── gemini_flash_service.py  # Integração Google Gemini
│   ├── nutrition_premium_service.py
│   ├── alerts_service.py
│   ├── audit_service.py
│   ├── cache_service.py
│   ├── translation_service.py
│   └── safety_validator.py
├── data/                  # Dados estáticos
└── tests/                 # Testes automatizados
```

## 4.3 Camadas da Aplicação

```
┌─────────────────────────────────────────────────────────────────┐
│                     CAMADA DE APRESENTAÇÃO                       │
│                        (API Routes)                              │
│  server.py: @api_router.get/post/put/delete                     │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                     CAMADA DE SERVIÇOS                          │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ AI Services │  │  Business   │  │    External APIs        │  │
│  │             │  │  Services   │  │                         │  │
│  │ • embedder  │  │ • nutrition │  │ • gemini_flash_service  │  │
│  │ • index     │  │ • alerts    │  │ • google_vision_service │  │
│  │ • policy    │  │ • audit     │  │ • translation_service   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                     CAMADA DE DADOS                              │
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │   MongoDB (Motor)   │  │    Sistema de Arquivos          │   │
│  │                     │  │                                 │   │
│  │ • users             │  │ • /datasets/organized/          │   │
│  │ • dishes            │  │ • dish_index.json               │   │
│  │ • daily_logs        │  │ • dish_index_embeddings.npy     │   │
│  │ • feedback          │  │                                 │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 4.4 Mapa de Rotas da API

### Rotas de IA
| Rota | Método | Descrição |
|------|--------|-----------|
| `/api/ai/identify` | POST | Identifica prato via imagem |
| `/api/ai/identify-with-ai` | POST | Força identificação via Gemini |
| `/api/ai/identify-multi` | POST | Identifica múltiplos pratos |
| `/api/ai/status` | GET | Status do índice CLIP |
| `/api/ai/reindex` | POST | Reindexa pratos |
| `/api/ai/dishes` | GET | Lista todos os pratos |
| `/api/ai/feedback` | POST | Registra feedback |

### Rotas Premium
| Rota | Método | Descrição |
|------|--------|-----------|
| `/api/premium/register` | POST | Cadastro de usuário |
| `/api/premium/login` | POST | Login (nome + PIN) |
| `/api/premium/profile` | POST | Atualiza perfil |
| `/api/premium/log-meal` | POST | Registra refeição |
| `/api/premium/daily-summary` | GET | Resumo do dia |
| `/api/premium/history` | GET | Histórico de refeições |
| `/api/premium/weekly-analysis` | GET | Análise semanal |

### Rotas Admin
| Rota | Método | Descrição |
|------|--------|-----------|
| `/api/admin/dishes` | GET | Lista pratos |
| `/api/admin/dishes-full` | GET | Lista completa com imagens |
| `/api/admin/dishes/{slug}` | PUT | Atualiza prato |
| `/api/admin/dishes/{slug}` | DELETE | Remove prato |
| `/api/admin/dish-image/{slug}` | GET | Obtém imagem |
| `/api/admin/dish-image/{slug}` | DELETE | Remove imagem |
| `/api/admin/audit` | GET | Auditoria de dados |

## 4.5 Ciclo de Vida da Requisição

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      KUBERNETES INGRESS                          │
│                    (SSL Termination)                             │
└─────────────────────────────────┬───────────────────────────────┘
       │ /api/* → Port 8001
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        UVICORN SERVER                            │
│                      (ASGI Application)                          │
└─────────────────────────────────┬───────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI MIDDLEWARE                          │
│                                                                  │
│  • CORS Handler                                                  │
│  • Request Validation (Pydantic)                                │
│  • Error Handler                                                 │
└─────────────────────────────────┬───────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ROUTE HANDLER                              │
│                    (@api_router.post/get)                        │
│                                                                  │
│  1. Parse request (Form/JSON)                                   │
│  2. Validate input                                              │
│  3. Execute business logic                                      │
│  4. Query database / AI services                                │
│  5. Format response                                             │
└─────────────────────────────────┬───────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      JSON RESPONSE                               │
│                                                                  │
│  {                                                               │
│    "ok": true,                                                  │
│    "data": {...}                                                │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

# 5. BANCO DE DADOS E ARMAZENAMENTO

## 5.1 Configuração

| Parâmetro | Valor |
|-----------|-------|
| Tipo | MongoDB (NoSQL) |
| Hosting | MongoDB Atlas (Cloud) |
| Driver | Motor (async) / PyMongo |
| Database Name | soulnutri |

## 5.2 Collections (Entidades)

### users
```json
{
  "_id": "ObjectId",
  "nome": "string",
  "pin_hash": "string (bcrypt)",
  "premium_ativo": "boolean",
  "peso": "number",
  "altura": "number",
  "idade": "number",
  "sexo": "string (M/F)",
  "objetivo": "string",
  "meta_calorica": "number",
  "restricoes": ["string"],
  "created_at": "datetime"
}
```

### dishes
```json
{
  "_id": "ObjectId",
  "name": "string",
  "slug": "string",
  "category": "string",
  "calorias": "number",
  "proteinas": "number",
  "carboidratos": "number",
  "gorduras": "number",
  "fibras": "number",
  "sodio": "number",
  "alergenos": ["string"],
  "ingredientes": ["string"],
  "modo_preparo": "string",
  "created_at": "datetime"
}
```

### daily_logs
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "date": "string (YYYY-MM-DD)",
  "meals": [
    {
      "dish_name": "string",
      "calorias": "number",
      "timestamp": "datetime"
    }
  ],
  "total_calorias": "number"
}
```

### feedback
```json
{
  "_id": "ObjectId",
  "dish_name": "string",
  "is_correct": "boolean",
  "suggested_name": "string",
  "timestamp": "datetime"
}
```

## 5.3 Diagrama ER

```
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ _id (PK)            │
│ nome                │
│ pin_hash            │◄─────────────────────┐
│ premium_ativo       │                      │
│ peso, altura, idade │                      │
│ meta_calorica       │                      │
│ restricoes[]        │                      │
└─────────────────────┘                      │
                                             │
┌─────────────────────┐           ┌──────────┴──────────┐
│      dishes         │           │     daily_logs      │
├─────────────────────┤           ├─────────────────────┤
│ _id (PK)            │           │ _id (PK)            │
│ name                │◄──────────│ user_id (FK)        │
│ slug                │           │ date                │
│ calorias            │           │ meals[]             │
│ proteinas           │           │ total_calorias      │
│ carboidratos        │           └─────────────────────┘
│ gorduras            │
│ alergenos[]         │
│ ingredientes[]      │
└─────────────────────┘

┌─────────────────────┐
│      feedback       │
├─────────────────────┤
│ _id (PK)            │
│ dish_name           │
│ is_correct          │
│ suggested_name      │
│ timestamp           │
└─────────────────────┘
```

## 5.4 Armazenamento de Arquivos

| Tipo | Localização | Descrição |
|------|-------------|-----------|
| Imagens de Treino | `/app/datasets/organized/` | Imagens para treino do CLIP |
| Índice Vetorial | `/app/datasets/dish_index.json` | Mapeamento prato → embeddings |
| Embeddings | `/app/datasets/dish_index_embeddings.npy` | Vetores 512-dim NumPy |

**Estrutura de Pastas:**
```
datasets/
├── organized/
│   ├── Arroz Branco/          # 15 imagens
│   ├── Feijão Preto/          # 12 imagens
│   ├── Strogonoff de Frango/  # 20 imagens
│   └── ... (291 pratos)
├── dish_index.json            # 291 pratos, 1728 embeddings
└── dish_index_embeddings.npy  # Matriz 1728 x 512
```

---

# 6. COMPONENTES DE IA E MACHINE LEARNING

## 6.1 Modelos Utilizados

| Modelo | Tipo | Finalidade | Custo |
|--------|------|------------|-------|
| OpenCLIP ViT-B-32 | Local (CPU) | Identificação de pratos Cibi Sana | ZERO |
| Google Gemini 1.5 Flash | API Externa | Identificação externa + fallback | ~$0.000006/req |

## 6.2 Pipeline de Identificação

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENTRADA: Imagem (JPEG)                      │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PRÉ-PROCESSAMENTO                              │
│                                                                  │
│  1. Redimensionar (224x224)                                     │
│  2. Normalizar pixels                                           │
│  3. Converter para tensor                                       │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLIP ENCODER                                │
│                    (ViT-B-32 OpenAI)                            │
│                                                                  │
│  Input: Tensor 224x224x3                                        │
│  Output: Embedding 512-dim (normalizado)                        │
│  Tempo: ~100ms (CPU)                                            │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSCA VETORIAL                                │
│                                                                  │
│  1. Calcular similaridade cosseno com índice (1728 embeddings)  │
│  2. Ordenar por score                                           │
│  3. Agrupar por prato (pegar melhor de cada)                    │
│  4. Aplicar calibração de confiança                             │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
         Score >= 90%                  Score < 90%
         (Cibi Sana)                   (ou Externo)
                    │                           │
                    ▼                           ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│    RETORNA CLIP         │     │        GOOGLE GEMINI            │
│                         │     │                                  │
│  dish: "Arroz Branco"   │     │  Prompt: "Identifique o prato   │
│  score: 0.95            │     │  brasileiro na imagem..."       │
│  source: "local_index"  │     │                                  │
│                         │     │  Output: Nome, calorias,        │
│                         │     │  ingredientes, alergênicos      │
└─────────────────────────┘     └─────────────────────────────────┘
```

## 6.3 Calibração de Confiança CLIP

A calibração converte scores brutos de similaridade em níveis de confiança interpretáveis:

| Score Bruto | Confiança Calibrada | Interpretação |
|-------------|---------------------|---------------|
| >= 0.85 | 90-98% | Alta confiança (match direto) |
| 0.70-0.85 | 80-90% | Confiança média-alta |
| 0.50-0.70 | 60-80% | Confiança média (usa gap analysis) |
| < 0.50 | < 60% | Baixa confiança |

## 6.4 Estratégia de Prompts (Gemini)

```python
PROMPT_TEMPLATE = """
Analise esta imagem de comida brasileira e responda em JSON:
{
  "nome": "Nome do prato em português",
  "confianca": 0.0-1.0,
  "calorias_estimadas": número,
  "ingredientes_principais": ["lista"],
  "alergenos": ["lista"],
  "categoria": "proteína/carboidrato/salada/sobremesa"
}

Regras:
- Foque em pratos brasileiros típicos
- Se não conseguir identificar, retorne confiança < 0.5
- Considere porção padrão de buffet (~100-150g)
"""
```

## 6.5 Considerações de Performance

| Métrica | CLIP Local | Gemini API |
|---------|------------|------------|
| Latência | ~100ms | ~800-1500ms |
| Custo | $0 | ~$0.000006/req |
| Acurácia Cibi Sana | 90-95% | 95-100% |
| Acurácia Externa | N/A | 90-95% |
| Disponibilidade | 100% | 99.9% |

---

# 7. INTEGRAÇÕES E SERVIÇOS EXTERNOS

## 7.1 Lista de Integrações

| Serviço | Função | Protocolo |
|---------|--------|-----------|
| Google Gemini | Identificação de pratos | REST API (HTTPS) |
| MongoDB Atlas | Banco de dados | MongoDB Wire Protocol |
| Hugging Face | Modelo CLIP (download inicial) | HTTPS |

## 7.2 Google Gemini

- **Endpoint:** `generativelanguage.googleapis.com`
- **Modelo:** `gemini-1.5-flash`
- **Autenticação:** API Key
- **Rate Limit:** 15 RPM (grátis), ilimitado (pago)
- **Custo:** ~$0.000006 por requisição

## 7.3 MongoDB Atlas

- **Conexão:** String de conexão via `MONGO_URL`
- **Driver:** Motor (async) / PyMongo
- **Região:** Automática (mais próxima)

---

# 8. INFRAESTRUTURA E DEPLOY

## 8.1 Ambiente de Hosting

| Componente | Hosting | Porta |
|------------|---------|-------|
| Frontend | Kubernetes Pod | 3000 |
| Backend | Kubernetes Pod | 8001 |
| MongoDB | MongoDB Atlas | 27017 |

## 8.2 Diagrama de Deploy

```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                            │
│                      (Emergent Platform)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      INGRESS                               │  │
│  │            nutri-scanner-10.preview.emergentagent.com     │  │
│  │                                                            │  │
│  │    / → Frontend:3000     /api/* → Backend:8001            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              ▼                               ▼                  │
│  ┌─────────────────────┐     ┌─────────────────────────────┐   │
│  │   POD: Frontend     │     │      POD: Backend           │   │
│  │                     │     │                             │   │
│  │  ┌───────────────┐  │     │  ┌───────────────────────┐  │   │
│  │  │  React App    │  │     │  │   FastAPI + Uvicorn   │  │   │
│  │  │  (yarn start) │  │     │  │   + OpenCLIP Model    │  │   │
│  │  │  Port 3000    │  │     │  │   Port 8001           │  │   │
│  │  └───────────────┘  │     │  └───────────────────────┘  │   │
│  │                     │     │              │               │   │
│  └─────────────────────┘     │  ┌───────────┴───────────┐  │   │
│                              │  │   Volume Mount        │  │   │
│                              │  │   /app/datasets/      │  │   │
│                              │  └───────────────────────┘  │   │
│                              └─────────────────────────────┘   │
│                                             │                   │
└─────────────────────────────────────────────┼───────────────────┘
                                              │
                                              ▼
                              ┌─────────────────────────────┐
                              │       MONGODB ATLAS         │
                              │     (External Cloud)        │
                              │                             │
                              │   Database: soulnutri       │
                              │   Region: Auto              │
                              └─────────────────────────────┘
```

## 8.3 Gestão de Processos (Supervisor)

```ini
[program:frontend]
command=yarn start
directory=/app/frontend
autostart=true
autorestart=true

[program:backend]
command=uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
autostart=true
autorestart=true
```

## 8.4 Variáveis de Ambiente

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://nutri-scanner-10.preview.emergentagent.com
```

### Backend (.env)
```
MONGO_URL=mongodb+srv://...
DB_NAME=soulnutri
GOOGLE_API_KEY=...
USE_LOCAL_MODEL=true
```

---

# 9. SEGURANÇA

## 9.1 Autenticação

| Tipo | Método | Descrição |
|------|--------|-----------|
| Premium Users | Nome + PIN (4 dígitos) | Hash bcrypt, sem JWT |
| Admin | Não implementado | Acesso direto via rota |

## 9.2 Gerenciamento de Segredos

- Variáveis sensíveis em arquivos `.env`
- Nunca commitados no repositório
- Gerenciados via plataforma Emergent

## 9.3 Segurança de Rede

- **HTTPS:** Obrigatório (SSL no Ingress)
- **CORS:** Configurado para domínio específico
- **Rate Limiting:** Não implementado (dependente do Gemini)

## 9.4 Proteção de Dados

- Senhas hashadas com bcrypt
- Sem armazenamento de dados de pagamento
- Logs sem informações sensíveis

---

# 10. OBSERVABILIDADE E OPERAÇÃO

## 10.1 Logs

| Componente | Localização | Formato |
|------------|-------------|---------|
| Backend | `/var/log/supervisor/backend.*.log` | Text/JSON |
| Frontend | `/var/log/supervisor/frontend.*.log` | Text |

## 10.2 Métricas Disponíveis

- Status do índice CLIP (`/api/ai/status`)
- Contagem de feedbacks (`/api/ai/feedback/stats`)
- Quota Google API (`/api/ai/google-quota-status`)

## 10.3 Health Checks

```bash
# Backend
GET /api/health → {"ok": true, "service": "SoulNutri AI Server"}

# AI Status
GET /api/ai/status → {"total_dishes": 291, "total_embeddings": 1728}
```

---

# 11. ESCALABILIDADE E EVOLUÇÃO

## 11.1 Modelo Atual

- **Vertical:** Single pod por serviço
- **Horizontal:** Não implementado

## 11.2 Gargalos Conhecidos

| Gargalo | Impacto | Solução Sugerida |
|---------|---------|------------------|
| server.py monolítico | Manutenção difícil | Modularizar em blueprints |
| Armazenamento local | Limite de disco | Migrar para Cloudflare R2 |
| Índice em memória | RAM limitada | Usar FAISS ou Pinecone |

## 11.3 Sugestões de Melhoria

1. **Aprendizado Contínuo:** Salvar identificações do Gemini no índice CLIP
2. **Cache Distribuído:** Redis para resultados frequentes
3. **CDN para Imagens:** Cloudflare R2 ou S3
4. **Autenticação Robusta:** JWT com refresh tokens

## 11.4 Roadmap Técnico

| Fase | Descrição | Prioridade |
|------|-----------|------------|
| 1 | Aprendizado contínuo | Alta |
| 2 | Migração imagens para R2 | Média |
| 3 | Refatoração server.py | Média |
| 4 | Sistema de pagamentos (Stripe) | Baixa |

---

# 12. TABELAS RESUMO

## 12.1 Tecnologias por Categoria

| Categoria | Tecnologias |
|-----------|-------------|
| **Frontend** | React 19, Tailwind CSS, Radix UI, React Router |
| **Backend** | FastAPI, Uvicorn, Pydantic, Motor |
| **IA/ML** | OpenCLIP, NumPy, Pillow |
| **Banco de Dados** | MongoDB Atlas |
| **Infraestrutura** | Kubernetes, Supervisor, Nginx |
| **APIs Externas** | Google Gemini |

## 12.2 Serviços e Responsabilidades

| Serviço | Arquivo | Responsabilidade |
|---------|---------|------------------|
| embedder.py | /backend/ai/ | Geração de embeddings CLIP |
| index.py | /backend/ai/ | Busca vetorial e calibração |
| policy.py | /backend/ai/ | Regras de nutrição e alertas |
| gemini_flash_service.py | /backend/services/ | Integração Google Gemini |
| alerts_service.py | /backend/services/ | Alertas personalizados |
| nutrition_premium_service.py | /backend/services/ | Cálculos nutricionais |

## 12.3 Lista de APIs e Finalidades

| API | Método | Finalidade |
|-----|--------|------------|
| /api/ai/identify | POST | Identificar prato via imagem |
| /api/ai/status | GET | Status do sistema de IA |
| /api/premium/login | POST | Autenticação de usuário |
| /api/premium/daily-summary | GET | Resumo diário de refeições |
| /api/admin/dishes | GET | Listar pratos (admin) |
| /api/admin/dishes/{slug} | PUT/DELETE | Gerenciar prato |

---

# 13. ANEXOS

## 13.1 Comandos Úteis

```bash
# Reiniciar serviços
sudo supervisorctl restart frontend backend

# Ver logs
tail -f /var/log/supervisor/backend.err.log

# Status do índice
curl http://localhost:8001/api/ai/status

# Rebuild índice CLIP
cd /app/backend && python3 rebuild_index.py
```

## 13.2 Estrutura de Resposta Padrão

```json
{
  "ok": true,
  "dish_display": "Arroz Branco",
  "score": 0.95,
  "confidence": "alta",
  "source": "local_index",
  "nutrition": {
    "calorias": 130,
    "proteinas": 2.7,
    "carboidratos": 28,
    "gorduras": 0.3
  },
  "alertas_personalizados": []
}
```

---

**Documento gerado em:** Fevereiro 2026  
**Versão:** 1.0  
**Autor:** Sistema SoulNutri
