---
task: integrateWhatsApp()
responsavel: "Bridge"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: leadsApi
    tipo: file
    obrigatorio: true
    descricao: "Endpoints de captura de leads implementados (source: createLeadEndpoints())"
  - nome: scopeDefinition
    tipo: file
    obrigatorio: true
    descricao: "DefiniÃ§Ã£o de escopo com flags condicionais (source: defineScope())"

Saida:
  - nome: whatsappIntegration
    tipo: file
    obrigatorio: true
    descricao: "MÃ³dulo de integraÃ§Ã£o com WhatsApp via Evolution API (destination: lp-reviewer)"
  - nome: webhookConfig
    tipo: object
    obrigatorio: true
    descricao: "ConfiguraÃ§Ã£o do webhook para recebimento de mensagens WhatsApp (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] leadsApi existe e foi gerado por createLeadEndpoints()"
    - "[ ] scopeDefinition contÃ©m whatsapp=true"
    - "[ ] InstÃ¢ncia do Evolution API disponÃ­vel e acessÃ­vel"
  post-conditions:
    - "[ ] Webhook endpoint POST /webhook/whatsapp criado e funcional"
    - "[ ] Templates de mensagem configurados (welcome, follow-up)"
    - "[ ] VariÃ¡veis de ambiente documentadas (EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME)"
    - "[ ] Fallback para log em banco de dados quando Evolution API estiver offline"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# integrateWhatsApp()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  leadsApi             â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  whatsappIntegration    â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  integrateWhatsApp   â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  scopeDefinition      â”‚â”€â”€â”€â”€â”€â”€>â”‚  @Bridge             â”‚â”€â”€â”€â”€â”€â”€>â”‚  webhookConfig          â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (object)               â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                                        â”‚
                                                                        â–¼
                                                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                               â”‚  lp-reviewer            â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `integrateWhatsApp()` Ã© **CONDICIONAL** â€” sÃ³ Ã© executada quando `scopeDefinition` contÃ©m o flag `whatsapp=true`. O agente **Bridge** conecta o sistema de captura de leads Ã  API do WhatsApp via Evolution API, permitindo notificaÃ§Ãµes automÃ¡ticas e interaÃ§Ã£o com leads pelo WhatsApp.

A integraÃ§Ã£o cria um webhook para receber mensagens, configura templates de mensagem (boas-vindas e follow-up) e implementa um mecanismo de fallback que registra as mensagens no banco de dados quando a Evolution API estiver indisponÃ­vel, garantindo que nenhum lead seja perdido.

## Passos

1. **Verificar prÃ©-condiÃ§Ãµes** â€” Confirmar que `leadsApi` existe, que `scopeDefinition` tem `whatsapp=true` e que a instÃ¢ncia do Evolution API estÃ¡ acessÃ­vel.
2. **Configurar variÃ¡veis de ambiente** â€” Documentar e validar as variÃ¡veis `EVOLUTION_API_URL`, `EVOLUTION_API_KEY` e `EVOLUTION_INSTANCE_NAME` no arquivo `.env`.
3. **Criar mÃ³dulo de integraÃ§Ã£o** â€” Implementar o client para comunicaÃ§Ã£o com a Evolution API, incluindo mÃ©todos para envio de mensagens e gerenciamento de instÃ¢ncia.
4. **Implementar webhook endpoint** â€” Criar endpoint `POST /webhook/whatsapp` para recebimento de mensagens e eventos do WhatsApp.
5. **Configurar templates de mensagem** â€” Criar templates de `welcome` (enviado ao primeiro contato do lead) e `follow-up` (enviado apÃ³s perÃ­odo configurÃ¡vel sem resposta).
6. **Implementar fallback para banco de dados** â€” Adicionar lÃ³gica que detecta indisponibilidade da Evolution API e registra as mensagens pendentes no banco de dados para reenvio posterior.
7. **Conectar ao leadsApi** â€” Integrar o fluxo de captura de leads com o envio automÃ¡tico da mensagem de boas-vindas via WhatsApp.
8. **Testar integraÃ§Ã£o end-to-end** â€” Validar o fluxo completo: lead capturado â†’ mensagem enviada â†’ webhook recebe resposta â†’ fallback funcional.
9. **Gerar outputs** â€” Disponibilizar `whatsappIntegration` e `webhookConfig` para o reviewer.

