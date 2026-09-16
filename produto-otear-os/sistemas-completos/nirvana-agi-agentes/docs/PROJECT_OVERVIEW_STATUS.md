# O Tear Agentes - Visao do Projeto e Pendencias

## Proposta

O O Tear Agentes e uma plataforma de criacao de conteudo digital assistida por agentes de IA. A proposta e concentrar, em uma unica interface, fluxos de trabalho que hoje ficam espalhados entre chat, editores de video, geradores de imagem, roteiristas, ferramentas de pesquisa, bibliotecas de assets e automacoes de marca.

O sistema se propoe a ajudar criadores, marcas e operacoes de conteudo a transformar ideias, referencias e materiais brutos em entregaveis prontos ou semi-prontos, como:

- roteiros;
- copys;
- estrategias de campanha;
- carrosseis;
- imagens;
- videos editados;
- cortes virais;
- legendas;
- analises de referencias;
- biblioteca de assets;
- memoria operacional da marca.

## Como o Produto Funciona Hoje

O caminho principal da aplicacao e:

```text
Frontend React
  -> FastAPI Gateway
    -> ProjectOrchestrator
      -> classifica intencao
      -> carrega contexto/memoria
      -> chama tools, agentes ou servicos auxiliares
      -> retorna resposta, URLs ou job_ids
```

O `ProjectOrchestrator` e o nucleo atual do chat. Ele substitui a dependencia direta de um time Agno/Hermes no caminho critico da interface. Hermes continua existindo como opcional, mas a recomendacao operacional atual e manter `ENABLE_HERMES=false` ate o nucleo principal estar estavel.

## Modulos Principais

### Chat de Projeto

Interface principal para conversar com o sistema. O chat deve responder de forma natural e acionar ferramentas quando o pedido indicar uma tarefa concreta, como roteiro, estrategia, imagem, carrossel ou video.

Estado atual:

- usa `/api/v1/chat/stream`;
- recebe eventos SSE;
- registra logs dos agentes;
- carrega contexto de usuario/marca quando disponivel;
- ja foi ajustado para esconder a lista tecnica de orquestracao da conversa principal.

### Editor de Video

Modulo para upload ou uso de URL direta de video, com chat especializado para pedir edicoes.

Capacidades previstas/atuais:

- upload de video;
- uso de URL direta de video acessivel pelo servidor;
- presets como `VIRAL`, `AULA`, `CLEAN`, `HORMOZI`, `PODCAST`;
- corte por tempo via `trim`;
- remocao de silencio via FFmpeg;
- legendas automaticas;
- extracao de melhores momentos;
- pipelines PRO/AI com Remotion e analise de cenas.

Observacao importante: os cortes simples e remocao de silencio nao sao feitos pelo Remotion. Eles passam por workers Celery e handlers FFmpeg. Remotion entra nos presets PRO/AI como etapa de render/motion/overlays.

### Carrossel

Fluxo para criar carrosseis a partir de prompts e contexto da marca.

Estado atual:

- existe service separado de carrossel;
- o backend chama tools de carrossel;
- depende de URL e chave configuradas corretamente em ambiente.

### Biblioteca e Assets

Area para armazenar outputs, roteiros, imagens, videos e creative packs.

Estado atual:

- ha endpoints de biblioteca;
- alguns outputs podem ser salvos automaticamente;
- ainda precisa consolidar UX e contratos de dados para todos os tipos de asset.

### Referencias e Pesquisa

Modulo para analisar criadores, videos, posts e tendencias.

Estado atual:

- existem endpoints e telas para referencias;
- ha dependencias externas e browser/headless em alguns fluxos;
- na VPS, esse e um dos pontos com maior chance de falha por ambiente, credenciais, bloqueios de rede ou falta de Playwright/Chromium.

### News Radar

Modulo para monitorar assuntos e gerar digests de ideias.

Estado atual:

- endpoints e painel existem;
- depende de chaves externas como YouTube, Reddit, Twitter API, Perplexity ou outras configuracoes.

## Arquitetura Tecnica

### Frontend

