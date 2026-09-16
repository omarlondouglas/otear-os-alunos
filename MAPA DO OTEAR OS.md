---
title: Mapa do Otear OS
created: 2026-08-22
tags: [otear-os, mapa]
---

# Mapa do Otear OS

Este mapa mostra as capacidades prontas nesta entrega.

## Mapa Mestre Para Hermes

- [[SOUL]]

## Squads Disponiveis

| Squad | Uso |
|---|---|
| Squad Copy Otear | anuncios, emails, paginas, posts, VSLs e roteiros |
| Squad Campanha Completa | campanha com oferta, copy, conteudo e revisao |
| Squad Site Completo | landing page, pagina de venda, proposta online e site |
| Squad Sistema e App | aplicativos, automacoes, sistemas internos e produtos digitais |
| Squad Carrossel Avancado | carrossel com narrativa, design, imagens e publicacao |
| Squad Conteudo Social | posts, legendas, pautas e conteudo curto |
| Squad Conteudo Longo | artigos, aulas, guias e newsletters longas |
| Squad Calendario Editorial | pilares, calendario e rotina de publicacao |
| Squad Analise de Perfil | diagnostico de perfil e plano de conteudo |
| Squad Prospecção | leads, abordagem e qualificacao comercial |
| Squad Marca | posicionamento, tom de voz e mensagem |
| Squad Identidade Visual | direcao visual, paleta, componentes e regras |
| Squad Anuncio Estatico | conceito, copy e direcao visual de anuncio |
| Squad Video | roteiros de video curto ou longo |
| Squad Slides de Aula | estrutura de aula e slides |
| Squad Capas e Thumbnails | capas, thumbnails e primeiras telas |
| Squad Thumbnail YouTube | thumbnail de video |
| Squad Melhoria de Processos | mapear, simplificar e melhorar processos |
| Squad Criador de Agentes | criar agentes, skills e squads personalizados |
| Squad Tráfego Pago | planejar, criar anúncios, gerenciar campanhas e relatórios de tráfego |

## Sistemas Prontos

| Sistema | Pasta | Uso |
|---|---|---|
| Otear Prospeccao | `produto-otear-os/sistemas-prontos/otear-prospeccao` | agente/squad de prospeccao e aplicacao visual/CRM |
| Otear Videos | `produto-otear-os/sistemas-prontos/otear-videos` | transcrever link/arquivo de video e preparar analise de roteiro |
| Otear Sites | `produto-otear-os/sistemas-prontos/otear-sites` | criar landing pages, paginas de venda, paginas de captura e sites simples |

## Nucleo Unificado

Use `produto-otear-os/nucleo-otear/roteador-otear.yaml` como entrada para todas as capacidades. Ele aplica uma politica unica de modelos, confiabilidade e revisao; os pacotes tecnicos em `produto-otear-os/sistemas-completos` sao motores internos e nao sistemas separados para o aluno escolher.

| Capacidade Otear | Principais entregas |
|---|---|
| Otear Copy, Marca e Pesquisa | copy, marca, pesquisa profunda, SEO e criacao de squads |
| Otear Anuncios, Noticias e Thumbnails | anuncios, carrosseis com fontes, aulas, identidade visual e thumbnails |
| Otear Sistemas | apps, automacoes, processos e skills especializadas |

## Roteamento Rapido Para Sites

| Pedido | Usar |
|---|---|
| "cria uma landing page" | Otear Sites |
| "faz uma pagina de vendas" | Otear Sites |
| "quero uma pagina com WhatsApp/formulario" | Otear Sites |
| "revisa essa pagina" | Otear Sites + Squad Site Completo |

## Roteamento Rapido Para Video

| Pedido | Usar |
|---|---|
| "transcreve esse link" | Otear Videos |
| "pega a transcricao desse video" | Otear Videos |
| "analisa esse video e melhora meu roteiro" | Otear Videos + Squad Video |
| "transforma esse video em post/carrossel" | Otear Videos + Squad Conteudo Social ou Squad Carrossel Avancado |
| "cria um roteiro de video do zero" | Squad Video |

## Bibliotecas

| Biblioteca | Uso |
|---|---|
| biblioteca-copy | frameworks, roteamento e checklist de copy |

## Skills De Entendimento

| Skill | Uso |
|---|---|
| Modo Leigo | explicar temas complexos em linguagem simples |

## Onde Criar Coisas Novas

| Tipo | Pasta |
|---|---|
| Agente novo | `produto-otear-os/meus-agentes` |
| Skill nova | `produto-otear-os/minhas-skills` |
| Squad novo | `produto-otear-os/meus-squads` |
