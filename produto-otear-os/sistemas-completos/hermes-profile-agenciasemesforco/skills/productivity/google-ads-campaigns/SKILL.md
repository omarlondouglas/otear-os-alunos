---
name: google-ads-campaigns
description: "Use when querying Google Ads campaigns or MCP credentials."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [google-ads, advertising, gaql, mcp, campaigns, marketing]
    related_skills: [mcp-server-integration, hermes-agent]
---

# Google Ads — Consulta e Gestão de Campanhas

## When to Use

- Consultar campanhas, métricas, orçamentos ou palavras-chave do Google Ads
- Descobrir IDs de contas Google Ads acessíveis
- Descobrir campos GAQL de um recurso antes de montar uma query
- Configurar/ativar credenciais do MCP `google-ads` (developer token, ADC,
  login customer ID)
- Pausar/criar/alterar campanhas (via API direta, mutações)

MCP `google-ads` registrado no Hermes (stdio via `uvx`, server oficial
`googleads/google-ads-mcp`). Ferramentas disponíveis em **nova sessão** após
adição (prefixo `mcp_google_ads_`):

| Ferramenta | Uso |
|---|---|
| `mcp_google_ads_customers_list_accessible_customers` | Descobrir IDs de contas acessíveis. Chamar SEMPRE primeiro. |
| `mcp_google_ads_metadata_get_resource_metadata` | Campos selecionáveis/filtráveis de um recurso (ex.: `campaign`). Chamar ANTES de montar GAQL — nunca adivinhar campos. |
| `mcp_google_ads_search_search` | Executar consultas GAQL (métricas, orçamentos, status). |

**O MCP é somente leitura** (readOnlyHint). Criar/pausar/alterar campanhas,
anúncios, orçamentos → usar Google Ads API direta (biblioteca `google-ads`
Python), ver secção MUTAÇÕES.

## Configuração registrada (D:\Hermes\config.yaml, mcp_servers.google-ads)

```yaml
command: uvx
args:
  - --from
  - git+https://github.com/googleads/google-ads-mcp.git
  - google-ads-mcp

# Nota: o servidor atual exige FastMCP >=4.0.3. Não adicionar o pin antigo
# `fastmcp<4`, pois ele torna as dependências incompatíveis.
env:
  GOOGLE_ADS_DEVELOPER_TOKEN: ${MCP_GOOGLE_ADS_DEVELOPER_TOKEN}
  GOOGLE_ADS_LOGIN_CUSTOMER_ID: ${MCP_GOOGLE_ADS_LOGIN_CUSTOMER_ID}
  GOOGLE_APPLICATION_CREDENTIALS: C:/Users/marlo/AppData/Roaming/gcloud/application_default_credentials.json
connect_timeout: 180
```

Segredos ficam em `D:\Hermes\.env` (nunca em config.yaml): as chaves
`MCP_GOOGLE_ADS_DEVELOPER_TOKEN` e `MCP_GOOGLE_ADS_LOGIN_CUSTOMER_ID`
já estão lá (vazias até preencher).

## ATIVAR CREDENCIAIS (runbook)

São 3 peças; o servidor já sobe e descobre ferramentas sem nenhuma delas
(credenciais só são lidas na chamada de tool).

1. **Developer token** — Google Ads (conta gerente) → Ferramentas e
   configurações → Central de API (API Center). Token de 22 chars. Token
   novo começa com acesso "Conta de teste" (só funciona em contas de teste);
   produção precisa de nível **Explorer** (pode ser auto-upgrade — verificar
   na Central de API). Preencher em `D:\Hermes\.env`:
   `MCP_GOOGLE_ADS_DEVELOPER_TOKEN=...`
2. **OAuth/ADC** — o arquivo
   `C:/Users/marlo/AppData/Roaming/gcloud/application_default_credentials.json`
   existe mas o refresh token estava EXPIRADO em 2026-08-31 (invalid_grant).
   Re-autenticar com escopo adwords:
   ```bash
   gcloud auth application-default login \
     --scopes=https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform
   ```
   **Pitfall:** o gcloud CLI NÃO está instalado (PATH tem
   `/d/google/google-cloud-sdk/bin` mas a pasta não existe). Instalar via
   winget `google.cloudsdk` OU usar um client OAuth desktop próprio
   (refresh_token flow com escopo `https://www.googleapis.com/auth/adwords`)
   e gravar o JSON no mesmo caminho ADC.
