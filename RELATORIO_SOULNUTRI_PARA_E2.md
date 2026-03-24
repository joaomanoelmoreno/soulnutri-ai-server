# RELATÓRIO COMPLETO - SOULNUTRI
## Para continuidade no Agente E2
**Data:** 27 de Janeiro de 2026
**Projeto:** SoulNutri - App de Reconhecimento de Alimentos

---

## 1. VISÃO GERAL DO PROJETO

**Objetivo:** Aplicativo de "agente de nutrição virtual" que identifica pratos em tempo real a partir de imagens, fornecendo informações nutricionais detalhadas.

**Stack Tecnológico:**
- Frontend: React (arquivo principal: `/app/frontend/src/App.js` - 2181 linhas)
- Backend: FastAPI (`/app/backend/server.py`)
- IA: OpenCLIP (embeddings visuais) + Gemini (fallback para identificação)
- Dados: Filesystem (`/app/datasets/organized/[slug]/dish_info.json`)

**URLs:**
- Preview: https://nutri-admin-fix.preview.emergentagent.com
- Admin: https://nutri-admin-fix.preview.emergentagent.com/admin
- Lista de Pratos: https://nutri-admin-fix.preview.emergentagent.com/lista-pratos.txt

---

## 2. ESTADO ATUAL DO SISTEMA

### ✅ O que FUNCIONA:
- Serviços rodando (backend, frontend, mongodb)
- 374 pastas de pratos no filesystem
- 374 arquivos dish_info.json
- Reconhecimento de alguns pratos (ex: Nachos funciona com Score 1.0)
- Painel Admin básico funcional
- Fluxo de montagem de prato com múltiplos itens

### ❌ O que NÃO FUNCIONA bem:
- **Reconhecimento com ~30% de acerto** (era melhor antes)
- Correção de pratos inconsistente (às vezes salva, às vezes não)
- Índice de embeddings com mapeamentos incorretos
- Muitos pratos retornam resultados errados

---

## 3. ARQUITETURA DO SISTEMA DE RECONHECIMENTO

```
FLUXO DE IDENTIFICAÇÃO:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Usuário envia foto                                           │
│    ↓                                                            │
│ 2. Backend recebe em /api/ai/identify                           │
│    ↓                                                            │
│ 3. Tenta match no índice LOCAL (OpenCLIP embeddings)            │
│    - Se score >= 90%: retorna resultado rápido                  │
│    - Se score < 90%: vai para Gemini                            │
│    ↓                                                            │
│ 4. FALLBACK: Gemini Vision identifica o nome do prato           │
│    ↓                                                            │
│ 5. Busca nome no índice local (text matching)                   │
│    ↓                                                            │
│ 6. Retorna informações do dish_info.json                        │
└─────────────────────────────────────────────────────────────────┘
```

### Arquivos críticos do sistema de IA:
- `/app/backend/ai/embedder.py` - Lógica principal de identificação
- `/app/backend/ai/index.py` - Gerenciamento do índice de embeddings
- `/app/backend/ai/policy.py` - Metadados dos pratos (DISH_INFO)
- `/app/datasets/dish_index.json` - Mapeamento slug -> índices de embedding
- `/app/datasets/dish_index_embeddings.npy` - Vetores de embedding (1806 x 512)

---

## 4. HISTÓRICO DE PROBLEMAS E TENTATIVAS

### Problema 1: Pratos com prefixo "unknown_"
**Descrição:** 97 pratos tinham nomes como "unknown_batata_frita" ao invés de "batata_frita"
**Tentativa:** Renomear pastas e atualizar dish_info.json
**Resultado:** ⚠️ Parcialmente resolvido - pastas renomeadas, mas índice de embeddings ficou inconsistente

### Problema 2: Índice de embeddings desatualizado
**Descrição:** Os embeddings foram gerados com slugs antigos (unknown_*). Ao renomear, o mapeamento quebrou.
**Tentativa 1:** Atualizar apenas o mapeamento no dish_index.json
**Resultado:** ❌ Erro "list index out of range" - os índices não correspondem mais

**Tentativa 2:** Reconstruir índice completo
**Resultado:** ⏳ Processo muito demorado (>15 min), não concluído

**Solução temporária:** Restaurado backup do dish_index.json

### Problema 3: Consolidação de duplicados
**Descrição:** Havia 60 grupos de pratos duplicados (ex: "saladeovos" e "saladadeovos")
**Tentativa:** Script automático de consolidação
**Resultado:** ⚠️ Consolidou os pratos mas pode ter afetado o índice

### Problema 4: Dados incompletos nos pratos
**Descrição:** Muitos pratos sem nutrição, ingredientes ou categoria
**Tentativa:** Ferramenta de auditoria + correção com IA (Gemini)
**Resultado:** ✅ Ferramenta criada em /admin -> aba Auditoria

