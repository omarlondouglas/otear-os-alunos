---
task: fullContentPipeline()
responsavel: "Strategist"
responsavel_type: Agente
atomic_layer: Page
elicit: true

Entrada:
  - campo: topic
    tipo: string
    origen: "UsuÃ¡rio â€” tema principal"
    obrigatorio: true
  - campo: channels
    tipo: array
    origen: "UsuÃ¡rio â€” canais alvo"
    obrigatorio: true
  - campo: format
    tipo: string
    origen: "UsuÃ¡rio â€” formato do conteÃºdo principal"
    obrigatorio: false

Saida:
  - campo: completePipeline
    tipo: object
    destino: "UsuÃ¡rio â€” resultado completo do pipeline"
    persistido: true
  - campo: contentCalendar
    tipo: file
    destino: "content-calendar.md"
    persistido: true
  - campo: longFormContent
    tipo: file
    destino: "long-form-content.md"
    persistido: true
  - campo: socialPosts
    tipo: array
    destino: "social-posts.json"
    persistido: true
  - campo: imageBriefs
    tipo: array
    destino: "image-briefs.json"
    persistido: true
  - campo: publishingSchedule
    tipo: file
    destino: "publishing-schedule.md"
    persistido: true

Checklist:
  pre-conditions:
    - "[ ] Tema definido"
    - "[ ] Ao menos 2 canais alvo"
    - "[ ] Acesso a plataformas de publicaÃ§Ã£o"
  post-conditions:
    - "[ ] ConteÃºdo longo escrito"
    - "[ ] AdaptaÃ§Ãµes sociais geradas"
    - "[ ] Briefs de imagem criados"
    - "[ ] PublicaÃ§Ãµes agendadas"
  acceptance-criteria:
    - blocker: true
      criteria: "Pipeline completo executado do planejamento ao agendamento"
    - blocker: true
      criteria: "ConteÃºdo adaptado para todos os canais solicitados"
    - blocker: false
      criteria: "VariaÃ§Ãµes A/B geradas"

Performance:
  duration_expected: "60-120 minutos"
  cost_estimated: "VariÃ¡vel conforme nÃºmero de canais e formatos"
  cacheable: false
  parallelizable: false

Error Handling:
  strategy: escalate
  retry:
    max_attempts: 2
    delay: "exponential(base=10s, max=60s)"
  fallback: "Se qualquer fase falhar, entregar resultado parcial e indicar fase pendente"
  notification: "content-strategist"

Metadata:
  version: "1.0.0"
  dependencies:
    - planContentCalendar()
    - writeLongForm()
    - adaptForSocial()
    - generateImageBrief()
    - schedulePublishing()
  author: "content-factory-squad"
  created_at: "2026-02-24T00:00:00Z"
---

# Full Content Pipeline

## Pipeline

```
Fase 1: Planejamento      â†’ @content-strategist    â†’ planContentCalendar()
Fase 2: Escrita            â†’ @long-form-writer      â†’ writeLongForm()
Fase 3: AdaptaÃ§Ã£o Social   â†’ @social-media-adapter  â†’ adaptForSocial()
Fase 4: Briefs de Imagem   â†’ @image-brief-generator â†’ generateImageBrief()
Fase 5: Agendamento        â†’ @publishing-scheduler  â†’ schedulePublishing()
```

## Elicitation

### Fase 1 â€” Tema e Canais
- "Qual o tema principal do conteÃºdo?"
- "Para quais canais deseja produzir? (blog, LinkedIn, Instagram, Twitter/X, TikTok)"
- "Qual o formato principal? (artigo, whitepaper, e-book)"
- "HÃ¡ keywords de SEO especÃ­ficas?"
- "Qual a data desejada para publicaÃ§Ã£o?"

### Fase 2 â€” Detalhamento
- "Qual a buyer persona alvo?"
- "HÃ¡ referÃªncias ou fontes obrigatÃ³rias?"
- "Qual o tom de voz desejado?"

### Fase 3 â€” AdaptaÃ§Ã£o
- "Alguma plataforma com prioridade para adaptaÃ§Ã£o?"
- "Deseja variaÃ§Ãµes A/B para teste?"

### Fase 5 â€” Agendamento
- "Qual o timezone do pÃºblico-alvo?"
- "HÃ¡ restriÃ§Ãµes de data ou horÃ¡rio?"

