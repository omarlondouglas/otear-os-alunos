# Capabilities

Capabilities sao as habilidades estaveis do produto.

Esta pasta deve virar a camada entre a interface/orquestrador e as tools reais.
Por enquanto, as tools principais ainda vivem em `app/agents/agno_tools.py`.

## Habilidades planejadas

- `research`: pesquisa web, noticias, resumo de fontes e insights.
- `references`: entrada e analise de referencias de criadores, marcas, imagens e videos.
- `model_extraction`: extracao de voz, visual, hooks, estrutura narrativa e guias de estilo.
- `writing`: roteiros, copy, legendas, anuncios e reescrita em estilo.
- `creation`: carrossel, imagem, thumbnail, capa e revisao visual.
- `video`: transcricao, cortes, highlights, legendas, render e status de jobs.
- `memory`: preferencias, contexto de marca, assets salvos e aprendizados.

## Regra de arquitetura

```text
Interface/Chat
  -> Orchestrator
  -> Capability
  -> Tool/provider
  -> Resultado + logs + memoria
```

Agentes podem usar capabilities, mas o produto nao deve depender de nomes de agentes
para definir o que sabe fazer.

## Estado atual

- `registry.py` declara o mapa inicial das habilidades estaveis.
- Cada subpasta ja existe como ponto de entrada futuro para facades finos.
- Nenhuma tool antiga foi movida ainda; os facades devem chamar o legado aos poucos.
