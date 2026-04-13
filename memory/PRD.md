# SoulNutri - Product Requirements Document

## Versao Atual: V3.2

## Stack
- Frontend: React (PWA) | Backend: FastAPI, Motor (MongoDB async)
- IA: OpenCLIP ViT-B-16 (ONNX pré-otimizado R2) | Gemini 2.5 Flash Lite (Emergent LLM Key)
- TTS: OpenAI Shimmer (Emergent Key) com fallback gTTS | DB: MongoDB Atlas | Deploy: Render Standard 1GB

## REGRAS IMUTÁVEIS → /app/memory/REGRAS_IMUTAVEIS.md

## Implementado

### V3.2 (13/Abr/2026)
- Fontes (instituições reais) em benefícios, riscos, notícias e Verdade/Mito
- Alertas nutricionais automáticos no scan (calorias, proteínas, gorduras, sódio, fibras, alérgenos) — zero créditos
- TTS OpenAI Shimmer em tudo (voz consistente scan + prato completo)
- Combinações incluídas no áudio TTS
- Anti-duplicata de pratos no prato completo
- Botão remover prato individual (X)
- Bug localização corrigido (GPS watcher parado no modal)
- Proporções nutricionais: fallback 0.10 para ingredientes desconhecidos
- Limpeza de 18 notificações "hidratar" duplicadas do banco
- Textos premium curtos (max 20 palavras)
- Notícias sem URLs falsos (apenas nome da instituição)

### V3.1 (12/Abr/2026)
- ONNX modelo pré-otimizado no R2 (sem re-export no build)
- ORT_DISABLE_ALL (compatível com CPU Render)
- Dockerfile sem torch (build 5min mais rápido)
- HSTS header + HSTS Preload submetido
- emergent-main.js condicional (só no preview)
- Enrich via useEffect (zero stale closure)
- Service Worker v10 minimal
- Health check, mensagens de erro amigáveis

## Endpoints Principais
- POST /ai/identify (CLIP + alertas automáticos)
- POST /ai/enrich (Gemini: benefícios/riscos/curiosidades/combinações/notícias/mito com fontes)
- POST /ai/tts (OpenAI Shimmer, fallback gTTS)
- GET /sw.js, /manifest.json (anti-cache)

## Backlog Priorizado

### P0 - Urgente
- (nenhum)

### P1 - Próximo
- Verificação geral de ingredientes e tabela nutricional em todos os pratos (versão gratuita e premium)
- Landing page premium com trial (aguardando mockup do usuário)
- Integração Stripe para cobrança de assinaturas
- Migração futura para key OpenAI própria (TTS) — em backlog até testes de voz

### P2 - Importante
- Revisão ingredientes/descrição pratos F-Z (usuário inserindo via admin)
- Fichas nutricionais automáticas após cadastro de ingredientes
- Melhorar tempo CLIP de 2s para <500ms (testar ORT_ENABLE_BASIC com modelo pré-otimizado)
- Notificações push: verificar se rotação diária funciona consistentemente

### P3 - Futuro
- Google Play (TWA) / Apple Store (Capacitor)
- Refatorar server.py (~5800 linhas) e App.js (~4400 linhas)
- Limpeza imagens Jiló Empanado (fotos contaminadas com Quiabo)

## Problemas Conhecidos
- Gemini pode gerar nomes de fontes imprecisos (mas não inventa URLs mais)
- 3+ usuários duplicados "Joao Manoel" no DB (update_many mitiga)
- Tempo CLIP no Render: ~2s (acima do ideal de 500ms, ORT_DISABLE_ALL necessário)
