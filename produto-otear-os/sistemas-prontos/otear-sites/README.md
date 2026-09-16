# Otear Sites

Sistema pronto do Otear OS para criar paginas de conversao.

## Pipeline

```text
briefing -> escopo -> pesquisa -> copy -> design -> imagens -> build -> integracoes -> QA -> publicacao/versionamento
```

## Componentes

| Pasta | Uso |
|---|---|
| `agents/` | agentes especialistas |
| `tasks/` | tarefas operacionais |
| `workflows/` | pipelines prontos |
| `squad.yaml` | manifesto do sistema |

## Entrada minima

```yaml
negocio: ""
produto_ou_servico: ""
publico: ""
objetivo_da_pagina: ""
oferta: ""
cta: ""
referencia_visual: ""
integracoes: ""
```

## Saida esperada

- briefing e escopo;
- pesquisa e referencias;
- copy por secao;
- direcao visual;
- estrutura da pagina;
- especificacao de integracoes;
- checklist de SEO/acessibilidade;
- plano de publicacao.

