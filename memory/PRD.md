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

## Calibracao CLIP (2026-04-02/03) - IMPLEMENTADO
- Gap analysis removido: decisao baseada apenas em score absoluto
- Thresholds sincronizados: >=0.85 alta, >=0.50 media, <0.50 rejeicao
- Auto-aceite CLIP: de 0.90 para 0.85
- Colecao `calibration_log` separada da `feedback` (registro leve, sem upload de imagem)
- POST /api/ai/calibration/log: registro automatico de amostras (Sim e Nao)
- DELETE /api/ai/calibration/{id}: deletar amostras individuais
- GET /api/ai/calibration: estatisticas, distribuicao, Youden's J
- Aba "Calibracao CLIP" no Admin com dashboard + botao Deletar por amostra
- Frontend: ambos botoes "Sim, esta correto" e "Nao, tentar novamente" registram na calibracao

## Correcoes Recentes (2026-04-01/02)

### Hard Lock Cibi Sana (2026-04-02)
- /ai/identify: restaurant=cibi_sana -> CLIP only, Gemini bloqueado
- /ai/identify-with-ai: restaurant=cibi_sana -> 403 bloqueado
- /ai/identify-flash: restaurant=cibi_sana -> 403 bloqueado
- Logs [HARD LOCK] para rastreabilidade

### Auditoria Corrigida
- audit_service.py usa MongoDB como fonte de verdade
- Stats admin mostra count real do DB (190)
- Botao Editar adicionado em itens sem dish_info.json

### Revisao Nutricional A e B
- 30 pratos atualizados com proporcoes Gemini + TACO
- 255 mapeamentos TACO corrigidos (63 quebrados)
- 13 alimentos adicionados ao banco TACO

### Indice IA Limpo
- 12 pratos obsoletos removidos, 10 duplicatas consolidadas
- 189 pratos IA, 1701 embeddings

## Estado Atual
- 190 pratos, 189 com embeddings IA
- 3929 fotos no Cloudflare R2
- 255 mapeamentos TACO
- 30 pratos A/B nutricionalmente revisados
- Thresholds CLIP: 85% alta / 50% media / <50% rejeicao (sem gap analysis)

## Upcoming Tasks
- (P0) Usuario testar fotos reais no buffet e coletar amostras para calibracao Youden
- (P1) Revisao nutricional pratos C-Z
- (P1) Validar notificacoes push
- (P1) Validar referencias/links na tela de resultado

## Future Tasks
- (P1) Refatorar server.py (5K+) e Admin.js (3K+)
- (P2) Integracao Stripe
- (P2) Upload ZIP no admin
- (P2) Categorias nao editaveis na aba Auditoria

## Restricoes Tecnicas
- NAO usar window.alert/confirm/prompt (iframe bloqueia)
- Imagens 2-4MB - sempre usar thumbnails no admin
- Usar xhrGet/xhrPost/xhrDelete no Admin.js
- Storage definitivo: Cloudflare R2
- Cibi Sana: CLIP ONLY, Gemini HARD LOCK
