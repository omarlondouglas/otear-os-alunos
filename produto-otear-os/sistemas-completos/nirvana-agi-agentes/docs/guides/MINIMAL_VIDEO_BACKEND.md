# Backend Minimo de Busca e Download de Videos

Este recorte sobe uma API separada do projeto principal para:

- listar videos de um perfil TikTok
- listar videos de um perfil Instagram
- baixar um video a partir da URL do post

Sem banco, sem Redis, sem Celery, sem Docker obrigatorio.

## Arquivos

- `mini_video_backend.py`
- `requirements-minimal-video.txt`

## Instalar

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-minimal-video.txt
```

Se quiser evitar erros no fallback do TikTok/Instagram, garanta que `yt-dlp` esteja no PATH:

```powershell
yt-dlp --version
```

## Rodar

```powershell
uvicorn mini_video_backend:app --reload --port 8010
```

## Endpoints

### Health

```text
GET /health
```

### Buscar videos de um perfil

```text
GET /search/tiktok/{handle}?count=10
GET /search/instagram/{handle}?count=10
```

Exemplos:

```text
GET /search/tiktok/mkbhd?count=5
GET /search/instagram/nasa?count=5
```

### Baixar video por URL

```text
POST /download
Content-Type: application/json
```

Body:

```json
{
  "url": "https://www.tiktok.com/@usuario/video/1234567890"
}
```

Ou informando plataforma:

```json
{
  "url": "https://www.instagram.com/reel/ABC123/",
  "platform": "instagram",
  "filename": "meu_video.mp4"
}
```

Resposta:

```json
{
  "platform": "tiktok",
  "source_url": "...",
  "filename": "arquivo.mp4",
  "local_path": "D:\\\\...\\\\var\\\\downloads\\\\mini_video_downloads\\\\arquivo.mp4",
  "download_url": "/downloads/arquivo.mp4",
  "size_bytes": 1234567
}
```

## Observacoes

- TikTok usa o downloader dedicado do projeto.
- Instagram usa `yt-dlp`.
- Arquivos baixados ficam em `./var/downloads/mini_video_downloads` por padrao.
- A API serve esses arquivos em `/downloads/{arquivo}`.
- Perfis privados do Instagram nao funcionam sem sessao autenticada.
