---
id: gerador-imagens
type: step
execution: inline
agent: gerador-imagens
label: "Gerar imagens com IA via Gemini API"
inputFile: "squads/slides-aula/output/visual-concept.md"
outputFile: "squads/slides-aula/output/images/"
---

# Gerador de Imagens — Gerar via Gemini API

## Contexto

Você recebeu o visual-concept.md com prompts de geração (ou mensagem de que não precisa).

## Processo

1. Ler o visual-concept.md
2. Se contiver "nenhuma geração de IA necessária": pular
3. Se tiver prompts: gerar cada imagem via Gemini API
4. Salvar em output/{run_id}/images/

## Veto Conditions

- Nenhuma imagem gerada quando havia prompts
- Arquivo de imagem com 0 bytes
