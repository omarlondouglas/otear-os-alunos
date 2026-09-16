# OpenSquad

Plataforma de criacao de conteudo com agentes de IA. Pesquisa noticias, cria estrategia, escreve copy, gera imagens e monta carrosseis para Instagram. Tudo automatico.

## Como funciona

```
Tema (input) --> Pesquisador --> Estrategista --> Redator --> Designer --> Imagens IA --> Revisor --> Publicador
```

Cada etapa e executada por um agente especializado orquestrado pelo Claude CLI. Checkpoints pausam para aprovacao humana antes de prosseguir.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Next.js 16, React 19, Tailwind CSS |
| Backend | Next.js API Routes, Node.js |
| Banco | Supabase (PostgreSQL) |
| Fila | BullMQ + Redis |
| IA (texto) | Claude CLI (Pro/Max via OAuth) |
| IA (imagens) | Google Gemini API |
| Storage | Cloudflare R2 / S3 (opcional, tem fallback local) |
| Deploy | Docker, EasyPanel |
| Escritorio 3D | Three.js (visualizacao dos agentes) |

## Squads disponiveis

| Squad | Descricao | Agentes |
|-------|-----------|---------|
| **noticias-carrossel-ia** | Noticias -> Carrossel Instagram | Pesquisador, Estrategista, Redator, Designer, Curador, Conceituador Visual, Gerador Imagens, Image Patcher, Revisor, Publicador |
| **anuncio-estatico** | Anuncio estatico para Meta Ads | Copywriter, Designer, Revisor |
| **slides-aula** | Apresentacao educacional (1920x1080) | Pesquisador, Estrategista, Redator, Designer, Curador, Gerador Imagens, Revisor |
| **cover-director** | Analise neuro-visual para capas | Neuro-estrategista |
| **instagram-scraper** | Download de carrosseis de perfis | Scraper (Playwright) |
| **yt-thumbnails** | Thumbnails otimizadas para YouTube | (em desenvolvimento) |

## Quick Start (local)

### 1. Clone e instale

```bash
git clone <repo-url> opensquad
cd opensquad
npm install
cd interface-app && npm install && cd ..
```

### 2. Configure o .env

```bash
cp .env.example .env
```

Preencha no minimo:

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Claude (usa seu plano Pro/Max)
CLAUDE_OAUTH_ACCESS_TOKEN=...
CLAUDE_OAUTH_REFRESH_TOKEN=...
CLAUDE_OAUTH_EXPIRES_AT=...

# Gemini (geracao de imagens)
GEMINI_API_KEY=...
```

### 3. Rode

```bash
cd interface-app
npm run dev
```

Acesse `http://localhost:3000`.

### 4. Escritorio 3D (opcional)

```bash
# Terminal separado
npm run office3d
```

Acesse `http://localhost:4200` ou pela interface (botao "Escritorio 3D").

## Deploy (Docker / EasyPanel)

### Servicos

| Servico | Porta | Entrypoint | Funcao |
|---------|-------|-----------|--------|
| **app** | 3000 | `bash entrypoint.sh` | Next.js (interface + API) |
| **worker** | - | `bash entrypoint-worker.sh` | Processa fila de jobs |
| **ws-gateway** | 3001 | `node ws-gateway.js` | WebSocket real-time |
| **redis** | 6379 | `redis-server` | Fila de jobs + pub/sub |

### Build

```bash
docker-compose up --build
```

### Env vars do EasyPanel

Todas as vars do `.env.example` devem ser configuradas no servico **app**. O **worker** precisa das mesmas vars (compartilha o mesmo Dockerfile).

Vars adicionais para producao:

```env
# Redis (obrigatorio se usar worker)
REDIS_URL=redis://default:SENHA@redis:6379

# Instagram (analise de perfil)
INSTAGRAM_USERNAME=seu_usuario
INSTAGRAM_PASSWORD=sua_senha

# S3/R2 (persistencia de imagens entre deploys)
S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=opensquad
S3_PUBLIC_URL=https://cdn.seudominio.com
```

**Sem Redis:** O app funciona em modo legacy (spawn direto do Claude CLI, sem fila). Remova `REDIS_URL` para desativar.

**Sem S3:** Imagens sao salvas localmente em `_opensquad/_image-bank/`. Carrosseis antigos nao sobrevivem redeploys.

## Estrutura do projeto

