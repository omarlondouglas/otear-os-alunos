---
task: implementDesignSystem()
responsavel: "Pixel"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Tokens de design â€” cores, tipografia, espaÃ§amento, sombras, bordas (source: defineDesignTokens())"
  - nome: componentSpecs
    tipo: file
    obrigatorio: true
    descricao: "EspecificaÃ§Ãµes dos componentes atÃ´micos â€” props, estados, variantes (source: createAtomicComponents())"
  - nome: frontendProject
    tipo: file
    obrigatorio: true
    descricao: "Projeto Next.js inicializado com infraestrutura base (source: setupFrontendProject())"

Saida:
  - nome: implementedDesignSystem
    tipo: file
    obrigatorio: true
    descricao: "Design system completo implementado com todos os componentes atÃ´micos (destination: buildSection())"
  - nome: tokensCssFile
    tipo: file
    obrigatorio: true
    descricao: "Arquivo CSS com custom properties para todos os tokens em light/dark (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] frontendProject existe e roda sem erros"
    - "[ ] designTokens existe com paleta completa (light + dark)"
    - "[ ] componentSpecs existe com especificaÃ§Ãµes de todos os Ã¡tomos, molÃ©culas e organismos"
  post-conditions:
    - "[ ] CSS custom properties criadas para todos os tokens (light e dark)"
    - "[ ] Todos os componentes atÃ´micos implementados (atoms, molecules, organisms)"
    - "[ ] Tailwind theme estendido com tokens customizados"
    - "[ ] Dark mode toggle funcional e persistente"
    - "[ ] Contraste verificado no browser (ratio mÃ­nimo WCAG AA)"
    - "[ ] Componentes renderizam corretamente em ambos os temas"

Performance:
  duration_expected: "25 minutes"
  cacheable: false
  parallelizable: false
---

# implementDesignSystem()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ designTokens     â”‚â”€â”€â”€â”
â”‚ (file)           â”‚   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                       â”œâ”€â”€â”€â”€>â”‚                         â”‚â”€â”€â”€â”€>â”‚ implementedDesignSystem â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚  implementDesignSystem  â”‚     â”‚ (file)                 â”‚
â”‚ componentSpecs   â”‚â”€â”€â”€â”¤     â”‚  @Pixel                 â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ (file)           â”‚   â”‚     â”‚                         â”‚â”€â”€â”€â”€>â”‚ tokensCssFile          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚ (file)                 â”‚
                       â”‚                                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚                                            â”‚
â”‚ frontendProject  â”‚â”€â”€â”€â”˜                                            â–¼
â”‚ (file)           â”‚                                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                     â”‚ buildSection()     â”‚
                                                         â”‚ lp-reviewer        â”‚
                                                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `implementDesignSystem()` transforma os tokens de design abstratos e as especificaÃ§Ãµes de componentes em cÃ³digo funcional dentro do projeto Next.js. O agente **Pixel** cria CSS custom properties para todos os tokens (com variantes light/dark), implementa cada componente atÃ´mico (Ã¡tomos, molÃ©culas e organismos) usando shadcn/ui como base, e estende o tema do Tailwind CSS.

Esta Ã© a task que materializa o design system no cÃ³digo â€” o resultado Ã© a fundaÃ§Ã£o visual sobre a qual todas as seÃ§Ãµes da landing page serÃ£o construÃ­das. A verificaÃ§Ã£o de contraste e a funcionalidade do dark mode sÃ£o validadas antes da entrega.

## Passos

1. **Mapear tokens para CSS custom properties** â€” Converter os designTokens em variÃ¡veis CSS (`--color-primary`, `--font-heading`, `--spacing-section`, etc.) para os temas light e dark.
2. **Criar arquivo de tokens CSS** â€” Gerar o arquivo `globals.css` (ou `tokens.css`) com `:root` e `[data-theme="dark"]` (ou `.dark`) contendo todas as variÃ¡veis.
3. **Estender Tailwind theme** â€” Configurar `tailwind.config.ts` para referenciar as CSS custom properties, criando classes utilitÃ¡rias que respeitem os tokens.
4. **Implementar Ã¡tomos** â€” Criar componentes base: Button, Input, Badge, Typography (H1-H6, P, Span), Icon, Link, Image.
5. **Implementar molÃ©culas** â€” Criar componentes compostos: Card, FormField, NavItem, TestimonialCard, BenefitCard, CTABlock.
6. **Implementar organismos** â€” Criar componentes complexos: Header/Navbar, Footer, HeroSection shell, SectionWrapper, ContactForm.
7. **Configurar dark mode** â€” Garantir que next-themes estÃ¡ funcional, o toggle persiste a preferÃªncia, e todos os componentes alternam corretamente.
8. **Verificar contraste** â€” Testar combinaÃ§Ãµes de cor primÃ¡rias em ambos os temas usando ferramentas de browser para WCAG AA compliance (ratio >= 4.5:1 para texto, >= 3:1 para elementos grandes).
9. **Testar componentes** â€” Renderizar cada componente isoladamente verificando estados (default, hover, focus, disabled, active) em light e dark.
10. **Validar post-conditions** â€” Confirmar que todos os componentes estÃ£o implementados, o dark mode funciona e o contraste estÃ¡ adequado.

