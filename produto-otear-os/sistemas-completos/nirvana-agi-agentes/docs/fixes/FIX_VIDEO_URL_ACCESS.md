# Fix: Problema de Acesso à URL do Vídeo

## Problema Real Identificado

O job **não está sendo criado** porque a API de edição de vídeo não consegue fazer download do arquivo de entrada.

### Erro Reportado
```
Erro de acesso à URL: https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4
```

**Causa:** A API de edição tenta baixar o vídeo da URL fornecida, mas:
1. A URL pode não estar acessível publicamente
2. O MinIO pode exigir autenticação
3. O bucket pode não ter permissões públicas
4. A URL pode estar incorreta

## Diagnóstico

### 1. Testar Acesso à URL

```bash
# Testar se a URL está acessível
curl -I "https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4"
```

**Possíveis respostas:**

#### ✅ Sucesso (200 OK)
```
HTTP/2 200
content-type: video/mp4
content-length: 12345678
```
→ URL está acessível, problema pode ser na API de edição

#### ❌ Não Autorizado (403 Forbidden)
```
HTTP/2 403
```
→ Bucket não tem permissões públicas ou precisa de autenticação

#### ❌ Não Encontrado (404 Not Found)
```
HTTP/2 404
```
→ Arquivo não existe ou caminho está incorreto

#### ❌ Erro de Conexão
```
curl: (6) Could not resolve host
```
→ URL do MinIO está incorreta ou servidor está offline

### 2. Verificar Configuração do MinIO

O MinIO está configurado em `.env`:
```env
S3_ENDPOINT_URL=https://teste-minio.qc7qit.easypanel.host/
S3_ACCESS_KEY=dVQdIdPJcQnmJsvsY4Zl
S3_SECRET_KEY=1ik5d8mYIFxlN22eeIkWS9oVVzo21FeCJXjZY8GO
S3_BUCKET_NAME=agi
```

**Problema:** A API de edição de vídeo pode não ter acesso a essas credenciais!

## Soluções

### Solução 1: Tornar o Bucket Público (Recomendado para Testes)

#### No MinIO Console:

