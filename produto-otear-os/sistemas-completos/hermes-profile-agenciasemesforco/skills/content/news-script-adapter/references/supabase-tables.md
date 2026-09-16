# O Tear — Supabase Data Sources

## Conexão

- **Projeto:** O Tear CRM (Supabase)
- **URL:** `https://jrkuuusrjzzpdjkulvmf.supabase.co`
- **Auth:** `service_role` key (via `Authorization` e `apikey` headers)
- **Chave está em:** memória do Hermes (variável de ambiente / credencial salva)

> O Project Ref pode mudar se o projeto for recriado. Se o DNS não resolver, peça o URL atual ao usuário e atualize a memória.

## Padrão de Query (Python — recomendado)

**NUNCA use `curl | python3 -c`** com chaves JWT no shell — os caracteres especiais (`.`, `-`, `_`) quebram o quoting. Use Python com `urllib`:

```python
import urllib.request, json

SUPABASE_URL = "https://jrkuuusrjzzpdjkulvmf.supabase.co"
SUPABASE_KEY = "eyJ..."  # service_role key da memória

url = f"{SUPABASE_URL}/rest/v1/{tabela}?order=created_at.desc&limit=10"
req = urllib.request.Request(url, headers={
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
```

Alternativa: salve a chave em arquivo e use `bash script.sh`.

## Tabelas de Conteúdo

### `noticias`
Notícias principais, geralmente inseridas manualmente ou via scraper.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | uuid | PK (UUID, não integer) |
| `titulo` | text | Título da notícia |
| `resumo` | text | Resumo/descrição curta |
| `conteudo` | text | Corpo completo (pode ser null) |
| `url` | text | Link original |
| `categoria` | text | Categoria (ex: `ia`) |
| `tags` | array/text | Tags (ex: `["nvidia","agentes","automacao"]`) |
| `fonte` | text | Nome do veículo/origem |
| `publicado_em` | timestamptz | Data de publicação (usar para ordenar) |
| `created_at` | timestamptz | Quando foi inserida no banco |

> ⚠️ **Schema mudou:** a tabela `noticias` agora usa UUID, tem `resumo`, `categoria`, `tags` e `publicado_em` (não só `created_at`). A coluna `conteudo` pode ser null — use `resumo` como fallback.

### `noticias_perplexity`
Notícias coletadas via consulta ao Perplexity AI.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | integer | PK |
| `headline` | text | Título da notícia (NÃO `titulo`/`tema`) |
| `resumo` | text | Resumo (NÃO `conteudo`) |
| `fonte` | text | Origem |
| `data_criacao` | timestamptz | Data de criação (NÃO `created_at`) |
| `data_atualizacao` | timestamptz | Data de atualização |

> ⚠️ **Schema diferente do documentado:** usar `headline` (não `titulo`), `resumo` (não `conteudo`), `data_criacao` (não `created_at`).

### `posts_do_reddit`
Posts de subreddits monitorados.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | integer | PK |
| `titulo` | text | Título do post |
| `url` | text | Link para o post |
| `resumo` | text | Corpo do post / selftext |
| `updates_engagement` | text | Métrica de engajamento |
| `date` | text | Data (string, não timestamptz) |

> ⚠️ **Sem `created_at`:** usar `date` para ordenação. Sem coluna `subreddit` nem `conteudo`.

### `videos_do_youtube`
Metadados de vídeos recentes de canais monitorados.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | integer | PK |
| `titulo` | text | Título do vídeo |
| `descricao` | text | Descrição |
| `canal` | text | Nome do canal (pode ser vazio) |
| `nome_do_canal` | text | Nome do canal (alternativo, pode ser vazio) |
| `url` | text | Link do YouTube (pode ser vazio) |
| `link_do_video` | text | Link do YouTube (alternativo) |
| `url_da_thumb` | text/array | URL da thumbnail (pode ser objeto JSON) |
| `resumo_rapido` | text | Resumo curto do vídeo |
| `resumo_detalhado` | text | Resumo detalhado com bullets |
| `views` | integer | Número de views (pode ser 0 ou null) |
| `created_at` | timestamptz | Quando foi inserido |
| `updated_at` | timestamptz | Quando foi atualizado |

> ✅ Esta tabela funcionou corretamente. `canal`, `nome_do_canal`, `url`, `link_do_video` podem vir vazios. `views` pode ser 0. `url_da_thumb` pode vir como objeto JSON `[{"url": "..."}]`. Use `resumo_rapido` para conteúdo resumido e `resumo_detalhado` para análise completa com bullets.

### `ideias_de_conteudo`
Ideias geradas por curadoria ou brainstorming.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | integer | PK |
| `idea_title` | text | Título da ideia (NÃO `ideia`) |
| `description` | text | Descrição completa |
| `porque` | text | Justificativa/motivo da ideia |

> ⚠️ **Sem `created_at`, `tema`:** usar `idea_title` (não `ideia`), `description` (não conteúdo genérico).

## Fluxo de Dados

```
Supabase (fontes)
  ├─ noticias ─────────────┐
  ├─ noticias_perplexity ───┤
  ├─ posts_do_reddit ───────┤
  ├─ videos_do_youtube ─────┤
  └─ ideias_de_conteudo ────┤
                            ▼
              news-script-adapter
              (roteiro no formato escolhido)
                            ▼
                   ClickUp (Tiktok list)
                   status: concept
```

## Troubleshooting

- **NXDOMAIN / host not found:** O Project Ref mudou ou o projeto foi recriado. Peça ao usuário o novo Supabase Project URL e atualize a memória.
- **401 Unauthorized:** A chave `service_role` expirou ou foi rotacionada. Peça nova chave ao usuário.
- **400 Bad Request:** A query está referenciando colunas que não existem mais. Verifique o schema atual desta referência antes de montar a query. As tabelas mudaram de schema ao longo do tempo — **sempre teste sem `order` primeiro** (`?limit=3`) para ver o retorno cru antes de adicionar ordenação.
- **Tabela vazia:** A fonte correspondente pode não ter novos itens ainda. Tente puxar de outra tabela ou buscar notícias frescas na web.
