# SoulNutri - Product Requirements Document

## Visao do Produto
Aplicativo de agente de nutricao virtual que identifica pratos em tempo real a partir de imagens, fornecendo informacoes nutricionais detalhadas e personalizadas com alta precisao (> 90%).

## Requisitos Principais
1. **Precisao**: Identificacao precisa, honesta e confiavel
2. **Qualidade**: Informacoes nutricionais cientificamente embasadas
3. **UX/UI**: Interface fluida, bonita e convidativa ("tao atrativo quanto um prato do Cibi Sana")
4. **Evolucao**: Implementacao incremental com estabilidade

## Arquitetura
- **Frontend**: React (App.js + Admin.js + NutritionFeed.jsx + WeeklyReport.jsx + Premium.jsx + DashboardPremium.jsx)
- **Backend**: FastAPI (server.py + services/)
- **Database**: MongoDB Atlas
- **Storage**: Emergent Object Storage (S3) para imagens
- **AI**: CLIP (reconhecimento) + Gemini (fallback + geracao de conteudo)

## O que foi Implementado

### V1.0 - Base
- Reconhecimento de imagem CLIP + Gemini fallback
- Painel Admin, fichas nutricionais (3 fontes: USDA, Open Food Facts, TACO)
- ~188 pratos, ~4700 imagens

### V1.1 - GPS Removido
- Fluxo unificado de reconhecimento

### V1.2 - Migracao S3 (22/Mar/2026)
- Todas imagens migradas para Object Storage (S3)
- Backend refatorado para usar S3 como fonte primaria com fallback local
- Novo servico image_service.py

### V1.3 - Conteudo e Engajamento (23/Mar/2026)
- **Feed de Noticias Nutricionais (Nutri News)**:
  - Geracao de conteudo por IA com verificacao de fontes
  - Fontes confiaveis: WHO, FDA, ANVISA, The Lancet, BMJ, Harvard, Mayo Clinic, BBC, CNN, Reuters, Estadao, VEJA, SuperInteressante
  - Fontes bloqueadas: Fox News, midias sociais nao verificaveis
  - 6 categorias: Curiosidade, Alerta, Dica, Ciencia, Tendencia, Mito vs Fato
  - Balanceamento otimista/realista
  - Verificacao anti-fake news
  - Sistema de likes e views
  - Filtros por categoria
  
- **Relatorio Semanal Premium**:
  - Analise de macros por IA (calorias, proteinas, carboidratos, gorduras)
  - Identificacao de excessos e deficits
  - Pontos positivos, alertas e dicas personalizadas
  - Curiosidade nutricional relevante
  - Mensagem motivacional personalizada
  
- **Programa Motivacional**:
  - 12 badges/conquistas (Primeira Refeicao, Constante, Dedicado, Disciplinado, Habito Formado, Explorador, Aventureiro, Gourmet, Alimentacao Nota A, Nutricao Excelente, Amigo Verde, Equilibrista)
  - Sistema de niveis (7: Iniciante -> Lenda SoulNutri) com XP
  - Streaks de dias consecutivos
  - Mensagens motivacionais contextuais
  - Barras de progresso para cada badge

## Status Atual
- **Funcional**: Reconhecimento, Admin, Upload, Fichas nutricionais, News Feed, Premium com Relatorios, Achievements
- **Indice CLIP**: 189 pratos, 1632 embeddings
- **Engenharia analisando**: Resultados dos testes no buffet

## Backlog

### P0 - Aguardando Engenharia
- Analise dos resultados do teste no buffet
- Nao salvar versao V1.25 ate conclusao da analise

### P1 - Proximo
- Redesign visual do frontend ("bonito como um prato do Cibi Sana")
- Revisao de dados nutricionais contaminados

### P2 - Futuro
- Refatorar server.py (~4500 linhas) e App.js (~3200 linhas) em modulos
- Integracao Stripe para funcionalidades premium
- Endpoint de upload direto de ZIPs
- Gerar lista atualizada de pratos com poucas fotos

## Integracoes
- Emergent Object Storage (S3) - imagens
- USDA FoodData Central API - nutricao
- Open Food Facts API - nutricao
- TACO (local) - nutricao brasileira
- Google Gemini - fallback reconhecimento + geracao de conteudo
- HuggingFace CLIP - reconhecimento primario
- MongoDB Atlas - banco de dados
