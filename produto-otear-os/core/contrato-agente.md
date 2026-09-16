---
title: Contrato de Agente do Otear OS
created: 2026-08-22
tags: [otear-os, agente, contrato]
---

# Contrato de Agente do Otear OS

Um agente e uma funcao especializada dentro do Otear OS.

## Estrutura

```yaml
id: agente-exemplo
name: Agente Exemplo
role: "Papel do agente"
mission: "Resultado que o agente deve produzir"
inputs:
  - briefing
outputs:
  - entrega_final
tools:
  - ferramenta_permitida
memory:
  - biblioteca_permitida
quality_check:
  - "Criterio de pronto"
```

## Regra

Agente bom tem missao estreita, entrada clara e saida verificavel.

