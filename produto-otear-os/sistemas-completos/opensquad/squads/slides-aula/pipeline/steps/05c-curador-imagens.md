---
id: curador-imagens
type: step
execution: inline
agent: curador-imagens
label: "Buscar imagens na web para os slides"
inputFile: "squads/slides-aula/output/slides-content.md"
outputFile: "squads/slides-aula/output/image-brief.md"
---

# Curador de Imagens — Busca na Web

## Contexto

Você recebeu o conteúdo dos slides e a preferência do usuário sobre imagens.

## Processo

1. Ler o conteúdo dos slides (slides-content.md)
2. Ler a preferência do usuário no checkpoint anterior
3. Identificar quais slides precisam de imagem
4. Para cada slide:
   - **Logos**: buscar via web_search em sites oficiais, GitHub, Wikipedia
   - **Screenshots**: buscar em documentação oficial
   - **Fotos**: buscar em fontes públicas e oficiais
5. Validar cada URL (acessível, sem marca d'água)
6. Para imagens não encontradas, marcar como `GERAR_IA` (fallback)
7. Salvar em image-brief.md

## Veto Conditions

- URLs inventadas ou inacessíveis
- Imagens com marca d'água
- Nenhuma imagem entregue quando solicitadas
