---
agent: scraper
execution: inline
inputFile: checkpoint-perfil
outputFile: squads/instagram-scraper/output/report.md
---

# Scraper — Coletar Imagens de Carrossel

## Instrucoes

1. Ler o perfil e quantidade de posts definidos no checkpoint
2. Usar o Playwright MCP (browser com sessao persistente) para:
   - Navegar ate o perfil no Instagram
   - Identificar posts de carrossel no grid
   - Abrir cada post e navegar pelos slides
   - Fazer screenshot ou download de cada imagem
3. Salvar todas as imagens organizadas por post
4. Gerar relatorio final

## Input

O usuario informou:
- Perfil alvo: {perfil do checkpoint}
- Quantidade de posts: {quantidade do checkpoint}

## Output

- Imagens salvas em `squads/instagram-scraper/output/{run_id}/{username}/post-{N}/`
- Relatorio em `squads/instagram-scraper/output/{run_id}/report.md`

## Veto Conditions

- Nenhuma imagem foi baixada
- Erro de autenticacao nao reportado ao usuario
- Mais de 10 posts acessados numa unica execucao
