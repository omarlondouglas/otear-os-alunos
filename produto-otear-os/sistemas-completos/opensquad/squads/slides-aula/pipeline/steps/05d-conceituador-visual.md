---
id: conceituador-visual
type: step
execution: inline
agent: conceituador-visual
label: "Criar conceito visual para imagens que precisam de IA"
inputFile: "squads/slides-aula/output/slides-content.md"
outputFile: "squads/slides-aula/output/visual-concept.md"
---

# Conceituador Visual — Conceito para Imagens IA

## Contexto

Você recebeu o conteúdo dos slides e o brief de imagens do Curador.

## Processo

1. Ler o image-brief.md
2. Se NÃO houver "GERAR_IA" ou "FALLBACK": pular e reportar que não precisa
3. Se houver slides que precisam de IA:
   a. Criar conceito visual didático para cada
   b. Gerar prompts otimizados para Gemini
   c. Especificar: 1920x1080, alto contraste, estilo profissional

## Veto Conditions

- Conceitos genéricos sem função didática
- Prompts sem especificações técnicas
