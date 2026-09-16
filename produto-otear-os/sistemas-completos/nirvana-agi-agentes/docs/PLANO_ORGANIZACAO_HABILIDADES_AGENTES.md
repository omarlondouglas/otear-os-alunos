# Plano de organizacao por habilidades dos agentes

Data: 2026-06-26

## Diagnostico

O nome "O Tear Agentes" faz sentido como interface, mas o produto nao deveria ser organizado mentalmente por nomes de agentes. O que voce chegou agora e o denominador comum correto:

- pesquisar;
- analisar referencias;
- extrair modelo de criador/marca;
- criar roteiro/copy;
- gerar carrossel/imagem/thumbnail;
- editar video/cortar/legendar;
- guardar aprendizados e assets;
- mostrar o desenvolvimento do trabalho na interface.

Hoje o repositorio ainda carrega a historia de como ele foi construido: Claude assinatura, Hermes, Agno, squads, ferramentas soltas, sidecars e referencias copiadas. A organizacao nova deve separar:

1. **Interface do produto**: onde o usuario trabalha.
2. **Habilidades**: capacidades reutilizaveis.
3. **Agentes**: personas que usam habilidades.
4. **Tools**: funcoes reais que executam trabalho.
5. **Providers**: Claude, OpenAI, Gemini, Tavily, NewsAPI, etc.
6. **Memoria e referencias**: dados que melhoram os proximos trabalhos.

## Modelo mental recomendado

Pare de pensar assim:

```text
Usuario -> Jobs/GaryV/Ogilvy/Beast -> alguma tool
```

Pense assim:

```text
Usuario
  -> Interface
  -> Orquestrador por intencao
  -> Habilidade certa
  -> Tool/provider certo
  -> Resultado + logs + memoria + biblioteca
```

Os agentes viram uma camada opcional de personalidade/especialidade, nao a arquitetura principal.

## Habilidades principais

### 1. Pesquisa

Objetivo: buscar contexto atual, noticias, dados, tendencias e exemplos.

Hoje existe em:

- `web_search_tool`
- `get_news_tool`
- `app/services/news_digest/`
- `frontend-react/src/components/ui/news-radar-panel.tsx`

Deveria virar uma habilidade clara:

```text
research/
  search_web
  search_news
  summarize_sources
  extract_insights
  save_research
```

### 2. Referencias

Objetivo: receber links, perfis, imagens, videos e materiais de marca para o sistema entender estilo.

Hoje existe em:

- `frontend-react/src/components/ui/references-panel.tsx`
- `app/api/v1/endpoints/references.py`
- `list_creators_tool`
- `get_creator_style_tool`
- `list_creator_videos_tool`
- `get_creator_video_tool`
- `instagram_screenshot_tool`

Deveria virar:

```text
references/
  import_profile
  import_video
  import_image
  capture_instagram
  analyze_visual_style
  analyze_writing_style
  save_reference
```

### 3. Extracao de modelo

Objetivo: transformar referencias em um modelo reutilizavel de estilo.

Exemplos:

- "quero a pegada desse criador";
- "analise esses posts e extraia o padrao";
- "crie um modelo de roteiro baseado nesses videos";
- "faça minha marca falar assim, mas sem copiar".

Hoje esta espalhado entre:

- `Erico`
- `InstaVisualRef`
- `get_creator_style_tool`
- `app/knowledge/`
- `graphify_ref/` como referencia externa

Deveria virar:

```text
model_extraction/
  extract_voice_model
  extract_visual_model
  extract_content_structure
  extract_hooks
  create_style_guide
  compare_against_brand
```

### 4. Roteiro e copy

Objetivo: criar textos prontos para uso.

Hoje existe em:

- `Ogilvy`
- `Olivetto`
- `ClaraCopy`
- `save_script_tool`
- `frontend-react/src/components/ui/scripts-panel.tsx`

Deveria virar:

```text
writing/
  create_script
  create_carousel_copy
  create_ad_copy
  create_caption
  rewrite_in_style
  save_script
```

### 5. Criacao visual

Objetivo: gerar carrossel, imagem, thumbnail e capa.

Hoje existe em:

- `GaryV`
- `Scher`
- `NewsCarousel`
- `YouTuberThumbnail`
- `NeuroCover`
- `generate_carousel_tool`
- `generate_image_tool`
- `carrocel/`
- `chatgpt-bridge-service/`

Deveria virar:

```text
creation/
  create_carousel
  create_image
  create_thumbnail
  create_cover
  render_asset
  inspect_asset
```

### 6. Video

Objetivo: editar, cortar, legendar, transcrever, detectar momentos e renderizar.

