---
name: marketing-performance-reports
description: Use when creating client-facing reports for paid media and advertising campaigns.
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

Use this skill to create simple client-facing reports for paid media and ad campaigns, especially WhatsApp-ready summaries and PDFs for business owners.

## Core Principle

Answer four questions in plain language: how much was invested, what result came back, what was the cost per result, and which product or objective performed best. Avoid platform jargon unless the user requests a technical audit.

## Client-Facing Language

Translate platform terms into business labels. Depending on the campaign and destination, examples include:

| Technical idea | Client-facing label |
|---|---|
| Messaging conversation started | Mensagens recebidas / Conversas iniciadas |
| Link click to a page | Cliques na pagina / Acessos |
| Landing page leading to a contact action | Contatos no site |
| Purchase event | Compras no site |
| Spend | Total investido |
| Cost per result | Custo por resultado |

Do not expose terms such as `link_click`, `actions`, API endpoints, raw breakdowns, or internal campaign-object jargon in a business-owner report.

## Grouping and Campaign Name Cleanup

Group by the business, product, offer, or objective the client understands. Split separate businesses sharing an ad account into distinct report sections. Use generic placeholders in examples (for example, Loja A, Produto A, Produto B) and never put actual client names or session-derived campaign details in reusable instructions.

Rename internal campaign labels into clean commercial names. For example, `MSG - WhatsApp - produto-a` can become `Produto A - WhatsApp`. Keep meaningful dates or locations only when needed to distinguish campaigns. Confirm uncertain mappings with the user.

## Metric Selection

- Messaging objective: report messages or conversations started when supported by the data.
- Traffic/page objective: report the relevant page or link clicks, not generic ad clicks.
- Landing page to a contact/group action: report contacts only when that event is measured and its meaning is clear.
- Sales objective: report purchases when available and correctly attributed.
- Trust explicit user corrections over assumptions from campaign names. Recalculate row and grouped totals whenever mappings change.

## PDF Layout

Recommended structure:

1. Cover or header with reporting period and relevant business/product names.
2. A short, plain-language introduction.
3. Summary cards for total invested, results, and average cost.
4. Clear visual sections for each business, product, or objective.
5. Tables with campaign, results, cost, and total invested.
6. A consolidated summary using concise labels.

Keep numeric headers aligned with their values. Use consistent visual separators and avoid splitting section headings, cards, table headers, or rows across pages. Do not include subjective recommendations unless requested or supported by the data.

## Quality Checklist

- No technical strings or raw campaign labels remain in client-facing copy unless intentionally requested.
- Separate businesses within a shared ad account.
- Use clean labels and objective-appropriate metrics.
- Recalculate grouped totals and costs after corrections.
- Verify the generated PDF and extractable text, expected labels, page count, and numeric alignment.
- Ensure no names, campaign details, or results from another client are included.

## Workflow

1. Export or receive campaign data.
2. Map each campaign to the correct business, product, and objective.
3. Select the business metric for each row; ask about ambiguous mappings.
4. Rename campaign labels for readability.
5. Calculate row-level costs and grouped totals.
6. Draft a plain-text summary when requested.
7. Build or update the PDF using the requested design system.
8. Verify the generated artifact and check that client data is isolated to the correct report.
