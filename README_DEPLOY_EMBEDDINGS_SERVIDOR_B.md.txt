# SoulNutri AI Server — Servidor B (Embeddings + Similaridade)

Este pacote adiciona um motor de reconhecimento por imagem baseado em embeddings (CLIP) e similaridade,
mantendo compatibilidade com o modo atual (hash + visual index).

## 1) Estrutura final esperada (local e Render)

/soulnutri-ai-server
  main.py
  requirements.txt
  render.yaml
  ai/
    __init__.py
    policy.py
    embedder.py
    emb_index.py
  data/
    brownie_de_chocolate/
    bolinho_de_bacalhau/
    ...
    candidates/
    hash_index.json
    visual_index.json

IMPORTANTE:
- A pasta precisa se chamar exatamente "ai" (sem ":" e sem caracteres especiais).
- Se existir uma pasta chamada ":ai", renomeie para "ai".

## 2) Modo de reconhecimento (hash vs embeddings)

O servidor passa a ter um "modo" selecionável por variável de ambiente:

RECO_MODE=hash        (padrão seguro, compatível com o atual)
RECO_MODE=embeddings  (novo modo recomendado)

No Render, você define isso em:
Service -> Environment -> Add Environment Variable

Sugestão:
- Primeiro deploy com RECO_MODE=hash (para garantir que nada quebre).
- Depois troque para RECO_MODE=embeddings e rode /ai/reindex.

## 3) Checklist antes de deploy

No seu Mac:

1) Confirmar que você está na pasta do projeto:
   cd /Users/joaomanoel/Desktop/soulnutri-ai-server

2) Confirmar estrutura:
   ls -la
   (deve existir main.py, requirements.txt, render.yaml, data/, ai/)

3) Confirmar que a pasta "ai" existe e contém os arquivos do pacote:
   ls -la ai

4) Confirmar que as fotos do banco estão em data/<dish_slug>/*.jpg:
   ls -la data/brownie_de_chocolate | head

## 4) Deploy no Render (GitHub)

Se o Render estiver conectado ao GitHub:

1) commit e push:
   git status
   git add -A
   git commit -m "Servidor B: embeddings CLIP + modo hash compat"
   git push

2) No painel do Render:
   Deploys -> Manual Deploy -> Deploy latest commit

## 5) Deploy no Render (ZIP)

Se você sobe ZIP no Render:

1) compacte a pasta do projeto (incluindo ai/ e data/):
   - selecione: main.py, requirements.txt, render.yaml, ai/, data/
   - botão direito -> Compress

2) no painel do Render:
   Settings/Deploy -> Upload ZIP -> Deploy

## 6) Testes após deploy

A) Ver se o servidor está no ar:
   curl -s https://soulnutri-ai-server.onrender.com/ ; echo

B) Ver rotas publicadas:
   curl -s https://soulnutri-ai-server.onrender.com/openapi.json | head ; echo

C) Status do índice (continua existindo):
   curl -s https://soulnutri-ai-server.onrender.com/ai/index-status ; echo

D) Reindex (obrigatório quando trocar para embeddings):
   curl -s -X POST https://soulnutri-ai-server.onrender.com/ai/reindex ; echo

E) Teste identify-image:
   curl -s -X POST https://soulnutri-ai-server.onrender.com/ai/identify-image \
     -F file=@./data/brownie_de_chocolate/20251220_113706.jpg ; echo

F) Teste save-capture (candidates):
   curl -s -X POST https://soulnutri-ai-server.onrender.com/ai/save-capture \
     -F file=@./data/brownie_de_chocolate/20251220_113706.jpg \
     -F source=terminal-test ; echo

G) Listar candidates:
   curl -s "https://soulnutri-ai-server.onrender.com/ai/candidates-list?limit=5" ; echo

## 7) Resultado esperado no modo embeddings

- identify-image retorna:
  - identified=true somente quando score >= HIGH (ex.: 0.85)
  - top_matches sempre (para transparência)
- Melhor redução de erros grosseiros em comparação ao hash.

## 8) Se o build do Render falhar

O modo embeddings usa torch + open_clip.
Se o build falhar, copie o log do Render e envie, que ajustamos as versões/pacote.

