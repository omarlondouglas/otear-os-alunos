# Task: validate-extraction

```yaml
id: validate-extraction
version: "1.0.0"
title: "Validate Extracted Content Quality"
description: >
  Valida qualidade do markdown pós-extração e pós-enriquecimento.
  Rejeita arquivos com qualidade insuficiente e reporta ao usuário.
  Falha segura: rejeitar em vez de aceitar duvidoso.
elicit: false
owner: copy-chief
executor: copy-chief
outputs:
  - Lista de arquivos aprovados (entram na base)
  - Lista de arquivos rejeitados (com motivo)
  - Relatório de validação
```

## Validation Criteria

### Content Quality

| Critério | Mínimo | Check |
|----------|--------|-------|
| Legibilidade | 70% | Texto legível sem artefatos de OCR |
| Completude | 80% | Conteúdo não cortado, seções inteiras |
| Estrutura | OK | Headings, parágrafos, listas preservados |
| Encoding | UTF-8 | Sem caracteres corrompidos |

### Metadata Quality

| Critério | Check |
|----------|-------|
| Copywriter | Identificado e válido |
| Framework | Pelo menos 1 identificado |
| Técnicas | Pelo menos 2 identificadas |
| Consciência | Nível Schwartz coerente com conteúdo |
| Tags | Pelo menos 3 tags relevantes |

### Decision

- **APROVADO**: Todos os critérios OK → arquivo entra na base
- **REJEITADO**: Qualquer critério falha → arquivo movido para `_rejected/` com log
- **MANUAL REVIEW**: Critérios borderline → movido para `_review/` com anotação

### Output Format

```
VALIDATION REPORT
Date: {YYYY-MM-DD}
Total: {N} files

APPROVED ({N}):
- {filename} — {copywriter} / {framework}

REJECTED ({N}):
- {filename} — Reason: {motivo específico}

MANUAL REVIEW ({N}):
- {filename} — Issue: {o que precisa de olho humano}
```