- React 18;
- Vite;
- TypeScript;
- Tailwind;
- Supabase Auth;
- componentes proprios para chat, editor, biblioteca, analytics, referencias e configuracoes.

### Backend

- FastAPI;
- ProjectOrchestrator;
- Agno agents/tools;
- Supabase/Postgres;
- Redis;
- Celery workers;
- FFmpeg;
- storage local, S3, R2 ou MinIO;
- Remotion service para renders avancados;
- chatgpt-bridge opcional para geracao de imagem.

### Servicos Auxiliares

- Redis: logs, fila e eventos;
- video worker/service: processamento de video;
- carousel service: renderizacao de carrossel;
- remotion-service: renderizacao com Remotion;
- chatgpt-bridge: geracao de imagem via auth Codex/ChatGPT;
- Supabase: auth, banco e dados multiusuario.

## Estado Atual do Projeto

O projeto ja tem uma base funcional, mas ainda nao esta em estado de produto final estavel. Ele esta em fase de integracao e estabilizacao.

Ja existe:

- frontend principal com abas;
- login/onboarding via Supabase;
- chat streaming;
- logs de agentes;
- editor de video;
- upload e uso de URL no editor;
- workers de video;
- presets de edicao;
- suporte a Remotion;
- biblioteca;
- referencias;
- news radar;
- configuracoes de marca;
- deploy via Docker/EasyPanel;
- documentacao tecnica inicial.

Ainda ha sinais claros de sistema em construcao:

- muitos servicos dependem de variaveis de ambiente sensiveis;
- alguns fluxos funcionam localmente mas falham na VPS por dependencia externa;
- ha sidecars que precisam estar vivos e roteados corretamente;
- o workspace tem alteracoes acumuladas e muitos arquivos gerados em `node_modules`;
- o typecheck do frontend ainda acusa imports/variaveis antigas nao usados;
- a experiencia do usuario ainda mistura partes de produto final com partes diagnosticas/admin.

## O Que Falta Para Finalizar

### 1. Fechar o Deploy da VPS

Prioridade alta.

- Garantir que a VPS esta rodando o ultimo commit do `main`.
- Garantir rebuild real do frontend depois de cada push.
- Confirmar que o bundle antigo nao fica cacheado no navegador/CDN/proxy.
- Validar variaveis `VITE_API_URL`, `PUBLIC_API_URL`, `ALLOWED_ORIGINS`.
- Confirmar que backend, frontend, worker, Redis, Remotion e servicos auxiliares estao no mesmo ambiente esperado.
- Criar um checklist de smoke test pos-deploy.

### 2. Estabilizar o Chat Principal

- Garantir que o chat sempre renderiza resposta natural, nao metadata.
- Manter logs e orquestracao apenas na aba de desenvolvimento/logs.
- Padronizar contrato de resposta entre `/chat`, `/chat/stream` e Hermes.
- Adicionar fallback quando SSE falhar.
- Reduzir respostas em formato de lista quando o usuario espera conversa natural.

### 3. Finalizar o Editor de Video

- Validar upload grande em producao.
- Validar URL direta de video em S3/R2/CDN.
- Mostrar erros claros quando a URL e uma pagina, nao um arquivo de video.
- Expor corte por tempo na UI, nao apenas via texto.
- Mostrar antes/depois e duracao final.
- Melhorar diagnostico de `remove_silence`, informando quando nenhum silencio foi detectado.
- Garantir que Celery worker esta rodando na VPS.
- Confirmar FFmpeg instalado e acessivel no container/host.
- Separar presets FFmpeg de presets Remotion para evitar expectativa errada.

### 4. Corrigir Pipeline de Referencias

- Instalar e validar Playwright/Chromium no ambiente de producao, se necessario.
- Definir quais fontes sao suportadas oficialmente.
- Tratar bloqueios de Instagram/TikTok/YouTube/Drive.
- Criar mensagens de erro especificas por tipo de falha.
- Separar "baixar video", "extrair metadados" e "analisar estilo" como etapas visiveis.

### 5. Consolidar Autenticacao e Multiusuario

- Confirmar todos os endpoints protegidos por JWT ou API key correta.
- Garantir isolamento por usuario, organizacao e marca.
- Revisar permissao de logs, biblioteca e assets.
- Padronizar headers `X-Org-Id` e `X-Brand-Id`.

