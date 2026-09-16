# Task: generate-copy

```yaml
id: generate-copy
version: "1.0.0"
title: "Generate Copy Draft"
description: >
  Especialista gera draft de copy baseado em briefing enriquecido.
  Consulta knowledge-base via grep/glob, aplica framework do copywriter
  selecionado, retorna draft para review.
elicit: false
owner: copy-chief
executor: "{specialist from routing}"
outputs:
  - Draft de copy no formato do canal
  - Metadados: copywriter usado, frameworks aplicados, sources consultadas
```

## When This Task Runs

- Após route-briefing selecionar especialista e estilo
- Especialista recebe briefing enriquecido

## Generation Steps

### Step 1: Consult Knowledge Base (frameworks)

OBRIGATÓRIO antes de gerar:

1. **grep por copywriter**: Buscar na knowledge-base por arquivos do copywriter selecionado
   ```
   grep -r "{copywriter}" knowledge-base/por-copywriter/
   ```

2. **grep por formato**: Buscar exemplos do formato solicitado
   ```
   grep -r "{formato}" knowledge-base/por-formato/
   ```

3. **grep por framework**: Se framework específico mencionado
   ```
   grep -r "{framework}" knowledge-base/por-framework/
   ```

4. **Ler index.md**: Para visão geral do que está disponível
   ```
   Read knowledge-base/index.md
   ```

### Step 1b: Consult Swipes DB (exemplos reais)

OBRIGATÓRIO — retrieval semântico de copy real dos mestres (~20.5k chunks).

Ver `knowledge-base/_swipes-db.md` para doc completa. Padrão:

1. **Formular query** do briefing: nicho + formato + angle
   - Ex: "lead saúde masculina urgência"
   - Ex: "headline curiosidade financeiro"
   - Ex: "close com garantia risco zero"

2. **Buscar** (min 3, max 10 resultados):
   ```bash
   python squads/copy/tools/swipes_search.py "{query}" --count 5
   ```

3. **Filtrar por autor** se briefing mencionar:
   ```bash
   python squads/copy/tools/swipes_search.py "{query}" --author {autor} --count 5
   ```

4. **Filtrar por idioma** se mercado BR:
   ```bash
   python squads/copy/tools/swipes_search.py "{query}" --language pt --count 5
   ```

5. Usar os chunks como **ancoragem concreta** (não copiar literalmente). Extrair:
   - Estrutura e ritmo
   - Gatilhos emocionais usados
   - Escolhas lexicais do autor
   - Padrões de prova, garantia, urgência

### Step 2: Apply Framework

Usar os padrões encontrados na base como fundação:
- Estrutura da peça seguindo o framework do mestre
- Tom e vocabulário do copywriter selecionado
- Técnicas identificadas nos exemplos da base
- Adaptar para o produto, público e canal do briefing

### Step 3: Generate Draft

Gerar copy seguindo a estrutura do especialista para o formato:
- Ads: Hook → Diagnóstico → Benefício → CTA
- Email: Subject → Preview → Opening → Body → CTA → PS
- Landing: 12 seções (headline → CTA)
- Social: formato nativo da plataforma

### Step 4: Tag Draft

Incluir metadados no draft:

```yaml
_draft_meta:
  specialist: "{specialist_id}"
  copywriter: "{copywriter usado}"
  frameworks: ["{frameworks aplicados}"]
  kb_sources: ["{arquivos consultados na base}"]
  cycle: 1
```

### Step 5: Submit for Review

Enviar draft + metadados ao @copy-reviewer para avaliação.
