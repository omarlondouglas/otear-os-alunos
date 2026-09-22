---
name: otear-criador
description: Conduz a criação de agentes, skills e squads reutilizáveis no padrão nativo Hermes.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, criador, agentes, skills, squads]
    related_skills: [otear-skill-creator, otear-agent-creator, otear-squad-orchestrator]
tools: [read_file, write_file, search_files]
---

# Otear Criador

## Fontes e saída

Leia `produto-otear-os/squads-base/squad-criador-de-agentes.yaml` e
`produto-otear-os/criador/README.md`. Use a skill específica de criação e salve em
`produto-otear-os/minhas-skills`, `produto-otear-os/meus-agentes` ou
`produto-otear-os/meus-squads`.

## Procedimento

1. Descubra qual artefato é necessário, usuário, gatilho, entrada, saída e limites.
2. Escolha `otear-skill-creator`, `otear-agent-creator` ou `otear-squad-orchestrator`.
3. Use métodos AIOX apenas como referência, nunca como requisito de runtime.
4. Garanta nome único, instruções claras, caminhos relativos e teste de exemplo.

## Requisitos

Subagentes só são usados se Hermes oferecer `delegate_task`; caso contrário, crie um
workflow sequencial.

## Verificação

Informe o arquivo criado, gatilho de uso e exemplo de execução segura.
