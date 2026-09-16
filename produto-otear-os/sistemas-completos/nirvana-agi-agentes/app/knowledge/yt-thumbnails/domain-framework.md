# Domain Framework — YouTube Thumbnail Prompt Generation

## Metodologia Operacional

### Etapa 1: Análise do Contexto do Vídeo
- Entender o tópico, público-alvo e emoção central do vídeo
- Identificar o "gancho visual" — qual é a promessa implícita da thumbnail?
- Definir o estilo: educacional, entretenimento, vlog, tutorial, polêmico

### Etapa 2: Pesquisa de Referências
- Analisar thumbnails de sucesso no mesmo nicho (top 5 vídeos por views)
- Identificar padrões visuais: cores dominantes, composição, uso de texto
- Notar o que os concorrentes NÃO fazem (oportunidade de diferenciação)

### Etapa 3: Geração de Conceitos
Criar 3-5 conceitos distintos usando estas fórmulas comprovadas:

**Fórmula 1 — Reação Emocional**
Rosto com expressão exagerada + contexto visual do tópico + texto curto (2-3 palavras)
Exemplo: rosto surpreso + pilha de dinheiro + "IMPOSSÍVEL"

**Fórmula 2 — Antes/Depois**
Split-screen ou comparação visual mostrando transformação
Exemplo: lado esquerdo escuro/velho, lado direito vibrante/novo

**Fórmula 3 — Escala Exagerada**
Objeto do tópico em escala absurda, pessoa pequena ao lado para referência
Exemplo: smartphone gigante, pessoa minúscula olhando para cima

**Fórmula 4 — Curiosity Gap Visual**
Imagem que levanta uma pergunta impossível de ignorar
Exemplo: objeto misterioso censurado/borrado + "O QUE É ISSO?"

**Fórmula 5 — Resultado Impossível**
Cenário visual que parece impossível ou extremo
Exemplo: pessoa rodeada por 1000 iPhones + expressão de choque

### Etapa 4: Detalhamento do Conceito
Para o conceito escolhido, definir:
- **Sujeito principal**: quem/o que ocupa o centro
- **Expressão facial**: qual emoção específica (choque, alegria, medo, curiosidade)
- **Composição**: onde cada elemento fica no frame (regra dos terços)
- **Palette de cores**: 3 cores máximo (60-30-10)
- **Texto overlay**: máximo 3-4 palavras, fonte bold
- **Fundo**: cor sólida, gradiente, ou cenário real
- **Elementos secundários**: objetos, setas, efeitos visuais

### Etapa 5: Engenharia de Prompt
Transformar o conceito em prompt otimizado:
1. Descrever a cena como se já existisse (presente, não imperativo)
2. Incluir especificações técnicas (aspect ratio, resolução, estilo)
3. Usar keywords de qualidade apropriadas ao modelo
4. Separar instruções de texto (adicionar em pós-produção)
5. Gerar versões para Midjourney, DALL-E e Flux

### Etapa 6: Revisão de Qualidade
Validar contra checklist:
- [ ] A thumbnail comunica a mensagem em 1 segundo?
- [ ] Funciona em 168×94px (mobile)?
- [ ] Tem contraste suficiente (teste P&B)?
- [ ] Gera curiosidade sem ser clickbait?
- [ ] É consistente com a identidade visual do canal?
- [ ] O prompt vai gerar uma imagem 16:9?

## Critérios de Decisão

### Quando usar Fórmula de Reação vs Curiosity Gap
- **Reação**: quando o vídeo tem um momento "wow" claro, resultado surpreendente
- **Curiosity Gap**: quando o valor está no processo/jornada, não no resultado
- **Antes/Depois**: quando há transformação visual clara
- **Escala Exagerada**: quando envolve quantidade, tamanho, ou comparação numérica
- **Resultado Impossível**: quando o vídeo mostra algo extremo ou nunca feito

### Quando priorizar qual modelo de IA
- **Precisa de texto legível na thumbnail**: DALL-E 3
- **Precisa de rosto fotorealista**: Midjourney v7 ou Flux 2
- **Estilo cinematográfico/dramático**: Midjourney v7
- **Pele natural, iluminação realista**: Flux 2
- **Iteração rápida (muitas variações)**: Midjourney Draft Mode
