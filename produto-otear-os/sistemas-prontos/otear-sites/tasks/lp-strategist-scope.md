---
task: defineScope()
responsavel: "Strategos"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: questionnaireAnswers
    tipo: file
    obrigatorio: true
    descricao: "Respostas completas do questionÃ¡rio de requisitos (source: elicitRequirements())"
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto (source: discoverProduct())"

Saida:
  - nome: scopeDefinition
    tipo: file
    obrigatorio: true
    descricao: "DefiniÃ§Ã£o de escopo com componentes ativados/desativados e regras de build (destination: all agents)"
  - nome: conditionalFlags
    tipo: object
    obrigatorio: true
    descricao: "Flags booleanos para mÃ³dulos condicionais: backend, whatsapp, email, admin (destination: orchestrator)"

Checklist:
  pre-conditions:
    - "[ ] questionnaireAnswers completo e validado"
  post-conditions:
    - "[ ] scopeDefinition contÃ©m lista de componentes ativados/desativados"
    - "[ ] conditionalFlags contÃ©m booleans para backend, whatsapp, email e admin"
    - "[ ] Nenhum componente condicional ficou sem flag definido"
    - "[ ] Escopo Ã© consistente com as respostas do questionÃ¡rio"

Performance:
  duration_expected: "5 minutes"
  cacheable: true
  parallelizable: false
---

# defineScope()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  questionnaireAnswers â”‚â”€â”€â”€â”€â”€â”€>â”‚                â”‚â”€â”€â”€â”€â”€â”€>â”‚  scopeDefinition    â”‚
â”‚  (file)               â”‚       â”‚  defineScope   â”‚       â”‚  (file)             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  @Strategos    â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  productBrief         â”‚â”€â”€â”€â”€â”€â”€>â”‚                â”‚â”€â”€â”€â”€â”€â”€>â”‚  conditionalFlags   â”‚
â”‚  (file)               â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  (object)           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                                  â”‚
                                                                  â–¼
                                                      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                                      â”‚  all agents         â”‚
                                                      â”‚  orchestrator       â”‚
                                                      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `defineScope()` transforma as respostas do questionÃ¡rio e o product brief em uma **definiÃ§Ã£o de escopo executÃ¡vel**. O agente **Strategos** analisa os requisitos capturados e determina quais componentes da landing page serÃ£o ativados ou desativados.

Esta task Ã© uma Molecule â€” combina dados de duas fontes para produzir uma decisÃ£o estruturada. O `scopeDefinition` Ã© o contrato que todos os agentes downstream respeitam: se um componente estÃ¡ desativado, nenhum agente gasta tempo nele. Os `conditionalFlags` orientam o orchestrator sobre quais pipelines paralelas precisam ser executadas.

## Passos

1. **Carregar inputs** â€” Ler `questionnaireAnswers` e `productBrief` para contexto completo.
2. **Mapear respostas para componentes** â€” Correlacionar cada resposta do questionÃ¡rio com os componentes disponÃ­veis no template da landing page (hero, features, testimonials, pricing, FAQ, contact form, etc.).
3. **Avaliar componentes obrigatÃ³rios** â€” Marcar componentes que sÃ£o sempre incluÃ­dos (hero, CTA primÃ¡rio, footer).
4. **Avaliar componentes opcionais** â€” Com base nas respostas, ativar ou desativar componentes como pricing table, testimonials, FAQ, blog preview, etc.
5. **Definir conditional flags** â€” Gerar os booleans:
   - `backend`: true se o usuÃ¡rio precisa de API, banco de dados ou autenticaÃ§Ã£o
   - `whatsapp`: true se integraÃ§Ã£o com WhatsApp foi solicitada
   - `email`: true se captura de leads por email foi requisitada
   - `admin`: true se painel administrativo Ã© necessÃ¡rio
6. **Gerar scopeDefinition** â€” Compilar documento com lista completa de componentes (ativados/desativados), justificativa para cada decisÃ£o e regras de build.
7. **Validar consistÃªncia** â€” Verificar que o escopo Ã© coerente com as respostas do questionÃ¡rio e que nenhum flag condicional ficou indefinido.
8. **Distribuir outputs** â€” Disponibilizar `scopeDefinition` para todos os agentes e `conditionalFlags` para o orchestrator.

