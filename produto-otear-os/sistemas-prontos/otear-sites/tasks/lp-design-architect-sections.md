---
task: designSections()
responsavel: "Prism"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: componentHierarchy
    tipo: file
    obrigatorio: true
    descricao: "Hierarquia de composiÃ§Ã£o dos componentes atÃ´micos â€” Atoms, Molecules, Organisms (source: createAtomicComponents())"
  - nome: allSectionsCopy
    tipo: array<file>
    obrigatorio: true
    descricao: "Copies finais de todas as seÃ§Ãµes da landing page (source: writeSectionCopy() iterations)"
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Sistema completo de design tokens (source: defineDesignTokens())"

Saida:
  - nome: sectionLayouts
    tipo: file
    obrigatorio: true
    descricao: "Layouts detalhados de cada seÃ§Ã£o com wireframes desktop + mobile e mapeamento de componentes (destination: lp-frontend-dev + lp-image-creator)"
  - nome: responsiveSpecs
    tipo: file
    obrigatorio: true
    descricao: "EspecificaÃ§Ãµes de comportamento responsivo por seÃ§Ã£o e por breakpoint (destination: lp-frontend-dev)"

Checklist:
  pre-conditions:
    - "[ ] componentHierarchy existe com Atoms, Molecules e Organisms definidos"
    - "[ ] allSectionsCopy contÃ©m copy de todas as seÃ§Ãµes planejadas"
    - "[ ] designTokens existe com tokens de espaÃ§amento, tipografia e breakpoints"
  post-conditions:
    - "[ ] Cada seÃ§Ã£o possui wireframe layout para desktop (>=1024px)"
    - "[ ] Cada seÃ§Ã£o possui wireframe layout para mobile (<768px)"
    - "[ ] Cada seÃ§Ã£o possui mapeamento de quais componentes (da componentHierarchy) sÃ£o usados e onde"
    - "[ ] Notas de variante light/dark incluÃ­das para cada seÃ§Ã£o"
    - "[ ] Comportamento responsivo definido por breakpoint (sm, md, lg, xl, 2xl) para cada seÃ§Ã£o"
    - "[ ] EspaÃ§amento entre seÃ§Ãµes definido e consistente"
    - "[ ] Hierarquia visual (Z-pattern ou F-pattern) documentada"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# designSections()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  componentHier.  â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  sectionLayouts     â”‚
â”‚  (file)          â”‚       â”‚                      â”‚       â”‚  (file)             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚       â”‚                      â”‚       â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ Atoms      â”‚  â”‚       â”‚  designSections      â”‚       â”‚  â”‚ Hero layout   â”‚  â”‚
â”‚  â”‚ Molecules  â”‚  â”‚       â”‚  @Prism              â”‚       â”‚  â”‚ Problem layoutâ”‚  â”‚
â”‚  â”‚ Organisms  â”‚  â”‚       â”‚                      â”‚       â”‚  â”‚ Benefits ...  â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚       â”‚                      â”‚       â”‚  â”‚ [desktop+mob] â”‚  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚  allSectionsCopy â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  (array<file>)   â”‚       â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  responsiveSpecs    â”‚
â”‚  [hero, problem, â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  (file)             â”‚
â”‚   benefits, ...] â”‚                                      â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤                                      â”‚  â”‚ sm  (640px)   â”‚  â”‚
â”‚  designTokens    â”‚â”€â”€â”€â”€â”€â”€>                               â”‚  â”‚ md  (768px)   â”‚  â”‚
â”‚  (file)          â”‚                                      â”‚  â”‚ lg  (1024px)  â”‚  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â”‚  â”‚ xl  (1280px)  â”‚  â”‚
                                                          â”‚  â”‚ 2xl (1536px)  â”‚  â”‚
                                                          â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
                                                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                                  â”‚
                                                                  â–¼
                                                          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                          â”‚  lp-frontend-dev    â”‚
                                                          â”‚  lp-image-creator   â”‚
                                                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `designSections()` Ã© a **montagem arquitetural** da landing page. O agente **Prism** combina os componentes atÃ´micos definidos, o copy de cada seÃ§Ã£o e os design tokens para produzir layouts detalhados de cada seÃ§Ã£o, tanto para desktop quanto para mobile, junto com especificaÃ§Ãµes completas de comportamento responsivo.

