---
name: otear-criador-imagens
description: Cria especificações e arquivos HTML/CSS para peças visuais e só renderiza imagem quando browser ou Playwright estiver disponível.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, imagens, design, carrossel]
    related_skills: [otear-anuncios, otear-noticias, otear-thumbnails]
tools: [read_file, write_file, search_files]
---

# Otear Criador de Imagens

Use para planejar e criar peças visuais a partir de briefing, copy aprovada e identidade da
marca. Esta skill é independente do runtime do OpenSquad.

## Processo

1. Colete objetivo, plataforma, dimensões, texto aprovado, identidade visual e direitos dos
   assets. Não use marca ou imagem de terceiros sem autorização.
2. Produza um plano visual e um HTML autocontido com CSS, salvo em
   `produto-otear-os/entregas/<sistema>/`. Use pasta coerente com a entrega, como `noticias`,
   `anuncios` ou `thumbnails`.
3. Confira contraste, hierarquia, texto legível em tela pequena e ausência de conteúdo
   cortado. Preserve o HTML para edição e nova renderização.
4. Só capture PNG/JPG se browser ou Playwright estiver disponível na sessão. Antes de
   declarar sucesso, confira visualmente a renderização.

## Sem renderizador

Se browser/Playwright não estiver disponível, entregue o HTML, o plano de assets e instruções
de preview. Não prometa que uma imagem final foi gerada.

## Verificação

Registre dimensões, arquivos produzidos, fontes/ativos usados e o status real: `especificado`,
`renderizado` ou `aguardando renderizador`.
