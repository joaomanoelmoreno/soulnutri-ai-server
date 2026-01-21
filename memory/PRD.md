# SoulNutri - Product Requirements Document

## Visão e Posicionamento

### Slogan
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

### Proposta de Valor
O SoulNutri é um **agente de nutrição virtual** que acompanha o cliente em todas as suas refeições, fornecendo informações **CIENTÍFICAS, RELEVANTES e RECENTES** que ele NÃO conhece.

### Disclaimer Legal
> "As informações são educativas e baseadas em pesquisas científicas. Não substituem orientação de profissionais de saúde."

---

## Diretrizes de Conteúdo

### O QUE NÃO FAZER (informações óbvias):
- "Muito colesterol faz mal" (todo mundo sabe)
- "Açúcar em excesso engorda" (óbvio)
- "Fritura não é saudável" (conhecimento popular)
- "Evitar glúten se for celíaco" (óbvio)
- "Fonte de proteínas" (genérico)

### O QUE FAZER (informações relevantes):
- **Com dados**: "Potássio (485mg) - regula impulsos elétricos do coração"
- **Com fonte**: "OMS classificou embutidos como Grupo 1 carcinógeno (2015)"
- **Com impacto**: "80% dos brasileiros têm deficiência de vitamina D (USP 2023)"
- **Com curiosidade**: "Cogumelos recarregam vitamina D no sol"

### Fontes Científicas:
- OMS/WHO (Organização Mundial da Saúde)
- ANVISA (Agência Nacional de Vigilância Sanitária)
- IARC (Agência Internacional de Pesquisa em Câncer)
- FDA (Food and Drug Administration)
- Tabela TACO (UNICAMP)
- Revistas: Nature, Lancet, JAMA, Harvard Health

---

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32)
- **Database**: MongoDB (soulnutri)
- **IA**: GPT-4o Vision (via Emergent LLM Key)

---

## Status Atual (Janeiro 2026)

### Base de Dados
- **Total de pratos**: 116
- **Com dados científicos**: 116 (100%)
- **Veganos**: 43 pratos
- **Vegetarianos**: 30 pratos
- **Proteína animal**: 42 pratos

### Funcionalidades Implementadas

#### Core
- [x] Identificação por imagem (139 pratos no índice visual)
- [x] Sistema de feedback (correto/incorreto)
- [x] Cadastro de pratos novos com IA
- [x] IA genérica para pratos não cadastrados (GPT-4o Vision)
- [x] Busca de pesquisas sobre ingredientes

#### UI/UX
- [x] Câmera com moldura retangular vertical
- [x] Toque para fotografar
- [x] Modal de correção com busca
- [x] Campo para cadastrar prato novo

#### Informações Científicas (CONCLUÍDO)
- [x] Todos os 116 pratos enriquecidos com dados científicos
- [x] beneficio_principal: informação educativa com dados
- [x] curiosidade_cientifica: fato interessante ou dica prática
- [x] referencia_pesquisa: fonte científica (journals, OMS, etc)
- [x] alerta_saude: alertas equilibrados quando relevante
- [x] Frontend exibindo seção científica estilizada

---

## Backlog

### P0 - URGENTE
- [ ] Investigar travamentos do app
- [ ] Melhorar precisão (meta: 100% pratos cadastrados)

### P1 - ESTA SEMANA
- [ ] Teste com grupo de 3-4 pessoas simultâneas
- [ ] Interface para mostrar link "Veja esta pesquisa"
- [ ] Retreinar índice com novas fotos

### P2 - FUTURO
- [ ] Versão Premium separada
- [ ] Perfil nutricional do usuário
- [ ] Reconhecimento de pratos compostos

---

## Arquitetura

```
/app
├── backend/
│   ├── ai/
│   │   ├── embedder.py      # OpenCLIP
│   │   ├── index.py         # Gerencia index.pkl
│   │   └── policy.py        # Lógica de decisão
│   ├── data/
│   │   └── index.pkl        # Índice visual
│   ├── scripts/
│   │   └── enrich_dishes.py # Script de enriquecimento
│   ├── services/
│   │   ├── dish_service.py  # CRUD MongoDB
│   │   └── generic_ai.py    # GPT-4o Vision
│   └── server.py            # FastAPI
├── frontend/
│   ├── src/
│   │   ├── App.css
│   │   └── App.js
│   └── package.json
└── datasets/
    └── organized/           # Imagens de pratos
```

## Endpoints Principais

- `POST /api/ai/identify` - Identifica prato por imagem
- `POST /api/ai/feedback` - Registra feedback
- `POST /api/ai/create-dish` - Cria novo prato com IA
- `GET /api/ai/dishes` - Lista pratos
- `GET /api/ai/status` - Status do índice
