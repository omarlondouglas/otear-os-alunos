---
name: opensquad-content-production
description: "Use when producing artifacts with local OpenSquad squads."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [OpenSquad, content, carousel, agents, local-projects]
    category: creative
---

# OpenSquad Content Production

## When to Use

Use this skill when the user asks to use a local OpenSquad/OpenSquad-like project or one of its squads/agents to produce content artifacts such as Instagram carousels, news-to-carousel outputs, briefs, scripts, or campaign assets.

The default expectation is a **working artifact saved into the squad's output tree**, not only a chat draft. If local render services are not running, still deliver deterministic fallback artifacts (Markdown/JSON and, when appropriate, simple image previews) and clearly report which renderer/API could not be reached.

## Procedure

1. **Locate the project and relevant squad.**
   - Check known local roots first when available (for this user, OpenSquad has appeared under `{OTEAR_SO_ROOT}/referencias/opensquad`).
   - Search for squad names, `squad.yaml`, `run-local.bat`, `README.md`, or agent files under `squads/<squad>/agents/`.
   - For news carousels, the relevant squad is commonly `squads/noticias-carrossel-ia/`.

2. **Read the squad's own instructions before creating content.**
   - Inspect `README.md`, `squad.yaml`, relevant `agents/*.agent.md`, and pipeline step files.
   - Preserve the output conventions used by the project (for example `carousel-content.md`, `research-brief.md`, `slides-data.json`, and `output/<run-id>/slides/`).

3. **Ground any factual/news claim before drafting.**
   - When the user provides a statistic, verify the original source and recut the claim if the percentage is being mixed across audiences or definitions.
   - Prefer primary sources (IBGE, official reports, PDFs) over SEO reposts.
   - Keep the source mapping in the deliverable so the user can post confidently.

4. **Create a run-specific output directory.**
   - Use a descriptive date/slug under the squad output directory, e.g. `squads/noticias-carrossel-ia/output/YYYY-MM-DD-topic-slug/`.
   - Write at minimum:
     - `research-brief.md` for source findings and angle.
     - `carousel-content.md` or equivalent final copy.
     - `slides-data.json` if the project has a carousel renderer/tool schema.

5. **Try the native renderer/API when it is clearly available.**
   - Inspect local docs/scripts for ports and endpoints.
   - Probe likely local services only enough to know whether they are running.
   - Do not present a dead local service as a blocker if a useful fallback artifact can be produced.

6. **Honor the image-generation path before falling back.**
   - For `noticias-carrossel-ia`, read `pipeline/steps/04b-checkpoint-imagens.md` and align any scripted run with its current choices: option 2 is â€œgerar com IA via Geminiâ€; option 3 is â€œmanter sÃ³ textoâ€. Do not trust stale helper scripts whose prose/options disagree with the pipeline.
   - If the user expects a strong designed carousel or asks why the cover was not AI-generated, create/run the IA cover path: write `visual-concept.md`, call Gemini image generation when `GEMINI_API_KEY` is available, save under `images/img-slide-01-ai-cover.png`, write `image-brief.md`, and set slide 1 in `slides-data.json` to `theme: "black"` with `imageFile` pointing at the generated image.
   - Use the squadâ€™s intended cover direction when present: intaglio/engraving protagonist + modern colorful digital/news elements, with negative space for headline overlay. A text-only fallback is acceptable only after the native/image path is unavailable or explicitly declined.

7. **Fallback artifact rule.**
   - If the OpenSquad renderer or dashboard is not running, generate usable fallback files in the squad output folder.
   - For carousels, create simple PNG slides or a contact-sheet preview when possible, using the same slide copy and design tokens from `slides-data.json`.
   - If the IA cover image was generated successfully but the renderer is down, composite a temporary preview PNG with the IA cover plus readable overlay rather than replacing it with a purely typographic slide.
   - Report that these are fallback renderings, not the full project renderer output.

8. **Verify before final response.**
   - Read back at least the final content file.
   - Verify the output folder exists and contains the expected artifacts.
   - For image fallback, inspect or attach a contact-sheet preview.

## Output conventions for `noticias-carrossel-ia`

Recommended files:

```text
squads/noticias-carrossel-ia/output/<run-id>/
â”œâ”€â”€ research-brief.md
â”œâ”€â”€ carousel-content.md
â”œâ”€â”€ slides-data.json
â”œâ”€â”€ preview-contact-sheet.png        # fallback preview if generated
â””â”€â”€ slides/
    â”œâ”€â”€ slide-01.png
    â””â”€â”€ ...
```

`carousel-content.md` should usually include:

- `=== FORMAT ===`
- `=== SLIDES ===`
- `=== LEGENDA ===`
- `=== HASHTAGS ===`
- `=== FONTES ===` when the carousel is factual/news-based.

## Pitfalls

- Do not treat a viral percentage as correct until the audience/denominator is verified. "Companies", "industrial companies", "consumers", "familiarity", and "daily use" are different claims.
- Do not stop after finding the source; create the artifact in the squad output directory.
- Do not invent renderer URLs. Probe documented or obvious local ports, then fall back honestly if unavailable.
- Do not overwrite existing output runs. Create a new dated slug unless the user explicitly asks to modify a prior run.
- Do not let fallback previews lower the design standard: if the user asked for OpenSquad/GaryV-style carousel output, avoid crude text-only design unless images/renderer are genuinely unavailable or the user chose â€œsem imagensâ€.
- Do not rely on `run-local.bat` checkpoint labels without checking pipeline step files; stale labels can select the wrong image strategy.

## References

- `references/ia-brasil-statistic-carousel.md` â€” example of correcting a mixed 77% IA statistic and producing a news carousel output in `noticias-carrossel-ia`.
- `references/ai-cover-generation.md` â€” manual Gemini cover-generation path for `noticias-carrossel-ia` when the renderer is down or helper scripts select the wrong image checkpoint.
