---
task: reviewDesignConsistency()
responsavel: "Shield"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Design tokens definidos â€” cores, tipografia, espaÃ§amento, bordas (source: defineDesignTokens())"
  - nome: componentSpecs
    tipo: file
    obrigatorio: true
    descricao: "EspecificaÃ§Ãµes dos componentes atÃ´micos â€” atoms, molecules, organisms (source: createAtomicComponents())"
  - nome: contrastReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de contraste de cores gerado na definiÃ§Ã£o dos tokens (source: defineDesignTokens())"
  - nome: tokensCssFile
    tipo: file
    obrigatorio: true
    descricao: "Arquivo CSS com tokens implementados â€” variÃ¡veis CSS custom properties (source: implementDesignSystem())"

Saida:
  - nome: designReview
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio detalhado de revisÃ£o de consistÃªncia visual com issues e sugestÃµes (destination: lp-design-architect para correÃ§Ãµes)"
  - nome: designScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de qualidade do design por dimensÃ£o (destination: produceFinalReport())"

Checklist:
  pre-conditions:
    - "[ ] Design system implementado com tokens CSS"
    - "[ ] RelatÃ³rio de contraste existe e foi gerado por defineDesignTokens()"
    - "[ ] EspecificaÃ§Ãµes dos componentes atÃ´micos disponÃ­veis"
    - "[ ] Arquivo CSS de tokens implementado"
  post-conditions:
    - "[ ] ConsistÃªncia do design system verificada"
    - "[ ] Contraste WCAG AAA verificado para TODOS os pares em ambos os modos light E dark"
    - "[ ] Hierarquia tipogrÃ¡fica consistente"
    - "[ ] Sistema de espaÃ§amento seguido"
    - "[ ] Comportamento responsivo verificado"
    - "[ ] Issues categorizados como BLOCKER/WARNING/INFO"

Performance:
  duration_expected: "12 minutes"
  cacheable: false
  parallelizable: false
---

# reviewDesignConsistency()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  designTokens         â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  designReview           â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  reviewDesign        â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  componentSpecs       â”‚â”€â”€â”€â”€â”€â”€>â”‚  Consistency         â”‚â”€â”€â”€â”€â”€â”€>â”‚  designScore            â”‚
â”‚  (file)               â”‚       â”‚  @Shield             â”‚       â”‚  (object)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  contrastReport       â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚               â”‚
â”‚  (file)               â”‚       â”‚                      â”‚               â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â–¼                   â–¼
â”‚  tokensCssFile        â”‚â”€â”€â”€â”€â”€â”€>                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  (file)               â”‚                                      â”‚ lp-design-       â”‚ â”‚ produceFinal â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â”‚ architect (fixes)â”‚ â”‚ Report()     â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `reviewDesignConsistency()` realiza uma **auditoria completa de consistÃªncia visual** do design system e sua implementaÃ§Ã£o. O agente **Shield** verifica se os tokens definidos foram corretamente implementados, se o contraste atende ao nÃ­vel WCAG AAA em todos os modos (light e dark), se a hierarquia tipogrÃ¡fica Ã© consistente e se o sistema de espaÃ§amento estÃ¡ sendo seguido.

O review compara as especificaÃ§Ãµes dos componentes atÃ´micos contra os tokens CSS implementados, verifica todos os pares de cores de texto/fundo para conformidade de contraste, valida a escala tipogrÃ¡fica e o ritmo vertical, e analisa o comportamento responsivo dos componentes.

## Passos

1. **Carregar todos os inputs** â€” Ler `designTokens`, `componentSpecs`, `contrastReport` e `tokensCssFile` para contexto completo.
2. **Verificar implementaÃ§Ã£o dos tokens** â€” Comparar os tokens definidos em `designTokens` com as variÃ¡veis CSS em `tokensCssFile`, identificando tokens nÃ£o implementados ou com valores divergentes.
3. **Auditar contraste WCAG AAA (light mode)** â€” Verificar todos os pares de cores texto/fundo no modo light, exigindo ratio mÃ­nimo de 7:1 para texto normal e 4.5:1 para texto grande (WCAG AAA).
4. **Auditar contraste WCAG AAA (dark mode)** â€” Repetir a verificaÃ§Ã£o de contraste para o modo dark, garantindo que todos os pares atendem AAA.
5. **Validar hierarquia tipogrÃ¡fica** â€” Verificar que os tamanhos de fonte seguem uma escala consistente (type scale), que o line-height Ã© adequado para legibilidade e que os font-weight sÃ£o usados de forma hierÃ¡rquica.
6. **Verificar sistema de espaÃ§amento** â€” Confirmar que padding, margin e gap utilizam exclusivamente os tokens de espaÃ§amento definidos, sem valores arbitrÃ¡rios (magic numbers).
7. **Auditar consistÃªncia dos componentes** â€” Verificar que cada componente nas `componentSpecs` utiliza os tokens corretos e segue os padrÃµes de design system.
8. **Verificar comportamento responsivo** â€” Analisar breakpoints, fluid typography e layout adaptations para mobile, tablet e desktop.
9. **Categorizar issues** â€” Classificar cada problema como BLOCKER (quebra acessibilidade ou consistÃªncia visual), WARNING (inconsistÃªncia menor) ou INFO (melhoria sugerida).
10. **Calcular scores** â€” Computar score por dimensÃ£o (tokens, contraste, tipografia, espaÃ§amento, responsividade) e score geral ponderado.
11. **Gerar outputs** â€” Produzir `designReview` com detalhamento completo e `designScore` com os valores numÃ©ricos para o relatÃ³rio final.

