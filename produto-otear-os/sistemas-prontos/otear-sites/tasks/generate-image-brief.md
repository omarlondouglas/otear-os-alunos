---
task: generateImageBrief()
responsavel: "ImageBriefer"
responsavel_type: Agente
atomic_layer: Organism
elicit: false

Entrada:
  - campo: content
    tipo: file
    origen: "writeLongForm() ou adaptForSocial() â€” conteÃºdo para criar visuais"
    obrigatorio: true
  - campo: platform
    tipo: string
    origen: "social-media-adapter â€” plataforma alvo"
    obrigatorio: false
  - campo: style
    tipo: string
    origen: "UsuÃ¡rio ou brand guidelines â€” estilo visual"
    obrigatorio: false

Saida:
  - campo: imageBriefs
    tipo: array
    destino: "designer/AI tool, publishing-scheduler"
    persistido: true
  - campo: aiPrompts
    tipo: array
    destino: "nano-banana ou dalle3 â€” prompts para geraÃ§Ã£o AI"
    persistido: true

Checklist:
  pre-conditions:
    - "[ ] ConteÃºdo disponÃ­vel"
    - "[ ] Plataforma alvo definida"
  post-conditions:
    - "[ ] Brief de imagem gerado com especificaÃ§Ãµes completas"
    - "[ ] Prompts de AI incluÃ­dos"
    - "[ ] DimensÃµes corretas para plataforma"
  acceptance-criteria:
    - blocker: true
      criteria: "Brief com dimensÃµes, composiÃ§Ã£o e estilo definidos"
    - blocker: true
      criteria: "Prompt de AI generation funcional"
    - blocker: false
      criteria: "VariaÃ§Ãµes de estilo propostas"

Performance:
  duration_expected: "5-15 minutos"
  cost_estimated: "~0 (criaÃ§Ã£o de brief)"
  cacheable: false
  parallelizable: true

Error Handling:
  strategy: retry
  retry:
    max_attempts: 2
    delay: "exponential(base=5s, max=30s)"
  fallback: "Se brand guidelines indisponÃ­veis, usar estilo genÃ©rico profissional"
  notification: "image-brief-generator"

Metadata:
  version: "1.0.0"
  dependencies: []
  author: "content-factory-squad"
  created_at: "2026-02-24T00:00:00Z"
---

# Generate Image Brief

## Flow

```
1. Receber conteÃºdo e contexto da plataforma
2. Definir dimensÃµes corretas para a plataforma
3. Especificar composiÃ§Ã£o e layout (rule of thirds, focal point)
4. Definir paleta de cores alinhada Ã  marca
5. Especificar tipografia e texto overlay
6. Gerar prompts otimizados para AI image generation
7. Incluir instruÃ§Ãµes detalhadas para designer humano
8. Enviar briefs para produÃ§Ã£o e scheduler
```

## Elicitation

- "Qual o conteÃºdo para o qual criar visuais?"
- "Para qual plataforma? (Instagram, LinkedIn, Twitter/X, Blog, YouTube)"
- "HÃ¡ estilo visual preferido? (flat, 3D, photorealistic, illustration)"
- "HÃ¡ brand guidelines ou paleta de cores definida?"

