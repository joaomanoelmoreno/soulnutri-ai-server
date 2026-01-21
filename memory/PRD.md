# SoulNutri - Product Requirements Document

## Visão Geral
Sistema inteligente de identificação de pratos em tempo real para restaurantes. Funciona como um "Waze para alimentação" - identificando pratos por imagem e fornecendo informações nutricionais, ingredientes, benefícios e riscos (alérgenos).

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32) para embeddings visuais
- **Database**: MongoDB (não utilizado atualmente - dados hardcoded)

## Funcionalidades Implementadas

### ✅ Core Features (Concluídas)
- [x] Identificação de pratos por imagem via câmera ou upload
- [x] 139 pratos cadastrados com dados completos
- [x] Indicador de confiança visual (ALTA/MÉDIA/BAIXA)
- [x] Exibição de ingredientes, benefícios e riscos
- [x] Informações nutricionais (calorias, proteínas, carbos, gorduras)
- [x] Técnicas de preparo Cibi Sana
- [x] Aviso "sem aditivos químicos e/ou alimentos industrializados"
- [x] Lógica de glúten corrigida

### ✅ UI/UX (Concluídas - 21/01/2026)
- [x] Câmera no topo com área ampla (280px min)
- [x] Botão "Nova Foto" sempre visível (lado do Galeria)
- [x] Bug da auto-captura corrigido (useRef para loading)
- [x] Footer "Powered by Emergent" discreto
- [x] Layout responsivo mobile-first
- [x] Logo SoulNutri oficial integrado com ® (21/01/2026)

### ✅ Performance (Melhorada - 21/01/2026)
- [x] Modelo CLIP pré-carregado no startup
- [x] Tempo de resposta: ~6000ms → ~250ms (25x mais rápido!)
- [ ] Meta: ~100ms (requer GPU)

## Backlog

### P0 - Alta Prioridade
- [x] ~~Gerar ícone/logo do app SoulNutri~~ (Usuário forneceu logo)
- [ ] Testar reconhecimento de pratos não cadastrados

### P1 - Média Prioridade
- [ ] Otimizar para ~100ms (requer GPU ou modelo mais leve)
- [ ] Investigar domínio personalizado `soulnutri.app.br`

### P2 - Baixa Prioridade
- [ ] Refatorar dados dos pratos para JSON/MongoDB
- [ ] Deploy em produção (Render com mais memória/GPU)

### Futuro
- [ ] Funcionalidades Premium (alertas inteligentes)
- [ ] Histórico de consultas
- [ ] Favoritos

## Arquivos Principais
- `/app/frontend/src/App.js` - Componente React principal
- `/app/frontend/src/App.css` - Estilos
- `/app/backend/server.py` - API FastAPI
- `/app/backend/ai/policy.py` - Dados dos pratos (HARDCODED)
- `/app/backend/ai/index.py` - Índice de embeddings

## Endpoints da API
- `GET /api/ai/status` - Status do índice
- `POST /api/ai/identify` - Identificar prato
- `POST /api/ai/reindex` - Reconstruir índice
- `GET /api/ai/dishes` - Listar pratos
- `POST /api/ai/learn` - Cadastrar novo prato

## Notas Importantes
- Usuário não é técnico - comunicação simples
- Dados dos 139 pratos estão hardcoded em `policy.py`
- Performance atual ~6s (necessita GPU para atingir 100ms)
