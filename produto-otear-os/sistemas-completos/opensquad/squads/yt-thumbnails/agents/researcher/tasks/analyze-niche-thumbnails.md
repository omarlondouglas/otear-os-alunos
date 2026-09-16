---
task: "Analyze Niche Thumbnails"
order: 2
input: |
  - topic_context: Contexto do tema pesquisado
  - research_brief: Conhecimento base sobre thumbnails
output: |
  - niche_analysis: Análise de thumbnails existentes no nicho
  - recommendations: Recomendações para a thumbnail
  - gaps: Oportunidades visuais identificadas
---

# Analyze Niche Thumbnails

Analisar thumbnails existentes no nicho do tema para identificar padrões visuais, o que funciona, e onde há oportunidade de diferenciação.

## Process

1. Pesquisar via web_search: "YouTube thumbnail {tema}" para encontrar análises de thumbnails do nicho
2. Pesquisar via web_search: "{tema} YouTube most viewed" para identificar vídeos de maior sucesso
3. Para os top 5-8 vídeos encontrados, analisar mentalmente as thumbnails baseado em títulos e descrições
4. Mapear padrões: cores mais usadas, tipo de composição, uso de texto, expressões faciais
5. Identificar o que os top performers fazem de diferente dos vídeos com menos views
6. Encontrar gaps — elementos visuais que ninguém usa mas que poderiam funcionar
7. Formular 3 recomendações específicas para esta thumbnail

## Output Format

```yaml
niche_analysis:
  patterns:
    colors: ["..."]
    composition: "..."
    text_usage: "..."
    facial_expressions: "..."
  top_references:
    - title: "..."
      views: "..."
      thumbnail_description: "..."
      why_it_works: "..."
  gaps:
    - "..."
  recommendations:
    - recommendation: "..."
      justification: "..."
```

## Output Example

```yaml
niche_analysis:
  patterns:
    colors: ["azul tech", "preto dramático", "vermelho urgência", "verde matrix"]
    composition: "Rosto em close + elemento tech ao lado, regra dos terços"
    text_usage: "2-3 palavras grandes, geralmente números ou palavras de impacto"
    facial_expressions: "Choque e surpresa dominam (4 de 6 top vídeos)"
  top_references:
    - title: "AI Will Replace 90% of Developers"
      views: "2.3M"
      thumbnail_description: "Rosto preocupado em close-up, fundo vermelho, texto grande '90%'"
      why_it_works: "Número específico cria urgência, expressão transmite medo real, vermelho reforça perigo"
    - title: "I Replaced My Dev Team with AI"
      views: "1.8M"
      thumbnail_description: "Split antes/depois — humanos vs robô, contraste de cores"
      why_it_works: "Visual storytelling instantâneo, antes/depois é fórmula comprovada"
    - title: "The TRUTH About AI Coding"
      views: "890K"
      thumbnail_description: "Close-up com código refletido nos óculos, fundo escuro, 'TRUTH' em amarelo"
      why_it_works: "Curiosity gap com 'TRUTH', reflexo nos óculos é criativo e tech"
  gaps:
    - "Ninguém usa estilo futurista/cyberpunk — todos são 'realistas'. Oportunidade de diferenciar"
    - "Poucos mostram a perspectiva positiva (oportunidade com IA) — maioria foca no medo"
  recommendations:
    - recommendation: "Usar expressão de CHOQUE em vez de medo"
      justification: "4 de 6 top thumbnails usam choque — gera mais curiosidade que medo"
    - recommendation: "Incluir elemento visual tech específico (código, terminal, IA)"
      justification: "Todos os top performers incluem contexto visual tech, não só rosto"
    - recommendation: "Testar abordagem futurista/neon como diferenciador"
      justification: "Gap identificado — 0 de 6 top vídeos usam estética cyberpunk"
```

## Quality Criteria

- [ ] Mínimo 3 thumbnails de referência analisadas em detalhe
- [ ] Padrões quantificados ("X de Y usam...")
- [ ] Pelo menos 1 gap/oportunidade identificada
- [ ] Recomendações justificadas com dados da análise

## Veto Conditions

1. Análise é puramente descritiva sem padrões identificados
2. Zero thumbnails de referência citadas com detalhes visuais
