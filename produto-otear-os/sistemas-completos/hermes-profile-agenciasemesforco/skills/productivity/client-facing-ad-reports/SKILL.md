---
name: client-facing-ad-reports
description: Use when making client-facing ad performance reports.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - ads-reporting
      - client-reports
      - meta-ads
      - pdf-reports
    related_skills:
      - meta-marketing-api-campaigns
      - pdf
---

# Client-Facing Ad Performance Reports

## When to Use

Use this skill when preparing a simple advertising performance report for a business owner or client, especially from Meta Ads data, screenshots, CSVs, or API insights.

## Core Principle

The artifact is for an entrepreneur/client, not for a technical ads operator. Show what matters for a decision:

- what was invested;
- what result came back;
- how much each result cost;
- which product/objective performed better.

Do **not** expose implementation language unless the user asks for a technical/debug report.

## Client-facing language

Prefer:

- **Mensagens recebidas**
- **Cliques na página** or **acessos** for page/live traffic
- **Contatos no site** when the ad sends people to a page/site before a WhatsApp/group action
- **Compras no site**
- **Custo por resultado**
- **Total investido**
- **Custo médio por mensagem**
- **Custo médio por clique/contato**

Avoid in the final client PDF/message:

- `API`
- `link_click`
- `action_type`
- `custom action`
- `ação personalizada`
- permission/token details
- raw internal campaign names when they look operational or messy

If the source metric is technical, translate it silently into a business label. For example, Meta `link_click` might become **Cliques na página**, **Acessos**, or **Contatos no site** depending on the campaign destination and the user's clarification.

## Choose the right result metric

Match the metric to the campaign objective or user clarification:

- Message/WhatsApp campaigns → report **Mensagens recebidas**.
- Traffic/live/group/link campaigns → report **Cliques no link**, not all ad clicks and not messages.
- Sales/ecommerce campaigns → report **Compras no site** or another explicit sales result if available.

If a campaign name says “Mensagem” but the user clarifies the objective was traffic, use traffic results. User clarification overrides naive name parsing.

## Grouping rules

Group for business understanding, not raw export order.

Typical hierarchy:

1. Account or brand, when it maps cleanly to the client.
2. Product/client/objective sections.
3. Campaign rows under each section.
4. Final consolidated summary.

Examples:

- Casa Biju can be separated by objective:
  - **Campanhas de Mensagens**
  - **Campanhas para Live / Grupo**
- A food/pizzeria account with several offers should be separated by offer/product:
  - **Feijoada**
  - **Sua Pizza**
  - **Pizzaburguer**
  - **Campanhas de Mensagens Pizzas Mistas**
  - **Sua Marmita**
  - **Cardápio**

If the ad account has an internal account name that is not useful to the client, do not headline every section with that account name. Use the public-facing product/client labels.

## Rename internal campaign names

Before final delivery, convert operational names into clean commercial labels.

Examples:

| Internal/source name | Client-facing name |
|---|---|
| `MSG - WhatsApp — pizzaburguer` | `Pizzaburguer — WhatsApp` |
| `MSG - WhatsApp — menos terça` | `Pizzas Mistas — WhatsApp` if user says it belongs to Pizzas Mistas |
| `8Km - MSG - WhatsApp` | `Pizzas Mistas — WhatsApp` if user says it belongs to Pizzas Mistas |
| `Mensagem - tatuqura - 18-08` | `Sua Pizza — Tatuquara 18/08` |
| `MENSAGENS - 3km - SUA PIZZA` | `Sua Pizza — WhatsApp 3km` |
| `tráfego para feijoada — Grupo whatsapp` | `Feijoada — Grupo WhatsApp` |

Keep dates only when they help distinguish campaigns. Fix obvious typos in labels.

## Recommended report shape

### WhatsApp-ready text

Use this compact pattern:

```text
Relatório Campanhas <Cliente/Produto>
Período: últimos 30 dias

Campanha: <Nome limpo>
Mensagens recebidas: <n>
Custo por mensagem: R$ <valor>
Total investido: R$ <valor>

---

Campanha: <Nome limpo>
Cliques no link: <n>
Custo por clique: R$ <valor>
Total investido: R$ <valor>

----------------------------------------

Total investido no período: R$ <valor>
Total de mensagens recebidas: <n>
Total de cliques no link: <n>
```

### PDF report

Use:

1. Cover/hero with period and high-level totals.
2. Summary cards.
3. Strong section separators per account/product/objective.
4. Tables with columns:
   - Campanha
   - Resultados
   - Custo
   - Total investido
5. Final summary by group/product.
6. Short decision note.

## Layout rules for PDFs

- Align numeric columns and their headers consistently, usually right-aligned:
  - Resultados
  - Custo
  - Total investido
- Do not let table headers drift away from numeric columns.
- Add summary cards under every major client/product section: result count, average cost, and total invested.
- Avoid dense technical footnotes in client PDFs.
- If using a design system from an HTML file, reuse its typography, spacing, cards, chips, section bands, tables, and print CSS, but rewrite content in client language.
- Use black section bands/tarjas to separate major groups when the user asks for visually clear separation.
- Prevent awkward page breaks: keep black bands, cards, table headers, and table rows together. Start dense product/objective sections on a fresh page rather than letting a heading sit at the bottom of one page and its content on the next.

## Calculations

- Cost per result = `total invested / result count`.
- Keep currency in Brazilian format when working in BRL: `R$ 1.234,56`.
- Keep counts with Brazilian thousands separator when helpful: `16.327`.
- If combining two rows into the same product group, recompute group totals and average cost from totals, not by averaging the campaign costs.

## Verification checklist

Before delivery:

1. Verify all totals and costs with a calculator/script.
2. Verify the final PDF exists, has expected page count, and text is extractable.
3. Search extracted text for forbidden technical terms: `API`, `link_click`, `action_type`, `ação personalizada`.
4. Search extracted text for internal names/typos the user rejected.
5. Confirm the requested public labels are present.
6. Confirm column headers align with their data.

## References

- `references/meta-client-report-notes.md` — concrete examples of metric corrections, client-facing labels, grouping corrections, and PDF page-break/layout checks from a Meta Ads reporting session.

## Pitfalls

- Do not assume every campaign with “Mensagem” in the name should be reported as messages; the objective may be traffic.
- Do not show general ad clicks when the user asked for page clicks, site contacts, or objective-specific clicks.
- Do not group every campaign under the ad account name if the account contains several clients or products.
- Do not leak internal taxonomy into a client-facing report.
- Do not present a technical explanation when the user asks for a PDF/report for a business owner.
