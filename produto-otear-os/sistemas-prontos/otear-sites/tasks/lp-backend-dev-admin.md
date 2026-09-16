---
task: buildAdminPanel()
responsavel: "Forge"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: leadsApi
    tipo: file
    obrigatorio: true
    descricao: "API de leads completa e funcional com todos os endpoints (source: createLeadEndpoints())"
  - nome: scopeDefinition
    tipo: file
    obrigatorio: true
    descricao: "DefiniÃ§Ã£o de escopo com flags backend=true e admin_panel=true (source: defineScope())"

Saida:
  - nome: adminPanel
    tipo: file
    obrigatorio: true
    descricao: "Painel administrativo completo com autenticaÃ§Ã£o, dashboard e gestÃ£o de leads (destination: lp-reviewer)"
  - nome: adminAuth
    tipo: file
    obrigatorio: true
    descricao: "Sistema de autenticaÃ§Ã£o do admin â€” JWT, login, middleware (destination: lp-integrator)"

Checklist:
  pre-conditions:
    - "[ ] leadsApi existe com endpoints funcionais"
    - "[ ] scopeDefinition tem backend=true E admin_panel=true"
  post-conditions:
    - "[ ] PÃ¡gina de login com autenticaÃ§Ã£o JWT funcional"
    - "[ ] Dashboard com contagem e estatÃ­sticas de leads"
    - "[ ] Tabela de leads com paginaÃ§Ã£o, busca e filtro"
    - "[ ] BotÃ£o de exportaÃ§Ã£o CSV funcional"
    - "[ ] VisualizaÃ§Ã£o individual de lead com todos os campos"
    - "[ ] ExclusÃ£o de lead com diÃ¡logo de confirmaÃ§Ã£o"
    - "[ ] Senhas hasheadas com bcrypt"
    - "[ ] Tokens JWT com expiraÃ§Ã£o configurada"

Performance:
  duration_expected: "25 minutes"
  cacheable: false
  parallelizable: false
---

# buildAdminPanel()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ leadsApi         â”‚â”€â”€â”€â”
â”‚ (file)           â”‚   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                  â”‚   â”œâ”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€>â”‚ adminPanel       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”‚  buildAdminPanel     â”‚     â”‚ (file)           â”‚
                       â”‚     â”‚  @Forge              â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚                      â”‚â”€â”€â”€â”€>â”‚ adminAuth        â”‚
â”‚ scopeDefinition  â”‚â”€â”€â”€â”˜     â”‚  CONDITIONAL:        â”‚     â”‚ (file)           â”‚
â”‚ (file)           â”‚         â”‚  backend=true AND    â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â”‚  admin_panel=true    â”‚            â”‚
                             â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜            â–¼
                                                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                      â”‚ lp-reviewer      â”‚
                                                      â”‚ lp-integrator    â”‚
                                                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Telas do Admin Panel:
  /admin/login      â†’ Login com JWT
  /admin/dashboard  â†’ EstatÃ­sticas de leads
  /admin/leads      â†’ Tabela paginada com busca/filtro
  /admin/leads/:id  â†’ Detalhe individual do lead
  [Export CSV]      â†’ Download via API

âš  CONDITIONAL â€” Executada somente se backend=true AND admin_panel=true
```

## DescriÃ§Ã£o

A task `buildAdminPanel()` cria o painel administrativo completo para gestÃ£o dos leads captados pela landing page. O agente **Forge** implementa autenticaÃ§Ã£o JWT, dashboard com estatÃ­sticas, tabela de leads com funcionalidades de busca/filtro/paginaÃ§Ã£o, exportaÃ§Ã£o CSV e gestÃ£o individual de leads.

Esta Ã© uma task **duplamente condicional** â€” requer tanto `backend=true` quanto `admin_panel=true` no escopo. Ã‰ a Ãºltima peÃ§a do backend, consumindo a API de leads jÃ¡ funcional para apresentar uma interface de gestÃ£o ao administrador do site.

## Passos

1. **Verificar condicionalidade** â€” Confirmar que `scopeDefinition.backend = true` E `scopeDefinition.admin_panel = true`. Se qualquer flag for false, skip a task.
2. **Implementar sistema de autenticaÃ§Ã£o** â€” Criar modelo User com email e password hash (bcrypt), endpoint `POST /api/auth/login` retornando JWT, middleware de verificaÃ§Ã£o de token.
3. **Configurar JWT** â€” Definir SECRET_KEY, algoritmo (HS256), expiraÃ§Ã£o (configurable via env), refresh token strategy.
4. **Criar seed de admin** â€” Script para criar o primeiro usuÃ¡rio admin via CLI ou migration (`python -m app.cli create-admin`).
5. **Implementar pÃ¡gina de login** â€” FormulÃ¡rio com email/senha, validaÃ§Ã£o client-side, feedback de erro, redirect para dashboard apÃ³s login.
6. **Implementar dashboard** â€” PÃ¡gina com cards de estatÃ­sticas: total de leads, leads hoje, leads esta semana, leads este mÃªs. GrÃ¡fico simples de leads por dia (Ãºltimos 30 dias).
7. **Implementar tabela de leads** â€” Tabela com colunas: nome, email, empresa, data, status. PaginaÃ§Ã£o server-side, busca por texto, filtro por data range.
8. **Implementar detalhe do lead** â€” PÃ¡gina com todos os campos do lead, incluindo UTM parameters, timestamp de criaÃ§Ã£o, e IP de origem (se captado).
9. **Implementar exportaÃ§Ã£o CSV** â€” BotÃ£o que dispara download via `GET /api/admin/leads/export` com os filtros ativos aplicados.
10. **Implementar exclusÃ£o de lead** â€” BotÃ£o de delete com diÃ¡logo de confirmaÃ§Ã£o modal, chamada ao endpoint `DELETE /api/admin/leads/{id}`, feedback de sucesso/erro.
11. **Proteger rotas** â€” Middleware que redireciona para login se token ausente/expirado em todas as rotas `/admin/*` exceto `/admin/login`.
12. **Testar fluxo completo** â€” Login â†’ dashboard â†’ listar leads â†’ buscar â†’ filtrar â†’ exportar CSV â†’ ver detalhe â†’ deletar lead â†’ logout.

