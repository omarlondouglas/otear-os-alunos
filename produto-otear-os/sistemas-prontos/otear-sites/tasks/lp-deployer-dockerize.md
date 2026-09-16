---
task: dockerizeBackend()
responsavel: "Anchor"
responsavel_type: Agente
atomic_layer: Organism
condicional: "backend: true"

Entrada:
  - nome: backendProject
    tipo: file
    obrigatorio: true
    descricao: "Projeto backend FastAPI funcional (source: setupBackend())"
  - nome: qaReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio final de QA com PASS >= 8.0 (source: finalReport())"

Saida:
  - nome: dockerConfig
    tipo: file
    obrigatorio: true
    descricao: "Dockerfile backend + docker-compose.prod.yml (destination: deployEasyPanel())"

Checklist:
  pre-conditions:
    - "[ ] Backend funcional com uvicorn"
    - "[ ] QA report com PASS e score >= 8.0"
    - "[ ] Flag backend: true no escopo"
  post-conditions:
    - "[ ] Dockerfile backend criado (Python slim + uvicorn, < 300MB)"
    - "[ ] docker-compose.prod.yml com backend + PostgreSQL"
    - "[ ] .env.example com variÃ¡veis do backend"
    - "[ ] docker compose build sem erros"
    - "[ ] Health check endpoint /health respondendo"

Performance:
  duration_expected: "8 minutes"
  cacheable: true
  parallelizable: false
---

# dockerizeBackend()

> **CONDICIONAL**: Esta task sÃ³ roda quando `backend: true` no escopo.
> Frontend NÃƒO precisa de Docker â€” vai direto na Vercel.

## DescriÃ§Ã£o

Gera Dockerfile otimizado para o backend FastAPI e docker-compose.prod.yml para orquestrar backend + PostgreSQL no EasyPanel. O frontend vai pra Vercel e nÃ£o precisa de Docker.

## Passos

1. **Validar QA gate** â€” Confirmar PASS com score >= 8.0.
2. **Criar Dockerfile backend** â€” Python slim, instalar deps, copiar app, uvicorn.
3. **Criar docker-compose.prod.yml** â€” Backend (porta 8000) + PostgreSQL.
4. **Criar .env.example** â€” DATABASE_URL, SECRET_KEY, CORS_ORIGINS (URL da Vercel).
5. **Configurar CORS** â€” Permitir origem da Vercel (`{cliente}-lp.vercel.app` + domÃ­nio prÃ³prio).
6. **Configurar health check** â€” Endpoint `/health` no FastAPI.
7. **Testar build** â€” `docker compose build` sem erros.
8. **Testar run** â€” `docker compose up` com health check OK.

## Dockerfile Backend

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## CORS â€” Conectar Vercel â†” EasyPanel

```python
# app/core/middleware.py
CORS_ORIGINS = [
    os.getenv("FRONTEND_URL"),           # https://{cliente}-lp.vercel.app
    os.getenv("FRONTEND_CUSTOM_DOMAIN"), # https://www.cliente.com.br (opcional)
]
```

## Nota
- Frontend NUNCA precisa de Docker â€” Vercel deploy nativo
- Esta task sÃ³ existe para o caso raro de LP com backend
- O docker-compose.prod.yml Ã© para EasyPanel, nÃ£o para Vercel

