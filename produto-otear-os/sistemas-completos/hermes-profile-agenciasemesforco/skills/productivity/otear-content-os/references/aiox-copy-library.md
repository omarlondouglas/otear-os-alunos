# AIOX Copy Library / otear-os

Use this reference when the user wants to organize or use copywriting materials from AIOX inside the O Tear / AgÃªncia Sem EsforÃ§o content OS.

## Durable paths

```text
Source AIOX root: {OTEAR_SO_ROOT}/referencias/aiox
Source Copy Squad: {OTEAR_SO_ROOT}/referencias/aiox/aiox-squads/squads/copy
Organized Obsidian base: {OTEAR_OS_ROOT}
Copywriter library: {OTEAR_OS_ROOT}/02-biblioteca-copywriters
Mirrored knowledge base: {OTEAR_OS_ROOT}/02-biblioteca-copywriters/knowledge-base
Raw OCR mirror: {OTEAR_OS_ROOT}/99-fontes-originais/AIOX-ocr_results
Main otear-os index: {OTEAR_OS_ROOT}/README.md
Copy Squad manual: {OTEAR_OS_ROOT}/04-manual-de-uso/Manual do Copy Squad.md
```

## What was found in AIOX

AIOX contains a working `copy` squad with:

- `squad.yaml`
- agents: Copy Chief, Ads Specialist, Email Specialist, Landing Specialist, Social Specialist, Copy Reviewer
- workflows for copy generation and extraction/indexing
- templates, checklists, routing matrix and copywriter frameworks
- knowledge-base organized by copywriter
- raw OCR outputs and swipe files

Verified inventory after organizing into `otear-os`:

| Item | Count |
|---|---:|
| Author/copywriter folders | 15 |
| Knowledge-base Markdown files | 1,428 copied under `knowledge-base` |
| Raw OCR Markdown files | 668 copied under `99-fontes-originais/AIOX-ocr_results` |
| Total Markdown under `{OTEAR_OS_ROOT}` | 2,118 |

## Copywriter folders observed

| Folder | Label | Files observed in source author folder |
|---|---|---:|
| `bencivenga` | Gary Bencivenga | 12 |
| `carlton` | John Carlton | 3 |
| `carneiro` | Paulo Maccedo / Carneiro | 9 |
| `clemens` | Clemens / Caples | 3 |
| `haddad` | Haddad | 204 |
| `halbert` | Gary Halbert | 18 |
| `hopkins` | Claude Hopkins | 8 |
| `kennedy` | Dan Kennedy | 1 |
| `lampropoulos` | Lampropoulos | 11 |
| `makepeace` | Clayton Makepeace | 2 |
| `miligan` | Miligan | 6 |
| `ogilvy` | David Ogilvy | 0 direct files in this folder; may appear as framework or under `outros`/OCR |
| `outros` | Outros / Agora / varied swipes | 1,107 |
| `schwartz` | Eugene Schwartz | 3 |
| `settle` | Ben Settle | 15 |

## Product naming

The user prefers the public/non-technical product name **AgÃªncia Sem EsforÃ§o**.

Recommended naming split:

```text
AgÃªncia Sem EsforÃ§o = public user-facing product/interface
otear-os = Obsidian operating base / knowledge library
Nirvana = orchestration engine/control plane
O Tear / agi-agentes = applied product/backend tools
Hermes Desktop = cockpit for natural-language operation
```

## How to use in future sessions

When asked to create copy/campaigns from this library, first load this skill and treat `{OTEAR_OS_ROOT}` as the organized source. Prefer referencing the mirrored Obsidian base over scanning all of `{OTEAR_SO_ROOT}/referencias/aiox` again unless the user asks to re-sync.

Default user-facing prompt pattern:

```text
Hermes, usa o otear-os e a biblioteca de copywriters do AIOX.
Cria uma copy de [canal] para [produto].
PÃºblico: [pÃºblico].
Estilo: [Halbert/Schwartz/Ogilvy/Kennedy/Carlton/Bencivenga/etc].
Entrega: copy final + headlines + bullets + CTA + explicaÃ§Ã£o do framework usado.
```

Leigo-facing pattern:

```text
Hermes, abre a AgÃªncia Sem EsforÃ§o e transforma esse briefing em campanha completa: anÃºncio, pÃ¡gina, sequÃªncia de emails e posts. Use os materiais dos grandes copywriters do otear-os.
```

## Operating guidance

- For organization tasks, create/update Obsidian notes under `{OTEAR_OS_ROOT}` and update `{OTEAR_VAULT_ROOT}/Manuais/Manual do ConteÃºdo Sem EsforÃ§o.md` when the change affects the global manual.
- Avoid copying entire development repos with `node_modules` into Obsidian. Mirror curated knowledge, manuals, templates, checklists, and raw OCR/reference files.
- If counts matter, compute them with tools instead of estimating.
- Do not treat the author folder counts as exhaustive proof that no material exists elsewhere; the source contains raw OCR and `outros` files that may include additional copywriters.
