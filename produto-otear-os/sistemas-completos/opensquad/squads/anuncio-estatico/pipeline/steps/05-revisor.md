---
execution: inline
agent: revisor
inputFile: squads/anuncio-estatico/output/ad-copy.md
outputFile: squads/anuncio-estatico/output/review-report.md
---

# Step 05: Revisão de Qualidade

## Context Loading

Load these files before executing:
- `squads/anuncio-estatico/output/ad-copy.md` — Copy do anúncio
- `squads/anuncio-estatico/output/ad-image.html` — Design HTML do anúncio
- `squads/anuncio-estatico/pipeline/data/quality-criteria.md` — Critérios de avaliação
- `squads/anuncio-estatico/pipeline/data/anti-patterns.md` — Anti-patterns a verificar

## Instructions

### Process
1. Ler a copy do anúncio e avaliar contra os 5 critérios de copy
2. Ler o HTML do design e verificar especificações técnicas
3. Renderizar o HTML com Playwright e fazer verificação visual
4. Avaliar contra os 5 critérios de design
5. Verificar alinhamento copy ↔ design
6. Pontuar cada critério de 1-10 com justificativa
7. Emitir veredito: APPROVE / REJECT com feedback acionável

## Output Format

```
==============================
 REVIEW VERDICT: [APPROVE/REJECT]
 Overall Score: [X.X/10]
 Revision: #[N]
==============================

## Copy Scores

| Critério | Nota | Justificativa |
|----------|------|---------------|
| Clareza headline | X/10 | ... |
| Especificidade | X/10 | ... |
| Gatilho emocional | X/10 | ... |
| CTA acionável | X/10 | ... |
| Alinhamento público | X/10 | ... |

## Design Scores

| Critério | Nota | Justificativa |
|----------|------|---------------|
| Legibilidade 3s | X/10 | ... |
| Hierarquia visual | X/10 | ... |
| Contraste e cores | X/10 | ... |
| Branding | X/10 | ... |
| Alinhamento copy-imagem | X/10 | ... |

## Required Changes (if REJECT)
1. [Mudança específica com localização e sugestão]

## Strengths
- [Ponto forte identificado]

## Non-blocking Suggestions
- [Sugestão de melhoria opcional]
```

## Output Example

```
==============================
 REVIEW VERDICT: APPROVE
 Overall Score: 8.2/10
 Revision: #1
==============================

## Copy Scores

| Critério | Nota | Justificativa |
|----------|------|---------------|
| Clareza headline | 9/10 | "12 agentes de IA prontos em 8 semanas" é específica e clara |
| Especificidade | 9/10 | Números concretos: 12 agentes, 8 semanas, SDR listado |
| Gatilho emocional | 7/10 | Oportunidade presente mas poderia ser mais urgente |
| CTA acionável | 8/10 | "Garanta sua vaga" tem verbo imperativo + escassez implícita |
| Alinhamento público | 8/10 | Linguagem adequada para agências e freelancers |

## Design Scores

| Critério | Nota | Justificativa |
|----------|------|---------------|
| Legibilidade 3s | 9/10 | Headline e CTA são os primeiros elementos visíveis |
| Hierarquia visual | 8/10 | Headline > corpo > CTA bem definidos |
| Contraste e cores | 8/10 | Verde neon sobre fundo escuro, contraste excelente |
| Branding | 8/10 | @marlonlima.ia presente, cores da marca |
| Alinhamento copy-imagem | 8/10 | Destaques visuais nos números corretos |

## Strengths
- Especificidade excelente: números concretos criam credibilidade
- Design limpo e focado em uma mensagem

## Non-blocking Suggestions
- Considerar adicionar selo de garantia para reforçar confiança
```

## Veto Conditions

1. Alguma nota sem justificativa escrita
2. Veredito APPROVE com algum critério abaixo de 4/10

## Quality Criteria

- [ ] Todos os 10 critérios pontuados com justificativa
- [ ] Veredito consistente com as notas (>= 7 média = APPROVE)
- [ ] Feedback de REJECT inclui mudanças específicas e acionáveis
- [ ] Pelo menos 1 ponto forte identificado
