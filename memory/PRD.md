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

### ❌ O QUE NÃO FAZER (informações óbvias):
- "Muito colesterol faz mal" (todo mundo sabe)
- "Açúcar em excesso engorda" (óbvio)
- "Fritura não é saudável" (conhecimento popular)
- "Evitar glúten se for celíaco" (óbvio)
- "Fonte de proteínas" (genérico)

### ✅ O QUE FAZER (informações relevantes):
- **Com dados**: "Potássio (485mg) - regula impulsos elétricos do coração, previne arritmias"
- **Com fonte**: "OMS classificou embutidos como Grupo 1 carcinógeno (2015)"
- **Com impacto**: "80% dos brasileiros têm deficiência de vitamina D (USP 2023)"
- **Com curiosidade**: "Cogumelos recarregam vitamina D no sol mesmo depois de colhidos"

### 📊 Fontes Científicas:
- OMS/WHO (Organização Mundial da Saúde)
- ANVISA (Agência Nacional de Vigilância Sanitária)
- IARC (Agência Internacional de Pesquisa em Câncer)
- FDA (Food and Drug Administration)
- Tabela TACO (UNICAMP)
- Revistas: Nature, Lancet, JAMA, Harvard Health

### ⚠️ Alertas de Saúde Relevantes:
- **Carnes Processadas**: OMS Grupo 1 carcinógeno (bacon, linguiça, presunto)
- **Peixes Grandes**: Mercúrio - FDA limite 340g/semana
- **Ultraprocessados**: +10% consumo = +12% risco câncer (NutriNet 2022)
- **Agrotóxicos**: Brasil maior consumidor mundial
- **Gordura Trans**: FDA baniu nos EUA em 2018

---

## Versões do Produto

### Versão Gratuita
- Identificação de pratos por imagem
- Categoria (vegano/vegetariano/proteína animal)
- Alérgenos em destaque
- 1 benefício principal (científico)
- 1 alerta de saúde (se relevante)
- 1 curiosidade científica
- Referência da pesquisa

### Versão Premium (Futuro)
- Perfil nutricional pessoal
- Histórico de consumo
- Alertas: "Você já consumiu X de sódio esta semana..."
- Link para notícias/pesquisas sobre ingredientes
- Busca: "Veja esta pesquisa recente sobre..."

---

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32)
- **Database**: MongoDB
- **IA**: GPT-4o Vision (identificação e informações científicas)

---

## Funcionalidades Implementadas

### ✅ Core
- [x] Identificação por imagem (139 pratos índice + 18 novos)
- [x] Sistema de feedback (correto/incorreto)
- [x] Cadastro de pratos novos com IA
- [x] IA genérica para pratos não cadastrados
- [x] Busca de pesquisas sobre ingredientes

### ✅ UI/UX
- [x] Câmera com moldura retangular vertical
- [x] Toque para fotografar
- [x] Modal de correção com busca
- [x] Campo para cadastrar prato novo

### ✅ Informações Científicas
- [x] Prompt detalhado para IA (evitar óbvio, focar em relevante)
- [x] 18 pratos com informações completas
- [x] Endpoint de pesquisa de ingredientes
- [ ] Estender para todos os 139 pratos

---

## Backlog

### P0 - URGENTE
- [ ] Estender informações científicas para TODOS os 139 pratos
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

## Estatísticas Atuais
- Pratos no índice: 139
- Pratos criados pelo usuário: 18
- Feedbacks coletados: 18
- Taxa de acerto: 83.3%
