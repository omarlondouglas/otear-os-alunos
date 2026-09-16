---
task: specBackendInterface()
responsavel: "Prism"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: sectionLayouts
    tipo: file
    obrigatorio: true
    descricao: "Layouts detalhados de cada seÃ§Ã£o com wireframes e mapeamento de componentes (source: designSections())"
  - nome: scopeDefinition
    tipo: file
    obrigatorio: true
    descricao: "DefiniÃ§Ã£o de escopo do projeto com flag backend=true/false e requisitos funcionais (source: defineScope())"

Saida:
  - nome: backendSpec
    tipo: file
    obrigatorio: true
    descricao: "EspecificaÃ§Ã£o completa da interface backend â€” endpoints REST, payloads, validaÃ§Ãµes e integraÃ§Ãµes (destination: lp-backend-dev)"
  - nome: dataModel
    tipo: file
    obrigatorio: true
    descricao: "Modelo de dados para leads, submissÃµes de formulÃ¡rio e conteÃºdo dinÃ¢mico (destination: lp-backend-dev)"

Checklist:
  pre-conditions:
    - "[ ] sectionLayouts existe com layouts de todas as seÃ§Ãµes"
    - "[ ] scopeDefinition existe com backend=true"
    - "[ ] SeÃ§Ãµes com formulÃ¡rios identificadas nos layouts"
  post-conditions:
    - "[ ] Todos os campos de formulÃ¡rio especificados com tipos, validaÃ§Ãµes e constraints"
    - "[ ] Endpoints REST definidos com method, path, payload e response schema"
    - "[ ] Modelo de dados de leads especificado (campos, tipos, required, unique)"
    - "[ ] Requisitos de admin panel documentados (CRUD de conteÃºdo, visualizaÃ§Ã£o de leads)"
    - "[ ] ValidaÃ§Ãµes server-side mapeadas para cada campo de formulÃ¡rio"
    - "[ ] Rate limiting e proteÃ§Ã£o anti-spam especificados"
    - "[ ] IntegraÃ§Ãµes externas listadas (email service, CRM, analytics)"

Performance:
  duration_expected: "8 minutes"
  cacheable: true
  parallelizable: false
---

# specBackendInterface()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  sectionLayouts  â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  backendSpec        â”‚
â”‚  (file)          â”‚       â”‚                      â”‚       â”‚  (file)             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚       â”‚  specBackend         â”‚       â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ forms      â”‚  â”‚       â”‚  Interface           â”‚       â”‚  â”‚ endpoints     â”‚  â”‚
â”‚  â”‚ CTAs       â”‚  â”‚       â”‚  @Prism              â”‚       â”‚  â”‚ validations   â”‚  â”‚
â”‚  â”‚ dynamic    â”‚  â”‚       â”‚                      â”‚       â”‚  â”‚ integrations  â”‚  â”‚
â”‚  â”‚ content    â”‚  â”‚       â”‚                      â”‚       â”‚  â”‚ rate limits   â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤               â”‚                      â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  scopeDefinition â”‚â”€â”€â”€â”€â”€â”€>        â”‚                      â”‚  dataModel          â”‚
â”‚  (file)          â”‚               â”‚                      â”‚  (file)             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚               â”‚                      â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ backend=   â”‚  â”‚               â”‚                      â”‚  â”‚ leads         â”‚  â”‚
â”‚  â”‚ true       â”‚  â”‚               â”‚                      â”‚  â”‚ submissions   â”‚  â”‚
â”‚  â”‚ features[] â”‚  â”‚               â”‚                      â”‚  â”‚ content       â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚               â”‚                      â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”‚                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚                              â”‚
                           â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”                      â–¼
                           â”‚  CONDITIONAL  â”‚              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                           â”‚  Only if      â”‚              â”‚  lp-backend-dev     â”‚
                           â”‚  backend=true â”‚              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `specBackendInterface()` Ã© **condicional** â€” ela sÃ³ Ã© executada quando `backend=true` no `scopeDefinition`. Quando ativada, o agente **Prism** analisa os layouts das seÃ§Ãµes para identificar todos os pontos de interaÃ§Ã£o que requerem backend (formulÃ¡rios, conteÃºdo dinÃ¢mico, integraÃ§Ãµes) e produz uma especificaÃ§Ã£o tÃ©cnica completa para o backend developer.

A task cobre quatro domÃ­nios principais:

