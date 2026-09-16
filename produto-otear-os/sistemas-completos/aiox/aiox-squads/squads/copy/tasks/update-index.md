# Task: update-index

```yaml
id: update-index
version: "1.0.0"
title: "Update Knowledge Base Index"
description: >
  Regenera o index.md da knowledge-base com todos os arquivos
  aprovados, organizados por copywriter, formato e framework.
elicit: false
owner: copy-chief
executor: copy-chief
outputs:
  - index.md atualizado
```

## When This Task Runs

- Após validate-extraction aprovar novos arquivos
- Manualmente via *extract → update-index

## Index Structure

```markdown
# Knowledge Base Index

Last updated: {YYYY-MM-DD}
Total files: {N}

## Por Copywriter

### Gary Halbert ({N} files)
- [{filename}](por-copywriter/halbert/{filename}.md) — {framework} | {tipo}

### Eugene Schwartz ({N} files)
- [{filename}](por-copywriter/schwartz/{filename}.md) — {framework} | {tipo}

### David Ogilvy ({N} files)
- [{filename}](por-copywriter/ogilvy/{filename}.md) — {framework} | {tipo}

### Dan Kennedy ({N} files)
- [{filename}](por-copywriter/kennedy/{filename}.md) — {framework} | {tipo}

## Por Framework
- [{framework}](por-framework/{framework}/) — {N} files

## Por Formato
- [{formato}](por-formato/{formato}/) — {N} files

## Stats
- Total files: {N}
- By copywriter: Halbert {N} | Schwartz {N} | Ogilvy {N} | Kennedy {N} | Other {N}
- By format: PDF {N} | Video {N} | Image {N}
- Last extraction: {date}
```

## Regeneration Logic

1. Glob `knowledge-base/por-copywriter/**/*.md`
2. Ler frontmatter de cada arquivo
3. Agrupar por copywriter, framework, formato
4. Gerar index.md com links relativos
5. Escrever em `knowledge-base/index.md`
