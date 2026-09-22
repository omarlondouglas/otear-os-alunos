---
name: otear-apuracao-fontes
description: Apura uma notícia em fontes verificáveis e salva um dossiê de evidências, consensos, divergências e lacunas.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, jornalismo, apuracao, fontes]
    related_skills: [otear-noticias, otear-pesquisa-noticias, otear-verificacao-factual]
tools: [read_file, write_file, search_files]
---

# Otear Apuração de Fontes

Use esta skill para transformar um tema ou uma alegação em um dossiê editorial verificável.
Ela complementa `otear-noticias`; não é um runtime do OpenSquad.

## Antes de começar

Peça o tema, a janela de tempo, o país/região quando necessário e o objetivo editorial.
Para fatos atuais, só prossiga se a sessão puder acessar fontes verificáveis. Nunca invente
URLs, datas, números, citações ou o conteúdo de uma fonte.

## Processo

1. Priorize documento oficial, fonte primária e veículos confiáveis; registre URL, veículo,
   data de publicação e data da consulta.
2. Colete ao menos três fontes independentes quando isso for viável. Se não for, declare a
   limitação em vez de preencher lacunas por inferência.
3. Separe fatos atribuídos, citações, contexto e interpretações. Compare valores, nomes,
   datas e cronologia entre as fontes.
4. Classifique o resultado em consensos, contradições, fatos de fonte única e lacunas.
5. Salve o dossiê em `produto-otear-os/entregas/noticias/` com nome descritivo e data.

## Estrutura de entrega

Inclua `Fontes coletadas`, `Linha do tempo`, `Pontos de consenso`, `Contradições e
divergências`, `Fatos de fonte única`, `Lacunas` e `Limitações da apuração`. Cada fato deve
apontar para a fonte correspondente.

## Verificação

Confira se toda URL foi realmente consultada, se há atribuição em cada alegação importante e
se fatos não confirmados estão claramente marcados. Encaminhe o dossiê para
`otear-verificacao-factual` antes de tratá-lo como texto publicável.
