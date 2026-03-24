# SoulNutri - Product Requirements Document

## Visão
Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens com alta precisão, atuando como um "radar do prato".

## Credenciais
- Admin: joaomanoelmoreno / Pqlamz0192

## Arquitetura
- Frontend: React (CRA) + CSS Custom
- Backend: FastAPI + Motor (MongoDB async)
- AI: OpenCLIP local (ViT-B-32) para embedding de imagens
- Storage: Object Storage (S3) via Emergent integrations
- DB: MongoDB Atlas

## Funcionalidades Implementadas
- Identificação de pratos via câmera/foto
- Ficha nutricional detalhada com dados TACO
- Sistema premium com pin de acesso
- Nutri News (feed de notícias IA)
- Sistema de engajamento (gamificação)
- Painel admin completo com moderação
- Fluxo de feedback com fila de moderação
- Notificações push personalizadas
- Design "Gourmet Dark Mode"

## Correções Realizadas (2026-03-24/25)

### Correção Definitiva Admin - 3 Problemas Raiz
1. **URL absoluta → relativa:** `Admin.js` usava `process.env.REACT_APP_BACKEND_URL/api` que era interferida pelo script Emergent → Corrigido para `const API = '/api'`
2. **React.StrictMode + Emergent script:** O double-mount do StrictMode combinado com o wrapper `window.fetch` do `emergent-main.js` causava corrupção de estado. Solução: Removido StrictMode + migrado data loading para XMLHttpRequest via `xhrGet()` que contorna o wrapper.
3. **Chamadas síncronas bloqueando event loop:** `storage_service.py` e `image_service.py` usavam `requests` (síncrono) e `pymongo` (síncrono) que bloqueavam o event loop do asyncio. Solução: envolvido todas as chamadas com `asyncio.to_thread()`.

### Melhorias de Resiliência
- Retry automático em respostas não-OK (502, 503)
- Lazy loading por aba (carrega dados apenas da aba ativa)
- XHR timeout de 20 segundos por request

## Pending Issues
- (P1) Resultados insatisfatórios nos testes do buffet (aguardando análise)
- (P2) Revisão de dados nutricionais contaminados (aguardando lista)

## Upcoming Tasks
- (P0) Validar notificações push
- (P1) Validar referências/links na tela de resultado
- (P1) Atualização segura de dados nutricionais (pipeline em safe_nutrition_updater.py)

## Future Tasks
- (P1) Refatorar server.py e App.js em módulos menores
- (P2) Integração Stripe para premium
- (P2) Upload ZIP pelo admin
