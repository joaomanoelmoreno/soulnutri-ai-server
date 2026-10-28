# Canelone — endurecimento experimental da segurança nutricional

Status: `LOCAL_ONLY_NOT_DEPLOYED`

## Contrato final

- Identidade visual, ranking, score e confiança permanecem auditáveis e inalterados.
- `dish_display` público é `Canelone` enquanto o membro não estiver confirmado.
- A resposta lista `Canelone 4 Queijos` e `Canelone de Espinafre` e mantém a orientação para conferir a plaquinha ou consultar o atendente.
- Nutrição, ingredientes, alergênicos e enriquecimento Premium específicos ficam indisponíveis.
- `/ai/enrich` e `/premium/log-meal` recusam os nomes protegidos antes de chamada paga ou escrita.
- Não existe confirmação pública implementada; portanto a ficha específica não é liberada.

## Matriz de falhas

| Cenário | Resultado experimental |
|---|---|
| Família Mongo válida | Família exibida; ficha específica retida |
| Mongo indisponível | Fail-closed local para os dois IDs conhecidos |
| Consulta `dishes.family` falha | Fail-closed local |
| Documento `dish_families` ausente | Fail-closed local |
| Membros ausentes/inconsistentes | Cadastro local aprovado prevalece |
| Flag Mongo ausente | Proteção local permanece ativa |
| Cache visual v2 | Identidade cacheada é reprocessada e retida |
| Cache legado de resposta | Payload é sanitizado antes da resposta |
| Frontend antigo | Recebe `dish_display=Canelone` e nenhum dado específico |
| Premium | Enriquecimento específico indisponível |
| Persistência | Refeição ambígua recusada antes da escrita |
| Scanner atual | Exibe família, sem estimativa nutricional substituta |
| Pastel | Comportamento anterior preservado |
| Gratinados | Comportamento anterior preservado; risco legado documentado |
| Outra massa | Nenhuma retenção ou família Canelone indevida |

## Testes

- 16 testes direcionados de backend: PASS.
- 3 testes direcionados de frontend: PASS.
- 79 testes de regressão v2/famílias: PASS.
- Build frontend: PASS, apenas warnings ESLint preexistentes.
- Avaliação offline: 7/7 fotos reais de 4 Queijos e 10/10 referências de Espinafre com ficha retida; 0/5 controles negativos receberam a família.
- Índice congelado: 237 classes, 1.518 embeddings, dimensão 512; arquivos não modificados.

## Risco legado separado — Gratinados

Gratinados continua exibindo o nome da família, mas autoriza a ficha nutricional do membro top-1. O comportamento não foi alterado nesta etapa porque o endurecimento é opt-in e a decisão humana atual cobre somente Canelone.

## Limitações

- Não há mecanismo público existente que transforme a consulta à plaquinha/atendente em confirmação no aplicativo.
- Enquanto isso, a nutrição específica de Canelone permanece indisponível.
- Uma futura classe de Canelone precisa entrar simultaneamente no cadastro Mongo e na lista local de segurança para manter o fail-closed sem Mongo.
- Os resultados P0 são regressão conhecida, não validação independente de acurácia.