Esta task transforma o que atÃ© aqui eram peÃ§as isoladas (componentes, copy, tokens) em uma **composiÃ§Ã£o visual integrada**. Cada seÃ§Ã£o da landing page recebe um wireframe que define: posicionamento dos componentes, grid utilizado, espaÃ§amentos internos e externos, hierarquia visual (Z-pattern para hero, F-pattern para conteÃºdo denso), e como o copy se encaixa nos componentes.

As especificaÃ§Ãµes responsivas definem como cada seÃ§Ã£o se adapta em cada breakpoint â€” quais componentes re-organizam, quais escondem/mostram, como a tipografia escala e como o grid se transforma. Estas specs sÃ£o o insumo direto para o frontend developer implementar os layouts com precisÃ£o pixel-perfect.

## Passos

1. **Carregar inputs** â€” Ler `componentHierarchy`, `allSectionsCopy` e `designTokens` para ter a visÃ£o completa dos materiais disponÃ­veis.
2. **Definir ordem das seÃ§Ãµes** â€” Estabelecer a sequÃªncia final das seÃ§Ãµes na landing page (hero -> problem-agitation -> benefits -> features -> social-proof -> CTA -> FAQ -> footer) e validar contra o copy disponÃ­vel.
3. **Projetar layout do Hero** â€” Definir wireframe desktop e mobile do Hero: posiÃ§Ã£o do headline, subheadline, CTA, imagem/ilustraÃ§Ã£o hero, e background treatment. Aplicar Z-pattern para guiar o olhar.
4. **Projetar layout de Problem-Agitation** â€” Definir wireframe com Ãªnfase nos pain points, usando componentes Card ou lista para estruturar os problemas. Considerar uso de Ã­cones e espaÃ§o negativo para impacto emocional.
5. **Projetar layout de Benefits/Features** â€” Definir wireframe com grid de benefÃ­cios (BenefitsGrid), usando Cards com Ã­cones, headlines curtas e descriÃ§Ãµes. Definir variaÃ§Ã£o 2-col vs 3-col por breakpoint.
6. **Projetar layout de Social Proof** â€” Definir wireframe com TestimonialCarousel ou grid de TestimonialCards, posiÃ§Ã£o de logos de clientes, mÃ©tricas e badges de confianÃ§a.
7. **Projetar layout de CTA** â€” Definir wireframe do CTA section com urgÃªncia visual, formulÃ¡rio (se aplicÃ¡vel), botÃ£o principal e microcopy de suporte.
8. **Projetar layout de FAQ** â€” Definir wireframe com componente Accordion, espaÃ§amento entre itens, e posiÃ§Ã£o de CTA secundÃ¡rio ao final.
9. **Projetar layout do Footer** â€” Definir wireframe com links de navegaÃ§Ã£o, informaÃ§Ãµes legais, redes sociais e marca.
10. **Mapear componentes por seÃ§Ã£o** â€” Para cada seÃ§Ã£o, listar exatamente quais componentes da `componentHierarchy` sÃ£o usados, com quais variantes e quais props.
11. **Definir notas light/dark** â€” Para cada seÃ§Ã£o, documentar como o layout se adapta entre light e dark mode (background colors, image treatments, shadow adjustments).
12. **Definir espaÃ§amento inter-seÃ§Ãµes** â€” Estabelecer o ritmo vertical da pÃ¡gina com espaÃ§amento consistente entre seÃ§Ãµes (usando tokens de spacing).
13. **Especificar comportamento responsivo** â€” Para cada seÃ§Ã£o e cada breakpoint (sm, md, lg, xl, 2xl), documentar: mudanÃ§as de grid, reordenamento de elementos, ajustes tipogrÃ¡ficos, elementos que escondem/mostram.
14. **Compilar sectionLayouts e responsiveSpecs** â€” Gerar os arquivos finais e validar contra as post-conditions.

