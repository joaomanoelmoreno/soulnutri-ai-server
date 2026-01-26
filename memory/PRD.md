# SoulNutri - Product Requirements Document

**Última atualização:** 26 Janeiro 2026
**Versão:** 2.1

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
- **Preview:** https://food-radar-5.preview.emergentagent.com ✅
- **Produção:** https://soulnutri.app.br ❌ (erro CUDA pendente)

---

## 3. BLOQUEADOR CRÍTICO - Erro de Deploy

### Problema
```
libcublas.so.*[0-9] not found in the system path
```

### Causa
PyTorch está tentando usar bibliotecas CUDA/GPU, mas o ambiente Kubernetes de produção NÃO tem GPU.

### Correções Aplicadas (preview funciona)
- `/app/backend/ai/embedder.py` - adicionado `os.environ["CUDA_VISIBLE_DEVICES"] = ""`

### Ainda Necessário
- Forçar CPU em `/app/backend/ai/__init__.py` ANTES de qualquer import
- Verificar todos os arquivos que importam torch

---

## 4. Funcionalidades Implementadas

### Core (FREE)
- ✅ Identificação de pratos por imagem
- ✅ Nome, categoria, ingredientes
- ✅ Informações nutricionais básicas
- ✅ Alertas de alérgenos
- ✅ **Modo Scanner Contínuo** (detecta mudança de imagem)

### Premium (R$14,90/mês)
- ✅ Contador de calorias diário
- ✅ Alertas personalizados
- ✅ Perfil nutricional completo
- ✅ Novidades/Notícias em tempo real
- ✅ "Verdade ou Mito" educativo
- ✅ **Sistema de liberação manual** (Admin > Aba Premium)

---

## 5. Backlog Priorizado

### P0 - BLOQUEADOR
- [ ] **Resolver erro CUDA no deploy** - forçar CPU em todos os imports de torch

### P1 - Importante
- [ ] Indicadores Premium (🔒 cadeados) para versão Free
- [ ] Trial 7 dias grátis
- [ ] Padronizar cores da tela Premium

### P2 - Desejável
- [ ] Verificar internacionalização (24 idiomas)
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

- `/app/backend/ai/embedder.py` - Modelo OpenCLIP (CORRIGIR CUDA)
- `/app/backend/ai/__init__.py` - Inicialização (FORÇAR CPU AQUI)
- `/app/backend/server.py` - API principal
- `/app/frontend/src/App.js` - Interface principal
- `/app/frontend/src/Admin.js` - Painel admin (inclui aba Premium)

---

## 9. Credenciais para Teste

- **Admin:** https://soulnutri.app.br/admin
- **Premium liberado via:** Admin > Aba ⭐ Premium > Liberar

---

## 10. Contatos

- **Domínio:** soulnutri.app.br (configurado no Registro.br)
