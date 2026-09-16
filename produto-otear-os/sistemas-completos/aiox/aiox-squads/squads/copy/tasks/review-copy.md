# Task: review-copy

```yaml
id: review-copy
version: "1.0.0"
title: "Review Copy Draft"
description: >
  Copy Reviewer avalia draft contra 4 critérios obrigatórios.
  Retorna APROVADO (com scores) ou REJEITADO (com feedback acionável).
  Máximo 2 ciclos de reescrita antes de escalar.
elicit: false
owner: copy-reviewer
executor: copy-reviewer
outputs:
  - Verdict: APROVADO ou REJEITADO
  - Scores por critério (1-10)
  - Feedback específico (se rejeitado)
```

## When This Task Runs

- Após especialista gerar draft (generate-copy)
- Após especialista reescrever draft rejeitado (ciclo 2)

## Review Process

### Step 1: Read Draft + Briefing

- Ler o draft completo
- Ler o briefing original para comparação
- Verificar metadados (_draft_meta) para contexto

### Step 2: Score 4 Criteria

| Critério | Mínimo | O que avalia |
|----------|--------|-------------|
| Diagnóstico de Dor | 6/10 | Dor nomeada, específica, reconhecível pelo lead |
| Articulação de Benefício | 6/10 | Benefício (não feature), conectado à dor, específico |
| Framework Identificável | 5/10 | Técnica do mestre visível e corretamente aplicada |
| Ausência de Tom IA | 7/10 | Sem clichês de IA, com personalidade e ritmo |

### Step 3: Decide Verdict

- **APROVADO**: Todos os 4 scores >= mínimo
- **REJEITADO**: Qualquer score < mínimo

### Step 4: Generate Output

SE APROVADO:
```
REVIEW RESULT: APROVADO ✓

Scores: Dor [X]/10 | Benefício [X]/10 | Framework [X]/10 | Tom [X]/10
Overall: [média]/10

Destaques: [pontos fortes]
Nota: [sugestão opcional]
```

SE REJEITADO:
```
REVIEW RESULT: REJEITADO ✗
Ciclo: [1 ou 2] de 2

[Para cada critério abaixo do mínimo:]
Critério N ([nome]): [score]/10
→ Problema: [o que está errado]
→ Correção: [exatamente o que fazer]
→ Exemplo: [trecho problemático] → [sugestão corrigida]

AÇÃO REQUERIDA:
→ [Lista numerada do que reescrever]
```

### Step 5: Route Result

- APROVADO → devolver ao Copy Chief para entrega
- REJEITADO (ciclo 1) → devolver ao especialista com feedback
- REJEITADO (ciclo 2) → escalar ao Copy Chief com relatório completo