1. **FormulÃ¡rios e ValidaÃ§Ãµes** â€” Cada campo de formulÃ¡rio presente nos layouts (contact forms, newsletter signup, lead capture) Ã© especificado com tipo de dado, validaÃ§Ãµes client-side e server-side, constraints de banco e mensagens de erro.

2. **Endpoints REST** â€” A API Ã© definida com endpoints para submissÃ£o de formulÃ¡rios, consulta de leads (admin), gerenciamento de conteÃºdo dinÃ¢mico e health check. Cada endpoint inclui method, path, payload schema, response schema e cÃ³digos de status.

3. **Modelo de Dados** â€” O schema do banco Ã© especificado para armazenar leads, submissÃµes de formulÃ¡rio, conteÃºdo editÃ¡vel e logs de auditoria. Inclui campos, tipos, constraints (NOT NULL, UNIQUE, DEFAULT), Ã­ndices e relaÃ§Ãµes.

4. **Admin e IntegraÃ§Ãµes** â€” Requisitos para painel administrativo (CRUD de conteÃºdo, listagem de leads, exportaÃ§Ã£o) e integraÃ§Ãµes externas (envio de email, CRM, analytics, webhook).

## Passos

1. **Verificar condicional** â€” Confirmar que `scopeDefinition` contÃ©m `backend=true`. Se `backend=false`, esta task Ã© SKIPPED e nÃ£o produz outputs.
2. **Inventariar pontos de interaÃ§Ã£o** â€” Analisar `sectionLayouts` para identificar todos os formulÃ¡rios, Ã¡reas de conteÃºdo dinÃ¢mico e pontos que requerem backend (newsletter signup, contact form, lead capture, FAQ dinÃ¢mico, testimonials dinÃ¢micos).
3. **Especificar campos de formulÃ¡rio** â€” Para cada formulÃ¡rio identificado, listar todos os campos com: nome, tipo de dado (string, email, phone, textarea, select, checkbox), obrigatoriedade, validaÃ§Ãµes (regex, min/max length, format), e mensagens de erro.
4. **Definir validaÃ§Ãµes server-side** â€” Mapear validaÃ§Ãµes que devem ocorrer no servidor alÃ©m do client-side: sanitizaÃ§Ã£o de input, verificaÃ§Ã£o de email, rate limiting por IP, honeypot anti-spam, CAPTCHA (se configurado).
5. **Projetar endpoints REST** â€” Definir cada endpoint:
   - `POST /api/leads` â€” SubmissÃ£o de lead capture form
   - `POST /api/contact` â€” SubmissÃ£o de contact form
   - `POST /api/newsletter` â€” InscriÃ§Ã£o em newsletter
   - `GET /api/content/:section` â€” ConteÃºdo dinÃ¢mico por seÃ§Ã£o (admin)
   - `PUT /api/content/:section` â€” AtualizaÃ§Ã£o de conteÃºdo (admin)
   - `GET /api/leads` â€” Listagem de leads (admin, paginado)
   - `GET /api/health` â€” Health check
6. **Definir schemas de payload e response** â€” Para cada endpoint, especificar o JSON schema do body (request) e do response, incluindo cÃ³digos de status (200, 201, 400, 401, 429, 500).
7. **Modelar dados** â€” Definir as tabelas/collections:
   - `leads` â€” id, name, email, phone, source, created_at, metadata
   - `submissions` â€” id, form_type, data (JSONB), ip_address, user_agent, created_at
   - `content` â€” id, section, key, value, updated_at, updated_by
8. **Especificar rate limiting** â€” Definir limites por endpoint: submissÃµes de formulÃ¡rio (ex: 5/minuto por IP), leitura de conteÃºdo (ex: 60/minuto), endpoints admin (ex: autenticaÃ§Ã£o requerida).
9. **Documentar requisitos de admin** â€” Listar funcionalidades do painel administrativo: visualizar leads com filtros e busca, exportar leads (CSV), editar conteÃºdo das seÃ§Ãµes, visualizar mÃ©tricas de conversÃ£o.
10. **Listar integraÃ§Ãµes externas** â€” Documentar integraÃ§Ãµes necessÃ¡rias: serviÃ§o de email (Resend, SendGrid), CRM (se aplicÃ¡vel), analytics (eventos de conversÃ£o), webhooks (notificaÃ§Ã£o de novo lead).
11. **Compilar backendSpec e dataModel** â€” Gerar os arquivos finais com todas as especificaÃ§Ãµes organizadas e validar contra as post-conditions.
12. **Validar completude** â€” Verificar que nenhum ponto de interaÃ§Ã£o dos layouts ficou sem especificaÃ§Ã£o de backend correspondente.

