---
task: reviewSeoAccessibility()
responsavel: "Shield"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: landingPage
    tipo: file
    obrigatorio: true
    descricao: "Landing page montada com todos os componentes (source: assemblePage())"
  - nome: seoReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de SEO gerado durante a montagem da pÃ¡gina (source: assemblePage())"
  - nome: sectionA11yReports
    tipo: array<file>
    obrigatorio: true
    descricao: "RelatÃ³rios de acessibilidade individuais por seÃ§Ã£o (source: buildSection() iteraÃ§Ãµes)"

Saida:
  - nome: seoA11yReview
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio detalhado de revisÃ£o de SEO e acessibilidade com issues e sugestÃµes (destination: lp-frontend-dev para correÃ§Ãµes)"
  - nome: seoA11yScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de SEO e acessibilidade por dimensÃ£o (destination: produceFinalReport())"

Checklist:
  pre-conditions:
    - "[ ] Landing page montada por assemblePage()"
    - "[ ] Metadata SEO presente (title, description, OG tags)"
    - "[ ] RelatÃ³rios de acessibilidade por seÃ§Ã£o disponÃ­veis"
  post-conditions:
    - "[ ] Meta tags verificadas (title, description, OG, Twitter, canonical)"
    - "[ ] Structured data vÃ¡lido (JSON-LD)"
    - "[ ] HTML semÃ¢ntico validado"
    - "[ ] Conformidade WCAG AAA verificada"
    - "[ ] NavegaÃ§Ã£o por teclado testada"
    - "[ ] Skip-to-content verificado"
    - "[ ] Hierarquia de headings validada (h1 Ãºnico)"
    - "[ ] Alt texts presentes em todas as imagens"
    - "[ ] Core Web Vitals estimados"
    - "[ ] Issues categorizados como BLOCKER/WARNING/INFO"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# reviewSeoAccessibility()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  landingPage          â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  seoA11yReview          â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  reviewSeo           â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  seoReport            â”‚â”€â”€â”€â”€â”€â”€>â”‚  Accessibility       â”‚â”€â”€â”€â”€â”€â”€>â”‚  seoA11yScore           â”‚
â”‚  (file)               â”‚       â”‚  @Shield             â”‚       â”‚  (object)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  sectionA11yReports   â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚               â”‚
â”‚  (array<file>)        â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                              â–¼                  â–¼
                                                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                               â”‚ lp-frontend  â”‚   â”‚ produceFinal â”‚
                                                               â”‚ -dev (fixes) â”‚   â”‚ Report()     â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `reviewSeoAccessibility()` realiza uma **auditoria abrangente de SEO e acessibilidade** da landing page montada. O agente **Shield** verifica a presenÃ§a e correÃ§Ã£o de todos os elementos de SEO (meta tags, structured data, semÃ¢ntica HTML), conformidade WCAG AAA, navegabilidade por teclado, hierarquia de headings e estimativas de Core Web Vitals.

O review consolida os relatÃ³rios individuais de acessibilidade por seÃ§Ã£o com uma anÃ¡lise global da pÃ¡gina montada, identificando problemas que sÃ³ sÃ£o visÃ­veis no contexto da pÃ¡gina completa (como h1 duplicados, falta de skip-to-content, ou structured data incompleto).

## Passos

1. **Carregar todos os inputs** â€” Ler `landingPage`, `seoReport` e todos os `sectionA11yReports` para contexto completo.
2. **Verificar meta tags essenciais** â€” Validar presenÃ§a e qualidade de: `<title>` (50-60 caracteres), `<meta description>` (150-160 caracteres), canonical URL, e robots meta.
3. **Verificar Open Graph e Twitter Cards** â€” Validar `og:title`, `og:description`, `og:image`, `og:url`, `og:type` e equivalentes Twitter (`twitter:card`, `twitter:title`, etc.).
4. **Validar structured data (JSON-LD)** â€” Verificar presenÃ§a de schema.org markup vÃ¡lido (Organization, WebPage, Product/Service conforme aplicÃ¡vel), sem erros de sintaxe.
5. **Auditar HTML semÃ¢ntico** â€” Verificar uso correto de `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>` e landmarks ARIA.
6. **Validar hierarquia de headings** â€” Confirmar que existe um Ãºnico `<h1>`, que a hierarquia Ã© sequencial (h1 â†’ h2 â†’ h3, sem pular nÃ­veis) e que os headings sÃ£o descritivos.
7. **Verificar conformidade WCAG AAA** â€” Consolidar relatÃ³rios por seÃ§Ã£o e verificar critÃ©rios globais: foco visÃ­vel, labels em formulÃ¡rios, ARIA attributes, live regions para conteÃºdo dinÃ¢mico.
8. **Testar navegaÃ§Ã£o por teclado** â€” Verificar que todos os elementos interativos sÃ£o acessÃ­veis por Tab, que a ordem de foco Ã© lÃ³gica e que existe skip-to-content link.
9. **Verificar alt texts** â€” Confirmar que todas as imagens possuem alt text descritivo (nÃ£o genÃ©rico como "image" ou "foto"), e que imagens decorativas usam `alt=""`.
10. **Estimar Core Web Vitals** â€” Analisar o cÃ³digo para estimar LCP (Largest Contentful Paint), FID/INP (Interaction to Next Paint), e CLS (Cumulative Layout Shift) com base em: tamanho de imagens, lazy loading, font loading strategy e layout shifts potenciais.
11. **Categorizar issues** â€” Classificar cada problema como BLOCKER (impede indexaÃ§Ã£o ou acessibilidade), WARNING (impacto negativo em ranking ou usabilidade) ou INFO (otimizaÃ§Ã£o recomendada).
12. **Calcular scores** â€” Computar score por dimensÃ£o (SEO tÃ©cnico, structured data, semÃ¢ntica, acessibilidade, performance) e score geral ponderado.
13. **Gerar outputs** â€” Produzir `seoA11yReview` com detalhamento completo e `seoA11yScore` com os valores numÃ©ricos para o relatÃ³rio final.

