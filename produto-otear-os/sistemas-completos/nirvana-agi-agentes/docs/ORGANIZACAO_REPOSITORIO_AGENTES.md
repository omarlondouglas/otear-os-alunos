# Organizacao do repositorio de agentes

Data da analise: 2026-06-26

Este repositorio virou uma mistura de produto ativo, sidecars, referencias copiadas, experimentos, scripts de diagnostico, conhecimento de agentes e arquivos temporarios. A boa noticia: existe um nucleo claro. A arrumacao deve preservar esse nucleo e tirar da raiz tudo que nao precisa estar no caminho diario.

## Leitura rapida

O sistema ativo parece ser:

```text
frontend-react/ -> app/ FastAPI -> ProjectOrchestrator -> tools/agentes -> sidecars
```

Arquivos centrais:

- `app/main.py`: entrada FastAPI.
- `app/api/v1/router.py`: registra endpoints.
- `app/orchestrator/project_orchestrator.py`: caminho principal do chat.
- `app/orchestrator/router.py`: classificacao de intencao.
- `app/agents/agno_agents.py`: agentes Agno principais.
- `app/agents/squad_agents.py`: squads adaptados.
- `app/agents/agno_tools.py`: ferramentas reais usadas pelos agentes.
- `frontend-react/`: interface atual em React/Vite.
- `remotion-service/`: sidecar para renderizacao Remotion.
- `chatgpt-bridge-service/`: sidecar para geracao de imagem via bridge.
- `carrocel/`: sidecar legado/externo de carrossel, usado pelo compose.
- `agi-videos-temp/`: referencia/servico temporario de video, nao deveria ficar como pasta de produto no root.

## Problema atual

A raiz do repositorio esta fazendo papeis demais ao mesmo tempo:

1. Produto principal: `app/`, `frontend-react/`, `remotion-service/`, `chatgpt-bridge-service/`, `docker-compose.yml`.
2. Sidecars ou projetos copiados: `carrocel/`, `agi-videos-temp/`, `editordofuturo/`.
3. Referencias: `aios-core/`, `a2ui/`, `agent-dashboard-main/`, `athena_ref/`, `ralph_ref/`, `graphify_ref/`, `hermes_ref/`, `chatgpt_bridge_ref/`.
4. Conhecimento e prompts de agentes: `app/knowledge/`, `hermes_skills/`, `.agents/skills/`, `.claude/skills/`, `knowledge/`.
5. Scripts operacionais e de diagnostico: `scripts/`, varios `.bat` e `.py` antigos que ja foram movidos parcialmente.
6. Temporarios/logs/downloads: `tmp_*`, `mini_video_*`, `tmp_garyvee/`, `mini_video_downloads/`, `videos/`, `storage/`, `__pycache__/`.
7. Frontend legado: `frontend/`, aparentemente HTML/CSS/JS simples, diferente do `frontend-react/`.

O efeito pratico: fica dificil saber o que roda, o que e biblioteca, o que e referencia, e o que pode apagar/mover.

## O que faz sentido ficar junto

### 1. Produto principal

Deve ficar junto porque sobe como uma plataforma unica:

```text
app/
frontend-react/
remotion-service/
chatgpt-bridge-service/
alembic/
supabase_migrations/
docker-compose.yml
Dockerfile
requirements.txt
.env.example
```

Esse grupo representa o sistema O Tear/AGI Agentes atual.

### 2. Agentes, tools e orquestracao

Dentro do backend, estes arquivos deveriam ser tratados como uma unidade:

```text
app/orchestrator/
app/agents/
app/workers/
app/services/
app/knowledge/
```

Regra mental:

- `orchestrator/`: decide o que fazer.
- `agents/`: define personas/agentes/squads.
- `agents/agno_tools.py`: ponte entre agentes e a execucao real.
- `services/`: implementa servicos de dominio.
- `workers/`: jobs assicronos e operacoes de video.
- `knowledge/`: prompts, bases e regras que os agentes leem.

### 3. Skills de agente

Hoje existem pelo menos tres lugares parecidos:

```text
.agents/skills/
.claude/skills/
hermes_skills/
```

Proposta:

- `.agents/skills/`: skills locais do ambiente de agente.
- `.claude/skills/`: compatibilidade Claude, se ainda for usada.
- `hermes_skills/`: skills que pertencem ao Hermes/produto.

Nao misturar esses tres sem decisao explicita. Eles parecem ter consumidores diferentes.

