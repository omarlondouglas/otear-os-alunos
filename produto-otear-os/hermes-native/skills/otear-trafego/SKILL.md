---
name: otear-trafego
description: Planeja e revisa campanhas de mídia paga e atende também a rota Tráfego Pago.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, trafego, ads, campanhas]
    related_skills: [otear-router, otear-relatorios-trafego]
tools: [read_file, write_file, search_files]
---

# Otear Tráfego

Esta skill atende `Otear Trafego` e o alias `Otear Trafego Pago`.

## Fontes e saída

Leia `produto-otear-os/skills-base/gerenciar-trafego-pago.skill.md`,
`produto-otear-os/agentes-base/gestor-de-trafego.agent.md` e
`produto-otear-os/squads-base/squad-trafego-pago.yaml`. Salve em
`produto-otear-os/entregas/trafego/`.

## Procedimento

1. Colete oferta, objetivo, orçamento, mercado, período, dados históricos e limites.
2. Defina funil, público, mensagem, criativos, evento de conversão e hipótese de teste.
3. Monte plano de campanha e revisão de risco; não publique, gaste orçamento ou afirme
   acesso a contas sem autorização explícita.
4. Revise métricas, conformidade da plataforma e próxima decisão.

## Requisitos

APIs de Meta/Google e contas de anúncio são externas. Skills legadas do perfil Hermes
são referência e não são executadas automaticamente.

## Verificação

Entregue plano, rastreamento necessário, critérios de pausa/escala e pendências.
