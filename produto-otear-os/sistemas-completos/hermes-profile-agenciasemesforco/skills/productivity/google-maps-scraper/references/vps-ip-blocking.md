# VPS IP Blocking — Search Engines & Platforms

## IP da VPS

- **IP**: 49.13.218.249 (Hetzner, Alemanha)
- **Tipo**: Datacenter (não residencial)
- **Detectado por**: Google, YouTube, Bing, Brave, DuckDuckGo

## Plataformas bloqueadas (confirmado 2026-06-20)

| Plataforma | Comportamento | Contorno? |
|---|---|---|
| Google Maps | Redirect para consentimento, nunca aceita | Não (sem proxy residencial) |
| Google Search | CAPTCHA infinito | Não |
| YouTube (navegação) | Redirect para consentimento | Invidious API funciona |
| YouTube (transcripts) | **Funciona** via yt-dlp | — |
| Bing | CAPTCHA / Cloudflare challenge | Não |
| Brave Search | Verificação de bot | Não |
| DuckDuckGo | CAPTCHA | Não |
| Invidious | **Funciona** (pode variar por instância) | Múltiplas instâncias disponíveis |
| Jina Reader | **Funciona** | — |
| Exa Search | **Funciona** (via mcporter) | — |
| Foursquare API | **Funciona** | — |
| OpenStreetMap/Overpass | **Funciona** | — |

## Alternativas que funcionam

1. **Jina Reader** — `curl https://r.jina.ai/URL` — lê qualquer página
2. **Exa Search** — busca semântica via mcporter (instalado em /root/Agent-Reach/.venv)
3. **Invidious** — `curl https://inv.nadeko.net/api/v1/search?q=termo`
4. **Foursquare Places API** — POI data, free tier
5. **OpenStreetMap/Overpass** — dados geográficos abertos
6. **CNPJ.ws / QIAPI** — dados de empresas brasileiras

## Agent Reach (instalado)

- Venv: `/root/Agent-Reach/.venv/`
- 7/13 canais funcionando (GitHub, YouTube transcripts, V2EX, RSS, Exa search, Jina web, B站)
- 6 canais precisam de login: Twitter, Reddit, 小红书, 小宇宙, 雪球, LinkedIn
- Twitter precisa de Cookie do x.com (exportar via plugin Cookie-Editor)
