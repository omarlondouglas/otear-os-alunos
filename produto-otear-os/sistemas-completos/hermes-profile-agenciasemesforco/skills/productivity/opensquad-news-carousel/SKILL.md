---
name: opensquad-news-carousel
description: Create OpenSquad news carousels in O Tear style.
version: 0.1.0
author: Marlon Lima, Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [OpenSquad, Carousel, Instagram, News, O Tear]
    related_skills: [grounded-citations]
---

# OpenSquad News Carousel Skill

Use this skill to produce Instagram news carousels in the user's OpenSquad workflow, adapting the editorial characteristics of `@brandsdecoded__` to O Tear / Marlon Lima. It covers source verification, carousel copy, image direction, local output structure, and verification.

## When to Use

- User asks to create a carousel from a news URL or current story.
- User mentions OpenSquad, `noticias-carrossel-ia`, carrossel de notÃ­cias, or carousel agents.
- User wants the visual/editorial style based on `@brandsdecoded__`.
- User needs a reusable flow that avoids Gemini and uses Codex / ChatGPT Image 2 for generated imagery.

Don't use for generic writing that is not intended to become an OpenSquad carousel.

## Prerequisites

- Main OpenSquad path: `{OTEAR_SO_ROOT}/referencias/opensquad`.
- Active squad path: `{OTEAR_SO_ROOT}/referencias/opensquad/squads/noticias-carrossel-ia`.
- Reference profile analysis should exist at:
  `{OTEAR_SO_ROOT}/referencias/opensquad/_opensquad/_memory/reference-profiles/brandsdecoded__/design-analysis.md`.
- Use the `grounded-citations` skill before making factual claims from external sources.
- Codex CLI/app should be authenticated locally for generated images. Do not require `.env` or API keys when local Codex is already logged in.

## Canonical Output

Create a dated output folder under:

```text
{OTEAR_SO_ROOT}/referencias/opensquad/squads/noticias-carrossel-ia/output/<YYYY-MM-DD-slug>
```

Minimum files:

```text
research-brief.md
carousel-content.md
slides-data.json
visual-concept.md
image-brief.md
slides/slide-01.png ... slide-N.png
preview-contact-sheet.png
```

Optional image files:

```text
images/<source-thumbnail-or-ai-cover>.png
images/<supporting-editorial-image>.png
```

## Editorial Rules

- Style target: `@brandsdecoded__` adapted to O Tear, not copied literally.
- Tone: journalistic, analytical, sharp, curiosity-driven.
- Structure: 6â€“8 slides by default.
- Cover sells tension; it does not explain everything.
- Each slide advances one narrative layer: fact â†’ tension â†’ behavior â†’ risk â†’ opportunity â†’ conclusion.
- Use concrete sources, cases, dates, numbers, and consequences.
- Avoid generic AI hype, generic robots, stock handshakes, and fluffy CTA language.
- Final slide should land a strong conclusion or question, not a sales pitch.

## Visual Rules

- No visible slide numbering like `01/08`, `02/08`, etc.
- Header may be used discreetly:
  `Powered by O Tear | @marlonlima.ia | 2026 //`.
- Use Urbanist where the OpenSquad template supports it.
- Palette:
  - dark: `#0A0A0A` / `#0D0D0D`
  - light: `#F5F5F0`
  - accent: `#A3F12E`
  - text: `#FFFFFF` or `#1A1A1A`
- Format: 4:5 Instagram carousel, preferably 1080x1350 or the active squad template size.
- Cover: strong editorial protagonist or symbolic scene, dark/dramatic, high contrast, clean headline area.
- Internal slides: editorial headline, contextual image/metaphor, concise analytical support text.

## Image Generation Rule

Use Codex / ChatGPT Image 2 via the locally authenticated Codex environment for generated imagery.

- Do not use Gemini by default.
- Do not require `.env`, `CHATGPT_BRIDGE_URL`, or API keys when Codex is locally authenticated.
- If Codex image generation is unavailable, stop and report the blocker.
- Only use Gemini/OpenAI API fallback if the user explicitly asks for fallback in that run.

## Procedure

1. **Load grounding.** Load `grounded-citations` and reset/register a fresh citation ledger for the source URL. Completion: every external source used in copy has a citation id.

2. **Fetch source.** Retrieve the news URL with `terminal`, `browser_exec`, or relevant extraction tools. For video pages, extract title, description, publish date, thumbnail, structured metadata, and transcript if accessible. Completion: `research-brief.md` can state exactly what was verified and what could not be extracted.

3. **Read reference style.** Read `{OTEAR_SO_ROOT}/referencias/opensquad/_opensquad/_memory/reference-profiles/brandsdecoded__/design-analysis.md`. Completion: carousel decisions explicitly follow the reference without copying its brand colors.

4. **Create output folder.** Use a date slug like `YYYY-MM-DD-topic-source`. Completion: folder exists under the squad output directory.

5. **Write `research-brief.md`.** Include source title, URL, date, extractable facts, caveats, and editorial angle. Completion: no unsupported percentage or claim is invented.

6. **Write `carousel-content.md`.** Draft 6â€“8 slides with title, subtitle/body, caption, hashtags, and source block. Completion: every fact from the source is cited or explicitly scoped as interpretation.

7. **Write `slides-data.json`.** Match the active OpenSquad structure where possible. Completion: no visible slide numbering fields are added.

8. **Write `visual-concept.md` and `image-brief.md`.** Specify cover prompt, image roles, and which slides use images. Completion: generated imagery is assigned to Codex / ChatGPT Image 2, not Gemini.

9. **Generate or render slides.** Prefer the active OpenSquad renderer. If unavailable, create a clearly labeled local preview fallback with PIL/HTML rendering, while preserving the correct content files. Completion: `slides/` contains all slide PNGs.

10. **Generate cover with Codex when needed.** Use local Codex image generation for a premium cover. If Codex cannot generate in the current environment, stop and report the blocker instead of silently using Gemini. Completion: cover image exists in the output folder and is referenced by `slides-data.json` or the rendered slide.

11. **Create contact sheet.** Generate `preview-contact-sheet.png`. Completion: all slides are visible in order for quick review.

12. **Verify visually.** Use `vision_analyze` on the contact sheet and, if needed, on the cover. Check legibility, style, no visible numbering, source-safe copy, and whether it resembles the BrandsDecoded editorial structure adapted to O Tear. Completion: issues are fixed or clearly reported.

## Pitfalls

- Do not infer an exact percentage from a headline like â€œquase metadeâ€ unless the source exposes the exact number.
- Do not use Gemini automatically just because it is configured in `.env`.
- Do not leave the cover as a generic AI/dashboard visual; the user dislikes generic direction.
- Do not add slide numbers. The user specifically does not want visible numbering.
- Do not confuse `@brandsdecoded__` style with copying its colors or identity.
- If using fallback rendering, say it is a preview fallback and keep the OpenSquad content files reusable.

## Verification

Before final delivery, confirm:

- [ ] `research-brief.md` exists.
- [ ] `carousel-content.md` exists.
- [ ] `slides-data.json` exists.
- [ ] `visual-concept.md` exists.
- [ ] `slides/` contains the expected count.
- [ ] `preview-contact-sheet.png` exists.
- [ ] No visible slide numbering appears.
- [ ] Generated imagery uses Codex or the blocker is reported.
- [ ] Source claims are cited or caveated.

Final response should include the output folder path, files created, source caveats, and whether the visual was final Codex generation or preview fallback.
