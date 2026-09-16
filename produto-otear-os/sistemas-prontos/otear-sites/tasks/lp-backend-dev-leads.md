---
task: createLeadEndpoints()
responsavel: "Forge"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: backendProject
    tipo: file
    obrigatorio: true
    descricao: "Projeto FastAPI inicializado com infraestrutura base (source: setupBackendProject())"
  - nome: backendSpec
    tipo: file
    obrigatorio: true
    descricao: "EspecificaÃ§Ã£o dos endpoints de leads â€” schemas, validaÃ§Ãµes, rate limits (source: specBackendInterface())"
  - nome: dataModel
    tipo: file
    obrigatorio: true
    descricao: "Modelo de dados para leads â€” campos, tipos, Ã­ndices (source: specBackendInterface())"

Saida:
  - nome: leadsApi
    tipo: file
    obrigatorio: true
    descricao: "API de leads completa com CRUD, validaÃ§Ã£o e rate limiting (destination: lp-integrator)"
  - nome: apiDocs
    tipo: file
    obrigatorio: true
    descricao: "DocumentaÃ§Ã£o da API â€” endpoints, schemas, exemplos de request/response (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] backendProject existe com database configurado e funcional"
    - "[ ] backendSpec existe com especificaÃ§Ã£o dos endpoints"
    - "[ ] dataModel existe com schema de leads definido"
  post-conditions:
    - "[ ] POST /api/leads funcional (pÃºblico, com rate limiting)"
    - "[ ] GET /api/admin/leads funcional (autenticado, paginado)"
    - "[ ] GET /api/admin/leads/export funcional (CSV com UTF-8 BOM)"
    - "[ ] DELETE /api/admin/leads/{id} funcional (autenticado)"
    - "[ ] ValidaÃ§Ã£o de input via Pydantic em todos os endpoints"
    - "[ ] CORS configurado para o domÃ­nio do frontend"
    - "[ ] OpenAPI docs auto-gerados e acessÃ­veis em /docs"

Performance:
  duration_expected: "20 minutes"
  cacheable: false
  parallelizable: false
---

# createLeadEndpoints()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ backendProject   â”‚â”€â”€â”€â”
â”‚ (file)           â”‚   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                       â”œâ”€â”€â”€â”€>â”‚                         â”‚â”€â”€â”€â”€>â”‚ leadsApi         â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚  createLeadEndpoints   â”‚     â”‚ (file)           â”‚
â”‚ backendSpec      â”‚â”€â”€â”€â”¤     â”‚  @Forge                 â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ (file)           â”‚   â”‚     â”‚                         â”‚â”€â”€â”€â”€>â”‚ apiDocs          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”‚  CONDITIONAL:           â”‚     â”‚ (file)           â”‚
                       â”‚     â”‚  backend=true           â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜            â”‚
â”‚ dataModel        â”‚â”€â”€â”€â”˜                                            â–¼
â”‚ (file)           â”‚                                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                     â”‚ lp-integrator      â”‚
                                                         â”‚ lp-reviewer        â”‚
                                                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Endpoints gerados:
  POST   /api/leads              (pÃºblico, rate limited)
  GET    /api/admin/leads        (autenticado, paginado)
  GET    /api/admin/leads/export (CSV, UTF-8 BOM)
  DELETE /api/admin/leads/{id}   (autenticado)

âš  CONDITIONAL â€” Executada somente se backend=true
```

## DescriÃ§Ã£o

A task `createLeadEndpoints()` implementa a API completa de captaÃ§Ã£o e gestÃ£o de leads da landing page. O agente **Forge** cria os endpoints pÃºblicos (para o formulÃ¡rio de contato) e administrativos (para gestÃ£o dos leads captados), com validaÃ§Ã£o robusta, rate limiting, autenticaÃ§Ã£o e exportaÃ§Ã£o.

Esta Ã© uma task **condicional** que depende do backend estar habilitado no escopo. Ela implementa o core business do backend â€” a captaÃ§Ã£o de leads Ã© a razÃ£o de existir do backend em uma landing page de captaÃ§Ã£o.

## Passos

1. **Criar modelo SQLAlchemy** â€” Implementar `app/models/lead.py` com os campos definidos no dataModel (nome, email, telefone, empresa, mensagem, created_at, source, utm_params).
2. **Gerar migraÃ§Ã£o** â€” Criar migraÃ§Ã£o Alembic para a tabela de leads com Ã­ndices em email e created_at.
3. **Criar schemas Pydantic** â€” Implementar `app/schemas/lead.py` com LeadCreate (input), LeadResponse (output), LeadListResponse (paginado), com validaÃ§Ãµes de email, telefone e campos obrigatÃ³rios.
4. **Implementar POST /api/leads** â€” Endpoint pÃºblico para captaÃ§Ã£o: validar input, sanitizar dados, salvar no DB, retornar confirmaÃ§Ã£o. Adicionar rate limiting (ex: 5 req/min por IP).
5. **Implementar GET /api/admin/leads** â€” Endpoint autenticado com paginaÃ§Ã£o (page, per_page), filtros (date range, search by email/name) e ordenaÃ§Ã£o (created_at desc).
6. **Implementar GET /api/admin/leads/export** â€” Endpoint autenticado que gera CSV com UTF-8 BOM para compatibilidade com Excel, incluindo todos os campos e filtros aplicados.
7. **Implementar DELETE /api/admin/leads/{id}** â€” Endpoint autenticado para exclusÃ£o individual de lead com soft-delete ou hard-delete conforme spec.
8. **Configurar CORS** â€” Atualizar middleware CORS para aceitar requisiÃ§Ãµes do domÃ­nio do frontend (origin especÃ­fico, nÃ£o wildcard em produÃ§Ã£o).
9. **Implementar rate limiting** â€” Adicionar middleware ou dependÃªncia de rate limiting para o endpoint pÃºblico de captaÃ§Ã£o.
10. **Testar endpoints** â€” Verificar cada endpoint via `/docs` (Swagger UI): criar lead, listar, exportar, deletar. Validar erros de input e autenticaÃ§Ã£o.
11. **Gerar apiDocs** â€” Documentar todos os endpoints com schemas, exemplos de request/response, cÃ³digos de erro e rate limits.

