---
id: curador-imagens
type: step
execution: inline
agent: curador-imagens
label: "Buscar imagens para o carrossel"
inputFile: "squads/noticias-carrossel-ia/output/carousel-content.md"
outputFile: "squads/noticias-carrossel-ia/output/image-brief.md"
---

# Curador de Imagens — Busca de Imagens para os Slides

## Contexto

Voce recebeu o conteudo completo do carrossel escrito pelo Redator e a preferencia do usuario sobre tipo de imagens (fotos reais, IA ou misto).

## Processo

1. Ler o conteudo do Redator (carousel-content.md)
2. Ler a preferencia do usuario no checkpoint anterior
3. Identificar quais slides precisam de imagem contextual
4. Executar a busca conforme o modo selecionado:
   - **Fotos reais**: Buscar via web_search e web_fetch em sites oficiais, press rooms, e fontes editoriais
   - **Imagens IA**: Criar prompts detalhados no estilo editorial/fotografico
   - **Misto**: Tentar fotos reais primeiro, gerar prompt IA como fallback
5. Compilar o brief de imagens com todas as opcoes
6. Salvar em image-brief.md

## Input

- Conteudo do carrossel (do Redator)
- Preferencia de imagens (do checkpoint)
- Tema e fontes da pesquisa (do Pesquisador)

## Output

- Brief de imagens organizado por slide
- URLs das imagens encontradas (modo fotos reais)
- Prompts de geracao (modo IA)
- Descricao e credito de cada imagem

## Veto Conditions

- Nenhuma imagem/prompt entregue para slides que precisam de foto
- URLs quebradas ou inacessiveis
- Imagens com marca d'agua visivel
- Imagens stock genericas (handshake, escritorio generico)
