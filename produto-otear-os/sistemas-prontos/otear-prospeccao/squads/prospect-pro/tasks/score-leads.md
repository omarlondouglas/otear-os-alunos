---
task:
  name: "Score Leads"
  id: "score-leads"
  agent: "pp-enricher"
  description: "Calcular scoring dos leads baseado em critérios de oportunidade"

inputs:
  - name: leads_file
    type: file
    required: false
    description: "Arquivo de leads para scoring"

outputs:
  - name: scored_leads
    type: file
    description: "Leads com score e classificação"

pre_conditions:
  - "scoring_rules.yaml configurado"

post_conditions:
  - "Cada lead tem score.total e score.classification"
  - "Classificação: hot (≥8), warm (5-7), cold (<5)"

script: "scripts/utils/scoring.py"
---

# Score Leads

Aplica o algoritmo de scoring em cada lead.

## Critérios (0-16 pontos)

| Critério | Pontos |
|----------|--------|
| Sem website | +3 |
| Sem Instagram | +4 |
| Engagement <2% | +3 |
| Posting irregular | +2 |
| Poucos reviews | +1 |
| Rating baixo | +1 |
| Bio não profissional | +1 |
| Sem link na bio | +1 |
