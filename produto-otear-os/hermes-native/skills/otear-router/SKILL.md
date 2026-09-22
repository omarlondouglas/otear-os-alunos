---
name: otear-router
description: Roteia pedidos pela vault portatil do Otear OS.
version: 0.1.0
author: Marlon Douglas, Hermes Agent
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, roteamento, vault, alunos]
    related_skills: []
tools: [read_file, search_files]
---

# Roteador Otear OS

Use esta skill para localizar a vault do Otear OS e escolher uma rota antes de
executar uma tarefa. Ela nao inicia runtimes AIOX, Nirvana, Docker ou servicos
externos por conta propria.

## Quando usar

- O aluno pede qualquer entrega pelo Otear OS.
- A tarefa menciona agentes, skills, squads ou um sistema do Otear.

Nao use para operar um projeto externo que nao esteja na vault.

## Procedimento

1. Use `search_files` para localizar `SOUL.md` a partir do diretorio de trabalho. Se
   houver mais de um resultado, peca ao aluno a raiz correta. Conclua somente com uma
   raiz de vault identificada.
2. Use `read_file` nesta ordem: `SOUL.md`,
   `produto-otear-os/nucleo-otear/CONTRATO-OPERACIONAL.md`,
   `produto-otear-os/nucleo-otear/roteador-otear.yaml` e
   `produto-otear-os/catalogo-integracao.json`. Todos os caminhos sao relativos a raiz.
3. Compare o pedido com uma rota e confirme que os arquivos declarados existem antes de
   citar a rota. Conclua com o nome da rota e os arquivos que serao usados.
4. Leia os materiais da rota. AIOX e Nirvana sao referencia de metodo; nao diga que
   foram executados como runtime Hermes.
5. Antes de iniciar um componente tecnico, informe requisitos indicados no catalogo e
   solicite configuracao quando ela for indispensavel. Conclua sem prometer uma acao
   externa que nao foi executada.

## Verificacao

Informe: raiz identificada, rota escolhida, fontes locais lidas e qualquer requisito
externo pendente.
