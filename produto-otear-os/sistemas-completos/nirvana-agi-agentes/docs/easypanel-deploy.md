# Deploy Hermes + Vault no EasyPanel

**Hermes nÃ£o Ã© app separado.** Ele roda dentro do gateway atual â€” basta
configurar volumes + envs corretos.

## VisÃ£o geral

```
â”Œâ”€ EasyPanel App "gateway" (FastAPI) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  /api/v1/hermes/chat   â† Hermes embutido     â”‚
â”‚  /api/v1/agents/*      â† RPC pros 13 agentes â”‚
â”‚  /api/v1/references/*  â† banco creators      â”‚
â”‚  /api/v1/graph/*       â† mapa visual         â”‚
â”‚  /llm-proxy/v1/*       â† Claude CLI proxy    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## 1. Volumes a criar no EasyPanel

| Nome (sugerido) | Mount path | Por que |
|---|---|---|
| `hermes_home` | `/root/.hermes` | Persiste sessions, skills custom, config Hermes |
| `claude_credentials` | `/root/.claude` | OAuth Max do Claude (jÃ¡ existente) |
| `app_storage` | `/app/storage` | Uploads, Playwright Chromium cache e referÃªncias extraÃ­das |
| `otear_vault` | `/app/vault` | USER.md, MEMORY.md e conteÃºdo-base clonado do GitHub |

## 2. Environment variables novas

```env
# Vault Obsidian
VAULT_PATH=/app/vault
REFERENCES_PATH=/app/storage/references
VAULT_REPO_URL=https://github.com/omarlondouglas/o-tear-vault.git
VAULT_DEPLOY_TOKEN=ghp_xxxxxxxxxxxx       # PAT classico, scope "repo"

# Hermes
HERMES_LLM_PROXY_URL=http://localhost:8000/llm-proxy/v1

# Imagem (sem chatgpt-bridge no EasyPanel inicial)
IMAGE_GEN_PROVIDER=gemini
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxx          # se for usar Gemini
```

## 3. Como gerar o `VAULT_DEPLOY_TOKEN`

1. Vai em [github.com/settings/tokens/new](https://github.com/settings/tokens/new)
2. **Note**: `o-tear-vault deploy (EasyPanel)`
3. **Expiration**: 90 dias (ou "no expiration" se preferir)
4. **Scopes**: marca apenas `repo` (full control of private repositories â€” precisa pra escrever tambÃ©m se Hermes for fazer commits)
5. Generate token â†’ copia o `ghp_...`
6. Cola em `VAULT_DEPLOY_TOKEN` no EasyPanel

> Se quiser **sÃ³ leitura**, cria fine-grained PAT com escopo "Contents: Read".
> Mas Hermes pode querer atualizar `MEMORY.md` automaticamente â€” nesse caso
> precisa de write tambÃ©m.

## 4. SequÃªncia do entrypoint no boot

O `entrypoint.sh` faz tudo automaticamente:

1. Injeta credenciais OAuth do Claude (do env var)
2. Smoke test do Claude CLI
3. Instala Playwright Chromium se necessÃ¡rio
4. **Clona vault do GitHub** (ou faz `git pull` se jÃ¡ existe)
5. **Inicializa `~/.hermes/`** se primeira boot (config.yaml + SOUL.md)
6. Sobe FastAPI

## 5. Vault â€” fluxo de sincronizaÃ§Ã£o

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  VocÃª (dev local)     â”‚ git pushâ”‚  GitHub: o-tear-vaultâ”‚
â”‚  {OTEAR_VAULT_ROOT}             â”‚â”€â”€â”€â”€â”€â”€â”€â”€â–¶â”‚  (repo privado)      â”‚
â”‚  edita USER.md no     â”‚         â”‚                      â”‚
â”‚  Obsidian app         â”‚         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                   â”‚ git clone
                                            â”‚ no boot
                                            â–¼
                                  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                  â”‚  EasyPanel containerâ”‚
                                  â”‚  /app/vault         â”‚
                                  â”‚  Hermes le daqui    â”‚
                                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**LimitaÃ§Ã£o atual:** o boot clona o vault uma vez. Se vocÃª editar no
Obsidian local e quiser atualizar em produÃ§Ã£o, precisa **restartar o container**
(o entrypoint faz `git pull` no prÃ³ximo boot).

**Melhoria futura:** rota POST /api/v1/admin/vault/refresh que dispara `git pull`
sem restart. NÃ£o implementada ainda â€” basta restart por enquanto.

## 6. Credenciais Claude â€” refresh automatico (NUNCA expirar)

### Problema

As env vars `CLAUDE_OAUTH_ACCESS_TOKEN` no EasyPanel sao **imutaveis** ate
voce editar o painel. O token tem validade curta (~8h). Se o entrypoint
sobrescrever o arquivo a cada boot com a env var antiga, o sistema fica
sempre expirado.

### Solucao (ja implementada)

1. **Volume persistente** `claude_credentials â†’ /root/.claude` (ja tinha)
2. **Entrypoint inteligente** so injeta a env var quando o arquivo NAO existe.
   Se ja existe (segundo boot em diante), preserva o token mais recente.
3. **Celery beat task** roda a cada 30min e troca o `access_token` por um
   novo via `refresh_token` se faltar < 1h pro expiry. Salva no volume.
4. **Backup persistente** em `/app/storage/.claude_credentials_backup.json`
   (sobrevive se `/root/.claude` for resetado).

### Setup pratico no EasyPanel

1. Confirma o volume `claude_credentials` em `/root/.claude` (provavelmente
   ja tem do deploy anterior).
2. Confirma que ha **so um instance** rodando (o beat duplica jobs se voce
   subir o app em multiplos containers â€” use 1 replica pro gateway).
3. Cola as 3 env vars com tokens **frescos** copiados do seu CLI:
   ```env
   CLAUDE_OAUTH_ACCESS_TOKEN=sk-ant-oat01-...
   CLAUDE_OAUTH_REFRESH_TOKEN=sk-ant-ort01-...
   CLAUDE_OAUTH_EXPIRES_AT=1234567890123   # ms desde epoch
   ```
4. Deploy â†’ o app injeta no boot e a partir de entao o beat mantem fresco.
5. Pra reinjetar tokens novos (caso o refresh_token tambem expire â€” raro,
   dura meses): cola tokens novos + define `CLAUDE_OAUTH_FORCE_REINJECT=true`,
   redeploy, depois remova essa env var.

### Como pegar tokens frescos da sua maquina

Linux/Mac:
```bash
cat ~/.claude/.credentials.json | jq '.claudeAiOauth | {accessToken, refreshToken, expiresAt}'
```

Windows PowerShell:
```powershell
Get-Content "$env:USERPROFILE\.claude\.credentials.json" | ConvertFrom-Json | Select-Object -ExpandProperty claudeAiOauth | Select-Object accessToken, refreshToken, expiresAt
```

### Endpoints uteis (auth via header `X-Admin-Password` ou Bearer)

```bash
# Status atual
curl -H "X-Admin-Password: $ADMIN_PASSWORD" \
  https://seu-dominio.com/api/v1/admin/claude/credentials/status
