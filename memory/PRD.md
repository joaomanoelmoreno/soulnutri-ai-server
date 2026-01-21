# SoulNutri - Product Requirements Document

## Visão Geral
Sistema inteligente de identificação de pratos em tempo real para restaurantes. Funciona como um "Waze para alimentação" - identificando pratos por imagem e fornecendo informações nutricionais, ingredientes, benefícios e riscos (alérgenos).

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32) para embeddings visuais
- **Database**: MongoDB (98 pratos migrados)

## Funcionalidades Implementadas

### ✅ Core Features (Concluídas)
- [x] Identificação de pratos por imagem via câmera ou upload
- [x] 139 pratos cadastrados no índice visual
- [x] 98 pratos com dados completos no MongoDB
- [x] Indicador de confiança visual (ALTA/MÉDIA/BAIXA)
- [x] Exibição de ingredientes, benefícios e riscos
- [x] Informações nutricionais (calorias, proteínas, carbos, gorduras)
- [x] Técnicas de preparo Cibi Sana
- [x] Aviso "sem aditivos químicos e/ou alimentos industrializados"
- [x] Lógica de glúten corrigida

### ✅ UI/UX (Concluídas - 21/01/2026)
- [x] Câmera no topo com área ampla (300px min)
- [x] **"Toque para fotografar"** - interação intuitiva
- [x] **Botões maiores** - Galeria e Nova Foto bem visíveis
- [x] **Categoria logo abaixo do nome** (Vegano=verde, Vegetariano=branco, Proteína=laranja)
- [x] **Alérgenos em destaque** com formato específico
- [x] Logo SoulNutri oficial com ®
- [x] Footer "Powered by Emergent" discreto
- [x] Layout responsivo mobile-first

### ✅ Performance (Melhorada - 21/01/2026)
- [x] Modelo CLIP pré-carregado no startup
- [x] Tempo de resposta: ~250ms

### ✅ Banco de Dados MongoDB (21/01/2026)
- [x] 98 pratos migrados
- [x] 34 veganos, 25 vegetarianos, 38 proteína animal
- [x] Estrutura: slug, nome, categoria, ingredientes, benefícios, riscos, nutrição
- [x] Índices criados para performance

## Backlog

### P0 - Alta Prioridade
- [ ] Revisar dados dos pratos com informações genéricas
- [ ] Testar reconhecimento de pratos não cadastrados

### P1 - Média Prioridade
- [ ] Melhorar precisão entre pratos similares (confusão)
- [ ] Sistema de feedback: "correto/incorreto"
- [ ] Migrar dados para MongoDB (escalabilidade)

### P2 - Baixa Prioridade
- [ ] Investigar domínio personalizado `soulnutri.app.br`
- [ ] Otimizar para ~100ms (requer GPU)
- [ ] Deploy em produção

### Premium (Futuro)
- [ ] Perfil nutricional do usuário
- [ ] Alertas personalizados
- [ ] Histórico de consumo
- [ ] Notícias e pesquisas

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
