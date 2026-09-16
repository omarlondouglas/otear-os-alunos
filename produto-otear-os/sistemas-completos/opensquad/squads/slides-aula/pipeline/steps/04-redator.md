---
id: redator
type: step
execution: inline
agent: redator
label: "Escrever conteúdo de cada slide"
inputFile: "squads/slides-aula/output/strategy-brief.md"
outputFile: "squads/slides-aula/output/slides-content.md"
---

# Redator — Criação do Conteúdo dos Slides

## Contexto

Você recebeu o brief estratégico com a estrutura da apresentação.
Sua missão: escrever o conteúdo completo de cada slide em português (Brasil).

## Processo

1. Ler o brief estratégico do Estrategista
2. Escrever o conteúdo de cada slide seguindo a estrutura definida
3. Garantir headlines curtas (máx 8 palavras)
4. Máximo 3 bullets por lista
5. Definir palavras-destaque para cor accent
6. Indicar tema visual de cada slide (dark/light/accent)
7. Indicar quais slides precisam de imagem e descrever o que
8. Salvar o conteúdo completo no outputFile

## Veto Conditions

- Headlines com mais de 8 palavras
- Listas com mais de 3 items
- Slides sem ponto principal claro
- Ausência de slide de fechamento
- Texto em inglês (exceto nomes de ferramentas)
