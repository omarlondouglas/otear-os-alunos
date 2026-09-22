---
name: otear-canva
description: Prepara ou cria peças no Canva quando a conta do aluno estiver conectada por OAuth/MCP, sem guardar segredos na vault.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, canva, design, apresentacoes]
    related_skills: [otear-aulas, otear-anuncios, otear-identidade-visual]
tools: [read_file, write_file, search_files]
---

# Otear Canva

Use para preparar, buscar, preencher ou exportar designs apenas quando a integração Canva da
sessão estiver conectada e autorizada pelo aluno.

## Processo

1. Confirme objetivo, formato, conteúdo aprovado, identidade visual e se o aluno quer criar,
   alterar, exportar ou apenas preparar a peça.
2. Verifique se o MCP/integração Canva e OAuth estão disponíveis. Se não estiverem, pare com
   uma instrução simples de conectar a conta; nunca peça, copie ou salve tokens na vault.
3. Com autorização ativa, trabalhe apenas no design ou template indicado pelo aluno. Apresente
   o que será criado ou alterado antes de ações que modifiquem um design existente.
4. Salve na vault um brief e referências em `produto-otear-os/entregas/<sistema>/`; registre
   somente o link/ID que o aluno autorizar compartilhar, sem credenciais.
5. Exporte o formato solicitado somente após checar conteúdo, marca e finalidade de uso.

## Sem integração

Produza um brief de Canva com textos, dimensões, paleta, assets autorizados e instruções de
montagem. Isso permite que o aluno conclua a peça manualmente sem expor a conta.

## Verificação

Informe se a entrega ficou `preparada`, `criada no Canva` ou `exportada`, além de formato,
dimensões e origem dos assets.
