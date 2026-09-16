# Hacker News Algolia API — Fallback para notícias de IA

## Por que usar

Quando o Supabase (O Tear CRM) estiver vazio, o HN Algolia é a fonte mais rápida e rica para encontrar notícias quentes de IA/tech com relevância comprovada (pontuação da comunidade).

## Queries padrão

### Top stories gerais (todas as áreas)
```bash
curl -s "https://hn.algolia.com/api/v1/search?tags=story&hitsPerPage=50"
```

### AI e tecnologia (recomendado — tema do cliente)
```bash
curl -s "https://hn.algolia.com/api/v1/search?query=AI+OR+LLM+OR+agent+OR+artificial+intelligence&tags=story&hitsPerPage=30"
```

### Empresas/modelos específicos
```bash
curl -s "https://hn.algolia.com/api/v1/search?query=OpenAI+OR+Anthropic+OR+Google+AI+OR+DeepSeek&tags=story&hitsPerPage=20"
```

### Por recência (numericFilters com timestamp Unix)
```bash
# Últimos 7 dias (timestamp aproximado: data_atual - 604800)
curl -s "https://hn.algolia.com/api/v1/search?query=AI&tags=story&numericFilters=created_at_i>1749513600&hitsPerPage=20"
```

### Alto impacto (mais pontos)
```bash
curl -s "https://hn.algolia.com/api/v1/search?tags=story&hitsPerPage=100"
```
Depois filtre localmente: points >= 10, data >= 30 dias.

## Processamento dos resultados

Cada hit do HN retorna:
- `title` — título da notícia (usar como manchete)
- `points` — votos (quanto maior, mais relevante)
- `created_at` — data ISO
- `url` — link original
- `objectID` — ID único (útil para dedup)

Pipeline de filtragem em Python:
```python
import json, sys
d = json.load(sys.stdin)
for h in d.get('hits', []):
    t = h.get('title', '')
    dt = h.get('created_at', '')[:10]
    p = h.get('points', 0)
    if dt >= '2026' and p >= 5:
        # manter apenas temas conectáveis a IA para negócios
        ai_keywords = ['ai','llm','model','openai','anthropic','google','agent','gpt','claude','deepseek','gemini','data center','nvidia','gpu','inference','training']
        if any(kw in t.lower() for kw in ai_keywords):
            print(f'{dt} | {p}pts | {t}')
```

## Limitações

- HN é focado em tech inglês — notícias em português podem ser raras
- Alguns links são blocked paywall (CNBC, Bloomberg) — pule ou busque texto via visão geral
- O timestamp `numericFilters` com `created_at_i` pode falhar se o timestamp for futuro — use sem ele como fallback