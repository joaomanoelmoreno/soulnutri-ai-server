# SoulNutri - Product Requirements Document

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-32) para embedding de imagens
- Storage: Cloudflare R2 (bucket: soulnutri-images) - 3939 fotos migradas
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

## Correcoes Realizadas (2026-03-27)

### Performance Admin
- Thumbnails via Pillow (300x300, JPEG 60%) - reducao de 207x (3MB -> 14KB)
- Todos os img tags do admin usam ?thumb=1
- Paginacao com 30 pratos por pagina + lazy loading

### Botao Mover Imagens
- Input texto substituido por dropdown/select com todos os pratos
- Backend valida se prato destino existe antes de mover
- Contagens atualizadas no frontend apos mover

### Sistema de Notificacao Inline
- 48 chamadas alert() substituidas por notify() com toast inline
- Resolve alert() bloqueado no iframe da Emergent

### Validacoes de Backend
- DELETE/MOVE retornam 404 para imagens inexistentes
- Contagem usa len(images) real
- get_dish_image_bytes nao retorna imagem aleatoria para filename inexistente

### Sincronizacao de Dados
- dish_storage sincronizado com arquivos reais no disco (4 counts corrigidos)
- _find_local_folder melhorado: pula pastas vazias, normaliza parenteses
- 2 pratos restaurados do nutrition_sheets (abobora-ao-curry, tabule-de-trigo)
- Botao Editar agora carrega galeria de imagens (antes nao carregava)

## Migracao Cloudflare R2 (2026-03-30) - VALIDADO
- 3939 imagens migradas com sucesso para bucket soulnutri-images
- r2_service.py criado com boto3 para integracao nativa
- image_service.py refatorado para rotear todos os requests para R2
- Thumbnails gerados on-the-fly com Pillow (300x300, JPEG 60%)
- Testes automatizados: 12/12 backend, frontend 100% - PASS

## Estado Atual
- 196 pratos totais (189 com embeddings AI)
- 3939 fotos no Cloudflare R2
- 1632 embeddings de imagem no indice
- 192 com ingredientes
- 0 com descricao (nunca foi populado)
- Object Storage Emergent: ABANDONADO (erro 500)

## Pending Issues
- (P1) 14 pratos sem ingredientes
- (P1) 206 pratos sem descricao
- (P2) Categorias nao editaveis na aba Auditoria

## Upcoming Tasks
- (P1) Validar notificacoes push
- (P1) Atualizar dados nutricionais com safe_nutrition_updater.py
- (P1) Validar referencias/links na tela de resultado

## Future Tasks
- (P1) Refatorar server.py (5K+ linhas) e Admin.js (3K+ linhas)
- (P2) Integracao Stripe para premium
- (P2) Upload ZIP pelo admin
- (P2) Investigar lentidao intermitente MongoDB

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt (iframe da Emergent bloqueia)
- Imagens 2-4MB - sempre usar thumbnails no admin
- Usar xhrGet/xhrPost/xhrDelete no Admin.js (fetch falha silenciosamente)
- Storage definitivo: Cloudflare R2 (NAO usar Emergent S3)
