# MVP TODO - 2026-07-09

Objetivo de hoje: deixar um MVP funcional, com o menor numero de funcionalidades possivel, mas com fluxo completo funcionando sem depender de logs tecnicos.

Regra de prioridade: primeiro estabilizar o caminho principal. Funcionalidade que nao participa do fluxo essencial fica congelada ate o MVP passar nos smoke tests.

## Fluxo MVP Principal

- [ ] Usuario entra no app e chega na tela principal sem erro.
- [ ] Usuario configura ou seleciona uma marca/workspace.
- [ ] Usuario conversa no chat de projeto e recebe resposta natural.
- [ ] Usuario gera pelo menos um roteiro/copy simples.
- [ ] Usuario envia ou cola uma URL de video.
- [ ] Usuario pede uma edicao simples de video.
- [ ] Usuario acompanha o status do job.
- [ ] Usuario baixa ou acessa o resultado final.
- [ ] Output aparece ou pode ser salvo na biblioteca.

## Funcionalidades Que Entram No MVP

### 1. Autenticacao, Organizacao e Marca

- [ ] Login abre corretamente.
- [ ] Sessao autenticada persiste ao recarregar.
- [ ] Onboarding nao bloqueia usuario indevidamente.
- [ ] Criar/selecionar organizacao funciona.
- [ ] Criar/selecionar marca funciona.
- [ ] Headers `X-Org-Id` e `X-Brand-Id` chegam nos endpoints principais.
- [ ] Erros de auth aparecem de forma compreensivel na UI.

### 2. Chat Principal / Projeto

- [ ] `/api/v1/chat/stream` responde com SSE em ambiente local.
- [ ] Chat mostra texto natural, nao metadata tecnica.
- [ ] Logs de agentes ficam fora da conversa principal.
- [ ] Fallback funciona quando streaming falha.
- [ ] Intencao `script` gera roteiro/copy utilizavel.
- [ ] Intencao `strategy` gera plano simples.
- [ ] Intencao `memory` salva preferencia basica da marca/usuario.
- [ ] Resposta de erro informa proximo passo claro.

### 3. Editor de Video

- [x] Configurar LLM principal e modelos auxiliares para iniciar pelo editor de video.
- [ ] Upload de video pequeno funciona.
- [ ] URL direta de video funciona quando aponta para arquivo real.
- [ ] UI diferencia URL de arquivo de URL de pagina.
- [ ] Corte por tempo funciona no backend.
- [ ] Corte por tempo esta acessivel na UI.
- [ ] Status de job atualiza ate finalizar ou falhar.
- [ ] Resultado final mostra URL/download.
- [ ] Erro de job aparece com causa provavel.
- [ ] `remove_silence` informa quando nao encontra silencio.
- [ ] FFmpeg esta instalado e acessivel.
- [ ] Worker Celery esta ativo.
- [ ] Redis esta ativo.

### 4. Biblioteca

- [ ] `GET /api/v1/library` lista assets do usuario/marca.
- [ ] Output de roteiro/copy pode ser salvo.
- [ ] Output de video pode ser salvo ou aparece automaticamente.
- [ ] Links de asset abrem no navegador.
- [ ] Download/copy link funciona.
- [ ] Biblioteca nao mistura dados de outra organizacao/marca.

### 5. Configuracoes e Diagnostico

- [ ] Tela de Marca/Settings abre sem quebrar.
- [ ] `GET /api/v1/health` retorna ok.
- [ ] `GET /api/v1/health/llm` mostra provider disponivel.
- [ ] `GET /api/v1/health/full` diagnostica Redis, Supabase, Vault e sidecars.
- [ ] Tela de desenvolvimento/logs fica disponivel para debug.
- [ ] Usuario final nao precisa abrir logs para usar o MVP.

### 6. Deploy / Ambiente

- [ ] `.env.example` cobre variaveis obrigatorias do MVP.
- [ ] `VITE_API_URL` aponta para backend correto.
- [ ] `ALLOWED_ORIGINS` permite frontend de producao.
- [ ] Supabase esta configurado.
- [ ] Storage esta configurado e publicamente acessivel quando necessario.
- [ ] Frontend builda sem erro.
- [ ] Backend sobe sem erro.
- [ ] Worker sobe sem erro.
- [ ] Smoke test pos-deploy documentado e executado.

## Funcionalidades Congeladas Ate O MVP Estar Estavel

Estas existem no produto, mas nao devem bloquear o MVP de hoje:

- [ ] Voz / `VoiceOrb`.
- [ ] Criacao avancada por templates e squads.
- [ ] News Radar / pesquisa de tendencias.
- [ ] Referencias de criadores.
- [ ] Mapa/Graph.
- [ ] Analytics.
- [ ] Hermes como caminho principal.
- [ ] Remotion avancado/PRO.
- [ ] Automacoes externas complexas.
- [ ] TTS/ElevenLabs.

## Smoke Tests Minimos

- [ ] `GET /api/v1/health`
- [ ] `GET /api/v1/health/llm`
- [ ] `POST /api/v1/chat/stream`
- [ ] `POST /api/v1/videos/upload` ou fluxo equivalente no editor.
- [ ] `POST /api/v1/videos/chat`
- [ ] `GET /api/v1/videos/status/{job_id}`
- [ ] `GET /api/v1/library`
- [ ] `GET /api/v1/logs`

## Criterio De Pronto Do MVP

- [ ] Fluxo principal completo foi testado localmente.
- [ ] Fluxo principal completo foi testado na VPS/producao.
- [ ] Nenhuma funcionalidade congelada aparece como dependencia obrigatoria.
- [ ] Erros conhecidos estao documentados com solucao ou contorno.
- [ ] Usuario consegue criar um output real sem ajuda tecnica.

## Proxima Acao

- [ ] Rodar health checks locais.
- [ ] Rodar build/typecheck do frontend.
- [ ] Testar chat principal.
- [ ] Testar editor de video com arquivo pequeno.
- [ ] Corrigir o primeiro bloqueio encontrado antes de abrir outra frente.
