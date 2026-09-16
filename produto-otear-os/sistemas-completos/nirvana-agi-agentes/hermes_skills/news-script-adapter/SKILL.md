---
name: news-script-adapter
description: "Transforma uma notícia, manchete, briefing ou artigo em roteiro curto para TikTok/Reels/Shorts usando padrões de hook, desenvolvimento, gatilhos, edição de tela e estilo de fala inspirados em creators analisados no projeto."
version: 1.0.0
author: O Tear
license: MIT
metadata:
  hermes:
    tags: [otear, news, script, tiktok, reels, shorts]
    category: content
---

# news-script-adapter

## When to Use

Use esta skill quando o cliente:

- mandar uma notícia e quiser transformar em roteiro
- pedir adaptação para TikTok, Reels ou Shorts
- quiser separar `hook`, `desenvolvimento`, `gatilho`, `edição/tela` e `delivery`
- quiser versões em estilos diferentes de creators

## Archetypes Disponíveis

Leia `references/creator-patterns.md` quando precisar da análise completa.

- `v_daily_journal` -> boletim factual, rotina, clareza
- `dylan_page` -> breaking news, urgência, crise
- `rpn` -> oportunidade prática, ferramenta, leverage
- `gabrieladamuchi` -> ruptura, obsolescência, monetização
- `gigaqian` -> explicação técnica com metáfora
- `dr_cintas` -> roundup comprimido, muita informação
- `kanekallaway` -> futuro, surpresa, mudança de paradigma

## Procedure

1. Extraia os fatos centrais da notícia.
2. Escolha o ângulo principal:
   - urgência
   - ameaça
   - oportunidade
   - ruptura
   - explicação
   - futuro
3. Escolha o primeiro gatilho emocional.
4. Escolha o arquétipo mais adequado.
5. Escreva o roteiro no formato abaixo.

## Output Padrão

```md
## Angle

## Theme

## Primary Trigger

## Script
Hook:

Development:

Closing:

## On-Screen Editing

## Delivery Notes
```

## Drafting Rules

- O hook precisa aparecer nas 1-2 primeiras frases.
- Não explique antes de criar interesse.
- O desenvolvimento precisa avançar a história ou esclarecer implicações.
- As instruções de tela devem apoiar o entendimento:
  - headline
  - screenshots
  - mapa
  - gráfico
  - lista numerada
  - facecam
  - demo
- Para notícia técnica, explique por que importa antes de aprofundar.
- Para crise, priorize status atual e consequência.
- Para IA/negócios, enfatize leverage, obsolescência ou vantagem competitiva.

## Default Blend

Se o cliente disser apenas "adapte com esses fundamentos", use:

- tensão de abertura de `dylan_page` ou `gabrieladamuchi`
- clareza de explicação de `gigaqian`
- consequência prática de `rpn`
- compressão de `dr_cintas`
- framing de futuro de `kanekallaway`
- disciplina factual de `v_daily_journal`

## Avoid

- hook genérico sem stakes
- introdução longa
- repetição do mesmo ponto
- notas de tela inúteis
- neutralidade excessiva quando o arquétipo pede tensão

