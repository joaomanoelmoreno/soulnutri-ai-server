# SoulNutri - Product Requirements Document

## Última Atualização: 2026-02-04

### Status do Projeto: ✅ OPERACIONAL

---

## Visão do Produto
Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real via câmera, fornecendo informações nutricionais detalhadas e personalizadas.

## Arquitetura Atual

### Reconhecimento de Imagem (Cascata)
1. **CLIP Local** (custo zero) - Modelo ViT-B-32 com 299 pratos indexados
2. **Gemini Flash** (backup) - Usado apenas fora do Cibi Sana quando CLIP não confiante

### Detecção de Localização
- GPS com geofencing (raio 100m do Cibi Sana)
- No Cibi Sana: usa APENAS CLIP (Gemini travado)
- Fora: CLIP primeiro, Gemini como backup

### Tabela TACO
- 597 alimentos da Tabela Brasileira de Composição de Alimentos
- Endpoint `/api/admin/revisar-prato-taco` - ZERO créditos
- Cálculo automático de nutrição baseado em ingredientes

---

## O que foi implementado (04/02/2026)

### Correções Críticas
- ✅ Calibração do CLIP restaurada (scores altos = confiança alta)
- ✅ Índice reconstruído: 299 pratos, 1778 imagens
- ✅ 78 novas fotos adicionadas (7 pratos do Drive)
- ✅ Botão "Usar IA" removido do App (só Admin tem acesso)
- ✅ Lógica de conflito vegano melhorada (reconhece versões veganas)

### Novos Recursos
- ✅ Botão "📊 Nutrição TACO (grátis)" no Admin
- ✅ Endpoint `/api/admin/revisar-prato-taco` - usa Tabela Brasileira sem IA
- ✅ Service Worker atualizado para evitar cache no Safari

---

## Fluxo de Economia de Créditos

| Ação | Custo |
|------|-------|
| Reconhecimento no Cibi Sana | ZERO (CLIP) |
| Reconhecimento fora | Pode usar Gemini |
| Nutrição com TACO | ZERO |
| Nutrição com IA | GASTA créditos |
| "Revisar com IA" no Admin | GASTA créditos |

---

## Tarefas Pendentes

### P1 - Alta Prioridade
- [ ] Limpeza de fotos incorretas no dataset (usuário fazendo pelo Admin)
- [ ] Adicionar mais fotos aos pratos com poucas imagens (<3 fotos)

### P2 - Média Prioridade
- [ ] Implementar aprendizado contínuo (Gemini → CLIP)
- [ ] Migração para Cloudflare R2 (disco 89% usado)

### P3 - Backlog
- [ ] Refatorar App.js e server.py (arquivos monolíticos)
- [ ] Implementar Stripe para assinaturas Premium
- [ ] Integrar API de reconhecimento Nível 2 (LogMeal)

---

## Credenciais de Teste
- Usuário Premium: `Joao mc`, PIN: `1212`

## Arquivos Principais
- `/app/backend/server.py` - API principal
- `/app/backend/ai/index.py` - Lógica CLIP e calibração
- `/app/frontend/src/App.js` - Interface principal
- `/app/frontend/src/Admin.js` - Painel administrativo
- `/app/backend/data/taco_database.py` - Tabela TACO
- `/app/datasets/organized/` - Fotos dos pratos
