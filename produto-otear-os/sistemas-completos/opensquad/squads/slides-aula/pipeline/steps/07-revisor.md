---
id: revisor
type: step
execution: inline
agent: revisor
label: "Revisão de qualidade da apresentação"
inputFile: "squads/slides-aula/output/slides-content.md"
outputFile: "squads/slides-aula/output/review-report.md"
---

# Revisor — Controle de Qualidade

## Contexto

Você recebeu o conteúdo dos slides e o JSON do Designer.
Sua missão: revisar qualidade didática e design antes de apresentar ao usuário.

## Processo

1. Ler o conteúdo dos slides (slides-content.md)
2. Aplicar checklist de revisão de conteúdo (progressão didática, headlines, listas, CTA)
3. Ler o slides-data.json do Designer
4. Aplicar checklist de revisão de design (JSON válido, temas, elementos)
5. Produzir relatório com aprovação ou lista de correções

## Veto Conditions

- Slides com headlines maiores que 8 palavras não reportados
- CTA ausente não reportado
- Erros ortográficos não reportados
