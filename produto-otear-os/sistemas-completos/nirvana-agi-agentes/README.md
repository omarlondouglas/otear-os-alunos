# O Tear / AGI Agentes

Plataforma de criaÃ§Ã£o de conteÃºdo digital com memÃ³ria de cliente, agentes
especialistas e ferramentas para carrossÃ©is, vÃ­deos, imagens, roteiros,
referÃªncias, calendÃ¡rio editorial e biblioteca de assets.

O caminho principal agora Ã© controlado por um **ProjectOrchestrator interno**:
ele lÃª o contexto do cliente, classifica a intenÃ§Ã£o, chama a ferramenta ou
agente certo e salva aprendizados Ãºteis na memÃ³ria. Hermes continua disponÃ­vel,
mas Ã© opcional.

---

## SumÃ¡rio

- [Arquitetura Atual](#arquitetura-atual)
- [Fluxo de Conversa](#fluxo-de-conversa)
- [Papel do Hermes](#papel-do-hermes)
- [Agentes e Tools](#agentes-e-tools)
- [Stack](#stack)
- [VariÃ¡veis de Ambiente](#variÃ¡veis-de-ambiente)
- [Rodando Localmente](#rodando-localmente)
- [Endpoints Principais](#endpoints-principais)
- [MemÃ³ria do Cliente](#memÃ³ria-do-cliente)
- [ServiÃ§os Auxiliares](#serviÃ§os-auxiliares)
- [Troubleshooting](#troubleshooting)

---

## Arquitetura Atual

```mermaid
flowchart LR
    UI["Frontend React / Vite"]
    API["FastAPI :8000"]
    ORCH["ProjectOrchestrator"]
    MEM["Client Memory / Vault"]
    ROUTER["Intent Router"]
    TOOLS["Tools diretas"]
    AGENTS["Agentes especialistas Agno"]
    VIDEO["Video service :8001"]
    CAROUSEL["Carousel service :8002"]
    REMOTION["Remotion :8003"]
    IMG["chatgpt-bridge / Gemini"]
    STORE["Supabase / S3 / Local storage"]
    HERMES["Hermes opcional"]

    UI -->|/api/v1/chat/stream| API
    API --> ORCH
    ORCH --> MEM
    ORCH --> ROUTER
    ROUTER --> TOOLS
    ROUTER --> AGENTS
    TOOLS --> VIDEO
    TOOLS --> CAROUSEL
    TOOLS --> REMOTION
    TOOLS --> IMG
    TOOLS --> STORE

    UI -. VITE_ENABLE_HERMES=true .->|/api/v1/hermes/chat| HERMES
    HERMES -. agno-bridge .-> API
```

### DecisÃ£o de arquitetura

O projeto tinha duas camadas de orquestraÃ§Ã£o competindo: Hermes e Agno Team.
Isso aumentava latÃªncia e pontos de falha. Agora:

- **ProjectOrchestrator** Ã© o caminho principal da interface.
- **Hermes** vira opcional, para memÃ³ria/skills avanÃ§adas.
- **Agno Agents** continuam como executores especialistas.
- **Tools** fazem o trabalho real: gerar carrossel, editar vÃ­deo, gerar imagem,
  salvar roteiro, consultar status.

---

## Fluxo de Conversa

Fluxo padrÃ£o:

```text
Frontend React
  -> POST /api/v1/chat/stream
    -> ProjectOrchestrator
      -> carrega memÃ³ria do cliente/marca
      -> classifica intenÃ§Ã£o
      -> chama tool/agente
      -> retorna resposta e URLs/job_ids
```

IntenÃ§Ãµes roteadas hoje:

| IntenÃ§Ã£o | Exemplo | AÃ§Ã£o |
|---|---|---|
| `carousel` | "crie um carrossel sobre IA" | Monta slides e chama `generate_carousel_tool` |
| `video_edit` | "edite este vÃ­deo ..." | Cria job com `edit_video_tool` |
| `video_status` | "status do job ..." | Chama `check_video_status_tool` |
| `image` | "gere uma capa..." | Chama `generate_image_tool` |
| `script` | "crie um roteiro..." | Usa LLM de texto ou fallback estruturado |
| `strategy` | "planeje uma campanha..." | Usa LLM de texto ou plano fallback |
| `memory` | "lembre que nÃ£o gosto de roxo" | Salva aprendizado no vault |
| `general` | Conversa normal | Responde ou pergunta prÃ³ximo formato |

Arquivos principais:

- `app/orchestrator/project_orchestrator.py`
- `app/orchestrator/router.py`
- `app/orchestrator/memory.py`
- `app/api/v1/endpoints/chat.py`

---

## Papel do Hermes

Hermes nÃ£o Ã© mais obrigatÃ³rio para a interface funcionar.

Ele sÃ³ entra se o frontend tiver:

```env
VITE_ENABLE_HERMES=true
```

E o backend responder:

```text
GET /api/v1/hermes/health
ready=true
```

Quando ativo, o fluxo fica:

```text
Frontend
  -> /api/v1/hermes/chat
    -> Hermes
      -> skill agno-bridge
        -> /api/v1/agents/{agent}/run
```

Skill principal:

- `hermes_skills/agno-bridge/SKILL.md`

RecomendaÃ§Ã£o atual: deixe Hermes desligado atÃ© o nÃºcleo estar estÃ¡vel.

---

## Agentes e Tools

### Agentes especialistas

| Agente | ID/API | FunÃ§Ã£o |
|---|---|---|
| Beast | `beast` | AnÃ¡lise viral, cortes, highlights |
| Nolan | `nolan` | EdiÃ§Ã£o de vÃ­deo, legendas, presets |
| Ogilvy | `ogilvy` | Copy, roteiros, scripts |
| Olivetto | `olivetto` | Roteiro viral/VSL |
| GaryV | `garyv` | CarrossÃ©is Instagram |
| Scher | `scher` | Imagens e direÃ§Ã£o de arte |
| Erico | `erico` | Estilo de criadores e funil |
| Neumeier | `neumeier` | Branding, PDF, PPTX |

### Squads

| Squad | ID/API | FunÃ§Ã£o |
|---|---|---|
| Clara Copy | `clara_copy` | AnÃºncio estÃ¡tico |
| News Carousel | `news_carousel` | Carrossel de notÃ­cias |
| YouTuber Thumbnail | `youtuber_thumbnail` | Thumbnail YouTube |
| Neuro Cover | `neuro_cover` | Capa de mÃºsica/podcast/ebook |
| Insta Visual Ref | `insta_visual_ref` | ReferÃªncias visuais de Instagram |

### Chamada direta de agente

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/agents/garyv/run `
  -ContentType "application/json" `
  -Body '{"task":"Crie um carrossel com 3 slides sobre IA"}'
```

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Uvicorn |
| OrquestraÃ§Ã£o | `ProjectOrchestrator` prÃ³prio |
| Agentes | Agno |
| LLM | Anthropic API ou Claude CLI; fallbacks especÃ­ficos |
| Frontend | React 18 + Vite + TypeScript + Tailwind |
| Auth | Supabase Auth |
| Banco | Supabase/Postgres + SQLAlchemy |
| Fila | Celery + Redis |
| Storage | Local, S3, R2 ou MinIO |
| VÃ­deo | FFmpeg, Whisper, Remotion |
| Imagem | chatgpt-bridge / GPT image, Gemini fallback |
| MemÃ³ria | Vault Obsidian (`USER.md`, `MEMORY.md`) |

---

## VariÃ¡veis de Ambiente

Exemplos atualizados:

- Backend: `.env.example`
- Frontend: `frontend-react/.env.example`

### Backend mÃ­nimo

```env
API_KEY=change-me
ADMIN_PASSWORD=change-me-min-12
ENV=development
ENABLE_DOCS=true

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/videoeditor
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

PUBLIC_URL=http://localhost:8000
PUBLIC_API_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

CHAT_ORCHESTRATOR_TIMEOUT_S=120

MODEL_PLANNER=claude-sonnet-4-6
MODEL_WRITER=claude-sonnet-4-6
MODEL_FAST=claude-haiku-4-5-20251001

# Use Anthropic API em produÃ§Ã£o, ou Claude CLI logado em dev.
# ANTHROPIC_API_KEY=sk-ant-...

VAULT_PATH={OTEAR_VAULT_ROOT}

VIDEO_SERVICE_URL=http://localhost:8001
VIDEO_EDITOR_API_URL=http://localhost:8001
CAROUSEL_SERVICE_URL=http://localhost:8002
CAROUSEL_API_URL=http://localhost:8002
REMOTION_SERVICE_URL=http://localhost:8003

ENABLE_HERMES=false
HERMES_CHAT_TIMEOUT_S=120
```

### Frontend mÃ­nimo

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=O Tear Agentes
VITE_ENABLE_HERMES=false
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

### ObservaÃ§Ã£o sobre modelos

NÃ£o use `MODEL_PLANNER=gemini...` quando o backend estiver usando Claude CLI.
O `model_factory` agora normaliza IDs incompatÃ­veis, mas o correto Ã© manter os
modelos Claude nas variÃ¡veis `MODEL_PLANNER`, `MODEL_WRITER` e `MODEL_FAST`.

---

## Rodando Localmente

### PrÃ©-requisitos

- Python 3.11+
- Node 20+
- Redis local ou container Redis
- Postgres local ou Supabase configurado
- Claude CLI logado ou `ANTHROPIC_API_KEY`

Opcional:

- Docker / Docker Compose
- FFmpeg instalado no PATH
- Playwright Chromium para captura de referÃªncias

### Backend

```powershell
cd "{OTEAR_SO_ROOT}\referencias\nirvana-agi-agentes"
python -m pip install -r requirements.txt

$env:PYTHONIOENCODING="utf-8"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

### Frontend

```powershell
cd "{OTEAR_SO_ROOT}\referencias\nirvana-agi-agentes\frontend-react"
npm install
npm run dev
```

Acesse:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs` se `ENABLE_DOCS=true`

### Sidecars locais

```powershell
# Video service
cd "{OTEAR_SO_ROOT}\referencias\nirvana-agi-agentes\agi-videos-temp"
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Carousel service
cd "{OTEAR_SO_ROOT}\referencias\nirvana-agi-agentes\carrocel\backend"
$env:PORT="8002"
python main.py

# Remotion
cd "{OTEAR_SO_ROOT}\referencias\nirvana-agi-agentes\remotion-service"
npm install
npm run dev
```

Script Windows:

```powershell
scripts\windows\start_services.bat
```

---

## Endpoints Principais

Base: `/api/v1`

### Conversa

| MÃ©todo | Endpoint | FunÃ§Ã£o |
|---|---|---|
| POST | `/chat` | Chat via ProjectOrchestrator |
| POST | `/chat/stream` | Chat SSE via ProjectOrchestrator |
| GET | `/hermes/health` | Status Hermes |
| POST | `/hermes/chat` | Chat Hermes, se ativo |
| POST | `/agents/{name}/run` | Chamada direta de agente/squad |

### VÃ­deo

| MÃ©todo | Endpoint | FunÃ§Ã£o |
|---|---|---|
| POST | `/videos/upload` | Upload de vÃ­deo |
| POST | `/videos/edit` | Criar job de ediÃ§Ã£o |
| GET | `/videos/status/{job_id}` | Status do job |
| POST | `/videos/transcribe` | TranscriÃ§Ã£o |
| POST | `/videos/detect-highlights` | Momentos virais |
| POST | `/videos/extract-clips` | Extrair clips |
| POST | `/videos/plan-scenes` | Plano de cenas |

### ConteÃºdo e operaÃ§Ã£o

| Endpoint | FunÃ§Ã£o |
|---|---|
| `/library/*` | Biblioteca de assets |
| `/calendar/*` | CalendÃ¡rio editorial |
| `/analytics/*` | MÃ©tricas |
| `/references/*` | ReferÃªncias de criadores |
| `/graph/*` | Grafo de conexÃµes |
| `/brands/*` | Marcas |
| `/organizations/*` | Workspaces |
| `/media/*` | Uploads auxiliares |
| `/tts/*` | ElevenLabs TTS |
| `/logs/*` | Logs Redis |
| `/news/*` | News Radar |

---

## MemÃ³ria do Cliente

O sistema usa um vault Obsidian para memÃ³ria operacional:

```text
VAULT_PATH/
  .system/
    USER.md
    MEMORY.md
  references/
  news_digests/
```

O `ProjectOrchestrator` carrega:

- contexto de marca;
- contexto de usuÃ¡rio;
- `USER.md` e `MEMORY.md`;
- preferÃªncias explÃ­citas ditas no chat.

Exemplo de aprendizado:

```text
UsuÃ¡rio: "lembre que nÃ£o gosto de fundo roxo"
Sistema: salva em MEMORY.md > aprendizados do cliente
```

O objetivo Ã© permitir projetos Ãºnicos por cliente, mantendo preferÃªncias,
decisÃµes e feedback de produÃ§Ã£o.

---

## ServiÃ§os Auxiliares

### Carousel

Usado por `generate_carousel_tool`.

```env
CAROUSEL_API_URL=http://localhost:8002
CAROUSEL_API_KEY=
```

Fallback legado:

```env
CAROUSEL_WEBHOOK_URL=https://n8n.example.com/webhook/editor-de-carrossel
```

### Video

Usado por `edit_video_tool`, transcriÃ§Ã£o, highlights e status.

```env
VIDEO_SERVICE_URL=http://localhost:8001
VIDEO_EDITOR_API_URL=http://localhost:8001
VIDEO_EDITOR_API_KEY=
```

### Remotion

Usado para templates e renderizaÃ§Ãµes avanÃ§adas.

```env
REMOTION_SERVICE_URL=http://localhost:8003
```

### chatgpt-bridge

Sidecar opcional para geraÃ§Ã£o de imagem via assinatura ChatGPT/Codex auth.

```env
IMAGE_GEN_PROVIDER=auto
CHATGPT_BRIDGE_URL=http://chatgpt-bridge:10531/v1
CHATGPT_BRIDGE_MODEL=gpt-image-2
```

Setup detalhado:

- `docs/chatgpt-bridge-setup.md`

---

## Docker / EasyPanel

O `docker-compose.yml` sobe:

- `gateway` (`app.main:app`)
- `redis`
- `carousel`
- `remotion`
- `chatgpt-bridge`

Em produÃ§Ã£o, configure:

- `DATABASE_URL`
- `REDIS_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `PUBLIC_API_URL`
- `ALLOWED_ORIGINS`
- `S3_*` se usar storage externo
- `ANTHROPIC_API_KEY` ou OAuth Claude

Hermes sÃ³ deve ser habilitado quando estiver instalado e testado:

```env
ENABLE_HERMES=true
```

No frontend correspondente:

```env
VITE_ENABLE_HERMES=true
```

---

## Testes e Smoke Checks

### Import do backend

```powershell
$env:PYTHONIOENCODING="utf-8"
python -c "from app.main import app; print(app.title)"
```

### Import dos agentes legados

```powershell
$env:PYTHONIOENCODING="utf-8"
python -c "from app.agents.agno_agents import orchestrator, carousel_agent; print(orchestrator.name, carousel_agent.name)"
```

### Classificador do orquestrador

```powershell
python -c "from app.orchestrator.router import classify_intent; print(classify_intent('crie um carrossel sobre IA').value)"
```

### Health local

```powershell
Invoke-RestMethod http://localhost:8000/health
```

---

## Troubleshooting

### O backend nÃ£o sobe por banco inacessÃ­vel

O app nÃ£o deve mais quebrar no import se `DATABASE_URL` apontar para um host
inacessÃ­vel. No startup ele registra warning e continua. Para operaÃ§Ã£o real,
configure um Postgres/Supabase acessÃ­vel.

### A interface demora muito

Verifique se o caminho ativo Ã© o ProjectOrchestrator:

```env
VITE_ENABLE_HERMES=false
```

Se estiver usando Claude CLI, confirme:

```powershell
claude --version
claude -p "responda ok"
```

Em produÃ§Ã£o, prefira `ANTHROPIC_API_KEY` para reduzir latÃªncia e falhas do
subprocess.

### Hermes nÃ£o aparece

Confira:

```text
GET /api/v1/hermes/health
```

Precisa retornar `ready=true`. Caso contrÃ¡rio, mantenha:

```env
VITE_ENABLE_HERMES=false
ENABLE_HERMES=false
```

### Carrossel nÃ£o gera

Confira:

```text
GET http://localhost:8002/api/health
```

E confirme:

```env
CAROUSEL_API_URL=http://localhost:8002
```

### VÃ­deo nÃ£o cria job

Confira:

```text
GET http://localhost:8001/health
```

E confirme:

```env
VIDEO_EDITOR_API_URL=http://localhost:8001
```

### Frontend tenta Hermes sem querer

No `frontend-react/.env`:

```env
VITE_ENABLE_HERMES=false
```

Reinicie o Vite depois de mudar env.

---

## Estrutura Relevante

```text
app/
  orchestrator/
    project_orchestrator.py
    router.py
    memory.py
    schemas.py
  api/v1/endpoints/
    chat.py
    hermes_chat.py
    agents.py
    videos.py
  agents/
    agno_agents.py
    agno_tools.py
    squad_agents.py
  services/
    user_memory.py
    profile_cache.py
    hermes_engine.py

frontend-react/
  src/components/ui/ruixen-moon-chat.tsx
  src/lib/api.ts
  .env.example

hermes_skills/
  agno-bridge/

chatgpt-bridge-service/
remotion-service/
carrocel/
agi-videos-temp/
```

---

## Status Atual

- Caminho principal: `Frontend -> /chat/stream -> ProjectOrchestrator`.
- Hermes: opcional.
- Agno Team `Jobs`: legado/fallback, nÃ£o Ã© mais o caminho crÃ­tico.
- Tools: continuam responsÃ¡veis pela execuÃ§Ã£o real.
- `.env.example` e `frontend-react/.env.example` estÃ£o atualizados para essa
  arquitetura.

