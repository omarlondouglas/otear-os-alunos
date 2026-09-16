---
id: pesquisador
type: step
execution: subagent
agent: pesquisador
model_tier: fast
label: "Pesquisar conteúdo sobre o tema"
inputFile: "squads/slides-aula/output/research-focus.md"
outputFile: "squads/slides-aula/output/research-brief.md"
---

# Pesquisador — Busca de Conteúdo Educacional

## Contexto

Você recebeu o tema da aula definido pelo usuário no checkpoint anterior.
Seu objetivo é pesquisar na web os conceitos, dados, exemplos e referências
mais relevantes para construir uma apresentação educacional completa.

## Processo

1. Ler o arquivo de foco da aula (inputFile)
2. Executar buscas usando WebSearch com queries variadas:
   - Português: "[tema] tutorial", "[tema] conceitos", "[tema] exemplos"
   - Inglês: "[topic] guide", "[topic] explained", "[topic] best practices"
   - Técnicas: "[tema] documentação", "[tema] cheat sheet"
3. Usar WebFetch nos 5-10 artigos mais relevantes para extrair detalhes
4. Compilar o brief com conceitos-chave, dados, exemplos e fontes
5. Listar logos e ferramentas mencionadas (para o curador de imagens buscar depois)
6. Salvar o brief no outputFile

## Veto Conditions

- Menos de 5 conceitos-chave encontrados
- Nenhuma fonte verificável
- Conteúdo desatualizado (mais de 2 anos sem justificativa)
