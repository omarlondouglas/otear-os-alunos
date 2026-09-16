---
execution: inline
agent: squads/yt-thumbnails/agents/conceptor
inputFile: squads/yt-thumbnails/output/research-report.md
outputFile: squads/yt-thumbnails/output/thumbnail-concepts.md
---

# Step 03: Gerar Conceitos de Thumbnail

## Context Loading

Load these files before executing:
- `squads/yt-thumbnails/output/research-report.md` — pesquisa de contexto e referências
- `squads/yt-thumbnails/pipeline/data/research-focus.md` — tema e estilo do usuário
- `squads/yt-thumbnails/pipeline/data/domain-framework.md` — fórmulas de thumbnail
- `squads/yt-thumbnails/pipeline/data/output-examples.md` — exemplos de conceitos
- `squads/yt-thumbnails/pipeline/data/anti-patterns.md` — erros a evitar

## Instructions

### Process
1. Ler o relatório de pesquisa e identificar: tema, emoções-chave, padrões do nicho, oportunidades
2. Ler o estilo desejado pelo usuário (do research-focus.md)
3. Para cada uma das 5 fórmulas do domain-framework.md, avaliar se se aplica ao tema
4. Gerar 4 conceitos distintos usando fórmulas diferentes:
   - Conceito 1: Fórmula que melhor se encaixa no tema
   - Conceito 2: Fórmula alternativa com abordagem oposta
   - Conceito 3: Baseado nos gaps/oportunidades da pesquisa
   - Conceito 4: Estilo experimental/diferenciado
5. Para cada conceito, detalhar: sujeito, expressão, composição, cores (60-30-10), texto overlay, fundo, elementos secundários
6. Verificar cada conceito contra anti-patterns

## Output Format

```markdown
# Conceitos de Thumbnail: {tema do vídeo}

## Conceito 1: {nome descritivo}
**Fórmula**: {nome da fórmula usada}
**Descrição visual**: {1-2 frases descrevendo a cena}

### Elementos
- **Sujeito principal**: {descrição detalhada}
- **Expressão facial**: {descrição física específica}
- **Composição**: {posição dos elementos, regra dos terços}
- **Cores**: {60% X, 30% Y, 10% Z — com nomes de cores}
- **Texto overlay**: {máximo 3-4 palavras, fonte sugerida}
- **Fundo**: {descrição}
- **Elementos secundários**: {objetos, efeitos}
- **Por que funciona**: {justificativa baseada na pesquisa}

## Conceito 2: {nome descritivo}
(mesma estrutura)

## Conceito 3: {nome descritivo}
(mesma estrutura)

## Conceito 4: {nome descritivo}
(mesma estrutura)

## Recomendação
Minha recomendação é o **Conceito {N}** porque {justificativa}.
```

## Output Example

```markdown
# Conceitos de Thumbnail: Como IA vai substituir programadores

## Conceito 1: Choque Digital
**Fórmula**: Reação Emocional
**Descrição visual**: Close-up de homem com expressão de choque extremo, código verde sendo "dissolvido" ao lado

### Elementos
- **Sujeito principal**: Homem jovem, close-up do rosto ocupando 40% do frame
- **Expressão facial**: Olhos arregalados, sobrancelhas levantadas, boca aberta em O, mãos nas bochechas
- **Composição**: Rosto à esquerda (1/3), código dissolving à direita (2/3)
- **Cores**: 60% preto profundo, 30% verde matrix (#00FF41), 10% vermelho de alerta (#FF0000)
- **Texto overlay**: "ACABOU?" em Impact bold amarelo com outline preto
- **Fundo**: Preto com partículas de código verde flutuando
- **Elementos secundários**: Linhas de código se transformando em pixels/poeira
- **Por que funciona**: Expressão facial forte + código visual = alta relevância + gatilho emocional

## Conceito 2: Antes & Depois
**Fórmula**: Antes/Depois
**Descrição visual**: Split-screen — esquerda: dev estressado com código manual; direita: tela com IA fazendo tudo automaticamente

### Elementos
- **Sujeito principal**: Mesma pessoa nos dois lados, expressões opostas
- **Expressão facial**: Esquerda: cansado/frustrado. Direita: sorriso confiante
- **Composição**: Split vertical 50/50 com linha diagonal
- **Cores**: Esquerda: tons frios/cinza (60% cinza, 30% azul escuro). Direita: tons quentes/vibrantes (60% azul brilhante, 30% dourado)
- **Texto overlay**: Esquerda "2024" / Direita "2026" em Bebas Neue
- **Fundo**: Esquerda: escritório escuro e bagunçado. Direita: ambiente clean e futurista
- **Elementos secundários**: Esquerda: pilha de papéis, café. Direita: hologramas flutuantes
- **Por que funciona**: Contraste visual forte, conta uma história instantânea, gera curiosidade sobre a transformação

## Recomendação
Minha recomendação é o **Conceito 1** porque expressões faciais fortes são o #1 driver de CTR e o estilo "código se dissolvendo" é único no nicho.
```

## Veto Conditions

Reject and redo if ANY are true:
1. Menos de 3 conceitos gerados
2. Dois ou mais conceitos usam a mesma fórmula
3. Algum conceito tem mais de 4 palavras de texto overlay
4. Conceitos não têm cores específicas nomeadas

## Quality Criteria

- [ ] 4 conceitos distintos com fórmulas diferentes
- [ ] Cada conceito tem todos os elementos detalhados
- [ ] Cores seguem regra 60-30-10
- [ ] Texto overlay tem máximo 3-4 palavras
- [ ] Recomendação é justificada com dados da pesquisa
- [ ] Nenhum anti-pattern presente nos conceitos
