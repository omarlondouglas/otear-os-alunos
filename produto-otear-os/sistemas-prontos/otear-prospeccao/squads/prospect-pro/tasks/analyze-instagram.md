---
task:
  name: "Analyze Instagram"
  id: "analyze-instagram"
  agent: "pp-stalker"
  description: "Analisar perfis Instagram dos leads — métricas, engagement, frequência"

inputs:
  - name: leads_file
    type: file
    required: false
    description: "Arquivo de leads enriquecidos"
  - name: posts_to_analyze
    type: integer
    required: false
    default: 12

outputs:
  - name: analyzed_leads
    type: file
    description: "Leads com dados completos do Instagram"

pre_conditions:
  - "Leads enriquecidos com Instagram handles"
  - "Playwright instalado"

post_conditions:
  - "Cada lead com Instagram tem: followers, engagement_rate, posting_frequency"
  - "Score recalculado com dados reais"
  - "Script de abordagem gerado"

script: "scripts/instagram_scraper.py"
---

# Analyze Instagram

Scraper perfis do Instagram e calcula métricas de engagement.

## Dados Extraídos

- Bio, followers, following, posts count
- Últimos 12 posts: likes, comments
- Engagement rate, frequência de postagem
- É conta business? É verificada?

## Execução

```bash
cd squads/prospect-pro
python -m scripts.instagram_scraper [caminho_do_arquivo]
```
