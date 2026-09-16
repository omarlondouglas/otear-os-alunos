---
id: revisor
type: step
execution: inline
agent: revisor
label: "Revisão de qualidade"
inputFile: "squads/noticias-carrossel-ia/output/carousel-content.md"
outputFile: "squads/noticias-carrossel-ia/output/review-report.md"
---

# Revisor — Controle de Qualidade

## Contexto

Você recebeu o conteúdo do Redator e os slides HTML do Designer.
Sua missão: revisar ambos com rigor antes de apresentar ao Marlon.

## Processo

1. Ler o conteúdo do Redator (carousel-content.md)
2. Aplicar o checklist de revisão de conteúdo:
   - Formato do carrossel explícito e estrutura correta
   - Slide 1 com gancho bold (máx. 20 palavras)
   - Hierarquia dois níveis em cada slide
   - 40-80 palavras por slide
   - Alternância de fundos entre slides
   - Legenda: primeiros 125 chars como gancho standalone
   - Legenda termina com pergunta aberta ou CTA
   - Hashtags: 5-15, mix nicho/mid/broad
   - CTA acionável no último slide
3. Listar os arquivos HTML de slides (squads/noticias-carrossel-ia/output/{run_id}/slides/)
4. Verificar design de cada slide:
   - Design system documentado
   - HTML auto-contido
   - Viewport 1080x1440
   - Fontes dentro dos mínimos
   - Branding @marlonlima.ia presente
   - Sem contadores de slide
5. Produzir relatório com: aprovação ou lista de correções específicas
6. Salvar relatório no outputFile

## Veto Conditions

- Slides com menos de 40 palavras não reportados como problema
- CTA ausente não reportado
- Aprovação de conteúdo com erros ortográficos em português
- Aprovação de HTML com fontes abaixo do mínimo de plataforma
