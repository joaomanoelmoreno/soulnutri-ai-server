# SoulNutri - Product Requirements Document

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-16, DataComp.XL) para embedding de imagens
- Storage: Cloudflare R2 (bucket: soulnutri-images) - 3929 fotos
- DB: MongoDB Atlas

## Regra de Negocio Critica: Hard Lock Cibi Sana
- Dentro do Cibi Sana (restaurant=cibi_sana): APENAS OpenCLIP. Gemini 100% BLOQUEADO.
- Fora do Cibi Sana: Gemini permitido como fallback quando CLIP < 85%.
- Aplicado em 3 endpoints: /ai/identify, /ai/identify-with-ai, /ai/identify-flash
- Log: [HARD LOCK] nos logs do backend para rastreabilidade

## Funcionalidades Implementadas
- Identificacao de pratos via camera/foto
- Ficha nutricional detalhada com dados TACO (255 mapeamentos)
- Sistema premium com pin de acesso
- Nutri News (feed de noticias IA)
- Sistema de engajamento (gamificacao)
- Painel admin completo com moderacao
- Fluxo de feedback com fila de moderacao
- Notificacoes push personalizadas
- Design "Gourmet Dark Mode"

## Calibracao CLIP - IMPLEMENTADO
- Thresholds: >=0.90 alta, >=0.50 media, <0.50 rejeicao
- Colecao `calibration_log` (registro leve, sem upload de imagem)
- POST /api/ai/calibration/log: registro automatico de amostras
- DELETE /api/ai/calibration/{id}: deletar amostras individuais
- GET /api/ai/calibration: estatisticas, distribuicao, Youden's J
- Aba "Calibracao CLIP" no Admin com dashboard + botao Deletar

## Normalizacao iOS/Android (2026-04-04) - IMPLEMENTADO
- Resolucao padronizada 1024px max em todas as capturas (tap, auto-scan, galeria)
- Qualidade JPEG padronizada em 85% (antes era 70%)
- Funcao normalizeImage() aplicada no upload de galeria

## Auditoria de Dados (2026-04-04) - CORRIGIDO
- Campos ingleses (ingredients, description) com fallback correto
- Health Score baseado em erros severos apenas (ignora missing_description)
- Endpoint GET /api/admin/audit/low-photos usando dish_storage (R2 real)
- 27 pratos com <=5 fotos identificados

## Padronizacao de Nomes (2026-04-04) - IMPLEMENTADO
- Regra: Maiusculas nas palavras principais, minusculas em artigos/preposicoes
- Sem acentos, sem hifens, sem underscores nos nomes
- Parenteses preservados para agrupar pratos similares
- Abreviacoes c/ e s/ preservadas
- Aplicado em dishes e dish_storage

## Estado Atual
- 191 pratos, 191 com embeddings IA (ViT-B-16)
- 2994 embeddings no indice (max 20/prato)
- 3929+ fotos no Cloudflare R2
- 255 mapeamentos TACO
- 30 pratos A/B nutricionalmente revisados
- Threshold CLIP: 90% alta / 50% media / <50% rejeicao
- Health Score auditoria: 85.1%
- Precisao teste: 100% (20/20 pratos aleatorios, 0 falsos positivos)

## Upcoming Tasks (Aguardando testes no buffet)
- (P0) Usuario testar fotos reais no buffet com modelo ViT-B-16 (reindexado 2026-04-05)
- (P1) Revisao nutricional pratos C-Z
- (P1) Validar notificacoes push
- (P1) Validar referencias/links na tela de resultado

## Future Tasks
- (P1) Refatorar server.py (5K+) e Admin.js (3K+)
- (P2) Integracao Stripe
- (P2) Upload ZIP no admin

## REGRA CRITICA: LOCK do Pipeline ViT-B-16 (2026-04-05)
### NENHUM AGENTE PODE ALTERAR OS SEGUINTES ARQUIVOS/CONFIGS SEM AUTORIZACAO EXPLICITA DO USUARIO:
- /app/backend/ai/embedder.py — modelo, pre-processamento, parametros
- /app/backend/ai/index.py — logica de similaridade, thresholds, penalidades
- /app/datasets/dish_index.json — indice de pratos
- /app/datasets/dish_index_embeddings.npy — vetores de embedding
- Nao trocar modelo (ViT-B-16 DataComp.XL), nao alterar dimensao (512), nao mudar normalizacao
- Nao rodar reindex sem autorizacao do usuario
- Pequenos ajustes de threshold ou logica de resposta sao permitidos APENAS se o usuario pedir
- Esta versao foi validada com 100% de precisao (20/20 pratos, 0 falsos positivos)

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt (iframe bloqueia)
- Imagens 2-4MB - sempre usar thumbnails no admin
- Usar xhrGet/xhrPost/xhrDelete no Admin.js
- Storage definitivo: Cloudflare R2
- Cibi Sana: CLIP ONLY, Gemini HARD LOCK
- Fonte de verdade para fotos: colecao dish_storage (R2), NAO disco local
