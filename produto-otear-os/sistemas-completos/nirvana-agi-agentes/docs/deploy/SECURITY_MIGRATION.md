# Migração de Segurança — O Tear Agentes

## O que mudou

As chaves secretas foram **removidas do frontend** e do repositório Git.
Agora elas ficam **apenas no EasyPanel** (variáveis de ambiente do serviço backend).

O frontend **não precisa mais de chaves secretas** — ele usa o token JWT do Supabase
para se autenticar com o backend.

---

## Onde colocar cada chave

### EasyPanel — Serviço BACKEND (variáveis de ambiente)

Vá em **EasyPanel > seu serviço backend > Environment Variables** e configure:

```
# OBRIGATÓRIAS
API_KEY=<gere uma chave segura com: openssl rand -hex 32>
ADMIN_PASSWORD=<senha forte, mínimo 12 caracteres>
DATABASE_URL=postgres://postgres:<senha>@otear_db_agi:5432/agi
REDIS_URL=redis://default:<senha>@otear_redis_otear:6379
CELERY_BROKER_URL=redis://default:<senha>@otear_redis_otear:6379

# Supabase (server-side)
SUPABASE_URL=https://gagzdrhqmdkrcotrvfgc.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...  (a mesma anon key)
SUPABASE_SERVICE_KEY=eyJhbGci...  (Service Role Key do Supabase)

# LLM (pelo menos uma dessas)
GOOGLE_API_KEY=<nova chave do Google AI Studio>
# ANTHROPIC_API_KEY=sk-ant-...  (opcional, para produção sem CLI)

# Storage S3/MinIO (você já tem MinIO configurado)
STORAGE_TYPE=s3
S3_ENDPOINT_URL=https://teste-minio.qc7qit.easypanel.host/
S3_ACCESS_KEY=<nova chave — rotacionar no painel MinIO>
S3_SECRET_KEY=<nova chave — rotacionar no painel MinIO>
S3_BUCKET_NAME=agi
S3_REGION=us-east-1

# Tools dos Agentes
TAVILY_API_KEY=<nova chave>
NEWS_API_KEY=<nova chave>

# TTS
ELEVENLABS_API_KEY=<nova chave>
ELEVENLABS_VOICE_ID=GDzHdQOi6jjf8zaXhCYD

# WhatsApp
EVOLUTION_API_URL=https://evo2.otear.com.br
EVOLUTION_API_KEY=<nova chave>
EVOLUTION_INSTANCE_NAME=agi

# Video Editor
VIDEO_EDITOR_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host
VIDEO_EDITOR_API_KEY=<nova chave>

# URLs
PUBLIC_URL=https://otear-agentes-otear.qc7qit.easypanel.host
ALLOWED_ORIGINS=https://otear-agentes-frontend.qc7qit.easypanel.host

# Models
MODEL_PLANNER=claude-sonnet-4-6
MODEL_WRITER=claude-sonnet-4-6
MODEL_FAST=claude-haiku-4-5-20251001

# Storage local (apenas para vídeos temporários do ffmpeg, não para arquivos permanentes)
STORAGE_PATH=/app/storage
```

### EasyPanel — Serviço FRONTEND

O frontend **NÃO precisa de variáveis de ambiente**. Tudo já está no `.env.production`
que é commitado no Git (contém apenas chaves públicas):

```
VITE_API_URL=https://otear-agentes-otear.qc7qit.easypanel.host
VITE_APP_NAME=O Tear Agentes
VITE_SUPABASE_URL=https://gagzdrhqmdkrcotrvfgc.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...  (anon key é pública por design do Supabase)
```

---

## Chaves que DEVEM ser rotacionadas (foram expostas no Git)

Todas as chaves abaixo estavam no arquivo `frontend-react/.env` que foi commitado.
Gere novas chaves para cada uma:

| Serviço | Onde gerar nova chave |
|---------|----------------------|
| OpenAI | https://platform.openai.com/api-keys |
| Google AI | https://aistudio.google.com/apikey |
| ElevenLabs | https://elevenlabs.io/app/settings/api-keys |
| Tavily | https://tavily.com/dashboard |
| NewsAPI | https://newsapi.org/account |
| Evolution API | Painel da Evolution |
| S3/MinIO | Painel do MinIO |
| Database | SQL: `ALTER USER postgres PASSWORD 'nova_senha';` |
| Redis | Reconfigurar no EasyPanel |

---

## Como funciona a autenticação agora

```
ANTES:
  Frontend → envia x-admin-password: "Senha021@..." → Backend

AGORA:
  1. Usuário faz login no Supabase (email + senha)
  2. Frontend recebe JWT token do Supabase
  3. Frontend envia Authorization: Bearer <jwt_token> → Backend
  4. Backend valida o JWT com o Supabase
  5. Backend retorna dados do usuário autenticado
```

Vantagens:
- Cada usuário tem seu próprio token (multi-user)
- Tokens expiram automaticamente
- Não há senha compartilhada
- Webhooks/integrações usam X-API-Key (separado)

---

## Checklist de deploy

- [ ] Gerar novas chaves para todos os serviços listados acima
- [ ] Configurar variáveis de ambiente no backend do EasyPanel
- [ ] Rebuild do backend (para instalar `slowapi`)
- [ ] Rebuild do frontend (para aplicar mudanças de auth)
- [ ] Testar login no frontend
- [ ] Testar chat (deve funcionar com Bearer token)
- [ ] Testar onboarding
- [ ] Revogar as chaves antigas nos painéis dos serviços
