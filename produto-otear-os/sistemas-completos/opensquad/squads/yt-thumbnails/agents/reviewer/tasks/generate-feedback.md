---
task: "Generate Review Feedback"
order: 2
input: |
  - scores: Tabela de scores da task anterior
  - anti_pattern_check: Resultado da verificação
output: |
  - verdict: APROVAR / APROVAR COM REVISÕES / REJEITAR
  - feedback: Pontos fortes, correções obrigatórias, sugestões
  - best_prompt: Recomendação do melhor prompt com justificativa
---

# Generate Review Feedback

Compilar o feedback estruturado baseado nos scores e emitir veredito final.

## Process

1. Ler os scores da task anterior
2. Aplicar regras de decisão:
   - Média >= 7 + nenhum critério < 4 → APROVAR
   - Média >= 7 + critério não-crítico entre 4-6 → APROVAR COM REVISÕES
   - Média < 7 → REJEITAR
   - Qualquer critério < 4 → REJEITAR (hard trigger)
3. Compilar pontos fortes (scores >= 8) com referências específicas
4. Compilar correções obrigatórias (scores < 7 em critérios de peso alto) com solução
5. Compilar sugestões de melhoria (nice-to-have) para scores entre 7-8
6. Determinar o melhor prompt entre os 3 modelos baseado nos scores
7. Montar review report no formato final

## Output Format

```yaml
review:
  verdict: "APROVAR / APROVAR COM REVISÕES / REJEITAR"
  revision_number: 1
  strengths:
    - "..."
  blocking_fixes: # empty if APROVAR
    - problem: "..."
      solution: "..."
      affected_prompts: ["..."]
  suggestions: # non-blocking
    - "..."
  best_prompt:
    model: "Midjourney / DALL-E / Flux"
    reason: "..."
  summary: "..."
```

## Output Example

```yaml
review:
  verdict: "APROVAR COM REVISÕES"
  revision_number: 1
  strengths:
    - "Excelente uso de iluminação dramática no Midjourney — 'dramatic cool blue side lighting from monitor' é específico e vai gerar resultado cinematográfico"
    - "Especificidade técnica perfeita — todos os parâmetros presentes, aspect ratio correto, keywords de qualidade"
    - "Expressão facial bem detalhada nos prompts — 'wide eyes, raised eyebrows, open mouth' vai gerar emoção forte"
  blocking_fixes: []
  suggestions:
    - "Adicionar 'clean empty space in upper right for text overlay' em todos os prompts — garante espaço para texto em pós"
    - "Prompt Flux: adicionar expressão facial mais detalhada — incluir 'raised eyebrows, fully open eyes, parted lips showing teeth'"
    - "Considerar adicionar --style raw ao Midjourney para menos estilização e mais fotorealismo"
  best_prompt:
    model: "Midjourney"
    reason: "Média mais alta (8.6), melhor equilíbrio entre drama visual e especificidade técnica. Excelente em iluminação e emoção."
  summary: "Prompts de alta qualidade com média geral de 8.1/10. O prompt Midjourney é o mais forte. Sugestões de melhoria são non-blocking — os prompts podem ser usados como estão ou refinados com as sugestões."
```

## Quality Criteria

- [ ] Veredito consistente com os scores
- [ ] Pelo menos 1 ponto forte reconhecido
- [ ] Correções blocking (se houver) são específicas com solução
- [ ] Sugestões são acionáveis e referenciam prompts específicos
- [ ] Melhor prompt recomendado com justificativa quantitativa
- [ ] Summary em 2-3 frases cobre o essencial

## Veto Conditions

1. Veredito REJEITAR sem nenhuma correção blocking listada
2. Feedback genérico sem referência aos prompts específicos
