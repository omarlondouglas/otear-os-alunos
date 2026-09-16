# Comandos por servico

Use este guia para subir, parar, debugar e testar cada ramificacao da aplicacao.

## Atalho principal

O script abaixo roda a partir da raiz do repo:

```powershell
.\scripts\dev\service.ps1 status
```

Para os servicos Docker, o Docker Desktop/CLI precisa estar instalado e disponivel no `PATH`.

Formato:

```powershell
.\scripts\dev\service.ps1 <acao> <servico>
```

Acoes:

```text
up       sobe servico
down     para servico
restart  reinicia servico
logs     acompanha logs
status   lista containers
health   testa healthcheck
build    rebuilda imagem ou frontend
shell    abre shell dentro do container
```

Servicos:

```text
all
video-backend
video-editor
social-media
gateway
redis
carousel
remotion
chatgpt-bridge
frontend
```

## Social media e calendario editorial

Use este modo quando voce quer planejar calendario editorial, rodar News Radar, criar entradas em `/api/v1/calendar`, analisar referencias sociais e estruturar conteudo nos 4 formatos:

```text
noticias
vlog
tutorial
review sincero
```

Ele sobe:

```text
redis
gateway
```

Dentro do `gateway`, o `supervisord` inicia:

```text
api_gateway.py                         porta 8000
uvicorn app.main:app --port 8001       API principal com calendar/news/social
celery worker                          social_tasks e news_digest
celery beat                            digest diario
```

Ele nao sobe:

```text
frontend
carousel
remotion
chatgpt-bridge
```

Comandos:

```powershell
.\scripts\dev\service.ps1 up social-media
.\scripts\dev\service.ps1 logs social-media
.\scripts\dev\service.ps1 health social-media
.\scripts\dev\service.ps1 restart social-media
.\scripts\dev\service.ps1 down social-media
```

Knowledge do fluxo:

```text
app/knowledge/social-media-calendar/CODEX.md
```

Endpoints principais:

```text
Calendario:
GET  http://localhost:8001/api/v1/calendar
POST http://localhost:8001/api/v1/calendar
PUT  http://localhost:8001/api/v1/calendar/{entry_id}

News Radar:
GET  http://localhost:8001/api/v1/news/feed
POST http://localhost:8001/api/v1/news/run
GET  http://localhost:8001/api/v1/news/list

Referencias sociais:
GET  http://localhost:8001/api/v1/references/creators
POST http://localhost:8001/api/v1/references/creators
POST http://localhost:8001/api/v1/references/videos
```

## Editor de video existente com Remotion

Use este modo quando voce quer apenas o backend/editor de video existente para fazer videos com Remotion, sem frontend e sem carousel.

Ele sobe:

```text
redis
remotion
gateway
```

Dentro do `gateway`, o `supervisord` inicia o editor de video antigo:

```text
api_gateway.py                         porta 8000
uvicorn app.main:app --port 8001       editor/API de video
celery worker                          processamento dos jobs
celery beat                            tarefas periodicas
```

Ele nao sobe:

```text
frontend
carousel
chatgpt-bridge
```

Comandos:

```powershell
.\scripts\dev\service.ps1 up video-editor
.\scripts\dev\service.ps1 logs video-editor
.\scripts\dev\service.ps1 health video-editor
.\scripts\dev\service.ps1 restart video-editor
.\scripts\dev\service.ps1 down video-editor
```

Alias equivalente:

```powershell
.\scripts\dev\service.ps1 up video-backend
.\scripts\dev\service.ps1 logs video-backend
.\scripts\dev\service.ps1 health video-backend
.\scripts\dev\service.ps1 restart video-backend
.\scripts\dev\service.ps1 down video-backend
```

O comando usa `--no-deps` ao subir o `gateway`, porque o `docker-compose.yml` principal declara dependencia no `carousel`. Para fluxo de video com Remotion, o `carousel` nao e necessario.

URLs principais:

```text
API/Gateway: http://localhost:8000
Editor de video direto: http://localhost:8001
Remotion: http://localhost:8003
Redis: localhost:6379
```

Endpoints principais do editor:

