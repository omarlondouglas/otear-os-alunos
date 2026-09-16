---
task: reviewCopyQuality()
responsavel: "Shield"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: allSectionsCopy
    tipo: array<file>
    obrigatorio: true
    descricao: "Copy de todas as seÃ§Ãµes da landing page (source: writeSectionCopy() iteraÃ§Ãµes)"
  - nome: toneReviewReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de revisÃ£o de tom e voz (source: reviewCopyTone())"
  - nome: researchSynthesis
    tipo: file
    obrigatorio: true
    descricao: "SÃ­ntese consolidada das pesquisas de mercado, concorrÃªncia e pÃºblico-alvo (source: synthesizeResearch())"

Saida:
  - nome: copyReview
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio detalhado de revisÃ£o de qualidade do copy com issues e sugestÃµes (destination: lp-copywriter para correÃ§Ãµes)"
  - nome: copyScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de qualidade do copy por dimensÃ£o (destination: produceFinalReport())"

Checklist:
  pre-conditions:
    - "[ ] Todas as seÃ§Ãµes possuem copy gerado por writeSectionCopy()"
    - "[ ] RevisÃ£o de tom concluÃ­da por reviewCopyTone()"
    - "[ ] researchSynthesis disponÃ­vel para validaÃ§Ã£o de claims"
  post-conditions:
    - "[ ] Cada seÃ§Ã£o pontuada em: clareza (20%), persuasÃ£o (20%), eficÃ¡cia do CTA (20%), consistÃªncia (15%), gramÃ¡tica (10%), uso de framework (15%)"
    - "[ ] Issues categorizados como BLOCKER/WARNING/INFO"
    - "[ ] SugestÃµes especÃ­ficas de correÃ§Ã£o fornecidas para cada issue"

Performance:
  duration_expected: "10 minutes"
  cacheable: false
  parallelizable: false
---

# reviewCopyQuality()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  allSectionsCopy      â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  copyReview             â”‚
â”‚  (array<file>)        â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  reviewCopyQuality   â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  toneReviewReport     â”‚â”€â”€â”€â”€â”€â”€>â”‚  @Shield             â”‚â”€â”€â”€â”€â”€â”€>â”‚  copyScore              â”‚
â”‚  (file)               â”‚       â”‚                      â”‚       â”‚  (object)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  researchSynthesis    â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚               â”‚
â”‚  (file)               â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                              â–¼                  â–¼
                                                               â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                               â”‚ lp-copywriterâ”‚   â”‚ produceFinal â”‚
                                                               â”‚ (para fixes) â”‚   â”‚ Report()     â”‚
                                                               â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `reviewCopyQuality()` realiza uma **anÃ¡lise qualitativa e quantitativa** de todo o copy produzido para a landing page. O agente **Shield** avalia cada seÃ§Ã£o individualmente e o conjunto como um todo, aplicando critÃ©rios de qualidade ponderados para produzir um score objetivo.

O review analisa seis dimensÃµes com pesos definidos: clareza (20%), persuasÃ£o (20%), eficÃ¡cia do CTA (20%), consistÃªncia entre seÃ§Ãµes (15%), gramÃ¡tica e ortografia (10%) e uso correto do framework de copywriting (15%). Cada issue encontrado Ã© categorizado por severidade (BLOCKER para problemas que impedem publicaÃ§Ã£o, WARNING para melhorias recomendadas e INFO para sugestÃµes opcionais) e acompanhado de uma sugestÃ£o especÃ­fica de correÃ§Ã£o.

## Passos

1. **Carregar todos os inputs** â€” Ler `allSectionsCopy`, `toneReviewReport` e `researchSynthesis` para contexto completo.
2. **Analisar clareza (20%)** â€” Para cada seÃ§Ã£o, avaliar se a mensagem Ã© compreensÃ­vel em primeira leitura, sem ambiguidades ou jargÃ£o desnecessÃ¡rio.
3. **Analisar persuasÃ£o (20%)** â€” Verificar se o copy utiliza tÃ©cnicas persuasivas adequadas ao pÃºblico-alvo, se os argumentos sÃ£o embasados na pesquisa e se a proposta de valor estÃ¡ clara.
4. **Analisar eficÃ¡cia do CTA (20%)** â€” Avaliar se cada CTA Ã© claro, urgente quando apropriado, e se o microcopy de suporte reduz objeÃ§Ãµes.
5. **Analisar consistÃªncia (15%)** â€” Verificar coerÃªncia de tom, voz, terminologia e nÃ­vel de formalidade entre todas as seÃ§Ãµes, usando o `toneReviewReport` como referÃªncia.
6. **Analisar gramÃ¡tica e ortografia (10%)** â€” Verificar correÃ§Ã£o gramatical, pontuaÃ§Ã£o, concordÃ¢ncia e ortografia em todo o copy.
7. **Analisar uso de framework (15%)** â€” Verificar se os frameworks de copywriting foram aplicados corretamente em cada seÃ§Ã£o e se os elementos obrigatÃ³rios do framework estÃ£o presentes.
8. **Categorizar issues** â€” Classificar cada problema encontrado como BLOCKER (impede publicaÃ§Ã£o), WARNING (recomendaÃ§Ã£o forte) ou INFO (sugestÃ£o opcional).
9. **Gerar sugestÃµes de correÃ§Ã£o** â€” Para cada issue BLOCKER e WARNING, fornecer uma sugestÃ£o especÃ­fica de reescrita ou ajuste.
10. **Calcular scores** â€” Computar score por dimensÃ£o e score geral ponderado para cada seÃ§Ã£o e para o conjunto.
11. **Gerar outputs** â€” Produzir `copyReview` com detalhamento completo e `copyScore` com os valores numÃ©ricos para o relatÃ³rio final.

