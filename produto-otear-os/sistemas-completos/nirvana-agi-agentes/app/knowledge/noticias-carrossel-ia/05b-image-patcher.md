---
id: image-patcher
type: step
execution: inline
agent: image-patcher
label: "Injetar imagens no slides-data.json"
inputFile: "squads/noticias-carrossel-ia/output/slides-data.json"
imageFile: "squads/noticias-carrossel-ia/output/image-brief.md"
outputFile: "squads/noticias-carrossel-ia/output/slides-data.json"
---

# Image Patcher — Injetar imagens nos slides

## Contexto

O Designer já criou o `slides-data.json` com o texto completo de todos os slides (todos com `imageFile: null`).

O Curador de Imagens (e opcionalmente o Gerador de Imagens) já rodou e produziu o `image-brief.md` com as imagens disponíveis para cada slide.

## Sua missão

Abrir o `slides-data.json`, ler o `image-brief.md` e atualizar apenas os campos `imageFile` e `theme` dos slides que têm imagem disponível.

## Processo

1. Verificar se o usuário escolheu "Não — manter só texto" no checkpoint. Se sim, pular tudo e reportar "sem alterações".

2. Ler `slides-data.json` e `image-brief.md`

3. Para cada linha do brief no formato:
   - `Slide N: [url ou filename] — descrição` → atualizar slide de id N
   - `Slide N: null` → manter como está

4. Salvar o JSON atualizado

## Importante

- `imageFile` com URL completa (`https://...`) = imagem do banco R2
- `imageFile` com nome de arquivo (`img-slide-01.png`) = imagem IA gerada localmente
- Ao adicionar qualquer imagem: mudar `theme` para `"black"`
- Nunca modificar `elements`
