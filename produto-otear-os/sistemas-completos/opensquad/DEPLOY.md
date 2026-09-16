# Deploy na VPS

## Pre-requisitos

- Docker + Docker Compose instalados na VPS
- Projeto Supabase criado (https://supabase.com)
- Conta Claude com plano Max

## Passo 1: Clonar o repositorio

```bash
git clone <seu-repo> /opt/opensquad
cd /opt/opensquad
```

## Passo 2: Configurar Supabase

### 2.1 Criar tabelas existentes
No Supabase SQL Editor, execute o conteudo de:
```
interface-app/supabase/schema.sql
```

### 2.2 Criar tabelas multi-tenant
No Supabase SQL Editor, execute o conteudo de:
```
interface-app/supabase/001-multi-tenant.sql
```

### 2.3 Habilitar Auth
No Supabase Dashboard:
1. Va em **Authentication > Providers**
2. Confirme que **Email** esta habilitado
3. Em **Authentication > URL Configuration**, configure:
   - Site URL: `https://seu-dominio.com`
   - Redirect URLs: `https://seu-dominio.com/auth/callback`

### 2.4 Copiar chaves
No Supabase Dashboard > **Settings > API**, copie:
- **Project URL** -> `SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_URL`
- **anon public key** -> `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **service_role secret key** -> `SUPABASE_SERVICE_ROLE_KEY`

## Passo 3: Configurar .env

```bash
cp .env.example .env
nano .env
```

Preencha TODAS as variaveis. Minimo obrigatorio:

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Claude (rodar "claude login" local, copiar de ~/.claude/.credentials.json)
CLAUDE_OAUTH_ACCESS_TOKEN=...
CLAUDE_OAUTH_REFRESH_TOKEN=...
CLAUDE_OAUTH_EXPIRES_AT=...

# Gemini (para gerar imagens)
GEMINI_API_KEY=...

# Redis (nao mudar, ja aponta pro container)
REDIS_URL=redis://redis:6379
```

## Passo 4: Build e subir

```bash
docker compose build
docker compose up -d
```

Isso sobe 4 servicos:
- **app** (porta 3000) - Next.js frontend + API
- **worker** - Processa fila de carrosseis (spawna Claude CLI)
- **ws-gateway** (porta 3001) - WebSocket para atualizacoes em tempo real do escritorio
- **redis** (porta 6379) - Fila de jobs + pub/sub

## Passo 5: Verificar

```bash
# Ver logs dos 3 servicos
docker compose logs -f

# Verificar se tudo subiu
docker compose ps

# Testar app
curl http://localhost:3000/api/health
```

## Passo 6: Testar o fluxo

1. Acesse `http://seu-ip:3000`
2. Sera redirecionado para `/login`
3. Clique em "Criar conta"
4. Preencha email, senha, nome da agencia, nicho
5. Ao finalizar, o tenant e provisionado automaticamente
6. No dashboard, crie seu primeiro carrossel

## Comandos uteis

```bash
# Ver fila do Redis
docker compose exec redis redis-cli
> KEYS bull:squad-runs:*
> LLEN bull:squad-runs:wait

# Ver logs do worker
docker compose logs -f worker

# Reiniciar worker (se mudar credentials)
docker compose restart worker

# Escalar workers (mais concorrencia)
docker compose up -d --scale worker=2

# Ver tenants provisionados
ls data/
```

## Estrutura dos volumes

```
/opt/opensquad/
├── data/                    # Dados dos tenants (volume: tenant-data)
│   └── {tenant-uuid}/
│       ├── squads/carousel/ # Squad clonado do template
│       ├── _opensquad/_memory/company.md
│       └── skills/
├── squads/                  # Template original (volume: squad-output)
└── .env                     # Variaveis de ambiente
```

## Troubleshooting

**Worker nao processa jobs:**
- Verificar se Redis esta rodando: `docker compose ps redis`
- Verificar credentials: `docker compose logs worker | grep credentials`
- Verificar se Claude CLI funciona: `docker compose exec worker claude --version`

**Signup nao provisiona tenant:**
- Verificar se tabelas existem no Supabase
- Verificar SUPABASE_SERVICE_ROLE_KEY no .env
- Ver logs: `docker compose logs app | grep provision`

**Carousel nao gera:**
- Verificar GEMINI_API_KEY
- Verificar se o squad template foi copiado: `docker compose exec worker ls /opensquad/squads/noticias-carrossel-ia/`
- Ver logs do job: `docker compose logs worker`
