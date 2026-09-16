---
task: extractDesign()
responsavel: "Radar"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: referenceUrl
    tipo: string
    obrigatorio: true
    descricao: "URL da pÃ¡gina de referÃªncia para extrair design system"

Saida:
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Design tokens extraÃ­dos em formato CSS custom properties (destination: lp-design-architect)"
  - nome: visualStyle
    tipo: object
    obrigatorio: true
    descricao: "AnÃ¡lise do estilo visual: categoria, dark mode, animaÃ§Ãµes (destination: lp-design-architect)"

Checklist:
  pre-conditions:
    - "[ ] URL de referÃªncia acessÃ­vel"
  post-conditions:
    - "[ ] Paleta de cores extraÃ­da (primÃ¡ria, secundÃ¡ria, neutros)"
    - "[ ] Tipografia identificada (families, sizes, weights)"
    - "[ ] EspaÃ§amento mapeado (section padding, gaps, container)"
    - "[ ] Bordas e sombras capturadas"
    - "[ ] Estilo visual categorizado"
    - "[ ] Estrutura de seÃ§Ãµes documentada"
    - "[ ] Tokens formatados como CSS custom properties"

Performance:
  duration_expected: "3 minutes"
  cacheable: true
  parallelizable: true
---

# extractDesign()

## DescriÃ§Ã£o

Acessa a URL de referÃªncia, extrai todos os elementos visuais (cores, tipografia, espaÃ§amento, sombras, layout) e transforma em design tokens utilizÃ¡veis pelo pipeline.

## Passos

1. **Fetch da pÃ¡gina** â€” WebFetch da URL completa.
2. **Extrair CSS** â€” Computed styles, custom properties, classes principais.
3. **Mapear cores** â€” Identificar paleta primÃ¡ria, secundÃ¡ria, neutros, gradientes.
4. **Mapear tipografia** â€” Font families, sizes, weights, line-heights.
5. **Mapear espaÃ§amento** â€” Padding de seÃ§Ãµes, gaps, container width.
6. **Mapear bordas/sombras** â€” Border radius, box-shadow levels.
7. **Analisar layout** â€” Grid, breakpoints, estrutura de seÃ§Ãµes.
8. **Categorizar estilo** â€” Minimalista, bold, glassmorphism, etc.
9. **Verificar dark mode** â€” Se existe alternativa dark.
10. **Gerar output** â€” `extracted-design-tokens.md` com CSS custom properties.

