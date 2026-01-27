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

## O que foi implementado

### 26/01/2025 - Ferramenta de Auditoria
- Endpoint GET `/api/admin/audit` - Analisa todos os pratos
- Correção com IA via POST `/api/admin/audit/fix-single/{slug}`
- Interface Admin com aba "Auditoria"

### 27/01/2025 - Correções e Melhorias
- **Bug "body stream already read"** - Corrigido no frontend
- **Leite de coco = VEGANO** - Prompt da IA atualizado
- **Novos alérgenos no Admin**: Lactose, Ovo, Castanhas, Frutos do Mar, Soja
- **Lista para impressão**: `/lista-pratos.html` com 308 pratos únicos
- **Auditoria inteligente**: Não considera "leite de coco" como conflito vegano

## Problemas de Dados (27/01)
- 308 pratos únicos catalogados
- ~90 pratos com "Unknown" no nome
- Muitos duplicados com nomes ligeiramente diferentes
- Usuário revisou manualmente até letra C

## Decisões Pendentes

### Pratos Múltiplos (Buffet vs À la carte)
**Problema:** Em buffets, clientes montam combinações infinitas. Salvar essas fotos complica o reconhecimento.

**Solução proposta:**
1. Detectar múltiplos itens → reconhecer individualmente
2. NÃO salvar combinação como novo "prato"
3. Apenas pratos individuais padronizados vão para o dataset

## Backlog Prioritizado

### P0 - Crítico
- [ ] Usuário testar Admin e fazer deploy
- [ ] Corrigir pratos restantes com IA em lote

### P1 - Alto
- [ ] Consolidar nomes duplicados
- [ ] Implementar lógica de pratos múltiplos
- [ ] Otimizar velocidade da IA

### P2 - Médio
- [ ] Refatorar App.js em componentes
- [ ] Completar i18n
- [ ] Sistema de pagamentos

## Endpoints Principais
- `POST /api/ai/identify` - Identificar prato
- `GET /api/admin/audit` - Auditoria de dados
- `POST /api/admin/audit/fix-single/{slug}` - Corrigir com IA
- `PUT /api/admin/dishes/{slug}` - Salvar edição manual
- `GET /lista-pratos.html` - Lista para impressão
