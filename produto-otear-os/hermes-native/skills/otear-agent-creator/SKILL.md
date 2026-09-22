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

Crie definicoes de agentes para a vault do aluno. Um agente define um papel e criterios;
ele nao garante que o Hermes tenha subagentes ou ferramentas extras disponiveis.

## Quando usar

- O aluno pede um especialista reutilizavel, como qualificador de leads ou revisor.

Nao use quando um procedimento simples basta; nesse caso crie uma skill.

## Procedimento

1. Localize `SOUL.md` com `search_files` e confirme a raiz unica da vault. Conclua
   somente depois de identificar onde fica `produto-otear-os/meus-agentes`.
2. Use `read_file` em um agente-base parecido e no contrato operacional. Extraia apenas
   padroes uteis para o papel solicitado.
3. Especifique papel, objetivo, entradas aceitas, limites, formato da entrega e criterios
   de qualidade. Nao atribua acesso a dados, APIs ou ferramentas que a sessao nao possui.
4. Use `write_file` para criar `produto-otear-os/meus-agentes/<nome-kebab>.agent.md`.
   Inclua secoes: Identidade, Missao, Entradas, Procedimento, Limites e Saida.
5. Use `read_file` para verificar o arquivo, checar caminhos relativos e remover dados
   pessoais, segredos e referencias a clientes. Termine com caminho e prompt de teste.

## Verificacao

O agente esta pronto quando o arquivo esta legivel, descreve uma saida verificavel e pode
ser acionado pelo Hermes como instrucao local, mesmo sem delegacao.
