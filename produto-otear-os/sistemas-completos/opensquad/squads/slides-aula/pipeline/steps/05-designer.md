---
id: designer
type: step
execution: inline
agent: designer
format: slide-design
label: "Criar slides em JSON (1a passagem, sem imagens)"
inputFile: "squads/slides-aula/output/slides-content.md"
outputFile: "squads/slides-aula/output/slides-data.json"
---

# Designer — 1ª Passagem: Slides em Texto

## Contexto

Esta é a **primeira passagem** do Designer. O objetivo é criar os slides com foco total no conteúdo textual e hierarquia visual. As imagens serão adicionadas em uma etapa separada.

## Processo

1. Ler o conteúdo completo do Redator (slides-content.md)
2. Criar o `slides-data.json` com **todos os `imageFile: null`**
3. Usar temas `dark`, `light` ou `accent` para variação visual (não usar `black`)
4. Focar na tipografia, hierarquia e impacto do texto
5. Incluir `meta` com título, autor e data

## Regras desta passagem

- **NUNCA** colocar imageFile com valor — sempre `null`
- **NUNCA** usar o tema `black` (reservado para slides com imagem)
- Criar slides impactantes só com texto, stat e hierarquia tipográfica
