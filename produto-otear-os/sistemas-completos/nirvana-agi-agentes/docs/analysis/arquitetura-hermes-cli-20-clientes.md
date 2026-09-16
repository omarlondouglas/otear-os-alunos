# Decisao Arquitetural: Hermes, CLI e Operacao Para 20 Clientes

Data: 2026-05-30

## Contexto

Objetivo: operar criacao de conteudo e carrosseis para aproximadamente 20
clientes com baixo custo de API, maior automacao e possibilidade de usar a CLI
como motor principal de LLM.

Pergunta central:

> Manter Agno, migrar para Hermes ou combinar os dois?

## Diagnostico Atual

A aplicacao possui bons componentes de execucao:

- FastAPI
- Redis + Celery
- Renderizador de carrosseis
- FFmpeg, Whisper e Remotion
- Storage S3 compativel
- Contexto e memoria de marca
- News Radar agendado

O principal problema e a sobreposicao de camadas de orquestracao:

1. `ProjectOrchestrator`
2. `Team` legado do Agno (`Jobs`)
3. Hermes opcional

Tambem existem agentes com responsabilidades parcialmente repetidas:

- Ogilvy
- Olivetto
- GaryV
- Scher
- Erico
- Clara Copy
- News Carousel
- Neuro Cover
- Nolan
- Beast
- Neumeier

Boa parte desses agentes representa um prompt especializado com acesso a
ferramentas. Nem todos precisam permanecer como agentes autonomos carregados em
runtime.

## Decisao Recomendada

Usar:

- **Hermes como unico orquestrador conversacional**
- **FastAPI como camada deterministica de execucao**
- **Celery como motor de workflows assincronos**
- **Claude CLI Gateway como provider principal de texto**
- **Agno apenas como ponte temporaria durante a migracao**

Arquitetura desejada:

```text
Frontend / WhatsApp
  -> FastAPI
    -> Hermes
      -> Skills especializadas
      -> cria, consulta ou aprova jobs
    -> Workflow Engine
      -> Redis + Celery
      -> Workers
        -> Claude CLI Gateway
        -> Carousel Renderer
        -> FFmpeg / Whisper / Remotion
        -> Image Bridge
        -> Supabase / S3
```

## Papel De Cada Camada

### Hermes

Responsavel por:

- Entender pedidos do usuario
- Selecionar skills
- Criar jobs
- Solicitar aprovacao
- Consultar resultados
- Tratar excecoes

Hermes nao deve executar toda a producao de forma serial dentro de uma conversa.

### FastAPI

Responsavel por:

- Expor endpoints
- Validar entradas
- Persistir estados
- Disparar jobs
- Consultar status
- Executar tools deterministicas

### Celery

Responsavel por:

- Processar filas
- Retomar jobs
- Aplicar retries controlados
- Distribuir tarefas pesadas
- Executar producao em lote

### Claude CLI Gateway

Responsavel por:

- Serializar chamadas para CLI
- Limitar concorrencia
- Aplicar timeout
- Registrar latencia
- Fazer cache por hash
- Permitir troca futura para API sem alterar as skills

Configuracao inicial recomendada:

```text
CLI_CONCURRENCY=2
MAX_RETRIES=1
TIMEOUT=120
```

## Migracao Dos Agentes Agno

Nao migrar cada agente Agno para outro agente autonomo. Priorizar skills e
workflows.

| Agente atual | Destino recomendado |
|---|---|
| Ogilvy | Skill `copywriter-carousel` |
| Olivetto | Skill `roteiro-video` |
| GaryV | Skill `carousel-builder` |
| Scher | Skill `direcao-visual` |
| Erico | Skill `modelagem-estilo` |
| Clara Copy | Skill `meta-ads-copy` |
| News Carousel | Workflow agendado + skill de aprovacao |
| Neuro Cover | Skill `cover-director` |
| Beast | Workflow assincrono de video |
| Nolan | Tool direta de edicao por preset |
| Neumeier | Skill `brandcraft` |

Regra:

- **Skill**: raciocinio editorial
- **Tool direta**: execucao previsivel
- **Workflow**: varias etapas pesadas ou demoradas

## Operacao Para 20 Clientes

Exemplo de capacidade:

```text
20 clientes
x 5 conteudos por semana
= 100 conteudos por semana
```

Nao executar uma cadeia completa por post individualmente. Trabalhar em lotes.

### Fluxo Semanal Por Cliente

```text
brief da marca
  -> pesquisa consolidada por nicho
  -> calendario semanal com 5-10 ideias
  -> aprovacao humana
  -> geracao em lote das copys aprovadas
  -> revisao automatica em lote
  -> aprovacao humana
  -> geracao opcional de imagens
  -> render dos carrosseis
  -> biblioteca
  -> publicacao agendada
```

