---
id: image-patcher
type: step
execution: inline
agent: image-patcher
label: "Injetar imagens no slides-data.json"
inputFile: "squads/slides-aula/output/slides-data.json"
imageFile: "squads/slides-aula/output/image-brief.md"
outputFile: "squads/slides-aula/output/slides-data.json"
---

# Image Patcher — Injetar imagens nos slides

## Contexto

O Designer criou o `slides-data.json` com texto completo (todos com `imageFile: null`).
O Curador e o Gerador produziram as imagens disponíveis.

## Missão

Atualizar apenas `imageFile` e `theme` dos slides que têm imagem.

## Processo

1. Se o usuário escolheu "manter só texto": pular
2. Ler `slides-data.json` e `image-brief.md`
3. Para cada slide com imagem: atualizar `imageFile` e mudar `theme` para `"black"`
4. Salvar o JSON atualizado
