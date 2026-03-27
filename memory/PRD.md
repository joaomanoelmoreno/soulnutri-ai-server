# SoulNutri - Product Requirements Document

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-32) para embedding de imagens
- Storage: Hibrido - Object Storage (S3) via Emergent (99 pratos) + disco local (107 pratos)
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

## Estado Atual
- 206 pratos totais
- 204 com imagens (4.854 fotos)
- 192 com ingredientes
- 0 com descricao (nunca foi populado)
- 99 pratos na nuvem (S3), 107 no disco local
- Object Storage UPLOAD indisponivel (erro 500 da plataforma), READ OK

## Pending Issues
- (P0 BLOQUEADO) Migracao completa para S3 - upload da plataforma retorna 500
- (P1) 14 pratos sem ingredientes
- (P1) 206 pratos sem descricao
- (P2) 2 pratos sem nenhuma imagem acessivel (upload original falhou)
- (P2) Categorias nao editaveis na aba Auditoria

## Upcoming Tasks
- Validar notificacoes push
- Atualizar dados nutricionais com safe_nutrition_updater.py
- Validar referencias/links na tela de resultado

## Future Tasks
- Refatorar server.py (5K+ linhas) e Admin.js (3K+ linhas)
- Integracao Stripe para premium
- Upload ZIP pelo admin

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt (iframe da Emergent bloqueia)
- Imagens 2-4MB - sempre usar thumbnails no admin
- Object Storage instavel - manter fallback local