### Estados Persistidos

Cada conteudo deve possuir um estado:

```text
IDEA
DRAFT
AWAITING_APPROVAL
APPROVED
RENDERING
READY
SCHEDULED
PUBLISHED
FAILED
```

Isso permite retomar jobs interrompidos sem repetir chamadas de LLM.

## Como Reduzir Custo

### Usar Pesquisa Compartilhada Por Nicho

Se varios clientes atuam em fitness, nao pesquisar tendencias separadamente
para cada um.

```text
fitness -> 1 radar compartilhado
marketing -> 1 radar compartilhado
estetica -> 1 radar compartilhado
```

Depois personalizar os angulos conforme cada marca.

### Usar Chamadas Em Lote

Por cliente:

```text
1 chamada -> calendario semanal com 10 ideias
1 chamada -> copys dos 5 conteudos aprovados
1 chamada -> revisao consolidada das 5 copys
```

Estimativa inicial:

```text
20 chamadas para calendario
20 chamadas para copys em lote
20 chamadas para revisao em lote
= aproximadamente 60 chamadas editoriais por semana
```

Acrescentar pesquisas compartilhadas e imagens pontuais.

### Renderizar Sem LLM

Depois da aprovacao:

```text
copy estruturada em JSON
  -> template visual da marca
  -> renderer
```

Nao usar LLM para renderizar ou formatar slides previsiveis.

### Gerar Menos Imagens

Manter uma biblioteca visual por marca:

- Packshots
- Fotos lifestyle
- Fundos
- Paleta
- Fontes
- Templates
- Assets aprovados

Gerar imagem com IA apenas quando faltar um asset adequado. Carrosseis
educativos podem usar slides tipograficos e poucas imagens.

## Problemas Tecnicos A Corrigir

### Remover Guard LLM Do Fluxo Normal

O `GuardAgent` pode gerar uma chamada adicional para quase toda mensagem.

Substituir por regras locais. Usar LLM apenas para casos ambiguos.

### Remover Contexto Carregado Duas Vezes

O endpoint de chat e o `ProjectOrchestrator` carregam contexto. Centralizar essa
responsabilidade.

### Consolidar Providers

Existe cascata compartilhada e logica duplicada em servicos especificos.

Criar um unico `LLMGateway`:

```text
fast      -> modelo barato
writer    -> modelo intermediario
reviewer  -> modelo intermediario quando necessario
vision    -> provider de imagem
fallback  -> somente para falha tecnica
```

### Simplificar Deploy

Evitar processos duplicados e dois entrypoints FastAPI.

Estrutura recomendada:

```text
api
worker-video
worker-content
scheduler
redis
postgres
carousel-renderer
remotion-renderer
image-bridge
```

Usar somente `app.main:app` como API principal.

## Checkpoints Humanos

Manter dois pontos de aprovacao:

1. Aprovar calendario semanal
2. Aprovar copy antes de gerar imagens e renderizar

Esses checkpoints evitam gastar recursos em ideias rejeitadas.

## Ordem Recomendada De Migracao

1. Corrigir autenticacao da Claude CLI.
2. Ativar Hermes como unico chat.
3. Criar `LLMGateway` para CLI com fila e concorrencia limitada.
4. Migrar Ogilvy para skill nativa.
5. Migrar GaryV para skill + tool direta de carrossel.
6. Persistir workflow e estados de conteudo.
7. Migrar Nolan e Beast para workflows assincronos.
8. Migrar agentes editoriais restantes.
9. Remover Agno da rota principal.
10. Remover `ProjectOrchestrator` como orquestrador completo, preservando seus
    servicos deterministicas uteis.
11. Consolidar deploy em processos separados.

## Ressalva Sobre CLI-Only

Claude CLI via OAuth e adequado para operacao interna e producao assincrona de
baixo ou medio volume.

Para SaaS com muitos usuarios simultaneos, existem riscos:

- Subprocess por chamada
- Latencia maior
- Expiracao de autenticacao
- Limites da assinatura
- Baixa concorrencia
- Menor previsibilidade operacional que API oficial

Por isso, a arquitetura deve preservar uma interface de provider:

```text
LLMGateway
  -> claude-cli     # agora
  -> anthropic-api  # fallback ou futuro
```

## Resumo Da Decisao

A direcao recomendada e:

- Hermes como comandante
- Skills no lugar da maioria dos agentes
- Celery como motor operacional
- CLI com fila propria
- Producao em lote
- Render deterministico
- Aprovacao antes das etapas caras
- Agno apenas como ponte temporaria

O sistema central nao deve ser um superagente. Deve ser um workflow persistente,
retomavel e observavel.
