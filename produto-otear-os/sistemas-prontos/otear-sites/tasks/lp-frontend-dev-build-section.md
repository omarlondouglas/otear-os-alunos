---
task: buildSection()
responsavel: "Pixel"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: sectionName
    tipo: string
    obrigatorio: true
    descricao: "Nome da seÃ§Ã£o a ser construÃ­da â€” hero, benefits, testimonials, etc. (source: orchestrator)"
  - nome: sectionCopy
    tipo: file
    obrigatorio: true
    descricao: "Copy da seÃ§Ã£o com textos, headlines e CTAs (source: writeSectionCopy())"
  - nome: sectionLayouts
    tipo: file
    obrigatorio: true
    descricao: "Layout da seÃ§Ã£o com grid, espaÃ§amento e hierarquia visual (source: designSections())"
  - nome: sectionImages
    tipo: array<file>
    obrigatorio: false
    descricao: "Imagens da seÃ§Ã£o se aplicÃ¡vel (source: generateSectionImages())"
  - nome: implementedDesignSystem
    tipo: file
    obrigatorio: true
    descricao: "Design system implementado com componentes atÃ´micos disponÃ­veis (source: implementDesignSystem())"

Saida:
  - nome: sectionComponent
    tipo: file
    obrigatorio: true
    descricao: "Componente React da seÃ§Ã£o completo e funcional (destination: assemblePage())"
  - nome: sectionA11yReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de acessibilidade da seÃ§Ã£o â€” ARIA, keyboard, semÃ¢ntica (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] implementedDesignSystem existe e componentes atÃ´micos estÃ£o disponÃ­veis"
    - "[ ] sectionCopy existe para a seÃ§Ã£o-alvo"
    - "[ ] sectionLayouts existe com layout definido para a seÃ§Ã£o-alvo"
  post-conditions:
    - "[ ] SeÃ§Ã£o renderiza corretamente em light e dark mode"
    - "[ ] HTML semÃ¢ntico utilizado (section, article, heading levels corretos)"
    - "[ ] ARIA labels presentes em elementos interativos"
    - "[ ] SeÃ§Ã£o navegÃ¡vel por teclado (Tab, Enter, Escape)"
    - "[ ] Responsivo de 320px (mobile) a 1440px+ (desktop)"
    - "[ ] Alt text em todas as imagens"
    - "[ ] RelatÃ³rio de a11y gerado"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: true
---

# buildSection()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ sectionName       â”‚â”€â”€â”€â”
â”‚ (string)          â”‚   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”‚
â”‚ sectionCopy       â”‚â”€â”€â”€â”¤
â”‚ (file)            â”‚   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€>â”‚                  â”‚â”€â”€â”€â”€>â”‚ sectionComponent   â”‚
â”‚ sectionLayouts    â”‚â”€â”€â”€â”¤     â”‚  buildSection    â”‚     â”‚ (file)             â”‚
â”‚ (file)            â”‚   â”‚     â”‚  @Pixel          â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”‚     â”‚                  â”‚â”€â”€â”€â”€>â”‚ sectionA11yReport  â”‚
â”‚ sectionImages?    â”‚â”€â”€â”€â”¤     â”‚  [ITERATIVA]     â”‚     â”‚ (file)             â”‚
â”‚ (array<file>)     â”‚   â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”‚                                      â”‚
â”‚ implemented       â”‚â”€â”€â”€â”˜                                      â–¼
â”‚ DesignSystem      â”‚                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ (file)            â”‚                               â”‚ assemblePage()     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                               â”‚ lp-reviewer        â”‚
                                                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Nota: Chamada uma vez POR SEÃ‡ÃƒO â€” hero, benefits, testimonials, etc.
```

## DescriÃ§Ã£o

A task `buildSection()` constrÃ³i um componente React individual para uma seÃ§Ã£o especÃ­fica da landing page. O agente **Pixel** recebe o nome da seÃ§Ã£o, seu copy, layout, imagens (se aplicÃ¡vel) e o design system implementado, produzindo um componente completo, acessÃ­vel e responsivo.

Esta Ã© uma task **iterativa** â€” Ã© chamada uma vez por seÃ§Ã£o (hero, benefits, solution-demo, testimonials, FAQ, CTA final, footer, etc.). Cada execuÃ§Ã£o produz um componente independente pronto para ser montado na pÃ¡gina final. A paralelizaÃ§Ã£o Ã© possÃ­vel: seÃ§Ãµes sem dependÃªncia entre si podem ser construÃ­das simultaneamente.

## Passos

1. **Identificar seÃ§Ã£o-alvo** â€” Ler `sectionName` e localizar o layout e copy correspondentes nos inputs.
2. **Selecionar componentes do design system** â€” Mapear quais Ã¡tomos, molÃ©culas e organismos do implementedDesignSystem serÃ£o utilizados na seÃ§Ã£o.
3. **Criar estrutura do componente** â€” Definir o componente React com TypeScript, props tipadas e estrutura semÃ¢ntica (section, headings, article).
4. **Implementar layout** â€” Aplicar o grid, espaÃ§amento e hierarquia visual definidos no sectionLayouts usando Tailwind CSS.
5. **Inserir copy** â€” Integrar headline, body text, CTAs e demais textos do sectionCopy nos elementos corretos.
6. **Integrar imagens** â€” Se sectionImages existirem, posicionar imagens com `next/image`, alt text descritivo e loading otimizado (lazy/eager conforme posiÃ§Ã£o).
7. **Implementar responsividade** â€” Garantir comportamento correto em breakpoints: mobile (320px), tablet (768px), desktop (1024px), large (1440px+).
8. **Adicionar acessibilidade** â€” Inserir ARIA labels em interativos, garantir heading hierarchy, landmark roles, focus indicators visÃ­veis.
9. **Testar light/dark** â€” Verificar renderizaÃ§Ã£o correta em ambos os temas, incluindo imagens e backgrounds.
10. **Gerar relatÃ³rio a11y** â€” Documentar verificaÃ§Ãµes realizadas (semÃ¢ntica, ARIA, keyboard, contraste) no sectionA11yReport.

