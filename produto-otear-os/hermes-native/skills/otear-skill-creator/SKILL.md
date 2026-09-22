---
name: otear-skill-creator
description: Cria skills portateis na area do aluno Otear.
version: 0.1.0
author: Marlon Douglas, Hermes Agent
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, skills, criacao, alunos]
    related_skills: []
tools: [read_file, search_files, write_file]
---

# Criador de Skills Otear

Crie uma skill reutilizavel na vault do aluno. Esta skill produz um arquivo de
conhecimento do Otear; nao instala nem altera skills globais do Hermes.

## Quando usar

- O aluno descreve um procedimento repetivel e pede uma skill.

Nao use para uma tarefa unica; execute a tarefa ou crie um agente quando o papel for
mais importante que o procedimento.

## Procedimento

1. Localize a raiz com `search_files` procurando `SOUL.md`; confirme uma unica vault.
   Termine a etapa apenas quando a raiz estiver clara.
2. Use `read_file` em `produto-otear-os/minhas-skills/README.md` e em uma skill-base
   relacionada, se existir. Reaproveite o padrao, sem copiar instrucoes conflitantes.
3. Defina com o aluno: objetivo, gatilhos, entradas, saidas, limites e criterios de
   qualidade. Termine com uma especificacao curta aprovada ou explicitamente inferida.
4. Crie `produto-otear-os/minhas-skills/<nome-kebab>.skill.md` com titulo, objetivo,
   quando usar, entradas, procedimento numerado, saida esperada, limites e checklist.
   Use `write_file` e somente caminho relativo a raiz da vault.
5. Use `read_file` para conferir que o arquivo existe, tem conteudo e nao contem
   caminhos absolutos, credenciais ou instrucoes para instalar software. Termine citando
   o caminho salvo e um prompt de teste.

## Verificacao

O sucesso exige arquivo legivel em `minhas-skills`, nome em kebab-case, procedimento
repetivel e um teste manual descrito. Para disponibilizar a skill globalmente, o aluno
deve decidir isso depois usando as opcoes da propria versao do Hermes.
