---
task: identifyAudience()
responsavel: "Scout"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com informaÃ§Ãµes de mercado-alvo (source: discoverProduct())"
  - nome: competitorAnalysis
    tipo: file
    obrigatorio: false
    descricao: "AnÃ¡lise de concorrentes para enriquecer perfil de audiÃªncia (source: researchCompetitors())"

Saida:
  - nome: audienceProfile
    tipo: file
    obrigatorio: true
    descricao: "Perfil detalhado de personas primÃ¡ria e secundÃ¡ria com dados demogrÃ¡ficos, psicogrÃ¡ficos e comportamentais (destination: synthesizeResearch() + lp-copywriter)"
  - nome: painPoints
    tipo: array
    obrigatorio: true
    descricao: "Lista de dores e frustraÃ§Ãµes do pÃºblico-alvo com evidÃªncias (destination: lp-copywriter)"

Checklist:
  pre-conditions:
    - "[ ] productBrief existe com informaÃ§Ãµes de mercado-alvo"
  post-conditions:
    - "[ ] Persona primÃ¡ria definida com dados demogrÃ¡ficos e psicogrÃ¡ficos"
    - "[ ] Persona secundÃ¡ria definida"
    - "[ ] MÃ­nimo 5 pain points mapeados com evidÃªncia"
    - "[ ] Buyer journey documentado (awareness â†’ consideration â†’ decision)"
    - "[ ] Linguagem e vocabulÃ¡rio do pÃºblico capturados"

Performance:
  duration_expected: "15 minutes"
  cacheable: true
  parallelizable: true

Tools:
  - WebSearch
  - WebFetch
---

# identifyAudience()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  productBrief   â”‚â”€â”€â”€â”€â”€â”€>â”‚                    â”‚â”€â”€â”€â”€â”€â”€>â”‚  audienceProfile    â”‚
â”‚  (file)         â”‚       â”‚  identifyAudience  â”‚       â”‚  (file)             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  @Scout            â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  competitor     â”‚â”€â”€â”€â”€â”€â”€>â”‚                    â”‚â”€â”€â”€â”€â”€â”€>â”‚  painPoints         â”‚
â”‚  Analysis?      â”‚       â”‚  [WebSearch,       â”‚       â”‚  (array)            â”‚
â”‚  (file)         â”‚       â”‚   WebFetch]        â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â”‚
                                                               â–¼
                                                   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                   â”‚  synthesizeResearch() â”‚
                                                   â”‚  lp-copywriter       â”‚
                                                   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `identifyAudience()` constrÃ³i um perfil profundo do pÃºblico-alvo da landing page. O agente **Scout** pesquisa fÃ³runs, redes sociais, reviews e comunidades para entender quem Ã© o potencial cliente, o que o motiva, quais sÃ£o suas dores e como ele toma decisÃµes de compra.

O resultado vai muito alÃ©m de dados demogrÃ¡ficos â€” o Scout captura a **linguagem real** que o pÃºblico usa, os **pain points com evidÃªncia** (citaÃ§Ãµes, posts, reviews), e o **buyer journey** completo. Esses insights sÃ£o fundamentais para o copywriter produzir copy que ressoa emocionalmente com o pÃºblico.

Se a `competitorAnalysis` estiver disponÃ­vel, o Scout a utiliza para enriquecer o perfil com dados sobre como o pÃºblico interage com soluÃ§Ãµes concorrentes.

## Passos

1. **Carregar productBrief** â€” Extrair informaÃ§Ãµes iniciais de mercado-alvo, nicho e posicionamento.
2. **Carregar competitorAnalysis** (se disponÃ­vel) â€” Usar dados de concorrentes para identificar padrÃµes de pÃºblico compartilhado.
3. **Pesquisar perfil demogrÃ¡fico** â€” Usar `WebSearch` para encontrar dados sobre idade, gÃªnero, localizaÃ§Ã£o, renda e profissÃ£o do pÃºblico-alvo tÃ­pico do nicho.
4. **Pesquisar perfil psicogrÃ¡fico** â€” Investigar valores, crenÃ§as, aspiraÃ§Ãµes, medos e motivaÃ§Ãµes:
   - FÃ³runs (Reddit, Quora, comunidades de nicho)
   - Reviews de produtos similares
   - Grupos em redes sociais
   - ComentÃ¡rios em blogs e vÃ­deos do nicho
5. **Mapear pain points** â€” Identificar as 5+ principais dores e frustraÃ§Ãµes, com evidÃªncia:
   - CitaÃ§Ãµes diretas do pÃºblico
   - PadrÃµes recorrentes em reclamaÃ§Ãµes
   - Gaps nÃ£o atendidos por soluÃ§Ãµes existentes
6. **Documentar buyer journey** â€” Mapear o caminho de decisÃ£o:
   - **Awareness:** Como o pÃºblico descobre o problema?
   - **Consideration:** Que soluÃ§Ãµes ele avalia? Que critÃ©rios usa?
   - **Decision:** O que faz ele escolher uma soluÃ§Ã£o? Quais objeÃ§Ãµes precisa superar?
7. **Capturar vocabulÃ¡rio** â€” Coletar palavras, expressÃµes e jargÃµes que o pÃºblico usa naturalmente para descrever o problema e a soluÃ§Ã£o desejada.
8. **Construir personas** â€” Criar persona primÃ¡ria e secundÃ¡ria com:
   - Nome fictÃ­cio, idade, profissÃ£o
   - Objetivos e motivaÃ§Ãµes
   - FrustraÃ§Ãµes e medos
   - Comportamento de compra
   - Canais de informaÃ§Ã£o preferidos
9. **Compilar audienceProfile** â€” Gerar documento completo com personas, pain points, buyer journey e vocabulÃ¡rio.
10. **Validar post-conditions** â€” Confirmar que ambas as personas estÃ£o definidas, 5+ pain points com evidÃªncia e buyer journey documentado.

