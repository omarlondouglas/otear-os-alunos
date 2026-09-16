---
task: discoverProduct()
responsavel: "Strategos"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: userIdea
    tipo: string
    obrigatorio: true
    descricao: "DescriÃ§Ã£o do produto/serviÃ§o fornecida pelo usuÃ¡rio (source: user input)"
  - nome: existingBranding
    tipo: object
    obrigatorio: false
    descricao: "Assets de marca existentes â€” logo, paleta, guidelines (source: user assets)"

Saida:
  - nome: productBrief
    tipo: file
    obrigatorio: true
    descricao: "Briefing completo do produto com USP, mercado-alvo, tom/voz e posicionamento competitivo (destination: lp-researcher + all agents)"
  - nome: valueProposition
    tipo: string
    obrigatorio: true
    descricao: "Proposta de valor principal sintetizada em uma frase (destination: lp-copywriter)"

Checklist:
  pre-conditions:
    - "[ ] UsuÃ¡rio forneceu descriÃ§Ã£o do produto/serviÃ§o"
  post-conditions:
    - "[ ] Product brief contÃ©m USP (Unique Selling Proposition)"
    - "[ ] Product brief contÃ©m mercado-alvo definido"
    - "[ ] Product brief contÃ©m tom e voz da marca"
    - "[ ] Product brief contÃ©m posicionamento competitivo"

Performance:
  duration_expected: "10 minutes"
  cacheable: false
  parallelizable: false
---

# discoverProduct()

## Pipeline Diagram

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  userIdea    â”‚â”€â”€â”€â”€â”€â”€>â”‚                  â”‚â”€â”€â”€â”€â”€â”€>â”‚  productBrief       â”‚
â”‚  (string)    â”‚       â”‚  discoverProduct â”‚       â”‚  (file)             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤       â”‚  @Strategos      â”‚       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  existing    â”‚â”€â”€â”€â”€â”€â”€>â”‚                  â”‚â”€â”€â”€â”€â”€â”€>â”‚  valueProposition   â”‚
â”‚  Branding?   â”‚       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚  (string)           â”‚
â”‚  (object)    â”‚                                  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                          â”‚
                                                         â–¼
                                              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                              â”‚  lp-researcher      â”‚
                                              â”‚  lp-copywriter      â”‚
                                              â”‚  all agents         â”‚
                                              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## DescriÃ§Ã£o

A task `discoverProduct()` Ã© o ponto de partida de toda a pipeline da landing page. O agente **Strategos** analisa a ideia bruta do usuÃ¡rio e quaisquer assets de marca existentes para produzir um **Product Brief** estruturado e uma **Value Proposition** destilada.

O Product Brief serve como documento fundacional que alimenta todos os agentes subsequentes â€” pesquisadores, copywriters, designers e desenvolvedores. Ele estabelece o vocabulÃ¡rio compartilhado, o posicionamento estratÃ©gico e as diretrizes de comunicaÃ§Ã£o que garantem coerÃªncia em toda a landing page.

## Passos

1. **Receber input do usuÃ¡rio** â€” Capturar a descriÃ§Ã£o do produto/serviÃ§o (`userIdea`) e verificar se existem assets de branding (`existingBranding`).
2. **Analisar o mercado implÃ­cito** â€” Identificar o setor, nicho e contexto competitivo a partir da descriÃ§Ã£o fornecida.
3. **Definir USP (Unique Selling Proposition)** â€” Extrair ou formular o diferencial principal do produto/serviÃ§o em relaÃ§Ã£o aos concorrentes.
4. **Mapear mercado-alvo** â€” Definir o perfil inicial do pÃºblico-alvo (demogrÃ¡fico, psicogrÃ¡fico, comportamental).
5. **Estabelecer tom e voz** â€” Determinar o estilo de comunicaÃ§Ã£o adequado ao produto e ao pÃºblico (formal, casual, tÃ©cnico, inspiracional, etc.).
6. **Posicionar competitivamente** â€” Definir como o produto se diferencia no mercado e qual espaÃ§o ocupa na mente do consumidor.
7. **Sintetizar Value Proposition** â€” Condensar o posicionamento em uma frase de proposta de valor clara e memorÃ¡vel.
8. **Gerar Product Brief** â€” Compilar todos os elementos em um documento estruturado e validar contra as post-conditions.

