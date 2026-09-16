---
task: reviewCopyTone()
responsavel: "Quill"
responsavel_type: Agente
atomic_layer: Atom

Entrada:
  - nome: allSectionsCopy
    tipo: array<file>
    obrigatorio: true
    descricao: "Todos os copies de seÃ§Ãµes gerados pelas iteraÃ§Ãµes de writeSectionCopy() (source: writeSectionCopy() iterations)"
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com USP, mercado-alvo, tom/voz e posicionamento (source: discoverProduct())"

Saida:
  - nome: toneReviewReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio de revisÃ£o de tom/voz com inconsistÃªncias encontradas e correÃ§Ãµes aplicadas (destination: lp-reviewer)"
  - nome: correctedCopy
    tipo: array<file>
    obrigatorio: true
    descricao: "Copies de todas as seÃ§Ãµes com tom/voz harmonizado e correÃ§Ãµes aplicadas (destination: lp-frontend-dev)"

Checklist:
  pre-conditions:
    - "[ ] Todas as seÃ§Ãµes possuem copy escrito por writeSectionCopy()"
    - "[ ] productBrief existe com tom/voz e brand voice definidos"
  post-conditions:
    - "[ ] Tom/voz consistente em TODAS as seÃ§Ãµes"
    - "[ ] Nenhuma contradiÃ§Ã£o de messaging entre seÃ§Ãµes"
    - "[ ] Brand voice mantida conforme productBrief"
    - "[ ] TransiÃ§Ãµes entre seÃ§Ãµes fluem naturalmente"
    - "[ ] Terminologia tÃ©cnica uniforme em toda a landing page"
    - "[ ] toneReviewReport documenta todas as alteraÃ§Ãµes realizadas"

Performance:
  duration_expected: "6 minutes"
  cacheable: false
  parallelizable: false
---

# reviewCopyTone()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  allSectionsCopy â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  toneReviewReport   â”‚
â”‚  (array<file>)   â”‚       â”‚  reviewCopyTone      â”‚       â”‚  (file)             â”‚
â”‚  [hero,          â”‚       â”‚  @Quill              â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚   problem,       â”‚       â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  correctedCopy      â”‚
â”‚   benefits,      â”‚       â”‚                      â”‚       â”‚  (array<file>)      â”‚
â”‚   social-proof,  â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚   cta, ...]      â”‚               â–²                              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤               â”‚                              â–¼
â”‚  productBrief    â”‚â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  (file)          â”‚                                      â”‚  lp-reviewer        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â”‚  lp-frontend-dev    â”‚
                                                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `reviewCopyTone()` Ã© a etapa de **harmonizaÃ§Ã£o final** de todo o copy da landing page. ApÃ³s todas as seÃ§Ãµes terem sido escritas individualmente por `writeSectionCopy()`, o agente **Quill** revisa o conjunto completo para garantir consistÃªncia de tom, voz, terminologia e messaging.

Como cada seÃ§Ã£o Ã© escrita de forma iterativa e independente, podem surgir inconsistÃªncias sutis â€” variaÃ§Ãµes no nÃ­vel de formalidade, contradiÃ§Ãµes entre promessas de diferentes seÃ§Ãµes, ou mudanÃ§as involuntÃ¡rias no vocabulÃ¡rio tÃ©cnico. Esta task funciona como um "quality pass" editorial que unifica a experiÃªncia de leitura de ponta a ponta.

O output inclui tanto um relatÃ³rio detalhado das inconsistÃªncias encontradas e correÃ§Ãµes aplicadas (para o reviewer validar) quanto os copies corrigidos prontos para implementaÃ§Ã£o pelo frontend.

## Passos

1. **Carregar todos os copies de seÃ§Ãµes** â€” Reunir todos os outputs de `writeSectionCopy()` na ordem de fluxo da landing page (hero -> problem-agitation -> benefits -> social-proof -> features -> CTA -> FAQ -> footer).
2. **Extrair referÃªncia de tom/voz** â€” Ler o `productBrief` e extrair as diretrizes de brand voice, tom, nÃ­vel de formalidade e vocabulÃ¡rio preferido.
3. **Analisar consistÃªncia de tom** â€” Comparar o tom de cada seÃ§Ã£o contra a referÃªncia e entre si, identificando variaÃ§Ãµes de formalidade, energia ou estilo.
4. **Detectar contradiÃ§Ãµes de messaging** â€” Verificar se promessas, nÃºmeros, claims ou posicionamento se contradizem entre seÃ§Ãµes diferentes.
5. **Auditar terminologia** â€” Garantir que termos tÃ©cnicos, nomes de features e vocabulÃ¡rio especÃ­fico do produto sÃ£o usados de forma uniforme em todas as seÃ§Ãµes.
6. **Avaliar transiÃ§Ãµes** â€” Verificar se o fluxo narrativo entre seÃ§Ãµes Ã© fluido e se cada seÃ§Ã£o conecta naturalmente com a seguinte.
7. **Aplicar correÃ§Ãµes** â€” Corrigir as inconsistÃªncias encontradas, mantendo a essÃªncia e o impacto de cada seÃ§Ã£o original.
8. **Gerar relatÃ³rio de revisÃ£o** â€” Documentar cada inconsistÃªncia encontrada, a seÃ§Ã£o afetada, o tipo de problema e a correÃ§Ã£o aplicada no `toneReviewReport`.
9. **Produzir copies corrigidos** â€” Gerar o `correctedCopy` com todas as seÃ§Ãµes harmonizadas e prontas para implementaÃ§Ã£o.
10. **Validar contra post-conditions** â€” Verificar que todas as condiÃ§Ãµes de saÃ­da foram atendidas antes de entregar os outputs.

