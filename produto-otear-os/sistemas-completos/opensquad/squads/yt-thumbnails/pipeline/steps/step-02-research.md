---
execution: subagent
agent: squads/yt-thumbnails/agents/researcher
inputFile: squads/yt-thumbnails/pipeline/data/research-focus.md
outputFile: squads/yt-thumbnails/output/research-report.md
model_tier: powerful
---

# Step 02: Pesquisa de Contexto e Referências

## Context Loading

Load these files before executing:
- `squads/yt-thumbnails/pipeline/data/research-focus.md` — tema e estilo escolhido pelo usuário
- `squads/yt-thumbnails/pipeline/data/research-brief.md` — conhecimento base sobre thumbnails
- `squads/yt-thumbnails/pipeline/data/domain-framework.md` — metodologia operacional

## Instructions

### Process
1. Ler o tema do vídeo e estilo desejado do research-focus.md
2. Pesquisar via web_search: "{tema} YouTube" para entender o contexto do tópico
3. Pesquisar via web_search: "YouTube thumbnail {tema}" para ver thumbnails existentes no nicho
4. Pesquisar via web_search: "best YouTube thumbnails {nicho/categoria}" para referências de sucesso
5. Analisar os resultados: quais cores, composições e elementos visuais os top performers usam neste nicho?
6. Identificar gaps visuais: o que ninguém está fazendo que poderia diferenciar?
7. Compilar um relatório com contexto do tópico + análise de thumbnails do nicho + recomendações

## Output Format

```markdown
# Relatório de Pesquisa: {tema do vídeo}

## Contexto do Tópico
- Resumo do tema em 3-5 frases
- Público interessado neste tema
- Emoções associadas ao tópico (medo, curiosidade, oportunidade, etc.)

## Análise de Thumbnails do Nicho
### Padrões Encontrados
- Cores dominantes: {lista}
- Composição mais comum: {descrição}
- Uso de texto: {padrão}
- Expressões faciais: {padrão}

### Top 3 Thumbnails de Referência
1. {título do vídeo} — {por que a thumbnail funciona}
2. {título do vídeo} — {por que funciona}
3. {título do vídeo} — {por que funciona}

### Gaps e Oportunidades
- {oportunidade 1}
- {oportunidade 2}

## Recomendações para Esta Thumbnail
1. {recomendação com justificativa}
2. {recomendação com justificativa}
3. {recomendação com justificativa}
```

## Output Example

```markdown
# Relatório de Pesquisa: Como IA vai substituir programadores

## Contexto do Tópico
- Tema quente e polêmico no mundo tech. Gera forte engajamento por tocar em medo de perder emprego.
- Público: desenvolvedores, estudantes de programação, profissionais de tech.
- Emoções dominantes: medo (perda de emprego), curiosidade (como se adaptar), oportunidade (quem usa IA ganha).

## Análise de Thumbnails do Nicho
### Padrões Encontrados
- Cores dominantes: azul (tech), vermelho (urgência), preto (drama)
- Composição: rosto de perfil olhando para tela com código, ou split antes/depois
- Uso de texto: "ACABOU", "O FIM", números grandes ("2026")
- Expressões: choque, preocupação, determinação

### Top 3 Thumbnails de Referência
1. "AI Will Replace 90% of Developers" (Fireship) — rosto preocupado + robô, vermelho/preto
2. "I Replaced My Dev Team with AI" — antes/depois split, verde=humano vs azul=IA
3. "The TRUTH About AI Coding" — close-up rosto + código refletido nos óculos

### Gaps e Oportunidades
- Poucos usam estilo futurista/cyberpunk — poderia diferenciar
- Ninguém mostra a perspectiva positiva (oportunidade) visualmente

## Recomendações para Esta Thumbnail
1. Usar expressão de CHOQUE (não medo) — gera mais curiosidade
2. Cores: azul neon + preto para estilo tech futurista
3. Elemento visual: código sendo "apagado" ou "transformado" por luz de IA
```

## Veto Conditions

Reject and redo if ANY are true:
1. Relatório não contém análise de thumbnails existentes no nicho (só fala do tema)
2. Recomendações são genéricas sem conexão com os padrões encontrados

## Quality Criteria

- [ ] Contexto do tópico é específico e bem pesquisado
- [ ] Pelo menos 3 thumbnails de referência analisadas
- [ ] Gaps e oportunidades identificados são acionáveis
- [ ] Recomendações são específicas para ESTE tema, não genéricas
