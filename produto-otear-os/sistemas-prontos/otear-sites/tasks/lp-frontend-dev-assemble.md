---
task: assemblePage()
responsavel: "Pixel"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: allSectionComponents
    tipo: array<file>
    obrigatorio: true
    descricao: "Todos os componentes de seÃ§Ã£o construÃ­dos e validados (source: buildSection() iterations)"
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing do produto para SEO metadata e structured data (source: discoverProduct())"

Saida:
  - nome: landingPage
    tipo: file
    obrigatorio: true
    descricao: "Landing page completa montada com todas as seÃ§Ãµes, SEO e acessibilidade (destination: lp-integrator + lp-reviewer)"
  - nome: seoReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de SEO â€” metadata, structured data, sitemap, robots (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] Todos os componentes de seÃ§Ã£o construÃ­dos e renderizando corretamente"
    - "[ ] productBrief disponÃ­vel para extraÃ§Ã£o de metadata SEO"
  post-conditions:
    - "[ ] PÃ¡gina montada com todas as seÃ§Ãµes na ordem correta"
    - "[ ] SEO metadata completo â€” title, description, OG tags, Twitter cards"
    - "[ ] URL canÃ´nica configurada"
    - "[ ] JSON-LD structured data para Organization/Product/FAQ"
    - "[ ] sitemap.xml gerado"
    - "[ ] robots.txt configurado"
    - "[ ] Link skip-to-content presente e funcional"
    - "[ ] Hierarquia de headings validada (Ãºnico h1)"
    - "[ ] PÃ¡gina inteira navegÃ¡vel por teclado"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# assemblePage()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ allSectionComponents  â”‚â”€â”€â”€â”
â”‚ (array<file>)         â”‚   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                       â”‚   â”œâ”€â”€â”€â”€>â”‚                  â”‚â”€â”€â”€â”€>â”‚ landingPage      â”‚
â”‚ - HeroSection         â”‚   â”‚     â”‚  assemblePage    â”‚     â”‚ (file)           â”‚
â”‚ - BenefitsSection     â”‚   â”‚     â”‚  @Pixel          â”‚     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ - SolutionSection     â”‚   â”‚     â”‚                  â”‚â”€â”€â”€â”€>â”‚ seoReport        â”‚
â”‚ - TestimonialsSection â”‚   â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚ (file)           â”‚
â”‚ - FAQSection          â”‚   â”‚                              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚ - CTASection          â”‚   â”‚                                     â”‚
â”‚ - FooterSection       â”‚   â”‚                                     â–¼
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚                           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                            â”‚                           â”‚ lp-integrator    â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚                           â”‚ lp-reviewer      â”‚
â”‚ productBrief          â”‚â”€â”€â”€â”˜                           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚ (file)                â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `assemblePage()` Ã© a etapa de montagem final da landing page no frontend. O agente **Pixel** recebe todos os componentes de seÃ§Ã£o jÃ¡ construÃ­dos e validados individualmente, e os compÃµe em uma pÃ¡gina Ãºnica e coesa, adicionando toda a camada de SEO, structured data e acessibilidade global.

Esta task nÃ£o cria componentes novos â€” ela orquestra os existentes, define a ordem de apresentaÃ§Ã£o, implementa a navegaÃ§Ã£o entre seÃ§Ãµes, configura metadata para motores de busca e garante que a pÃ¡gina como um todo funciona como uma unidade coerente e otimizada.

## Passos

1. **Inventariar seÃ§Ãµes** â€” Listar todos os componentes recebidos em allSectionComponents e definir a ordem de montagem na pÃ¡gina (hero primeiro, CTA/footer por Ãºltimo).
2. **Criar pÃ¡gina principal** â€” Implementar `app/page.tsx` (ou `app/(landing)/page.tsx`) importando e posicionando todos os componentes de seÃ§Ã£o na ordem definida.
3. **Implementar layout root** â€” Configurar `app/layout.tsx` com ThemeProvider, fontes, metadata base e skip-to-content link.
4. **Configurar SEO metadata** â€” Extrair do productBrief: title, description, keywords. Configurar `metadata` export do Next.js com OG tags, Twitter cards e URL canÃ´nica.
5. **Adicionar JSON-LD** â€” Criar structured data para Organization, Product e FAQ usando os dados do productBrief e do conteÃºdo das seÃ§Ãµes.
6. **Gerar sitemap.xml** â€” Configurar geraÃ§Ã£o automÃ¡tica de sitemap via `app/sitemap.ts` ou plugin.
7. **Configurar robots.txt** â€” Criar `app/robots.ts` com regras adequadas (allow all, referÃªncia ao sitemap).
8. **Validar heading hierarchy** â€” Garantir que existe um Ãºnico `<h1>` na pÃ¡gina (no hero) e que os headings seguem uma hierarquia lÃ³gica (h1 > h2 > h3).
9. **Implementar skip-to-content** â€” Adicionar link de skip-to-content visÃ­vel no focus para navegaÃ§Ã£o por teclado.
10. **Testar pÃ¡gina completa** â€” Verificar renderizaÃ§Ã£o de todas as seÃ§Ãµes, navegaÃ§Ã£o por teclado end-to-end, dark mode consistente e performance de carregamento.
11. **Gerar seoReport** â€” Documentar todas as configuraÃ§Ãµes de SEO, structured data implementados, scores de acessibilidade e heading hierarchy no relatÃ³rio.

