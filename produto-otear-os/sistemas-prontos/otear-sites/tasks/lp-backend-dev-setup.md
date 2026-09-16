---
task: setupBackendProject()
responsavel: "Forge"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: backendSpec
    tipo: file
    obrigatorio: true
    descricao: "EspecificaÃ§Ã£o da interface backend â€” endpoints, modelos, autenticaÃ§Ã£o (source: specBackendInterface())"
  - nome: scopeDefinition
    tipo: file
    obrigatorio: true
    descricao: "DefiniÃ§Ã£o de escopo com flag backend=true habilitada (source: defineScope())"

Saida:
  - nome: backendProject
    tipo: file
    obrigatorio: true
    descricao: "Projeto Python/FastAPI inicializado com infraestrutura configurada (destination: createLeadEndpoints())"
  - nome: backendConfig
    tipo: object
    obrigatorio: true
    descricao: "ConfiguraÃ§Ãµes do backend â€” porta, base URL, DB connection, scripts (destination: lp-integrator)"

Checklist:
  pre-conditions:
    - "[ ] backendSpec existe com endpoints e modelos definidos"
    - "[ ] scopeDefinition tem backend=true"
  post-conditions:
    - "[ ] Python 3.12+ projeto inicializado com pyproject.toml"
    - "[ ] FastAPI app criado com roteamento configurado"
    - "[ ] SQLAlchemy 2.0 configurado com async engine"
    - "[ ] Alembic configurado para migraÃ§Ãµes"
    - "[ ] Pydantic v2 Settings para configuraÃ§Ã£o via env vars"
    - "[ ] Estrutura de diretÃ³rios criada (app/api, app/models, app/schemas, app/services)"
    - "[ ] MigraÃ§Ã£o inicial criada e aplicada"
    - "[ ] Servidor inicia sem erros com uvicorn"

Performance:
  duration_expected: "10 minutes"
  cacheable: true
  parallelizable: false
---

# setupBackendProject()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ backendSpec      â”‚â”€â”€â”€â”
â”‚ (file)           â”‚   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                  â”‚   â”œâ”€â”€â”€â”€>â”‚                       â”‚â”€â”€â”€â”€>â”‚ backendProject      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”‚  setupBackendProject  â”‚     â”‚ (file)              â”‚
                       â”‚     â”‚  @Forge               â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚                       â”‚â”€â”€â”€â”€>â”‚ backendConfig       â”‚
â”‚ scopeDefinition  â”‚â”€â”€â”€â”˜     â”‚  CONDITIONAL:         â”‚     â”‚ (object)            â”‚
â”‚ (file)           â”‚         â”‚  backend=true         â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜            â”‚
                                                                  â–¼
                                                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                     â”‚ createLeadEndpoints()  â”‚
                                                     â”‚ lp-integrator          â”‚
                                                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

âš  CONDITIONAL â€” Executada somente se scopeDefinition.backend = true
```

## DescriÃ§Ã£o

A task `setupBackendProject()` estabelece a fundaÃ§Ã£o tÃ©cnica do backend da landing page. O agente **Forge** inicializa um projeto Python moderno com FastAPI, configura SQLAlchemy 2.0 com suporte async, Alembic para migraÃ§Ãµes de banco de dados e Pydantic v2 para validaÃ§Ã£o e configuraÃ§Ã£o.

Esta Ã© uma task **condicional** â€” sÃ³ Ã© executada quando o escopo do projeto inclui backend (`backend=true`). Projetos puramente estÃ¡ticos (sem captaÃ§Ã£o de leads ou admin) nÃ£o ativam esta task. O backendConfig exportado permite que o integrador conecte frontend e backend.

## Passos

1. **Verificar condicionalidade** â€” Confirmar que `scopeDefinition.backend = true`. Se false, skip a task inteira.
2. **Inicializar projeto Python** â€” Criar estrutura com `pyproject.toml`, configurar dependÃªncias (fastapi, uvicorn, sqlalchemy, alembic, pydantic, python-jose, passlib, python-multipart).
3. **Criar estrutura de diretÃ³rios** â€” Organizar em `app/api/` (routers), `app/models/` (SQLAlchemy), `app/schemas/` (Pydantic), `app/services/` (lÃ³gica de negÃ³cio), `app/core/` (config, security, database).
4. **Configurar FastAPI app** â€” Criar `app/main.py` com CORS middleware, router includes, lifespan events para conexÃ£o DB.
5. **Configurar SQLAlchemy 2.0** â€” Criar engine async, SessionLocal, Base declarativa em `app/core/database.py`.
6. **Configurar Alembic** â€” Inicializar Alembic com `alembic init`, configurar `env.py` para usar async e target_metadata do SQLAlchemy.
7. **Configurar Pydantic Settings** â€” Criar `app/core/config.py` com Settings class lendo de `.env` (DATABASE_URL, SECRET_KEY, CORS_ORIGINS, etc.).
8. **Criar migraÃ§Ã£o inicial** â€” Gerar e aplicar a primeira migraÃ§Ã£o com o schema base.
9. **Testar setup** â€” Executar `uvicorn app.main:app --reload` e verificar que a API inicia, `/docs` Ã© acessÃ­vel e a conexÃ£o com DB funciona.
10. **Exportar backendConfig** â€” Documentar porta, base URL, connection string (template), scripts e endpoints de health check.

