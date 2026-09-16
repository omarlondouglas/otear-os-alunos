---
name: google-maps-scraper
description: "Busca empresas/negócios no Google Maps via browser automation. Extrai nome, telefone, endereço, website, rating e reviews. Salva resultados em CSV e JSON."
version: "1.0.0"
metadata:
  hermes:
    tags: [scraper, google-maps, leads, prospeccao, negocios]
---

# Google Maps Scraper

Busca empresas no Google Maps via Playwright (script Python standalone). Não precisa de API key — navega direto no site.

## ⚠️ REQUISITO CRÍTICO: IP Residencial

**O Google Maps bloqueia IPs de datacenter (VPS, cloud).** Se o servidor tem IP não-residencial, o scraping **não funciona** — nem com browser tool, nem com Playwright, nem com cookies injetados. O Google redireciona para `consent.google.com` e nunca aceita o consentimento automaticamente.

**Antes de começar, verifique:** o servidor tem IP residencial? Se for VPS/cloud (AWS, GCP, DigitalOcean, Hetzner, etc.), o scraping vai falhar. Nesse caso, rode o script na máquina local do usuário.

## Quando usar

- "Busca restaurantes em São Paulo"
- "Encontra dentistas no Rio de Janeiro"
- "Lista salões de beleza em Belo Horizonte"
- "Faz uma lista de leads de [tipo] em [cidade]"
- Qualquer pedido de busca de negócios locais

## Fluxo de operação

### 1. Verificar ambiente

Confirmar que o servidor tem IP residencial. Se não tiver, pedir ao usuário para rodar localmente:

> "O Google Maps bloqueia IPs de datacenter. Você pode rodar o script na sua máquina local — o arquivo está em `/root/prospect/scraper_v2.py`. Instale as dependências com `pip install playwright pyyaml` e rode `python scraper_v2.py 'termo' 'cidade' [limite]`."

### 2. Rodar o script standalone

O script em `scripts/scraper.py` (ou `/root/prospect/scraper_v2.py`) usa Playwright com:
- `locale: pt-BR` e `timezone: America/Sao_Paulo`
- User-agent rotativo
- Delays humanos entre ações
- Scroll no feed para carregar resultados
- Extração de dados de cada listing

```bash
cd /root/prospect && /root/prospect/.venv/bin/python scraper_v2.py "termo" "cidade" [limite]
```

### 3. Script salva automaticamente

Os resultados são salvos em `/root/prospect/data/`:
- `leads_{termo}_{timestamp}.json`
- `leads_{termo}_{timestamp}.csv`

### 4. Reportar ao usuário

Mostrar quantidade de leads encontrados, arquivos salvos e resumo dos primeiros resultados.

## Dados extraídos por listing

- **Nome** → `h1`
- **Categoria** → `button[jsaction*='category']`
- **Rating** → `div.F7nice span[aria-hidden='true']`
- **Reviews** → `div.F7nice span[aria-label*='coment']` ou `aria-label*='review'`
- **Endereço** → `button[data-item-id='address']`
- **Telefone** → `button[data-item-id*='phone']`
- **Website** → `a[data-item-id='authority']`
- **URL do Maps** → href do listing

## Seletores CSS principais

| Dado | Seletor |
|------|---------|
| Feed de resultados | `div[role='feed']` |
| Links de listings | `div[role='feed'] a[href*='/maps/place/']` |
| Nome | `h1` |
| Categoria | `button[jsaction*='category']` |
| Rating | `div.F7nice span[aria-hidden='true']` |
| Reviews | `div.F7nice span[aria-label*='coment']` |
| Endereço | `button[data-item-id='address']` |
| Telefone | `button[data-item-id*='phone']` |
| Website | `a[data-item-id='authority']` |
| Fim da lista | `span.HlvSq` |

## Dicas e cuidados

- **Delays**: O Google pode bloquear se for muito rápido. Entre ações, esperar 2-5 segundos.
- **Scroll**: Scroll suave, não tudo de uma vez. Fazer 2-3 scrolls, esperar carregar, repetir.
- **Limite**: Recomendado máximo 50 resultados por sessão pra não levar bloqueio.
- **Erros**: Se o Google mostrar CAPTCHAs, parar e avisar o usuário.

