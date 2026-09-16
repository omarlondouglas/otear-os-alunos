# Task: route-briefing

```yaml
id: route-briefing
version: "1.0.0"
title: "Route Briefing to Specialist"
description: >
  Recebe briefing validado e determina: (1) qual especialista executa
  e (2) qual estilo/copywriter usar. Usa routing-matrix.yaml para
  decisão automática quando copywriter não especificado.
elicit: false
owner: copy-chief
executor: copy-chief
outputs:
  - Briefing enriquecido com specialist_id e copywriter selecionados
  - Justificativa da seleção
```

## When This Task Runs

- Após validate-briefing retornar briefing válido
- Copy Chief precisa decidir para quem enviar

## Routing Logic

### Step 1: Select Specialist by Canal

| Canal | Specialist |
|-------|-----------|
| ads | @ads-specialist |
| email | @email-specialist |
| landing | @landing-specialist |
| social | @social-specialist |

### Step 2: Select Copywriter/Style

- SE `briefing.copywriter` especificado → usar o especificado (override)
- SE NÃO especificado → consultar Style Selection Matrix:

| Canal | Público Frio | Público Morno | Público Quente | B2B |
|-------|-------------|---------------|----------------|-----|
| ads | halbert | kennedy | schwartz | ogilvy |
| email | schwartz | ogilvy | kennedy | ogilvy |
| landing | schwartz | halbert | kennedy | ogilvy |
| social | halbert | schwartz | kennedy | ogilvy |

### Step 3: Determine Audience Temperature

Inferir temperatura do público a partir do briefing:
- **Frio**: sem menção de awareness, público genérico, topo de funil
- **Morno**: alguma familiaridade, retargeting leve, meio de funil
- **Quente**: lista engajada, carrinho abandonado, fundo de funil
- **B2B**: público corporativo, decisores, profissionais

### Step 4: Enrich Briefing

```yaml
# Campos adicionados pelo routing
_routing:
  specialist_id: "{specialist selecionado}"
  copywriter: "{copywriter selecionado}"
  audience_temperature: "{frio|morno|quente|b2b}"
  selection_reason: "{justificativa da seleção}"
```

### Step 5: Dispatch to Specialist

Passar briefing enriquecido ao especialista com instrução:
- Estilo do copywriter selecionado
- Consultar knowledge-base antes de gerar
- Retornar draft para review
