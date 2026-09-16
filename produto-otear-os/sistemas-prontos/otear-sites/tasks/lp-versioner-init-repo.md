---
task: initClientRepo()
responsavel: "Vault"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: clientName
    tipo: string
    obrigatorio: true
    descricao: "Nome do cliente (usado como nome do repositÃ³rio)"
  - nome: orgName
    tipo: string
    obrigatorio: false
    descricao: "OrganizaÃ§Ã£o GitHub (default: configurado no squad)"

Saida:
  - nome: repoUrl
    tipo: string
    obrigatorio: true
    descricao: "URL do repositÃ³rio criado (destination: saveVersion())"
  - nome: repoConfig
    tipo: object
    obrigatorio: true
    descricao: "ConfiguraÃ§Ã£o do repo: nome, URL, branch default, proteÃ§Ãµes"

Checklist:
  pre-conditions:
    - "[ ] GitHub CLI (gh) autenticado"
    - "[ ] Nome do cliente definido"
    - "[ ] OrganizaÃ§Ã£o GitHub acessÃ­vel"
  post-conditions:
    - "[ ] RepositÃ³rio criado no GitHub (private)"
    - "[ ] .gitignore configurado (node_modules, __pycache__, .env, .next, etc.)"
    - "[ ] README.md inicial com nome do projeto"
    - "[ ] Branch main protegido"
    - "[ ] Repo clonado localmente"

Performance:
  duration_expected: "3 minutes"
  cacheable: false
  parallelizable: false
---

# initClientRepo()

## DescriÃ§Ã£o

Cria um repositÃ³rio privado no GitHub para o cliente usando GitHub CLI (`gh`). Configura .gitignore, README inicial e branch protection.

## Passos

1. **Verificar autenticaÃ§Ã£o** â€” `gh auth status` para confirmar login.
2. **Criar repositÃ³rio** â€” `gh repo create org/{client-name}-lp --private --description "Landing Page - {Client Name}"`.
3. **Clonar localmente** â€” `gh repo clone org/{client-name}-lp`.
4. **Criar .gitignore** â€” Node.js + Python + Docker exclusions.
5. **Criar README.md inicial** â€” Nome do projeto, stack, status.
6. **Commit inicial** â€” `feat: initialize client repository`.
7. **Push** â€” `git push origin main`.
8. **Branch protection** â€” Configurar via `gh api` (require PR, no force push).

