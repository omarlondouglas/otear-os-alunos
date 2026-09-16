---
id: pesquisador
type: step
execution: subagent
agent: pesquisador
model_tier: fast
label: "Pesquisar notícias relevantes"
inputFile: "squads/noticias-carrossel-ia/output/research-focus.md"
outputFile: "squads/noticias-carrossel-ia/output/research-brief.md"
---

# Pesquisador — Busca de Notícias via Banco de Dados

## Contexto

Você recebeu o foco do dia definido no checkpoint anterior.
As notícias já foram coletadas e estão no banco de dados (Supabase).
Seu trabalho é buscar via API, selecionar as melhores e formatar o brief.

## Processo

1. Ler o arquivo de foco do dia (inputFile) para extrair TEMA e PERÍODO
2. Converter o período para horas:
   - "Últimas 24 horas" → 24
   - "Últimos 3 dias" → 72
   - "Última semana" → 168
3. Chamar a API de notícias:
   ```
   GET http://localhost:3000/api/news?tema={TEMA}&horas={HORAS}&limite=10
   ```
4. Se a API retornar notícias (total > 0):
   - Selecionar a MELHOR notícia com base em: relevância para agências digitais, frescor, potencial de engajamento
   - Listar 2-3 alternativas
   - Formatar em research-brief.md
5. Se a API retornar 0 resultados:
   - Tentar com tema mais genérico (ex: "IA" em vez de "agentes de IA para vendas")
   - Se ainda 0: fazer UMA busca web com web_search como fallback
6. Salvar o brief no outputFile

## Output Format

```markdown
# Research Brief

## Notícia Principal
- **Título:** {titulo}
- **Fonte:** {fonte}
- **URL:** {url}
- **Resumo:** {resumo}
- **Por que essa:** {justificativa de escolha}

## Alternativas
1. {titulo} — {fonte} — {resumo curto}
2. {titulo} — {fonte} — {resumo curto}

## Ângulo Editorial
{sugestão de ângulo para o carrossel, focado em agências digitais}
```

## Veto Conditions

- Nenhuma notícia encontrada (nem via API nem via fallback)
- Notícia sem URL verificável
- Notícia com mais de 7 dias sem justificativa
