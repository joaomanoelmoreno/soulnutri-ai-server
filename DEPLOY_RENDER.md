# SoulNutri - Guia de Deploy no Render
## Deploy Unificado (FastAPI + React)

---

## Pre-requisitos
- Conta Render (plano Starter)
- Repositorio GitHub com o codigo SoulNutri
- Dominio `soulnutri.app.br` configurado no Cloudflare

---

## Passo 1: Subir o Codigo para o GitHub

No seu computador local (ou usando "Save to GitHub" no Emergent):

```bash
git add -A
git commit -m "Deploy unificado: FastAPI serve React build"
git push origin main
```

**Arquivos criticos que DEVEM estar no repo:**
- `Dockerfile` (raiz do projeto)
- `.dockerignore` (raiz do projeto)
- `render.yaml` (raiz do projeto)
- `datasets/dish_index.json` (~146KB)
- `datasets/dish_index_embeddings.npy` (~6MB)
- `datasets/descriptions.json` (~37KB)
- `datasets/dish_name_mapping.json` (~2KB)

**NAO subir para o GitHub:**
- `datasets/organized/` (3.3GB de imagens - adicionar ao `.gitignore`)
- `frontend/build/` (sera gerado pelo Docker)
- `backend/.env` (segredos)

---

## Passo 2: Criar Servico no Render

1. Acesse [dashboard.render.com](https://dashboard.render.com)
2. Clique em **"New" > "Web Service"**
3. Conecte o repositorio GitHub do SoulNutri
4. Configure:
   - **Name**: `soulnutri`
   - **Region**: Oregon (US West)
   - **Runtime**: **Docker**
   - **Plan**: Starter ($7/mes)
   - **Dockerfile Path**: `./Dockerfile`

---

## Passo 3: Configurar Variaveis de Ambiente

No painel do Render, va em **Environment > Environment Variables** e adicione:

| Variavel | Valor |
|----------|-------|
| `MONGO_URL` | `mongodb+srv://cibisanajoaomanoel_db_user:ptS8L9nD1iPx2x1P@soulnutricluster0.zptgmki.mongodb.net/soulnutri?retryWrites=true&w=majority` |
| `DB_NAME` | `soulnutri` |
| `CORS_ORIGINS` | `*` |
| `EMERGENT_LLM_KEY` | *(sua chave Emergent)* |
| `GOOGLE_API_KEY` | *(sua chave Google)* |
| `USDA_API_KEY` | *(sua chave USDA)* |
| `R2_ACCESS_KEY_ID` | *(sua chave R2)* |
| `R2_SECRET_ACCESS_KEY` | *(seu secret R2)* |
| `R2_ENDPOINT` | `https://2723f210eede7a83470abe72ffeaeecb.r2.cloudflarestorage.com` |
| `R2_BUCKET` | `soulnutri-images` |
| `USE_LOCAL_MODEL` | `false` |

---

## Passo 4: Configurar Health Check

No painel do Render:
- **Health Check Path**: `/health`

---

## Passo 5: Configurar Dominio Customizado

1. No Render, va em **Settings > Custom Domains**
2. Adicione: `soulnutri.app.br`
3. O Render fornecera um registro CNAME
4. No Cloudflare DNS, adicione:
   - **Type**: CNAME
   - **Name**: `@` (ou `soulnutri.app.br`)
   - **Target**: O CNAME fornecido pelo Render (ex: `soulnutri.onrender.com`)
   - **Proxy**: Desligado (DNS only - nuvem cinza)

---

## Passo 6: Deploy

1. Clique em **"Manual Deploy" > "Deploy latest commit"**
2. Aguarde o build (primeira vez pode levar ~5-10 min)
3. O log deve mostrar:
   ```
   [DEPLOY] Frontend build encontrado em ... - Modo unificado ativo
   ```
4. Acesse `https://soulnutri.app.br` e verifique!

---

## Arquitetura do Deploy

```
Usuario -> soulnutri.app.br
              |
         [Render - Docker]
              |
         FastAPI (porta $PORT)
           /         \
     /api/*        /*  (catch-all)
       |              |
   Backend API    React SPA
   (MongoDB,      (index.html +
    R2, IA)       static files)
```

## Como funciona:
- Rotas `/api/*` -> Processadas pelo FastAPI (backend)
- Rota `/health` -> Health check do Kubernetes/Render
- Qualquer outra rota -> Serve o `index.html` do React (SPA)
- Arquivos estaticos (`/static/js/*.js`, `/manifest.json`, etc.) -> Servidos diretamente

---

## Troubleshooting

### Build falha no Docker
- Verifique se `datasets/dish_index.json` e `datasets/dish_index_embeddings.npy` estao no repo
- Verifique se `frontend/yarn.lock` esta no repo

### App carrega mas API nao funciona
- Verifique as variaveis de ambiente no Render (especialmente MONGO_URL)
- Cheque os logs no Render Dashboard

### Imagens dos pratos nao carregam
- Verifique as chaves R2 (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY)
- O bucket `soulnutri-images` deve estar acessivel

### IA nao identifica pratos
- Verifique se `USE_LOCAL_MODEL=false` esta configurado
- Os arquivos de indice devem estar em `/app/datasets/` dentro do container
