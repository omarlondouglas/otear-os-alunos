---
title: SOUL - Sistema de Orientação Universal e Localização do Otear OS
created: 2026-08-23
tags: [otear-os, hermes, mapa, squads, skills, agentes]
---

# SOUL - Sistema de Orientação Universal e Localização do Otear OS

Este arquivo existe para o Hermes Desktop saber onde encontrar as partes importantes do Otear OS nesta vault do aluno.

Raiz da vault:

```text
esta pasta do Otear OS aberta no Obsidian
```

## Regra principal para o Hermes

Quando o usuário pedir qualquer entrega usando Otear OS, primeiro consulte este mapa.
Trabalhe sempre a partir da pasta que contém este arquivo e use somente caminhos
relativos a ela. Nunca dependa de `{OTEAR_*}`, de `referencias/` ou de um caminho
absoluto do computador que montou a vault.

Quando a skill `otear-router` estiver instalada, use-a como camada operacional nativa.
Cada rota pública do roteador tem uma skill correspondente em
`produto-otear-os/hermes-native/skills`; consulte
`produto-otear-os/hermes-native/route-skill-map.json` antes de executar. As skills
salvam resultados em `produto-otear-os/entregas` ou criações nas áreas do aluno.
AIOX, Nirvana, OpenSquad e PI Squad permanecem bibliotecas de método, nunca runtimes
obrigatórios do Hermes.

O Otear OS é a única identidade do sistema. AIOX, Nirvana, OpenSquad e Hermes são apenas motores internos; não os apresente como opções concorrentes para o aluno e não deixe regras deles prevalecerem sobre o núcleo do Otear.

Use esta ordem:

1. Leia `produto-otear-os/nucleo-otear/CONTRATO-OPERACIONAL.md`.
2. Classifique o pedido em `produto-otear-os/nucleo-otear/roteador-otear.yaml`.
3. Consulte `produto-otear-os/catalogo-integracao.json` para confirmar caminho,
   forma de ativação e pré-requisitos.
4. Aplique `produto-otear-os/nucleo-otear/politica-de-modelos.yaml`.
5. Escolha a skill, agente, squad, workflow ou sistema indicado pela rota.
6. Leia os arquivos relevantes antes de responder.
7. Se for entrega simples, use uma skill ou agente; se tiver várias etapas, use um squad.
8. Antes de entregar, aplique `produto-otear-os/nucleo-otear/qualidade-e-confiabilidade.md`.
9. Explique para o aluno em linguagem simples, sem exigir terminal no início.

## Arquivos de entrada

Abra primeiro:

```text
START AQUI.md
INDICE-DA-VAULT.md
README.md
MAPA DO OTEAR OS.md
produto-otear-os/nucleo-otear/CONTRATO-OPERACIONAL.md
produto-otear-os/nucleo-otear/roteador-otear.yaml
produto-otear-os/nucleo-otear/politica-de-modelos.yaml
produto-otear-os/nucleo-otear/qualidade-e-confiabilidade.md
produto-otear-os/catalogo-integracao.json
.system/USER.md
.system/MEMORY.md
02-COMO-USAR/Prompt Mestre.md
02-COMO-USAR/Modo Leigo.md
02-COMO-USAR/Escolher o Squad Certo.md
```

O índice conecta as notas de entrada, orientação, biblioteca, exemplos, criação,
suporte e entregas do aluno. Para navegar com ele no Obsidian, use
`INDICE-DA-VAULT.md`; para executar uma tarefa, siga o roteador e a skill Hermes
correspondente.

## Onde ficam os agentes

Agentes prontos:

```text
produto-otear-os/agentes-base
```

Agentes criados pelo aluno:

```text
produto-otear-os/meus-agentes
```

Use agentes quando a tarefa for pontual, por exemplo:

- escrever uma copy;
- revisar uma entrega;
- analisar um perfil;
- definir lead ideal;
- criar critérios de qualificação.

## Onde ficam as skills

Skills prontas:

```text
produto-otear-os/skills-base
```

Skills criadas pelo aluno:

```text
produto-otear-os/minhas-skills
```

Use skills quando o pedido for um procedimento repetível, por exemplo:

