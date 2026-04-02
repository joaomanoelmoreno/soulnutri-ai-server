# SoulNutri - Product Requirements Document

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-32) para embedding de imagens
- Storage: Cloudflare R2 (bucket: soulnutri-images) - 3929 fotos
- DB: MongoDB Atlas

## Funcionalidades Implementadas
- Identificacao de pratos via camera/foto
- Ficha nutricional detalhada com dados TACO
- Sistema premium com pin de acesso
- Nutri News (feed de noticias IA)
- Sistema de engajamento (gamificacao)
- Painel admin completo com moderacao
- Fluxo de feedback com fila de moderacao
- Notificacoes push personalizadas
- Design "Gourmet Dark Mode"

## Correcoes Realizadas Anteriormente
- Thumbnails via Pillow (300x300, JPEG 60%) - reducao de 207x
- Botao Mover com dropdown + XHR
- 48 alert() substituidos por notify() inline
- dish_storage sincronizado com R2

## Migracao Cloudflare R2 - CONCLUIDO
- 3929 imagens no bucket soulnutri-images
- r2_service.py + image_service.py refatorados
- Testes 12/12 backend PASS

## Correcoes 2026-04-01

### Auditoria Corrigida
- audit_service.py agora usa MongoDB como fonte de verdade (antes usava filesystem)
- Normalizacao de nomes de pastas para match com slugs do banco
- Deduplicacao: cada prato auditado apenas uma vez
- Botao Editar adicionado aos itens "sem dish_info.json"
- Stats do admin agora mostra count real do DB (190), nao do indice IA (189)
- Resultado: 190 pratos auditados, 93.2% saude, 13 com problemas

### Indice IA Limpo
- Removidos 12 pratos obsoletos (teste/fantasma)
- Consolidadas 10 entradas duplicadas
- De 212 -> 189 pratos IA unicos, 1701 embeddings

### Revisao Nutricional A e B - CONCLUIDO
- 255 mapeamentos INGREDIENTE_PARA_TACO corrigidos (63 estavam quebrados)
- 13 entradas adicionadas ao TACO_DATABASE (canela, gengibre, curry, alho, vinagre, etc.)
- 30 pratos atualizados com proporcoes reais do Gemini Flash + dados TACO
- Metodo: Gemini determina proporcoes culinarias reais por 100g, TACO calcula nutricao
- Divergencias graves corrigidas: Atum ao Gergelim 28->227kcal, Babaganoush 31->170kcal, etc.

### Upload Cocada
- 6 fotos de cocada enviadas para R2 (total: 7 fotos)

## Estado Atual
- 190 pratos no banco (189 com embeddings IA)
- 3929 fotos no Cloudflare R2
- 1701 embeddings de imagem
- 255 mapeamentos de ingredientes TACO
- 30 pratos A/B com nutricao revisada
- beringela-a-parmegiana: sem ingredientes (possivel duplicata)

## Upcoming Tasks
- (P1) Revisao nutricional pratos C-Z (mesmo metodo: Gemini proporcoes + TACO)
- (P1) Validar notificacoes push
- (P1) Validar referencias/links na tela de resultado

## Future Tasks
- (P1) Refatorar server.py (5K+ linhas) e Admin.js (3K+ linhas)
- (P2) Integracao Stripe para premium
- (P2) Upload ZIP no admin
- (P2) Categorias nao editaveis na aba Auditoria
- (P2) Investigar lentidao MongoDB

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt (iframe bloqueia)
- Imagens 2-4MB - sempre usar thumbnails no admin
- Usar xhrGet/xhrPost/xhrDelete no Admin.js
- Storage definitivo: Cloudflare R2
