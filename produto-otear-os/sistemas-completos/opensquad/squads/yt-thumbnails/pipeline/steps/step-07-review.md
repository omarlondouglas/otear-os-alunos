---
execution: inline
agent: squads/yt-thumbnails/agents/reviewer
inputFile: squads/yt-thumbnails/output/thumbnail-prompts.md
outputFile: squads/yt-thumbnails/output/review-report.md
---

# Step 07: Revisão de Qualidade

## Context Loading

Load these files before executing:
- `squads/yt-thumbnails/output/thumbnail-prompts.md` — prompts criados
- `squads/yt-thumbnails/output/thumbnail-concepts.md` — conceito original
- `squads/yt-thumbnails/output/research-report.md` — pesquisa de contexto
- `squads/yt-thumbnails/pipeline/data/quality-criteria.md` — critérios de avaliação
- `squads/yt-thumbnails/pipeline/data/anti-patterns.md` — erros a verificar

## Instructions

### Process
1. Ler os prompts gerados e o conceito original
2. Para cada critério do quality-criteria.md, avaliar cada prompt (Midjourney, DALL-E, Flux)
3. Avaliar: Clareza Visual, Gatilho Emocional, Curiosity Gap, Contraste/Legibilidade, Especificidade Técnica, Composição, Alinhamento com Canal, Viabilidade
4. Verificar se algum anti-pattern está presente
5. Compilar feedback específico e acionável para cada problema encontrado
6. Emitir veredito: APROVAR, APROVAR COM REVISÕES, ou REJEITAR

## Output Format

```markdown
# Review Report: Thumbnail Prompts

## Veredito: {APROVAR / APROVAR COM REVISÕES / REJEITAR}

## Scores
| Critério | Midjourney | DALL-E | Flux | Média |
|----------|-----------|--------|------|-------|
| Clareza Visual | X/10 | X/10 | X/10 | X/10 |
| Gatilho Emocional | X/10 | X/10 | X/10 | X/10 |
| Curiosity Gap | X/10 | X/10 | X/10 | X/10 |
| Contraste | X/10 | X/10 | X/10 | X/10 |
| Especificidade Técnica | X/10 | X/10 | X/10 | X/10 |
| Composição | X/10 | X/10 | X/10 | X/10 |
| Alinhamento Canal | X/10 | X/10 | X/10 | X/10 |
| Viabilidade | X/10 | X/10 | X/10 | X/10 |
| **MÉDIA** | **X/10** | **X/10** | **X/10** | **X/10** |

## Feedback Detalhado
### Pontos Fortes
- {ponto forte 1 com referência ao prompt}
- {ponto forte 2}

### Correções Obrigatórias (se REJEITAR)
1. {problema} → {solução específica}

### Sugestões de Melhoria (não-blocking)
1. {sugestão} → {como melhorar}

## Melhor Prompt
Recomendo usar o prompt **{Midjourney/DALL-E/Flux}** porque {justificativa}.
```

## Output Example

```markdown
# Review Report: Thumbnail Prompts

## Veredito: APROVAR COM REVISÕES

## Scores
| Critério | Midjourney | DALL-E | Flux | Média |
|----------|-----------|--------|------|-------|
| Clareza Visual | 9/10 | 8/10 | 8/10 | 8.3 |
| Gatilho Emocional | 9/10 | 8/10 | 7/10 | 8.0 |
| Curiosity Gap | 8/10 | 8/10 | 7/10 | 7.7 |
| Contraste | 9/10 | 9/10 | 8/10 | 8.7 |
| Especificidade Técnica | 10/10 | 9/10 | 8/10 | 9.0 |
| Composição | 8/10 | 8/10 | 7/10 | 7.7 |
| Alinhamento Canal | 7/10 | 7/10 | 7/10 | 7.0 |
| Viabilidade | 9/10 | 8/10 | 9/10 | 8.7 |
| **MÉDIA** | **8.6** | **8.1** | **7.6** | **8.1** |

## Feedback Detalhado
### Pontos Fortes
- Excelente uso de iluminação dramática no prompt Midjourney — "dramatic side lighting" é específico e eficaz
- Cores vibrantes e contrastantes em todos os prompts

### Sugestões de Melhoria
1. Prompt Flux poderia ser mais específico na expressão facial — adicionar "raised eyebrows, wide open eyes, slightly parted lips"
2. Considerar adicionar "clean space in upper right for text overlay" em todos os prompts

## Melhor Prompt
Recomendo usar o prompt **Midjourney** porque oferece o melhor equilíbrio entre drama visual e fotorealismo.
```

## Veto Conditions

Reject and redo if ANY are true:
1. Algum critério não foi avaliado (score faltando)
2. Veredito REJEITAR sem correções obrigatórias listadas
3. Feedback é genérico sem referência aos prompts específicos

## Quality Criteria

- [ ] Todos os 8 critérios avaliados para cada prompt
- [ ] Scores têm justificativa
- [ ] Feedback é acionável (não "melhorar contraste" mas "adicionar 'high contrast, vivid colors' ao prompt")
- [ ] Melhor prompt é recomendado com justificativa
- [ ] Anti-patterns verificados
