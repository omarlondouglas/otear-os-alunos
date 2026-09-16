# Task: enrich-metadata

```yaml
id: enrich-metadata
version: "1.0.0"
title: "Enrich Markdown with Metadata"
description: >
  Adiciona frontmatter YAML a cada markdown convertido: copywriter,
  formato original, framework, nível de consciência Schwartz, técnicas.
elicit: false
owner: copy-chief
executor: copy-chief
outputs:
  - Markdown com frontmatter YAML completo
  - Arquivo organizado na estrutura de pastas
```

## When This Task Runs

- Após extract-content converter com sucesso
- Para cada arquivo markdown novo

## Enrichment Steps

### Step 1: Analyze Content

Ler o markdown e identificar:
- **Copywriter**: Quem escreveu/ensinou (Halbert, Schwartz, Ogilvy, Kennedy, outro)
- **Formato original**: O que era (sales letter, email, ad, transcript, livro, curso)
- **Framework**: Qual técnica/framework principal é demonstrado
- **Técnicas**: Lista de técnicas específicas usadas no texto
- **Nível de consciência**: Para qual nível Schwartz a peça foi escrita

### Step 2: Generate Frontmatter

```yaml
---
copywriter: "halbert|schwartz|ogilvy|kennedy|{outro}"
source_format: "pdf|video|image"
original_type: "sales-letter|email|ad|transcript|book|course|direct-mail"
framework: "{framework principal identificado}"
techniques:
  - "{técnica 1}"
  - "{técnica 2}"
consciousness_level: "unaware|problem-aware|solution-aware|product-aware|most-aware"
tags:
  - "{tag 1}"
  - "{tag 2}"
quality_score: "{1-10 pós validação}"
extracted_date: "{YYYY-MM-DD}"
source_file: "{nome do arquivo original}"
---
```

### Step 3: Organize in Structure

Mover arquivo enriquecido para a estrutura:

```
knowledge-base/
├── por-copywriter/{copywriter}/{filename}.md
├── por-formato/{original_type}/{filename}.md  (symlink ou cópia)
└── por-framework/{framework}/{filename}.md    (symlink ou cópia)
```

Organização primária: por-copywriter (arquivo real)
Organização secundária: por-formato e por-framework (referências)

### Step 4: Update Index

Adicionar entrada ao index.md da knowledge-base com:
- Nome do arquivo
- Copywriter
- Framework
- Tipo original
- Data de extração
