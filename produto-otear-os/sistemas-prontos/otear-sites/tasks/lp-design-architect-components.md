---
task: createAtomicComponents()
responsavel: "Prism"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Sistema completo de design tokens â€” cores, tipografia, espaÃ§amento, sombras, breakpoints (source: defineDesignTokens())"
  - nome: dsSelection
    tipo: file
    obrigatorio: true
    descricao: "Documento de seleÃ§Ã£o do design system com escolha e configuraÃ§Ã£o base (source: selectDesignSystem())"

Saida:
  - nome: componentSpecs
    tipo: file
    obrigatorio: true
    descricao: "EspecificaÃ§Ãµes completas de todos os componentes atÃ´micos â€” props, variantes, estados e acessibilidade (destination: lp-frontend-dev)"
  - nome: componentHierarchy
    tipo: file
    obrigatorio: true
    descricao: "Hierarquia de composiÃ§Ã£o dos componentes â€” quais Atoms compÃµem Molecules, quais Molecules compÃµem Organisms (destination: designSections())"

Checklist:
  pre-conditions:
    - "[ ] designTokens existe com todas as categorias de tokens definidas (cores, tipografia, espaÃ§amento, borders, shadows, breakpoints)"
    - "[ ] dsSelection existe com design system base e configuraÃ§Ã£o"
  post-conditions:
    - "[ ] Atoms especificados: Button, Input, Label, Icon, Badge, Avatar â€” cada um com props, variantes e estados"
    - "[ ] Molecules especificadas: FormField, SearchBar, Card, NavItem, TestimonialCard â€” cada uma com composiÃ§Ã£o de Atoms"
    - "[ ] Organisms especificados: Header, HeroSection, BenefitsGrid, TestimonialCarousel, Footer â€” cada um com composiÃ§Ã£o de Molecules"
    - "[ ] Cada componente tem props tipadas documentadas"
    - "[ ] Cada componente tem variantes listadas (size, color, variant)"
    - "[ ] Cada componente tem estados documentados (default, hover, focus, active, disabled, loading)"
    - "[ ] Requisitos de acessibilidade documentados por componente (ARIA roles, labels, keyboard navigation)"
    - "[ ] componentHierarchy mapeia a Ã¡rvore de composiÃ§Ã£o completa"

Performance:
  duration_expected: "12 minutes"
  cacheable: true
  parallelizable: false
---

# createAtomicComponents()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  designTokens    â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  componentSpecs     â”‚
â”‚  (file)          â”‚       â”‚  createAtomic        â”‚       â”‚  (file)             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚       â”‚  Components          â”‚       â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ colors     â”‚  â”‚       â”‚  @Prism              â”‚       â”‚  â”‚ Atoms         â”‚  â”‚
â”‚  â”‚ typography â”‚  â”‚       â”‚                      â”‚       â”‚  â”‚ Molecules     â”‚  â”‚
â”‚  â”‚ spacing    â”‚  â”‚       â”‚                      â”‚       â”‚  â”‚ Organisms     â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤               â”‚                      â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  dsSelection     â”‚â”€â”€â”€â”€â”€â”€>        â”‚                      â”‚  componentHierarchy â”‚
â”‚  (file)          â”‚               â”‚                      â”‚  (file)             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”‚                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚                              â”‚
                                   â–¼                              â–¼
                           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                           â”‚  Atomic      â”‚               â”‚  lp-frontend-dev    â”‚
                           â”‚  Design      â”‚               â”‚  designSections()   â”‚
                           â”‚  Methodology â”‚               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `createAtomicComponents()` aplica a **metodologia Atomic Design** para especificar todos os componentes visuais da landing page em trÃªs nÃ­veis hierÃ¡rquicos: Atoms, Molecules e Organisms. O agente **Prism** usa os design tokens e o design system selecionado como base para definir cada componente com precisÃ£o suficiente para implementaÃ§Ã£o direta pelo frontend.

