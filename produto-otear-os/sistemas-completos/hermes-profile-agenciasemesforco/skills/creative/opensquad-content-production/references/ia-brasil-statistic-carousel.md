# IA Brasil Statistic Carousel Example

This reference captures a reusable pattern from a news-carousel session: the user wanted a carousel around “77% of companies using AI in Brazil,” but the percentage was a mixed statistic. The durable lesson is to validate the **recut** of a statistic before writing the carousel.

## Corrected statistic pattern

When a user asks for “77% das empresas usando IA no Brasil,” verify whether the 77% refers to:

- **adoption by companies**,
- **adoption by a specific sector** such as industrial companies,
- **familiarity with AI agents**,
- or **consumer/person usage**.

In this case the cleaner sourcing was:

- IBGE: **41.9%** of investigated industrial companies used AI in 2024, up from 16.9% in 2022.
- TOTVS/H2R Panorama IA 2025: **50%** of Brazilian companies reported using AI in work routines; only a small share measured ROI.
- TOTVS/H2R: **77%** had medium/high familiarity with AI agents — familiarity is not implementation.
- Bain via Jornal Razão: **77%** of Brazilians/consumers used AI — people, not companies.

## Recommended carousel angle

Use a fact-check hook:

> “77% das empresas usam IA no Brasil? Cuidado.”

Then teach the corrected recuts:

1. 77% is not the best claim for business adoption.
2. IBGE gives the strongest sector-specific adoption stat: 41.9% in industry.
3. TOTVS gives a broader business routine stat: 50%.
4. 77% is useful only when framed as familiarity with AI agents or consumer usage.
5. Business insight: adoption is accelerating, but maturity remains low.

## Output folder convention used

For `squads/noticias-carrossel-ia`, save a run like:

```text
squads/noticias-carrossel-ia/output/YYYY-MM-DD-ia-brasil-porcentagem-correta/
├── research-brief.md
├── carousel-content.md
├── slides-data.json
├── preview-contact-sheet.png
└── slides/slide-01.png ... slide-08.png
```

## Draft structure that worked

- `research-brief.md`: source summary, facts, editorial angle, alternatives.
- `carousel-content.md`: `=== FORMAT ===`, `=== SLIDES ===`, `=== LEGENDA ===`, `=== HASHTAGS ===`, `=== FONTES ===`.
- `slides-data.json`: list of slide dictionaries with `type`, `title`, `subtitle`, `bgColor`, `titleColor`, `highlight`, `highlightColor`, `fontFamily`.

## Verification

- Read back `carousel-content.md` after writing.
- Check whether local renderer ports are running; if not, produce fallback PNG slides and a contact sheet.
- Inspect/attach the contact sheet so the user can see whether the fallback slides are legible.
