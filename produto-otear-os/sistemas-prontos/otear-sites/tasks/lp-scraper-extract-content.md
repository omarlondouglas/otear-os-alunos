---
task: extractContent()
responsavel: "Radar"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: referenceUrl
    tipo: string
    obrigatorio: true
    descricao: "URL da pÃ¡gina de referÃªncia para extrair estrutura de conteÃºdo"

Saida:
  - nome: contentStructure
    tipo: file
    obrigatorio: true
    descricao: "Estrutura de seÃ§Ãµes e tom do copy (destination: lp-copywriter, lp-strategist)"

Checklist:
  pre-conditions:
    - "[ ] URL de referÃªncia acessÃ­vel"
  post-conditions:
    - "[ ] SeÃ§Ãµes identificadas e ordenadas"
    - "[ ] Headlines e CTAs capturados como referÃªncia de tom"
    - "[ ] Estrutura de navegaÃ§Ã£o documentada"
    - "[ ] Elementos de social proof identificados"

Performance:
  duration_expected: "2 minutes"
  cacheable: true
  parallelizable: true
---

# extractContent()

## DescriÃ§Ã£o

Extrai a estrutura de conteÃºdo da URL de referÃªncia: quais seÃ§Ãµes existem, que tipo de headlines/CTAs usam, tom de voz, e elementos de social proof. Serve como referÃªncia para o Strategos e Quill.

## Passos

1. **Fetch da pÃ¡gina** â€” WebFetch da URL.
2. **Identificar seÃ§Ãµes** â€” Mapear cada seÃ§Ã£o da LP (hero, features, etc.).
3. **Extrair headlines** â€” H1, H2, H3 de cada seÃ§Ã£o.
4. **Extrair CTAs** â€” Textos dos botÃµes e links de aÃ§Ã£o.
5. **Analisar tom** â€” Formal, casual, urgente, tÃ©cnico, etc.
6. **Mapear social proof** â€” Logos, depoimentos, nÃºmeros, badges.
7. **Documentar navegaÃ§Ã£o** â€” Tipo de menu, links, comportamento.
8. **Gerar output** â€” `extracted-content-structure.md`.

