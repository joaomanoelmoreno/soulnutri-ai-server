# SoulNutri - Product Requirements Document

## Original Problem Statement
Construir o SoulNutri, um aplicativo de "agente de nutricao virtual" que identifica pratos em tempo real a partir de imagens. Foco em precisao maxima (> 90%) e "honestidade" - evitando falsos positivos com alta confianca.

## Core Requirements
1. **Visao:** Radar do prato - seguranca alimentar e informacao nutricional em tempo real
2. **Precisao:** Identificacao precisa, honesta e confiavel. Rejeitar pratos desconhecidos
3. **Qualidade:** Informacoes corretas, educativas e cientificamente embasadas
4. **UX/UI:** Minimo de cliques, fluida, estavel, mensagens claras de confianca
5. **Evolucao Incremental:** Implementar e validar cada etapa isoladamente

## Architecture
- Frontend: React (Admin + App principal)
- Backend: FastAPI (server.py)
- Database: MongoDB (Atlas)
- AI: CLIP local (Hugging Face) + Gemini Flash (fallback)
- Nutrition: USDA API + Open Food Facts + TACO

## What's Been Implemented
- Sistema de reconhecimento de pratos com CLIP + Gemini Flash
- Painel Admin completo com gestao de pratos, auditoria, novidades, premium
- Pipeline de fichas nutricionais (USDA + Open Food Facts + TACO)
- Sistema de cache para identificacoes
- Funcionalidades Premium (alertas, mitos/verdades, dados cientificos)
- Upload de fotos (individual, ZIP, pasta)
- Sistema de metricas de processamento
- 188 pratos no dataset com 1627 imagens

## Prioritized Backlog
### P0 (Critical)
- [DONE] Bug do Admin Panel corrigido - pratos exibidos corretamente

### P1 (High Priority)
- Expandir fichas nutricionais para todos os ~200 pratos
- Monitorar uso de disco e .gitignore para datasets

### P2 (Medium)
- Refatorar server.py e Admin.js
- Integracao Stripe para premium
- Validacao da logica de reconhecimento em ambiente real

## 3rd Party Integrations
- USDA FoodData Central API (chave real configurada)
- Open Food Facts API
- TACO (Tabela Brasileira de Composicao de Alimentos)
- Hugging Face (openai/clip-vit-base-patch32)
- Google Gemini (via emergentintegrations)
- MongoDB Atlas

## Key Endpoints
- GET /api/admin/dishes-full - Lista pratos no Admin
- GET /api/nutrition-sheet/{dish_name} - Ficha nutricional
- POST /api/ai/identify - Identificacao de pratos
- GET /api/ai/status - Status do indice

## DB Collections
- dishes: dados dos pratos
- nutrition_sheets: fichas nutricionais detalhadas
- users: perfis de usuarios
- novidades: noticias dos pratos
- settings: configuracoes
- processing_metrics: metricas

## Last Update: 2026-03-21
- GPS removido completamente do frontend
- Fluxo CLIP/Gemini unificado (sem bloqueio por restaurante)
- 4642 imagens migradas para Emergent Object Storage (188 pratos)
- Popup de permissões atualizado (só câmera)
- Service Worker desregistrado (causava erro postMessage)
- 5 pratos revisados pelo usuario salvos no MongoDB
- 13 + 170 pratos com fichas nutricionais (188/188 total)
