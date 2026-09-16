---
task: writeSectionCopy()
responsavel: "Quill"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: sectionName
    tipo: string
    obrigatorio: true
    descricao: "Nome da seÃ§Ã£o a ser escrita â€” hero, problem-agitation, benefits, social-proof, cta, etc. (source: orchestrator)"
  - nome: researchSynthesis
    tipo: file
    obrigatorio: true
    descricao: "SÃ­ntese consolidada das pesquisas de mercado, concorrÃªncia e pÃºblico-alvo (source: synthesizeResearch())"
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com USP, mercado-alvo, tom/voz e posicionamento (source: discoverProduct())"
  - nome: recommendedFrameworks
    tipo: array
    obrigatorio: true
    descricao: "Frameworks de copywriting recomendados â€” AIDA, PAS, BAB, 4Ps, StoryBrand, etc. (source: researchCopyExperts())"

Saida:
  - nome: sectionCopy
    tipo: file
    obrigatorio: true
    descricao: "Copy completo da seÃ§Ã£o com headline, subheadline, body, CTA e microcopy (destination: lp-design-architect + lp-frontend-dev)"
  - nome: headlineVariants
    tipo: array
    obrigatorio: true
    descricao: "MÃ­nimo 5 variantes de headline para testes A/B e revisÃ£o (destination: lp-reviewer)"

Checklist:
  pre-conditions:
    - "[ ] researchSynthesis existe e foi gerado por synthesizeResearch()"
    - "[ ] sectionName Ã© vÃ¡lido (hero, problem-agitation, benefits, social-proof, features, cta, faq, footer)"
    - "[ ] productBrief existe com USP e tom/voz definidos"
    - "[ ] recommendedFrameworks contÃ©m pelo menos 1 framework aplicÃ¡vel"
  post-conditions:
    - "[ ] Copy contÃ©m headline principal"
    - "[ ] Copy contÃ©m subheadline de suporte"
    - "[ ] Copy contÃ©m body text completo"
    - "[ ] Copy contÃ©m CTA (Call to Action) com texto do botÃ£o e microcopy"
    - "[ ] Framework de copywriting utilizado estÃ¡ documentado no output"
    - "[ ] MÃ­nimo 5 variantes de headline geradas em headlineVariants"
    - "[ ] Tom/voz consistente com productBrief"

Performance:
  duration_expected: "8 minutes"
  cacheable: false
  parallelizable: false
---

# writeSectionCopy()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  sectionName     â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  sectionCopy        â”‚
â”‚  (string)        â”‚       â”‚                      â”‚       â”‚  (file)             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  researchSynth.  â”‚â”€â”€â”€â”€â”€â”€>â”‚  writeSectionCopy    â”‚â”€â”€â”€â”€â”€â”€>â”‚  headlineVariants   â”‚
â”‚  (file)          â”‚       â”‚  @Quill              â”‚       â”‚  (array)            â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  productBrief    â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚               â”‚
â”‚  (file)          â”‚       â”‚                      â”‚               â–¼
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  recommended     â”‚â”€â”€â”€â”€â”€â”€>                               â”‚  lp-design-architectâ”‚
â”‚  Frameworks      â”‚                                      â”‚  lp-frontend-dev    â”‚
â”‚  (array)         â”‚                                      â”‚  lp-reviewer        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `writeSectionCopy()` Ã© responsÃ¡vel por produzir o copy completo de **uma seÃ§Ã£o** da landing page. O agente **Quill** recebe o nome da seÃ§Ã£o, a sÃ­ntese de pesquisa, o briefing do produto e os frameworks de copywriting recomendados, e produz um copy estruturado com todos os elementos textuais necessÃ¡rios.

Esta task Ã© **chamada uma vez por seÃ§Ã£o** (iterativa) â€” o orchestrator invoca `writeSectionCopy()` para cada seÃ§Ã£o da landing page (hero, problem-agitation, benefits, social-proof, features, CTA, FAQ, footer). Cada invocaÃ§Ã£o produz o copy especÃ­fico daquela seÃ§Ã£o, aplicando o framework de copywriting mais adequado ao objetivo da seÃ§Ã£o.

AlÃ©m do copy principal, a task gera no mÃ­nimo 5 variantes de headline para possibilitar testes A/B e para que o reviewer possa selecionar a versÃ£o mais impactante.

## Passos

1. **Receber e validar inputs** â€” Verificar que `sectionName` Ã© uma seÃ§Ã£o vÃ¡lida, que `researchSynthesis` e `productBrief` existem, e que `recommendedFrameworks` contÃ©m frameworks aplicÃ¡veis.
2. **Selecionar framework de copywriting** â€” Analisar os `recommendedFrameworks` e escolher o mais adequado para o tipo de seÃ§Ã£o (ex: PAS para problem-agitation, AIDA para hero, StoryBrand para narrativa).
3. **Extrair dados relevantes** â€” Filtrar da `researchSynthesis` e do `productBrief` os pontos mais relevantes para a seÃ§Ã£o especÃ­fica (pain points para problem-agitation, benefÃ­cios para benefits, prova social para social-proof).
4. **Redigir headline principal** â€” Criar a headline principal da seÃ§Ã£o aplicando o framework selecionado e os dados extraÃ­dos.
5. **Gerar variantes de headline** â€” Produzir no mÃ­nimo 5 variantes alternativas da headline, explorando Ã¢ngulos diferentes (emocional, racional, urgÃªncia, curiosidade, benefÃ­cio direto).
6. **Redigir subheadline** â€” Complementar a headline com uma subheadline que expanda o argumento ou adicione contexto.
7. **Redigir body text** â€” Desenvolver o corpo do texto da seÃ§Ã£o, mantendo coerÃªncia com o tom/voz definido no `productBrief`.
8. **Definir CTA e microcopy** â€” Criar o texto do botÃ£o de CTA e o microcopy de suporte (ex: "Sem cartÃ£o de crÃ©dito", "Cancele quando quiser").
9. **Documentar framework utilizado** â€” Registrar no output qual framework foi aplicado e por que foi escolhido para esta seÃ§Ã£o.
10. **Validar contra post-conditions** â€” Verificar que todos os elementos obrigatÃ³rios estÃ£o presentes e que o tom/voz estÃ¡ consistente com o `productBrief`.

