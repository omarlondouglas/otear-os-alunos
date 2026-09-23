---
name: otear-agent-creator
description: Cria agentes portateis na area do aluno Otear.
version: 0.1.0
author: Marlon Douglas, Hermes Agent
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, agentes, criacao, alunos]
    related_skills: []
tools: [read_file, search_files, write_file]
---

# Criador de Agentes Otear

## Propósito e limites

Cria definições portáteis de agentes na área do aluno. Não instala componentes globais e não presume ferramentas, acessos ou delegacao.

## Fontes portáteis

Localize uma única vault por `SOUL.md`. Leia e confirme estes caminhos relativos antes de agir:

- `produto-otear-os/nucleo-otear/CONTRATO-OPERACIONAL.md`
- `produto-otear-os/nucleo-otear/roteador-otear.yaml`
- `produto-otear-os/nucleo-otear/qualidade-e-confiabilidade.md`
- `produto-otear-os/meus-agentes/README.md`
- `produto-otear-os/skills-base/criar-agente.skill.md`
- `produto-otear-os/workflows-base/criar-agente.md`
- `produto-otear-os/agentes-base/orquestrador-otear.agent.md`

## Entradas mínimas

Colete papel, missao, usuário, entradas, saida, limites e nome. Se houver lacuna indispensável, peça apenas esse dado.

## Fluxo operacional

1. Confirme que o pedido precisa de um papel persistente, e não somente de um procedimento.
2. Leia as fontes e extraia o padrão aplicavel sem atribuir capacidades inexistentes.
3. Defina identidade, missao, entradas, processo, limites, formato de saida e critério de qualidade.
4. Grave `produto-otear-os/meus-agentes/<nome-kebab>.agent.md` quando houver autorização.
5. Reabra e teste a definição com um prompt curto; remova caminhos pessoais, segredos e promessas de ferramentas.

## Entregáveis

Entregue arquivo legivel, gatilho de uso, exemplo de acionamento e pendências.

## Critérios de qualidade

O agente deve ter papel não ambiguo, saida verificavel, limites claros e nenhum dado sensivel.

## Fallback para integrações opcionais

Se faltar ferramenta, permissão ou delegacao, produza a definição local e declare o limite; não tente contornar a ausência.
