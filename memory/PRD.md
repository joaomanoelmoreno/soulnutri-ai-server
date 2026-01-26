# SoulNutri - Product Requirements Document

**Última atualização:** 26 Janeiro 2026
**Versão:** 2.3

---

## 1. Visão do Produto

**SoulNutri** é um agente de nutrição virtual que identifica pratos em tempo real a partir de imagens, fornecendo informações nutricionais detalhadas e personalizadas.

**Slogan:** "Porque nutre também a sua alma"

**Missão:** Atuar como um "radar do prato", focando em segurança alimentar e informação de valor em tempo real.

---

## 2. Status Atual

### Dataset
- **499 pratos** cadastrados
- **1806+ imagens** indexadas
- Pratos do CibiSana + pratos genéricos

### URLs
- **Preview:** https://soulnutri.preview.emergentagent.com ✅
- **Produção:** https://soulnutri.app.br ⏳ (aguardando redeploy)

---

## 3. ✅ CORREÇÕES APLICADAS

### Erro de Deploy CUDA - RESOLVIDO
- `/app/backend/ai/__init__.py` - Forçar modo CPU ANTES de qualquer import
- **Status:** Aguardando REDEPLOY (usar "Replace Deployment" - SEM custos)

---

## 4. Funcionalidades Implementadas

### Core (FREE)
- ✅ Identificação de pratos por imagem
- ✅ Nome, categoria, ingredientes
- ✅ Informações nutricionais básicas
- ✅ Alertas de alérgenos
- ✅ **Modo Scanner Contínuo** (detecta mudança de imagem)
- ✅ **Internacionalização** (6 idiomas)
- ✅ **Popup de Boas-vindas** com seleção de idioma

### Premium (R$14,90/mês)
- ✅ Contador de calorias diário
- ✅ Alertas personalizados
- ✅ Perfil nutricional completo
- ✅ Novidades/Notícias em tempo real
- ✅ "Verdade ou Mito" educativo
- ✅ **Sistema de liberação manual** (Admin > Aba Premium)

### Internacionalização (26/01/2026)
- ✅ 🇧🇷 Português (padrão)
- ✅ 🇺🇸 English
- ✅ 🇪🇸 Español
- ✅ 🇫🇷 Français
- ✅ 🇩🇪 Deutsch
- ✅ 🇨🇳 中文 (Mandarim)
- **Tecnologia:** LibreTranslate (GRATUITO e open-source)
- **Seletor de idioma** no header
- **Popup de boas-vindas** para novos usuários

### Painel Admin (/admin)
- ✅ Gerenciamento de pratos (criar, editar, excluir)
- ✅ Edição completa: nome, categoria, ingredientes, nutrição, benefícios, riscos
- ✅ Aba Novidades para informações em tempo real
- ✅ Aba Premium para liberar/bloquear acesso manualmente

---

## 5. Backlog Priorizado

### P0 - BLOQUEADOR
- [x] ~~Resolver erro CUDA no deploy~~ ✅ RESOLVIDO
- [ ] **Fazer REDEPLOY** para aplicar correção em produção

### P1 - Importante
- [ ] Indicadores Premium (🔒 cadeados) para versão Free
- [ ] Trial 7 dias grátis
- [ ] Padronizar cores da tela Premium
- [ ] Testar internacionalização em produção

### P2 - Desejável
- [x] ~~Internacionalização~~ ✅ IMPLEMENTADO (6 idiomas)
- [x] ~~Popup de boas-vindas~~ ✅ IMPLEMENTADO
- [ ] Histórico semanal com gráficos
- [ ] Fluxo de coleta de dados na balança (OCR)

---

## 6. Plano de Lançamento

### Fase 1: CibiSana (Atual)
- Foco: Validação com clientes reais no buffet
- Meta: 100 downloads, 10 assinantes Premium
- Tática: QR codes nas mesas + garçons apresentando

### Fase 2: Lojas (Após validação)
- Apple App Store ($99/ano)
- Google Play ($25 único)

---

## 7. Fluxo de Uso no Buffet

```
Cliente no buffet → Prato na mão + Celular na outra
→ Aponta para item → Scanner detecta mudança
→ Info aparece automaticamente (ZERO toques!)
→ Decide (pega ou não) → Próximo item
→ Pesa prato → Almoça
```

### Modo Scanner Contínuo
- Verifica mudança de imagem a cada 500ms
- Só faz reconhecimento se mudança > 15%
- Overlay com info aparece sobre a câmera
- Toque para ver detalhes completos

---

## 8. Arquivos Importantes

### Backend
- `/app/backend/ai/__init__.py` - Inicialização (FORÇAR CPU) ✅
- `/app/backend/ai/embedder.py` - Modelo OpenCLIP
- `/app/backend/server.py` - API principal
- `/app/backend/services/translation_service.py` - Internacionalização

### Frontend
- `/app/frontend/src/App.js` - Interface principal + WelcomePopup
- `/app/frontend/src/I18nContext.js` - Contexto de idiomas
- `/app/frontend/src/Admin.js` - Painel admin

---

## 9. Credenciais para Teste

- **Admin:** https://soulnutri.app.br/admin
- **Premium liberado via:** Admin > Aba ⭐ Premium > Liberar

---

## 10. Integrações

| Serviço | Uso | Custo |
|---------|-----|-------|
| OpenCLIP | Identificação visual | GRATUITO |
| Hugging Face | Fallback de identificação | GRATUITO |
| LibreTranslate | Tradução automática | GRATUITO |
| Gemini Vision | Fallback para pratos desconhecidos | Emergent LLM Key |

---

## 11. Contatos

- **Domínio:** soulnutri.app.br (configurado no Registro.br)
