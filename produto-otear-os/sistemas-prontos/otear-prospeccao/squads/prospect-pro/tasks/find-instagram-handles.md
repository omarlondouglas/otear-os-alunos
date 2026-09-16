---
task:
  name: "Find Instagram Handles"
  id: "find-instagram-handles"
  agent: "pp-enricher"
  description: "Buscar Instagram handles dos leads via website e Google search"

inputs:
  - name: leads_file
    type: file
    required: false
    description: "Arquivo JSON de leads brutos (usa último se não informado)"

outputs:
  - name: enriched_json
    type: file
    description: "Arquivo JSON com leads enriquecidos"
  - name: found_count
    type: integer
    description: "Número de Instagram handles encontrados"

pre_conditions:
  - "Arquivo de leads brutos existe em data/leads/"
  - "Playwright instalado"

post_conditions:
  - "Cada lead tem campo instagram (handle ou null)"
  - "Arquivo salvo em data/enriched/"

script: "scripts/lead_enricher.py"
---

# Find Instagram Handles

Busca o Instagram de cada empresa usando duas estratégias:

1. **Via website**: acessa o site da empresa e procura links do Instagram
2. **Via Google**: busca "{nome da empresa} instagram" no Google

## Execução

```bash
cd squads/prospect-pro
python -m scripts.lead_enricher [caminho_do_arquivo]
```
