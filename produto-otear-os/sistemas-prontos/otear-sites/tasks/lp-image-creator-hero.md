---
task: generateHeroImage()
responsavel: "Lens"
responsavel_type: Agente
atomic_layer: Atom

Entrada:
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Paleta de cores, tipografia e tokens visuais definidos (source: defineDesignTokens())"
  - nome: sectionCopy
    tipo: file
    obrigatorio: true
    descricao: "Copy da seÃ§Ã£o hero para contexto visual â€” headline, subheadline, CTA (source: writeSectionCopy('hero'))"
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com USP, mercado-alvo e posicionamento (source: discoverProduct())"

Saida:
  - nome: heroImageVariants
    tipo: array<file>
    obrigatorio: true
    descricao: "3-4 variantes de imagem hero geradas com diferentes ferramentas (destination: lp-frontend-dev)"
  - nome: imageGenerationLog
    tipo: file
    obrigatorio: true
    descricao: "Log detalhado dos prompts utilizados, ferramentas empregadas e racional de seleÃ§Ã£o (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] designTokens existe e contÃ©m paleta de cores completa"
    - "[ ] sectionCopy do hero existe com headline, subheadline e CTA"
    - "[ ] productBrief existe com USP e mercado-alvo definidos"
  post-conditions:
    - "[ ] 3-4 variantes de imagem hero geradas usando ferramentas diferentes (nano-banana-pro, dalle3, flux)"
    - "[ ] Todos os prompts documentados no imageGenerationLog"
    - "[ ] Variante recomendada identificada com racional de escolha"
    - "[ ] Imagens alinhadas com a paleta de cores dos designTokens"
    - "[ ] Imagens coerentes com o tom e posicionamento do productBrief"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# generateHeroImage()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ designTokens â”‚â”€â”€â”€â”
â”‚ (file)       â”‚   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                   â”œâ”€â”€â”€â”€>â”‚                    â”‚â”€â”€â”€â”€>â”‚ heroImageVariants   â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚  generateHeroImage â”‚     â”‚ (array<file>)       â”‚
â”‚ sectionCopy  â”‚â”€â”€â”€â”¤     â”‚  @Lens             â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ (file)       â”‚   â”‚     â”‚                    â”‚â”€â”€â”€â”€>â”‚ imageGenerationLog  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”‚  Tools:            â”‚     â”‚ (file)              â”‚
                   â”‚     â”‚  nano-banana-pro   â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚  dalle3            â”‚            â”‚
â”‚ productBrief â”‚â”€â”€â”€â”˜     â”‚  flux              â”‚            â–¼
â”‚ (file)       â”‚         â”‚  fal-video         â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚ lp-frontend-dev     â”‚
                                                    â”‚ lp-reviewer         â”‚
                                                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `generateHeroImage()` Ã© responsÃ¡vel por criar mÃºltiplas variantes visuais para a seÃ§Ã£o hero da landing page. O agente **Lens** utiliza diversas ferramentas de geraÃ§Ã£o de imagem (nano-banana-pro, dalle3, flux, fal-video) para produzir 3-4 opÃ§Ãµes distintas, cada uma explorando uma abordagem visual diferente enquanto mantÃ©m coerÃªncia com os tokens de design e o posicionamento do produto.

O objetivo Ã© fornecer ao time opÃ§Ãµes reais de escolha â€” nÃ£o variaÃ§Ãµes mÃ­nimas, mas abordagens visuais genuinamente distintas que comuniquem a proposta de valor do hero. O log de geraÃ§Ã£o documenta cada prompt e ferramenta utilizada, permitindo rastreabilidade e iteraÃ§Ã£o futura.

## Passos

1. **Analisar inputs** â€” Ler os designTokens (paleta, tipografia), o sectionCopy do hero (headline, subheadline, CTA) e o productBrief (USP, tom, mercado-alvo) para extrair contexto visual.
2. **Definir direÃ§Ã£o visual** â€” Estabelecer 3-4 direÃ§Ãµes visuais distintas baseadas no posicionamento do produto (ex: minimalista, lifestyle, abstrato, product-shot).
3. **Construir prompts** â€” Para cada direÃ§Ã£o visual, elaborar um prompt detalhado incorporando paleta de cores, tom da marca e contexto do hero copy.
4. **Gerar com nano-banana-pro** â€” Criar a primeira variante usando Gemini via nano-banana-pro, priorizando aderÃªncia Ã  paleta.
5. **Gerar com dalle3** â€” Criar a segunda variante usando DALL-E 3 via dalle3, explorando fotorrealismo ou estilo editorial.
6. **Gerar com flux** â€” Criar a terceira variante usando Flux, aproveitando sua aderÃªncia a prompt e tipografia.
7. **Gerar variante adicional (opcional)** â€” Se necessÃ¡rio, usar fal-video (imagen4, ideogram, recraft) para uma quarta variante com abordagem diferenciada.
8. **Avaliar e recomendar** â€” Comparar todas as variantes contra os designTokens e o tom do productBrief, identificar a variante recomendada com racional documentado.
9. **Documentar no log** â€” Registrar todos os prompts, ferramentas, parÃ¢metros e o racional de recomendaÃ§Ã£o no imageGenerationLog.
10. **Validar post-conditions** â€” Confirmar que todas as condiÃ§Ãµes de saÃ­da foram atendidas antes de entregar os artefatos.

