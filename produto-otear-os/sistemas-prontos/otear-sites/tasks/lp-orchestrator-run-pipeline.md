---
task: runPipeline()
responsavel: "Nexus"
responsavel_type: Agente
atomic_layer: Template

Entrada:
  - nome: normalizedOrder
    tipo: file
    obrigatorio: true
    descricao: "Pedido normalizado (source: receiveOrder())"
  - nome: workspace
    tipo: string
    obrigatorio: true
    descricao: "Path do workspace do job"
  - nome: jobId
    tipo: string
    obrigatorio: true
    descricao: "ID do job para tracking"

Saida:
  - nome: pipelineResult
    tipo: object
    obrigatorio: true
    descricao: "Resultado completo: URLs, repo, QA score, duraÃ§Ã£o (destination: notify())"

Checklist:
  pre-conditions:
    - "[ ] Workspace criado com order.json e status.json"
    - "[ ] Claude Code CLI disponÃ­vel e autenticado"
    - "[ ] Vercel CLI autenticada"
    - "[ ] GitHub CLI autenticada"
  post-conditions:
    - "[ ] Todas as etapas executadas (ou skipped se condicional)"
    - "[ ] LP deployada na Vercel com URL acessÃ­vel"
    - "[ ] CÃ³digo versionado no GitHub do cliente"
    - "[ ] QA score >= 8.0"
    - "[ ] status.json atualizado com resultado final"
    - "[ ] Logs de cada etapa salvos"

Performance:
  duration_expected: "30-60 minutes"
  cacheable: false
  parallelizable: false
---

# runPipeline()

## DescriÃ§Ã£o

Executa o pipeline completo invocando cada agente via Claude Code CLI em sequÃªncia. Cada etapa Ã© um processo isolado que lÃª inputs do workspace e escreve outputs de volta.

## Pipeline Steps

```
Step  Agente          Comando Claude Code CLI                           Condicional
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
 1    Radar           *extract-design {reference_url}                   se url existe
 2    Radar           *extract-content {reference_url}                  se url existe
 3    Strategos       *discover + *elicit + *scope (auto mode)          sempre
 4    Scout           *research-competitors + *research-audience        sempre
 5    Quill           *write-section (todas as seÃ§Ãµes)                  sempre
 6    Prism           *select-ds + *tokens + *components + *sections    sempre
 7    Lens            *generate-hero + *generate-sections               sempre
 7b   Silo            *init-storage + *upload-assets                   sempre
 8    Pixel           *setup + *design-system + *build-sections + *assemble  sempre
 9    Forge           *setup + *leads + *admin                          backend: true
10    Bridge          *whatsapp + *email + *connect                     whatsapp/email: true
11    Shield          *run-qa (todas as dimensÃµes)                      sempre
12    Anchor          *deploy-vercel                                    sempre
13    Anchor          *dockerize + *deploy-easypanel                    backend: true
14    Anchor          *setup-domain                                     se custom_domain
15    Vault           *init-repo + *export + *save-version              sempre
```

## ExecuÃ§Ã£o via Claude Code CLI

```bash
#!/bin/bash
# Cada step Ã© uma invocaÃ§Ã£o do Claude Code CLI
# O workspace compartilha artefatos entre steps

WORKSPACE="/workspace/jobs/${JOB_ID}"
ORDER="${WORKSPACE}/order.json"

# Step 1: Extract design (se URL de referÃªncia existe)
if [ -n "$REFERENCE_URL" ]; then
  claude -p "You are lp-scraper (Radar). Extract design system from ${REFERENCE_URL}.
  Save output to ${WORKSPACE}/artifacts/extracted-design-tokens.md
  and ${WORKSPACE}/artifacts/extracted-content-structure.md" \
    --allowedTools "WebFetch,Write,Read,Grep" \
    2>&1 | tee "${WORKSPACE}/logs/01-scraper.log"
fi

# Step 2: Discovery (auto mode â€” sem questionÃ¡rio interativo)
claude -p "You are lp-strategist (Strategos). Run auto-discovery using:
  - Order: $(cat ${ORDER})
  - Reference design: ${WORKSPACE}/artifacts/extracted-design-tokens.md
  - Reference content: ${WORKSPACE}/artifacts/extracted-content-structure.md
  Generate product-brief.md and scope-definition.md in ${WORKSPACE}/artifacts/" \
    --allowedTools "Write,Read,WebSearch,WebFetch" \
    2>&1 | tee "${WORKSPACE}/logs/02-strategist.log"

# Step 3-15: ... mesmo padrÃ£o para cada agente
```

## Retry Logic

```python
async def run_step(step_name: str, claude_prompt: str, max_retries: int = 1):
    for attempt in range(max_retries + 1):
        result = await execute_claude_cli(claude_prompt)
        if result.success:
            update_status(step_name, "done", result.duration)
            return result
        if attempt < max_retries:
            notify(f"âš ï¸ {step_name} falhou, retentando...")
            await asyncio.sleep(5)

    update_status(step_name, "failed", error=result.error)
    notify(f"ðŸš¨ {step_name} falhou apÃ³s {max_retries + 1} tentativas: {result.error}")
    raise PipelineError(step_name, result.error)
```

## DecisÃ£o de Skip

```python
order = load_order()
steps_to_skip = []

if not order.get("reference_url"):
    steps_to_skip.extend(["extract-design", "extract-content"])

if not order["features"].get("backend"):
    steps_to_skip.extend(["backend-build", "dockerize", "deploy-easypanel"])

if not order["features"].get("whatsapp") and not order["features"].get("email"):
    steps_to_skip.append("integrations")

if not order.get("custom_domain"):
    steps_to_skip.append("setup-domain")
```

