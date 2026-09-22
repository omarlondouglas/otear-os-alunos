---
name: otear-verificacao-factual
description: Classifica alegações por evidência, identifica divergências e produz um relatório de checagem rastreável.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, jornalismo, verificacao, fatos]
    related_skills: [otear-apuracao-fontes, otear-redacao-jornalistica]
tools: [read_file, write_file, search_files]
---

# Otear Verificação Factual

Use para revisar um dossiê ou rascunho antes de ele circular como conteúdo factual. A skill
não dá certeza artificial: ausência de evidência deve continuar visível no resultado.

## Processo

1. Liste cada alegação verificável, incluindo números, datas, nomes, cargos e citações.
2. Compare a alegação com fontes primárias ou independentes que estejam acessíveis na sessão.
3. Marque cada item como `confirmado`, `disputado`, `não verificado` ou `fora de escopo`, e
   explique o critério e as fontes usadas.
4. Registre contradições, buscas que não resolveram a dúvida e o que não deve ser publicado
   sem confirmação adicional.
5. Salve o relatório em `produto-otear-os/entregas/noticias/`.

## Saída exigida

Entregue `Fatos confirmados`, `Fatos disputados`, `Fatos não verificados`, `Lacunas`,
`Alerta ao redator` e `Fontes consultadas`. Mantenha URL e data de consulta para cada fonte.

## Limites

Não invente busca, fonte ou veredito. Assuntos médicos, jurídicos, financeiros, eleitorais ou
de segurança exigem cuidado extra, fontes primárias quando possível e revisão humana antes de
publicação.
