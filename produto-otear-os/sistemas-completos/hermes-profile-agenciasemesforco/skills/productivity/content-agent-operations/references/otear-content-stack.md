# O Tear / Nirvana Content Stack Reference

Created from the session that produced `{OTEAR_VAULT_ROOT}/Manuais/Manual do ConteÃºdo Sem EsforÃ§o.md` on 2026-08-14. Treat this as a seed map, not as proof of current state; verify live files before updating manuals.

## Canonical Paths

| System | Path | Notes |
|---|---|---|
| Obsidian vault | `{OTEAR_VAULT_ROOT}` | User's vault for manuals and operational notes. |
| Nirvana / O Tear Agentes | `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes` | Main project/workspace. Nirvana data under `.nirvana`. |
| OpenSquad | `{OTEAR_SO_ROOT}/referencias/opensquad` | YAML + `.agent.md` squads for content production. |
| PI Squad | `{OTEAR_SO_ROOT}/referencias/pi-squad` | Ultimate landing page squad. |
| Hermes skills | `{HERMES_SKILLS_ROOT}` | Personal/runtime skills available to Hermes. |

## Nirvana / O Tear Agentes

Path: `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes`.

Role: broad content platform with FastAPI backend, React frontend, ProjectOrchestrator, client memory, direct tools, video services, carousel services, image generation, references, library, brands, calendar, and Agno specialist agents.

### Specialist Agents

| Agent | API ID | Use for |
|---|---|---|
| Beast | `beast` | Viral analysis, cuts, highlights. |
| Nolan | `nolan` | Video editing, captions, presets. |
| Ogilvy | `ogilvy` | Copy, hooks, scripts. |
| Olivetto | `olivetto` | Viral scripts and VSL. |
| GaryV | `garyv` | Instagram carousels. |
| Scher | `scher` | Image generation and art direction. |
| Erico | `erico` | Creator style and funnel modeling. |
| Neumeier | `neumeier` | Branding, PDF, PPTX. |

### API Squads

| Squad | API ID | Use for |
|---|---|---|
| Clara Copy | `clara_copy` | Static ads. |
| News Carousel | `news_carousel` | News-to-carousel. |
| YouTuber Thumbnail | `youtuber_thumbnail` | YouTube thumbnails. |
| Neuro Cover | `neuro_cover` | Music/podcast/ebook covers. |
| Insta Visual Ref | `insta_visual_ref` | Instagram visual reference analysis. |

### Hermes-local Skills in Nirvana Repo

| Skill folder | Function |
|---|---|
| `hermes_skills/agno-bridge` | Calls `/api/v1/agents/{agent_name}/run`. |
| `hermes_skills/otear-orchestrator` | Delegates general requests to `/api/v1/chat`. |
| `hermes_skills/news-script-adapter` | Converts news/briefings into short-form scripts. |

### Useful Endpoints

Base: `http://localhost:8000/api/v1`.

- `POST /chat/stream` â€” ProjectOrchestrator chat.
- `GET /hermes/health`, `POST /hermes/chat` â€” optional Hermes bridge.
- `POST /agents/{name}/run` â€” direct agent/squad call.
- `/videos/*` â€” upload, edit, transcribe, highlights, clip extraction.
- `/carousels/*` â€” carousel render/download/images.
- `/references/*` â€” creators, visual references, screenshots.
- `/news/*` â€” news feed/RSS/digests.
- `/library/*`, `/calendar/*`, `/brands/*`, `/media/*`, `/tts/*` â€” supporting operations.

## OpenSquad

Path: `{OTEAR_SO_ROOT}/referencias/opensquad`.

Role: explicit squad pipelines for content creation. Typical pipeline: theme -> researcher -> strategist -> writer -> designer -> images -> reviewer -> publisher.

### Squads Found

| Squad | Use for | Agents |
|---|---|---|
| `noticias-carrossel-ia` | News to Instagram carousel. | Pesquisador, Estrategista, Redator, Designer, Curador de Imagens, Conceituador Visual, Gerador de Imagens, Image Patcher, Revisor, Publicador. |
| `anuncio-estatico` | Static Meta Ads. | Clara Copy, Diego Design, Vera Veredito. |
| `slides-aula` | Educational slide decks. | Pesquisador, Estrategista, Redator, Designer, Curador, Gerador Imagens, Revisor. |
| `cover-director` | Neurovisual cover analysis. | Neuro-Estrategista. |
| `instagram-scraper` | Instagram carousel/profile collection and analysis. | Scraper. |
| `yt-thumbnails` | YouTube thumbnail concepts/prompts. | Researcher, Conceptor, Prompt Engineer, Reviewer. |
| `vyve-identidade-visual` | Visual identity/branding. | Brand Designer. |

### Important OpenSquad User Rules

- For carousel images, prefer Codex / ChatGPT Image 2 via locally authenticated Codex, not Gemini.
- Do not show visible slide numbering such as `01/08`.
- For news carousels, use `@brandsdecoded__` as an editorial inspiration adapted to O Tear, not copied literally.
- Header can be: `Powered by O Tear | @marlonlima.ia | 2026 //`.

## PI Squad / Ultimate Landing Page

Path: `{OTEAR_SO_ROOT}/referencias/pi-squad`.

Role: full-stack landing-page generation pipeline for high-conversion pages.

Main agents/components found in `squad.yaml`:

- `lp-strategist` â€” discovery, elicitation, scope.
- `lp-researcher` â€” competitors, audience, copy experts.
- `lp-copywriter` â€” section copy and tone review.
- `lp-design-architect` â€” design system, tokens, components, sections.
- `lp-image-creator` â€” hero and section images.
- `lp-frontend-dev` â€” Next.js frontend setup/build/assembly.
- `lp-backend-dev` â€” FastAPI backend, leads, admin.
- `lp-integrator` â€” WhatsApp and email integrations.
- `lp-reviewer` â€” copy, design, SEO, accessibility, backend, integrations.
- `lp-deployer` â€” Vercel, domain, Docker, EasyPanel.
- `lp-versioner` â€” GitHub repo/version export.
- `lp-scraper` â€” design/content extraction from references.
- `lp-orchestrator` â€” receive order, run pipeline, notify.
- `lp-storage` â€” bucket, upload assets, generate URLs.

## Manual Produced

The session created:

```text
{OTEAR_VAULT_ROOT}/Manuais/Manual do ConteÃºdo Sem EsforÃ§o.md
```

It included:

- ecosystem map;
- flow from idea/link to finished content;
- Hermes skills already created for content workflows;
- Nirvana agents, API squads, and endpoints;
- OpenSquad squads and agent roles;
- PI Squad landing-page pipeline;
- use cases by outcome;
- Hermes Desktop prompt recipes;
- durable personal workflow rules;
- paths index and backlog.

## Prompt Recipe Pattern

Use this pattern in future manuals:

```text
Hermes, usa [sistema/agente/skill] para [resultado final].
Contexto: [marca/pÃºblico/produto/link].
Regras: [estilo, formato, restriÃ§Ãµes].
Entrega: [arquivo, pasta, preview, resumo].
```

## Curator Notes

The session also created user-requested skills:

- `opensquad-news-carousel`
- `hormozi-marketing-mentor`

Because they were created in a foreground user-requested context, avoid autonomous edits unless curator policy has adopted them as managed skills. If they need future automated maintenance, recommend that the user run `hermes curator adopt <skill-name>`.
