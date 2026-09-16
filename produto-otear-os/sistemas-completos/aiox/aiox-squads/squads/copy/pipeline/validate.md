# Pipeline: Validate Extraction

## Filosofia

Falha segura: rejeitar em vez de aceitar duvidoso. Markdown ruidoso na base
degrada a qualidade de toda copy gerada. Melhor ter 180 arquivos limpos
do que 200 com 20 poluindo os resultados.

## Critérios de Validação

### Content Quality (obrigatório)

| Check | Threshold | Ação se Falhar |
|-------|-----------|---------------|
| Texto legível | > 70% do conteúdo | REJEITAR |
| Conteúdo completo | > 80% preservado | REJEITAR |
| Estrutura preservada | Headings + parágrafos | MANUAL REVIEW |
| Encoding correto | UTF-8 | REJEITAR |
| Sem artefatos de OCR | < 5% caracteres estranhos | REJEITAR |

### Metadata Quality (obrigatório)

| Check | Threshold | Ação se Falhar |
|-------|-----------|---------------|
| Copywriter identificado | Presente e válido | MANUAL REVIEW |
| Framework identificado | >= 1 | MANUAL REVIEW |
| Técnicas listadas | >= 2 | MANUAL REVIEW |
| Nível consciência coerente | Match com conteúdo | MANUAL REVIEW |
| Tags relevantes | >= 3 | MANUAL REVIEW |
| Frontmatter YAML válido | Parseable | REJEITAR |

## Processo de Decisão

```
PARA CADA arquivo:
  1. Verificar content quality
     - QUALQUER check crítico falha → REJEITADO → _rejected/
  
  2. Verificar metadata quality
     - TODOS ok → APROVADO → base
     - ALGUNS falham → MANUAL REVIEW → _review/
     - TODOS falham → REJEITADO → _rejected/
  
  3. Atribuir quality_score (1-10)
     - 9-10: Conteúdo perfeito + metadata rica
     - 7-8: Conteúdo bom + metadata adequada
     - 5-6: Conteúdo ok + metadata mínima
     - < 5: Não deveria ter passado (bug no pipeline)
```

## Destinos

```
knowledge-base/
├── por-copywriter/     # Arquivos APROVADOS (organizados)
├── por-formato/        # Referências de APROVADOS
├── por-framework/      # Referências de APROVADOS
├── _inbox/             # Arquivos novos (entrada)
├── _rejected/          # Arquivos REJEITADOS (com log)
│   └── {filename}.rejected.log
├── _review/            # Arquivos para CURADORIA MANUAL
│   └── {filename}.review.log
└── index.md            # Índice dos APROVADOS
```

## Report Output

```
VALIDATION REPORT — {date}

SUMMARY:
  Processed: {N}
  Approved: {N} ({%})
  Rejected: {N} ({%})
  Manual Review: {N} ({%})
  Avg Quality Score: {X}/10

APPROVED:
  {filename} — {copywriter}/{framework} — score {X}/10

REJECTED:
  {filename} — Reason: {motivo}

MANUAL REVIEW:
  {filename} — Issue: {o que checar}
```
