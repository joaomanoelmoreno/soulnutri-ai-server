# SoulNutri - Product Requirements Document

## Visão Geral
Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens.

## O que foi implementado

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

## Backlog

### P0 - Crítico
- [x] Consolidar duplicados
- [ ] Corrigir pratos restantes com IA

### P1 - Alto
- [ ] Remover ~90 pratos "Unknown"
- [ ] Otimizar velocidade IA

### P2 - Médio
- [ ] Refatorar App.js
- [ ] i18n completo
