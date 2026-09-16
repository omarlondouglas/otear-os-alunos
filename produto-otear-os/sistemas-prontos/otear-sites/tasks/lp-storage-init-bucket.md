---
task: initStorage()
responsavel: "Silo"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: clientName
    tipo: string
    obrigatorio: true
    descricao: "Nome do cliente (usado como prefixo no bucket)"

Saida:
  - nome: storageConfig
    tipo: object
    obrigatorio: true
    descricao: "Config do storage: bucket, prefixo, base URL (destination: uploadAssets())"

Checklist:
  pre-conditions:
    - "[ ] Cloudflare R2 configurado com API keys"
    - "[ ] Bucket 'lp-assets' existe (criar se primeiro uso)"
  post-conditions:
    - "[ ] Prefixo {client-slug}/ criado no bucket"
    - "[ ] Sub-prefixos images/ e videos/ criados"
    - "[ ] Public access ativo no bucket"
    - "[ ] Base URL disponÃ­vel"

Performance:
  duration_expected: "30 seconds"
  cacheable: false
  parallelizable: true
---

# initStorage()

## DescriÃ§Ã£o

Inicializa o storage no Cloudflare R2 para um novo cliente. Cria o prefixo (pasta virtual) dentro do bucket compartilhado `lp-assets` e retorna a config com base URL.

## Passos

1. **Verificar bucket** â€” Confirmar que `lp-assets` existe, criar se primeiro uso.
2. **Criar prefixos** â€” `{client-slug}/images/` e `{client-slug}/videos/`.
3. **Verificar public access** â€” Bucket deve ter acesso pÃºblico ativo.
4. **Gerar base URL** â€” `https://assets.seudominio.com/{client-slug}` ou `https://lp-assets.{id}.r2.dev/{client-slug}`.
5. **Retornar config** â€” bucket, prefixo, base URL, credentials reference.

## CriaÃ§Ã£o do Bucket (primeira vez)

```python
s3.create_bucket(Bucket="lp-assets")
# Ativar public access via Cloudflare Dashboard ou API
```

## CORS (primeira vez)

```python
s3.put_bucket_cors(
    Bucket="lp-assets",
    CORSConfiguration={
        "CORSRules": [
            {
                "AllowedHeaders": ["*"],
                "AllowedMethods": ["GET", "HEAD"],
                "AllowedOrigins": ["*"],
                "MaxAgeSeconds": 86400,
            }
        ]
    },
)
```

