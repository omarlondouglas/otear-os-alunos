# Estrutura atual do repositorio

Este repositorio esta organizado em camadas para separar produto ativo,
referencias, legado e artefatos locais.

## Produto ativo

```text
app/                    Backend FastAPI, agentes, tools, workers e services
frontend-react/          Interface principal
remotion-service/        Sidecar de renderizacao Remotion
chatgpt-bridge-service/  Sidecar de geracao de imagem
carrocel/                Sidecar de carrossel usado pelo docker-compose
alembic/                 Migracoes SQLAlchemy
supabase_migrations/     Migracoes Supabase
scripts/                 Scripts operacionais
tests/                   Testes e verificacoes
docs/                    Documentacao
```

## Agentes e habilidades

```text
app/agents/              Agentes Agno, squads e tools
app/orchestrator/        Roteamento principal do chat
app/capabilities/        Mapa novo das habilidades estaveis do produto
app/knowledge/           Knowledge base usada pelos squads/agentes
hermes_skills/           Skills do Hermes, opcional
.agents/skills/          Skills locais do ambiente de agente
.claude/skills/          Compatibilidade/legado Claude
```

## Referencias externas

```text
references/
  agent-dashboard-main/
  editordofuturo/
```

Ainda pendentes na raiz por permissao/bloqueio local:

```text
a2ui/
aios-core/
athena_ref/
ralph_ref/
graphify_ref/
hermes_ref/
chatgpt_bridge_ref/
```

Essas pastas parecem ser referencias/projetos copiados. Quando o bloqueio local
for resolvido, o destino correto e `references/`.

## Legado e conteudo

```text
legacy/content/O tear - conteudo/
frontend/                Frontend legado; ainda nao movido para evitar quebrar links
examples/                Exemplos legados; ainda mantidos na raiz
knowledge/               Knowledge antiga/raiz; revisar antes de mover
```

## Artefatos locais

```text
var/logs/                Logs e outputs temporarios antigos
var/tmp/                 Temporarios de execucao
var/downloads/           Downloads temporarios
var/cache/               Caches locais
storage/                 Storage runtime do backend; mantido na raiz por compatibilidade
videos/                  Videos runtime/legado; mantido na raiz por compatibilidade
```

## Regra daqui para frente

- Produto ativo fica na raiz somente se for chamado por import, compose ou script.
- Referencia externa vai para `references/`.
- Conteudo antigo vai para `legacy/`.
- Log, cache, download e temporario vao para `var/`.
- Novas habilidades entram primeiro em `app/capabilities/`.
