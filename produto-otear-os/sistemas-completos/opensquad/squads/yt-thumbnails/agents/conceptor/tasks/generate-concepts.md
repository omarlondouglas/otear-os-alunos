---
task: "Generate Thumbnail Concepts"
order: 1
input: |
  - research_report: Análise de contexto e referências do nicho
  - research_focus: Tema e estilo desejado
  - domain_framework: Fórmulas de thumbnail
output: |
  - concepts: 4 conceitos visuais distintos com todos os elementos
---

# Generate Thumbnail Concepts

Gerar 4 conceitos visuais distintos para a thumbnail, cada um usando uma fórmula diferente do domain-framework.

## Process

1. Ler o research report e extrair: tema, emoções-chave, padrões do nicho, gaps
2. Ler o estilo desejado pelo usuário (do research-focus.md)
3. Selecionar as 4 fórmulas mais adequadas para o tema:
   - Fórmula 1: a que melhor combina com o tema + estilo do usuário
   - Fórmula 2: abordagem oposta (se F1 é emocional, F2 é conceitual)
   - Fórmula 3: baseada em gap/oportunidade identificada na pesquisa
   - Fórmula 4: experimental ou combinação de fórmulas
4. Para cada conceito, definir todos os elementos visuais
5. Verificar contra anti-patterns
6. Escolher recomendação

## Output Format

```yaml
concepts:
  - name: "..."
    formula: "..."
    visual_description: "..."
    subject: "..."
    expression: "..."
    composition: "..."
    colors:
      dominant_60: "... (#hex)"
      secondary_30: "... (#hex)"
      accent_10: "... (#hex)"
    text_overlay: "..."
    background: "..."
    secondary_elements: "..."
    why_it_works: "..."
recommendation:
  concept: "..."
  reason: "..."
```

## Output Example

```yaml
concepts:
  - name: "Choque Digital"
    formula: "Reação Emocional"
    visual_description: "Close-up de homem com expressão de choque extremo, código verde sendo dissolvido ao lado"
    subject: "Homem jovem, close-up do rosto ocupando 40% do frame esquerdo"
    expression: "Olhos arregalados ao máximo, sobrancelhas levantadas, boca aberta em O, mãos nas bochechas estilo Home Alone"
    composition: "Rosto à esquerda (1/3), código dissolving à direita (2/3), ponto focal no rosto"
    colors:
      dominant_60: "Preto profundo (#0a0a0a)"
      secondary_30: "Verde matrix (#00FF41)"
      accent_10: "Vermelho alerta (#FF0000)"
    text_overlay: "ACABOU?"
    background: "Preto com partículas de código verde flutuando"
    secondary_elements: "Linhas de código se transformando em pixels/poeira digital"
    why_it_works: "Expressão facial forte é #1 driver de CTR. Código dissolving cria curiosity gap visual"

  - name: "Evolução Forçada"
    formula: "Antes/Depois"
    visual_description: "Split vertical — esquerda: dev estressado com código manual; direita: ambiente futurista com IA"
    subject: "Mesma pessoa nos dois lados com expressões contrastantes"
    expression: "Esquerda: olhos cansados, testa franzida, boca cerrada. Direita: sorriso leve confiante, olhos brilhantes"
    composition: "Split vertical 50/50 com linha diagonal sutil separando os lados"
    colors:
      dominant_60: "Cinza escuro esquerda (#2d2d2d) / Azul brilhante direita (#0066FF)"
      secondary_30: "Laranja código esquerda (#FF6B35) / Dourado IA direita (#FFD700)"
      accent_10: "Vermelho error esquerda (#FF0000) / Verde sucesso direita (#00FF00)"
    text_overlay: "2024 → 2026"
    background: "Esquerda: escritório escuro com monitores. Direita: ambiente clean futurista"
    secondary_elements: "Esquerda: pilha de papéis, xícara vazia. Direita: hologramas flutuantes de IA"
    why_it_works: "Antes/depois é fórmula comprovada. Contraste visual extremo conta história instantânea"

recommendation:
  concept: "Choque Digital"
  reason: "Expressões faciais fortes são o #1 driver de CTR (42.3% aumento). Código dissolving é visual único no nicho (gap identificado na pesquisa)"
```

## Quality Criteria

- [ ] 4 conceitos com fórmulas diferentes
- [ ] Cada conceito tem TODOS os campos preenchidos
- [ ] Cores com hex codes
- [ ] Texto overlay ≤ 4 palavras
- [ ] Expressões descritas fisicamente
- [ ] Recomendação justificada

## Veto Conditions

1. Menos de 3 conceitos
2. Dois conceitos com mesma fórmula
3. Algum conceito com texto overlay > 4 palavras
