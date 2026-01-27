# SoulNutri - Product Requirements Document

## Visão Geral
Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens.

## O que foi implementado

### 27/01/2025 - Correções de Lógica de Classificação (NOVA)
- **Queijo vegano diferenciado** - Sistema agora reconhece "queijo vegano", "queijo de castanha", etc. como vegano
- **Decoração ignorada** - Ingredientes em contexto de "decoração" não afetam a classificação
- **Endpoint de regeneração** - POST `/api/admin/dishes/{slug}/regenerate` regenera toda a ficha baseado no nome
- **Versões veganas** - Adicionada lista completa de ingredientes veganos (leite de coco, creme de coco, etc.)
- **Detecção inteligente** - Word boundaries evitam falsos positivos (ex: "decoração" não detecta "coração")

### 27/01/2025 - Consolidação de Duplicados
- **60 grupos consolidados** automaticamente
- **468 → 258 pratos únicos** (todas imagens mantidas)
- Endpoint POST `/api/admin/consolidate-all` - consolida em massa
- Endpoint GET `/api/admin/duplicates` - lista grupos similares
- Lógica de criação alterada: verifica similaridade antes de criar novo prato

### 27/01/2025 - Melhorias Admin
- Mais alérgenos: Lactose, Ovo, Castanhas, Frutos do Mar, Soja
- Leite de coco = VEGANO (prompt IA atualizado)
- Bug "body stream already read" corrigido

### 26/01/2025 - Ferramenta de Auditoria
- Endpoint GET `/api/admin/audit`
- Correção com IA via POST `/api/admin/audit/fix-single/{slug}`

## Arquivos Importantes
- `/lista-pratos.txt` - Lista de 258 pratos para impressão
- `/admin` - Painel de administração

## Decisões de Design

### Pratos Múltiplos (Buffet)
- NÃO criar novos pratos para combinações
- Se nome similar existe (>85%) → adiciona foto ao existente
- Pratos "unknown_" do Gemini não são salvos automaticamente

### Duplicados
- Consolidados automaticamente
- Mantém todas as imagens na pasta principal
- Informações mescladas (pega o mais completo)

### Classificação de Ingredientes (NOVA)
- **Vegano**: Zero produtos animais
- **Vegetariano**: Pode ter ovo/leite/queijo de vaca, sem carne
- **Proteína animal**: Tem carne/peixe/frango
- **Versões veganas reconhecidas**: queijo vegano, leite de coco, creme vegetal, etc.
- **Decoração ignorada**: Ingredientes usados apenas para decorar não contam

## Backlog

### P0 - Crítico
- [x] Consolidar duplicados
- [x] Corrigir lógica queijo vegano vs comum
- [ ] Reconstruir índice de embeddings (em progresso)

### P1 - Alto
- [ ] Remover ~90 pratos "Unknown"
- [ ] Otimizar velocidade IA
- [ ] Corrigir bug de salvamento inconsistente no admin

### P2 - Médio
- [ ] Refatorar App.js
- [ ] i18n completo