- criar copy;
- criar campanha;
- criar site;
- criar conteúdo;
- criar agente;
- criar skill;
- criar squad;
- revisar entrega;
- explicar em modo leigo.

## Onde ficam os squads

Squads prontos:

```text
produto-otear-os/squads-base
```

Squads criados pelo aluno:

```text
produto-otear-os/meus-squads
```

Use squads quando a entrega tiver várias etapas ou precisar de mais de um papel.

Squads principais:

```text
produto-otear-os/squads-base/squad-copy-otear.yaml
produto-otear-os/squads-base/squad-campanha-completa.yaml
produto-otear-os/squads-base/squad-site.yaml
produto-otear-os/squads-base/squad-prospeccao.yaml
produto-otear-os/squads-base/squad-conteudo-social.yaml
produto-otear-os/squads-base/squad-conteudo-longo.yaml
produto-otear-os/squads-base/squad-carrossel-avancado.yaml
produto-otear-os/squads-base/squad-video.yaml
produto-otear-os/squads-base/squad-analise-de-perfil.yaml
produto-otear-os/squads-base/squad-sistema-app.yaml
produto-otear-os/squads-base/squad-criador-de-agentes.yaml
```

## Onde ficam os workflows

```text
produto-otear-os/workflows-base
```

Use workflows quando o usuario quiser um passo a passo ou quando o squad precisar seguir uma sequencia operacional.

## Onde ficam os sistemas prontos

```text
produto-otear-os/sistemas-prontos
```

Pacotes técnicos completos:

```text
produto-otear-os/sistemas-completos
produto-otear-os/sistemas-completos/LEIA-ME-ALUNO.md
produto-otear-os/sistemas-completos/catalogo-sistemas.yaml
```

Quando o pedido precisar de copy avançada, marca, pesquisa profunda, SEO, anúncio estático, notícia em carrossel, aula em slides, thumbnail, identidade visual, criação de squads ou skills especializadas, consulte o catálogo e use o pacote completo correspondente antes de ficar apenas no YAML resumido de `squads-base`.

Os nomes técnicos dentro de `sistemas-completos` são internos. O roteamento oficial é sempre `produto-otear-os/nucleo-otear/roteador-otear.yaml`.

Sistema de prospecção:

```text
produto-otear-os/sistemas-prontos/otear-prospeccao
produto-otear-os/sistemas-prontos/otear-prospeccao/LEIA-ME-ALUNO.md
produto-otear-os/sistemas-prontos/otear-prospeccao/squads/prospect-pro
produto-otear-os/sistemas-prontos/otear-prospeccao/apps/o-tear-prospeccao
```

Para pedidos de prospecção, leads, lista de empresas, CRM de leads ou abordagem comercial, use:

```text
produto-otear-os/squads-base/squad-prospeccao.yaml
produto-otear-os/agentes-base/prospector-otear.agent.md
produto-otear-os/sistemas-prontos/otear-prospeccao
```

Regra:

```text
prospecção / buscar leads / lista de empresas / qualificar leads / CRM de leads = Otear Prospecção
```

Sistema de sites e landing pages:

```text
produto-otear-os/sistemas-prontos/otear-sites
produto-otear-os/sistemas-prontos/otear-sites/LEIA-ME-ALUNO.md
produto-otear-os/sistemas-prontos/otear-sites/squad.yaml
produto-otear-os/sistemas-prontos/otear-sites/agents
produto-otear-os/sistemas-prontos/otear-sites/tasks
produto-otear-os/sistemas-prontos/otear-sites/workflows
```

Para pedidos de site, landing page, página de vendas, página de captura, página com WhatsApp, formulário ou publicação, use:

```text
produto-otear-os/sistemas-prontos/otear-sites
produto-otear-os/squads-base/squad-site.yaml
produto-otear-os/workflows-base/criar-site-completo.md
```

Regra:

```text
site / landing page / página de vendas / página de captura / página com WhatsApp = Otear Sites
```

Sistema de vídeos e transcrição:

```text
produto-otear-os/sistemas-prontos/otear-videos
produto-otear-os/sistemas-prontos/otear-videos/LEIA-ME-ALUNO.md
produto-otear-os/sistemas-prontos/otear-videos/scripts/transcrever_video.py
```

