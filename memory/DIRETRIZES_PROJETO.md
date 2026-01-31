# SoulNutri - Diretrizes, Premissas e Decisões do Projeto

## IMPORTANTE: Este documento contém TODAS as diretrizes do fundador do projeto.
## O agente DEVE ler este arquivo antes de qualquer implementação.

---

## 1. VISÃO DO PRODUTO

### Slogan Oficial
**"SOULNUTRI - O SEU AGENTE DE NUTRIÇÃO VIRTUAL"**

### Proposta de Valor
- Funcionar como um "Waze da alimentação"
- Agente de nutrição virtual que acompanha o cliente em TODAS as refeições
- Fornecer informações CIENTÍFICAS, RELEVANTES e RECENTES que o cliente NÃO conhece
- Identificação de pratos por imagem em tempo real

### Disclaimer Legal (OBRIGATÓRIO em todas as telas)
> "As informações são educativas e baseadas em pesquisas científicas. Não substituem orientação de profissionais de saúde."

---

## 2. PREMISSA FUNDAMENTAL - 100% DE PRECISÃO

### CRÍTICO: O reconhecimento correto é a BASE de TUDO
- Sem precisão, o app não tem valor
- "O erro no reconhecimento é VENENO do app"
- Meta: 100% de acerto para pratos cadastrados
- Usar redundâncias, verificação cruzada, múltiplas IAs se necessário

### Arquitetura Aprovada: Sistema Híbrido em 3 Níveis

```
NÍVEL 1: Índice Local (OpenCLIP)
├── Para: Parceiros cadastrados (ex: Cibi Sana)
├── Custo: $0
├── Velocidade: ~200ms
├── Precisão esperada: 95%+
├── Se confiança >= 90% → RESULTADO FINAL
└── Se confiança < 90% → Passa para Nível 2

NÍVEL 2: IA Especializada (LogMeal API)
├── Para: Pratos não cadastrados / confirmação
├── Custo: Free tier / baixo
├── Velocidade: ~500ms
├── Precisão: 93-98%
├── Se confiança >= 85% → RESULTADO FINAL
└── Se confiança < 85% → Passa para Nível 3

NÍVEL 3: IA Genérica (GPT-4o Vision)
├── Para: Fallback universal
├── Custo: ~$0.01-0.02
├── Velocidade: ~1-2s
└── Sempre retorna resultado

VALIDAÇÃO CRUZADA (Opcional):
├── Se Nível 1 e Nível 2 concordam → 99%+ confiança
└── Se divergem → Mostrar opções ao usuário
```

---

## 3. ESCOPO E ESCALA

### Cibi Sana = Protótipo e Modelo de Referência
- Laboratório para testar e aperfeiçoar
- Deve funcionar com 100% de precisão
- Modelo que será replicado para outros restaurantes

### SoulNutri = Preparado para Demanda MUNDIAL
- Cibi Sana é "uma gota no oceano"
- Arquitetura deve ser escalável globalmente
- Não depender apenas de pratos cadastrados

### Modelo de Negócio Futuro
- **Restaurantes parceiros**: Pagam para ter índice próprio (100% precisão)
- **Usuários finais**: Usam IA genérica (freemium)

---

## 4. QUALIDADE DA INFORMAÇÃO

### O QUE NÃO FAZER (informações óbvias):
- "Muito colesterol faz mal" (todo mundo sabe)
- "Açúcar em excesso engorda" (óbvio)
- "Fritura não é saudável" (conhecimento popular)
- "Fonte de proteínas" (genérico demais)

### O QUE FAZER (informações relevantes):
- **Com dados numéricos**: "Potássio (485mg) - regula impulsos elétricos do coração"
- **Com fonte científica**: "OMS classificou embutidos como Grupo 1 carcinógeno (2015)"
- **Com impacto real**: "80% dos brasileiros têm deficiência de vitamina D (USP 2023)"
- **Com curiosidade**: "Cogumelos recarregam vitamina D no sol mesmo depois de colhidos"

### EQUILÍBRIO OBRIGATÓRIO
- 50% notícias BOAS / benefícios / curiosidades positivas
- 50% alertas quando relevante
- NÃO ser um "app do apocalipse" - não só alertas negativos!
- Informar SEM assustar, educar COM equilíbrio

### Fontes Científicas Válidas:
- OMS/WHO
- ANVISA
- IARC
- FDA
- Tabela TACO (UNICAMP)
- Revistas: Nature, Lancet, JAMA, Harvard Health

---

