---
task: writeLongForm()
responsavel: "Writer"
responsavel_type: Agente
atomic_layer: Organism
elicit: false

Entrada:
  - campo: topic
    tipo: string
    origen: "content-strategist ou UsuÃ¡rio â€” tema do conteÃºdo"
    obrigatorio: true
  - campo: format
    tipo: string
    origen: "content-strategist â€” article/blogpost/whitepaper/ebook"
    obrigatorio: false
  - campo: keywords
    tipo: array
    origen: "content-strategist ou UsuÃ¡rio â€” SEO keywords"
    obrigatorio: false
  - campo: contentCalendar
    tipo: file
    origen: "planContentCalendar() â€” calendÃ¡rio editorial"
    obrigatorio: false

Saida:
  - campo: longFormContent
    tipo: file
    destino: "long-form-content.md, social-media-adapter, image-brief-generator"
    persistido: true
  - campo: contentMetadata
    tipo: object
    destino: "publishing-scheduler"
    persistido: true

Checklist:
  pre-conditions:
    - "[ ] Tema definido"
    - "[ ] Formato escolhido (ou padrÃ£o: article)"
  post-conditions:
    - "[ ] ConteÃºdo escrito com heading structure"
    - "[ ] Otimizado para SEO"
    - "[ ] CTAs incluÃ­dos"
  acceptance-criteria:
    - blocker: true
      criteria: "ConteÃºdo com mÃ­nimo 800 palavras para artigos"
    - blocker: true
      criteria: "Heading structure H1-H4 correta"
    - blocker: false
      criteria: "Meta description e keywords incluÃ­dos"

Performance:
  duration_expected: "20-45 minutos"
  cost_estimated: "~0 (criaÃ§Ã£o de conteÃºdo)"
  cacheable: false
  parallelizable: false

Error Handling:
  strategy: retry
  retry:
    max_attempts: 2
    delay: "exponential(base=5s, max=30s)"
  fallback: "Se briefing incompleto, solicitar informaÃ§Ãµes adicionais ao content-strategist"
  notification: "long-form-writer"

Metadata:
  version: "1.0.0"
  dependencies: []
  author: "content-factory-squad"
  created_at: "2026-02-24T00:00:00Z"
---

# Write Long-Form Content

## Flow

```
1. Receber briefing do content-strategist ou usuÃ¡rio
2. Pesquisar tema e referÃªncias relevantes
3. Definir estrutura (outline) com H1-H4
4. Escrever headline magnÃ©tica
5. Desenvolver corpo do artigo com storytelling
6. Incluir CTAs estratÃ©gicos alinhados com a fase do funil
7. Otimizar para SEO (keywords, meta description, heading structure)
8. Revisar e polir o texto
9. Gerar metadata de conteÃºdo (title, description, keywords)
10. Enviar para social-media-adapter e image-brief-generator
```

## Elicitation

- "Qual o tema do conteÃºdo?"
- "Qual o formato desejado? (artigo, blog post, whitepaper, e-book, case study)"
- "HÃ¡ keywords de SEO especÃ­ficas a incluir?"
- "Qual a buyer persona alvo?"
- "HÃ¡ referÃªncias ou fontes obrigatÃ³rias?"

