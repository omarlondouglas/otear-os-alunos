---
task: reviewIntegrations()
responsavel: "Shield"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: whatsappIntegration
    tipo: file
    obrigatorio: false
    descricao: "MÃ³dulo de integraÃ§Ã£o com WhatsApp (source: integrateWhatsApp())"
  - nome: emailIntegration
    tipo: file
    obrigatorio: false
    descricao: "MÃ³dulo de integraÃ§Ã£o com email (source: integrateEmail())"
  - nome: connectionTestReport
    tipo: file
    obrigatorio: false
    descricao: "RelatÃ³rio de teste de conexÃ£o frontendâ†”backend (source: connectFrontendBackend())"
  - nome: apiClient
    tipo: file
    obrigatorio: false
    descricao: "Client TypeScript para comunicaÃ§Ã£o com a API (source: connectFrontendBackend())"

Saida:
  - nome: integrationReview
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio detalhado de revisÃ£o das integraÃ§Ãµes com issues e sugestÃµes (destination: lp-integrator para correÃ§Ãµes)"
  - nome: integrationScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de qualidade das integraÃ§Ãµes por dimensÃ£o (destination: produceFinalReport())"

Checklist:
  pre-conditions:
    - "[ ] Pelo menos uma integraÃ§Ã£o existe para revisÃ£o"
  post-conditions:
    - "[ ] Cada integraÃ§Ã£o ativa testada end-to-end"
    - "[ ] Entrega de mensagem WhatsApp verificada (se ativo)"
    - "[ ] Entrega de email verificada (se ativo)"
    - "[ ] SubmissÃ£o de formulÃ¡rio frontendâ†’backend verificada (se ativo)"
    - "[ ] Fallbacks de erro testados"
    - "[ ] VariÃ¡veis de ambiente documentadas e nÃ£o hardcoded"
    - "[ ] Issues categorizados como BLOCKER/WARNING/INFO"

Performance:
  duration_expected: "12 minutes"
  cacheable: false
  parallelizable: false
---

# reviewIntegrations()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  whatsappIntegration  â”‚â”€â”€?â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  integrationReview      â”‚
â”‚  (file, optional)     â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  reviewIntegrations  â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  emailIntegration     â”‚â”€â”€?â”€â”€>â”‚  @Shield             â”‚â”€â”€â”€â”€â”€â”€>â”‚  integrationScore       â”‚
â”‚  (file, optional)     â”‚       â”‚                      â”‚       â”‚  (object)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  connectionTestReport â”‚â”€â”€?â”€â”€>â”‚                      â”‚               â”‚
â”‚  (file, optional)     â”‚       â”‚                      â”‚               â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â–¼                  â–¼
â”‚  apiClient            â”‚â”€â”€?â”€â”€>                                â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  (file, optional)     â”‚                                      â”‚ lp-integratorâ”‚   â”‚ produceFinal â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â”‚ (para fixes) â”‚   â”‚ Report()     â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

  â”€â”€?â”€â”€>  = condicional (sÃ³ se a integraÃ§Ã£o estiver ativa)
```

## DescriÃ§Ã£o

A task `reviewIntegrations()` Ã© **CONDICIONAL** â€” sÃ³ Ã© executada quando pelo menos uma integraÃ§Ã£o estÃ¡ ativa (WhatsApp, email ou conexÃ£o frontendâ†”backend). O agente **Shield** realiza uma **auditoria de qualidade e confiabilidade** de todas as integraÃ§Ãµes ativas, testando cada uma end-to-end e verificando que os mecanismos de fallback funcionam corretamente.

O review Ã© adaptativo: analisa apenas as integraÃ§Ãµes que foram efetivamente implementadas, sem penalizar o score por integraÃ§Ãµes que nÃ£o fazem parte do escopo. Cada integraÃ§Ã£o ativa Ã© testada em seu fluxo completo, incluindo cenÃ¡rios de sucesso e de falha.

## Passos

1. **Detectar integraÃ§Ãµes ativas** â€” Verificar quais inputs foram fornecidos para determinar quais integraÃ§Ãµes existem: WhatsApp (`whatsappIntegration`), email (`emailIntegration`), frontendâ†”backend (`connectionTestReport` + `apiClient`).
2. **Revisar integraÃ§Ã£o WhatsApp (se ativa)** â€” Verificar:
   - Webhook `POST /webhook/whatsapp` responde corretamente
   - Templates de mensagem (welcome, follow-up) estÃ£o configurados
   - Envio de mensagem funciona end-to-end
   - Fallback para banco de dados opera quando Evolution API indisponÃ­vel
   - VariÃ¡veis de ambiente (`EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE_NAME`) documentadas e nÃ£o hardcoded
3. **Revisar integraÃ§Ã£o email (se ativa)** â€” Verificar:
   - Email de notificaÃ§Ã£o ao admin Ã© enviado ao capturar lead
   - Email de confirmaÃ§Ã£o ao lead Ã© enviado corretamente
   - Templates HTML renderizam adequadamente
   - Fallback para banco de dados opera quando SMTP falha
   - VariÃ¡veis de ambiente (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`) documentadas e nÃ£o hardcoded
4. **Revisar conexÃ£o frontendâ†”backend (se ativa)** â€” Verificar:
   - API client TypeScript estÃ¡ tipado e funcional
   - CORS configurado restritivamente
   - SubmissÃ£o de formulÃ¡rio funciona end-to-end
   - Tratamento de erros apresenta mensagens amigÃ¡veis
   - Fallback localStorage opera quando backend indisponÃ­vel
   - VariÃ¡veis de ambiente (`NEXT_PUBLIC_API_URL`) configuradas
5. **Testar cenÃ¡rios de falha** â€” Para cada integraÃ§Ã£o, simular indisponibilidade do serviÃ§o externo e verificar que o fallback opera conforme esperado.
6. **Verificar documentaÃ§Ã£o de env vars** â€” Confirmar que todas as variÃ¡veis de ambiente estÃ£o documentadas em `.env.example` e que nenhuma estÃ¡ hardcoded no cÃ³digo.
7. **Categorizar issues** â€” Classificar cada problema como BLOCKER (integraÃ§Ã£o quebrada ou insegura), WARNING (fallback incompleto ou documentaÃ§Ã£o ausente) ou INFO (otimizaÃ§Ã£o sugerida).
8. **Calcular scores** â€” Computar score por integraÃ§Ã£o ativa e score geral ponderado (apenas integraÃ§Ãµes ativas contam).
9. **Gerar outputs** â€” Produzir `integrationReview` com detalhamento completo e `integrationScore` com os valores numÃ©ricos para o relatÃ³rio final.

