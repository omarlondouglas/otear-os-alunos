---
name: marketing-performance-reports
description: Use when creating client ad performance reports.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - marketing-reports
      - ads-reporting
      - client-reports
      - pdf-reports
    related_skills:
      - meta-marketing-api-campaigns
      - pdf
---

# Marketing Performance Reports

## When to Use

Use this skill when creating simple client-facing reports for paid media/ad campaigns, especially WhatsApp/PDF reports for business owners.

## Core Principle

Write for the entrepreneur receiving the report, not for the media buyer or API operator. The report should answer:

- How much was invested?
- What result came back?
- What was the cost per result?
- Which product/client/objective performed best?

Avoid technical platform language unless the user explicitly asks for an audit.

## Client-Facing Language

Do **not** expose terms such as:

- `link_click`
- `actions`
- API / endpoint / level / breakdown
- custom action / ação personalizada
- raw campaign-object jargon

Translate to plain business terms:

| Technical idea | Client-facing label |
|---|---|
| messaging conversation started | Mensagens recebidas / Conversas iniciadas |
| link click to page | Cliques na página |
| click that leads to WhatsApp/group after landing page | Contatos no site |
| purchase event | Compra no site |
| spend | Total investido |
| cost per result | Custo por resultado / Custo por mensagem |

## Grouping Rules

Group by what the client understands:

1. **Account** only when it maps cleanly to a client/business.
2. **Product / business line / objective** when one ad account contains multiple fronts.
3. **Separate businesses sharing one ad account must appear as separate sections** in the summary.

Example preferred final summary labels:

- Casa Biju
- Feijoada
- Sua Pizza
- Marmitaria
- Pizzas Mistas
- Pizzaburguer
- Cardápio

Avoid repeated prefixes like `Pizzaria Dona Calabresa — Sua Pizza` in final summary rows if the row itself is the business/product.

## Campaign Name Cleanup

Before delivering, rename internal campaign names into clean labels.

Examples:

| Internal/raw name | Client-facing name |
|---|---|
| `MSG - WhatsApp — pizzaburguer` | Pizzaburguer — WhatsApp |
| `MSG - WhatsApp — menos terça` | Pizzas Mistas — WhatsApp |
| `8Km - MSG - WhatsApp` | Pizzas Mistas — WhatsApp |
| `Mensagem - tatuqura - 18-08` | Sua Pizza — Tatuquara 18/08 |
| `tráfego para feijoada — Grupo whatsapp` | Feijoada — Grupo WhatsApp |
| `MENSAGENS - SUA Marmita — seg a sáb` | Marmitas — WhatsApp |

Fix obvious typos in labels, but keep meaningful dates only when they help distinguish campaigns.

## Metric Selection

Do not use generic ad clicks by default. Pick the metric that reflects the objective and any user correction.

- Messaging objective: report `Mensagens recebidas` and `Custo por mensagem`.
- Traffic/page objective: report `Cliques na página` and `Custo por clique`.
- Landing page to WhatsApp/group: report `Contatos no site` and `Custo por contato`.
- Sales/cardápio objective: report `Compras no site` and `Custo por compra` when available.

If the user corrects a metric mapping, trust the correction and update the report. Example: “Grupo da Live is 650 page clicks” means do not keep a larger generic click number for that row.

## PDF Layout for This User

Preferred structure:

1. Cover/hero with business names as chips.
2. One sentence in plain language, e.g. `Essa foi a performance dos seus anúncios do mês de agosto.`
3. Top summary cards: total invested, total messages, total accesses/contacts, average cost.
4. Section with black band/tarja for each major business or product.
5. Immediately under each major section title, include cards: result volume, average cost, total invested.
6. Tables with columns:
   - Campanha
   - Resultados
   - Custo
   - Total investido
7. Right-align numeric columns and their headers. Keep table header alignment consistent.
8. Final summary table with clean business/product names.

Use black section bands/tarjas between client/product sections; this matches the user's preferred design direction.

## Reference Notes

- See `references/meta-ads-report-lessons.md` for concrete Meta Ads report corrections and naming examples from a client-facing PDF iteration.

## Quality Checklist

Before final delivery:

- No technical strings such as `link_click`, `API`, `actions`, or `ação personalizada` remain.
- No raw/internal campaign names remain unless intentionally kept.
- Numeric columns and headers are aligned.
- Major sections have summary cards before detailed tables.
- One ad account containing multiple businesses is split into those businesses.
- Final summary rows use clean labels.
- Recalculate totals after changing metric mappings.
- Verify the PDF was actually generated and text extraction includes expected labels.

## Workflow

1. Pull/export campaign data.
2. Map each campaign to a client/product/objective.
3. Select the business metric per row.
4. Rename campaign labels for client readability.
5. Calculate per-row cost and grouped totals.
6. Build WhatsApp/plain-text summary first if the user asks for simple copy.
7. For PDF: create or update HTML using the chosen design system, then render to PDF with a browser engine.
8. Verify generated PDF text for expected labels and absence of technical/internal terms.