### 4. Referencias externas

Estas pastas parecem ser repositorios ou projetos usados como fonte de inspiracao/copia:

```text
a2ui/
agent-dashboard-main/
aios-core/
athena_ref/
ralph_ref/
graphify_ref/
hermes_ref/
chatgpt_bridge_ref/
editordofuturo/
```

Elas nao deveriam competir visualmente com o produto principal na raiz. O lugar correto e uma pasta unica de referencias.

### 5. Artefatos temporarios

Tudo abaixo e saida de execucao, teste, download ou log:

```text
tmp_*
tmp_garyvee/
mini_video_downloads/
mini_video_server.log
mini_video_server.err.log
videos/
storage/
__pycache__/
```

Isso deve sair da leitura normal do projeto e ficar ignorado pelo Git.

## Estrutura proposta

Proposta conservadora, pensando em mover depois sem quebrar imports imediatamente:

```text
agi-agentes/
  README.md
  docker-compose.yml
  Dockerfile
  .env.example
  requirements.txt
  requirements-hermes.txt
  requirements-minimal-video.txt

  apps/
    api/
      app/
      alembic/
      alembic.ini
      supabase_migrations/
      supabase_schema.sql
      supabase_migration_multitenant.sql
      api_gateway.py
      mini_video_backend.py
    web/
      frontend-react/
    web-legacy/
      frontend/
    remotion/
      remotion-service/
    chatgpt-bridge/
      chatgpt-bridge-service/
    carousel/
      carrocel/

  agents/
    runtime/
      hermes_skills/
    local/
      .agents/skills/
    claude/
      .claude/skills/
    knowledge/
      app/knowledge/
      knowledge/

  packages/
    aios-core/

  references/
    a2ui/
    agent-dashboard-main/
    athena_ref/
    ralph_ref/
    graphify_ref/
    hermes_ref/
    chatgpt_bridge_ref/
    editordofuturo/

  ops/
    docker/
    scripts/
      windows/
      diagnose/
      verify/
      manual/
      utils/
      debug/
    supervisord.conf
    entrypoint.sh
    start.sh

  docs/
    architecture/
    guides/
    deploy/
    fixes/
    analysis/
    archive/
    stories/

  tests/
    unit/
    integration/
    smoke/
    shell/

  var/
    storage/
    videos/
    downloads/
    logs/
    tmp/
```

## Estrutura alternativa menos invasiva

Se voce quiser organizar sem mudar imports e caminhos agora, use esta etapa intermediaria:

```text
agi-agentes/
  app/
  frontend-react/
  remotion-service/
  chatgpt-bridge-service/
  carrocel/
  alembic/
  supabase_migrations/
  scripts/
  tests/
  docs/

  references/
    a2ui/
    agent-dashboard-main/
    aios-core/
    athena_ref/
    ralph_ref/
    graphify_ref/
    hermes_ref/
    chatgpt_bridge_ref/
    editordofuturo/

  legacy/
    frontend/
    examples/
    O tear - conteudo/

  var/
    storage/
    videos/
    mini_video_downloads/
    tmp_garyvee/
    logs/
```

Esta e a melhor primeira arrumacao porque quase nao exige alterar codigo. Voce so move referencias, legado e artefatos temporarios.

## Plano de migracao recomendado

### Fase 1: limpar a raiz sem quebrar o produto

Mover para `references/`:

```text
a2ui/
agent-dashboard-main/
aios-core/
athena_ref/
ralph_ref/
graphify_ref/
hermes_ref/
chatgpt_bridge_ref/
editordofuturo/
```

Mover para `legacy/`:

```text
frontend/
examples/
O tear - conteudo/
```

Mover para `var/` ou apagar se forem descartaveis:

```text
tmp_*
tmp_garyvee/
mini_video_downloads/
mini_video_server.log
mini_video_server.err.log
videos/
storage/
__pycache__/
```

Antes de mover `carrocel/` e `agi-videos-temp/`, verificar se o ambiente atual ainda depende deles. O `docker-compose.yml` usa `carrocel/` diretamente.

### Fase 2: consolidar documentacao

Manter `README.md` como guia principal de uso.

Dentro de `docs/`:

```text
docs/
  architecture/   # arquitetura real, diagramas, decisoes
  guides/         # como usar/testar
  deploy/         # EasyPanel, Docker, producao
  fixes/          # correcoes tecnicas ainda relevantes
  analysis/       # analises de marca, produto e investigacoes
  archive/        # historico antigo que nao guia mais operacao diaria
  stories/        # historias AIOS
```

