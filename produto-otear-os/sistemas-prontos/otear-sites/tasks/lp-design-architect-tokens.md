---
task: defineDesignTokens()
responsavel: "Prism"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: dsSelection
    tipo: file
    obrigatorio: true
    descricao: "Documento de seleÃ§Ã£o do design system com escolha e configuraÃ§Ã£o base (source: selectDesignSystem())"
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com USP, mercado-alvo, tom/voz e identidade visual (source: discoverProduct())"
  - nome: userPreferences
    tipo: object
    obrigatorio: false
    descricao: "PreferÃªncias do usuÃ¡rio para cores, tipografia e estilo visual (source: elicitRequirements())"

Saida:
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Sistema completo de design tokens â€” cores, tipografia, espaÃ§amento, sombras, breakpoints (destination: createAtomicComponents() + lp-frontend-dev + lp-image-creator)"
  - nome: contrastReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de verificaÃ§Ã£o de contraste WCAG AAA para todos os pares foreground/background (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] dsSelection existe com design system base definido"
    - "[ ] productBrief existe com identidade visual e tom/voz"
  post-conditions:
    - "[ ] Color primitives definidas (paleta completa com shades 50-950)"
    - "[ ] Semantic tokens para light mode definidos (background, foreground, primary, secondary, accent, muted, destructive, border, ring)"
    - "[ ] Semantic tokens para dark mode definidos (todas as mesmas categorias)"
    - "[ ] Escala tipogrÃ¡fica definida (font-family, sizes, weights, line-heights, letter-spacing)"
    - "[ ] Sistema de espaÃ§amento definido (grid de 4px: 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24)"
    - "[ ] Border-radius tokens definidos (none, sm, md, lg, xl, 2xl, full)"
    - "[ ] Shadow tokens definidos (sm, md, lg, xl, 2xl, inner)"
    - "[ ] Breakpoints responsivos definidos (sm, md, lg, xl, 2xl)"
    - "[ ] Contraste WCAG AAA verificado â€” ratio 7:1 para texto normal, 4.5:1 para texto grande em TODOS os pares foreground/background"
    - "[ ] contrastReport gerado com status PASS/FAIL para cada par"

Performance:
  duration_expected: "10 minutes"
  cacheable: true
  parallelizable: false
---

# defineDesignTokens()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  dsSelection     â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  designTokens       â”‚
â”‚  (file)          â”‚       â”‚                      â”‚       â”‚  (file)             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  defineDesignTokens  â”‚       â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  productBrief    â”‚â”€â”€â”€â”€â”€â”€>â”‚  @Prism              â”‚       â”‚  â”‚ colors        â”‚  â”‚
â”‚  (file)          â”‚       â”‚                      â”‚       â”‚  â”‚ typography    â”‚  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â”‚  â”‚ spacing       â”‚  â”‚
â”‚  userPreferences â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚       â”‚  â”‚ borders       â”‚  â”‚
â”‚  (object)?       â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  â”‚ shadows       â”‚  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”‚                      â”‚  â”‚ breakpoints   â”‚  â”‚
                                   â”‚                      â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
                                   â”‚                      â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
                                   â”‚                      â”‚  contrastReport     â”‚
                                   â–¼                      â”‚  (file)             â”‚
                           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â”‚  WCAG AAA        â”‚                   â”‚
                           â”‚  Contrast Check  â”‚                   â–¼
                           â”‚  7:1 / 4.5:1     â”‚           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜           â”‚  createAtomic...()  â”‚
                                                          â”‚  lp-frontend-dev    â”‚
                                                          â”‚  lp-image-creator   â”‚
                                                          â”‚  lp-reviewer        â”‚
                                                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `defineDesignTokens()` Ã© o **alicerce do sistema visual** da landing page. O agente **Prism** constrÃ³i um sistema completo de design tokens sobre o design system selecionado em `selectDesignSystem()`, definindo cada primitiva visual que serÃ¡ usada por componentes, layouts e assets grÃ¡ficos.

Os design tokens sÃ£o a "linguagem visual" compartilhada entre design e cÃ³digo. Eles garantem que cores, tipografia, espaÃ§amento e outros atributos visuais sejam consistentes em toda a landing page, tanto no light mode quanto no dark mode. Cada token Ã© nomeado semanticamente (ex: `--color-primary`, `--text-heading`, `--space-lg`) para que mudanÃ§as de tema possam ser feitas alterando apenas os valores dos tokens, sem tocar nos componentes.

Um requisito crÃ­tico desta task Ã© a **verificaÃ§Ã£o de contraste WCAG AAA**. Todos os pares foreground/background devem atingir ratio mÃ­nimo de 7:1 para texto normal e 4.5:1 para texto grande, garantindo acessibilidade mÃ¡xima. O `contrastReport` documenta o resultado de cada verificaÃ§Ã£o para auditoria pelo reviewer.

## Passos

1. **Carregar dsSelection** â€” Ler o design system selecionado e sua configuraÃ§Ã£o base para entender as convenÃ§Ãµes de tokens do DS.
2. **Extrair identidade visual** â€” Do `productBrief` e `userPreferences`, extrair: cores da marca, tipografia desejada, estilo visual (minimalista, bold, etc.), preferÃªncias explÃ­citas.
3. **Definir color primitives** â€” Criar a paleta completa com shades de 50 a 950 para cada cor base (primary, secondary, accent, neutral, success, warning, error).
4. **Criar semantic tokens â€” light mode** â€” Mapear os primitives para tokens semÃ¢nticos: background, foreground, card, popover, primary, secondary, muted, accent, destructive, border, input, ring.
5. **Criar semantic tokens â€” dark mode** â€” Definir a versÃ£o dark de cada token semÃ¢ntico, garantindo que a identidade visual se mantenha com luminosidade invertida.
6. **Definir escala tipogrÃ¡fica** â€” Estabelecer font-family (heading + body), escala de tamanhos (xs a 6xl), pesos (light a black), line-heights e letter-spacing.
7. **Definir sistema de espaÃ§amento** â€” Criar a escala baseada no grid de 4px com valores de 0 a 24 unidades (0px a 96px).
8. **Definir border-radius e shadows** â€” Criar tokens para arredondamento (none a full) e sombras (sm a 2xl + inner).
9. **Definir breakpoints** â€” Estabelecer os pontos de quebra responsivos: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px).
10. **Verificar contraste WCAG AAA** â€” Para cada par foreground/background nos tokens semÃ¢nticos (light e dark), calcular o ratio de contraste e verificar: >=7:1 para texto normal, >=4.5:1 para texto grande.
11. **Gerar contrastReport** â€” Compilar o relatÃ³rio de contraste com status PASS/FAIL, ratio calculado e recomendaÃ§Ã£o de correÃ§Ã£o para pares que falham.
12. **Ajustar tokens com falha** â€” Se algum par nÃ£o atingir o ratio mÃ­nimo, ajustar os valores dos tokens e re-verificar atÃ© todos passarem.
13. **Compilar designTokens** â€” Gerar o arquivo final com todos os tokens organizados por categoria, prontos para consumo pelos componentes e pelo frontend.