**Atoms** sÃ£o os blocos elementares (Button, Input, Label, Icon, Badge, Avatar) â€” componentes indivisÃ­veis que nÃ£o contÃªm outros componentes. **Molecules** sÃ£o composiÃ§Ãµes de Atoms que formam unidades funcionais (FormField = Label + Input, Card = imagem + texto + Badge, TestimonialCard = Avatar + texto + rating). **Organisms** sÃ£o composiÃ§Ãµes de Molecules que formam seÃ§Ãµes completas (Header = NavItem[] + Button, HeroSection = heading + subheading + CTA + imagem).

Cada componente Ã© especificado com: props tipadas, variantes (size, color, style), estados interativos (default, hover, focus, active, disabled, loading) e requisitos de acessibilidade (ARIA roles, labels, keyboard navigation). Esta especificaÃ§Ã£o serve como contrato entre design e desenvolvimento.

## Passos

1. **Carregar designTokens e dsSelection** â€” Entender os tokens disponÃ­veis e as convenÃ§Ãµes do design system base para garantir que os componentes sejam nativamente compatÃ­veis.
2. **Inventariar componentes necessÃ¡rios** â€” A partir das seÃ§Ãµes planejadas da landing page, listar todos os componentes UI necessÃ¡rios e classificÃ¡-los em Atoms, Molecules e Organisms.
3. **Especificar Atoms** â€” Para cada Atom (Button, Input, Label, Icon, Badge, Avatar):
   - Definir props tipadas (ex: Button: variant, size, disabled, loading, icon, children)
   - Listar variantes (ex: Button: default, secondary, outline, ghost, link, destructive)
   - Documentar estados (default, hover, focus, active, disabled, loading)
   - Mapear tokens utilizados (ex: Button default â†’ bg: primary, text: primary-foreground)
   - Definir requisitos de acessibilidade (ex: Button â†’ role="button", aria-disabled, keyboard: Enter/Space)
4. **Especificar Molecules** â€” Para cada Molecule (FormField, SearchBar, Card, NavItem, TestimonialCard):
   - Definir composiÃ§Ã£o de Atoms (quais Atoms sÃ£o usados e como)
   - Definir props prÃ³prias (que combinam ou estendem props dos Atoms)
   - Documentar variantes e estados compostos
   - Definir acessibilidade composta (ex: FormField â†’ label associado via htmlFor/id)
5. **Especificar Organisms** â€” Para cada Organism (Header, HeroSection, BenefitsGrid, TestimonialCarousel, Footer):
   - Definir composiÃ§Ã£o de Molecules e Atoms
   - Definir layout interno (flex, grid, posicionamento)
   - Documentar comportamento responsivo (como o Organism se adapta em mobile/tablet/desktop)
   - Definir acessibilidade estrutural (landmarks, headings, navigation)
6. **Construir componentHierarchy** â€” Mapear a Ã¡rvore de composiÃ§Ã£o completa mostrando as dependÃªncias entre todos os nÃ­veis (quais Atoms compÃµem quais Molecules, quais Molecules compÃµem quais Organisms).
7. **Validar cobertura** â€” Verificar que todos os componentes necessÃ¡rios para as seÃ§Ãµes da landing page estÃ£o especificados e que nÃ£o hÃ¡ lacunas na hierarquia.
8. **Validar acessibilidade** â€” Revisar que cada componente tem requisitos de acessibilidade documentados e que a hierarquia de headings e landmarks faz sentido no contexto da pÃ¡gina completa.
9. **Compilar componentSpecs** â€” Gerar o documento final com todas as especificaÃ§Ãµes organizadas por nÃ­vel atÃ´mico (Atoms -> Molecules -> Organisms).
10. **Validar contra post-conditions** â€” Verificar que todos os componentes listados nas post-conditions estÃ£o presentes com props, variantes, estados e acessibilidade documentados.