### Problema 5: Nomes editados pelo usuário (A-C) não persistem
**Descrição:** Usuário editou nomes de pratos de A a C no Admin, mas não estão sendo salvos
**Status:** 🔍 Não investigado completamente

---

## 5. ESTRUTURA DE DADOS ATUAL

### Filesystem:
```
/app/datasets/organized/
├── [slug]/
│   ├── dish_info.json      # Metadados do prato
│   ├── imagem1.jpg
│   ├── imagem2.jpg
│   └── ...
```

### Exemplo de dish_info.json:
```json
{
  "nome": "Nachos",
  "slug": "nachos",
  "categoria": "vegano",
  "ingredientes": ["Tortilhas de milho", "Sal", "Óleo"],
  "descricao": "Nachos são pedaços de tortilhas...",
  "beneficios": ["Fonte de carboidratos"],
  "riscos": ["Alto teor de sódio"],
  "nutricao": {
    "calorias": "140 kcal",
    "proteinas": "2g",
    "carboidratos": "18g",
    "gorduras": "7g"
  },
  "contem_gluten": false,
  "contem_lactose": false
}
```

### Índice de embeddings:
```
/app/datasets/dish_index.json:
{
  "dishes": ["slug1", "slug2", ...],
  "dish_to_idx": {
    "slug1": [0, 1, 2],      // índices no array de embeddings
    "slug2": [3, 4, 5, 6],
    ...
  }
}

/app/datasets/dish_index_embeddings.npy:
- Array numpy (1806, 512) - 1806 embeddings de 512 dimensões
```

---

## 6. ESTATÍSTICAS ATUAIS

| Métrica | Valor |
|---------|-------|
| Total de pastas de pratos | 374 |
| Pastas com "unknown" no nome | 0 |
| Arquivos dish_info.json | 374 |
| Pratos no índice (dish_to_idx) | 492 |
| Total de embeddings | 1806 |
| Slugs com "unknown" no índice | 7 |
| Taxa de acerto atual | ~30% |

---

## 7. PROBLEMAS CONHECIDOS NÃO RESOLVIDOS

1. **Índice de embeddings inconsistente** - Os embeddings foram gerados com nomes antigos
2. **7 slugs "unknown" ainda no índice** - unknownbúnchả, unknownkibbeh, etc.
3. **Salvamento no Admin inconsistente** - Às vezes funciona, às vezes não
4. **App.js muito grande** - 2181 linhas, difícil manutenção
5. **Velocidade da IA** - Fallback para Gemini adiciona 3-5s de latência

---

## 8. ARQUIVOS DE BACKUP DISPONÍVEIS

```
/app/datasets/dish_index_backup_20260127_153624.json  # Backup funcional
/app/datasets/dish_index_embeddings_backup_*.npy      # Se existir
```

---

## 9. ENDPOINTS PRINCIPAIS DA API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| /api/ai/identify | POST | Identificar prato por imagem |
| /api/ai/status | GET | Status do sistema de IA |
| /api/admin/dishes | GET | Listar todos os pratos |
| /api/admin/dishes/{slug} | PUT | Atualizar prato |
| /api/admin/audit | GET | Auditoria de qualidade dos dados |
| /api/admin/audit/fix-single/{slug} | POST | Corrigir prato com IA |
| /api/admin/duplicates | GET | Listar grupos de duplicados |

---

## 10. RECOMENDAÇÕES PARA O E2

### Prioridade ALTA:
1. **Reconstruir o índice de embeddings do zero** - É a única forma de garantir correspondência correta entre imagens e slugs
2. **Validar que todos os pratos têm dish_info.json correto**
3. **Testar reconhecimento com amostra representativa**

### Prioridade MÉDIA:
4. **Investigar por que salvamento no Admin falha às vezes**
5. **Remover os 7 slugs "unknown" restantes do índice**
6. **Implementar sistema de backup automático antes de alterações**

### Prioridade BAIXA:
7. **Refatorar App.js em componentes menores**
8. **Otimizar velocidade da IA (reduzir uso do Gemini)**
9. **Completar internacionalização (i18n)**

---

## 11. CREDENCIAIS E CONFIGURAÇÕES

- **MongoDB**: Configurado via MONGO_URL em `/app/backend/.env`
- **Gemini API**: Usa EMERGENT_LLM_KEY (chave universal Emergent)
- **Admin**: Não requer autenticação (acesso direto em /admin)

---

## 12. CONTATO E SUPORTE

- O usuário já enviou email para support@emergent.sh
- Discord: https://discord.gg/VzKfwCXC4A
- Job ID disponível no botão "i" no canto superior direito

---

**FIM DO RELATÓRIO**

*Documento gerado automaticamente para continuidade no Agente E2*