Hoje existe em:

- `Nolan`
- `Beast`
- `app/workers/operations/`
- `edit_video_tool`
- `transcribe_video_tool`
- `select_viral_clips_tool`
- `detect_viral_moments_tool`
- `eval_cut_quality_tool`
- `fast_render_subtitles_tool`
- `remotion-service/`
- `agi-videos-temp/`

Deveria virar:

```text
video/
  transcribe
  detect_highlights
  select_clips
  clean_fillers
  add_subtitles
  render_short
  check_job_status
```

### 7. Memoria e biblioteca

Objetivo: lembrar preferencias, salvar assets e deixar o usuario reutilizar o que ja foi feito.

Hoje existe em:

- `app/orchestrator/memory.py`
- `app/services/user_memory.py`
- `app/services/profile_cache.py`
- `app/api/v1/endpoints/library.py`
- `frontend-react/src/components/ui/library-panel.tsx`
- `frontend-react/src/components/ui/settings-panel.tsx`

Deveria virar:

```text
memory/
  save_preference
  load_brand_context
  load_user_context
  save_asset
  save_learning
  retrieve_context
```

## Nova organizacao do produto

### Interface

A interface nao deveria destacar "agentes" primeiro. Ela deveria destacar os modos de trabalho:

```text
Painel principal
  Chat de projeto
  Pesquisa
  Referencias
  Modelos extraidos
  Roteiros
  Criacao
  Video
  Biblioteca
  Memoria/Marca
  Logs
```

Os agentes aparecem dentro do processo, nao como a navegacao principal.

Exemplo de nomes melhores para abas:

| Aba atual | Melhor nome | Motivo |
|---|---|---|
| Chat | Projeto | Conversa central com contexto |
| Criar | Criacao | Inclui carrossel, imagem, thumbnail |
| Roteiros | Roteiros | Mantem |
| News Radar | Pesquisa | Mais amplo que noticias |
| Referencias | Referencias | Mantem |
| Conexoes | Mapa de contexto | Mais claro para usuario |
| Biblioteca | Biblioteca | Mantem |
| Agencia | Workspace | Mais neutro |
| Config | Marca e memoria | O que o usuario realmente configura |
| Logs | Desenvolvimento | Mostra o trabalho dos agentes |

### Backend

Manter o backend atual por enquanto, mas criar uma camada conceitual de habilidades.

Estrutura futura:

```text
app/
  capabilities/
    research/
    references/
    model_extraction/
    writing/
    creation/
    video/
    memory/
  agents/
    personas/
    squads/
  tools/
    web.py
    news.py
    creators.py
    image.py
    carousel.py
    video.py
    storage.py
  providers/
    llm/
    search/
    image/
    storage/
  orchestrator/
  api/
```

Na pratica, nao precisa mover tudo agora. Primeiro documente e comece a criar nomes novos ao redor do que ja existe.

## Mudanca saindo da assinatura Claude

Hoje o codigo ainda esta muito acoplado a Claude:

- `app/core/model_factory.py` prioriza `ANTHROPIC_API_KEY` ou Claude CLI.
- `frontend-react/src/App.tsx` ainda tem `ClaudeSetupPage`.
- `app/core/claude_code_model.py` existe como adapter.
- `docker-compose.yml` injeta credenciais Claude.

O objetivo novo deveria ser:

```text
O produto usa um provedor LLM configuravel.
Claude e apenas um provider possivel.
```

### Nome melhor

Trocar mentalmente:

```text
Claude setup
```

por:

```text
LLM provider setup
```

### Providers possiveis

```text
providers/llm/
  anthropic.py
  openai.py
  google.py
  local.py
  router.py
```

Variaveis de ambiente futuras:

