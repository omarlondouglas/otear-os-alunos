---
task: deployEasyPanel()
responsavel: "Anchor"
responsavel_type: Agente
atomic_layer: Organism
condicional: "backend: true"

Entrada:
  - nome: dockerConfig
    tipo: file
    obrigatorio: true
    descricao: "Dockerfile backend + docker-compose.prod.yml (source: dockerizeBackend())"
  - nome: clientName
    tipo: string
    obrigatorio: true
    descricao: "Nome do cliente para nomear o serviÃ§o no EasyPanel"
  - nome: vercelUrl
    tipo: string
    obrigatorio: true
    descricao: "URL do frontend na Vercel para configurar CORS (source: deployVercel())"

Saida:
  - nome: backendResult
    tipo: object
    obrigatorio: true
    descricao: "Resultado do deploy backend: URL API, health status (destination: lp-versioner)"

Checklist:
  pre-conditions:
    - "[ ] Dockerfile backend testado e funcional"
    - "[ ] Acesso Ã  VPS com EasyPanel configurado"
    - "[ ] Frontend jÃ¡ deployado na Vercel"
    - "[ ] Flag backend: true no escopo"
  post-conditions:
    - "[ ] Projeto 'lp-backends' existe no EasyPanel (criado se primeiro deploy)"
    - "[ ] ServiÃ§o backend criado: {cliente}-api"
    - "[ ] PostgreSQL provisionado: {cliente}-db"
    - "[ ] VariÃ¡veis de ambiente configuradas (incluindo CORS para Vercel)"
    - "[ ] Health check respondendo 200"
    - "[ ] API acessÃ­vel via URL do EasyPanel"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# deployEasyPanel()

> **CONDICIONAL**: Esta task sÃ³ roda quando `backend: true` no escopo.
> Para LPs sem backend (90% dos casos), esta task Ã© pulada completamente.

## DescriÃ§Ã£o

Deploy do backend FastAPI no EasyPanel da VPS. Cria serviÃ§o Docker + PostgreSQL dentro do projeto `lp-backends`. O frontend jÃ¡ estÃ¡ na Vercel â€” aqui sÃ³ sobe o backend e banco.

## Passos

1. **Verificar acesso ao EasyPanel** â€” API acessÃ­vel.
2. **Verificar projeto `lp-backends`** â€” Criar se nÃ£o existir (sÃ³ na primeira vez).
3. **Criar serviÃ§o `{cliente}-api`** â€” Docker com Dockerfile do backend.
4. **Criar serviÃ§o `{cliente}-db`** â€” PostgreSQL via template EasyPanel.
5. **Configurar variÃ¡veis de ambiente**:
   - `DATABASE_URL` â€” PostgreSQL interno
   - `FRONTEND_URL` â€” URL da Vercel do cliente (CORS)
   - `FRONTEND_CUSTOM_DOMAIN` â€” DomÃ­nio prÃ³prio se tiver (CORS)
   - `SECRET_KEY` â€” Chave JWT
6. **Configurar networking** â€” Backend â†” PostgreSQL via rede interna.
7. **Build & deploy** â€” Triggar build no EasyPanel.
8. **Verificar health check** â€” `/health` respondendo 200.
9. **Registrar URL da API** â€” Para configurar no frontend (Vercel env vars).
10. **Atualizar frontend** â€” Setar `NEXT_PUBLIC_API_URL` na Vercel apontando para o backend.

## EasyPanel â€” Estrutura Backend

```
EasyPanel Dashboard (Free â€” 3 projetos)
â”œâ”€â”€ Projeto: lp-backends              â† backends de todos os clientes
â”‚   â”œâ”€â”€ Service: cliente-maria-api    â† FastAPI
â”‚   â”œâ”€â”€ Service: cliente-maria-db     â† PostgreSQL
â”‚   â”œâ”€â”€ Service: cliente-ana-api
â”‚   â”œâ”€â”€ Service: cliente-ana-db
â”‚   â””â”€â”€ ...
â”œâ”€â”€ Projeto: (reserva)
â””â”€â”€ Projeto: (reserva)
```

## ConexÃ£o Vercel â†” EasyPanel

```
Vercel (Frontend)                    EasyPanel (Backend)
{cliente}.vercel.app  â”€â”€HTTPâ”€â”€>  {cliente}-api.easypanel.host
                                      â”‚
                                      â–¼
                                 {cliente}-db (PostgreSQL)
```

### VariÃ¡veis de ambiente

**Na Vercel (frontend):**
```
NEXT_PUBLIC_API_URL=https://{cliente}-api.easypanel.host
```

**No EasyPanel (backend):**
```
DATABASE_URL=postgresql://user:pass@{cliente}-db:5432/leads
FRONTEND_URL=https://{cliente}-lp.vercel.app
SECRET_KEY=...
```

