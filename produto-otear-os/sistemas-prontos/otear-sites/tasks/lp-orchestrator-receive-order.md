---
task: receiveOrder()
responsavel: "Nexus"
responsavel_type: Agente
atomic_layer: Organism

Entrada:
  - nome: orderPayload
    tipo: object
    obrigatorio: true
    descricao: "JSON do pedido recebido via webhook (client_name, business_name, niche, product, reference_url, contact, features)"

Saida:
  - nome: jobId
    tipo: string
    obrigatorio: true
    descricao: "ID Ãºnico do job criado"
  - nome: workspace
    tipo: string
    obrigatorio: true
    descricao: "Path do workspace isolado para este job"
  - nome: normalizedOrder
    tipo: file
    obrigatorio: true
    descricao: "Pedido normalizado e validado (destination: runPipeline())"

Checklist:
  pre-conditions:
    - "[ ] Payload contÃ©m campos obrigatÃ³rios (client_name, niche, product)"
    - "[ ] reference_url acessÃ­vel (se fornecida)"
  post-conditions:
    - "[ ] Job ID gerado (UUID)"
    - "[ ] Workspace criado no filesystem"
    - "[ ] order.json salvo no workspace"
    - "[ ] status.json inicializado"
    - "[ ] NotificaÃ§Ã£o enviada: job iniciado"

Performance:
  duration_expected: "30 seconds"
  cacheable: false
  parallelizable: false
---

# receiveOrder()

## DescriÃ§Ã£o

Recebe o pedido do webhook, valida os campos, gera um job ID, cria o workspace isolado e inicializa o tracking de status.

## Passos

1. **Validar payload** â€” Campos obrigatÃ³rios presentes e vÃ¡lidos.
2. **Gerar job ID** â€” UUID curto: `job_{8chars}`.
3. **Criar workspace** â€” `/workspace/jobs/job_{id}_{client-slug}/`.
4. **Salvar order.json** â€” Pedido original normalizado.
5. **Inicializar status.json** â€” Todas as etapas como "pending".
6. **Criar diretÃ³rios** â€” `logs/`, `artifacts/`, `packages/`.
7. **Notificar** â€” "ðŸš€ Job {id}: Criando LP para {client}..."
8. **Retornar** â€” job_id + workspace path.

