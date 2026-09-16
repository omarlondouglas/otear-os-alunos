---
task: notify()
responsavel: "Nexus"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: event
    tipo: string
    obrigatorio: true
    descricao: "Tipo de evento: started, progress, qa_passed, deployed, completed, error"
  - nome: payload
    tipo: object
    obrigatorio: true
    descricao: "Dados do evento (job_id, client, message, urls, etc.)"

Saida:
  - nome: notificationSent
    tipo: boolean
    obrigatorio: true
    descricao: "ConfirmaÃ§Ã£o de que a notificaÃ§Ã£o foi enviada"

Checklist:
  pre-conditions:
    - "[ ] Webhook de notificaÃ§Ã£o configurado (Slack/Discord/WhatsApp)"
  post-conditions:
    - "[ ] NotificaÃ§Ã£o enviada com sucesso"
    - "[ ] Log da notificaÃ§Ã£o salvo"

Performance:
  duration_expected: "5 seconds"
  cacheable: false
  parallelizable: true
---

# notify()

## DescriÃ§Ã£o

Envia notificaÃ§Ãµes de status do pipeline via webhook para Slack, Discord ou WhatsApp.

## Tipos de NotificaÃ§Ã£o

### Job Iniciado
```json
{
  "event": "started",
  "job_id": "job_abc123",
  "client": "Studio Maria",
  "message": "ðŸš€ Criando LP para Studio Maria...",
  "estimated_time": "45 min"
}
```

### Progresso
```json
{
  "event": "progress",
  "job_id": "job_abc123",
  "step": "frontend-build",
  "progress": "7/12",
  "message": "â³ Copy + design prontos, buildando frontend..."
}
```

### QA Aprovada
```json
{
  "event": "qa_passed",
  "job_id": "job_abc123",
  "score": 9.2,
  "message": "âœ… QA aprovada (9.2/10). Deployando na Vercel..."
}
```

### Deploy ConcluÃ­do
```json
{
  "event": "deployed",
  "job_id": "job_abc123",
  "urls": {
    "vercel": "https://studio-maria-lp.vercel.app",
    "custom": null
  },
  "message": "ðŸŽ‰ LP live! https://studio-maria-lp.vercel.app"
}
```

### Entrega Completa
```json
{
  "event": "completed",
  "job_id": "job_abc123",
  "urls": {
    "live": "https://studio-maria-lp.vercel.app",
    "github": "https://github.com/org/studio-maria-lp",
    "release": "https://github.com/org/studio-maria-lp/releases/tag/v1.0.0"
  },
  "qa_score": 9.2,
  "duration": "42 min",
  "message": "ðŸŽ‰ LP Studio Maria entregue!\nðŸŒ Live: studio-maria-lp.vercel.app\nðŸ“¦ GitHub: org/studio-maria-lp\nâ­ QA: 9.2/10"
}
```

### Erro
```json
{
  "event": "error",
  "job_id": "job_abc123",
  "step": "image-generation",
  "error": "MCP nano-banana-pro timeout",
  "message": "ðŸš¨ Falha em image-generation: MCP timeout. Retentando..."
}
```

## Canais de NotificaÃ§Ã£o

```python
NOTIFICATION_CHANNELS = {
    "slack": {
        "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
        "enabled": True
    },
    "discord": {
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
        "enabled": False
    },
    "whatsapp": {
        "api_url": os.getenv("EVOLUTION_API_URL"),
        "instance": os.getenv("EVOLUTION_INSTANCE"),
        "number": os.getenv("NOTIFY_WHATSAPP_NUMBER"),
        "enabled": False
    }
}
```

