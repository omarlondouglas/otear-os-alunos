---
task: saveVersion()
responsavel: "Vault"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: repoUrl
    tipo: string
    obrigatorio: true
    descricao: "URL do repositÃ³rio do cliente (source: initClientRepo())"
  - nome: projectFiles
    tipo: file
    obrigatorio: true
    descricao: "CÃ³digo fonte completo (frontend + backend + infra)"
  - nome: qaReport
    tipo: file
    obrigatorio: true
    descricao: "RelatÃ³rio final de QA com score e metadados"
  - nome: deployResult
    tipo: object
    obrigatorio: true
    descricao: "Resultado do deploy: URL live, domÃ­nio, EasyPanel project (source: deployEasyPanel())"
  - nome: version
    tipo: string
    obrigatorio: false
    descricao: "VersÃ£o semÃ¢ntica (default: auto-increment)"

Saida:
  - nome: releaseUrl
    tipo: string
    obrigatorio: true
    descricao: "URL da release no GitHub com metadados"
  - nome: versionTag
    tipo: string
    obrigatorio: true
    descricao: "Tag semÃ¢ntica criada (ex: v1.0.0)"

Checklist:
  pre-conditions:
    - "[ ] RepositÃ³rio do cliente existe e estÃ¡ clonado"
    - "[ ] CÃ³digo fonte completo disponÃ­vel"
    - "[ ] QA report com PASS"
    - "[ ] Deploy realizado com sucesso"
  post-conditions:
    - "[ ] CÃ³digo copiado para o repo do cliente"
    - "[ ] Commit com conventional commit message"
    - "[ ] Tag semÃ¢ntica criada"
    - "[ ] Release criada no GitHub com metadados"
    - "[ ] Changelog atualizado"

Performance:
  duration_expected: "5 minutes"
  cacheable: false
  parallelizable: false
---

# saveVersion()

## DescriÃ§Ã£o

Copia o cÃ³digo fonte completo para o repositÃ³rio do cliente, cria um commit semÃ¢ntico, aplica tag de versÃ£o e cria uma release no GitHub com metadados completos (QA score, seÃ§Ãµes, domÃ­nio, URL live).

## Passos

1. **Copiar arquivos** â€” Copiar packages/ (frontend + backend + infra) para o repo do cliente.
2. **Gerar README.md** â€” README completo com instruÃ§Ãµes, stack, seÃ§Ãµes, deploy guide.
3. **Gerar deploy-guide.md** â€” Guia especÃ­fico de deploy via EasyPanel.
4. **Atualizar changelog** â€” Adicionar entrada no changelog.md.
5. **Stage e commit** â€” `git add . && git commit -m "feat: landing page v{version}"`.
6. **Criar tag** â€” `git tag v{version}`.
7. **Push** â€” `git push origin main --tags`.
8. **Criar release** â€” `gh release create v{version}` com release notes incluindo metadados.

