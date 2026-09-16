# Instagram Carousel Scraper

📸 Squad de pesquisa que entra no Instagram com sessão persistente (Playwright), navega até um perfil, identifica os carrosséis mais recentes e baixa todas as imagens dos slides.

Usado para análise de referências visuais e estudo de conteúdo de perfis concorrentes.

## Pipeline

```
[CHECKPOINT Perfil] → Scraper (Playwright)
```

| # | Etapa | O que faz |
|---|-------|-----------|
| 1 | **checkpoint-perfil** | Usuário informa o @username do Instagram |
| 2 | **scraper** | Abre browser, navega ao perfil, identifica carrosséis e baixa todas as imagens |

## Output

Imagens organizadas por post em `output/{username}/{post-id}/slide-N.jpg` + relatório `output/report.md`.

## Sessão persistente

Reutiliza o perfil de browser global em `_opensquad/_browser_profile/`. Primeira execução exige login manual; runs seguintes reaproveitam a sessão.

> **Importante:** o plugin nativo do Playwright no Claude Code precisa estar desabilitado. O Opensquad usa o `@playwright/mcp` próprio configurado em `.mcp.json`.

## Como rodar

```bash
/opensquad run instagram-scraper
```

Ou pela interface web (botão "Analisar perfil").

## Estrutura

```
instagram-scraper/
├── squad.yaml              # Config (pipeline minimalista)
├── _scraper.js             # Implementação Playwright headless
├── _debug.js               # Helper de debug
├── agents/
│   └── scraper.agent.md    # Persona + instruções
├── pipeline/
│   ├── pipeline.yaml
│   └── steps/              # checkpoint-perfil + scraper
├── _investigations/        # Histórico de perfis analisados
└── output/                 # Imagens baixadas
```

## Uso típico

1. Apontar para um perfil de referência (ex: `@aiagencyhq`)
2. Scraper baixa os últimos N carrosséis
3. Imagens viram input para análise visual em `cover-director` ou enriquecem o `_memory/` de outros squads

## Limites

- Respeita rate-limit do Instagram (não fazer scraping massivo)
- Apenas perfis públicos ou contas que você segue
- Login pode expirar — refazer manualmente no profile persistente
