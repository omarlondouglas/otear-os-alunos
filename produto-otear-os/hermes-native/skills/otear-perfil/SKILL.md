---
name: otear-perfil
description: Analisa perfis e presença digital a partir de material fornecido e consentido.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, perfil, instagram, analise]
    related_skills: [otear-router]
tools: [read_file, write_file, search_files]
---

# Otear Perfil

## Fontes e saída

Leia `produto-otear-os/squads-base/squad-analise-de-perfil.yaml` e
`produto-otear-os/sistemas-completos/opensquad/squads/instagram-scraper`. Salve em
`produto-otear-os/entregas/perfil/`.

## Procedimento

1. Peça URL, capturas ou dados que o usuário tenha permissão para analisar.
2. Avalie proposta, bio, conteúdo, prova, CTA, consistência e oportunidades.
3. Faça recomendações por prioridade; não colete dados privados nem burle plataformas.
4. Transforme pontos aprovados em plano de melhoria com exemplos.

## Requisitos

Scraping, login e APIs são módulos externos. Hermes só analisa material disponível com
autorização; OpenSquad é referência.

## Verificação

Entregue evidências observadas, recomendações e limitações de acesso.
