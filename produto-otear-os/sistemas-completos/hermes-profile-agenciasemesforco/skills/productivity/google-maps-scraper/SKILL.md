---
name: google-maps-scraper
description: "Busca empresas/negócios no Google Maps via automação de browser (Playwright). Extrai nome, telefone, endereço, website, rating e reviews para prospecção local."
version: "1.0.0"
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [scraper, google-maps, leads, prospeccao, negocios]
---

# Google Maps Scraper

Busca empresas no Google Maps via Playwright sem necessidade de chaves de API pagas.

## ⚠️ Requisito de Execução: IP Residencial
O Google Maps bloqueia ativamente requisições vindas de datacenters/VPSs em nuvem, forçando redirecionamentos para telas de consentimento. **Execute este scraper preferencialmente na sua máquina local com conexão residencial.**

## Como Usar

### 1. Dependências
```bash
pip install playwright pyyaml
playwright install chromium
```

### 2. Executar a busca
```bash
python scripts/scraper.py "Nicho/Termo" "Cidade - UF" [limite_maximo]
```
Exemplo:
```bash
python scripts/scraper.py "Clinica Odontologica" "Campinas - SP" 30
```

### 3. Resultados
Os dados são exportados automaticamente em formatos estruturados (`.csv` e `.json`) com os campos:
- Nome do estabelecimento
- Categoria / Ramo
- Nota e quantidade de avaliações
- Telefone / WhatsApp comercial
- Endereço completo
- Website ou link direto do Google Maps
