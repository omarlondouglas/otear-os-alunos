---
task: exportClient()
responsavel: "Vault"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: repoUrl
    tipo: string
    obrigatorio: true
    descricao: "URL do repositÃ³rio do cliente"
  - nome: projectFiles
    tipo: file
    obrigatorio: true
    descricao: "CÃ³digo fonte completo"
  - nome: dockerConfig
    tipo: file
    obrigatorio: true
    descricao: "Dockerfiles e compose"

Saida:
  - nome: exportPackage
    tipo: file
    obrigatorio: true
    descricao: "Pacote completo exportado no repo do cliente (cÃ³digo + Docker + docs)"

Checklist:
  pre-conditions:
    - "[ ] RepositÃ³rio do cliente existe"
    - "[ ] CÃ³digo fonte completo disponÃ­vel"
    - "[ ] Dockerfiles disponÃ­veis"
  post-conditions:
    - "[ ] Pacote completo no repo: frontend + backend + infra + docs"
    - "[ ] docker-compose.yml simplificado para o cliente"
    - "[ ] .env.example com todas as variÃ¡veis"
    - "[ ] README.md com instruÃ§Ãµes completas"
    - "[ ] deploy-guide.md com passo a passo do EasyPanel"

Performance:
  duration_expected: "5 minutes"
  cacheable: false
  parallelizable: false
---

# exportClient()

## DescriÃ§Ã£o

Exporta o pacote completo da landing page para o repositÃ³rio do cliente, incluindo cÃ³digo fonte, configuraÃ§Ã£o Docker, documentaÃ§Ã£o de deploy via EasyPanel e templates de variÃ¡veis de ambiente.

## Passos

1. **Copiar cÃ³digo fonte** â€” packages/frontend/ e packages/backend/ (condicional).
2. **Copiar infra** â€” Dockerfiles, docker-compose.prod.yml, nginx.conf.
3. **Criar docker-compose.yml simplificado** â€” VersÃ£o fÃ¡cil de usar para o cliente.
4. **Criar .env.example** â€” Template com todas as variÃ¡veis e comentÃ¡rios.
5. **Gerar README.md** â€” DocumentaÃ§Ã£o completa com:
   - VisÃ£o geral do projeto
   - Stack tecnolÃ³gica
   - Como rodar localmente
   - Como fazer deploy via EasyPanel
   - ConfiguraÃ§Ã£o de domÃ­nio
   - VariÃ¡veis de ambiente
6. **Gerar deploy-guide.md** â€” Guia passo a passo para deploy no EasyPanel:
   - Criar projeto no EasyPanel
   - Conectar repo GitHub
   - Configurar variÃ¡veis
   - Adicionar domÃ­nio
   - Verificar SSL
7. **Commit e push** â€” Enviar tudo para o repo do cliente.