```env
LLM_PROVIDER=openai
LLM_PLANNER_MODEL=gpt-4.1
LLM_WRITER_MODEL=gpt-4.1
LLM_FAST_MODEL=gpt-4.1-mini

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

Ou, se quiser manter compatibilidade:

```env
MODEL_PROVIDER=openai
MODEL_PLANNER=
MODEL_WRITER=
MODEL_FAST=
```

### O que mudar primeiro

1. Renomear a tela `ClaudeSetupPage` para algo como `ProviderSetupPage`.
2. Alterar textos da interface para nao falar "Claude configurado".
3. Fazer `model_factory.py` escolher provider por `MODEL_PROVIDER`.
4. Manter Claude CLI como fallback local, mas nao como caminho principal.
5. Separar imagem de texto: Gemini/OpenAI imagem nao deve ser confundido com LLM de escrita.

## Organizacao dos agentes

Os agentes atuais podem continuar existindo, mas devem ser mapeados para habilidades:

| Agente atual | Papel novo |
|---|---|
| Jobs | Orquestrador legado/fallback |
| GaryV | Especialista de carrossel dentro de `creation` |
| Ogilvy | Especialista de copy dentro de `writing` |
| Olivetto | Especialista de roteiro dentro de `writing` |
| Erico | Especialista de modelagem de estilo dentro de `model_extraction` |
| Scher | Especialista visual dentro de `creation` |
| Nolan | Especialista de edicao simples dentro de `video` |
| Beast | Especialista de analise/corte viral dentro de `video` |
| ClaraCopy | Especialista de anuncio dentro de `writing` |
| NewsCarousel | Workflow de pesquisa + carrossel |
| YouTuberThumbnail | Workflow de thumbnail |
| NeuroCover | Workflow de capa |
| InstaVisualRef | Workflow de referencia visual |

Isso permite manter a personalidade sem deixar a arquitetura virar bagunca.

## Workflows que fazem sentido

### Workflow 1: referencia para modelo

```text
Usuario envia @, link, imagem ou video
  -> importar referencia
  -> analisar texto/visual/estrutura
  -> extrair padroes
  -> salvar modelo de estilo
  -> mostrar resumo na interface
```

### Workflow 2: pesquisa para roteiro

```text
Usuario pede tema atual
  -> pesquisar fontes
  -> resumir achados
  -> escolher angulo
  -> criar roteiro
  -> salvar em Roteiros/Biblioteca
```

### Workflow 3: modelo para criacao

```text
Usuario escolhe modelo salvo
  -> aplicar voz/visual
  -> gerar roteiro ou carrossel
  -> revisar contra preferencias da marca
  -> renderizar asset
  -> salvar na Biblioteca
```

### Workflow 4: video para cortes

```text
Usuario envia video
  -> transcrever
  -> detectar momentos
  -> sugerir cortes
  -> usuario aprova
  -> renderizar com legenda
  -> salvar resultado
```

### Workflow 5: memoria de marca

```text
Usuario corrige ou prefere algo
  -> detectar aprendizado
  -> salvar preferencia
  -> aplicar em proximas criacoes
```

## Como organizar as pastas sem quebrar tudo agora

Nao mova `app/agents/agno_tools.py` inteiro ainda. Ele esta grande, mas e o centro das tools. Primeiro crie documentos e modulos novos aos poucos.

Primeira etapa segura:

```text
docs/
  ORGANIZACAO_REPOSITORIO_AGENTES.md
  PLANO_ORGANIZACAO_HABILIDADES_AGENTES.md

app/
  capabilities/
    README.md
```

Depois, cada habilidade pode ganhar um facade fino que chama as tools antigas.

Exemplo:

```text
app/capabilities/research/service.py
  chama web_search_tool/get_news_tool

app/capabilities/creation/service.py
  chama generate_carousel_tool/generate_image_tool

app/capabilities/video/service.py
  chama edit_video_tool/select_viral_clips_tool/etc.
```

Assim voce muda a arquitetura sem quebrar os agentes.

## Proposta de `app/capabilities/README.md`

```text
Capabilities sao as habilidades estaveis do produto.

Agentes podem usar capabilities.
Chat pode chamar capabilities direto.
Workflows combinam varias capabilities.
Tools antigas continuam em app/agents/agno_tools.py ate serem extraidas.
```

## Prioridade de execucao

### Agora

1. Parar de organizar por persona.
2. Criar mapa de habilidades.
3. Separar interface em modos de trabalho.
4. Trocar "Claude setup" por "Provider setup".
5. Manter `ProjectOrchestrator` como caminho principal.

### Depois

1. Criar `app/capabilities/`.
2. Criar um registry de habilidades.
3. Fazer o chat chamar capabilities antes de chamar agentes.
4. Separar `agno_tools.py` em arquivos menores.
5. Transformar agentes em especialistas opcionais.

### Mais tarde

1. Mover sidecars para `apps/`.
2. Separar providers.
3. Criar um painel de workflows.
4. Criar versionamento de modelos extraidos.
5. Criar avaliacao de qualidade por habilidade.

## Decisao recomendada

O produto deve virar:

```text
Uma bancada de criacao com IA para pesquisa, referencias, roteiros, visual e video.
```

Nao:

```text
Uma lista de agentes com nomes legais.
```

Os agentes continuam uteis, mas como operadores especializados por tras das habilidades. A interface deve deixar o usuario pensar em trabalho real: pesquisar, modelar, escrever, criar, editar e salvar.
