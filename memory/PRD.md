# SoulNutri - Product Requirements Document

## Visão
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

O SoulNutri é um agente de nutrição virtual que acompanha o cliente em TEMPO REAL durante as refeições, fornecendo informações científicas, alertas personalizados e educação nutricional.

---

## Funcionalidades por Versão

### 🆓 VERSÃO GRATUITA
- Identificação de pratos por imagem
- Nome, categoria e ingredientes do prato
- Alérgenos básicos
- Modo Multi-Item (buffet)

### ⭐ VERSÃO PREMIUM
**Exclusivo Premium - Alertas em Tempo Real:**
- ✅ Informações científicas (curiosidade, benefício, referência)
- ✅ Alertas de alérgenos baseados no PERFIL do usuário
- ✅ Alertas de nutrientes baseados no HISTÓRICO semanal
  - Ex: "Este prato tem 800mg de sódio. Você já consumiu 1500mg esta semana!"
- ✅ Combinações inteligentes
  - Ex: "Combine feijão com limão para absorver 6x mais ferro!"
- ✅ Substituições saudáveis
  - Ex: "Troque batata frita por batata assada: 70% menos gordura"
- ✅ Meta calórica automática (Harris-Benedict)
- ✅ Contador nutricional diário
- ✅ Histórico de consumo

**Educação Nutricional (implementado no backend):**
- Combinações que melhoram absorção
- Substituições mais saudáveis
- Rastreamento de nutrientes: sódio, açúcar, fibras, proteínas

---

## Status Atual (Janeiro 2026)

### Implementado
- [x] Identificação em cascata (OpenCLIP + Gemini Vision)
- [x] Login com Nome + PIN
- [x] Perfil com dados físicos e alergias
- [x] Meta calórica calculada
- [x] Contador nutricional diário
- [x] **Alertas Premium em tempo real**
- [x] **Combinações inteligentes**
- [x] **Substituições saudáveis**
- [x] **Info científica só para Premium**

### Pendente
- [ ] Receitas saudáveis (vegan, vegetariano, práticas)
- [ ] Histórico semanal com gráficos
- [ ] Gamificação (conquistas)
- [ ] Interações medicamentosas

---

## Limites Nutricionais Configurados (OMS/ANVISA)

| Nutriente | Limite Diário | Tipo |
|-----------|---------------|------|
| Sódio | 2000mg | máximo |
| Açúcar | 25g | máximo |
| Gordura Saturada | 22g | máximo |
| Fibras | 25g | mínimo |
| Proteínas | 50g | mínimo |

---

## Arquitetura

### Backend
- FastAPI + MongoDB
- Serviços: `profile_service.py`, `alerts_service.py`, `generic_ai.py`

### Frontend
- React com componentes Premium
- LocalStorage para sessão (nome + PIN)

### Fluxo Premium
1. Usuário faz login (nome + PIN)
2. Ao identificar prato, envia credenciais
3. Backend verifica se é Premium
4. Se sim, retorna dados científicos + alertas personalizados
5. Frontend exibe alertas em tempo real

---

## Endpoints

| Endpoint | Premium? | Descrição |
|----------|----------|-----------|
| `POST /api/ai/identify` | Parcial | Retorna alertas Premium se autenticado |
| `POST /api/premium/register` | - | Criar perfil |
| `POST /api/premium/login` | - | Login nome + PIN |
| `POST /api/premium/log-meal` | Sim | Registrar refeição |
| `GET /api/premium/daily-summary` | Sim | Resumo do dia |
| `GET /api/premium/history` | Sim | Histórico semanal |

---

## URL
https://plate-radar.preview.emergentagent.com
