---
name: otear-pesquisa-noticias
description: Pesquisa pautas atuais com fontes verificáveis e entrega um mapa de relevância sem inventar fatos ou citações.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, jornalismo, pesquisa, noticias]
    related_skills: [otear-noticias, otear-apuracao-fontes]
tools: [read_file, write_file, search_files]
---

# Otear Pesquisa de Notícias

Use para localizar e priorizar pautas recentes. Esta skill pesquisa e organiza informação;
não afirma que uma notícia está confirmada sem fontes verificáveis.

## Processo

1. Defina tema, recorte geográfico, público e o que significa “recente” para o pedido.
2. Consulte fontes atuais e confiáveis disponíveis na sessão. Prefira fontes primárias para
   anúncios, números e decisões oficiais.
3. Para cada pauta candidata, registre título, resumo factual, fonte, URL, data publicada,
   data de consulta e por que é relevante ao público.
4. Diferencie confirmação, cobertura inicial e opinião. Não escolha “a principal notícia”
   como fato objetivo: explique o critério editorial usado.
5. Salve o mapa de pautas em `produto-otear-os/entregas/noticias/`.

## Saída

Entregue uma lista priorizada com palavras-chave para aprofundamento e próximos passos.
Quando nenhuma fonte atual puder ser consultada, pare e explique a limitação; não use memória
do modelo como se fosse notícia recente.

## Verificação

Revise links, datas e atribuições. Se a pauta for publicada, encaminhe-a para
`otear-apuracao-fontes` e `otear-verificacao-factual`.
