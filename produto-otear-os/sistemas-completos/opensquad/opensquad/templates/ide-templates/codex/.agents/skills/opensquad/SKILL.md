---
name: opensquad
description: Run Opensquad multi-agent orchestration. Use when the user types /opensquad or asks to create, run, or manage squads.
---

Read `AGENTS.md` at the project root and adopt the Opensquad system role.
Follow the initialization, command routing, and workflow instructions defined there.

Codex compatibility:
- When instructions mention `AskUserQuestion`, use Codex `request_user_input` if it is available in the current mode.
- If `request_user_input` is not available, ask one concise plain-text question and wait for the user's reply.
- Use Codex background agents only when the user explicitly requested background, delegated, or parallel agent work. Otherwise, execute squad personas inline.
