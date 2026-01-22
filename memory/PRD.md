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

## Arquitetura de Reconhecimento (IMPLEMENTADA)

### Sistema Híbrido em 3 Níveis

**NÍVEL 1 - Índice Local (OpenCLIP)**
- Custo: $0 | Velocidade: ~200ms | Precisão: 95%+
- Se confiança >= 95% → RESULTADO FINAL
- Se confiança < 95% → Nível 3

**NÍVEL 2 - IA Especializada (Clarifai)**
- Status: DESABILITADO (código implementado, mas desativado por custo)
- Pode ser reativado quando necessário

**NÍVEL 3 - IA Genérica (Gemini Vision)**
- Custo: via Emergent LLM Key | Velocidade: ~1-2s
- Fallback universal, sempre retorna resultado

---

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32)
- **Database**: MongoDB (soulnutri)
- **IA**: Gemini Vision (via Emergent LLM Key)

---

## Status Atual (Janeiro 2026)

### Base de Dados
- **Total de pratos**: 139 no índice
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
- [x] **NOVO: Modo Multi-Item** - Identifica múltiplos alimentos no prato

### Última Implementação (22/01/2026)
- **Reconhecimento de Múltiplos Itens**: 
  - Novo endpoint `POST /api/ai/identify-multi`
  - Identifica cada item separadamente (útil para buffets)
  - Mostra calorias individuais e totais
  - Indica equilíbrio nutricional da refeição
  - Combina alertas de alérgenos de todos os itens
  - Toggle na UI para alternar entre modo Único e Multi

---

## Backlog Priorizado

### P0 - CRÍTICO (Em andamento)
- [x] ~~Reconhecimento de múltiplos itens no prato~~ ✅ CONCLUÍDO
- [ ] Validação de precisão com pratos do Cibi Sana (aguardando feedback do usuário)

### P1 - ALTA
- [ ] Investigar travamentos ocasionais do app
- [ ] Implementar link "Veja esta notícia" junto a alertas
- [ ] Histórico de pratos identificados

### P2 - MÉDIA
- [ ] Painel para restaurantes cadastrarem pratos
- [ ] Retreinar índice com fotos de feedback
- [ ] Teste com 3-4 usuários simultâneos

### P3 - FUTURO (Premium)
- [ ] Contador nutricional em tempo real
- [ ] Perfil do usuário (médico/alergias/restrições)
- [ ] Histórico de consumo semanal
- [ ] Alertas personalizados

---

## Endpoints Principais

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/ai/identify` | POST | Identifica prato único por imagem |
| `/api/ai/identify-multi` | POST | **NOVO** - Identifica múltiplos itens |
| `/api/ai/feedback` | POST | Registra feedback |
| `/api/ai/create-dish` | POST | Cria novo prato com IA |
| `/api/ai/dishes` | GET | Lista pratos |
| `/api/ai/status` | GET | Status do índice |

---

## Testes de Precisão (22/01/2026)

### Modo Único
| Imagem | Resultado | Confiança | Fonte |
|--------|-----------|-----------|-------|
| Pizza | Pizza Havaiana | 95% | Gemini Vision |
| Salada | Buddha Bowl Vegano | 95% | Gemini Vision |
| Sushi | Uramaki de Salmão | 95% | Gemini Vision |
| Hambúrguer | Hambúrguer Duplo | 95% | Gemini Vision |

### Modo Multi-Item
| Imagem | Itens | Calorias Totais |
|--------|-------|-----------------|
| Prato composto | 4 itens | ~287 kcal |
| Buffet | 6 itens | ~1180 kcal |

---

## URL de Preview
https://nutrivision-39.preview.emergentagent.com
