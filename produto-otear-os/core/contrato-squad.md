---
title: Contrato de Squad do Otear OS
created: 2026-08-22
tags: [otear-os, squad, contrato]
---

# Contrato de Squad do Otear OS

Um squad e um conjunto de agentes trabalhando em etapas.

## Estrutura

```yaml
id: squad-exemplo
name: Squad Exemplo
purpose: "Resultado que o squad entrega"
agents:
  - id: estrategista
    role: "Planeja"
  - id: executor
    role: "Executa"
workflow:
  - step: planejamento
    agent: estrategista
  - step: producao
    agent: executor
outputs:
  - entrega_final
acceptance_criteria:
  - "Criterio de pronto"
```

## Regra

Squad bom existe quando um unico agente nao resolve o trabalho com qualidade.

