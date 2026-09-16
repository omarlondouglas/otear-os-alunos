---
task: "Research Topic Context"
order: 1
input: |
  - research_focus: Tema do vídeo e estilo desejado pelo usuário
  - research_brief: Conhecimento base sobre thumbnails
output: |
  - topic_context: Resumo do tema, público, emoções associadas
  - niche_overview: Visão geral do cenário de conteúdo neste tema
---

# Research Topic Context

Pesquisar o contexto do tema do vídeo para entender o que o público espera e quais emoções estão associadas ao assunto.

## Process

1. Ler o tema do vídeo do research-focus.md
2. Pesquisar via web_search: "{tema} YouTube" — entender o volume e tipo de conteúdo existente
3. Pesquisar via web_search: "{tema} tendências 2026" — identificar o que é atual
4. Identificar: público-alvo do tema, emoções dominantes (medo, curiosidade, oportunidade), ângulos mais populares
5. Resumir em formato estruturado

## Output Format

```yaml
topic_context:
  theme: "..."
  target_audience: "..."
  dominant_emotions:
    - emotion: "..."
      intensity: high/medium/low
  current_trends:
    - "..."
  content_volume: high/medium/low
  competition_level: high/medium/low
```

## Output Example

```yaml
topic_context:
  theme: "IA substituindo programadores"
  target_audience: "Desenvolvedores, estudantes de tech, profissionais preocupados com automação"
  dominant_emotions:
    - emotion: "medo"
      intensity: high
    - emotion: "curiosidade"
      intensity: high
    - emotion: "oportunidade"
      intensity: medium
  current_trends:
    - "AI coding assistants como Cursor, Claude Code"
    - "Agentes autônomos que programam sozinhos"
    - "Debate sobre futuro das profissões tech"
  content_volume: high
  competition_level: high
```

## Quality Criteria

- [ ] Tema pesquisado com pelo menos 2 buscas web diferentes
- [ ] Emoções identificadas são específicas ao tema (não genéricas)
- [ ] Tendências são atuais (2025-2026)

## Veto Conditions

1. Contexto é puramente genérico sem conexão com o tema específico
2. Nenhuma emoção dominante identificada
