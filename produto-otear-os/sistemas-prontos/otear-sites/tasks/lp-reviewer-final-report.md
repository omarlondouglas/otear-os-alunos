---
task: produceFinalReport()
responsavel: "Shield"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: copyScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de qualidade do copy por dimensÃ£o (source: reviewCopyQuality())"
  - nome: designScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de qualidade do design por dimensÃ£o (source: reviewDesignConsistency())"
  - nome: seoA11yScore
    tipo: object
    obrigatorio: true
    descricao: "Score numÃ©rico de SEO e acessibilidade por dimensÃ£o (source: reviewSeoAccessibility())"
  - nome: backendScore
    tipo: object
    obrigatorio: false
    descricao: "Score numÃ©rico de seguranÃ§a do backend por dimensÃ£o (source: reviewBackendSecurity())"
  - nome: integrationScore
    tipo: object
    obrigatorio: false
    descricao: "Score numÃ©rico de qualidade das integraÃ§Ãµes por dimensÃ£o (source: reviewIntegrations())"

Saida:
  - nome: finalReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio consolidado com scores, sumÃ¡rio executivo e action items priorizados (destination: orchestrator + user)"
  - nome: verdict
    tipo: string
    obrigatorio: true
    descricao: "Veredicto final â€” PASS, CONCERNS, NEEDS_WORK ou FAIL (destination: orchestrator)"

Checklist:
  pre-conditions:
    - "[ ] Todas as dimensÃµes de review aplicÃ¡veis foram concluÃ­das"
    - "[ ] copyScore gerado por reviewCopyQuality()"
    - "[ ] designScore gerado por reviewDesignConsistency()"
    - "[ ] seoA11yScore gerado por reviewSeoAccessibility()"
    - "[ ] backendScore gerado por reviewBackendSecurity() (se backend=true)"
    - "[ ] integrationScore gerado por reviewIntegrations() (se integraÃ§Ãµes ativas)"
  post-conditions:
    - "[ ] RelatÃ³rio consolidado com score por dimensÃ£o (0-10)"
    - "[ ] Score geral ponderado calculado"
    - "[ ] Veredicto emitido (PASS >=8.0, CONCERNS 6.0-7.9, NEEDS_WORK 4.0-5.9, FAIL <4.0)"
    - "[ ] SumÃ¡rio executivo presente"
    - "[ ] Action items priorizados para issues encontrados"

Performance:
  duration_expected: "8 minutes"
  cacheable: false
  parallelizable: false
---

# produceFinalReport()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  copyScore            â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  finalReport            â”‚
â”‚  (object, required)   â”‚       â”‚                      â”‚       â”‚  (file)                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  designScore          â”‚â”€â”€â”€â”€â”€â”€>â”‚  produceFinal        â”‚â”€â”€â”€â”€â”€â”€>â”‚  verdict                â”‚
â”‚  (object, required)   â”‚       â”‚  Report              â”‚       â”‚  (string)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  @Shield             â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  seoA11yScore         â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚               â”‚
â”‚  (object, required)   â”‚       â”‚                      â”‚               â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚               â–¼                  â–¼
â”‚  backendScore         â”‚â”€â”€?â”€â”€>â”‚                      â”‚       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  (object, optional)   â”‚       â”‚                      â”‚       â”‚ orchestrator â”‚   â”‚ user         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  integrationScore     â”‚â”€â”€?â”€â”€>
â”‚  (object, optional)   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

  â”€â”€?â”€â”€>  = condicional (sÃ³ se a dimensÃ£o for aplicÃ¡vel)

  Verdicts:
  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚  >= 8.0  â†’  PASS                           â”‚
  â”‚  6.0-7.9 â†’  CONCERNS                       â”‚
  â”‚  4.0-5.9 â†’  NEEDS_WORK                     â”‚
  â”‚  < 4.0   â†’  FAIL                           â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `produceFinalReport()` Ã© o **capstone do pipeline de review** â€” consolida os scores de todas as dimensÃµes de qualidade em um relatÃ³rio final unificado. O agente **Shield** agrega os resultados de copy, design, SEO/acessibilidade, seguranÃ§a do backend (se aplicÃ¡vel) e integraÃ§Ãµes (se aplicÃ¡veis) para produzir um veredicto objetivo e um relatÃ³rio acionÃ¡vel.

Esta task Ã© um Organism porque combina mÃºltiplos outputs de tasks anteriores (Analysis) em um artefato de nÃ­vel superior. O relatÃ³rio final serve tanto ao orchestrator (para decidir se o projeto estÃ¡ pronto para deploy) quanto ao usuÃ¡rio (para visibilidade do estado geral da qualidade).

O score geral Ã© ponderado dinamicamente: quando dimensÃµes opcionais (backend, integraÃ§Ãµes) nÃ£o sÃ£o aplicÃ¡veis, os pesos sÃ£o redistribuÃ­dos entre as dimensÃµes obrigatÃ³rias (copy, design, SEO/acessibilidade).

## Passos

1. **Carregar todos os scores** â€” Ler `copyScore`, `designScore`, `seoA11yScore` e, se disponÃ­veis, `backendScore` e `integrationScore`.
2. **Determinar dimensÃµes ativas** â€” Identificar quais dimensÃµes de review foram executadas (obrigatÃ³rias: copy, design, SEO/a11y; condicionais: backend, integraÃ§Ãµes).
3. **Normalizar scores** â€” Garantir que todos os scores estÃ£o na mesma escala (0-10) e que as subdimensÃµes de cada review estÃ£o corretamente agregadas.
4. **Calcular pesos dinÃ¢micos** â€” Redistribuir pesos entre as dimensÃµes ativas:
   - Se todas as 5 dimensÃµes: copy 25%, design 25%, SEO/a11y 25%, backend 15%, integraÃ§Ãµes 10%
   - Se 3 dimensÃµes (sem backend/integraÃ§Ãµes): copy 35%, design 35%, SEO/a11y 30%
   - Ajustes intermediÃ¡rios para 4 dimensÃµes
5. **Calcular score geral ponderado** â€” Aplicar os pesos dinÃ¢micos aos scores individuais para obter o score final.
6. **Determinar veredicto** â€” Aplicar as faixas de classificaÃ§Ã£o:
   - **PASS** (>= 8.0): Projeto pronto para deploy
   - **CONCERNS** (6.0-7.9): Deploy possÃ­vel com ressalvas documentadas
   - **NEEDS_WORK** (4.0-5.9): CorreÃ§Ãµes necessÃ¡rias antes do deploy
   - **FAIL** (< 4.0): Problemas crÃ­ticos que impedem o deploy
7. **Coletar BLOCKERs de todas as dimensÃµes** â€” Agregar todos os issues BLOCKER dos reviews individuais como action items prioritÃ¡rios.
8. **Redigir sumÃ¡rio executivo** â€” Criar um resumo de 3-5 parÃ¡grafos com: estado geral, destaques positivos, Ã¡reas de preocupaÃ§Ã£o e recomendaÃ§Ãµes principais.
9. **Priorizar action items** â€” Ordenar todos os issues encontrados por: (1) severidade (BLOCKER > WARNING > INFO), (2) impacto no score, (3) esforÃ§o estimado de correÃ§Ã£o.
10. **Compilar relatÃ³rio final** â€” Montar o `finalReport` com: sumÃ¡rio executivo, tabela de scores por dimensÃ£o, veredicto, lista de action items priorizados e detalhamento por dimensÃ£o.
11. **Gerar outputs** â€” Disponibilizar `finalReport` para orchestrator e user, e `verdict` como string para decisÃ£o automÃ¡tica do orchestrator.

