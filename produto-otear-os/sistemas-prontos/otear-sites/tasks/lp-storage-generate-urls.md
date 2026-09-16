---
task: generateUrls()
responsavel: "Silo"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: clientName
    tipo: string
    obrigatorio: true
    descricao: "Nome do cliente para buscar assets"

Saida:
  - nome: assetsManifest
    tipo: file
    obrigatorio: true
    descricao: "assets-manifest.json atualizado com todas as URLs"

Checklist:
  pre-conditions:
    - "[ ] Assets jÃ¡ uploaded no R2"
  post-conditions:
    - "[ ] Manifesto gerado com todas as URLs"
    - "[ ] URLs verificadas e acessÃ­veis"

Performance:
  duration_expected: "30 seconds"
  cacheable: true
  parallelizable: true
---

# generateUrls()

## DescriÃ§Ã£o

Lista todos os objetos no prefixo do cliente no R2 e gera o assets-manifest.json com URLs pÃºblicas.

## Passos

1. **Listar objetos** â€” `s3.list_objects_v2(Bucket="lp-assets", Prefix="{client-slug}/")`.
2. **Gerar URLs** â€” Para cada objeto, construir URL pÃºblica.
3. **Classificar** â€” Separar por tipo (image, video) e seÃ§Ã£o.
4. **Gerar manifesto** â€” JSON com mapa completo.
5. **Salvar** â€” `assets-manifest.json` no workspace.

