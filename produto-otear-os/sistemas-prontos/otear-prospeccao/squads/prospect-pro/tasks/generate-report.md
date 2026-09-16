---
task:
  name: "Generate Report"
  id: "generate-report"
  agent: "pp-reporter"
  description: "Gerar relatório de prospecção com scoring, classificação e scripts de abordagem"

inputs:
  - name: leads_file
    type: file
    required: false
    description: "Arquivo de leads analisados"
  - name: title
    type: string
    required: false
    default: "Relatório de Prospecção"

outputs:
  - name: report_md
    type: file
    description: "Relatório em Markdown"
  - name: report_json
    type: file
    description: "Relatório em JSON"
  - name: report_csv
    type: file
    description: "CSV final para CRM/planilha"

pre_conditions:
  - "Leads analisados com score e Instagram data"

post_conditions:
  - "Relatório salvo em data/reports/"
  - "CSV com colunas: nome, telefone, instagram, score, script"

script: "scripts/report_generator.py"
---

# Generate Report

Gera relatório executivo de prospecção.

## Seções do Relatório

1. **Resumo** — total, hot, warm, cold
2. **Leads Hot** — detalhes completos + script de abordagem
3. **Leads Warm** — detalhes + script
4. **Leads Cold** — tabela resumida

## Execução

```bash
cd squads/prospect-pro
python -m scripts.report_generator [caminho] "Título do Relatório"
```
