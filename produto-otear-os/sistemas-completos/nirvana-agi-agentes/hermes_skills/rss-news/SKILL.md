---
name: rss-news
description: "Busca noticias recentes via RSS pelo backend do O Tear e estrutura a melhor noticia como roteiro curto."
version: 1.1.0
author: O Tear
license: MIT
metadata:
  hermes:
    tags: [otear, news, rss, script, research]
    category: content
---

# rss-news

## Quando usar

Use esta skill quando o usuario pedir:

- noticias recentes sobre um tema
- pesquisa via RSS
- pauta baseada em noticia atual
- noticia estruturada como roteiro
- roteiro curto para TikTok, Reels, Shorts ou carrossel narrado

Esta skill nao salva dados. Ela apenas busca noticias e devolve uma estrutura de roteiro para o Hermes usar.

## Contrato

O script chama o backend do O Tear:

```text
GET {OTEAR_API_URL}/api/v1/news/feed?source=rss&search={query}&limit={limit}
X-API-Key: {OTEAR_API_KEY}
```

O backend busca no Google News RSS por padrao ou nos feeds configurados em `NEWS_RSS_FEEDS`.

## Variaveis

```env
OTEAR_API_URL=http://localhost:8000
OTEAR_API_KEY=...
OTEAR_TIMEOUT_S=30
```

## Instalar dependencias

```bash
pip install -r {SKILL_DIR}/requirements.txt
```

## Uso

Buscar noticias e devolver roteiro estruturado:

```bash
python {SKILL_DIR}/script.py "agentes de IA para vendas"
```

Buscar mais itens antes de escolher a principal:

```bash
python {SKILL_DIR}/script.py "IA no Brasil" --limit 50
```

Retornar apenas o JSON cru do feed, sem roteiro:

```bash
python {SKILL_DIR}/script.py "IA no Brasil" --format json
```

Validar URL sem chamar API:

```bash
python {SKILL_DIR}/script.py "agentes de IA" --dry-run
```

## Saida

O script imprime JSON em stdout.

Saida padrao:

```json
{
  "ok": true,
  "mode": "script",
  "query": "agentes de IA",
  "total": 10,
  "selected_news": {
    "title": "...",
    "source_label": "...",
    "url": "...",
    "published_at": "..."
  },
  "alternatives": [],
  "script_markdown": "# Roteiro baseado em noticia RSS..."
}
```

O campo mais importante para o Hermes e `script_markdown`.

## Procedimento para Hermes

1. Transforme o pedido do usuario em uma query curta e objetiva.
2. Execute `script.py`.
3. Leia `selected_news`, `alternatives` e `script_markdown`.
4. Se `selected_news` vier vazio, tente uma query mais ampla.
5. Reescreva ou refine o roteiro mantendo os fatos da fonte.
6. Nao invente fonte, URL, data ou resumo.

## Estrutura de roteiro

O roteiro segue este formato:

```md
## Angle

## Theme

## Primary Trigger

## Script
Hook:

Development:

Closing:

## On-Screen Editing

## Delivery Notes
```

## Cuidados

- Esta skill nao persiste dados.
- O roteiro e uma primeira estrutura. O Hermes pode adaptar tom, publico e formato depois.
- Nao use noticia antiga como "de hoje" sem checar `published_at`.
