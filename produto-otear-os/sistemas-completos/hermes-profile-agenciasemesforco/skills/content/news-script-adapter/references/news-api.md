# News API — newsapi.org

## Credencial

- **Key:** `4102fa76d3e6430b893bc272c6225fb3`
- **Header:** `apiKey` (query param) — NÃO usa header `Authorization`

## Endpoints que funcionam no plano gratuito

### `top-headlines` — ✅ Funciona, retorna artigos completos

```
curl -s "https://newsapi.org/v2/top-headlines?apiKey=KEY&category=technology&pageSize=10"
curl -s "https://newsapi.org/v2/top-headlines?apiKey=KEY&q=AI+artificial+intelligence&pageSize=10"
```

- `category=technology` retorna ~70 resultados
- `q=` aceita query simples
- Retorna artigos com `title`, `description`, `url`, `urlToImage`, `publishedAt`, `content` (truncado)

### `everything` — ⚠️ Comportamento inconsistente no free tier

- Queries genéricas como `q=AI+business` retornam `totalResults: N` mas `articles: []` (vazio)
- Queries **específicas** (nomes de empresas, produtos) funcionam:
  ```
  q=OpenAI+OR+Anthropic+OR+Google+AI+OR+DeepSeek
  q=Claude+Code+OR+Cursor+OR+Replit+OR+Windsurf
  q=agentic+AI+enterprise
  ```
- `sortBy=publishedAt` para mais recentes
- `language=en` ou `language=pt` (PT tem bem menos resultados)

## Padrão de uso correto (evitar timeouts)

**NUNCA** pipe curl direto para `python3 -c` — causa timeout/block no Hermes.

```bash
# ✅ CORRETO: salvar em arquivo primeiro
curl -s --max-time 20 "https://newsapi.org/v2/top-headlines?apiKey=KEY&category=technology&pageSize=10" > /tmp/news.json

# Depois processar
python3 -c "
import json
with open('/tmp/news.json') as f:
    data = json.load(f)
for a in data.get('articles', []):
    print(a['publishedAt'][:10], '|', a['title'])
"
```

```bash
# ❌ ERRADO: pipe direto (causa timeout)
curl -s "URL" | python3 -c "import json,sys; ..."
```

## Queries recomendadas para IA/negócios

```bash
# Top tech headlines (melhor para fallback geral)
curl -s "https://newsapi.org/v2/top-headlines?apiKey=KEY&category=technology&pageSize=10"

# Específicas (everything, queries com nomes próprios)
curl -s "https://newsapi.org/v2/everything?apiKey=KEY&q=OpenAI+OR+Anthropic+OR+Google+DeepMind+OR+DeepSeek+OR+Mistral&sortBy=publishedAt&pageSize=10"

# Agentic AI / enterprise
curl -s "https://newsapi.org/v2/everything?apiKey=KEY&q=agentic+AI+enterprise+business&sortBy=publishedAt&pageSize=10"

# Português (poucos resultados)
curl -s "https://newsapi.org/v2/everything?apiKey=KEY&q=IA+inteligencia+artificial+negocios&language=pt&sortBy=publishedAt&pageSize=10"
```

## Limitações conhecidas

- Free tier: 100 requests/dia
- `content` vem truncado (~200 chars + "[+N chars]")
- `everything` com queries genéricas retorna articles vazio (bug/limitação do free tier)
- Sem acesso a corpo completo do artigo (só o snippet)
- Rate limit: 429 se exceder

## Quando usar no fluxo

1. Supabase vazio → News API `top-headlines` (category=technology)
2. Precisa de algo mais específico → News API `everything` (queries com nomes próprios)
3. Sem resultado → Hacker News Algolia (fallback 2, ver `hn-algolia-fallback.md`)
