---
name: otear-squad-orchestrator
description: Cria e coordena squads portateis do Otear OS.
version: 0.1.0
author: Marlon Douglas, Hermes Agent
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, squads, subagentes, orquestracao]
    related_skills: []
tools: [read_file, search_files, write_file, delegate_task]
---

# Orquestrador de Squads Otear

Modele squads multi-etapa e, quando disponivel, use subagentes Hermes. A definicao do
squad sempre e salva na vault; `delegate_task` e opcional e nunca deve ser presumido.

## Quando usar

- O aluno pede uma entrega com varias etapas ou papeis.
- O aluno pede para criar ou executar um squad.

Nao use para uma tarefa de papel unico que um agente ou skill resolve.

## Procedimento

1. Localize e leia `SOUL.md`, o contrato e o roteador com `search_files` e `read_file`.
   Conclua com a raiz e a rota identificadas.
2. Defina objetivo, entregavel final, etapas, dependencia entre etapas, revisao e criterio
   de aceite. Reaproveite um squad-base apenas como referencia.
3. Use `write_file` para salvar `produto-otear-os/meus-squads/<nome-kebab>.yaml` com
   `nome`, `objetivo`, `entrega_final`, `etapas`, `responsaveis`, `entradas`, `saidas` e
   `criterios_de_aceite`. Cada etapa precisa declarar uma saida que a proxima recebe.
4. Verifique com `read_file` se o YAML esta legivel e se toda dependencia aponta para uma
   etapa existente. Termine com o caminho do squad e a sequencia de execucao.
5. Se `delegate_task` estiver presente nesta sessao e o aluno autorizar executar, delegue
   apenas etapas independentes, fornecendo contexto minimo e exigindo saida estruturada.
   Se a ferramenta nao existir, execute sequencialmente no Hermes e declare esse limite.
6. Revise a entrega contra os criterios de aceite antes de reportar sucesso. Conclua com
   entregavel, arquivos gravados e limitacoes encontradas.

## Verificacao

Nunca afirme que houve subagentes sem resultado retornado por `delegate_task`. A ausencia
da ferramenta nao invalida o squad salvo; ela apenas exige execucao sequencial.
