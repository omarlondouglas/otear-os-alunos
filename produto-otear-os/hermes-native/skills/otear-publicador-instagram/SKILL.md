---
name: otear-publicador-instagram
description: Prepara e publica carrosséis no Instagram somente com integração configurada, consentimento explícito e confirmação final do aluno.
version: 0.1.0
author: Otear OS
license: UNLICENSED
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Otear, instagram, publicacao, carrossel]
    related_skills: [otear-noticias, otear-anuncios, otear-criador-imagens]
tools: [read_file, write_file, search_files]
---

# Otear Publicador de Instagram

Use para preparar um carrossel e, apenas no fim, publicar em uma conta que o aluno tenha
conectado e autorizado. Esta skill nunca publica por padrão.

## Fluxo seguro

1. Valide imagens finais, ordem, legenda, CTA, acessibilidade, conta de destino e direitos de
   uso. Salve o pacote em `produto-otear-os/entregas/anuncios/` ou
   `produto-otear-os/entregas/noticias/`, conforme o projeto.
2. Ofereça primeiro um `dry-run`: liste arquivos, ordem, legenda, conta e o que aconteceria.
   Não envie arquivos a hospedagem pública durante o dry-run.
3. Antes de publicar, confirme que Node, conta Instagram Business, Graph API e credenciais
   locais seguras estão configurados. Nunca peça ou grave tokens, chaves ou segredos em
   arquivos da vault.
4. Explique se a integração exigiria hospedar assets publicamente. Sem consentimento explícito
   do aluno, não hospede assets e não publique.
5. Peça uma confirmação explícita e inequívoca com a conta, o conjunto de imagens e a legenda
   final. Só então execute uma integração já configurada na máquina do aluno.
6. Registre resultado, horário, identificador/permalink retornado e erro, se houver, sem
   incluir credenciais.

## Limites

Não publique em conta pessoal ou não autorizada, não contorne políticas da plataforma e não
alegue publicação se a integração não retornou confirmação. Sem dependências, entregue apenas
o pacote pronto para publicação manual.