Hoje ja existem `docs/guides`, `docs/deploy`, `docs/fixes`, `docs/analysis`, `docs/archive` e `docs/stories`, entao a regra e mais de disciplina do que de criacao.

### Fase 3: separar testes por intencao

Hoje `tests/` mistura smoke checks, testes manuais e integracao. Proposta:

```text
tests/
  unit/
  integration/
  smoke/
  shell/
```

Exemplos:

- `test_simple.py`, `test_search.py`: `tests/smoke/` ou `tests/unit/`, dependendo do conteudo.
- `test_video_endpoints.py`, `test_webhook.py`: `tests/integration/`.
- `tests/shell/*.sh`: manter em `tests/shell/`.
- Scripts que imprimem diagnostico e nao assertam nada deveriam ir para `scripts/diagnose/`.

### Fase 4: decidir o papel do Hermes

O `README.md` atual diz que Hermes e opcional. Entao a organizacao deveria refletir isso:

```text
hermes_skills/               # plugin/skills do Hermes usados pelo produto
app/services/hermes_engine.py # integracao opcional no backend
app/api/v1/endpoints/hermes_chat.py
requirements-hermes.txt
```

Se Hermes continuar opcional, nao deixe arquivos Hermes parecerem caminho principal.

### Fase 5: mover sidecars com cuidado

Sidecars que podem virar `apps/*` depois:

```text
carrocel/ -> apps/carousel/
remotion-service/ -> apps/remotion/
chatgpt-bridge-service/ -> apps/chatgpt-bridge/
```

Mas isso exige atualizar:

- `docker-compose.yml`
- `README.md`
- scripts em `scripts/windows/`
- variaveis de ambiente/documentacao
- qualquer path hardcoded em codigo

Por isso eu deixaria essa fase para depois da limpeza inicial.

## Regras de organizacao daqui para frente

1. Pasta de produto nao deve ser referencia. Se e copia/fonte de estudo, vai para `references/`.
2. Saida de execucao vai para `var/`, `storage/`, `tmp/` ou `logs/`, nunca para a raiz.
3. Script que muda ambiente fica em `scripts/`; script que prova comportamento fica em `tests/`.
4. Prompt/knowledge que o backend usa fica em `app/knowledge/`.
5. Skill que o agente local usa fica em `.agents/skills/`.
6. Skill do Hermes fica em `hermes_skills/`.
7. Docs antigas vao para `docs/archive/`, docs operacionais ficam em `docs/guides/` ou `docs/deploy/`.
8. Frontend ativo e `frontend-react/`; `frontend/` deve ser marcado como legado ou removido.

## O que eu nao moveria ainda

Nao mover agora:

```text
app/
frontend-react/
remotion-service/
chatgpt-bridge-service/
carrocel/
alembic/
supabase_migrations/
scripts/
tests/
docs/
```

Motivo: esses nomes aparecem em configs, compose, docs e possivelmente scripts. Primeiro limpar referencias e temporarios. Depois fazer migracao estrutural com testes.

## Checklist de arrumacao segura

1. Criar `references/`, `legacy/` e `var/`.
2. Mover apenas pastas que ja estao no `.gitignore` como referencias.
3. Rodar `git status --short` para confirmar o impacto.
4. Atualizar `.gitignore` para incluir `var/`, `*.log`, `tmp_*`, `mini_video_downloads/`.
5. Atualizar `README.md` com a estrutura reduzida.
6. Rodar smoke checks:

```powershell
python -c "from app.main import app; print(app.title)"
python -c "from app.orchestrator.router import classify_intent; print(classify_intent('crie um carrossel sobre IA').value)"
```

7. Se usar Docker, rodar:

```powershell
docker compose config
```

8. So depois planejar a migracao para `apps/`.

## Minha recomendacao final

Comece pela estrutura intermediaria. Ela resolve a confusao visual sem tocar no caminho critico.

Prioridade:

1. Tirar referencias grandes da raiz.
2. Tirar temporarios/logs/downloads da raiz.
3. Declarar `frontend-react/` como frontend oficial e `frontend/` como legado.
4. Manter `app/` como backend oficial.
5. Tratar `carrocel/`, `remotion-service/` e `chatgpt-bridge-service/` como sidecars do produto.
6. So depois reorganizar para `apps/`, quando houver tempo para atualizar compose, scripts e docs.