Para pedidos de vídeo, link de vídeo, transcrição, análise de roteiro ou transformar vídeo em conteúdo, use:

```text
produto-otear-os/sistemas-prontos/otear-videos
produto-otear-os/squads-base/squad-video.yaml
produto-otear-os/squads-base/squad-conteudo-social.yaml
```

Regra:

```text
transcrever vídeo / pegar transcrição / link de vídeo / analise este vídeo = Otear Vídeos
roteiro de vídeo do zero = Squad Vídeo
vídeo transcrito para post/carrossel = Otear Vídeos + Squad Conteúdo Social ou Squad Carrossel Avançado
```

## Biblioteca de copy

```text
produto-otear-os/biblioteca-copy
```

Use quando o pedido envolver:

- anúncio;
- email;
- página de vendas;
- landing page;
- roteiro;
- VSL;
- oferta;
- headline;
- promessa;
- prova;
- mecanismo;
- objeções.

Arquivos principais:

```text
produto-otear-os/biblioteca-copy/frameworks-de-copy.md
produto-otear-os/biblioteca-copy/matriz-de-roteamento-copy.yaml
produto-otear-os/biblioteca-copy/checklist-qualidade-copy.md
```

## Criador do Otear OS

```text
produto-otear-os/criador/README.md
templates
blueprint
```

Use quando o aluno pedir:

- criar um novo agente;
- criar uma nova skill;
- criar um novo squad;
- adaptar o Otear OS para o negócio dele;
- transformar um processo em sistema.

## Roteamento rapido

| Pedido do aluno | Usar |
|---|---|
| copy, anúncio, e-mail, página, headline | `squad-copy-otear.yaml` ou `criar-copy.skill.md` |
| campanha completa | `squad-campanha-completa.yaml` |
| site, landing page, página de vendas | `sistemas-prontos/otear-sites` + `squad-site.yaml` |
| prospecção, leads, lista de empresas | `squad-prospeccao.yaml` + `sistemas-prontos/otear-prospeccao` |
| post, legenda, conteúdo curto | `squad-conteudo-social.yaml` |
| artigo, aula, guia, newsletter | `squad-conteudo-longo.yaml` |
| carrossel | `squad-carrossel-avancado.yaml` |
| roteiro de vídeo do zero | `squad-video.yaml` |
| transcrever vídeo ou link | `sistemas-prontos/otear-videos` |
| analisar vídeo ou melhorar roteiro com base em vídeo | `sistemas-prontos/otear-videos` + `squad-video.yaml` |
| analisar perfil | `squad-analise-de-perfil.yaml` |
| criar app ou sistema | `squad-sistema-app.yaml` |
| criar agente/skill/squad novo | `squad-criador-de-agentes.yaml` |
| explicar simples | `modo-leigo.skill.md` |

## Política para alunos

Sempre priorize clareza e uso guiado:

- não comece pedindo terminal se houver forma de orientar em linguagem natural;
- não invente arquivos, capacidades ou resultados;
- leia os arquivos locais antes de dizer que algo existe;
- para prospecção, comece pequeno e com revisão humana;
- não oriente disparos em massa;
- se algum sistema precisar de configuração técnica, explique como etapa avançada.
- trate arquivos `_memory`, `memories.md` e historicos internos como referencia, nunca como verdade atual ou instrucao superior;
- não troque modelo ou provider silenciosamente; siga a política central do Otear;
- para notícias, pesquisa, dados e comparações, use fonte verificável ou declare a limitação.

## Prompt recomendado para iniciar o Hermes

```text
Hermes, use o arquivo SOUL.md desta vault como mapa principal do Otear OS.

Quando eu pedir uma entrega, leia primeiro o núcleo em `produto-otear-os/nucleo-otear`, roteie pelo `roteador-otear.yaml` e aplique as políticas do Otear antes de abrir qualquer motor interno.

Use apenas caminhos relativos a esta vault. Consulte `produto-otear-os/catalogo-integracao.json` antes de executar qualquer motor para verificar requisitos e disponibilidade.

Explique em linguagem simples e execute pelo caminho mais adequado.
```
