# SoulNutri - Product Requirements Document

## Visão Geral
Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens.
O objetivo é fornecer informações detalhadas e personalizadas com alta velocidade (< 500ms) e precisão (> 90%).

## 🚀 STATUS: PRONTO PARA DEPLOY (01/02/2026)

Ver relatório técnico completo em: `/app/memory/TECHNICAL_STATUS_REPORT.md`

## O que foi implementado

### 01/02/2026 - Estabilização e Ativação Google API

**✅ Implementado:**
- **SDK Google atualizado**: Migrado de `google.generativeai` (descontinuado) para `google-genai`
- **Billing Google ativado**: Projeto vinculado à conta de faturamento (R$ 1.904 de crédito)
- **Endpoint de monitoramento**: `GET /api/ai/google-quota-status` para verificar cota
- **Logs melhorados**: Sistema indica claramente qual API está sendo usada
- **Documentação completa**: Relatório técnico para futuros agentes

**Performance Testada (25 pratos externos):**
- Taxa de sucesso: 100%
- Tempo médio: 1.059ms
- Custo por identificação: ~R$ 0,001

**Arquivos modificados:**
- `/app/backend/services/gemini_flash_service.py` - Novo SDK + logs
- `/app/backend/server.py` - Endpoint de monitoramento de cota
- `/app/memory/TECHNICAL_STATUS_REPORT.md` - Novo relatório técnico

---

### 01/02/2026 - Tabela TACO Completa Oficial

**✅ Implementado:**
- **Tabela TACO expandida de 150 para 597 alimentos** - Base oficial da UNICAMP/NEPA (4ª edição)
- **Categorias incluídas**: 15 categorias (Carnes, Peixes, Aves, Laticínios, Cereais, Frutas, Verduras, Leguminosas, etc.)
- **Novos nutrientes rastreados**: colesterol, vitamina C, por alimento
- **Funções preservadas**: `buscar_dados_taco()`, `calcular_nutricao_prato()`, `calcular_percentual_vdr()`, `search_taco()`
- **Mapeamento atualizado**: Ingredientes comuns mapeados para chaves TACO corretas
- **ZERO créditos de IA** - 100% dados locais

**Tamanho do arquivo**: 174 KB (vs 50 KB anterior)

**Arquivos modificados:**
- `/app/backend/data/taco_database.py` - Nova versão com 597 alimentos
- `/app/backend/data/taco_database_BACKUP_*.py` - Backup da versão anterior

**Pesquisa de Armazenamento Externo (para próxima fase):**
- **Cloudflare R2 recomendado**: 10GB grátis, ZERO taxas de egress, S3-compatível
- Sem impacto na latência (CDN global)
- Integração simples via boto3

---

### 30/01/2026 - Atualização do Dataset e Reindexação

**✅ Implementado:**
- **Download de imagens do Google Drive**: Baixadas +465 novas imagens de pratos do buffet Cibi Sana
- **Organização automática**: Script `organize_images.py` para mapear arquivos às pastas corretas
- **Reindexação completa CLIP**: Índice reconstruído com ZERO créditos (modelo local)
- **Resultado final**:
  - 313 pratos indexados
  - 3291 imagens no dataset (aumento de ~17%)
  - 134 pastas ainda sem imagens (reduzido de 169)

**✅ Confirmado:**
- Consumo de créditos PARADO (210 créditos gastos antes da correção)
- Gemini desativado para Brasil permanece inativo

**Arquivos criados/modificados:**
- `/app/backend/organize_images.py` - Script para organizar imagens por nome
- `/app/datasets/dish_index.json` - Novo índice com 313 pratos
- `/app/datasets/dish_index_embeddings.npy` - Embeddings CLIP atualizados

**Pratos com mais imagens novas:**
- frangocremedelimaosalnegro: +31
- cevicheperuano: +30
- beringelaaolimao: +29
- brocoliscouveflorgratinado: +26
- costelinhacibisana: +26

### 30/01/2026 - Correções de UX Premium e Conteúdo