## O que NÃO funciona (não tente)

- `browser_navigate` do Hermes para Google Maps em IP datacenter — sempre redireciona pra consentimento
- `browser_click` no botão "Aceitar" do consentimento — o clique não avança
- `browser_console` com JS para clicar botão ou injetar cookies — não funciona
- Playwright com `context.add_cookies()` em IP datacenter — o Google ignora os cookies e força consentimento baseado no IP
- Qualquer abordagem de scraping do Google Maps em IP não-residencial — simplesmente não funciona
- **Google Search** (`google.com/search`) também bloqueia com CAPTCHA em IP datacenter
- **YouTube** (`youtube.com`) — bloqueia navegação (browse/search) em IP datacenter com redirect para consentimento. **Exceção**: `yt-dlp` para extrair legendas/transcripts funciona normalmente (endpoint diferente)
- **Bing** (`bing.com/search`) — bloqueia com CAPTCHA em IP datacenter
- **Brave Search** (`search.brave.com`) — bloqueia com verificação de bot em IP datacenter
- **DuckDuckGo** (`html.duckduckgo.com`) — bloqueia com CAPTCHA em IP datacenter
- **Diretórios brasileiros** (Apontador, GuiaFacil) funcionam mas têm busca por segmento limitada e retornam resultados genéricos

## Alternativas de busca que funcionam em IP datacenter

- **Jina Reader** (`curl https://r.jina.ai/URL`) — lê qualquer página web, funciona de qualquer IP
- **Exa Search** (via mcporter) — busca semântica, funciona de qualquer IP (requer configuração mcporter)
- **Invidious** (instâncias públicas) — busca e watch do YouTube sem bloqueio (ex: `inv.nadeko.net`)
- **Foursquare Places API** — dados de POI, funciona de qualquer IP, free tier generoso
- **OpenStreetMap / Overpass API** — dados geográficos abertos, sem bloqueio
- **CNPJ.ws / QIAPI** — dados abertos de empresas brasileiras (CNPJ, razão social, telefone)

## Alternativas quando IP datacenter

1. **Rodar script localmente** (melhor opção) — `python scraper_v2.py "termo" "cidade"`
2. **Foursquare Places API** (tier gratuito, funciona de qualquer IP) — https://developer.foursquare.com
3. **Google Places API** (paga, mas confiável) — requer API key, ~$200/mês free tier
4. **Proxy residencial** (complexo e pago) — Bright Data, Oxylabs, etc.
5. **CNPJ.ws / QIAPI** — Dados abertos de empresas brasileiras (CNPJ, razão social, telefone), não depende de Google

## Lições aprendidas (sessão 2026-06-19)

- **IP 49.13.218.249 (Hetzner, Alemanha)** é bloqueado pelo Google para Maps e Search
- Cookies do Google (SID, HSID, SSID, NID, etc.) **não contornam** o bloqueio baseado em IP
- O Google Maps força `consent.google.com` para IPs de datacenter, independente de cookies
- O `browser_console` do Hermes não tem acesso ao CDP para injetar cookies antes da navegação
- O `browser_click` no botão "Alle akzeptieren" (consentimento em alemão) não funciona — a página não avança
- Playwright com `context.add_cookies(COOKIES)` injeta os cookies com sucesso (21 cookies), mas o Google ainda redireciona para consentimento
- **Conclusão**: não há como contornar o bloqueio de IP datacenter do Google Maps sem proxy residencial ou rodar em máquina local

## Arquivos de suporte

- `scripts/scraper.py` — Script standalone Playwright. Funciona em IPs residenciais. Uso: `python scraper.py "termo" "cidade" [limite]`
- `references/ip-blocking.md` — Documentação detalhada do bloqueio de IP datacenter e alternativas
- `references/vps-ip-blocking.md` — Referência rápida de plataformas bloqueadas/funcionais no IP atual da VPS (49.13.218.249)
