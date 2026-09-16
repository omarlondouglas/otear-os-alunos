---
task: researchCopyExperts()
responsavel: "Scout"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto para contextualizar a pesquisa de especialistas (source: discoverProduct())"
  - nome: audienceProfile
    tipo: file
    obrigatorio: false
    descricao: "Perfil de audiÃªncia para refinar seleÃ§Ã£o de frameworks (source: identifyAudience())"

Saida:
  - nome: copyExpertsReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio com especialistas de copywriting e seus frameworks relevantes (destination: synthesizeResearch() + lp-copywriter)"
  - nome: recommendedFrameworks
    tipo: array
    obrigatorio: true
    descricao: "Frameworks de copy recomendados com mapeamento para seÃ§Ãµes da landing page (destination: lp-copywriter)"

Checklist:
  pre-conditions:
    - "[ ] productBrief existe"
  post-conditions:
    - "[ ] MÃ­nimo 3 especialistas de copywriting world-class identificados"
    - "[ ] Frameworks relevantes de cada especialista documentados"
    - "[ ] Mapeamento framework-para-seÃ§Ã£o fornecido"
    - "[ ] Justificativa de relevÃ¢ncia para o produto/nicho incluÃ­da"

Performance:
  duration_expected: "12 minutes"
  cacheable: true
  parallelizable: true

Tools:
  - WebSearch
  - WebFetch
---

# researchCopyExperts()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  productBrief   â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  copyExpertsReport      â”‚
â”‚  (file)         â”‚       â”‚  researchCopyExperts â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  @Scout              â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  audienceProfileâ”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  recommendedFrameworks   â”‚
â”‚  ? (file)       â”‚       â”‚  [WebSearch,         â”‚       â”‚  (array)                â”‚
â”‚                 â”‚       â”‚   WebFetch]          â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”‚
                                                                 â–¼
                                                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                     â”‚  synthesizeResearch() â”‚
                                                     â”‚  lp-copywriter       â”‚
                                                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `researchCopyExperts()` identifica os maiores especialistas mundiais em copywriting e seus frameworks mais relevantes para o produto/nicho do usuÃ¡rio. O agente **Scout** pesquisa referÃªncias como David Ogilvy, Eugene Schwartz, Gary Halbert, Joanna Wiebe, entre outros, e seleciona os frameworks mais adequados ao contexto.

O diferencial desta task Ã© o **mapeamento framework-para-seÃ§Ã£o** â€” cada framework recomendado Ã© associado a uma seÃ§Ã£o especÃ­fica da landing page (ex: PAS para hero, AIDA para above-the-fold, Before-After-Bridge para testimonials). Isso dÃ¡ ao copywriter uma base teÃ³rica sÃ³lida e testada para cada parte da pÃ¡gina.

Esta Ã© uma task Molecule â€” combina pesquisa externa com anÃ¡lise contextual, sem a complexidade multi-fase de um Organism.

## Passos

1. **Carregar productBrief** â€” Extrair tipo de produto, nicho, tom de voz e posicionamento para contextualizar a pesquisa.
2. **Carregar audienceProfile** (se disponÃ­vel) â€” Usar dados de personas e pain points para refinar a seleÃ§Ã£o de frameworks.
3. **Identificar especialistas relevantes** â€” Usar `WebSearch` para encontrar os maiores copywriters e suas contribuiÃ§Ãµes:
   - Copywriters clÃ¡ssicos (Ogilvy, Schwartz, Halbert, Caples, Hopkins)
   - Copywriters modernos (Wiebe, Klaff, Cialdini, Hormozi)
   - Especialistas de nicho relevantes ao produto
4. **Pesquisar frameworks de cada especialista** â€” Para cada especialista, documentar:
   - Frameworks principais (PAS, AIDA, BAB, 4Ps, StoryBrand, etc.)
   - PrincÃ­pios-chave de conversÃ£o
   - Casos de uso onde o framework se destaca
5. **Avaliar relevÃ¢ncia por contexto** â€” Filtrar frameworks pela adequaÃ§Ã£o ao:
   - Tipo de produto (SaaS, e-commerce, serviÃ§o, info-produto)
   - EstÃ¡gio de awareness do pÃºblico (unaware â†’ most aware)
   - Tom de voz definido no productBrief
6. **Mapear framework para seÃ§Ã£o** â€” Criar associaÃ§Ã£o direta:
   - Hero section: qual framework usar para headline e sub-headline
   - Features/Benefits: qual framework para apresentaÃ§Ã£o de benefÃ­cios
   - Social Proof: qual abordagem para prova social
   - CTA: qual tÃ©cnica de persuasÃ£o para call-to-action
   - ObjeÃ§Ãµes: qual framework para tratamento de dÃºvidas
7. **Compilar copyExpertsReport** â€” Gerar relatÃ³rio com perfil de cada especialista, frameworks documentados e justificativa de relevÃ¢ncia.
8. **Gerar recommendedFrameworks** â€” Exportar array estruturado com framework, seÃ§Ã£o-alvo, especialista de origem e prioridade.
9. **Validar post-conditions** â€” Confirmar mÃ­nimo de 3 especialistas, frameworks documentados e mapeamento completo.

