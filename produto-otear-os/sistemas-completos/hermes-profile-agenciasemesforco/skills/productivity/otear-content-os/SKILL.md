---
name: otear-content-os
description: Operate O Tear/Nirvana as a content OS.
version: 0.1.0
author: Marlon Lima, Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [O Tear, Nirvana, Content OS, Agents, Obsidian]
    related_skills: [obsidian, hermes-agent, opensquad-news-carousel, hormozi-marketing-mentor]
---

# O Tear Content OS Skill

Use this skill when the user wants to operate O Tear/Nirvana/OpenSquad as a personal or client-facing content operating system through Hermes Desktop. The goal is to hide terminal complexity from non-technical users while preserving the power of Nirvana businesses, squads, mind-clones, OpenSquad pipelines, O Tear API tools, Codex image/code generation, and Obsidian memory.

Session-specific inventory and architecture notes live in `references/nirvana-content-os-inventory.md`.

AIOX copywriter library and `otear-os` organization notes live in `references/aiox-copy-library.md`.

## When to Use

- User asks to organize agents, squads, Nirvana, OpenSquad, PI Squad, or O Tear into a usable system.
- User asks whether Nirvana can become a custom operating system for content, marketing, sales, automation, or agency operations.
- User wants a non-technical interface or workflow for people who should not use terminal commands.
- User asks how Hermes Desktop, Nirvana-OS, O Tear Agentes, Codex, OpenSquad, and Obsidian should fit together.
- User asks to update the Obsidian manual for â€œconteÃºdo sem esforÃ§oâ€, content OS, agent OS, or similar.
- User asks to organize or use AIOX copywriter materials, swipe files, OCRs, Copy Squad, or `otear-os`.

Do not use for a single content artifact; use `opensquad-news-carousel`, video/content skills, or direct tools instead.

## Core Architecture

Recommended split:

```text
Hermes Desktop = human cockpit / non-technical interface
Nirvana-OS engine = orchestration protocol, harness, audit, registries
O Tear / AGI Agentes = product backend, UI, jobs, tools, media services
OpenSquad = structured content squads and reusable content pipelines
Codex = premium executor for image/code where useful
Obsidian = durable manuals, memory, operating docs, decisions
```

Do not collapse these layers into one monolith. Keep engine, product, content packs, and user-facing interface separated.

## Design Principles

1. **Interface first for leigos.** Non-technical users should interact through Hermes Desktop or the O Tear UI, not terminal commands.
2. **Language-natural commands.** The user should say what they want; Hermes chooses skill/tool/agent/squad.
3. **Capability over agent name.** Organize what the system can do by capability: research, references, model extraction, writing, creation, video, memory, campaigns, distribution.
4. **Nirvana as control plane.** Use `nrv`, businesses, squads, and harness for orchestration, audit, routing and quality gates.
5. **O Tear as product layer.** Use FastAPI/React/services for actual user workflows, jobs, storage, brand data, calendar, assets, video, image, and outputs.
6. **Obsidian as operating memory.** Save manuals and stable operating decisions in `{OTEAR_VAULT_ROOT}`.
7. **Codex for premium generation.** Use Codex/ChatGPT Image 2 for premium image/code generation where the user has specified that preference; do not silently use Gemini for those flows.

## Canonical User Flow

```text
User in Hermes Desktop
  -> asks in natural language
  -> Hermes loads the right skill
  -> Hermes checks Obsidian/project context if needed
  -> Hermes calls Nirvana (`nrv`) or O Tear/OpenSquad APIs/tools
  -> Job creates artifact/output
  -> Hermes verifies real files/URLs/previews
  -> Hermes saves or updates Obsidian manual if durable
  -> Hermes responds with result path, status and next action
```

For truly non-technical customers, prefer an O Tear UI button flow that calls the same backend capabilities.

## Main Paths

```text
Obsidian vault: {OTEAR_VAULT_ROOT}
O Tear OS / organized operating base: {OTEAR_OS_ROOT}
O Tear / AGI Agentes: {OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes
Nirvana project state: {OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes/.nirvana
AIOX source materials: {OTEAR_SO_ROOT}/referencias/aiox
AIOX Copy Squad source: {OTEAR_SO_ROOT}/referencias/aiox/aiox-squads/squads/copy
OpenSquad: {OTEAR_SO_ROOT}/referencias/opensquad
PI Squad / Ultimate Landing Page: {OTEAR_SO_ROOT}/referencias/pi-squad
Hermes skills: {HERMES_SKILLS_ROOT}
```

