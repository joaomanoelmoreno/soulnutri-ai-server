# SoulNutri - Resumo de Problemas Críticos (29/01/2026)

## ⚠️ SITUAÇÃO ATUAL: APP NÃO ESTÁ PRONTO PARA PRODUÇÃO

O cliente está extremamente frustrado com a quantidade de problemas e o gasto excessivo de créditos em correções que não resolvem os problemas fundamentais.

---

## 🔴 PROBLEMAS CRÍTICOS NÃO RESOLVIDOS

### 1. RECONHECIMENTO DE PRATOS MUITO RUIM
- **Sintoma**: Espaguete reconhece como "arroz com frutas", bolinho de bacalhau como "molho sugo", cocada confunde com camarão
- **Causa raiz**: Em produção (sem GPU), o sistema usa Gemini para identificar pratos, que:
  - É CARO (gasta créditos a cada identificação)
  - É LENTO (~3-13 segundos)
  - ERRA MUITO (não conhece pratos específicos do buffet)
- **Google Vision NÃO resolve**: Retorna labels genéricos como "Food", "Rice" - não identifica "Bolinho de Bacalhau"
- **PRECISA**: Pesquisar APIs específicas de reconhecimento de alimentos (LogMeal, Passio, Foodvisor)

### 2. CÂMERA INSTÁVEL
- **Sintoma**: Trava frequentemente, precisa fechar e abrir navegador várias vezes
- **Correção parcial aplicada**: Melhorado gerenciamento de estado com refs
- **Status**: Precisa validar se resolveu

### 3. CORREÇÕES DO ADMIN NÃO PERSISTEM
- **Sintoma**: Usuário faz correções no /admin mas elas não aparecem no app
- **Correção aplicada**: Adicionados campos de alérgenos no endpoint
- **Status**: Precisa validar

### 4. INFORMAÇÕES DOS PRATOS ERRADAS
- **Nomes sem espaços**: "Cestinhadecamarao" em vez de "Cestinha de Camarão"
- **Calorias inconsistentes**: Cestinha de camarão (com massa folhada, creme de leite) mostra 99 kcal
- **Categorias erradas**: Salada com queijo marcada como vegano
- **Correção parcial**: Script corrigiu 123 pratos, mas precisa revisão manual

### 5. ALERGENOS NÃO DETECTADOS
- **Sintoma**: Prato com camarão, queijo, leite, peixe, trigo mostra "Nenhum alérgeno detectado"
- **Causa**: Flags de alérgenos não estão sendo calculadas corretamente

### 6. FUNCIONALIDADES PREMIUM INCOMPLETAS
- **Contador de calorias no rodapé não funciona**
- **Faltam**: notícias, combinações, "você sabia", ficha nutricional completa
- **Análise personalizada do prato não existe** (deveria tratar cliente pelo nome e comentar escolhas)
- **Paleta de cores inconsistente** entre telas

### 7. DETECTA COMIDA EM QUALQUER COISA
- **Sintoma**: Fotografa carro/chão/caixa e identifica como alimento com score alto
- **Correção aplicada**: Threshold de 25% para "não parece alimento"
- **Status**: Precisa validar

---

## 💰 PROBLEMA DE CUSTOS

O cliente está muito preocupado com:
1. **Gemini consome créditos a cada reconhecimento** - inviável para escala
2. **Créditos gastos em correções que não funcionam**
3. **Soluções implementadas sem pesquisa prévia adequada**

### CITAÇÃO DO CLIENTE:
> "Não posso trabalhar com uma ferramenta que diz 'é comida'. Como assim???? O app é exatamente um identificador de comidas."

---

## 📋 O QUE PRECISA SER FEITO

### PRIORIDADE 1: Resolver Reconhecimento
1. **PESQUISAR ANTES DE IMPLEMENTAR** - APIs específicas de food recognition:
   - LogMeal (credit-based, 1 crédito por imagem)
   - Passio Nutrition AI
   - Foodvisor
   - Clarifai Food Model
2. Comparar: custo, precisão, velocidade
3. Apresentar opções ao cliente ANTES de implementar

### PRIORIDADE 2: Estabilizar App
1. Validar correção da câmera
2. Garantir que admin salva corretamente
3. Testar detecção de "não é comida"

### PRIORIDADE 3: Corrigir Dados
1. Revisar todas as fichas de pratos
2. Corrigir nomes, calorias, categorias, alérgenos
3. Cliente vai enviar fotos novas para melhorar dataset

### PRIORIDADE 4: Completar Premium
1. Contador de calorias
2. Análise personalizada
3. Informações faltantes

---

## 🚫 O QUE NÃO FAZER

1. **NÃO implementar soluções sem pesquisar antes**
2. **NÃO usar Gemini para reconhecimento** (caro, lento, impreciso)
3. **NÃO usar Google Vision** (só detecta labels genéricos)
4. **NÃO gastar créditos em testes** - pesquisar documentação primeiro

---

## 📁 ARQUIVOS IMPORTANTES

- `/app/backend/server.py` - Lógica principal da API
- `/app/backend/ai/embedder.py` - Sistema de embeddings (problema central)
- `/app/backend/services/google_vision_service.py` - Fallback atual (não resolve)
- `/app/frontend/src/App.js` - Frontend principal (câmera, exibição)
- `/app/frontend/src/Admin.js` - Painel admin
- `/app/datasets/organized/` - Dataset de pratos

---

## 📊 MÉTRICAS ATUAIS

- **Total pratos no índice**: 301
- **Total embeddings**: 1321
- **Precisão atual**: MUITO BAIXA em produção
- **Tempo de resposta**: 3-13 segundos (inaceitável)
- **Custo por reconhecimento**: Alto (usa Gemini)

---

## ✅ O QUE FOI CORRIGIDO NESTA SESSÃO

1. Bug da câmera (gerenciamento de estado)
2. Script de correção de nomes/categorias (123 pratos)
3. Endpoint admin com todos os campos de alérgenos
4. Threshold para "não é comida" (< 25%)
5. Prompt do Gemini com contexto de buffet brasileiro
6. Contador de uso do Google Vision no admin

**MAS** o problema fundamental do reconhecimento NÃO foi resolvido.