3. **(Opcional) Login Customer ID** — só se o acesso à conta for via conta
   gerente (MCC): ID de 10 dígitos SEM hifens da gerente em
   `MCP_GOOGLE_ADS_LOGIN_CUSTOMER_ID`.

Também ativar a Google Ads API no projeto GCP (console.cloud.google.com →
APIs → `googleads.googleapis.com`). Projeto atual do gcloud config:
`chat-do-whatsapp`.

### Verificação (após preencher credenciais)

```bash
hermes mcp test google-ads          # deve conectar e listar 3 tools
```
Depois, numa sessão nova: pedir "liste os customers acessíveis" → deve
retornar IDs. Se vier `DEVELOPER_TOKEN_PERMISSION_DENIED` → token ainda é
test-account. Se `USER_PERMISSION_DENIED` → ADC sem acesso à conta.

## GAQL — receitas prontas (tool `search_search`)

`customer_id` sempre como string de 10 dígitos SEM hifens (123-456-7890 →
1234567890). Datas YYYY-MM-DD com traços, intervalos finitos.

- **Campanhas ativas:** fields `campaign.id,campaign.name,campaign.status`,
  resource `campaign`, conditions `["campaign.status = 'ENABLED'"]`
- **Performance 30d:** fields `campaign.id,campaign.name,metrics.clicks,metrics.impressions,metrics.cost_micros`
  (confirmar nomes via metadata tool), conditions
  `["metrics.impressions > 0", "segments.date DURING LAST_30_DAYS"]`
- **Cuidado com segmentos:** incluir `segments.date` na lista de fields cria
  uma linha por dia por campanha — cuidado ao agregar.
- **Orçamentos:** resource `campaign_budget`, fields
  `campaign_budget.id,campaign_budget.name,campaign_budget.amount_micros,campaign_budget.status`
- **Palavras-chave:** resource `ad_group_criterion` (fields via metadata),
  conditions tipo `["ad_group_criterion.status = 'ENABLED'"]`

Regras de ouro: (1) `metadata_get_resource_metadata` antes de qualquer
query nova; (2) `limit` durante exploração; (3) segmentos multiplicam
linhas; (4) custos vêm em micros (dividir por 1.000.000 para BRL).

## MUTAÇÕES (criar/pausar/alterar — API direta)

MCP não muta. Para operações reais usar `uv run --with google-ads python`
ou script no venv do projeto com `google-ads`:

```python
from google.ads.googleads.client import GoogleAdsClient
client = GoogleAdsClient.load_from_env()  # GOOGLE_ADS_* no ambiente
# pausar campanha: CampaignService.mutate_campaigns com
# operation.update.campaign.status = PAUSED e update_mask campaign.status
```

Segurança: testar em conta de teste primeiro; mutações têm efeito real de
gasto/veiculação; nunca logar tokens. Campanhas de vídeo (line-item) não
suportam mutação via API — usar Performance Max/Demand Gen p/ vídeo.

## Pitfalls

- **Dependências do servidor**: o repositório atual exige FastMCP >=4.0.3;
  não usar os pins antigos `fastmcp<4` ou `mcp<2`.
- **PYTHONPATH**: o terminal do Hermes pode injetar o venv dele no PYTHONPATH,
  contaminando subprocessos `uvx` (ImportError rpds). Hermes filtra o ambiente
  dos MCP servers, mas em testes manuais via terminal usar `env -u PYTHONPATH uvx ...`.
- **Nova sessão necessária** para as ferramentas aparecerem após add/test.
- Token vazio em `.env` → erro de credencial na chamada (não no boot) —
  comportamento esperado até preencher.
- `gcloud` não instalado (PATH aponta pra pasta inexistente) — ver runbook item 2.
- **Erro "This is mcp 2.x"** → pins faltando nos args do uvx.
- **Erro "FastMCP server support is not installed"** → fastmcp 4 beta instalado; aplicar pins.
- ADC `invalid_grant` no refresh → re-autenticar (runbook item 2), não é erro de config.
- **Erro "Cannot connect to (host, port)"** ao usar streamable-http: não usar `httpUrl`; a config stdio/uvx registrada é a correta para setup local.