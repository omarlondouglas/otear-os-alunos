---
execution: inline
agent: copywriter
inputFile: squads/anuncio-estatico/pipeline/data/ad-brief.md
outputFile: squads/anuncio-estatico/output/ad-copy.md
---

# Step 02: Criação da Copy do Anúncio

## Context Loading

Load these files before executing:
- `squads/anuncio-estatico/pipeline/data/ad-brief.md` — Brief do anúncio com produto, objetivo e ângulo
- `squads/anuncio-estatico/pipeline/data/tone-of-voice.md` — Opções de tom de voz
- `squads/anuncio-estatico/pipeline/data/research-brief.md` — Frameworks de copywriting e referências
- `squads/anuncio-estatico/pipeline/data/output-examples.md` — Exemplos de copy para ads
- `squads/anuncio-estatico/pipeline/data/anti-patterns.md` — Erros a evitar
- `_opensquad/_memory/company.md` — Contexto da empresa

## Instructions

### Process
1. Ler o brief e identificar: produto, objetivo, ângulo emocional, público-alvo
2. Diagnosticar o nível de consciência do público (Schwartz) e escolher o framework de copy mais adequado (AIDA, PAS, BAB ou Hook-Story-Offer)
3. Ler tone-of-voice.md, recomendar o tom mais adequado ao brief
4. Escrever 3 opções de headline usando diferentes abordagens emocionais
5. Apresentar as 3 headlines ao usuário para seleção
6. Com a headline escolhida, escrever o corpo do anúncio (máx 4 linhas) e o CTA
7. Incluir direção visual sugerida para o designer

## Output Format

```
# Ad Copy — [Nome do Produto]

## Diagnóstico
- Nível de consciência: [unaware/problem-aware/solution-aware/product-aware/most-aware]
- Framework: [AIDA/PAS/BAB/Hook-Story-Offer]
- Tom de voz: [tom escolhido]
- Gatilho principal: [medo/oportunidade/curiosidade/autoridade/pertencimento]

## Copy Final

HEADLINE: [headline escolhida — máx 8 palavras]

CORPO:
[Linha 1 — proposta de valor principal]
[Linha 2 — prova ou dado de suporte]
[Linha 3 — diferencial ou mecanismo]
[Linha 4 — urgência ou escassez (opcional)]

CTA: [Verbo imperativo + benefício] →

## Direção Visual
- Destaque: [palavra ou número a destacar visualmente]
- Sugestão de layout: [posição headline, corpo, CTA]
- Cores sugeridas: [cores para destaque]
- Elementos extras: [ícones, selos, badges]
```

## Output Example

```
# Ad Copy — Mentoria Sua Agência de IA

## Diagnóstico
- Nível de consciência: Solution-aware
- Framework: PAS (Problem, Agitate, Solution)
- Tom de voz: Direto e Prático
- Gatilho principal: Oportunidade

## Copy Final

HEADLINE: 12 agentes de IA prontos em 8 semanas

CORPO:
Enquanto agências gastam meses tentando entender IA,
você sai com 12 agentes funcionando.
SDR, atendimento, follow-up, conteúdo e mais.
Sem programação. Suporte ao vivo toda semana.

CTA: Garanta sua vaga na mentoria →

## Direção Visual
- Destaque: "12" e "8 semanas" em verde neon
- Sugestão de layout: headline topo, corpo centro, CTA base
- Cores sugeridas: verde neon (#A3F12E) para números, branco para texto
- Elementos extras: ícones minimalistas dos tipos de agente
```

## Veto Conditions

1. Headline com mais de 10 palavras ou genérica (poderia ser de qualquer empresa)
2. CTA sem verbo no imperativo ou sem benefício claro
3. Uso de travessões (—) na copy

## Quality Criteria

- [ ] Headline específica e diferenciada (não genérica)
- [ ] Corpo com máximo 4 linhas, uma proposição de valor por linha
- [ ] CTA com verbo imperativo + benefício
- [ ] Direção visual alinhada com a copy
- [ ] Tom de voz consistente com o brief
