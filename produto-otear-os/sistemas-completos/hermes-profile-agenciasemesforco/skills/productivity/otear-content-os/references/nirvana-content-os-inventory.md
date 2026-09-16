# Nirvana / O Tear Content OS Inventory

Session inventory captured from the user's local environment and the public `gutomec/nirvana-os-engine` repository. Use as orientation, not as a substitute for live checks when running jobs.

## Public Engine Repository

Repository:

```text
https://github.com/gutomec/nirvana-os-engine
```

Verified metadata at time of session:

```text
full_name: gutomec/nirvana-os-engine
description: Nirvana-OS â€” source-available engine for agentic work (squads, businesses, mind-clones). Developed in the open. Runtime-agnostic: Claude Code, Codex, Gemini-CLI, Antigravity, Hermes.
default_branch: main
language: TypeScript
stars: 56
forks: 17
created_at: 2026-06-16
updated_at: 2026-08-14
pushed_at: 2026-08-14
```

Important directories/files in the repo:

```text
AGENTS.md / CLAUDE.md / GEMINI.md
README.pt-BR.md
INSTALL.md
package.json
nirvana-limits.example.yaml
bin/nrv
bin/nrv-hermes
skills/_shared
skills/harness
skills/businesses
skills/squads
skills/nirvana-os
```

Engine concept:

- **Businesses:** long-lived organizations with employees, org chart, routing and memory.
- **Squads:** portable multi-agent workflows with capabilities, tasks and DAG/gates.
- **Mind-clones:** persona/voice/method DNA injected into employees.
- **Harness:** orchestrator/maestro; receives brief, consults registries, dispatches, audits and gates output.

Dispatch cascade:

```text
Business -> Squad -> agent-x fallback
```

## Local Nirvana State

Verified commands existed locally:

```text
bun
nrv
~/.nirvana
{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes/.nirvana
```

Useful diagnostic commands:

```bash
cd "{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes"
nrv --help
nrv install --check
nrv list-squads
nrv list-businesses
nrv find "<brief>"
nrv route "<brief>"
```

`nrv --help` exposed commands including:

```text
install, uninstall, installed, update
glance, tui, doctor, route, find, validate, index
dispatch, run, auto, revise, ask, launch, clean
audit-view, search, export, memory
init, resume
list-squads, list-businesses, list-clones, inspect-clone, find-clone, fix-squad
```

## Squads Found in `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes` Scope

`nrv list-squads` in `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes` returned 11 squads in `scope=merge`:

| Scope | Squad | Notes |
|---|---|---|
| project | `noticias-carrossel-ia` | protocol 5.0, news carousel project squad |
| project | `noticias-carrossel-ia.1.0.0.bak...` | backup, likely not active |
| project | `instagram-scraper` | visual reference scraping |
| global | `awwwards-singularity-studio` | high-end web/design generation |
| global | `design-system-nirvana` | design systems |
| global | `fabrica-de-genios` | mind-clone / knowledge generation |
| global | `nirvana-backend` | full backend pipeline |
| global | `nirvana-squad-creator-v3` | creates squads |
| global | `nirvana-wiki-brain` | wiki/knowledge brain |
| global | `omnidoc-vision-nirvana` | document/vision workflows |
| global | `squad-forge` | squad creation/forging |

## Businesses Found

`nrv list-businesses` returned:

| Scope | Business | Function |
|---|---|---|
| global | `business-creator` | Creates whole businesses from a natural-language brief |
| global | `software-forge` | AI-native software factory |

Notable `business-creator` capabilities:

```text
multi_agent_orchestration.business_generation_pipeline.execute
multi_agent_orchestration.business_domain_discovery.execute
multi_agent_orchestration.business_publish_flow.execute
```

Notable `software-forge` produces:

```text
monorepo-scaffold
api-spec-openapi
deployment-pipeline
system-architecture-doc
mobile apps
backend services
observability stack
CI/CD
technical specs
frontend app build
database schema
```

## Current O Tear / AGI Agentes Product Layer

Main path:

```text
{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes
```

Architecture from project README:

```text
Frontend React / Vite
  -> FastAPI :8000
    -> ProjectOrchestrator
      -> memory/vault
      -> intent router
      -> direct tools or Agno agents
```

Current intent map:

| Intent | Action |
|---|---|
| `carousel` | generate carousel tool |
| `video_edit` | edit video tool/job |
| `video_status` | check video status |
| `image` | generate image tool |
| `script` | script generation |
| `strategy` | strategic plan |
| `memory` | save memory/vault fact |
| `general` | normal response |

Planned stable capabilities in `app/capabilities/README.md`:

| Capability | Function |
|---|---|
| `research` | web/news/source research |
| `references` | creator, brand, image and video references |
| `model_extraction` | voice, visuals, hooks, narrative structure |
| `writing` | scripts, copy, captions, ads, rewriting |
| `creation` | carousel, image, thumbnail, cover, visual review |
| `video` | transcription, cuts, highlights, captions, render/status |
| `memory` | preferences, brand context, assets and learnings |

## OpenSquad and PI Squad Paths

```text
OpenSquad: {OTEAR_SO_ROOT}/referencias/opensquad
PI Squad: {OTEAR_SO_ROOT}/referencias/pi-squad
Obsidian vault: {OTEAR_VAULT_ROOT}
```

OpenSquad known squads:

```text
noticias-carrossel-ia
anuncio-estatico
slides-aula
cover-director
instagram-scraper
yt-thumbnails
vyve-identidade-visual
```

PI Squad is an `ultimate-landingpage` squad with 14 agents covering strategy, research, copy, design architecture, image creation, frontend, backend, integrations, review, deploy, versioning, scraping, orchestration and storage.

## Architecture Recommendation

Create an `O Tear Content OS` layer rather than modifying engine internals directly:

```text
Hermes Desktop
  -> skills + natural-language cockpit
  -> Nirvana harness / nrv when orchestration is needed
  -> O Tear FastAPI / ProjectOrchestrator for product jobs
  -> OpenSquad or PI Squad for structured pipelines
  -> Codex for premium image/code execution
  -> Obsidian for manuals/memory
```

Recommended next object to create in Nirvana:

```text
business: otear-content-os
```

Possible squads/capabilities:

```text
news-carousel
short-video-script
visual-reference-analysis
viral-clipper
offer-mentor
landing-page-builder
brand-system-builder
content-calendar
distribution-engine
ads-creative-lab
```

## Hermes + Codex Token Guidance

Use this durable distinction:

- Hermes with Codex as the primary model sends Hermes context once: tools, skills, memory, system and conversation. This can be more input tokens than raw Codex, but is not two agents thinking.
- Hermes calling Codex CLI as a separate executor creates a nested-agent pattern and can cost more because Hermes and Codex both reason.
- For repeated workflows, make a skill/endpoint/job and keep prompts short.

## User Preferences Captured in Workflow

- Non-technical users need interface/cockpit; do not expose terminal flows as the primary UX.
- For OpenSquad/Nirvana carousels, prefer Codex/ChatGPT Image 2 for generated images rather than Gemini.
- Do not use visible slide numbering like `01/08` on carousel slides.
- Use Obsidian for manuals and durable operating docs.
