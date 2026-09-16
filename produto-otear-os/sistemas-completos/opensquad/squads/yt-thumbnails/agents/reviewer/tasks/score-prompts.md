---
task: "Score Thumbnail Prompts"
order: 1
input: |
  - thumbnail_prompts: Prompts gerados para Midjourney, DALL-E e Flux
  - quality_criteria: Critérios de avaliação com escalas
  - anti_patterns: Lista de erros a verificar
output: |
  - scores: Tabela de scores por critério e por modelo
  - anti_pattern_check: Resultado da verificação de anti-patterns
---

# Score Thumbnail Prompts

Avaliar cada prompt (Midjourney, DALL-E, Flux) contra os 8 critérios do quality-criteria.md.

## Process

1. Ler os 3 prompts e o conceito original que os gerou
2. Para cada prompt, avaliar contra cada um dos 8 critérios:
   - Clareza Visual (1-10)
   - Gatilho Emocional (1-10)
   - Curiosity Gap (1-10)
   - Contraste e Legibilidade (1-10)
   - Especificidade Técnica (1-10)
   - Composição e Layout (1-10)
   - Alinhamento com Canal (1-10)
   - Viabilidade de Geração (1-10)
3. Para cada score, escrever justificativa de 1-2 frases referenciando o prompt
4. Verificar cada prompt contra a lista de anti-patterns
5. Calcular médias por prompt e por critério
6. Identificar critérios abaixo de 4 (hard reject triggers)

## Output Format

```yaml
scoring:
  midjourney:
    clarity: { score: X, reason: "..." }
    emotion: { score: X, reason: "..." }
    curiosity: { score: X, reason: "..." }
    contrast: { score: X, reason: "..." }
    technical: { score: X, reason: "..." }
    composition: { score: X, reason: "..." }
    alignment: { score: X, reason: "..." }
    viability: { score: X, reason: "..." }
    average: X.X
  dalle:
    (same structure)
  flux:
    (same structure)
  overall_average: X.X
  anti_patterns:
    - pattern: "..."
      found_in: "..." 
      severity: "blocking/warning"
    # or empty list if none found
  hard_rejects: [] # criteria below 4
```

## Output Example

```yaml
scoring:
  midjourney:
    clarity: { score: 9, reason: "Descrição do sujeito e ação é imediata — 'man with shock expression looking at code being deleted' comunica em 1 segundo" }
    emotion: { score: 9, reason: "Expressão facial detalhada fisicamente (wide-eyed, open mouth) + cenário dramático gera impacto emocional forte" }
    curiosity: { score: 8, reason: "Código sendo deletado cria pergunta visual, mas poderia ter mais tensão com elemento misterioso" }
    contrast: { score: 9, reason: "Blue lighting vs dark background especificados, --no blurry garante nitidez" }
    technical: { score: 10, reason: "Todos os parâmetros presentes: --ar 16:9, --s 250, --q 2, --no, keywords de qualidade (4K, photorealistic)" }
    composition: { score: 8, reason: "'Left third of frame' segue regra dos terços. Poderia especificar espaço para texto overlay" }
    alignment: { score: 7, reason: "Estilo tech é consistente com @marlonlima_ia. Cores e mood alinham com nicho de IA" }
    viability: { score: 9, reason: "Prompt está dentro das capacidades do Midjourney v7, sem pedido de texto renderizado" }
    average: 8.6
  dalle:
    clarity: { score: 8, reason: "Descrição literal e clara, DALL-E vai entender bem cada elemento" }
    emotion: { score: 8, reason: "Expressão descrita mas menos vívida que o prompt Midjourney" }
    curiosity: { score: 8, reason: "Mesma estrutura de curiosity gap, adequada" }
    contrast: { score: 9, reason: "Cores nomeadas com hex codes, alto contraste especificado" }
    technical: { score: 9, reason: "Formato e dimensão especificados, linguagem literal adequada para DALL-E" }
    composition: { score: 8, reason: "Posição do sujeito clara, mas poderia detalhar mais o fundo" }
    alignment: { score: 7, reason: "Alinhado com identidade tech do canal" }
    viability: { score: 8, reason: "DALL-E pode ter dificuldade com a complexidade da cena de código, mas é viável" }
    average: 8.1
  flux:
    clarity: { score: 8, reason: "Foco em fotorealismo comunica bem o sujeito principal" }
    emotion: { score: 7, reason: "Expressão descrita mas com menos detalhes que Midjourney" }
    curiosity: { score: 7, reason: "Menos elementos de curiosity gap — foco é mais no retrato que na história" }
    contrast: { score: 8, reason: "Contraste entre luz azul e pele quente especificado" }
    technical: { score: 8, reason: "Especificações de câmera excelentes (85mm, f/1.4), mas falta aspect ratio explícito" }
    composition: { score: 7, reason: "Close-up descrito mas posição no frame poderia ser mais específica" }
    alignment: { score: 7, reason: "Estilo alinha com canal tech" }
    viability: { score: 9, reason: "Flux excele em fotorealismo — prompt está dentro de suas forças" }
    average: 7.6
  overall_average: 8.1
  anti_patterns: []
  hard_rejects: []
```

## Quality Criteria

- [ ] Todos os 8 critérios avaliados para cada um dos 3 prompts (24 scores total)
- [ ] Cada score tem justificativa referenciando o prompt específico
- [ ] Médias calculadas corretamente
- [ ] Anti-patterns verificados

## Veto Conditions

1. Algum critério não avaliado (score faltando)
2. Scores sem justificativa