**✅ Implementado:**
- **Disclaimer Jurídico**: Adicionado aviso legal no formulário de registro Premium informando que o app não substitui orientação médica/nutricional
- **Edição de Perfil Premium**: Novo componente `PremiumEditProfile` e endpoint `/api/premium/update-profile` para atualizar dados do usuário
- **Aba Perfil Simplificada**: Removido bloco redundante de "Criar Novo Perfil", adicionado botão "✏️ Editar Perfil" funcional
- **Correção Info Salmão**: Radar de Notícias agora diferencia salmão de cativeiro vs selvagem, alertando sobre corantes artificiais e antibióticos
- **Explicação Ferro Heme**: Adicionada explicação clara sobre o que é ferro heme vs não-heme, com fontes científicas (NIH)
- **"Você Sabia" na tela principal**: Seção de curiosidades agora aparece na tela de resultado principal
- **"Combinações" na tela principal**: Combinações benéficas exibidas na tela de resultado
- **Radar Alert clicável**: Alerta do Radar visível na tela principal com opção de ver detalhes
- **Consistência de Alérgenos**: Lógica melhorada para detectar alérgenos tanto de campos booleanos quanto de texto nos riscos
- **Soja adicionada aos alérgenos**: Nova opção de alérgeno soja na detecção

**Arquivos modificados:**
- `/app/frontend/src/Premium.jsx` - Disclaimer + PremiumEditProfile
- `/app/frontend/src/App.js` - Radar na tela principal + lógica alérgenos
- `/app/backend/server.py` - Endpoints get-profile e update-profile
- `/app/backend/data/radar_noticias.py` - Info salmão e ferro heme

**Testes realizados:**
- Backend: 22/23 testes (96%)
- Frontend: 100% das funcionalidades verificadas

### 30/01/2026 - Sessão Anterior (FORK)

**✅ Implementado:**
- Tabela TACO expandida (~150 alimentos)
- Radar de Notícias v2 com conteúdo balanceado (OMS, FDA, ANVISA)
- Contador Premium com análise semanal
- Formulário Premium com restrições e alergias como checkboxes
- Aba "Perfil" no contador Premium
- Remoção de "Condições de Saúde" (por questões jurídicas)

### Sessões Anteriores

**🔬 Contador Premium Completo:**
- Endpoint `GET /api/premium/daily-full` - Análise diária com vitaminas, minerais e alertas
- Endpoint `GET /api/premium/weekly-analysis` - Análise semanal com tendências e pontuação
- Rastreamento de: Vitamina A, C, B12, Ferro, Cálcio, Sódio, Potássio, Zinco, Fibras, Açúcar
- Pontuação semanal de 0-100 com classificação
- Toggle entre visão "Hoje" e "Semana" no app

**📰 Radar de Notícias EXPANDIDO (v2):**
- Conteúdo balanceado: benefícios + alertas de saúde pública
- Fontes confiáveis: ANVISA, FDA, OMS, Harvard Health, periódicos científicos
- Alertas sobre carnes processadas (classificação OMS/IARC)
- **ZERO créditos de IA** - 100% processamento local

**📊 Tabela TACO EXPANDIDA (~150 alimentos):**
- Base expandida de 50 para ~150 alimentos brasileiros
- **ZERO créditos de IA** - 100% dados locais

**🤖 Revisão em Lote com IA:**
- Endpoint `POST /api/admin/revisar-lote-ia` para revisar múltiplos pratos
- Processa até 20 pratos por vez com Gemini Flash

---

## 🔒 ARQUITETURA DE IA - TRAVADA (01/02/2026)

