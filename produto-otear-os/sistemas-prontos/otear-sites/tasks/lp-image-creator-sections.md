---
task: generateSectionImages()
responsavel: "Lens"
responsavel_type: Agente
atomic_layer: Atom

Entrada:
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Paleta de cores, tipografia e tokens visuais definidos (source: defineDesignTokens())"
  - nome: sectionLayouts
    tipo: file
    obrigatorio: true
    descricao: "Layouts das seÃ§Ãµes com indicaÃ§Ã£o de quais precisam de imagens (source: designSections())"
  - nome: heroImageVariants
    tipo: array<file>
    obrigatorio: true
    descricao: "Variantes de imagem do hero para manter coerÃªncia visual (source: generateHeroImage())"

Saida:
  - nome: sectionImages
    tipo: array<file>
    obrigatorio: true
    descricao: "Imagens geradas para cada seÃ§Ã£o que necessita de visual â€” benefits, testimonials, solution-demo (destination: lp-frontend-dev)"
  - nome: imageGenerationLog
    tipo: file
    obrigatorio: true
    descricao: "Log dos prompts, ferramentas e decisÃµes de geraÃ§Ã£o por seÃ§Ã£o (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] heroImageVariants existem com variante recomendada identificada (para coerÃªncia de estilo)"
    - "[ ] sectionLayouts identificam quais seÃ§Ãµes precisam de imagens"
    - "[ ] designTokens existe com paleta completa"
  post-conditions:
    - "[ ] Imagens geradas para seÃ§Ãµes de benefits, testimonials e solution-demo"
    - "[ ] CoerÃªncia visual mantida com a variante hero selecionada"
    - "[ ] Prompts documentados no imageGenerationLog"
    - "[ ] Imagens dimensionadas corretamente para os layouts definidos"
    - "[ ] Estilo visual consistente entre todas as seÃ§Ãµes"

Performance:
  duration_expected: "20 minutes"
  cacheable: false
  parallelizable: false
---

# generateSectionImages()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ designTokens     â”‚â”€â”€â”€â”
â”‚ (file)           â”‚   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                       â”œâ”€â”€â”€â”€>â”‚                         â”‚â”€â”€â”€â”€>â”‚ sectionImages    â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚  generateSectionImages  â”‚     â”‚ (array<file>)    â”‚
â”‚ sectionLayouts   â”‚â”€â”€â”€â”¤     â”‚  @Lens                  â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ (file)           â”‚   â”‚     â”‚                         â”‚â”€â”€â”€â”€>â”‚ imageGeneration  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”‚  Tools:                 â”‚     â”‚ Log (file)       â”‚
                       â”‚     â”‚  nano-banana-pro        â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚  dalle3                 â”‚            â”‚
â”‚ heroImageVariantsâ”‚â”€â”€â”€â”˜     â”‚  flux                   â”‚            â–¼
â”‚ (array<file>)    â”‚         â”‚  fal-video              â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚ lp-frontend-dev  â”‚
       â–²                                                     â”‚ lp-reviewer      â”‚
       â”‚ (coerÃªncia visual)                                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `generateSectionImages()` cria os assets visuais para todas as seÃ§Ãµes da landing page que necessitam de imagens â€” tipicamente benefits, testimonials e solution-demo. O agente **Lens** utiliza a variante hero selecionada como referÃªncia de estilo para garantir coerÃªncia visual ao longo de toda a pÃ¡gina.

Diferente da geraÃ§Ã£o do hero (que produz variantes para escolha), esta task gera imagens definitivas para cada seÃ§Ã£o, respeitando os layouts definidos pelo designer e mantendo consistÃªncia de paleta, estilo e tom visual. O log documenta as decisÃµes por seÃ§Ã£o para rastreabilidade.

## Passos

1. **Analisar hero selecionado** â€” Identificar a variante hero recomendada e extrair o estilo visual dominante (paleta, textura, composiÃ§Ã£o, realismo vs. ilustraÃ§Ã£o).
2. **Mapear seÃ§Ãµes que precisam de imagens** â€” Ler sectionLayouts para identificar quais seÃ§Ãµes requerem assets visuais e seus requisitos dimensionais.
3. **Definir estilo-guia** â€” Criar um prompt-base que capture o estilo visual do hero para garantir coerÃªncia em todas as imagens de seÃ§Ã£o.
4. **Gerar imagens de benefits** â€” Criar visuais para a seÃ§Ã£o de benefÃ­cios, tipicamente Ã­cones estilizados ou ilustraÃ§Ãµes que comuniquem cada benefÃ­cio.
5. **Gerar imagens de testimonials** â€” Criar visuais de apoio para a seÃ§Ã£o de depoimentos â€” avatars, backgrounds ou elementos decorativos.
6. **Gerar imagens de solution-demo** â€” Criar visuais demonstrativos do produto/soluÃ§Ã£o em aÃ§Ã£o, como mockups, screenshots estilizados ou diagramas.
7. **Verificar coerÃªncia visual** â€” Comparar todas as imagens geradas com o hero e entre si, ajustando prompts e regenerando se necessÃ¡rio.
8. **Dimensionar para layouts** â€” Garantir que as imagens atendem Ã s dimensÃµes especificadas nos sectionLayouts.
9. **Documentar no log** â€” Registrar prompts, ferramentas utilizadas e decisÃµes de estilo para cada seÃ§Ã£o no imageGenerationLog.
10. **Validar post-conditions** â€” Confirmar coerÃªncia, completude e documentaÃ§Ã£o antes de entregar os artefatos.

