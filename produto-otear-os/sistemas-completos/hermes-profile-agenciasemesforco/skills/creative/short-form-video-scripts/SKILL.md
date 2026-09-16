---
name: short-form-video-scripts
description: "Use when writing hook-driven 45-60s video scripts."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video-script, short-form, marketing, tools, ai-workflows, roteiro]
---

# Short-form Video Scripts

## When to Use

Use this skill when the user asks for a roteiro/script for a short video, especially about an AI tool, Chrome extension, workflow, product idea, or business concept.

## Core Workflow

1. **Ground the subject before writing.** If the script is about a current tool/product/extension, verify public facts from a source when available: name, description, ratings/users/version/permissions only if surfaced by the source. Do not invent feature claims.
2. **Use the user's local exemplars when present.** Search the user's project/knowledge workspace for prior roteiros and agent guidance before drafting. If the user has `agi-agentes`/Nirvana material, look for `Olivetto`, `roteiro`, `news-script-adapter`, recent `output/roteiro-*.md`, and relevant squad agent files.
3. **Pick a content angle, not a generic tutorial.** Frame the tool as a behavior change, business opportunity, mistake correction, or workflow upgrade.
4. **Deliver a usable script immediately.** Avoid long preambles. Include the script, optional alternative hook/version, on-screen editing notes, title, and caption when useful.
5. **Add safety caveats only where they matter.** For browser extensions, mention checking permissions briefly; do not derail the script into security explanation unless asked.

## Preferred 45-60s Structure

- **0s-3s — Hook:** a sharp contradiction, mistake, or opportunity.
- **3s-8s — Name the thing:** identify the tool/workflow in plain language.
- **8s-16s — Old way vs new way:** show what pain it removes.
- **16s-26s — Why it matters:** connect to studying, content, sales, research, operations, or money.
- **26s-38s — Concrete example:** give a day-to-day use case.
- **38s-50s — Reframe:** turn the feature into a bigger insight.
- **50s-60s — CTA:** ask a specific comment question, not a generic “follow me”.

## Tone Pattern

Use direct Brazilian Portuguese when the user writes in Portuguese. Prefer punchy lines and practical framing:

- “Você está usando X do jeito errado.”
- “O ponto não é só resumir. O ponto é transformar consumo passivo em base de conhecimento.”
- “Quem só assiste acumula informação solta. Quem organiza com IA constrói repertório reutilizável.”

## Output Format

Default output:

1. `## Roteiro — 45 a 60 segundos`
2. Timestamped script sections
3. `## Versão mais agressiva / viral` when a stronger version helps
4. `## On-screen editing`
5. `## Título`
6. `## Legenda curta`

## Pitfalls

- Do not over-explain the research process before giving the script.
- Do not treat a tool-review video as a feature list; build around a transformation.
- Do not claim the tool has capabilities not verified from source or user-provided material.
- Do not assume a user's Obsidian vault contains their project agents; inspect the project path they name.

## Reference Files

- `references/olivetto-style.md` — condensed pattern from the user's `agi-agentes` short-form scripts.
