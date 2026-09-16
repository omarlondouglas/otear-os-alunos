---
id: designer
type: step
execution: inline
agent: designer
format: image-design
label: "Criar slides em texto (1a passagem)"
inputFile: "squads/noticias-carrossel-ia/output/carousel-content.md"
outputFile: "squads/noticias-carrossel-ia/output/slides-data.json"
---

# Designer — 1ª Passagem: Slides em Texto

## Contexto

Esta é a **primeira passagem** do Designer. O objetivo é criar os slides com foco total no conteúdo textual e hierarquia visual. As imagens serão adicionadas em uma etapa separada (caso o usuário queira).

## Processo

1. Ler o conteúdo completo do Redator (carousel-content.md)
2. Criar o `slides-data.json` com **todos os `imageFile: null`** — sem imagens nesta passagem
3. Usar temas `dark`, `light` ou `accent` para criar variação visual (não usar `black`, pois esse tema é para slides com foto de fundo)
4. Focar 100% na tipografia, hierarquia e impacto do texto

## Regras desta passagem

- **NUNCA** colocar imageFile com um valor — sempre `null`
- **NUNCA** usar o tema `black` (é reservado para slides com imagem)
- Criar slides visualmente fortes só com texto: usar `stat` para números, `headline` bold, contraste de temas entre slides
- O usuário vai revisar esses slides antes de decidir se quer imagens

## Output

Salvar o arquivo `slides-data.json` no diretório de output do run atual.
