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

## Propósito e limites

Esta skill transforma um pedido do aluno em uma entrega verificavel usando apenas fontes portáteis da vault. Não inventa dados, acessos, permissões, resultados ou operações externas.

## Fontes portáteis

Localize uma única vault por `SOUL.md`. Leia e confirme a existência de cada caminho relativo antes de utilizá-lo:

- `produto-otear-os/nucleo-otear/CONTRATO-OPERACIONAL.md`
- `produto-otear-os/nucleo-otear/roteador-otear.yaml`
- `produto-otear-os/nucleo-otear/qualidade-e-confiabilidade.md`
- `produto-otear-os/skills-base/gerenciar-trafego-pago.skill.md`
- `produto-otear-os/agentes-base/gestor-de-trafego.agent.md`
- `produto-otear-os/squads-base/squad-trafego-pago.yaml`

## Entradas mínimas

Colete resultado esperado, público ou usuário, escopo, materiais disponíveis, restrições, prazo e critério de aceite. Peça somente a informação indispensável que faltar; sem ela, entregue um plano explicitamente marcado como incompleto.

## Fluxo operacional

1. Confirme rota, resultado esperado e itens fora de escopo. Registre requisitos que dependam de conta, permissão, integração ou autorização.
2. Leia as fontes específicas e extraia apenas instruções aplicáveis. Arquivo de referência não concede acesso a ferramenta, dado ou serviço.
3. Separe fatos, materiais fornecidos, decisões e hipóteses. Valide a origem de toda informação material antes de utilizá-la.
4. Produza o plano e o artefato em etapas, com versões identificáveis e justificativa para decisões que afetem mensagem, dados, qualidade ou risco.
5. Revise objetivo, público, restrições, coerência e rastreabilidade. Remova afirmações sem suporte e sinalize o que exige aprovação.
6. Salve em `produto-otear-os/entregas/trafego/` quando houver escrita autorizada. Reabra o arquivo para conferir conteúdo, caminhos relativos e ausência de dados sensíveis.

## Entregáveis

Entregue artefato principal, fontes usadas, premissas, decisões, pendências e próximo passo. Use nome descritivo e data quando ela ajudar a rastrear versões.

## Critérios de qualidade

A entrega só está pronta se atende ao objetivo, usa fontes acessíveis, separa fato de hipótese, respeita limites e pode ser localizada na vault. Nunca inclua segredos, caminhos pessoais ou prometa ação externa não executada.

## Fallback para integrações opcionais

Sem conta, permissão, browser, renderizador, API, runtime ou outro recurso opcional, não tente contornar a ausência. Entregue o artefato local preparatório, registre o requisito pendente e indique o menor próximo passo seguro.
