# SoulNutri - Product Requirements Document

## Visão Geral
Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens, fornecendo informações nutricionais detalhadas e personalizadas.

## Requisitos Principais
1. **Performance**: Identificação < 500ms e precisão > 90%
2. **Coleta de Dados**: Fluxo para fotografar pratos na balança (Cibi Sana)
3. **Qualidade**: Informações educativas e cientificamente embasadas
4. **UX/UI**: Interface fluida com mínimo de cliques
5. **Premium**: Funcionalidades de alto valor via assinatura
6. **Buffet Flexível**: Reconhecer pratos compostos por múltiplos itens
7. **i18n**: Suporte a EN, ES, FR, DE, ZH

## Arquitetura
- **Frontend**: React (App.js ~2000 linhas - precisa refatoração)
- **Backend**: FastAPI + IA (OpenCLIP local + Gemini fallback)
- **Dados**: Filesystem (/app/datasets/organized/[slug]/dish_info.json)

## O que foi implementado (26/01/2025)

### ✅ Ferramenta de Auditoria de Dados
- Endpoint GET `/api/admin/audit` - Analisa todos os 503 pratos
- Identifica: nomes Unknown, nutrição vazia, conflitos de categoria, alérgenos incorretos
- Health Score: atualmente 4.2% (483 pratos com problemas)

### ✅ Correção com IA (Gemini)
- Endpoint POST `/api/admin/audit/fix-single/{slug}` - Corrige 1 prato
- Endpoint POST `/api/admin/audit/batch-fix` - Corrige até 10 pratos em lote
- Prompt rigoroso para preencher: nome, categoria, ingredientes, nutrição, alérgenos
- Testado e funcionando (ex: "Unknowntomatesfatiados" → "Tomates Fatiados com Cebolinha")

### ✅ Interface Admin
- Nova aba "Auditoria" em /admin
- Dashboard com Health Score e resumo de problemas
- Botões para correção individual (🤖) e em lote
- CSS estilizado para visualização clara

## Problemas de Dados Identificados
| Tipo | Quantidade |
|------|------------|
| Sem arquivo dish_info.json | 130 |
| Nutrição vazia | 353 |
| Nomes "Unknown" | 15 |
| Conflitos de categoria | 18 |
| Alérgenos incorretos | 64 |

## Backlog Prioritizado

### P0 - Crítico
- [ ] Corrigir dados em lote (usar botões de auditoria)
- [ ] Validar fluxo no celular (usuário reportou bug)
- [ ] Otimizar velocidade da IA (reduzir uso do Gemini)

### P1 - Alto
- [ ] Refatorar App.js em componentes menores
- [ ] Completar i18n (textos hardcoded)
- [ ] Padronizar cores área Premium
- [ ] Implementar funcionalidade Galeria

### P2 - Médio
- [ ] Resolver travamentos mobile (camera lifecycle)
- [ ] Adicionar botão "Voltar" em todas as telas
- [ ] Sistema de pagamentos (Stripe/Apple/Google)
- [ ] Trial de 7 dias

## Endpoints Principais
- `POST /api/ai/identify` - Identificar prato por imagem
- `GET /api/admin/audit` - Auditoria de dados
- `POST /api/admin/audit/fix-single/{slug}` - Corrigir prato com IA
- `POST /api/admin/audit/batch-fix` - Correção em lote
- `POST /api/admin/dish/{slug}` - Salvar edição manual

## Notas Técnicas
- OpenCLIP precisa score ≥90% para responder sem Gemini
- Gemini fallback adiciona 3-5s de latência
- Premium gerenciado via /app/backend/data/premium_users.json
