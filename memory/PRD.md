# SoulNutri - Product Requirements Document

## Visao do Produto
Aplicativo de agente de nutricao virtual que identifica pratos em tempo real a partir de imagens. Fornece informacoes nutricionais detalhadas e personalizadas. Deve ser "tao atrativo quanto um prato do Cibi Sana" - bonito, convidativo e atraente.

## Requisitos Principais
1. Precisao: Identificacao confiavel (rejeita pratos desconhecidos)
2. Qualidade: Informacoes nutricionais com fontes verificaveis
3. UX/UI: Interface gourmet, fluida e convidativa
4. Engajamento: Conteudo relevante e personalizado, programa motivacional
5. Fontes: Todas as informacoes devem citar fontes confiaveis com links

## Arquitetura
- Frontend: React (App.js, Admin.js, NutritionFeed.jsx, WeeklyReport.jsx, Premium.jsx, DashboardPremium.jsx)
- Backend: FastAPI (server.py + services/)
- Database: MongoDB Atlas
- Storage: Emergent Object Storage (S3)
- AI: CLIP (reconhecimento) + Gemini (fallback + conteudo)
- Fonts: Playfair Display (titulos) + DM Sans (corpo)

## Implementado

### V1.0 - Base
- Reconhecimento CLIP + Gemini fallback
- Admin, fichas nutricionais (USDA, Open Food Facts, TACO)
- ~188 pratos, ~4700 imagens

### V1.1 - GPS Removido
- Fluxo unificado de reconhecimento

### V1.2 - Migracao S3 (22/Mar/2026)
- Imagens migradas para Object Storage (S3)
- Backend refatorado (image_service.py)

### V1.3 - Conteudo e Engajamento (23/Mar/2026)
- Feed Nutri News: Geracao IA com verificacao de fontes (WHO, FDA, ANVISA, Lancet, BBC, CNN, Harvard, etc.)
- Fontes bloqueadas: Fox News, midias sociais
- 6 categorias: Curiosidade, Alerta, Dica, Ciencia, Tendencia, Mito vs Fato
- Balanceamento otimista/realista, verificacao anti-fake news
- Links clicaveis para fontes originais
- Relatorio Semanal Premium: Analise IA de macros, excessos, deficits, dicas
- Programa Motivacional: 12 badges, 7 niveis, XP, streaks, mensagens contextuais
- Redesign visual: Paleta navy (#0f172a), glassmorphism, Playfair Display + DM Sans

## Status Atual
- Funcional: Reconhecimento, Admin, Upload, News Feed, Premium, Achievements
- Indice CLIP: 189 pratos, 1632 embeddings
- 14 artigos de noticias gerados
- Engenharia analisando resultados do teste no buffet

## Backlog

### P0 - Aguardando Engenharia
- Analise dos resultados do teste no buffet
- Nao salvar V1.25 ate conclusao

### P1 - Proximo
- Notificacoes push personalizadas (max 1/dia, baseadas no consumo do usuario)
- Revisao de dados nutricionais contaminados
- Adicionar referencia/link em alertas de identificacao de pratos

### P2 - Futuro
- Refatorar server.py e App.js em modulos menores
- Integracao Stripe para premium
- Upload direto de ZIPs
- Gerar lista de pratos com poucas fotos

## Integracoes
- Emergent Object Storage (S3)
- USDA FoodData Central API
- Open Food Facts API
- TACO (local)
- Google Gemini
- HuggingFace CLIP
- MongoDB Atlas
