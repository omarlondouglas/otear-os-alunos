---
task: listVersions()
responsavel: "Vault"
responsavel_type: Agente
atomic_layer: Molecule

Entrada:
  - nome: clientName
    tipo: string
    obrigatorio: true
    descricao: "Nome do cliente para buscar versÃµes"

Saida:
  - nome: versionList
    tipo: array
    obrigatorio: true
    descricao: "Lista de versÃµes entregues com metadados"

Checklist:
  pre-conditions:
    - "[ ] GitHub CLI autenticado"
    - "[ ] RepositÃ³rio do cliente existe"
  post-conditions:
    - "[ ] Lista de releases retornada com metadados"

Performance:
  duration_expected: "1 minute"
  cacheable: true
  parallelizable: true
---

# listVersions()

## DescriÃ§Ã£o

Lista todas as versÃµes (releases) entregues para um cliente especÃ­fico, incluindo metadados de cada entrega.

## Passos

1. **Buscar releases** â€” `gh release list --repo org/{client-name}-lp`.
2. **Formatar saÃ­da** â€” VersÃ£o, data, QA score, domÃ­nio, status.
3. **Retornar lista** â€” Array ordenado por data (mais recente primeiro).

