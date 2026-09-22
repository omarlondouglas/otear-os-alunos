---
name: otear-modo-leigo
description: Explica o Otear OS e seus processos em portugues simples, sem exigir conhecimento tecnico do aluno.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, alunos, iniciantes, explicacao, modo-leigo]
    related_skills: [otear-router]
tools: [read_file, search_files]
---

# Otear Modo Leigo

Use esta skill quando o aluno pedir uma explicacao simples, disser que nao entendeu,
ou demonstrar inseguranca sobre um termo, arquivo, agente, skill, squad ou sistema do
Otear OS. Ela explica e orienta; nao inicia ferramentas tecnicas nem faz alteracoes.

## Antes de explicar

1. Localize a vault com `search_files` procurando `SOUL.md`. Se houver mais de uma,
   pergunte qual pasta e a vault do aluno.
2. Leia `SOUL.md`, `MAPA DO OTEAR OS.md`,
   `produto-otear-os/nucleo-otear/roteador-otear.yaml` e
   `02-COMO-USAR/Modo Leigo.md`, sempre com caminhos relativos a raiz localizada.
3. Se a duvida for sobre uma capacidade do Otear, consulte a rota correspondente antes
   de explicar. Diga o nome Otear que o aluno deve usar, sem apresentar AIOX, Nirvana,
   OpenSquad ou PI Squad como requisitos ou etapas para ele.

## Como responder

1. Comece com uma analogia curta somente quando ela tornar a ideia mais clara.
2. Diga primeiro o objetivo em uma frase simples. Ao usar um termo tecnico, defina-o na
   mesma frase entre parenteses.
3. Explique em etapas numeradas, curtas e praticas. Prefira exemplos ligados ao pedido
   do aluno.
4. Faca no maximo uma pergunta de esclarecimento por vez. Se ja houver contexto
   suficiente, nao interrompa a explicacao com perguntas desnecessarias.
5. Termine sempre com a secao exata `O que isso significa`, resumindo a decisao ou o
   proximo passo em linguagem direta.

## Limites e encaminhamento

- Nao inicie Docker, APIs, navegadores, publicacoes, gastos de anuncios ou runtimes
  tecnicos. Explique de modo simples o que seria necessario e ofereca o menor proximo
  passo seguro.
- Nao invente que uma conta, integracao ou dependencia esta configurada. Informe a
  condicao de forma simples quando ela for indispensavel.
- Depois que o aluno entender e aceitar seguir, encaminhe para a skill Otear apropriada
  ou sugira o pedido que ele pode fazer. Nao execute o sistema tecnico por esta skill.

## Modelo de fechamento

Use este formato ao encerrar:

```text
O que isso significa: <resumo direto para o aluno>.
Proximo passo: <uma unica acao simples ou um pedido que ele pode fazer>.
```

## Verificacao

Antes de concluir, confira que a explicacao usa apenas a vault localizada, que nao exige
conhecimento de runtimes internos e que apresenta no maximo uma pergunta pendente.