```text
Direto no editor:
POST http://localhost:8001/api/v1/videos/edit
GET  http://localhost:8001/api/v1/videos/status/{job_id}
POST http://localhost:8001/api/v1/videos/render-template
POST http://localhost:8001/api/v1/videos/render-with-scenes

Via gateway/proxy:
POST http://localhost:8000/api/video-editor/upload
POST http://localhost:8000/api/video-editor/chat
GET  http://localhost:8000/api/video-editor/status/{job_id}
```

## Tudo via Docker

```powershell
.\scripts\dev\service.ps1 up all
.\scripts\dev\service.ps1 status
.\scripts\dev\service.ps1 health all
.\scripts\dev\service.ps1 logs all
.\scripts\dev\service.ps1 down all
```

Observacao: `frontend` nao esta no `docker-compose.yml` principal. Rode separado com Vite.

## Gateway/API principal

Servico: `gateway`

Porta externa: `8000`

Dentro do container, o supervisor tambem inicia:

- `api_gateway.py`
- `uvicorn app.main:app --port 8001`
- `celery worker`
- `celery beat`

Comandos:

```powershell
.\scripts\dev\service.ps1 up gateway
.\scripts\dev\service.ps1 logs gateway
.\scripts\dev\service.ps1 restart gateway
.\scripts\dev\service.ps1 shell gateway
.\scripts\dev\service.ps1 health gateway
```

URLs:

```text
API: http://localhost:8000
Health: http://localhost:8000/health
Swagger: http://localhost:8000/docs
```

## Redis

Servico: `redis`

Porta externa: `6379`

Comandos:

```powershell
.\scripts\dev\service.ps1 up redis
.\scripts\dev\service.ps1 logs redis
.\scripts\dev\service.ps1 health redis
```

Health manual:

```powershell
docker compose exec -T redis redis-cli ping
```

## Carousel

Servico: `carousel`

Pasta: `carrocel/`

Porta externa: `8002`

Comandos:

```powershell
.\scripts\dev\service.ps1 up carousel
.\scripts\dev\service.ps1 logs carousel
.\scripts\dev\service.ps1 restart carousel
.\scripts\dev\service.ps1 health carousel
```

URL:

```text
Health: http://localhost:8002/health
```

## Remotion

Servico: `remotion`

Pasta: `remotion-service/`

Porta externa: `8003`

Comandos:

```powershell
.\scripts\dev\service.ps1 up remotion
.\scripts\dev\service.ps1 logs remotion
.\scripts\dev\service.ps1 restart remotion
.\scripts\dev\service.ps1 health remotion
```

Local sem Docker:

```powershell
cd remotion-service
npm install
npm run dev
```

URL:

```text
Health: http://localhost:8003/health
```

## ChatGPT Bridge

Servico: `chatgpt-bridge`

Pasta: `chatgpt-bridge-service/`

Porta externa: `10531`

Comandos:

```powershell
.\scripts\dev\service.ps1 up chatgpt-bridge
.\scripts\dev\service.ps1 logs chatgpt-bridge
.\scripts\dev\service.ps1 restart chatgpt-bridge
.\scripts\dev\service.ps1 health chatgpt-bridge
```

URL:

```text
Health: http://localhost:10531/health
OpenAI-compatible base URL: http://localhost:10531/v1
```

## Frontend React

Servico local: `frontend`

Pasta: `frontend-react/`

Porta Vite padrao: `5173`

Comandos:

```powershell
.\scripts\dev\service.ps1 up frontend
.\scripts\dev\service.ps1 build frontend
```

Manual:

```powershell
cd frontend-react
npm install
npm run dev
```

URL:

```text
App: http://localhost:5173
```

## Comandos Docker diretos

Quando quiser usar Docker Compose sem o wrapper:

```powershell
docker compose up -d
docker compose ps
docker compose logs -f --tail 200 gateway
docker compose restart gateway
docker compose down
docker compose build gateway
```

## Ordem recomendada para desenvolvimento

1. Subir infraestrutura e backend:

```powershell
.\scripts\dev\service.ps1 up all
```

2. Subir frontend em outro terminal:

```powershell
.\scripts\dev\service.ps1 up frontend
```

3. Checar saude:

```powershell
.\scripts\dev\service.ps1 health all
```

4. Ver logs do backend:

```powershell
.\scripts\dev\service.ps1 logs gateway
```