```
opensquad/
├── interface-app/          # Next.js frontend + API routes
│   ├── src/app/api/        # 15+ API routes (run-squad, carousels, agents, etc)
│   ├── src/components/     # Dashboard, SlideEditor, CarouselShowcase, Onboarding
│   └── src/lib/            # Supabase, S3, render-slides, prompt-builder
├── squads/                 # Squads de agentes (YAML + .agent.md)
│   └── {nome}/
│       ├── squad.yaml      # Config do squad (pipeline steps, skills)
│       ├── agents/         # Agentes (.agent.md com persona, principios, tasks)
│       ├── pipeline/       # Steps, data, checkpoints
│       ├── _memory/        # Memoria persistente do squad
│       └── output/         # Saida (carrosseis, imagens, etc)
├── _opensquad/             # Core do framework
│   ├── core/               # Architect agent + best practices (23 guias)
│   ├── _memory/            # Contexto da empresa (company.md)
│   └── config/             # Configs (Playwright, etc)
├── skills/                 # Skills compartilhadas (8 disponiveis)
│   ├── image-creator/      # HTML -> imagem (Playwright)
│   ├── instagram-publisher/# Publicacao via Graph API
│   └── ...
├── agent-dashboard-main/   # Escritorio 3D (Three.js)
├── Dockerfile              # Build multi-stage (Node 22 Alpine + Chromium)
├── docker-compose.yml      # 4 servicos (app, worker, ws-gateway, redis)
└── .env.example            # Template de variaveis
```

## SaaS Multi-tenant

O sistema suporta multi-tenant via Supabase Auth:

| Plano | Runs/mes | Preco |
|-------|---------|-------|
| Free | 5 | Gratis |
| Starter | 50 | - |
| Pro | Ilimitado | - |

Cada tenant tem:
- Diretorio isolado (`data/{tenantId}/`)
- Limite de execucoes
- Squads e memoria proprios

## Pipeline do carrossel

```
1. [CHECKPOINT] Tema        -> Usuario define o assunto
2. Pesquisador              -> Busca noticias (Brave Search / Google News RSS)
3. Estrategista             -> Define angulo, publico, tom
4. Redator                  -> Escreve copy de cada slide (40-80 palavras)
5. Designer                 -> Cria slides-data.json (layout, temas, elementos)
6. [CHECKPOINT] Imagens     -> Aprovacao antes de gerar
7. Curador de Imagens       -> Seleciona do banco de imagens existente
8. Conceituador Visual      -> Define conceito visual unico por noticia
9. Gerador de Imagens       -> Gera com Gemini API (1024x1024+)
10. Image Patcher           -> Aplica imagens nos slides
```

Resultado: 7-10 slides JPG (1080x1440) prontos para Instagram.

## API Routes

| Rota | Metodo | Funcao |
|------|--------|--------|
| `/api/run-squad` | POST | Inicia pipeline |
| `/api/run-squad` | GET | Status do run atual |
| `/api/run-squad` | DELETE | Para execucao |
| `/api/carousels` | GET | Lista carrosseis (local + S3) |
| `/api/squad-progress` | GET | Progresso com slides renderizados |
| `/api/slides-editor` | GET/POST | Ler/salvar slides-data.json |
| `/api/carousel-content` | GET | Conteudo do ultimo carrossel |
| `/api/agents` | GET | Lista agentes (para escritorio 3D) |
| `/api/image-bank` | GET/POST | Banco de imagens (upload/listagem) |
| `/api/image-bank/file` | GET | Serve imagens locais do banco |
| `/api/analyze-profile` | GET/POST | Analise visual de perfil Instagram |
| `/api/extract-design-system` | POST | Extrai design system de website |
| `/api/collect-news` | POST | Coleta de noticias |
| `/api/news` | GET | Lista noticias do banco |
| `/api/provision` | POST | Provisiona novo tenant |
| `/api/health` | GET | Health check |

## Escritorio 3D

Visualizacao em tempo real dos agentes trabalhando. Cada agente aparece como personagem 3D sentado em uma mesa no escritorio virtual.

- **Sem pipeline rodando:** Todos os agentes ficam inativos (cinza)
- **Pipeline rodando:** Agentes acendem (verde) conforme executam, com baloes de atividade
- **Polling:** Atualiza a cada 15 segundos via `/api/agents`
- **Temas:** 5 temas visuais (Modern Office, Startup Garage, Cyberpunk Lab, Nature Retreat, Cozy Studio)
- **Interacao:** Arrastar para rotacionar, scroll para zoom, click para detalhes do agente

Acesse pelo botao "Escritorio 3D" na interface ou diretamente em `/office3d/index.html`.

## Licenca

Projeto privado. Todos os direitos reservados.
