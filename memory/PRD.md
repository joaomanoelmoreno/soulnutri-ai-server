# SoulNutri - Product Requirements Document

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-32) para embedding de imagens
- Storage: Hibrido - Object Storage (S3) via Emergent + disco local
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
- Thumbnails via Pillow (300x300, JPEG 60%) - reducao de 207x no tamanho (3MB -> 14KB)
- Todos os endpoints de imagem agora usam ?thumb=1 no grid e galeria de edicao
- Paginacao com 30 pratos por pagina + lazy loading

### Botao Mover Imagens
- Substituido input de texto por dropdown/select com todos os pratos existentes
- Backend valida se prato destino existe antes de mover
- Contagens atualizadas no frontend apos mover

### Sistema de Notificacao Inline
- 48 chamadas alert() substituidas por notify() com toast inline
- Notificacoes aparecem no canto superior direito com cores por tipo (sucesso/erro/info)
- Resolve problema de alert() bloqueado no iframe da Emergent

### Validacoes de Backend
- DELETE retorna 404 para imagens inexistentes (antes retornava 200)
- MOVE retorna 404 para imagens fonte inexistentes
- Contagem de imagens (dish-images-list) agora usa len(images) real em vez de campo count potencialmente desatualizado
- get_dish_image_bytes nao retorna imagem aleatoria quando filename especifico nao existe

### Restauracao de Dados
- 2 pratos restaurados do nutrition_sheets (abobora-ao-curry, tabule-de-trigo)
- Total: 192/206 pratos COM ingredientes, 14 SEM (sem dados disponiveis no backup)
- 0/206 pratos com descricao (nunca foram populados em nenhuma fonte)

## Estado Atual do Storage
- Cloud (S3): 99 pratos migrados
- Local (disco): 107 pratos
- Object Storage S3 da Emergent: INDISPONIVEL (retorna 500 em uploads)
- Sistema hibrido funcionando: busca na nuvem primeiro, fallback para disco

## Pending Issues
- (P0) BLOQUEADO: Migracao dos 107 pratos restantes (S3 da Emergent dando 500)
- (P1) 14 pratos sem ingredientes - precisam ser preenchidos manualmente ou via IA
- (P1) 206 pratos sem descricao - nunca populado de nenhuma fonte
- (P2) Categorias nao editaveis na aba "Auditoria"
- (P2) Saldo de creditos invisivel na UI da plataforma (problema da Emergent, nao do app)

## Upcoming Tasks
- Validar sistema de notificacoes push
- Atualizar dados nutricionais com safe_nutrition_updater.py
- Validar funcionalidade de adicionar referencias/links na tela de resultado
- Investigar lentidao intermitente no MongoDB (Shard 02 Timeout)

## Future Tasks
- Refatorar server.py (>5000 linhas) e Admin.js (>3000 linhas) em modulos menores
- Integracao Stripe para premium
- Upload ZIP pelo admin

## Key API Endpoints
- GET /api/admin/dishes-full: Lista metadados dos pratos (sem imagens)
- GET /api/admin/dishes/{slug}/images: Lista imagens ao abrir edicao
- GET /api/admin/dish-image/{slug}?thumb=1: Thumbnail comprimido (14KB)
- POST /api/admin/move-image: Move imagem entre pratos (com validacao)
- DELETE /api/admin/dish-image/{slug}?img=X: Deleta imagem (com validacao 404)
- PUT /api/admin/dishes/{slug}: Salva dados do prato

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt (iframe da Emergent bloqueia)
- Imagens sao enormes (2-4MB) - sempre usar thumbnails no admin
- Object Storage pode ficar instavel - manter fallback local