## Useful Capabilities to Expose

Expose user-facing actions, not implementation names:

| Button / Intent | Backing system |
|---|---|
| Criar carrossel de notÃ­cia | `opensquad-news-carousel` / OpenSquad / Nirvana squad |
| Criar roteiro curto | O Tear script capability / news-script-adapter |
| Encontrar cortes virais | Nirvana/O Tear video capability / Beast/Nolan |
| Gerar capa ou thumbnail | O Tear creation capability / Codex / thumbnail squad |
| Analisar referÃªncia visual | OpenSquad instagram-scraper / O Tear references |
| Criar landing page | PI Squad / software-forge / backend/design squads |
| Melhorar oferta/campanha | `hormozi-marketing-mentor` |
| Salvar conhecimento/manual | Obsidian skill |
| Criar novo squad/business | Nirvana business-creator / squad creator |

## Procedure

1. **Identify the user surface.** Decide whether the task is for the user in Hermes Desktop, an internal operator, or a leigo/client-facing UI. Completion: response assumes the right interface.

2. **Classify the requested outcome.** Map it to content, video, image, campaign, landing page, reference analysis, memory/manual, or new capability. Completion: one primary capability is selected.

3. **Choose orchestration layer.** Use:
   - Hermes skill for personal reusable workflow;
   - O Tear API/tool when the product backend already owns the job;
   - OpenSquad for structured content squads;
   - Nirvana `nrv`/harness/business/squad when orchestration, audit or new capability creation is needed;
   - PI Squad for landing pages.
   Completion: no unnecessary double-orchestration.

4. **Verify available state.** For Nirvana, check `nrv --help`, `nrv install --check`, `nrv list-squads`, `nrv list-businesses` when necessary. Completion: you know whether it is installed and which registries exist.

5. **Avoid terminal-facing UX for leigos.** Translate commands into buttons, prompts, or Hermes Desktop actions. Completion: final guidance can be followed without knowing CLI internals.

6. **Save durable system design.** If the task produces architecture, manual, operating rules, or reusable prompts, write/update an Obsidian note under `{OTEAR_VAULT_ROOT}/Manuais/`. Completion: note path is reported and file verified.

7. **Keep engine and content separate.** Do not put client outputs, content calendars, or generated assets in the engine repository. Completion: output lives in project/product/vault paths, not engine source.

## Pitfalls

- Do not tell leigos to use `nrv`, Codex CLI, `uvicorn`, or OpenSquad terminal flows directly unless they are operators.
- Do not build a monolith that mixes Nirvana engine source, O Tear app code, generated content and client outputs.
- Do not treat agent names as the product API. Use capability/intention labels for UI and routing.
- Do not assume using Hermes with Codex always doubles cost. Token cost depends on whether Codex is the primary model or a second agent layer.
- Do not silently fall back to Gemini for image generation in O Tear/OpenSquad content workflows where the user expects Codex/Image 2.
- Do not save transient install or setup failures as permanent rules.

## Token/Cost Guidance

Use this explanation when asked about Hermes + Codex cost:

- Hermes using Codex as the main model adds Hermes context: tools, skills, memory, project rules and conversation. This can increase input tokens compared with raw Codex, but it is not duplicate reasoning.
- Hermes calling Codex CLI as a separate executor can cost more because Hermes and Codex both reason. Use that pattern for code, premium image flows, or isolated execution tasks, not for every simple request.
- For repeated workflows, reduce cost by turning them into skills, endpoints and jobs instead of re-explaining the whole process every time.

## Verification

Before finalizing an architecture/content-OS answer, verify:

- [ ] Does the answer distinguish Hermes Desktop, Nirvana engine, O Tear product, OpenSquad, Codex and Obsidian?
- [ ] Is the recommended interface usable by a non-technical person?
- [ ] Are terminal commands framed as operator/internal, not end-user UX?
- [ ] Are outputs/manuals saved in Obsidian or project paths, not engine source?
- [ ] If discussing cost, does it distinguish primary-model use from nested-agent use?
