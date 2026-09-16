---
task: researchCompetitors()
responsavel: "Scout"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com mercado e indÃºstria (source: discoverProduct())"
  - nome: knownCompetitors
    tipo: array
    obrigatorio: false
    descricao: "Lista de concorrentes jÃ¡ conhecidos pelo usuÃ¡rio (source: questionnaire)"

Saida:
  - nome: competitorAnalysis
    tipo: file
    obrigatorio: true
    descricao: "AnÃ¡lise detalhada de concorrentes com padrÃµes de landing page, copy e design (destination: synthesizeResearch())"
  - nome: visualReferences
    tipo: array
    obrigatorio: true
    descricao: "ReferÃªncias visuais coletadas das landing pages dos concorrentes (destination: lp-design-architect)"

Checklist:
  pre-conditions:
    - "[ ] productBrief existe com informaÃ§Ãµes de mercado/indÃºstria"
  post-conditions:
    - "[ ] MÃ­nimo 5 concorrentes diretos analisados"
    - "[ ] MÃ­nimo 3 concorrentes indiretos analisados"
    - "[ ] PadrÃµes de estrutura de landing page capturados"
    - "[ ] PadrÃµes de copy capturados"
    - "[ ] PadrÃµes de design capturados"
    - "[ ] ReferÃªncias visuais coletadas e catalogadas"

Performance:
  duration_expected: "20 minutes"
  cacheable: true
  parallelizable: true

Tools:
  - WebSearch
  - WebFetch
---

# researchCompetitors()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  productBrief   â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  competitorAnalysis â”‚
â”‚  (file)         â”‚       â”‚  researchCompetitors â”‚       â”‚  (file)             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  @Scout              â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  knownCompeti-  â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  visualReferences   â”‚
â”‚  tors? (array)  â”‚       â”‚  [WebSearch,         â”‚       â”‚  (array)            â”‚
â”‚                 â”‚       â”‚   WebFetch]          â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”‚
                                                                 â–¼
                                                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                     â”‚  synthesizeResearch() â”‚
                                                     â”‚  lp-design-architect  â”‚
                                                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `researchCompetitors()` conduz uma pesquisa aprofundada do cenÃ¡rio competitivo. O agente **Scout** utiliza ferramentas de busca web (`WebSearch`, `WebFetch`) para encontrar, acessar e analisar as landing pages dos concorrentes diretos e indiretos do produto.

A anÃ¡lise vai alÃ©m de uma lista de concorrentes â€” o Scout examina a **estrutura** das landing pages (quais seÃ§Ãµes usam, em que ordem), os **padrÃµes de copy** (headlines, CTAs, prova social), e os **padrÃµes de design** (layout, cores, tipografia, imagens). O objetivo Ã© extrair intelligence acionÃ¡vel que informe as decisÃµes de copy e design da landing page do usuÃ¡rio.

Esta Ã© uma task Organism â€” envolve mÃºltiplas etapas de pesquisa externa, anÃ¡lise e sÃ­ntese, com dependÃªncia de ferramentas externas.

## Passos

1. **Carregar productBrief** â€” Extrair mercado, indÃºstria, nicho e keywords do produto para guiar a pesquisa.
2. **Identificar concorrentes diretos** â€” Usar `WebSearch` para encontrar empresas que oferecem produtos/serviÃ§os similares no mesmo mercado. Se `knownCompetitors` fornecidos, usÃ¡-los como ponto de partida.
3. **Identificar concorrentes indiretos** â€” Buscar soluÃ§Ãµes alternativas que o pÃºblico-alvo pode considerar (substitutos, adjacentes).
4. **Acessar landing pages** â€” Usar `WebFetch` para capturar o conteÃºdo das landing pages de cada concorrente.
5. **Analisar estrutura** â€” Para cada landing page, mapear:
   - SeÃ§Ãµes presentes e sua ordem (hero, features, social proof, pricing, FAQ, CTA)
   - PadrÃµes de navegaÃ§Ã£o e fluxo de conversÃ£o
   - Elementos above-the-fold vs below-the-fold
6. **Analisar copy** â€” Examinar:
   - Headlines e sub-headlines
   - CTAs (texto, posiÃ§Ã£o, frequÃªncia)
   - Prova social (tipo, quantidade, posiÃ§Ã£o)
   - Tratamento de objeÃ§Ãµes
7. **Analisar design** â€” Capturar:
   - Layout patterns (grid, full-width, cards)
   - Paleta de cores dominante
   - Tipografia e hierarquia visual
   - Uso de imagens, Ã­cones e vÃ­deo
8. **Coletar referÃªncias visuais** â€” Catalogar screenshots e URLs das melhores referÃªncias visuais encontradas.
9. **Compilar competitorAnalysis** â€” Gerar documento estruturado com anÃ¡lise comparativa, padrÃµes identificados e oportunidades de diferenciaÃ§Ã£o.
10. **Validar post-conditions** â€” Confirmar mÃ­nimo de 5 diretos + 3 indiretos, com padrÃµes de estrutura/copy/design documentados.

