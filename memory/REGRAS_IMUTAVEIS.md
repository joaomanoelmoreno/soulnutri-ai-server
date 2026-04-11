# REGRAS IMUTÁVEIS DO SOULNUTRI - NÃO MODIFICAR
# Este arquivo é a lei suprema do projeto. Nenhum agente pode violar estas regras.
# Qualquer mudança que contradiga este arquivo DEVE ser revertida imediatamente.

## 1. MOTOR DE RECONHECIMENTO - HARD LOCK

### Cibi Sana (restaurant=cibi_sana)
- **Engine**: OpenCLIP ONNX EXCLUSIVAMENTE
- **Gemini**: BLOQUEADO. Proibido usar Gemini para identificação no Cibi Sana
- **Tempo máximo de resposta**: 500ms (0.5 segundo)
- **Contexto**: Usuário está em pé no buffet, prato na mão, celular na outra
- **MongoDB**: NÃO consultar durante identify (dados de texto vêm do /ai/enrich)
- **Resposta imediata DEVE conter**: nome do prato, ingredientes, ficha nutricional, alertas alérgenos
- **NÃO alterar**: Lógica de CLIP search, scoring, ou policy

### Modo Externo (restaurant!=cibi_sana)
- **Engine**: Gemini 2.5 Flash Lite EXCLUSIVAMENTE
- **CLIP**: DESLIGADO (evita retornar pratos calibrados do Cibi Sana)
- **Tempo máximo de resposta**: 1-2 segundos (máximo absoluto: 2.5s)
- **NÃO alterar**: Lógica de chamada Gemini, formato de resposta

## 2. FLUXO PREMIUM - ENRIQUECIMENTO EM BACKGROUND

### Regra de ouro
- O `/api/ai/identify` retorna RÁPIDO com dados básicos
- O `/api/ai/enrich` roda em BACKGROUND e traz: benefícios ricos, riscos detalhados, curiosidades, combinações, notícias, alertas de histórico
- O enrich NUNCA deve bloquear a resposta do identify

### Propagação para o Prato
- Quando enrich completa, DEVE atualizar TANTO o `result` QUANTO os `plateItems`
- Se o usuário já adicionou ao prato antes do enrich terminar, os dados DEVEM chegar depois
- Na vista "Prato Completo" (mesa), todo conteúdo premium DEVE aparecer quando disponível
- Usar `setPlateItems` com matching por `dish_display` para atualizar itens existentes

## 3. TTS (Text-to-Speech)
- **Biblioteca**: gTTS (GRATUITO, pt-BR) - NUNCA usar OpenAI TTS
- **Velocidade**: 1.35x via pydub/ffmpeg
- **Custo**: ZERO (gTTS é gratuito, não consome créditos de IA)

### Áudio no SCAN (resultado imediato, buffet)
- Dados enviados ao TTS: APENAS nome do prato, categoria, ficha nutricional, ingredientes, alérgenos, alertas
- NÃO inclui: benefícios, riscos, curiosidades, combinações, notícias (esses vêm do enrich que ainda está processando)
- Propósito: Deficiente visual em pé no buffet precisa saber RÁPIDO o que escaneou

### Áudio no PRATO COMPLETO (mesa view, premium)
- Dados enviados ao TTS: TUDO — benefícios, riscos, curiosidades, combinações, notícias, alertas de saúde, verdade/mito
- Botão desabilitado enquanto enrich está carregando (aguardar dados premium)
- Botão dourado (diferenciado do verde do scan) para indicar conteúdo premium
- Propósito: Deficiente visual sentado, prato completo, quer ouvir TODAS as informações premium

## 4. ECONOMIA DE CRÉDITOS
- Cibi Sana identify: ZERO créditos (CLIP local)
- Enrich: 1 chamada Gemini por prato (background)
- TTS: ZERO créditos (gTTS local)
- NUNCA adicionar chamadas de IA desnecessárias
- NUNCA mudar gTTS para OpenAI TTS
- NUNCA adicionar Gemini ao fluxo de identify do Cibi Sana

## 5. SERVICE WORKER / PWA
- SW é MINIMAL (v10+): NÃO cacheia nada, NÃO intercepta fetch
- SW existe APENAS para manter PWA instalável
- Backend serve sw.js com no-cache headers
- NUNCA adicionar cache agressivo ao SW novamente

## 6. DADOS
- Proporções nutricionais: NUNCA dividir igualmente por ingrediente (usar proporções comerciais)
- Base de pratos: 200 pratos oficiais (não inflar com pratos da IA)
- Admin: Apenas reflete o banco de dados oficial