# {"present": true, "has_refresh_token": true, "expires_in_minutes": 412, "expired": false}

# Forcar refresh agora (bypass janela de 1h)
curl -X POST -H "X-Admin-Password: $ADMIN_PASSWORD" \
  "https://seu-dominio.com/api/v1/admin/claude/credentials/refresh?force=true"
# {"status": "refreshed", "expires_in_minutes": 480}
```

### Logs

Procure linhas `[claude-refresh-task]` ou `[claude-refresh]` nos logs do
EasyPanel pra ver o status do refresh periodico.

---

## 7. Sem chatgpt-bridge no EasyPanel inicial

O sidecar `chatgpt-bridge` precisa de `~/.codex/auth.json` montado, que Ã©
chato em ambiente managed como EasyPanel.

**RecomendaÃ§Ã£o:** comeÃ§a sÃ³ com `IMAGE_GEN_PROVIDER=gemini` (passa `GOOGLE_API_KEY`
no env). Quando precisar do gpt-image-2, sobe `chatgpt-bridge` como app separado
no EasyPanel ou em VPS prÃ³pria e aponta `CHATGPT_BRIDGE_URL` pra ele.

## 7. Checklist pra deploy

- [ ] Repo `o-tear-vault` estÃ¡ privado no GitHub
- [ ] PAT gerado e adicionado em `VAULT_DEPLOY_TOKEN` no EasyPanel
- [ ] 4 volumes criados (`hermes_home`, `claude_credentials`, `app_storage`, `otear_vault`)
- [ ] `VAULT_PATH=/app/vault`, `VAULT_REPO_URL=...`, `VAULT_DEPLOY_TOKEN=...` no env
- [ ] `IMAGE_GEN_PROVIDER=gemini` + `GOOGLE_API_KEY` configurados
- [ ] `CLAUDE_OAUTH_ACCESS_TOKEN` + refresh + expires (jÃ¡ tinha)
- [ ] Push do cÃ³digo â†’ EasyPanel faz redeploy
- [ ] Verificar logs: deve aparecer "Vault clonado com sucesso" + "AIAgent criado"
- [ ] Testar: `GET /api/v1/hermes/health` retorna `{ready: true}`

## 8. Troubleshooting

```bash
# Verificar se vault foi clonado
docker exec -it <container> ls -la /app/vault/.system/

# Ver logs do entrypoint
docker logs <container> | grep entrypoint

# Healthcheck Hermes
curl https://seu-app.easypanel.host/api/v1/hermes/health

# Reiniciar pra forÃ§ar git pull do vault
docker-compose restart gateway
```
