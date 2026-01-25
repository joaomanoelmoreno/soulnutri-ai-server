# SoulNutri - Product Requirements Document

**Última atualização:** 25 Janeiro 2026
**Versão:** 2.0

---

## 1. Visão do Produto

**SoulNutri** é um agente de nutrição virtual que identifica pratos em tempo real a partir de imagens, fornecendo informações nutricionais detalhadas e personalizadas.

**Slogan:** "Porque nutre também a sua alma"

**Missão:** Atuar como um "radar do prato", focando em segurança alimentar e informação de valor em tempo real.

---

## 2. Requisitos Principais

### Performance
- Identificação < 500ms
- Precisão > 90% para pratos únicos cadastrados
- Funcionar offline (PWA)

### Funcionalidades Core (FREE)
- ✅ Identificação de pratos por imagem
- ✅ Nome, categoria, ingredientes
- ✅ Informações nutricionais básicas
- ✅ Alertas de alérgenos
- ✅ Modo multi-item (buffet)

### Funcionalidades Premium (R$14,90/mês)
- ✅ Contador de calorias diário
- ✅ Alertas personalizados (alergias cadastradas)
- ✅ Perfil nutricional completo
- ✅ Check-in de Refeição (modo buffet guiado)
- ✅ Novidades/Notícias em tempo real
- ✅ "Verdade ou Mito" educativo
- ⏳ Histórico semanal com gráficos
- ⏳ Interação com medicamentos

---

## 3. Status Atual

### Dataset
- **488 pratos** cadastrados
- **1747+ imagens** indexadas
- Pratos do CibiSana + pratos genéricos

### Tecnologia
- Frontend: React (PWA)
- Backend: FastAPI + MongoDB
- IA: OpenCLIP (embeddings) + Gemini Vision (fallback)
- Cache: Sistema de cache para reduzir chamadas API

### URL Atual
https://food-radar-5.preview.emergentagent.com

---

## 4. O que foi Implementado

### Sessão 25/01/2026
- [x] Processamento de 344 novas fotos do WeTransfer
- [x] Check-in de Refeição (Premium) - modo buffet guiado
- [x] Sistema de Novidades Premium - alertas em tempo real
- [x] Painel Admin - gerenciamento de novidades
- [x] Logo colorida atualizada no PWA

### Sessões Anteriores
- [x] Sistema de reconhecimento otimizado (v5)
- [x] Limpeza e consolidação do dataset
- [x] Regeneração de metadados via Gemini
- [x] Sistema Premium completo
- [x] PWA com instalação offline

---

## 5. Backlog Priorizado

### P0 - Crítico (Próximas Semanas)
- [ ] Teste no CibiSana com clientes reais
- [ ] QR codes para mesas
- [ ] Ajustes baseados em feedback

### P1 - Importante (Próximo Mês)
- [ ] Criar contas Apple Developer e Google Play
- [ ] Preparar assets para lojas (ícones, screenshots)
- [ ] Integrar sistema de pagamentos (In-App Purchase)
- [ ] Publicar nas lojas

### P2 - Desejável (Futuro)
- [ ] Histórico semanal com gráficos
- [ ] Fluxo de coleta de dados na balança (OCR)
- [ ] Melhorar reconhecimento de pratos múltiplos
- [ ] Treinar modelo YOLOv8 customizado

---

## 6. Problemas Conhecidos

### Resolvido
- ✅ Precisão de pratos únicos (agora 95-100%)
- ✅ Dataset desorganizado (agora limpo e padronizado)

### Em Aberto
- ⚠️ Reconhecimento de múltiplos itens (acompanhamentos) ainda desafiador
- ⚠️ Travamentos em alguns dispositivos móveis (não investigado)

---

## 7. Plano de Lançamento

### Fase 1: CibiSana (Atual)
- Foco: Validação com clientes reais
- Meta: 100 downloads, 10 assinantes Premium
- Tática: QR codes nas mesas + garçons apresentando

### Fase 2: Boca a Boca (Meses 2-3)
- Programa de indicação
- Depoimentos de clientes
- Parcerias com nutricionistas

### Fase 3: Lojas (Meses 2-4)
- Apple App Store ($99/ano)
- Google Play ($25 único)

### Fase 4: Escala (Meses 4-6)
- Outros restaurantes
- Campanhas pagas
- Influenciadores

---

## 8. Preços

| Plano | Preço |
|-------|-------|
| FREE | R$0 |
| Premium Mensal | R$14,90/mês |
| Premium Anual | R$99,90/ano |
| Promoção Lançamento | R$9,90/mês (3 meses) |

---

## 9. Integrações

- **Gemini Vision:** Análise de imagens e geração de metadados
- **OpenCLIP:** Embeddings para busca por similaridade
- **MongoDB:** Armazenamento de dados
- **Emergent Platform:** Hospedagem e deploy

---

## 10. Arquivos Importantes

- `/app/backend/services/hybrid_identify_v5.py` - Lógica de reconhecimento
- `/app/datasets/organized/` - Dataset de pratos
- `/app/frontend/src/App.js` - Interface principal
- `/app/frontend/src/CheckinRefeicao.jsx` - Check-in de refeição
- `/app/memory/BUSINESS_PLAN.md` - Plano de negócios completo
