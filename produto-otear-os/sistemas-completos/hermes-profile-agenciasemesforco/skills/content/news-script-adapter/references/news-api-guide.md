# News API — Guia de Uso

## Chave

`NEWS_API_KEY=4102fa76d3e6430b893bc272c6225fb3`

## Endpoints e Comportamento

### `top-headlines` — ✅ Funciona no plano gratuito

Retorna artigos reais. Use para buscar notícias gerais.

```
curl -s "https://newsapi.org/v2/top-headlines?apiKey=KEY&category=technology&pageSize=10"
curl -s "https://newsapi.org/v2/top-headlines?apiKey=KEY&q=AI+artificial+intelligence&pageSize=10"
```

### `everything` — ⚠️ Comportamento inconsistente no plano gratuito

- Queries genéricas (ex: `q=AI+business`) retornam `totalResults: N` mas `articles: []`
- Queries específicas com OR funcionam: `q=OpenAI+OR+Anthropic+OR+Google+AI+OR+DeepSeek`
- Queries com muitas palavras-chave específicas funcionam: `q=AI+agent+enterprise+value+ROI+automation`
- **Regra:** se `articles` voltar vazio mas `totalResults > 0`, refaça a query com termos mais específicos usando OR

## Padrão Recomendado (execute_code)

```python
import urllib.request, json

KEY = "4102fa76d3e6430b893bc272c6225fb3"

# Tentar everything primeiro (mais resultados)
url = f"https://newsapi.org/v2/everything?apiKey=KEY&q=AI+agent+business+automation&sortBy=publishedAt&pageSize=10"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())

if not data.get('articles'):
    # Fallback: top-headlines
    url = f"https://newsapi.org/v2/top-headlines?apiKey=KEY&category=technology&pageSize=10"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

for a in data.get('articles', []):
    print(f"[{a['publishedAt'][:10]}] {a['title']} | {a['source']['name']}")
```

## Queries que Funcionam Bem

| Query | Uso |
|-------|-----|
| `q=AI+agent+enterprise+OR+business` | Notícias de IA empresarial |
| `q=OpenAI+OR+Anthropic+OR+Google+AI+OR+DeepSeek` | Lançamentos de big techs |
| `q=AI+automation+productivity+2026` | Produtividade com IA |
| `category=technology&pageSize=10` | Top tech headlines |

## Limitações Conhecidas

- **Rate limit:** ~100 requests/dia no plano gratuito
- **Sem pipe no terminal:** `curl | python3 -c` pode travar. Salve em arquivo primeiro (`> /tmp/news.json`) e depois leia com `read_file` ou `execute_code`
- **IP da VPS:** O IP alemão (49.13.218.249) pode ter saída lenta para newsapi.org. Use `timeout=20` no curl
