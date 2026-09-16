---
name: opensquad-carousel-workflows
description: "Use when improving OpenSquad Instagram carousel agents."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [opensquad, instagram, carousel, agents, visual-design, image-generation]
    category: software-development
---

# OpenSquad Carousel Workflows

## When to Use

Use this skill when the user asks to create, debug, or improve OpenSquad carousel/news agents, especially Instagram carousel pipelines under `{OTEAR_SO_ROOT}/referencias/opensquad` or mirrored projects under `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes`.

This covers workflow design, agent prompt updates, visual-reference integration, image-generation provider choice, and output validation for carousels.

## Core principles

1. **Do not treat images as decorative fallbacks.** For carousels modeled after premium editorial profiles, images are structural: cover hook, central context, and retention signal.
2. **Check existing analyses before scraping again.** The user may already have run `instagram-scraper` or another agent. Search outputs and memory first.
3. **Prefer reference-profile analysis over generic design guesses.** If a profile like `@brandsdecoded__` is mentioned, locate or create a local `design-analysis.md` and wire it into the carousel agents.
4. **Separate source correctness from design production.** Research/fact-check first, then brief, then editorial narrative, then visual system, then image generation/rendering.
5. **When the user criticizes design quality, inspect the pipeline before defending the output.** Common root causes: text-only fallback, wrong checkpoint option, image provider fallback, missing reference-profile analysis, or template not matching the intended layout.

## Standard OpenSquad paths

Typical project roots:

- `{OTEAR_SO_ROOT}/referencias/opensquad`
- `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes`

News carousel squad paths:

- `squads/noticias-carrossel-ia/agents/`
- `squads/noticias-carrossel-ia/pipeline/steps/`
- `squads/noticias-carrossel-ia/pipeline/slide-template.html`
- `squads/noticias-carrossel-ia/output/`

Instagram reference scraper paths:

- `squads/instagram-scraper/output/`
- `squads/instagram-scraper/_memory/memories.md`

Reference-profile memory target:

- `_opensquad/_memory/reference-profiles/<username>/design-analysis.md`

## Procedure: Improve a carousel flow

1. **Locate the active project and squad.**
   - Check both `{OTEAR_SO_ROOT}/referencias/opensquad` and `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes` if the user mentions OpenSquad, O Tear, agents, or carrossel.
   - Read the relevant `README.md`, `agents/*.agent.md`, `pipeline/pipeline.yaml`, and step files before patching.

2. **Find existing profile/reference analysis.**
   - Search for the username and distinctive phrases from the profile.
   - Prefer existing `design-analysis.md`, report files, or scraper outputs over new scraping.
   - For `@brandsdecoded__`, see `references/brandsdecoded-reference.md`.

3. **Patch the right agents, not just outputs.**
   - `design-system.md`: durable layout, palette, typography, reference-profile rules.
   - `designer.agent.md`: `slides-data.json` structure and content constraints.
   - `conceituador-visual.agent.md`: visual concept rules, cover image strategy, anti-patterns.
   - `gerador-imagens.agent.md` and `pipeline/steps/*gerador-imagens.md`: image provider order and generation workflow.
   - `slide-template.html`: header/footer, image zones, actual render behavior.

4. **Fix checkpoint mismatches.**
   - If a runner script says â€œsem imagensâ€ while the checkpoint option means â€œusar bancoâ€ or â€œgerar IAâ€, patch the runner. The pipelineâ€™s checkpoint text is the source of truth.
   - For premium/reference-style carousels, default to generating at least the cover image unless the user explicitly asks text-only.

5. **Use provider order intentionally.**
   - If the user prefers â€œImage 2 do Codex/ChatGPTâ€, do not silently use Gemini first.
   - Configure/teach the pipeline to try `CHATGPT_BRIDGE_URL` / gpt-image-2 first, then OpenAI Images, then Gemini/Imagen fallback.
   - If the preferred provider is not configured, report that explicitly and say which fallback was used. See `references/image-provider-priority.md`.

6. **Validate with artifacts.**
   - For generated carousels, verify actual files exist: `carousel-content.md`, `slides-data.json`, rendered images/HTML, and a contact sheet or preview.
   - Inspect at least the cover visually if possible. Do not call a text-only fallback â€œdoneâ€ when the requested style depends on imagery.

## BrandsDecoded-style adaptation rules

Do **not** copy a reference accountâ€™s identity wholesale. Extract structure and retention characteristics, then adapt to the userâ€™s brand.

For Marlon/O Tear:

- Keep `Urbanist` unless the user asks otherwise.
- Preserve O Tear/Marlon palette: black/off-white with neon green `#A3F12E`.
- Use BrandsDecoded-like structure: editorial header, dramatic cover, 3-zone internal slides, evidence-based storytelling.
- Avoid copying @brandsdecoded__ orange as the primary brand color unless explicitly requested.

## Pitfalls

- **Text-only fallback without saying so.** If image generation or renderer is unavailable, state it clearly and do not present the output as the requested premium visual direction.
- **Overloading the cover.** Dashboards, tiny numbers, robots, and many abstract elements look weak in feed thumbnails. Use one dominant protagonist and strong negative space.
- **Hardcoding Gemini when the user expects Codex/Image 2.** Patch the provider order and/or explain missing configuration.
- **Ignoring existing scraper analyses.** Users may have already paid the cost of scraping/analysis; search before re-running Instagram.
- **Generic CTAs.** BrandsDecoded-style carousels often close with an editorial conclusion or provocative question rather than a salesy CTA.

## Linked references

- `references/brandsdecoded-reference.md` â€” local analysis pattern for @brandsdecoded__ and how to adapt it.
- `references/image-provider-priority.md` â€” provider order and environment variables for Codex/Image 2 vs Gemini fallback.
