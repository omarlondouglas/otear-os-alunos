# AGI-Videos Project Consciousness

## 🚀 Overview
Sistema de automação para criação de conteúdo digital (vídeos, carrosséis, roteiros) usando agentes de IA orquestrados.

## 🛠 Tech Stack
- **Framework**: Agno (formerly Phidata) + FastAPI
- **Modelos**: Gemini 1.5 Pro/Flash
- **Banco**: PostgreSQL (Memory) + Redis (Logs)
- **Tools**: Custom tools em `app/agents/agno_tools.py`
- **Orquestração**: Synkra AIOS (God Mode) no desenvolvimento.

## 📁 Architecture (Agentes)
- **Jobs** (Estratégia): Orchestrator — coordena delegação entre membros.
- **Nolan** (Vídeo): Editor de vídeo para edições padrão (legendas, presets).
- **Beast** (Análise Viral): Analista avançado de vídeo (smart_cut, efeitos, transcrição).
- **Ogilvy** (Copy): Copywriter sênior para Reels e Carrosséis.
- **Olivetto** (Roteiro): Roteirista expert de vídeo viral.
- **GaryV** (Conteúdo): Especialista em carrosséis Instagram.
- **Scher** (Design): Diretor de arte e geração de imagens.
- **Erico** (Funil Digital): Modelagem de estilo de criadores.
- **Neumeier** (Branding): Design system, PDF, PPTX.

## 🔧 Core Commands
- **Build**: `docker-compose up --build`
- **Frontend**: `cd frontend-react && npm run dev`
- **Logs**: `python read_redis_logs.py`

## 🚨 Critical Context (Recent Fixes)
- **Tool Interception Bug**: Corrigido em `orchestration_logger.py`. Hooks do Agno DEVEM executar `function_call(**arguments)` e retornar o resultado, senão as tools retornam `None`.
- **NameError Fix**: `VIDEO_SERVICE_URL` substituído por `get_video_url()` em `agno_tools.py`.
- **Team Mode**: `mode="coordinate"` ativado no Jobs para evitar delegação ambígua.
- **Async Fix**: `orchestrator.run()` substituído por `await orchestrator.arun()` no `api_gateway.py`.

## 📜 Style Guide
- **Imports**: Usar caminhos absolutos (ex: `app.agents.agno_tools`).
- **Async**: Priorizar operações assíncronas para evitar bloqueio do FastAPI.
- **Rules**: Respeitar as regras em `.claude/rules/`.

## Git Rule
- Apos qualquer modificacao de codigo ou documentacao, commitar e fazer push para o remoto antes de encerrar a tarefa, preservando mudancas nao relacionadas.
