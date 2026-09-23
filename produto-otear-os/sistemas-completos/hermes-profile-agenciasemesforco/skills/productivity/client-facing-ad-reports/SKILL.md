---
name: client-facing-ad-reports
description: Use when making client-facing advertising performance reports.
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

Use this skill when preparing an advertising performance report for a business owner or client from ad-platform data, screenshots, CSV files, or API insights.

## Core Principle

Write for the entrepreneur receiving the report, not for a technical ads operator. Make clear what was invested, what result came back, how much each result cost, and which product or objective performed best. Do not expose implementation details unless the user asks for a technical audit.

## Client-Facing Language

Prefer clear labels such as:

- Mensagens recebidas
- Cliques na pagina or acessos
- Contatos no site
- Compras no site
- Custo por resultado
- Total investido
- Custo medio por mensagem, clique, contato, or compra

Avoid technical terms such as `API`, `link_click`, `action_type`, `custom action`, permission details, and raw campaign names that are confusing to a business owner. Translate technical source metrics according to the campaign destination and the user's clarification.

## Choose the Right Result Metric

- Messaging or WhatsApp campaigns: report messages or conversations started when that is the configured objective/result.
- Traffic, page, live, group, or link campaigns: report the relevant link/page clicks, not all ad clicks and not messages.
- Sales or ecommerce campaigns: report purchases or another explicit sales result when available.
- If the source metric is ambiguous, ask the user before presenting it as a business outcome.
- User corrections override assumptions based on campaign names. Recalculate totals after changing a metric mapping.

## Grouping and Campaign Names

Group campaigns by business, product, offer, or objective in a way the client understands. If one ad account contains multiple businesses or product lines, separate them in the report. Use neutral placeholders in examples (for example, Loja A, Produto A, Oferta B); never reuse another client's actual names, campaign labels, or performance figures.

Convert operational campaign names into concise commercial labels. Example: `MSG - WhatsApp - produto-a` can become `Produto A - WhatsApp`. Keep dates or geography only when they help distinguish campaigns. Confirm uncertain campaign-to-product mappings with the user instead of guessing.

## Recommended Report Shape

### WhatsApp-Ready Text

```text
Relatorio de campanhas - <Cliente ou produto>
Periodo: <periodo>

Campanha: <nome claro>
Resultados: <quantidade e tipo>
Custo por resultado: R$ <valor>
Total investido: R$ <valor>

Total investido no periodo: R$ <valor>
Total de resultados: <quantidade>
```

### PDF

1. Cover or header with the reporting period and high-level totals.
2. Summary cards for investment, result volume, and average cost.
3. Clear sections for each business, product, or objective.
4. Tables with campaign, results, cost, and total invested.
5. Consolidated summary and a concise decision note when useful.

## PDF Layout and Calculations

- Align numeric columns and their headers consistently, usually right-aligned.
- Keep section headings, summary cards, table headers, and rows together across page breaks.
- Avoid dense technical footnotes in client-facing reports.
- Cost per result = total invested / result count. When combining rows, recompute group totals and average cost from totals; do not average campaign costs directly.
- Format BRL as `R$ 1.234,56` and counts with Brazilian separators when appropriate.

## Verification Checklist

Before delivery:

1. Verify totals and costs with a calculator or script.
2. Confirm the generated PDF exists, has the expected page count, and contains extractable text.
3. Search the final text for technical terms, internal campaign names, and labels the user rejected.
4. Confirm that public-facing labels and metric definitions match the user's instructions.
5. Check alignment, page breaks, and that no client's data has been carried over from another report.

## Pitfalls

- Do not assume every campaign containing "message" in its name should be reported as messages; verify the objective and result.
- Do not substitute general ad clicks for page clicks, site contacts, or another objective-specific result.
- Do not group multiple businesses under one account label when the client needs them separated.
- Do not reuse client-specific examples, data, or report notes across accounts.
