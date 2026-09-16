# Session notes: Meta Ads client PDF reporting

Concrete corrections to preserve for future client-facing Meta Ads reports.

## Metric corrections

- Do not use generic ad clicks when the campaign's result metric is a more specific business action.
- A traffic/live campaign may need to show **cliques na página** instead of total ad clicks. Example: "Grupo da Live" should report 650 page clicks, not 2,505 generic link/ad clicks.
- A group/WhatsApp funnel that sends users to a page before joining a group should be labeled **contatos no site**, not generic clicks. Example: "Feijoada — Grupo WhatsApp 14/08" should report 140 contatos no site.
- If the user says a campaign belongs to "Sua Pizza" and its business objective was messages, report it as **mensagens**, even if the internal campaign name contains "vendas" or the raw export has click fields.

## Grouping/name corrections

- For a pizzeria account containing multiple products/business lines, do not headline everything as the ad-account name. Use client/product group labels:
  - Pizzaria Dona Calabresa
  - Marmitaria
  - Sua Pizza
  - Pizzaburguer
  - Pizzas Mistas
  - Cardápio
- "Sua Marmita" and "Feijoada" can be grouped together under **Marmitaria** when the user says they belong together. Rename the card/section from Feijoada to Marmitaria, with a subtitle like "Campanhas de feijoada e marmitas".
- "Menos Terça" and "Raio 8km" can both be renamed/grouped as **Campanhas de Mensagens Pizzas Mistas** when the user says they are Pizzas Mistas.
- In final summaries, omit parent prefixes like "Pizzaria Dona Calabresa — Sua Pizza". Use only the actual business/product names: "Sua Pizza", "Marmitaria", "Pizzas Mistas", etc.

## Client-facing tone corrections

- Use a direct intro such as: "Essa foi a performance dos seus anúncios do mês de agosto."
- Avoid generic process language like "cada campanha foi agrupada por conta, produto ou objetivo..." when the client just needs the result.
- Remove subjective advice blocks like "Resumo para decisão" if the user says they are bad or unnecessary.
- The deliverable is for an entrepreneur; do not discuss API, custom actions, event names, or implementation details.

## Layout corrections

- Add summary cards under every major client/product section, not only the first account.
- Keep spacing after major section bands consistent with the cards below.
- Prevent content from breaking in the middle: put large product sections on fresh pages when necessary; keep black bands, cards, table headers, and rows together.
- Consolidate duplicate product sections when they represent the same product (e.g. two Pizzas Mistas rows should be one Pizzas Mistas section with combined summary cards and both campaign rows).
