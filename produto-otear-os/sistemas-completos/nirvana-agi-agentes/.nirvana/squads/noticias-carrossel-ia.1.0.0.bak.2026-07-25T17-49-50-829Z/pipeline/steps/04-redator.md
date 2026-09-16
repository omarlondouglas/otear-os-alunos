---
id: redator
type: step
execution: inline
agent: redator
format: instagram-feed
label: "Escrever conteúdo do carrossel"
inputFile: "squads/noticias-carrossel-ia/output/strategy-brief.md"
outputFile: "squads/noticias-carrossel-ia/output/carousel-content.md"
---

# Redator — Criação do Conteúdo do Carrossel

## Contexto

Você recebeu o brief estratégico com: notícia escolhida, ângulo editorial, formato do carrossel,
gancho da capa, estrutura de slides e estratégia de hashtags.

Sua missão: escrever o conteúdo completo do carrossel em português (Brasil).

## Processo

1. Ler o brief estratégico do Estrategista
2. Escrever o conteúdo de cada slide seguindo o formato do carrossel escolhido
3. Garantir hierarquia em dois níveis por slide: headline bold + texto de apoio
4. Contar palavras de cada slide (mínimo 40, máximo 80)
5. Alternar fundos: escuro → claro → acento → escuro...
6. Definir palavras-destaque em acento para cada slide
7. Escrever a legenda completa:
   - Hook nos primeiros 125 caracteres
   - Corpo com quebras de linha
   - Pergunta final provocativa
8. Definir as hashtags (5-15, mix nicho/mid/broad)
9. Salvar o conteúdo completo no outputFile

## Veto Conditions

- Qualquer slide com menos de 40 palavras (headline + texto de apoio)
- Qualquer slide com mais de 80 palavras
- Legenda sem gancho nos primeiros 125 caracteres
- Ausência de CTA no último slide
- Mais de 15 hashtags
- Texto em inglês (exceto nomes de ferramentas/marcas)
