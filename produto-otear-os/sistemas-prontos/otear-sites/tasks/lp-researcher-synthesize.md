---
task: synthesizeResearch()
responsavel: "Scout"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: competitorAnalysis
    tipo: file
    obrigatorio: true
    descricao: "AnÃ¡lise detalhada de concorrentes diretos e indiretos (source: researchCompetitors())"
  - nome: audienceProfile
    tipo: file
    obrigatorio: true
    descricao: "Perfil de personas com pain points e buyer journey (source: identifyAudience())"
  - nome: copyExpertsReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de especialistas de copy com frameworks recomendados (source: researchCopyExperts())"

Saida:
  - nome: researchSynthesis
    tipo: file
    obrigatorio: true
    descricao: "Briefing unificado com insights acionÃ¡veis priorizados por impacto de conversÃ£o (destination: lp-copywriter + lp-design-architect + all agents)"

Checklist:
  pre-conditions:
    - "[ ] competitorAnalysis existe e estÃ¡ completo"
    - "[ ] audienceProfile existe e estÃ¡ completo"
    - "[ ] copyExpertsReport existe e estÃ¡ completo"
  post-conditions:
    - "[ ] Briefing unificado gerado com dados dos 3 inputs"
    - "[ ] Insights priorizados por impacto de conversÃ£o"
    - "[ ] ContradiÃ§Ãµes entre fontes identificadas e resolvidas"
    - "[ ] RecomendaÃ§Ãµes acionÃ¡veis para copy, design e estrutura"

Performance:
  duration_expected: "8 minutes"
  cacheable: true
  parallelizable: false
---

# synthesizeResearch()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  competitorAnalysis  â”‚â”€â”€â”€â”
â”‚  (file)              â”‚   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                           â”œâ”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€>â”‚  researchSynthesis  â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚     â”‚  synthesizeResearch  â”‚     â”‚  (file)             â”‚
â”‚  audienceProfile     â”‚â”€â”€â”€â”¤     â”‚  @Scout              â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  (file)              â”‚   â”‚     â”‚                      â”‚              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â–¼
                           â”‚                                â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚                                â”‚  lp-copywriter      â”‚
â”‚  copyExpertsReport   â”‚â”€â”€â”€â”˜                                â”‚  lp-design-architectâ”‚
â”‚  (file)              â”‚                                    â”‚  all agents         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `synthesizeResearch()` Ã© o ponto de convergÃªncia de toda a pesquisa conduzida pelo agente **Scout**. Ela recebe os trÃªs outputs de pesquisa â€” competitorAnalysis, audienceProfile e copyExpertsReport â€” e os funde em um **briefing unificado e acionÃ¡vel**.

O valor principal desta task Ã© a **priorizaÃ§Ã£o por impacto de conversÃ£o**. Em vez de simplesmente concatenar relatÃ³rios, o Scout cruza os dados para identificar:
- Quais pain points do pÃºblico sÃ£o menos atendidos pelos concorrentes (oportunidade de diferenciaÃ§Ã£o)
- Quais frameworks de copy sÃ£o mais eficazes para o perfil de audiÃªncia identificado
- Quais padrÃµes de design dos concorrentes demonstram melhores prÃ¡ticas vs oportunidades de melhoria
- Onde existem contradiÃ§Ãµes entre as fontes e como resolvÃª-las

O `researchSynthesis` se torna o documento de referÃªncia principal para copywriter e design architect.

## Passos

1. **Carregar os 3 inputs** â€” Ler `competitorAnalysis`, `audienceProfile` e `copyExpertsReport` em sua totalidade.
2. **Cruzar pain points com gaps competitivos** â€” Identificar quais dores do pÃºblico (do audienceProfile) sÃ£o mal atendidas pelos concorrentes (do competitorAnalysis). Estas sÃ£o as maiores oportunidades de conversÃ£o.
3. **Cruzar frameworks com perfil de audiÃªncia** â€” Avaliar quais frameworks recomendados (do copyExpertsReport) sÃ£o mais eficazes para o estÃ¡gio de awareness e perfil psicogrÃ¡fico das personas.
4. **Identificar padrÃµes de design vencedores** â€” Extrair os padrÃµes de design mais comuns entre concorrentes bem-sucedidos e marcar oportunidades de diferenciaÃ§Ã£o visual.
5. **Detectar contradiÃ§Ãµes** â€” Identificar dados conflitantes entre as fontes (ex: competitorAnalysis sugere tom formal, mas audienceProfile indica pÃºblico que prefere casual). Resolver com justificativa.
6. **Priorizar insights** â€” Classificar cada insight por impacto estimado de conversÃ£o:
   - **Alto impacto:** Diretamente afeta decisÃ£o de compra
   - **MÃ©dio impacto:** Influencia percepÃ§Ã£o e confianÃ§a
   - **Baixo impacto:** Nice-to-have, diferenciaÃ§Ã£o sutil
7. **Gerar recomendaÃ§Ãµes acionÃ¡veis** â€” Para cada insight priorizado, traduzir em recomendaÃ§Ã£o especÃ­fica:
   - Para copy: qual mensagem, em qual seÃ§Ã£o, usando qual framework
   - Para design: qual padrÃ£o visual, em qual componente, por qual razÃ£o
   - Para estrutura: quais seÃ§Ãµes incluir, em qual ordem, com qual peso
8. **Compilar researchSynthesis** â€” Gerar briefing unificado com seÃ§Ãµes claras: Executive Summary, Oportunidades de DiferenciaÃ§Ã£o, RecomendaÃ§Ãµes de Copy, RecomendaÃ§Ãµes de Design, RecomendaÃ§Ãµes de Estrutura, ContradiÃ§Ãµes Resolvidas.
9. **Validar post-conditions** â€” Confirmar que o briefing cobre dados dos 3 inputs, insights estÃ£o priorizados e recomendaÃ§Ãµes sÃ£o acionÃ¡veis.

