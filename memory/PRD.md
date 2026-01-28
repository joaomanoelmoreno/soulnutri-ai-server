# SoulNutri - Product Requirements Document

## Visão Geral
Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens.

## O que foi implementado

### 28/01/2025 - Sistema SEM Créditos e Correções P0
- **Checkpoint v1 criado** - Versão funcional salva em `/app/checkpoints/v1_funcional_20260128_113435/`
- **Restauração rápida** - Script `bash /app/checkpoints/RESTAURAR_V1.sh` restaura tudo
- **Índice restaurado** - 492 pratos, 1806 embeddings funcionando
- **Endpoint LOCAL para correção** - `POST /api/ai/create-dish-local` cria/corrige pratos SEM IA
- **Pernil de cordeiro corrigido** - Ingredientes agora corretos (era "suíno", agora "cordeiro")
- **Novos templates** - Cordeiro, Gnocchi, Berinjela adicionados ao banco local
- **Conteúdo Premium LOCAL** - Dados científicos sem chamar IA (benefício principal, curiosidades, mitos)
- **Feedback de correção melhorado** - Confirmação clara ao usuário com "Créditos usados: 0"

### 27/01/2025 - Correções de Lógica de Classificação
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
- `/app/checkpoints/RESTAURAR_V1.sh` - Script para restaurar versão funcional
- `/admin` - Painel de administração
- `/app/backend/services/local_dish_updater.py` - Sistema de atualização SEM IA

## Decisões de Design

### Operações SEM Créditos (PRIORIDADE)
- Correção de nome usa `/api/ai/create-dish-local` (local, sem IA)
- Atualização em massa usa `local_dish_updater.py`
- Dados Premium (científicos) vêm do banco local `CONTEUDO_PREMIUM`
- Reconhecimento visual usa índice CLIP local (não consome créditos Emergent)

### Pratos Múltiplos (Buffet)
- NÃO criar novos pratos para combinações
- Se nome similar existe (>85%) → adiciona foto ao existente
- Pratos "unknown_" do Gemini não são salvos automaticamente

### Duplicados
- Consolidados automaticamente
- Mantém todas as imagens na pasta principal
- Informações mescladas (pega o mais completo)

### Classificação de Ingredientes
- **Vegano**: Zero produtos animais
- **Vegetariano**: Pode ter ovo/leite/queijo de vaca, sem carne
- **Proteína animal**: Tem carne/peixe/frango
- **Versões veganas reconhecidas**: queijo vegano, leite de coco, creme vegetal, etc.
- **Decoração ignorada**: Ingredientes usados apenas para decorar não contam

## Backlog

### P0 - Crítico ✅ CONCLUÍDO
- [x] Restaurar índice de embeddings (492 pratos funcionando)
- [x] Criar checkpoint de segurança
- [x] Corrigir pernil de cordeiro
- [x] Endpoint de correção SEM créditos
- [x] Conteúdo Premium LOCAL

### P1 - Alto
- [ ] Melhorar tela resumo no buffet com informações de decisão rápida
- [ ] Adicionar mais tipos de pratos ao banco local
- [ ] Remover ~90 pratos "Unknown"
- [ ] Corrigir bug de salvamento inconsistente no admin

### P2 - Médio
- [ ] Refatorar App.js (componente monolítico)
- [ ] i18n completo
- [ ] Sistema de pagamento Stripe para Premium
