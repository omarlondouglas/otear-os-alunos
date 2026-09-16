---
task: planContentCalendar()
responsavel: "Strategist"
responsavel_type: Agente
atomic_layer: Molecule
elicit: false

Entrada:
  - campo: period
    tipo: string
    origen: "UsuÃ¡rio â€” mensal/trimestral/anual"
    obrigatorio: true
  - campo: channels
    tipo: array
    origen: "UsuÃ¡rio â€” lista de canais alvo"
    obrigatorio: false
  - campo: personas
    tipo: array
    origen: "UsuÃ¡rio â€” buyer personas"
    obrigatorio: false
  - campo: brandGuidelines
    tipo: object
    origen: "Projeto â€” tom de voz, visual identity"
    obrigatorio: false

Saida:
  - campo: contentCalendar
    tipo: file
    destino: "content-calendar.md, long-form-writer, social-media-adapter, publishing-scheduler"
    persistido: true
  - campo: themeMap
    tipo: object
    destino: "long-form-writer, social-media-adapter"
    persistido: true

Checklist:
  pre-conditions:
    - "[ ] PerÃ­odo definido"
    - "[ ] Ao menos um canal alvo identificado"
  post-conditions:
    - "[ ] CalendÃ¡rio editorial gerado com temas e datas"
    - "[ ] Temas mapeados ao buyer journey"
    - "[ ] Formatos definidos para cada canal"
  acceptance-criteria:
    - blocker: true
      criteria: "CalendÃ¡rio com pelo menos 4 semanas de conteÃºdo planejado"
    - blocker: true
      criteria: "Cada tema alinhado com fase do buyer journey"
    - blocker: false
      criteria: "Mix de formatos diversificado"

Performance:
  duration_expected: "15-30 minutos"
  cost_estimated: "~0 (planejamento estratÃ©gico)"
  cacheable: false
  parallelizable: false

Error Handling:
  strategy: retry
  retry:
    max_attempts: 2
    delay: "exponential(base=5s, max=30s)"
  fallback: "Se dados de persona indisponÃ­veis, usar persona genÃ©rica baseada no segmento"
  notification: "content-strategist"

Metadata:
  version: "1.0.0"
  dependencies: []
  author: "content-factory-squad"
  created_at: "2026-02-24T00:00:00Z"
---

# Plan Content Calendar

## Flow

```
1. Definir perÃ­odo e objetivos de marketing
2. Mapear buyer personas e etapas do funil
3. Identificar pilares de conteÃºdo (3-5 temas principais)
4. Distribuir temas por semana do perÃ­odo
5. Definir formatos por canal (blog, social, email, vÃ­deo)
6. Atribuir prioridades e datas de publicaÃ§Ã£o
7. Gerar calendÃ¡rio editorial em content-calendar.md
8. Enviar calendÃ¡rio para writers e scheduler
```

## Elicitation

- "Qual o perÃ­odo do calendÃ¡rio? (mensal, trimestral, anual)"
- "Quais canais serÃ£o utilizados? (blog, Instagram, LinkedIn, Twitter/X, TikTok, email)"
- "Quais sÃ£o as buyer personas do pÃºblico-alvo?"
- "HÃ¡ brand guidelines ou tom de voz definido?"

