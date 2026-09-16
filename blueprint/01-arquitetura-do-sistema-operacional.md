---
title: Arquitetura do Otear OS
created: 2026-08-22
tags: [otear-os, arquitetura, agentes, squads]
---

# Arquitetura do Otear OS

## Intencao

Criar um sistema operacional proprio do Otear para montar, testar e operar agentes, skills e squads sem depender de caminhos locais ou nomes tecnicos externos.

## Camadas

| Camada | Funcao |
|---|---|
| Cockpit | conversa com o usuario, entende o pedido e aciona fluxos |
| Orquestrador | decide qual agente ou squad executa o trabalho |
| Contratos | define o formato padrao de agente, skill, squad, workflow e output |
| Criador | transforma uma ideia do usuario em agente, skill ou squad |
| Memoria | guarda manuais, decisoes, historico, biblioteca e conhecimento reutilizavel |
| Execucao | roda scripts, ferramentas, APIs e adaptadores permitidos |
| Entrega | salva o resultado final em uma pasta portatil |

## Contrato de agente do Otear OS

Um agente deve ter:

| Campo | Obrigatorio | Uso |
|---|---:|---|
| `id` | sim | identificador estavel |
| `name` | sim | nome humano |
| `role` | sim | papel operacional |
| `mission` | sim | missao clara |
| `inputs` | sim | dados que recebe |
| `outputs` | sim | entregas que produz |
| `tools` | nao | ferramentas permitidas |
| `memory` | nao | bases consultadas |
| `quality_check` | sim | criterio de conclusao |

## Contrato de skill do Otear OS

Uma skill deve ter:

| Campo | Obrigatorio | Uso |
|---|---:|---|
| `id` | sim | identificador estavel |
| `name` | sim | nome humano |
| `trigger` | sim | quando usar |
| `procedure` | sim | passo a passo de execucao |
| `inputs` | sim | informacoes necessarias |
| `outputs` | sim | resultado esperado |
| `quality_check` | sim | criterio de pronto |

## Contrato de squad do Otear OS

Um squad deve ter:

| Campo | Obrigatorio | Uso |
|---|---:|---|
| `id` | sim | identificador estavel |
| `name` | sim | nome humano |
| `purpose` | sim | resultado que o squad entrega |
| `agents` | sim | agentes participantes |
| `workflow` | sim | ordem de execucao |
| `inputs` | sim | briefing minimo |
| `outputs` | sim | artefatos finais |
| `handoffs` | sim | passagem entre agentes |
| `acceptance_criteria` | sim | quando considerar pronto |

## Fluxo operacional padrao

1. Usuario pede um resultado no cockpit.
2. Otear OS classifica o pedido.
3. O orquestrador escolhe agente, skill ou squad.
4. O sistema gera um plano curto.
5. Os agentes executam as etapas.
6. O validador aplica o checklist.
7. O resultado e salvo em output portatil.
8. Decisoes reutilizaveis voltam para a memoria.

## Regra de portabilidade

Nenhum agente, skill, squad, script ou manual final deve exigir caminho fixo do computador do criador.

Use sempre placeholders:

```text
{OTEAR_OS_ROOT}
{OTEAR_PRODUCT_ROOT}
{OTEAR_USER_AGENTS}
{OTEAR_USER_SKILLS}
{OTEAR_USER_SQUADS}
{USER_HOME}
```

## Identidade do Otear OS

Tudo nesta pasta faz parte do Otear OS.

Use os nomes dos agentes, skills, squads e workflows desta pasta para operar o sistema.