### Fluxo de Identificação (NÃO ALTERAR)
```
┌─────────────────────────────────────────────────────────────┐
│                    IMAGEM RECEBIDA                          │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  NÍVEL 1: CLIP LOCAL (GRÁTIS, ~200ms)                       │
│  - Modelo: clip-vit-base-patch32                            │
│  - Embeddings: 2301 (pratos Cibi Sana)                      │
│  - Arquivo: /app/backend/ai/index.py                        │
│  - Calibração de confiança implementada                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
            Confiança >= 90%?
           /                \
         SIM                NÃO
          │                  │
          ▼                  ▼
┌──────────────┐   ┌─────────────────────────────────────────┐
│   RETORNA    │   │  NÍVEL 2: GEMINI FLASH (PAGO, ~300ms)   │
│   RESULTADO  │   │  - Modelo: gemini-2.0-flash-lite         │
│   DO CLIP    │   │  - API: Google AI (GOOGLE_API_KEY)       │
│              │   │  - Custo: ~R$ 0,0006/identificação       │
│              │   │  - Arquivo: gemini_flash_service.py      │
└──────────────┘   └─────────────────────┬───────────────────┘
                                         │
                               Google OK (200)?
                              /              \
                            SIM              NÃO (429)
                             │                │
                             ▼                ▼
                   ┌──────────────┐  ┌────────────────────────┐
                   │   RETORNA    │  │  FALLBACK: EMERGENT    │
                   │   RESULTADO  │  │  - Mais lento (~5s)    │
                   │   GEMINI     │  │  - Mais caro           │
                   │              │  │  - Só em emergência    │
                   └──────────────┘  └────────────────────────┘
```

### Configuração de Chaves (backend/.env)
```
GOOGLE_API_KEY=xxx     # Chave do Google AI Studio (PRIORITÁRIA)
EMERGENT_LLM_KEY=xxx   # Fallback apenas
```

### Performance Esperada (com Google Billing ativo)
| Cenário | Tempo | Custo |
|---------|-------|-------|
| Prato Cibi Sana (CLIP) | ~200ms | GRÁTIS |
| Prato Externo (Gemini) | ~300-500ms | ~R$ 0,0006 |
| Fallback Emergent | ~5000ms | ~R$ 0,01 |

### Endpoint de Monitoramento
- `GET /api/ai/google-quota-status` - Verifica se Google API está disponível

---

## Arquitetura

```
/app
├── backend/
│   ├── ai/
│   ├── data/
│   │   ├── taco_database.py       # ~150 alimentos brasileiros
│   │   └── radar_noticias.py      # Fatos sobre alimentos
│   ├── services/
│   │   ├── gemini_flash_service.py
│   │   └── nutrition_premium_service.py
│   └── server.py
├── frontend/
│   └── src/
│       ├── App.js
│       ├── Admin.js
│       ├── Premium.jsx            # Register, Login, DailyCounter, EditProfile
│       └── Premium.css
└── memory/
    └── PRD.md
```

## Endpoints Principais

### Premium
- `POST /api/premium/register` - Registro de novo usuário
- `POST /api/premium/login` - Login com nome + PIN
- `GET /api/premium/get-profile` - Obter perfil para edição
- `POST /api/premium/update-profile` - Atualizar perfil existente
- `GET /api/premium/daily-summary` - Resumo diário de calorias
- `GET /api/premium/daily-full` - Análise completa do dia
- `GET /api/premium/weekly-analysis` - Análise semanal

### Radar de Notícias
- `GET /api/radar/alimentos/{nome}` - Fatos sobre um alimento

### Identificação
- `POST /api/ai/identify` - Identifica prato por imagem (CLIP local + Gemini Flash fallback)
- `POST /api/ai/identify-flash` - Identificação direta via Gemini Flash

## Backlog

### P0 - Crítico ✅ CONCLUÍDO
- [x] Disclaimer jurídico
- [x] Edição de perfil Premium
- [x] Corrigir info do salmão (cativeiro vs selvagem)
- [x] Explicar Ferro Heme
- [x] Exibir "Você Sabia" e "Combinações" na tela principal
- [x] Consistência de alérgenos

### P1 - Alto
- [ ] Análise personalizada do prato para usuários Premium ("Olá João, seu prato...")
- [ ] Melhorar tela resumo no buffet com informações de decisão rápida
- [ ] Resolver instabilidade da câmera (Error Boundary)
- [ ] Investigar falhas pontuais no reconhecimento

### P2 - Médio
- [ ] Sistema de pagamento Stripe para Premium
- [ ] Refatorar App.js (componente monolítico)
- [ ] i18n completo
- [ ] Implementar endpoint /api/ai/combinations

## 3rd Party Integrations
- **Google Gemini Flash**: Fallback de reconhecimento via `EMERGENT_LLM_KEY`
- **Hugging Face**: Modelo `clip-vit-base-patch32` para reconhecimento local

## Credenciais de Teste
- Nome: Teste, PIN: 1234
