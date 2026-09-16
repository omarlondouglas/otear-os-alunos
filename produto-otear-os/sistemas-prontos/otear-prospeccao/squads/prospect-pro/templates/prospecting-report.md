---
name: prospecting-report
description: "Template para relatório de prospecção"
variables:
  - title
  - date
  - total_leads
  - hot_count
  - warm_count
  - cold_count
---

# {{title}}

**Data:** {{date}}
**Total de leads:** {{total_leads}}

## Resumo

| Classificação | Quantidade |
|---------------|-----------|
| 🔥 Hot | {{hot_count}} |
| 🌡️ Warm | {{warm_count}} |
| ❄️ Cold | {{cold_count}} |

## Leads Hot — Abordar Imediatamente

{{#each hot_leads}}
### {{index}}. {{name}}

| Dado | Valor |
|------|-------|
| Categoria | {{category}} |
| Telefone | {{phone}} |
| Website | {{website}} |
| Rating | {{rating}} ⭐ ({{reviews}} reviews) |
| Instagram | @{{instagram_handle}} |
| Followers | {{followers}} |
| Engagement | {{engagement_rate}}% |

**Oportunidades:** {{weaknesses}}

**Script de Abordagem:**
> {{approach_script}}

---
{{/each}}
