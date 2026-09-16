# Notícias → Carrossel IA

📰 Squad que busca diariamente as notícias mais relevantes sobre IA, agentes e automação para agências digitais. Cria um carrossel completo com design HTML/CSS e publica no Instagram.

## Pipeline

```
[CHECKPOINT Tema] → Pesquisador → Estrategista → Redator → Designer
       ↓
[CHECKPOINT Imagens] → Curador → Conceituador Visual → Gerador IA → Image Patcher
```

| # | Etapa | O que faz |
|---|-------|-----------|
| 1 | **checkpoint-tema** | Usuário define o assunto |
| 2 | **pesquisador** | Busca notícias via Brave Search / Google News RSS |
| 3 | **estrategista** | Define ângulo, público-alvo e tom |
| 4 | **redator** | Escreve copy de cada slide (40-80 palavras) |
| 5 | **designer** | Gera `slides-data.json` com layout, temas e elementos |
| 6 | **checkpoint-imagens** | Aprovação antes de gerar imagens |
| 7 | **curador-imagens** | Reaproveita imagens do banco existente |
| 8 | **conceituador-visual** | Define conceito visual único por notícia |
| 9 | **gerador-imagens** | Gera imagens com Gemini API (1024x1024+) |
| 10 | **image-patcher** | Aplica imagens nos slides finais |

## Output

7-10 slides JPG (1080x1440) prontos para Instagram, salvos em `output/`.

## Skills usadas

- `web_search` — busca de notícias
- `web_fetch` — leitura de artigos completos

## Como rodar

```bash
/opensquad run noticias-carrossel-ia
```

Ou pela interface web em `http://localhost:3000`.

## Estrutura

```
noticias-carrossel-ia/
├── squad.yaml              # Config (pipeline, skills, autor)
├── agents/                 # 11 agentes (.agent.md)
├── pipeline/
│   ├── pipeline.yaml       # Ordem dos steps
│   ├── steps/              # Instruções de cada step
│   └── slide-template.html # Template HTML dos slides
├── _memory/                # Memória persistente do squad
├── _investigations/        # Análises de perfis Instagram
└── output/                 # Carrosseis gerados
```

## Customização

- Editar tom de voz: `agents/redator.agent.md`
- Editar design: `agents/designer.agent.md` + `agents/design-system.md`
- Trocar fontes de notícias: `agents/pesquisador.agent.md`
