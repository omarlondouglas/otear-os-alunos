# YouTube Thumbnail Creator

🎬 Squad que gera conceitos e prompts otimizados de IA para criar thumbnails de YouTube com alto CTR.

Não renderiza a thumbnail final — entrega o **prompt pronto** para usar em Midjourney, DALL·E, Gemini ou outro gerador de imagem.

## Pipeline

```
[CHECKPOINT Foco] → Researcher → Conceptor → [CHECKPOINT Conceito]
       ↓
Prompt Engineer → [CHECKPOINT Prompts] → Reviewer → [CHECKPOINT Final]
```

| # | Etapa | O que faz |
|---|-------|-----------|
| 1 | **research-focus** | Usuário define vídeo, tema e ângulo |
| 2 | **research** | Busca thumbnails de referência (canais de alto CTR) |
| 3 | **generate-concepts** | Gera 3-5 conceitos visuais distintos |
| 4 | **select-concept** | Usuário escolhe o conceito |
| 5 | **create-prompts** | Engenheira prompts otimizados (composição, lighting, expressão) |
| 6 | **approve-prompts** | Aprovação dos prompts |
| 7 | **review** | Reviewer valida contra critérios de CTR |
| 8 | **final-approval** | Entrega final |

Em caso de rejeição no step 7, volta para o step 5 (`on_reject: review → create-prompts`).

## Output

`output/thumbnail-prompts.md` com 1-N prompts prontos para colar no gerador de imagem de sua escolha.

## Knowledge base

Squad alimentado por dados especializados em `pipeline/data/`:

- `research-brief.md` — briefing de pesquisa
- `domain-framework.md` — framework do domínio (CTR psychology)
- `quality-criteria.md` — critérios de qualidade
- `output-examples.md` — exemplos de saída
- `anti-patterns.md` — padrões a evitar

## Investigação enriquecida

Squad foi criado com análise de perfil de referência (`_investigations/`) — padrões reais de thumbnails de alto CTR foram extraídos e injetados nos agentes.

## Skills usadas

- `web_search` — pesquisa de thumbnails de referência
- `web_fetch` — análise de páginas de vídeo

## Como rodar

```bash
/opensquad run yt-thumbnails
```

## Estrutura

```
yt-thumbnails/
├── squad.yaml
├── agents/
│   ├── researcher.agent.md
│   ├── conceptor.agent.md
│   ├── prompt-engineer.agent.md
│   └── reviewer.agent.md
├── pipeline/
│   ├── pipeline.yaml
│   ├── steps/              # 8 steps
│   └── data/               # Knowledge base do domínio
├── _investigations/        # Análises de perfis de referência
└── output/                 # Prompts gerados
```

## Performance mode

Este squad roda em `performance_mode: alta-performance` — usa modelo mais capaz para conceituação visual.
