---
name: seo-auditor-generate-pdf
agent: seo-auditor
description: Gerar PDF do relatÃ³rio SEO a partir dos dados coletados
---

# Generate SEO Report PDF

## Inputs
- `seo-audit-raw.json`: Dados brutos do audit
- `client_name`: Nome do cliente
- `design_tokens`: Cores do design system do cliente

## Tecnologia
Usar `@react-pdf/renderer` para gerar o PDF no Node.js:
- Componentes React renderizados em PDF
- Estilizado com as cores do design system do cliente
- Profissional e pronto pra enviar

## Template de Componentes

### ScoreCircle
CÃ­rculo SVG com score numÃ©rico no centro:
- Verde: score >= 90
- Laranja: score 50-89
- Vermelho: score < 50

### ChecklistItem
Linha com Ã­cone âœ… ou âŒ + texto descritivo

### MetricBar
Barra horizontal mostrando valor vs threshold:
- Good (verde): dentro do limite
- Needs Improvement (amarelo): prÃ³ximo do limite
- Poor (vermelho): acima do limite

### KeywordRow
Linha com keyword, volume estimado, posiÃ§Ã£o atual, dificuldade

## Output
- `artifacts/seo-report.pdf`

