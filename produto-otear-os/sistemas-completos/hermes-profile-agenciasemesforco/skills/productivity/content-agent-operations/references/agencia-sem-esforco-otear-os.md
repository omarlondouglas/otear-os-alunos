# AgÃªncia Sem EsforÃ§o / otear-os operating notes

Use this reference when organizing the user's content-agent ecosystem into Obsidian manuals and diagrams.

## Durable product framing

- Public/non-technical name: **AgÃªncia Sem EsforÃ§o**.
- Internal knowledge base in Obsidian: `{OTEAR_OS_ROOT}`.
- User mental model: Hermes Desktop is the visible cockpit; Nirvana, O Tear/AGI Agentes, OpenSquad, Copy Squad, Codex, and Obsidian are execution/storage layers behind it.

## Hermes placement rule

When making manuals or diagrams, do not show Hermes as just another agent. Make it visibly central:

```text
UsuÃ¡rio leigo
  -> Hermes Desktop
    -> skills + memÃ³ria + otear-os
      -> executor certo por trÃ¡s
        -> entrega final revisada
```

Hermes responsibilities to document:

1. receive the user request in natural language;
2. translate vague asks into jobs;
3. load the relevant skill/procedure;
4. consult memory, Obsidian, and `otear-os`;
5. choose the executor: Nirvana, O Tear API, OpenSquad, Copy Squad, Codex, or local tools;
6. monitor execution and inspect artifacts;
7. quality-check and revise;
8. save outputs and return a path/preview.

## otear-os visibility rule

When creating a new Obsidian sub-base such as `{OTEAR_OS_ROOT}`, also create obvious entry notes so the user can see it in Obsidian:

- root vault entry note: `{OTEAR_VAULT_ROOT}/ABRIR otear-os.md`;
- sub-base start note: `{OTEAR_OS_ROOT}/START AQUI - otear-os.md`;
- sub-base README: `{OTEAR_OS_ROOT}/README.md`.

Verify with file counts and at least one read-back. If the user says the folder appears empty, check live filesystem first, then add/repair root entry notes rather than assuming the copy failed.

## AIOX Copy Squad organization discovered

Source path:

```text
{OTEAR_SO_ROOT}/referencias/aiox/aiox-squads/squads/copy
```

Useful source docs/files:

- `outputs/copy-agents-system-structure.md`
- `aiox-squads/squads/copy/squad.yaml`
- `aiox-squads/squads/copy/data/copywriter-frameworks.md`
- `aiox-squads/squads/copy/data/routing-matrix.yaml`
- `aiox-squads/squads/copy/checklists/copy-quality-checklist.md`
- `aiox-squads/squads/copy/templates/briefing-tmpl.yaml`

Known structure:

- Copy Chief: orchestration/routing.
- Ads Specialist: paid/social ads.
- Email Specialist: subject lines, broadcasts, sequences.
- Landing Specialist: sales pages, VSLs, opt-in pages.
- Social Specialist: posts, carousels, threads, short scripts.
- Copy Reviewer: quality gate.

Known copywriter folders found in AIOX knowledge-base:

- bencivenga
- carlton
- carneiro
- clemens
- haddad
- halbert
- hopkins
- kennedy
- lampropoulos
- makepeace
- miligan
- ogilvy
- outros
- schwartz
- settle

Important: verify counts live before reporting them; previous session counts were approximately 1.4k knowledge-base markdown files and 668 OCR markdown files.

## Diagramming rule

For Excalidraw diagrams of this ecosystem, create a dedicated version emphasizing Hermes as the cockpit if the first diagram reads like a generic architecture map. Label the central box explicitly:

```text
HERMES DESKTOP = COCKPIT CENTRAL
```

Group diagrams into:

- Pessoa leiga / entrada simples;
- Hermes Desktop internals: intention, skills, context, executor selection, job monitoring, review;
- Executors behind Hermes: Nirvana, O Tear/AGI Agentes, OpenSquad, Copy Squad/AIOX, Codex, Obsidian/otear-os;
- Outputs to the user: campaign, carousel, shorts, landing page, strategy, saved library.
