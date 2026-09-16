---
task: "Review Ad"
order: 1
input: |
  - ad-copy.md: Copy do anuncio com headline, corpo, CTA
  - ad-image.html: Design HTML do anuncio
  - quality-criteria.md: Criterios de avaliacao com pesos e minimos
output: |
  - review-report.md: Relatorio com scores, veredito e feedback
---

# Review Ad

Avalia a copy e o design de um anuncio estatico contra 10 criterios objetivos (5 copy + 5 design), emitindo veredito APPROVE ou REJECT com feedback acionavel.

## Process

1. **Carregar criterios**: Ler quality-criteria.md para entender pesos, minimos e regras de decisao.
2. **Avaliar copy**: Ler ad-copy.md. Pontuar cada um dos 5 criterios de copy (1-10) com justificativa escrita.
3. **Renderizar design**: Abrir ad-image.html em Playwright (1080x1080). Tirar screenshot para verificacao visual.
4. **Avaliar design**: Pontuar cada um dos 5 criterios de design (1-10) com justificativa.
5. **Calcular media**: Media de todos os 10 criterios.
6. **Aplicar regras**: APPROVE se media >= 7 e nenhum criterio < 4. REJECT caso contrario.
7. **Compilar relatorio**: Tabelas de scores, feedback detalhado, mudancas requeridas (se REJECT), pontos fortes, sugestoes opcionais.

## Output Format

```yaml
verdict: "APPROVE | REJECT"
overall_score: X.X
revision: N
copy_scores:
  - criterio: "..."
    nota: X
    justificativa: "..."
design_scores:
  - criterio: "..."
    nota: X
    justificativa: "..."
required_changes: ["..."]
strengths: ["..."]
suggestions: ["..."]
```

## Output Example

> Use as quality reference, not as rigid template.

```
==============================
 REVIEW VERDICT: APPROVE
 Overall Score: 8.2/10
 Revision: #1
==============================

## Copy Scores

| Criterio | Nota | Justificativa |
|----------|------|---------------|
| Clareza headline | 9/10 | "12 agentes de IA prontos em 8 semanas" especifica e clara |
| Especificidade | 9/10 | Numeros concretos: 12 agentes, 8 semanas |
| Gatilho emocional | 7/10 | Oportunidade presente, poderia ser mais urgente |
| CTA acionavel | 8/10 | "Garanta sua vaga" tem verbo imperativo + escassez |
| Alinhamento publico | 8/10 | Linguagem adequada para agencias |

## Design Scores

| Criterio | Nota | Justificativa |
|----------|------|---------------|
| Legibilidade 3s | 9/10 | Headline e CTA sao os primeiros elementos visiveis |
| Hierarquia visual | 8/10 | Headline > corpo > CTA bem definidos |
| Contraste e cores | 8/10 | Verde neon sobre fundo escuro, contraste excelente |
| Branding | 8/10 | @marlonlima.ia presente, cores da marca |
| Alinhamento copy-imagem | 8/10 | Destaques visuais nos numeros corretos |

## Strengths
- Especificidade excelente nos numeros
- Design limpo e focado

## Non-blocking Suggestions
- Considerar selo de garantia para reforcar confianca
```

## Quality Criteria

- [ ] Todos os 10 criterios pontuados com justificativa
- [ ] Veredito consistente com as notas
- [ ] Feedback de REJECT inclui mudancas especificas
- [ ] Pelo menos 1 ponto forte identificado

## Veto Conditions

Reject and redo if ANY are true:
1. Alguma nota sem justificativa escrita
2. Veredito APPROVE com criterio abaixo de 4/10
