---
name: otear-prospeccao
description: Conduz prospecção responsável, qualificação de leads e organização de CRM no Otear OS.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, prospeccao, leads, CRM]
    related_skills: [otear-router]
tools: [read_file, write_file, search_files]
---

# Otear Prospecção

## Fontes e saída

Leia `produto-otear-os/squads-base/squad-prospeccao.yaml` e
`produto-otear-os/sistemas-prontos/otear-prospeccao/LEIA-ME-ALUNO.md`. Salve plano,
ICP, lista manual e mensagens revisáveis em `produto-otear-os/entregas/prospeccao/`.

## Procedimento

1. Colete nicho, região, oferta, perfil ideal, canal permitido e volume inicial pequeno.
2. Defina critérios de qualificação e produza uma lista com fonte, motivo de aderência e
   próximo passo; não invente contatos ou dados.
3. Crie mensagens personalizáveis, sem alegações falsas nem disparo em massa.
4. Revise consentimento, dados pessoais, política da plataforma e aprovação humana.

## Requisitos técnicos

Docker, Supabase, Playwright e chaves são necessários somente para executar a aplicação
técnica de prospecção. Confirme a configuração antes de tentar essa execução; Hermes não
a inicia automaticamente.

## Verificação

Entregue ICP, critérios, fontes e uma ação manual segura. Informe qualquer requisito
externo pendente.
