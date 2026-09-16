---
task: selectDesignSystem()
responsavel: "Prism"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com USP, mercado-alvo, tom/voz e preferÃªncias visuais (source: discoverProduct())"
  - nome: userPreferences
    tipo: object
    obrigatorio: false
    descricao: "PreferÃªncias do usuÃ¡rio para stack visual â€” design system preferido, estilo, referÃªncias (source: elicitRequirements())"
  - nome: visualReferences
    tipo: array
    obrigatorio: false
    descricao: "ReferÃªncias visuais de concorrentes e benchmarks coletadas na pesquisa (source: researchCompetitors())"

Saida:
  - nome: dsSelection
    tipo: file
    obrigatorio: true
    descricao: "Documento de seleÃ§Ã£o do design system com escolha, justificativa e configuraÃ§Ã£o base (destination: defineDesignTokens())"
  - nome: dsRationale
    tipo: string
    obrigatorio: true
    descricao: "Resumo da justificativa de seleÃ§Ã£o para registro no documento de ideaÃ§Ã£o (destination: IDEATION.md)"

Checklist:
  pre-conditions:
    - "[ ] productBrief existe com preferÃªncias de marca/visual definidas"
    - "[ ] productBrief contÃ©m tipo de produto e pÃºblico-alvo"
  post-conditions:
    - "[ ] Design system base selecionado (shadcn/ui, Chakra, Material, Mantine ou Custom)"
    - "[ ] Rationale documenta por que o DS foi escolhido sobre as alternativas"
    - "[ ] SeleÃ§Ã£o considera tipo de produto e identidade de marca"
    - "[ ] SeleÃ§Ã£o considera requisitos de acessibilidade"
    - "[ ] ConfiguraÃ§Ã£o base do DS documentada (tema, variantes, extensÃµes necessÃ¡rias)"
    - "[ ] dsRationale registrado em IDEATION.md"

Performance:
  duration_expected: "5 minutes"
  cacheable: true
  parallelizable: false
---

# selectDesignSystem()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  productBrief    â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  dsSelection        â”‚
â”‚  (file)          â”‚       â”‚                      â”‚       â”‚  (file)             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  selectDesignSystem  â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  userPreferences â”‚â”€â”€â”€â”€â”€â”€>â”‚  @Prism              â”‚â”€â”€â”€â”€â”€â”€>â”‚  dsRationale        â”‚
â”‚  (object)?       â”‚       â”‚                      â”‚       â”‚  (string)           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚                      â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  visualReferencesâ”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚               â”‚
â”‚  (array)?        â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜               â–¼
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                          â”‚  defineDesignTokens â”‚
                                                          â”‚  IDEATION.md        â”‚
                                                          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `selectDesignSystem()` Ã© a **decisÃ£o estratÃ©gica de fundaÃ§Ã£o visual** da landing page. O agente **Prism** analisa o briefing do produto, as preferÃªncias do usuÃ¡rio e as referÃªncias visuais dos concorrentes para selecionar o design system mais adequado como base da implementaÃ§Ã£o.

A seleÃ§Ã£o nÃ£o Ã© meramente tÃ©cnica â€” ela considera o tipo de produto (SaaS, e-commerce, app, serviÃ§o), a identidade de marca desejada (minimalista, vibrante, corporativo, playful), os requisitos de acessibilidade (WCAG AA/AAA) e a capacidade de customizaÃ§Ã£o do DS escolhido.

As opÃ§Ãµes avaliadas sÃ£o: **shadcn/ui** (alta customizaÃ§Ã£o, Tailwind-native), **Chakra UI** (developer-friendly, flexÃ­vel), **Material UI** (enterprise, estabelecido), **Mantine** (moderno, feature-rich) ou **Custom** (quando nenhum DS existente atende aos requisitos visuais). O output alimenta diretamente `defineDesignTokens()`, que construirÃ¡ o sistema de tokens sobre a base escolhida.

## Passos

1. **Analisar productBrief** â€” Extrair tipo de produto, identidade de marca, pÃºblico-alvo e quaisquer preferÃªncias visuais declaradas.
2. **Processar userPreferences** â€” Se fornecidas, integrar as preferÃªncias explÃ­citas do usuÃ¡rio (DS preferido, estilo, restriÃ§Ãµes tÃ©cnicas).
3. **Avaliar visualReferences** â€” Analisar as referÃªncias visuais dos concorrentes para identificar padrÃµes de design do setor e oportunidades de diferenciaÃ§Ã£o.
4. **Mapear requisitos do DS** â€” Listar requisitos obrigatÃ³rios: acessibilidade, responsividade, dark mode, animaÃ§Ãµes, componentes necessÃ¡rios, nÃ­vel de customizaÃ§Ã£o.
5. **Avaliar candidatos** â€” Analisar cada DS candidato (shadcn/ui, Chakra, Material, Mantine, Custom) contra os requisitos mapeados, atribuindo scores.
6. **Selecionar DS base** â€” Escolher o DS com melhor fit geral, priorizando: adequaÃ§Ã£o Ã  identidade de marca > customizabilidade > ecosistema > performance.
7. **Documentar rationale** â€” Escrever justificativa clara explicando por que o DS selecionado Ã© superior Ã s alternativas para este caso especÃ­fico.
8. **Definir configuraÃ§Ã£o base** â€” Documentar o setup inicial do DS: tema base, variantes necessÃ¡rias, extensÃµes/plugins, integraÃ§Ãµes com Tailwind.
9. **Gerar dsSelection** â€” Compilar o documento de seleÃ§Ã£o completo com escolha, rationale, configuraÃ§Ã£o e roadmap de customizaÃ§Ã£o.
10. **Registrar em IDEATION.md** â€” Gravar o `dsRationale` no documento de ideaÃ§Ã£o para rastreabilidade da decisÃ£o.

