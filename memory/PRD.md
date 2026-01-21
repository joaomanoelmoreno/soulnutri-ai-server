# SoulNutri - Product Requirements Document

## Visão e Posicionamento

### Slogan
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

### Proposta de Valor
O SoulNutri é um **nutricionista virtual** que acompanha o cliente em todas as suas refeições, fornecendo informações **educativas e relevantes** que ele NÃO conhece.

### Diferencial
- ❌ NÃO: "Evitar glúten se for celíaco" (óbvio)
- ✅ SIM: "Rico em potássio (380mg), mineral que regula a pressão arterial e previne cãibras musculares"

### Disclaimer Legal
> "As informações são educativas e não substituem orientação de profissionais de saúde. Consulte um nutricionista para dietas personalizadas."

---

## Versões do Produto

### Versão Gratuita
- Identificação de pratos por imagem
- Categoria (vegano/vegetariano/proteína animal)
- Alérgenos em destaque
- 1 benefício educativo (o melhor do prato)
- 1 risco/atenção (o mais importante)
- Informações nutricionais básicas

### Versão Premium (Futuro)
- Perfil nutricional do usuário
- Histórico de consumo
- Alertas personalizados: "Esta semana você já consumiu X de potássio..."
- Sugestões baseadas no histórico
- Notícias/pesquisas sobre ingredientes
- Link com mídia especializada (saúde, agrotóxicos, etc.)

---

## Tecnologias
- **Backend**: FastAPI + Python
- **Frontend**: React
- **ML/CV**: OpenCLIP (ViT-B-32)
- **Database**: MongoDB
- **IA Genérica**: GPT-4o Vision

---

## Funcionalidades Implementadas

### ✅ Core Features
- [x] Identificação de pratos por imagem
- [x] 139 pratos no índice + 18 criados pelo usuário
- [x] Indicador de confiança (ALTA/MÉDIA/BAIXA)
- [x] Categorias coloridas (vegano/vegetariano/proteína animal)
- [x] Alérgenos sempre visíveis
- [x] Sistema de feedback (correto/incorreto)
- [x] Cadastro de pratos novos com IA
- [x] IA genérica para pratos não cadastrados

### ✅ UI/UX
- [x] Câmera com moldura retangular vertical
- [x] Toque para fotografar
- [x] Botões Galeria e Nova Foto
- [x] Modal de correção com busca
- [x] Campo para cadastrar prato novo

---

## Backlog Priorizado

### P0 - URGENTE
- [ ] Corrigir preenchimento de ingredientes/benefícios nos 18 pratos novos
- [ ] Investigar travamentos do app
- [ ] Melhorar precisão (meta: 100% em pratos cadastrados)
- [ ] Simplificar benefícios/riscos (1 melhor + 1 pior, educativos)

### P1 - ESTA SEMANA
- [ ] Implementar busca de notícias sobre ingredientes
- [ ] Preparar teste com múltiplos usuários simultâneos
- [ ] Retreinar índice com novas fotos coletadas

### P2 - FUTURO
- [ ] Reconhecimento de pratos compostos (múltiplos itens)
- [ ] Versão Premium separada
- [ ] Perfil nutricional do usuário
- [ ] Histórico de consumo
- [ ] Alertas personalizados

---

## Estatísticas Atuais
- Pratos no índice: 139
- Pratos criados pelo usuário: 18
- Feedbacks coletados: 18
- Taxa de acerto: 83.3%

---

## Notas Importantes
- Usuário não é técnico - comunicação simples
- Informações devem ser EDUCATIVAS, não óbvias
- Nunca se posicionar como profissional de saúde
- Foco em informar, não prescrever
