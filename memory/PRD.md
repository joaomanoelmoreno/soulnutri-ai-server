# SoulNutri - Product Requirements Document

## Visão e Posicionamento

### Slogan
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

### Proposta de Valor
O SoulNutri é um **agente de nutrição virtual** que acompanha o cliente em todas as suas refeições, fornecendo informações **CIENTÍFICAS, RELEVANTES e RECENTES** que ele NÃO conhece.

---

## Funcionalidades Implementadas

### ✅ Identificação de Pratos (Core)
- **Sistema em Cascata**: OpenCLIP (Nível 1, 95% threshold) + Gemini Vision (Nível 3)
- **139 pratos indexados** no Cibi Sana
- Identificação de alérgenos automática
- Informações científicas (benefício principal, curiosidade, referência)
- Botão de compartilhar curiosidade

### ✅ Modo Multi-Item (Novo - 22/01/2026)
- Endpoint: `POST /api/ai/identify-multi`
- Identifica múltiplos alimentos em buffets ou pratos compostos
- Mostra calorias individuais e totais
- Indica equilíbrio nutricional da refeição
- Combina alertas de alérgenos de todos os itens

### ✅ Premium com PIN Local (Novo - 22/01/2026)
- **Sistema de Perfil**:
  - Cadastro com PIN (4-6 dígitos)
  - Dados: peso, altura, idade, sexo, nível de atividade
  - Objetivo: perder/manter/ganhar peso
  - Alergias e restrições alimentares
  
- **Contador Nutricional**:
  - Cálculo automático de meta calórica (Harris-Benedict)
  - Registro de refeições identificadas
  - Progresso diário em anel visual
  - Alertas quando próximo da meta (75%, 90%, 100%)
  - Histórico de refeições do dia

- **Endpoints Premium**:
  - `POST /api/premium/register` - Criar perfil
  - `POST /api/premium/login` - Login com PIN
  - `POST /api/premium/log-meal` - Registrar refeição
  - `GET /api/premium/daily-summary` - Resumo do dia
  - `GET /api/premium/history` - Histórico semanal

### ✅ UX/UI
- Câmera com moldura guia
- Tratamento de erro de câmera com botão "Tentar novamente"
- Toggle Único/Multi para alternar modos
- Botão flutuante Premium (⭐ ou 📊 se logado)
- Mini-contador flutuante mostrando progresso do dia

---

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32)
- **Database**: MongoDB (soulnutri)
- **IA**: Gemini Vision (via Emergent LLM Key)

---

## Backlog Priorizado

### P0 - CRÍTICO
- [x] ~~Reconhecimento de múltiplos itens~~ ✅
- [x] ~~Sistema Premium com PIN~~ ✅
- [x] ~~Contador nutricional~~ ✅
- [ ] Validação de precisão com pratos do Cibi Sana (aguardando usuário)

### P1 - ALTA
- [ ] Investigar travamentos ocasionais do app
- [ ] Alertas personalizados baseados nas alergias do perfil (ao identificar prato)
- [ ] Botão compartilhar mais visível na UI

### P2 - MÉDIA
- [ ] Histórico semanal com gráficos
- [ ] Relatórios nutricionais
- [ ] Link "Veja esta pesquisa" para alertas

### P3 - FUTURO
- [ ] Modo offline (PWA)
- [ ] Notificações push
- [ ] Integração com wearables

---

## Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/ai/identify` | POST | Identifica prato único |
| `/api/ai/identify-multi` | POST | Identifica múltiplos itens |
| `/api/ai/feedback` | POST | Registra feedback |
| `/api/ai/create-dish` | POST | Cria novo prato com IA |
| `/api/ai/dishes` | GET | Lista pratos |
| `/api/ai/status` | GET | Status do índice |
| `/api/premium/register` | POST | Criar perfil Premium |
| `/api/premium/login` | POST | Login com PIN |
| `/api/premium/log-meal` | POST | Registrar refeição |
| `/api/premium/daily-summary` | GET | Resumo do dia |
| `/api/premium/history` | GET | Histórico semanal |

---

## URL de Preview
https://nutrivision-39.preview.emergentagent.com