## 5. VERSÃO PREMIUM (FUTURO)

### Contador Nutricional em Tempo Real
- Aparece NO MOMENTO em que o usuário vai:
  - Se servir em buffet
  - Comprar um alimento
  - Receber prato à la carte

### Dados do Perfil do Usuário:
- Dados físicos (peso, altura, idade)
- Dados médicos
- Alergias
- Restrições alimentares
- Preferências de alimentos

### Funcionalidade do Contador:
- Mostrar quanto já consumiu no dia/semana
- Alertar se está aquém ou além do recomendado
- Baseado na condição específica do usuário

### Outras Features Premium:
- Histórico de consumo semanal
- Perfil nutricional personalizado
- Alertas inteligentes baseados no histórico
- Link para pesquisas/notícias sobre ingredientes

---

## 6. CIBI SANA - PREMISSAS GASTRONÔMICAS

### Filosofia (SEMPRE mencionar quando relevante):
- Sem aditivos químicos
- Sem alimentos industrializados/processados
- Legumes e verduras orgânicos
- Peixes e carnes frescos (recebidos a cada 1-2 dias)
- Creme de leite fresco
- Bases e molhos feitos na cozinha
- Especiarias importadas (Índia, Arábia, Israel, China, Japão)
- Ervas frescas orgânicas recebidas diariamente
- Feijão demolhado antes do preparo
- Maple light e Maple Canadense para adoçar

### Técnicas de Preparo:
- Sous vide
- Vapor
- Braseamento
- Banho maria
- Grelhas
- Azeite
- Forno combinado (exceto bolinho de bacalhau que é frito)

---

## 7. UX/UI - DIRETRIZES

### Princípios:
- Mínimo de cliques possível
- Câmera com moldura guia retangular vertical
- Captura por "toque na tela"
- Botões grandes e fáceis de clicar

### Sistema de Feedback do Usuário:
1. Confirmar que identificação está correta
2. Corrigir identificação (selecionar prato certo de lista)
3. Cadastrar prato totalmente novo (IA gera info)
4. Salvar fotos para treinar a IA
5. Descartar fotos inutilizáveis

### Exibição de Resultados:
- Nome do prato em destaque
- Categoria (vegano/vegetariano/proteína) com cor
- Alérgenos SEMPRE visíveis
- Benefício principal (científico)
- Curiosidade científica
- Referência da pesquisa
- Botão de compartilhar

---

## 8. DECISÕES TÉCNICAS APROVADAS

### Stack Atual:
- Backend: FastAPI + Python
- Frontend: React
- Database: MongoDB
- ML/CV: OpenCLIP (ViT-B-32)
- IA: GPT-4o Vision via Emergent LLM Key

### Integrações a Implementar:
- LogMeal API (Nível 2 do sistema híbrido)

### Performance:
- Meta original: 100ms (flexibilizada)
- Atual aceitável: ~250ms em CPU
- Com sistema híbrido: ~200ms a 2s dependendo do nível

---

## 9. STATUS ATUAL (Janeiro 2026)

### Concluído:
- [x] 116 pratos com informações científicas (100%)
- [x] Sistema de feedback do usuário
- [x] Cadastro de pratos novos com IA
- [x] IA genérica para pratos não cadastrados
- [x] Botão de compartilhar curiosidade
- [x] UI com câmera e moldura guia

### Próximo Passo (FASE 1):
- [ ] Integrar LogMeal API como Nível 2
- [ ] Implementar lógica de cascata
- [ ] Testar precisão com pratos do Cibi Sana

### Pendente:
- [ ] Investigar travamentos do app
- [ ] Melhorar precisão do índice local
- [ ] Teste com 3-4 usuários simultâneos

---

## 10. CONTATOS E LINKS

### URL de Preview:
https://nutrivision-41.preview.emergentagent.com

### Arquivos Importantes:
- /app/memory/PRD.md - Requisitos do produto
- /app/memory/DIRETRIZES_PROJETO.md - Este arquivo
- /app/backend/server.py - API principal
- /app/frontend/src/App.js - Frontend

---

## INSTRUÇÕES PARA O PRÓXIMO AGENTE

1. LEIA este arquivo COMPLETAMENTE antes de implementar qualquer coisa
2. A precisão de 100% é PRIORIDADE MÁXIMA
3. Não mude o que já está funcionando sem necessidade
4. Sempre balancear informações (boas + alertas)
5. Cibi Sana é o protótipo, mas pense GLOBAL
6. Pergunte ao usuário se tiver dúvidas sobre diretrizes
