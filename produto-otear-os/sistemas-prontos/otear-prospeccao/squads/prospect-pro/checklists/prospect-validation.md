---
checklist:
  name: "Prospect Data Validation"
  id: "prospect-validation"
  description: "Validação da qualidade dos dados de prospecção"
  version: "1.0"
---

# Prospect Data Validation Checklist

## Nível 1 — Dados Básicos (BLOCKING)

- [ ] Cada lead tem `google.name` preenchido
- [ ] Cada lead tem `google.address` ou `google.phone`
- [ ] Arquivo JSON é válido e não está corrompido
- [ ] Nenhum lead duplicado (mesmo nome + endereço)

## Nível 2 — Enriquecimento (BLOCKING)

- [ ] Campo `instagram` existe em cada lead (mesmo que null)
- [ ] Handles do Instagram são válidos (sem caracteres inválidos)
- [ ] Score calculado para todos os leads
- [ ] Classificação (hot/warm/cold) atribuída

## Nível 3 — Análise Instagram (ADVISORY)

- [ ] Engagement rate calculado para leads com Instagram
- [ ] Frequência de postagem calculada
- [ ] Pelo menos 6 posts analisados por perfil
- [ ] Dados de followers são numéricos e > 0

## Nível 4 — Relatório (BLOCKING)

- [ ] Relatório Markdown gerado sem erros
- [ ] CSV exportado com todas as colunas
- [ ] Scripts de abordagem gerados para leads hot/warm
- [ ] Nenhum dado sensível exposto no relatório

## Nível 5 — Qualidade (ADVISORY)

- [ ] Leads hot representam < 40% do total (sanity check)
- [ ] Nenhum lead com score > 16
- [ ] Todos os scripts de abordagem são em PT-BR
- [ ] Relatório tem seções para hot, warm e cold
