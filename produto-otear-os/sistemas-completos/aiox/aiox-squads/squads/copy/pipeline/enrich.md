# Pipeline: Enrich Metadata

## Processo de Enriquecimento

Para cada arquivo markdown convertido, adicionar frontmatter YAML com metadados estruturados.

### Step 1: Identificar Copywriter

Análise do conteúdo para determinar autoria:

| Sinal | Copywriter |
|-------|-----------|
| Menção direta ao nome | Atribuição direta |
| Fonte/curso conhecido | Inferência por contexto |
| Estilo de escrita | Inferência por padrão |
| Pasta/coleção de origem | Metadado externo |

### Step 2: Identificar Framework

Mapear o conteúdo para frameworks conhecidos:

| Framework | Sinais |
|-----------|--------|
| Bullet Fascinations (Halbert) | Listas de "Como...", "O segredo de...", "Por que..." |
| 5 Níveis de Consciência (Schwartz) | Progressão de awareness, menção a níveis |
| Headline Principles (Ogilvy) | Headlines longas, dados específicos, prova |
| Deadline Copy (Kennedy) | Urgência, escassez, deadline explícito |
| AIDA | Atenção → Interesse → Desejo → Ação |
| PAS | Problem → Agitate → Solve |
| 4Ps | Promise → Picture → Proof → Push |

### Step 3: Identificar Técnicas

Técnicas específicas no texto:

- Storytelling (narrativa pessoal/case)
- Social proof (testimonials, números)
- Scarcity (escassez real ou percebida)
- Authority (credenciais, expertise)
- Reciprocity (valor grátis antes de pedir)
- Loss aversion (o que perde se não agir)
- Anchoring (ancoragem de preço)
- Future pacing (projeção de resultado)

### Step 4: Determinar Nível de Consciência

Para qual nível Schwartz a peça foi escrita:

| Nível | Sinais no Texto |
|-------|----------------|
| Unaware | Sem menção a problema, conteúdo educativo/story |
| Problem Aware | Nomeia problema, amplifica dor |
| Solution Aware | Apresenta categoria de solução, compara |
| Product Aware | Fala do produto, features, benefícios |
| Most Aware | Oferta direta, preço, urgência, CTA |

### Step 5: Gerar Frontmatter

```yaml
---
copywriter: "{nome}"
source_format: "{pdf|video|image}"
original_type: "{sales-letter|email|ad|transcript|book|course|direct-mail}"
framework: "{framework principal}"
techniques:
  - "{técnica 1}"
  - "{técnica 2}"
  - "{técnica 3}"
consciousness_level: "{unaware|problem-aware|solution-aware|product-aware|most-aware}"
tags:
  - "{tag 1}"
  - "{tag 2}"
  - "{tag 3}"
quality_score: null  # preenchido na validação
extracted_date: "{YYYY-MM-DD}"
source_file: "{nome original}"
---
```

### Step 6: Organizar

- Arquivo real em: `knowledge-base/por-copywriter/{copywriter}/{filename}.md`
- Referência em: `knowledge-base/por-formato/{type}/`
- Referência em: `knowledge-base/por-framework/{framework}/`
