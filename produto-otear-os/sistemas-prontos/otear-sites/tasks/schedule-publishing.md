---
task: schedulePublishing()
responsavel: "Scheduler"
responsavel_type: Agente
atomic_layer: Atom
elicit: false

Entrada:
  - campo: content
    tipo: array
    origen: "adaptForSocial() ou writeLongForm() â€” conteÃºdo a publicar"
    obrigatorio: true
  - campo: channels
    tipo: array
    origen: "content-strategist â€” canais de publicaÃ§Ã£o"
    obrigatorio: true
  - campo: preferredDate
    tipo: string
    origen: "UsuÃ¡rio ou calendÃ¡rio â€” data preferida"
    obrigatorio: false

Saida:
  - campo: publishingSchedule
    tipo: file
    destino: "publishing-schedule.md, content-strategist"
    persistido: true
  - campo: queueStatus
    tipo: object
    destino: "content-strategist"
    persistido: true

Checklist:
  pre-conditions:
    - "[ ] ConteÃºdo pronto para publicaÃ§Ã£o"
    - "[ ] Canais definidos"
  post-conditions:
    - "[ ] PublicaÃ§Ãµes agendadas com horÃ¡rios Ã³timos"
    - "[ ] Fila de publicaÃ§Ã£o atualizada"
    - "[ ] CalendÃ¡rio sincronizado"
  acceptance-criteria:
    - blocker: true
      criteria: "PublicaÃ§Ãµes agendadas em horÃ¡rios Ã³timos por plataforma"
    - blocker: true
      criteria: "Sem conflitos de agendamento"
    - blocker: false
      criteria: "CadÃªncia semanal consistente"

Performance:
  duration_expected: "5-10 minutos"
  cost_estimated: "~0 (agendamento)"
  cacheable: false
  parallelizable: false

Error Handling:
  strategy: retry
  retry:
    max_attempts: 2
    delay: "exponential(base=5s, max=30s)"
  fallback: "Se horÃ¡rio Ã³timo indisponÃ­vel, agendar no prÃ³ximo slot disponÃ­vel"
  notification: "publishing-scheduler"

Metadata:
  version: "1.0.0"
  dependencies: []
  author: "content-factory-squad"
  created_at: "2026-02-24T00:00:00Z"
---

# Schedule Publishing

## Flow

```
1. Receber conteÃºdo pronto e canais alvo
2. Consultar horÃ¡rios Ã³timos por plataforma e timezone
3. Verificar conflitos no calendÃ¡rio existente
4. Agendar publicaÃ§Ãµes nos horÃ¡rios Ã³timos
5. Atualizar fila de publicaÃ§Ã£o por canal
6. Confirmar agendamento com resumo detalhado
7. Reportar status ao content-strategist
```

## Elicitation

- "Qual conteÃºdo deseja agendar?"
- "Em quais canais publicar? (blog, Instagram, LinkedIn, Twitter/X, TikTok)"
- "HÃ¡ data/horÃ¡rio preferido para publicaÃ§Ã£o?"
- "Qual o timezone do pÃºblico-alvo?"