1. Acesse: `https://teste-minio.qc7qit.easypanel.host`
2. Login com as credenciais
3. Vá para o bucket `agi` (ou `stories`)
4. Clique em "Manage" → "Access Policy"
5. Selecione "Public" ou adicione policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::agi/*"]
    }
  ]
}
```

#### Via MinIO Client (mc):

```bash
# Configurar alias
mc alias set myminio https://teste-minio.qc7qit.easypanel.host dVQdIdPJcQnmJsvsY4Zl 1ik5d8mYIFxlN22eeIkWS9oVVzo21FeCJXjZY8GO

# Tornar bucket público
mc anonymous set download myminio/agi

# Verificar
mc anonymous get myminio/agi
```

### Solução 2: Gerar URL Pré-Assinada (Presigned URL)

URLs pré-assinadas permitem acesso temporário sem tornar o bucket público.

#### Criar ferramenta para gerar presigned URLs:

```python
# app/agents/agno_tools.py

import boto3
from botocore.client import Config
import os

@with_logging("Generate Presigned URL")
def generate_presigned_url_tool(object_key: str, expiration: int = 3600):
    """
    Gera uma URL pré-assinada para acesso temporário a um arquivo no MinIO/S3.
    
    Args:
        object_key: Caminho do arquivo no bucket (ex: 'stories/teste_jump.mp4')
        expiration: Tempo de validade em segundos (padrão: 1 hora)
    
    Returns:
        URL pré-assinada válida por {expiration} segundos
    """
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
            config=Config(signature_version='s3v4'),
            region_name=os.getenv('S3_REGION', 'us-east-1')
        )
        
        bucket_name = os.getenv('S3_BUCKET_NAME', 'agi')
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
        
        logger.info(f"[PRESIGNED URL] Gerada para {object_key}, válida por {expiration}s")
        return {
            "url": presigned_url,
            "expires_in": expiration,
            "object_key": object_key
        }
        
    except Exception as e:
        logger.error(f"[PRESIGNED URL] Erro: {e}")
        return {"error": str(e)}
```

#### Adicionar ao VideoDirectorAgent:

```python
# app/agents/agno_agents.py

video_director = Agent(
    name="VideoDirectorAgent",
    tools=[
        edit_video_tool, 
        transcribe_video_tool, 
        check_video_status_tool,
        generate_presigned_url_tool  # ✅ NOVO
    ],
    instructions=[
        # ... instruções existentes ...
        "",
        "### ACESSO A VÍDEOS NO MINIO ###",
        "Se o usuário fornecer um caminho do MinIO (ex: 'stories/teste_jump.mp4'):",
        "1. PRIMEIRO chame generate_presigned_url_tool(object_key='stories/teste_jump.mp4')",
        "2. Use a URL pré-assinada retornada para chamar edit_video_tool",
        "3. URLs pré-assinadas são válidas por 1 hora",
        "",
        "EXEMPLO:",
        "Usuário: 'Edita o vídeo stories/teste_jump.mp4'",
        "Você: [CHAMA generate_presigned_url_tool('stories/teste_jump.mp4')]",
        "Ferramenta retorna: {'url': 'https://...?X-Amz-Signature=...'}",
        "Você: [CHAMA edit_video_tool(video_url='https://...?X-Amz-Signature=...')]",
    ]
)
```

### Solução 3: Usar URLs Públicas Alternativas

Se o MinIO não puder ser público, use serviços de hospedagem de vídeo:

#### Google Drive
```
1. Faça upload do vídeo
2. Clique com botão direito → "Obter link"
3. Mude para "Qualquer pessoa com o link"
4. Copie o ID do arquivo (ex: 1a2b3c4d5e6f)
5. Use: https://drive.google.com/uc?export=download&id=1a2b3c4d5e6f
```

#### Dropbox
```
1. Faça upload do vídeo
2. Clique em "Compartilhar"
3. Copie o link (ex: https://www.dropbox.com/s/abc123/video.mp4?dl=0)
4. Mude ?dl=0 para ?dl=1
5. Use: https://www.dropbox.com/s/abc123/video.mp4?dl=1
```

#### WeTransfer
```
1. Faça upload do vídeo
2. Copie o link de download direto
3. Use o link fornecido
```

### Solução 4: Configurar API de Edição com Credenciais MinIO

Se a API de edição estiver no mesmo ambiente, configure as credenciais:

#### No docker-compose.yml da API de edição:

```yaml
services:
  video-editor:
    environment:
      - S3_ENDPOINT_URL=https://teste-minio.qc7qit.easypanel.host
      - S3_ACCESS_KEY=dVQdIdPJcQnmJsvsY4Zl
      - S3_SECRET_KEY=1ik5d8mYIFxlN22eeIkWS9oVVzo21FeCJXjZY8GO
      - S3_BUCKET_NAME=agi
```

#### No código da API de edição:

```python
# Detectar se é URL do MinIO e usar credenciais
if "teste-minio.qc7qit.easypanel.host" in video_url:
    # Usar boto3 com credenciais para baixar
    s3_client = boto3.client('s3', ...)
    s3_client.download_file(bucket, key, local_path)
else:
    # Download normal via HTTP
    response = requests.get(video_url)
```

## Teste Rápido

### 1. Verificar se URL está acessível

```bash
curl -I "https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4"
```

### 2. Se retornar 403, testar com credenciais

```bash
# Instalar awscli
pip install awscli

# Configurar
aws configure set aws_access_key_id dVQdIdPJcQnmJsvsY4Zl
aws configure set aws_secret_access_key 1ik5d8mYIFxlN22eeIkWS9oVVzo21FeCJXjZY8GO

# Testar acesso
aws s3 ls s3://agi/stories/ --endpoint-url https://teste-minio.qc7qit.easypanel.host
```

### 3. Gerar URL pré-assinada manualmente

```python
import boto3
from botocore.client import Config

s3_client = boto3.client(
    's3',
    endpoint_url='https://teste-minio.qc7qit.easypanel.host',
    aws_access_key_id='dVQdIdPJcQnmJsvsY4Zl',
    aws_secret_access_key='1ik5d8mYIFxlN22eeIkWS9oVVzo21FeCJXjZY8GO',
    config=Config(signature_version='s3v4')
)

url = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'agi', 'Key': 'stories/teste_jump.mp4'},
    ExpiresIn=3600
)

print(url)
```

### 4. Testar com a URL gerada

```bash
curl -I "URL_PRE_ASSINADA_AQUI"
```

## Workaround Imediato

Enquanto não resolve o MinIO, use um vídeo de teste público:

```
https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
```

Teste com o agente:
```
Edita esse vídeo: https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
```

Se funcionar, o problema é definitivamente o acesso ao MinIO.

## Checklist de Diagnóstico

- [ ] Testei acesso à URL com curl
- [ ] Verifiquei se bucket tem permissões públicas
- [ ] Testei com vídeo público (BigBuckBunny)
- [ ] Configurei credenciais na API de edição
- [ ] Implementei geração de presigned URLs
- [ ] Testei presigned URL manualmente

## Recomendação

**Para produção:**
1. Mantenha buckets privados
2. Use presigned URLs (Solução 2)
3. Configure TTL adequado (1-24 horas)

**Para desenvolvimento:**
1. Torne bucket público temporariamente (Solução 1)
2. Ou use vídeos de teste públicos

## Próximos Passos

1. **Teste de acesso:**
   ```bash
   curl -I "https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4"
   ```

2. **Se 403, implemente presigned URLs:**
   - Adicione `generate_presigned_url_tool` em `agno_tools.py`
   - Adicione ao VideoDirectorAgent
   - Instrua agente a usar presigned URLs

3. **Teste com vídeo público:**
   ```
   Edita esse vídeo: https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
   ```

---

**Resumo:** O problema não é no polling ou nas URLs de saída, mas no **acesso ao vídeo de entrada**. A API não consegue baixar o arquivo do MinIO.
