# SoulNutri - Product Requirements Document

## Visao do Produto
Aplicativo de agente de nutricao virtual que identifica pratos em tempo real a partir de imagens, fornecendo informacoes nutricionais detalhadas e personalizadas com alta precisao (> 90%).

## Requisitos Principais
1. **Precisao**: Identificacao precisa, honesta e confiavel (rejeita pratos que nao conhece)
2. **Qualidade**: Informacoes nutricionais corretas e cientificamente embasadas
3. **UX/UI**: Interface fluida com minimo de cliques
4. **Evolucao**: Implementacao incremental com foco em estabilidade

## Arquitetura
- **Frontend**: React (App.js + Admin.js)
- **Backend**: FastAPI (server.py)
- **Database**: MongoDB Atlas
- **Storage**: Emergent Object Storage (S3-compativel) para imagens
- **AI**: CLIP (openai/clip-vit-base-patch32) + Gemini (fallback)

## O que foi implementado

### V1.0 - Base
- Reconhecimento de imagem com CLIP local + Gemini fallback
- Painel Admin para gerenciamento de pratos
- Fichas nutricionais com dados de 3 fontes (USDA, Open Food Facts, TACO)
- ~188 pratos cadastrados com fichas nutricionais

### V1.1 - Migracao GPS Removido
- Remocao completa de logica de geolocalizacao
- Fluxo unificado de reconhecimento para todos os usuarios

### V1.2 - Migracao S3 (22/Mar/2026)
- Migracao de ~4700 imagens para Object Storage (S3)
- Importacao de 90 novas fotos de 3 arquivos ZIP
- Reconstrucao do indice CLIP (189 pratos, 1632 embeddings)
- **Refatoracao do backend para usar S3 como fonte primaria de imagens**:
  - `/api/admin/dish-image/{slug}` - Serve imagens do S3 com fallback local
  - `/api/admin/dishes` e `/api/admin/dishes-full` - Lista pratos do MongoDB
  - `/api/upload/status` - Estatisticas do MongoDB dish_storage
  - Upload endpoints - Salvam no S3 + MongoDB + disco local (cache)
  - Create/feedback endpoints - Salvam no S3 + MongoDB
  - Review endpoints - Leem/salvam no MongoDB ao inves de dish_info.json
  - Normalizacao de slugs entre collections (dishes usa snake_case, dish_storage usa Title Case)
- Novo servico `image_service.py` para abstracacao de operacoes com imagens

## Status Atual
- **Funcional**: Reconhecimento de imagem, Admin, Upload, Fichas nutricionais
- **Indice CLIP**: 189 pratos, 1632 embeddings, pronto para buscas
- **Imagens**: 4660+ no S3, fallback local disponivel

## Backlog

### P1 - Proximo
- Revisao de dados nutricionais contaminados (carpaccio de laranja, carpaccio de abobrinha, bolo vegano de chocolate, polenta com ragu)
- Salvar versao V1.25 apos validacao do usuario
- Implementar endpoints faltantes no Admin (api-usage, premium-users, settings)

### P2 - Futuro
- Refatorar server.py (~4400 linhas) e App.js (~3200 linhas) em modulos
- Integracao Stripe para funcionalidades premium
- Gerar lista atualizada de pratos com poucas fotos
- Endpoint para upload direto de ZIPs pelo usuario

## Integracoes
- Emergent Object Storage (S3) - imagens
- USDA FoodData Central API - nutricao
- Open Food Facts API - nutricao
- TACO (local) - nutricao brasileira
- Google Gemini - fallback reconhecimento
- HuggingFace CLIP - reconhecimento primario
- MongoDB Atlas - banco de dados
