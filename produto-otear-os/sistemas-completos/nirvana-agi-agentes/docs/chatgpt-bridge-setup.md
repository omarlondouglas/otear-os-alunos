# ChatGPT Bridge — Geração de imagens via subscription ChatGPT

Este projeto roda um sidecar Docker chamado `chatgpt-bridge` que expõe um endpoint
OpenAI-compatible em `http://chatgpt-bridge:10531/v1` (visivel só pela rede interna
`agi-network`).

A tool `generate_image_tool` (usada por Scher, GaryV e novos squads) tenta primeiro
o chatgpt-bridge (gpt-image-2) e cai pro Google Gemini se indisponivel.

## Por que

- Sem API key paga: usa o OAuth da sua subscription ChatGPT (que voce ja paga).
- Modelo `gpt-image-2`: estado da arte da OpenAI hoje.
- Custo por imagem: $0 (consome quota da subscription).

## Setup (uma vez)

### 1. Login no Codex CLI na sua maquina

```bash
npx -y @openai/codex login
```

Browser abre → autentica na ChatGPT (subscription Plus/Pro/Team) → CLI escreve `~/.codex/auth.json`.

### 2. Copia o conteudo do auth.json

**Windows (CMD):**
```cmd
type C:\Users\%USERNAME%\.codex\auth.json
```

**Windows (PowerShell):**
```powershell
Get-Content $env:USERPROFILE\.codex\auth.json -Raw
```

**Linux/Mac:**
```bash
cat ~/.codex/auth.json
```

### 3a. Producao via EasyPanel — RECOMENDADO

No `auth.json` voce ve algo assim:
```json
{
  "OPENAI_API_KEY": null,
  "tokens": {
    "id_token": "eyJhbG...",
    "access_token": "eyJhbG...",
    "refresh_token": "...",
    "account_id": "..."
  },
  "last_refresh": "2026-05-03T..."
}
```

No app `chatgpt-bridge` do EasyPanel, adiciona estas env vars (padronizadas
com o Claude OAuth):

| Env var | Valor |
|---|---|
| `CODEX_ACCESS_TOKEN` | `tokens.access_token` |
| `CODEX_REFRESH_TOKEN` | `tokens.refresh_token` |
| `CODEX_ID_TOKEN` | `tokens.id_token` (opcional) |
| `CODEX_ACCOUNT_ID` | `tokens.account_id` (opcional) |
| `CODEX_LAST_REFRESH` | `last_refresh` (opcional) |

O entrypoint do servico monta o `/root/.codex/auth.json` automaticamente no boot
(usa `jq` pra serializar com formato correto).

Alternativa simples: cola o JSON inteiro em UMA linha como `CODEX_AUTH_JSON`.
O entrypoint detecta e usa direto.

### 3b. Producao via volume Docker (alternativa)

Se preferir nao expor o JSON em env var:

```bash
# Linux/Mac
docker run --rm -v "$HOME/.codex:/src:ro" -v codex_auth:/dst alpine \
  sh -c "cp -r /src/. /dst/"

# Windows PowerShell
docker run --rm -v "${env:USERPROFILE}\.codex:/src:ro" -v codex_auth:/dst alpine `
  sh -c "cp -r /src/. /dst/"
```

### 3c. Dev local

Sobe o stack inteiro:
```bash
docker-compose up --build
```

O bridge vai usar `CODEX_AUTH_JSON` do `.env` se setado, senao espera o volume
ja ter sido populado pelo passo 3b.

### 4. Verificar

```bash
# Health do bridge
curl http://localhost:10531/health

# Gerar uma imagem de teste
curl -s http://localhost:10531/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"a fox","size":"1024x1024"}' \
  | jq -r '.data[0].b64_json' | base64 -d > test.png
```

## Configuração via env

| Variavel | Default | Descricao |
|---|---|---|
| `IMAGE_GEN_PROVIDER` | `auto` | `chatgpt`, `gemini` ou `auto` (cascata) |
| `CHATGPT_BRIDGE_URL` | `http://chatgpt-bridge:10531/v1` | URL interna do sidecar |
| `CHATGPT_BRIDGE_MODEL` | `gpt-image-2` | Modelo de imagem |
| `GOOGLE_API_KEY` | — | Fallback Gemini Imagen |

## Refresh do token

O bridge faz refresh automatico do OAuth. Se o token expirar (raro), repita o
passo 1 + 2 acima.

## Troubleshooting

```bash
# Ver logs do bridge
docker-compose logs -f chatgpt-bridge

# Inspecionar o auth.json no volume
docker run --rm -v codex_auth:/data alpine cat /data/auth.json | jq

# Forcar gerar imagem so via Gemini (bypass bridge)
IMAGE_GEN_PROVIDER=gemini docker-compose up
```
