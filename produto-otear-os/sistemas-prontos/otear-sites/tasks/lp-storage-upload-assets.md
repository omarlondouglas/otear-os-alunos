---
task: uploadAssets()
responsavel: "Silo"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: storageConfig
    tipo: object
    obrigatorio: true
    descricao: "Config do storage com bucket e prefixo (source: initStorage())"
  - nome: files
    tipo: array
    obrigatorio: true
    descricao: "Lista de arquivos para upload (imagens geradas, vÃ­deos do cliente, og:image)"

Saida:
  - nome: assetsManifest
    tipo: file
    obrigatorio: true
    descricao: "assets-manifest.json com URLs pÃºblicas de cada asset (destination: lp-frontend-dev)"

Checklist:
  pre-conditions:
    - "[ ] Storage inicializado para o cliente"
    - "[ ] Arquivos disponÃ­veis localmente"
  post-conditions:
    - "[ ] Imagens otimizadas (WebP, tamanho adequado)"
    - "[ ] Upload concluÃ­do para todos os arquivos"
    - "[ ] Cache headers configurados (max-age=31536000)"
    - "[ ] Content-Type correto em cada objeto"
    - "[ ] assets-manifest.json gerado com URLs"
    - "[ ] URLs acessÃ­veis publicamente"

Performance:
  duration_expected: "2-5 minutes (depende do tamanho dos arquivos)"
  cacheable: false
  parallelizable: true
---

# uploadAssets()

## DescriÃ§Ã£o

Otimiza e faz upload de todos os assets (imagens e vÃ­deos) para o Cloudflare R2. Gera um manifesto JSON com as URLs pÃºblicas de cada asset para o frontend usar.

## Passos

1. **Listar arquivos** â€” Identificar imagens e vÃ­deos para upload.
2. **Otimizar imagens** â€” Converter para WebP, redimensionar se necessÃ¡rio.
3. **Upload** â€” S3 putObject com ContentType e CacheControl corretos.
4. **Verificar acesso** â€” Confirmar que cada URL Ã© acessÃ­vel publicamente.
5. **Gerar manifesto** â€” `assets-manifest.json` com mapa completo de URLs.
6. **Salvar manifesto** â€” No workspace para o frontend e versioner consumirem.

## Upload com OtimizaÃ§Ã£o

```python
import io
from PIL import Image

def optimize_and_upload(local_path: str, r2_key: str, max_width: int = 1920):
    img = Image.open(local_path)

    # Resize se maior que max_width
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    # Converter para WebP
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=85)
    buffer.seek(0)

    s3.upload_fileobj(
        buffer,
        "lp-assets",
        r2_key,
        ExtraArgs={
            "ContentType": "image/webp",
            "CacheControl": "public, max-age=31536000, immutable",
        },
    )
```

## Upload de VÃ­deo

```python
def upload_video(local_path: str, r2_key: str):
    content_type = "video/mp4" if local_path.endswith(".mp4") else "video/webm"

    s3.upload_file(
        local_path,
        "lp-assets",
        r2_key,
        ExtraArgs={
            "ContentType": content_type,
            "CacheControl": "public, max-age=31536000",
        },
    )
```

