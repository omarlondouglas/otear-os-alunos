---
task: integrateEmail()
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
  - nome: emailIntegration
    tipo: file
    obrigatorio: true
    descricao: "MÃ³dulo de integraÃ§Ã£o com serviÃ§o de email via SMTP (destination: lp-reviewer)"
  - nome: emailTemplates
    tipo: array<file>
    obrigatorio: true
    descricao: "Templates de email criados â€” admin-notification e lead-confirmation (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] leadsApi existe e foi gerado por createLeadEndpoints()"
    - "[ ] scopeDefinition contÃ©m email=true"
    - "[ ] SMTP ou email MCP disponÃ­vel e configurado"
  post-conditions:
    - "[ ] NotificaÃ§Ã£o por email ao admin ao receber novo lead"
    - "[ ] Email de confirmaÃ§Ã£o enviado ao lead"
    - "[ ] Templates de email criados (admin-notification, lead-confirmation)"
    - "[ ] VariÃ¡veis de ambiente documentadas (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL)"
    - "[ ] Fallback para log em banco de dados quando SMTP falhar"

Performance:
  duration_expected: "12 minutes"
  cacheable: false
  parallelizable: false
---

# integrateEmail()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  leadsApi             â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  emailIntegration       â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  integrateEmail      â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  scopeDefinition      â”‚â”€â”€â”€â”€â”€â”€>â”‚  @Bridge             â”‚â”€â”€â”€â”€â”€â”€>â”‚  emailTemplates         â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (array<file>)          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                                        â”‚
                                                                        â–¼
                                                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                               â”‚  lp-reviewer            â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `integrateEmail()` Ã© **CONDICIONAL** â€” sÃ³ Ã© executada quando `scopeDefinition` contÃ©m o flag `email=true`. O agente **Bridge** conecta o sistema de captura de leads a um serviÃ§o de email via SMTP, permitindo notificaÃ§Ãµes automÃ¡ticas por email tanto para o administrador quanto para o lead.

A integraÃ§Ã£o cria dois fluxos de email: uma notificaÃ§Ã£o ao admin quando um novo lead Ã© capturado (contendo os dados do lead), e um email de confirmaÃ§Ã£o para o lead (agradecendo o contato e informando prÃ³ximos passos). Templates HTML sÃ£o criados para ambos os cenÃ¡rios, e um fallback para banco de dados garante que nenhuma notificaÃ§Ã£o seja perdida em caso de falha do SMTP.

## Passos

1. **Verificar prÃ©-condiÃ§Ãµes** â€” Confirmar que `leadsApi` existe, que `scopeDefinition` tem `email=true` e que o serviÃ§o SMTP estÃ¡ acessÃ­vel.
2. **Configurar variÃ¡veis de ambiente** â€” Documentar e validar as variÃ¡veis `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` e `FROM_EMAIL` no arquivo `.env`.
3. **Criar mÃ³dulo de integraÃ§Ã£o** â€” Implementar o client SMTP com mÃ©todos para envio de email, suporte a templates HTML e tratamento de erros de conexÃ£o.
4. **Criar template admin-notification** â€” Desenvolver template HTML para notificaÃ§Ã£o ao admin contendo: dados do lead, timestamp, origem e link para painel admin (se disponÃ­vel).
5. **Criar template lead-confirmation** â€” Desenvolver template HTML para confirmaÃ§Ã£o ao lead contendo: agradecimento personalizado, resumo do que foi enviado e expectativa de retorno.
6. **Implementar fallback para banco de dados** â€” Adicionar lÃ³gica que detecta falha no envio SMTP e registra os emails pendentes no banco de dados para reenvio posterior.
7. **Conectar ao leadsApi** â€” Integrar o fluxo de captura de leads com o disparo automÃ¡tico dos dois emails (admin e lead).
8. **Testar integraÃ§Ã£o end-to-end** â€” Validar o fluxo completo: lead capturado â†’ emails enviados â†’ fallback funcional quando SMTP indisponÃ­vel.
9. **Gerar outputs** â€” Disponibilizar `emailIntegration` e `emailTemplates` para o reviewer.

