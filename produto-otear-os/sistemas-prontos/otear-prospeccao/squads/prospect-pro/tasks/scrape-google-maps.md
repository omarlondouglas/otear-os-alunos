---
task:
  name: "Scrape Google Maps"
  id: "scrape-google-maps"
  agent: "pp-scout"
  description: "Buscar empresas no Google Maps por categoria e localização"

inputs:
  - name: query
    type: string
    required: true
    description: "Categoria da empresa (ex: restaurantes, salões de beleza)"
  - name: location
    type: string
    required: true
    description: "Cidade ou região (ex: São Paulo)"
  - name: limit
    type: integer
    required: false
    default: 20
    description: "Número máximo de leads"

outputs:
  - name: leads_json
    type: file
    description: "Arquivo JSON com leads brutos"
  - name: leads_csv
    type: file
    description: "Arquivo CSV com leads brutos"
  - name: leads_count
    type: integer
    description: "Número de leads encontrados"

pre_conditions:
  - "Playwright instalado (playwright install chromium)"
  - "Conexão com internet ativa"
  - "scraper_config.yaml configurado"

post_conditions:
  - "Arquivo JSON salvo em data/leads/"
  - "Arquivo CSV salvo em data/leads/"
  - "Cada lead tem pelo menos: name, address"

script: "scripts/google_maps_scraper.py"
---

# Scrape Google Maps

Executa scraping do Google Maps para extrair dados de empresas.

## Execução

```bash
cd squads/prospect-pro
python -m scripts.google_maps_scraper "restaurantes" "São Paulo" 20
```

## Dados Extraídos

- Nome, endereço, telefone, website
- Rating, número de reviews, categoria
- URL do Google Maps
