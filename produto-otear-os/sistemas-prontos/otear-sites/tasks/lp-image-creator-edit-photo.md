---
task: editClientPhoto()
responsavel: "Lens"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: clientPhotos
    tipo: array
    obrigatorio: true
    descricao: "Fotos do cliente no R2 (URLs de photos/) com usage (hero, about, profile)"
  - nome: designTokens
    tipo: file
    obrigatorio: true
    descricao: "Design tokens da LP (cores, estilo visual) para harmonizar a foto"
  - nome: sectionLayouts
    tipo: file
    obrigatorio: true
    descricao: "Layouts das seÃ§Ãµes para saber dimensÃµes e posicionamento"

Saida:
  - nome: editedPhotos
    tipo: array
    obrigatorio: true
    descricao: "Fotos editadas com URLs no R2 (em images/) prontas para o frontend"

Checklist:
  pre-conditions:
    - "[ ] Fotos do cliente uploaded no R2 (photos/)"
    - "[ ] Design tokens definidos (cores, estilo)"
    - "[ ] MCP nano-banana-pro disponÃ­vel"
  post-conditions:
    - "[ ] Fotos editadas para combinar com o design system"
    - "[ ] Fundo removido ou substituÃ­do conforme design"
    - "[ ] Cores e tonalidade harmonizadas com a paleta da LP"
    - "[ ] DimensÃµes adequadas para cada seÃ§Ã£o (hero, about, etc.)"
    - "[ ] Fotos editadas salvas no R2 em images/ (nÃ£o photos/)"
    - "[ ] assets-manifest.json atualizado com fotos editadas"

Performance:
  duration_expected: "3-8 minutes (depende do nÃºmero de fotos)"
  cacheable: false
  parallelizable: true
---

# editClientPhoto()

## DescriÃ§Ã£o

Pega as fotos do cliente (uploaded no R2 em `photos/`), usa o MCP nano-banana-pro (Google Gemini) para editar cada foto de forma que fique harmonizada com o design system da landing page, e salva o resultado em `images/`.

## Tipos de EdiÃ§Ã£o por Uso

### Hero Photo
```
- Remover fundo original
- Aplicar fundo com gradiente/cor do design system
- Ajustar tonalidade para combinar com a paleta
- Redimensionar para 1920x1080
- Adicionar efeitos sutis (shadow, glow) conforme estilo visual
```

### About / Profile Photo
```
- Remover fundo
- Aplicar fundo neutro do design system (--color-background ou --color-surface)
- Crop circular ou com border-radius do DS
- Redimensionar para 600x600
- Ajustar warmth/contrast para combinar com a paleta
```

### Testimonial Photo
```
- Remover fundo
- Crop circular
- Redimensionar para 200x200
- Ajustar para ficar consistente com outras fotos
```

## Passos

1. **Listar fotos** â€” Buscar todas as fotos do cliente no R2 (`photos/`).
2. **Ler design system** â€” Extrair cores primÃ¡rias, estilo visual, backgrounds.
3. **Para cada foto**:
   a. **Download** â€” Baixar foto do R2.
   b. **Analisar uso** â€” Hero? About? Testimonial? (tag no metadata).
   c. **Gerar prompt de ediÃ§Ã£o** â€” Baseado no design system:
      ```
      "Remove the background and replace with a gradient from {primary} to {secondary}.
       Adjust the photo warmth and contrast to match a {style} design aesthetic.
       Maintain the person's natural appearance. Output at {width}x{height}."
      ```
   d. **Editar via nano-banana-pro** â€” MCP call com a foto + prompt.
   e. **Otimizar** â€” Converter para WebP, comprimir.
   f. **Upload** â€” Salvar em R2 `images/client-photo-{usage}.webp`.
4. **Atualizar manifesto** â€” Adicionar fotos editadas ao `assets-manifest.json`.

## Prompts de EdiÃ§Ã£o por Estilo Visual

### Minimalista
```
Remove the background. Replace with a clean, solid {background-color} background.
Keep the subject sharp and well-lit. Minimal shadows. Professional look.
```

### Bold / Vibrant
```
Remove the background. Replace with a bold gradient from {primary} to {secondary}.
Add a subtle shadow behind the subject. Vibrant but professional.
```

### Glassmorphism
```
Remove the background. Replace with a frosted glass effect using colors {primary-light}
and {secondary-light}. Add soft light blur and subtle reflections.
```

### Dark / Elegant
```
Remove the background. Replace with a deep dark {background-dark} background.
Add dramatic lighting from the side. Elegant, high-contrast professional look.
```

## MCP nano-banana-pro â€” EdiÃ§Ã£o de Imagem

```
Tool: nano-banana-pro
Action: edit_image
Input:
  - image: {foto do cliente (URL ou base64)}
  - prompt: {prompt de ediÃ§Ã£o baseado no DS}
  - reference: {screenshot/preview do design system}
Output:
  - edited_image: {imagem editada}
```

## Fluxo no Pipeline

```
Cliente envia foto
  â†’ Upload R2: photos/photo-hero-maria.jpg (original)
  â†’ Lens lÃª design tokens (cores, estilo)
  â†’ nano-banana-pro edita a foto
  â†’ Upload R2: images/client-photo-hero.webp (editada)
  â†’ Frontend usa images/client-photo-hero.webp
```

## Anti-patterns
- NÃƒO distorÃ§a o rosto ou corpo da pessoa â€” ediÃ§Ã£o sÃ³ no fundo e tonalidade
- NÃƒO use filtros exagerados â€” a foto precisa parecer profissional
- NÃƒO ignore o design system â€” a foto DEVE combinar com as cores e estilo
- NÃƒO esqueÃ§a de otimizar (WebP) â€” fotos originais podem ser muito grandes
- NÃƒO sobrescreva a original â€” photos/ mantÃ©m a original, images/ tem a editada

