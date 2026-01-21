# SoulNutri - Product Requirements Document

## ATENÇÃO: Leia também /app/memory/DIRETRIZES_PROJETO.md para contexto completo!

---

## Visão e Posicionamento

### Slogan
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

### Proposta de Valor
O SoulNutri é um **agente de nutrição virtual** que acompanha o cliente em todas as suas refeições, fornecendo informações **CIENTÍFICAS, RELEVANTES e RECENTES** que ele NÃO conhece.

### Disclaimer Legal
> "As informações são educativas e baseadas em pesquisas científicas. Não substituem orientação de profissionais de saúde."

---

## Arquitetura de Reconhecimento (APROVADA)

### Sistema Híbrido em 3 Níveis

**NÍVEL 1 - Índice Local (OpenCLIP)**
- Custo: $0 | Velocidade: ~200ms | Precisão: 95%+
- Se confiança >= 90% → RESULTADO FINAL
- Se confiança < 90% → Nível 2

**NÍVEL 2 - IA Especializada (LogMeal API)** ← A IMPLEMENTAR
- Custo: Free tier | Velocidade: ~500ms | Precisão: 93-98%
- Se confiança >= 85% → RESULTADO FINAL
- Se confiança < 85% → Nível 3

**NÍVEL 3 - IA Genérica (GPT-4o Vision)**
- Custo: ~$0.01-0.02 | Velocidade: ~1-2s
- Fallback universal, sempre retorna resultado

---

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32)
- **Database**: MongoDB (soulnutri)
- **IA**: GPT-4o Vision (via Emergent LLM Key)
- **A integrar**: LogMeal API

---

## Status Atual (Janeiro 2026)

### Base de Dados
- **Total de pratos**: 115
- **Com dados científicos**: 115 (100%)
- **Veganos**: 43 | **Vegetarianos**: 30 | **Proteína animal**: 42

### Funcionalidades Implementadas
- [x] Identificação por imagem (139 pratos no índice)
- [x] Sistema de feedback (correto/incorreto)
- [x] Cadastro de pratos novos com IA
- [x] IA genérica para pratos não cadastrados
- [x] Informações científicas em todos os pratos
- [x] Botão de compartilhar curiosidade
- [x] Câmera com moldura guia

---

## Backlog Priorizado

### P0 - CRÍTICO (Próxima Implementação)
- [ ] Integrar LogMeal API (Nível 2 do sistema híbrido)
- [ ] Implementar lógica de cascata para 100% precisão
- [ ] Investigar travamentos do app

### P1 - ALTA
- [ ] Teste com 3-4 usuários simultâneos
- [ ] Melhorar índice local (mais fotos)
- [ ] Validação cruzada Nível 1 + Nível 2

### P2 - MÉDIA
- [ ] Painel para restaurantes cadastrarem pratos
- [ ] Link "Veja esta pesquisa" na UI
- [ ] Retreinar índice com fotos de feedback

### P3 - FUTURO (Premium)
- [ ] Contador nutricional em tempo real
- [ ] Perfil do usuário (médico/alergias/restrições)
- [ ] Histórico de consumo semanal
- [ ] Alertas personalizados

---

## Endpoints Principais

- `POST /api/ai/identify` - Identifica prato por imagem
- `POST /api/ai/feedback` - Registra feedback
- `POST /api/ai/create-dish` - Cria novo prato com IA
- `GET /api/ai/dishes` - Lista pratos
- `GET /api/ai/status` - Status do índice

---

## URL de Preview
https://nutriwaze.preview.emergentagent.com
