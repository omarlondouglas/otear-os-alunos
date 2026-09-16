---
task: elicitRequirements()
responsavel: "Strategos"
responsavel_type: Agente
atomic_layer: Organism
elicit: true

Entrada:
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto gerado por discoverProduct() (source: discoverProduct())"

Saida:
  - nome: questionnaireAnswers
    tipo: file
    obrigatorio: true
    descricao: "Respostas completas do questionÃ¡rio com 10 perguntas obrigatÃ³rias e condicionais (destination: defineScope())"
  - nome: userPreferences
    tipo: object
    obrigatorio: true
    descricao: "PreferÃªncias visuais e funcionais do usuÃ¡rio extraÃ­das das respostas (destination: lp-design-architect)"

Checklist:
  pre-conditions:
    - "[ ] productBrief existe e estÃ¡ completo"
  post-conditions:
    - "[ ] Todas as 10 perguntas obrigatÃ³rias foram respondidas"
    - "[ ] Flags condicionais (backend, whatsapp, email) definidos"
    - "[ ] PreferÃªncias do usuÃ¡rio extraÃ­das e estruturadas"
    - "[ ] Nenhuma pergunta obrigatÃ³ria ficou sem resposta"

Performance:
  duration_expected: "15 minutes"
  cacheable: false
  parallelizable: false
---

# elicitRequirements()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  productBrief   â”‚â”€â”€â”€â”€â”€â”€>â”‚                      â”‚â”€â”€â”€â”€â”€â”€>â”‚  questionnaireAnswers â”‚
â”‚  (file)         â”‚       â”‚  elicitRequirements  â”‚       â”‚  (file)               â”‚
â”‚                 â”‚       â”‚  @Strategos          â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                 â”‚       â”‚  [elicit: true]      â”‚â”€â”€â”€â”€â”€â”€>â”‚  userPreferences      â”‚
â”‚                 â”‚       â”‚                      â”‚       â”‚  (object)             â”‚
â”‚                 â”‚       â”‚    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚                 â”‚       â”‚    â”‚ USER INPUT   â”‚  â”‚               â”‚
â”‚                 â”‚       â”‚    â”‚ (interactive)â”‚  â”‚               â–¼
â”‚                 â”‚       â”‚    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                 â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  defineScope()        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                      â”‚  lp-design-architect  â”‚
                                                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `elicitRequirements()` Ã© uma task **interativa** (`elicit: true`) que conduz o usuÃ¡rio atravÃ©s de um questionÃ¡rio estruturado para capturar requisitos especÃ­ficos da landing page. O agente **Strategos** utiliza o Product Brief como contexto para formular perguntas inteligentes e relevantes.

O questionÃ¡rio contÃ©m 10 perguntas obrigatÃ³rias que cobrem objetivos de conversÃ£o, funcionalidades desejadas, integraÃ§Ãµes necessÃ¡rias e preferÃªncias visuais. Perguntas condicionais sÃ£o ativadas com base nas respostas (ex: se o usuÃ¡rio quer captura de leads, perguntas sobre backend e email sÃ£o desbloqueadas).

Esta task Ã© o principal ponto de interaÃ§Ã£o humana no pipeline e determina o escopo real do projeto.

## Passos

1. **Carregar Product Brief** â€” Ler o productBrief gerado por `discoverProduct()` para contextualizar as perguntas.
2. **Preparar questionÃ¡rio base** â€” Montar as 10 perguntas obrigatÃ³rias com base no template e no contexto do produto.
3. **Apresentar perguntas ao usuÃ¡rio** â€” Exibir cada pergunta de forma clara, com exemplos e defaults inteligentes derivados do productBrief.
4. **Capturar respostas** â€” Registrar cada resposta, validando completude e coerÃªncia.
5. **Avaliar flags condicionais** â€” Com base nas respostas, determinar se backend, integraÃ§Ã£o WhatsApp, captura de email e painel admin sÃ£o necessÃ¡rios.
6. **Desbloquear perguntas condicionais** â€” Se flags ativados, apresentar perguntas adicionais especÃ­ficas (ex: provedor de email, nÃºmero WhatsApp, tipo de backend).
7. **Extrair preferÃªncias do usuÃ¡rio** â€” Compilar preferÃªncias visuais (cores, estilo, referÃªncias) e funcionais (seÃ§Ãµes desejadas, CTAs, formulÃ¡rios).
8. **Gerar questionnaireAnswers** â€” Salvar todas as respostas em arquivo estruturado.
9. **Gerar userPreferences** â€” Exportar preferÃªncias extraÃ­das como objeto para o lp-design-architect.
10. **Validar post-conditions** â€” Confirmar que todas as perguntas obrigatÃ³rias foram respondidas e flags definidos.

