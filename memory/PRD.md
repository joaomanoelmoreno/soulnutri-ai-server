# SoulNutri - Product Requirements Document

## Visao
Aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens com alta precisao, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-32) para embedding de imagens
- Storage: Object Storage (S3) via Emergent integrations
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

## Correcoes Realizadas (2026-03-24/25)

### Correcao Definitiva Admin - 3 Problemas Raiz
1. **URL absoluta -> relativa:** Admin.js usava process.env.REACT_APP_BACKEND_URL/api -> Corrigido para const API = '/api'
2. **React.StrictMode + Emergent script:** Double-mount + wrapper window.fetch causava corrupcao. Removido StrictMode + migrado para XMLHttpRequest
3. **Chamadas sincronas bloqueando event loop:** storage_service.py e image_service.py usavam requests (sincrono). Corrigido com asyncio.to_thread()

### Melhorias de Resiliencia
- Retry automatico em respostas nao-OK (502, 503)
- Lazy loading por aba
- XHR timeout de 20 segundos

## Auditoria Completa (2026-03-25)

### Relatorio Gerado
- Arquivo: /app/RELATORIO_AUDITORIA_SOULNUTRI.docx
- URL: https://hybrid-storage-dev.preview.emergentagent.com/RELATORIO_AUDITORIA_SOULNUTRI.docx

### 8 Problemas Identificados
1. (CRITICO) 148 slugs corrompidos no MongoDB (ex: aboboraaocurry em vez de abobora-ao-curry)
2. (ALTO) 10 pastas duplicadas no disco (normalizam para o mesmo slug)
3. (CRITICO) 250/250 pratos sem dados nutricionais, ingredientes ou categoria
4. (ALTO) dish_storage completamente vazio (0 documentos)
5. (ALTO) Codigo usa campos em portugues (nome, categoria) mas MongoDB usa ingles (name, category)
6. (MEDIO-ALTO) 113 pastas de imagens sem entrada no MongoDB
7. (MEDIO) 148 pratos fantasmas no MongoDB sem pasta no disco
8. (BAIXO) Pastas de teste/lixo no disco

### Dados Intactos
- 4.903 imagens em 225 pastas no disco - NENHUMA imagem perdida
- Problemas sao de apresentacao/mapeamento, nao de perda de dados

### Status
- AGUARDANDO orientacoes da engenharia do usuario
- NENHUMA alteracao foi feita no codigo ou dados

## Plano de Correcao Proposto (aguardando aprovacao)
- Fase 1: Backup + scripts de validacao (sem risco)
- Fase 2: Correcoes no codigo sem mexer dados (nomes de campos, logica de leitura)
- Fase 3: Correcoes nos dados com aprovacao explicita (slugs, pastas duplicadas, fantasmas)

## Pending Issues
- (P0) Todos os 8 problemas da auditoria - AGUARDANDO orientacoes
- (P1) Resultados insatisfatorios nos testes do buffet
- (P2) Categorias nao editaveis na aba Auditoria

## Upcoming Tasks (pos-aprovacao)
- Corrigir incompatibilidade de campos no codigo
- Corrigir logica de pastas duplicadas
- Corrigir slugs corrompidos no MongoDB
- Validar notificacoes push
- Atualizacao segura de dados nutricionais

## Future Tasks
- Refatorar server.py e App.js em modulos menores
- Integracao Stripe para premium
- Upload ZIP pelo admin