### 6. Limpar Repositorio e Build

- Remover `node_modules` do controle de versao, se estiver rastreado.
- Revisar `.gitignore`.
- Resolver warnings de typecheck.
- Separar subprojetos/submodules ou transformar em pacotes claros.
- Criar comandos padronizados de dev, build e deploy.

### 7. Testes e Smoke Checks

Criar testes minimos para:

- chat trivial;
- chat streaming;
- editor com URL direta;
- parser de corte por tempo;
- upload de video;
- status de job;
- render Remotion;
- biblioteca;
- auth.

Smoke checks recomendados:

```text
GET /api/v1/health
POST /api/v1/chat/stream
POST /api/v1/videos/chat
GET /api/v1/videos/status/{job_id}
GET /api/v1/logs
GET /api/v1/settings/llm-status
```

### 8. UX de Produto

- Transformar abas tecnicas em areas mais claras para usuario final.
- Separar modo usuario de modo admin/desenvolvimento.
- Melhorar empty states, loading states e erros.
- Criar onboarding que realmente configura marca, tom de voz e objetivos.
- Mostrar outputs em biblioteca automaticamente.
- Criar fluxo completo "ideia -> roteiro -> video/carrossel -> biblioteca".

## Checklist de Finalizacao

### Obrigatorio para MVP Estavel

- [ ] Deploy reproduzivel na VPS.
- [ ] Frontend sempre atualizado apos push.
- [ ] Chat responde de forma natural.
- [ ] Editor aceita upload e URL direta.
- [ ] Corte por tempo funcionando.
- [ ] Corte de silencio com diagnostico claro.
- [ ] Worker Celery ativo em producao.
- [ ] Redis ativo em producao.
- [ ] FFmpeg ativo em producao.
- [ ] Supabase configurado e protegido.
- [ ] Storage configurado e acessivel pelo navegador.
- [ ] Logs separados da conversa principal.
- [ ] Typecheck limpo ou warnings justificados.
- [ ] `.gitignore` e repo limpos.

### Desejavel para Produto Comercial

- [ ] Painel de status dos servicos.
- [ ] Monitoramento de jobs.
- [ ] Retry visual de jobs falhos.
- [ ] Historico de conversas por projeto.
- [ ] Biblioteca organizada por marca/projeto.
- [ ] Templates de video/carrossel versionados.
- [ ] Sistema de creditos ou limite de uso.
- [ ] Testes automatizados no CI.
- [ ] Guia de operacao para VPS.
- [ ] Guia de troubleshooting para suporte.

## Riscos Atuais

- Dependencia forte de ambiente: VPS, Docker, Redis, workers, FFmpeg, Remotion e storage precisam estar alinhados.
- Muitas integracoes externas podem falhar por chave, quota, bloqueio ou mudanca de API.
- O sistema tem varios fluxos paralelos que ainda precisam de padronizacao.
- O repositorio contem sinais de sujeira operacional, principalmente arquivos gerados e alteracoes nao relacionadas.
- Sem smoke tests automatizados, regressao em deploy e provavel.

## Proximo Plano Recomendado

1. Limpar e proteger o repositorio.
2. Criar smoke tests de deploy.
3. Estabilizar chat e editor de video como nucleo do MVP.
4. Criar painel interno de status dos servicos.
5. Resolver referencias/perfil como modulo separado, com diagnostico claro.
6. Documentar processo de deploy na VPS passo a passo.
7. So depois disso, expandir para Remotion avancado, News Radar e automacoes complexas.

## Definicao de Pronto

O projeto pode ser considerado finalizado como MVP quando um usuario conseguir:

1. entrar na aplicacao;
2. configurar sua marca;
3. conversar naturalmente com o chat;
4. gerar pelo menos um roteiro/copy;
5. enviar ou colar URL de um video;
6. pedir um corte/legenda/preset;
7. acompanhar o job;
8. baixar o resultado;
9. encontrar o output na biblioteca;
10. fazer tudo isso na VPS sem precisar acessar logs tecnicos.

