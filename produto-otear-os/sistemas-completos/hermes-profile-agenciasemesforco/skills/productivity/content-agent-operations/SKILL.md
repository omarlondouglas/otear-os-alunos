---
name: content-agent-operations
description: Map content agent stacks into operating manuals.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Content Operations, Agents, Obsidian, Manuals, Orchestration]
    related_skills: [obsidian]
---

# Content Agent Operations Skill

Use this skill to organize a user's ecosystem of content agents, squads, skills, projects, and automations into a practical operating manual. The goal is not a code inventory dump; it is a usable command center that tells the user what they already have, what each thing does, and how to trigger it from Hermes Desktop.

This skill is especially useful when the user has multiple local agent systems and wants a "content with no effort" map across them.

## When to Use

- User asks to list, organize, or map their agents, squads, skills, tools, or automations.
- User asks for a manual in Obsidian explaining what they have and how to use it.
- User wants to connect Hermes Desktop with local projects such as Nirvana/O Tear Agentes, OpenSquad, PI Squad, AIOX, or similar content stacks.
- User asks for prompts, operating procedures, or command recipes for using agents without remembering paths or commands.

Don't use for one-off content creation unless the task is to document or organize the content-production system itself.

## Prerequisites

- Load the `obsidian` skill before writing notes into the vault.
- Load `hermes-agent` only when the user asks about Hermes itself, configuration, surfaces, or how Hermes Desktop should call tools/skills.
- Resolve the user's vault path from memory or environment before writing. For this user, the Obsidian vault is normally `{OTEAR_VAULT_ROOT}`.
- Use live filesystem discovery before claiming an agent/squad exists.

## Reference Files

- `references/otear-content-stack.md` â€” current known map of the user's Nirvana/OpenSquad/PI Squad ecosystem from the session that created this skill. Treat it as a starting point; verify live paths before updating a manual.
- `references/agencia-sem-esforco-otear-os.md` â€” operating notes for the user's AgÃªncia Sem EsforÃ§o framing, `otear-os` Obsidian base, AIOX Copy Squad organization, and the rule that Hermes Desktop must be shown as the central cockpit rather than just another agent.

## Procedure

1. **Confirm scope from the request.** Determine whether the user wants a full ecosystem manual, a subsystem map, or an update to an existing manual. Completion: the target note name and systems are clear.

2. **Inventory live projects.** Use `search_files` and `read_file` to inspect manifests, READMEs, `squad.yaml`, `.agent.md`, API endpoint files, and local skill folders. Completion: every listed system has a source path.

3. **Group by user outcome.** Organize by what the user can do, not by repo structure. Recommended buckets: short-form content, carousels, video, visuals, marketing/sales, landing pages, memory/library, automation. Completion: the manual answers "what should I use for this job?".

4. **Extract trigger language.** For each agent/squad/skill, write how to ask Hermes Desktop to use it. Completion: every major capability has at least one copy-paste prompt.

5. **Document paths and outputs.** Include canonical paths, local service ports, output folders, and where finished assets appear. Completion: the user can find generated work without asking again.

6. **Capture preferences as operating rules.** Record durable workflow preferences for that class of task in the manual and, if appropriate, the governing skill. Completion: repeated corrections such as "no visible slide numbering" or "use Codex/Image 2 instead of Gemini" are not lost.

7. **Write the Obsidian manual.** Use `write_file` for a new note or `patch` for a focused update. Prefer a durable location such as `{OTEAR_VAULT_ROOT}/Manuais/<manual>.md`. Completion: the note exists and has frontmatter, sections, tables, and prompt recipes.

8. **Create visible entry points for new sub-bases.** When creating a nested knowledge base such as `{OTEAR_OS_ROOT}`, create an obvious root-level entry note (for example `{OTEAR_VAULT_ROOT}/ABRIR otear-os.md`) plus a start note inside the sub-base. Completion: the user can find the base from Obsidian search without browsing deep folders.

9. **Verify.** Read the first section and run a simple presence/count check for critical terms and file counts. Completion: the note includes the requested systems, paths, usage guidance, and the new folder is not just documented but actually populated.

## Manual Structure

A strong manual should include:

```markdown
---
title: <Manual Title>
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
status: ativo
tags: [manual, conteudo, hermes, agentes]
---

# <Manual Title>

## Mapa rÃ¡pido do ecossistema
## Fluxo-mÃ£e do pedido ao conteÃºdo pronto
## Skills Hermes disponÃ­veis
## Sistema 1: funÃ§Ã£o, agentes, endpoints, como pedir
## Sistema 2: funÃ§Ã£o, agentes, endpoints, como pedir
## Casos de uso por resultado
## Como usar com Hermes Desktop
## Biblioteca de prompts prontos
## Regras pessoais consolidadas
## O que falta organizar depois
## Ãndice de caminhos
```

## Writing Rules

- Write in Portuguese when the user's system and notes are in Portuguese.
- Be operational and concise: tables, paths, prompts, and checklists beat long explanations.
- Use the user's names for systems even if the repo names differ: e.g. "Nirvana / O Tear Agentes".
- Distinguish verified facts from interpretations.
- Do not expose secrets, API keys, tokens, or credential values.
- Do not claim a local service is running unless you actually checked it in the current session.
- When a name is ambiguous, state the interpretation used, e.g. "interpretei pensquad como PI Squad".

## Pitfalls

- **Flat inventory dump:** a list of files is not a manual. Convert files into capabilities and usage recipes.
- **Stale paths:** verify live paths before writing or updating a note.
- **Over-documenting internals:** users need what they can do and how to invoke it; keep implementation details secondary.
- **Missing Hermes Desktop bridge:** always include natural-language prompt examples for Hermes Desktop.
- **Hermes shown as just another box:** when the user's goal is a non-technical interface, make Hermes Desktop the central cockpit/entry layer, with Nirvana, O Tear, OpenSquad, Copy Squad, Codex, and Obsidian shown as executors behind it.
- **Invisible Obsidian sub-base:** creating a populated folder is not enough if the user cannot find it. Add root-level entry notes such as `ABRIR <base>.md`, a `START AQUI` note inside the folder, and verify file counts.
- **Forgetting user workflow corrections:** if the user corrected provider, style, slide numbering, folder visibility, or format, encode that in the relevant operating rules.
- **Protected skills:** if the relevant skill is user-owned, bundled, external, or pinned, do not patch it; mention that it should be adopted by the curator if future automated updates are desired.

## Verification

Before final delivery, confirm:

- [ ] Manual file exists in the Obsidian vault.
- [ ] Major systems requested by the user are present.
- [ ] Key paths are included.
- [ ] Each capability category has a "how to ask Hermes" example.
- [ ] Durable user preferences are present.
- [ ] Secrets are absent.
- [ ] Final response includes the Obsidian path and a short summary of what was organized.
