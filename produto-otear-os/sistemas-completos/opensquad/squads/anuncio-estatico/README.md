# Anúncio Estático — Meta Ads

🎯 Squad que cria anúncios estáticos (imagem + copy) para Meta Ads. Produz headline, corpo, CTA e design visual em HTML/CSS pronto para renderizar.

## Pipeline

```
[CHECKPOINT Brief] → Copywriter → [CHECKPOINT Copy] → Designer → Revisor → [CHECKPOINT Final]
```

| # | Etapa | O que faz |
|---|-------|-----------|
| 1 | **checkpoint-brief** | Usuário define produto, público, objetivo, oferta |
| 2 | **copywriter** | Escreve headline, corpo e CTA seguindo tom de voz |
| 3 | **checkpoint-copy** | Aprovação textual antes de partir para o visual |
| 4 | **designer** | Cria layout HTML/CSS do anúncio |
| 5 | **revisor** | Valida copy + design contra critérios de qualidade |
| 6 | **checkpoint-final** | Aprovação final |

Em caso de rejeição no step 5, volta para o step 2 (`on_reject: revisor → copywriter`).

## Output

- `output/copy.md` — headline + corpo + CTA
- `output/anuncio.html` — design final renderizável
- `output/anuncio.jpg` — imagem renderizada (via skill `image-creator`)

## Knowledge base

Squad alimentado por dados especializados em `pipeline/data/`:

- `research-brief.md` — briefing de pesquisa
- `domain-framework.md` — framework de copy (AIDA, PAS, etc.)
- `quality-criteria.md` — critérios de qualidade
- `output-examples.md` — exemplos de anúncios de alta performance
- `anti-patterns.md` — padrões a evitar
- `tone-of-voice.md` — tom de voz da marca

## Skills usadas

- `web_search` — pesquisa de produto/concorrência
- `web_fetch` — análise de landing pages

## Como rodar

```bash
/opensquad run anuncio-estatico
```

## Estrutura

```
anuncio-estatico/
├── squad.yaml
├── agents/
│   ├── copywriter.agent.md
│   ├── designer.agent.md
│   └── revisor.agent.md
├── pipeline/
│   ├── pipeline.yaml
│   ├── steps/              # 6 steps
│   └── data/               # Knowledge base do domínio
├── _memory/                # Memória persistente
└── output/                 # Anúncios gerados
```

## Customização

- Tom de voz da marca: `pipeline/data/tone-of-voice.md`
- Estilo visual: `agents/designer.agent.md`
- Frameworks de copy preferidos: `pipeline/data/domain-framework.md`

## Uso típico

1. Brief com produto + oferta + público
2. Copywriter entrega 1-3 variações de copy
3. Aprovação textual
4. Designer monta o visual
5. Revisor valida
6. Render final em JPG pronto para subir no Ads Manager
