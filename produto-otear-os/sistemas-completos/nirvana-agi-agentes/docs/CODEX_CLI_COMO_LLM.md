# Codex CLI como LLM principal

Este projeto agora pode usar o Codex CLI como backend de LLM dos agentes Agno.

## Configuracao minima

Na VPS:

```bash
codex login
codex exec --sandbox read-only --ephemeral "responda apenas: ok"
```

No `.env` do backend:

```env
MODEL_PROVIDER=codex-cli
CODEX_CLI_SANDBOX=read-only
CODEX_CLI_TIMEOUT_S=240
```

Por padrao, o sistema nao define `CODEX_MODEL`. Assim o Codex usa o modelo
padrao aceito pela conta autenticada. No ambiente testado, passar
`gpt-5.1-codex-mini` explicitamente falhou por nao estar disponivel na conta,
enquanto o default do CLI funcionou.

Se quiser forcar um modelo especifico:

```env
CODEX_MODEL=gpt-5.5
# ou por papel:
CODEX_MODEL_PLANNER=gpt-5.5
CODEX_MODEL_WRITER=gpt-5.5
CODEX_MODEL_FAST=gpt-5.5
```

## Como funciona

```text
Agno Agent
  -> app.core.model_factory.get_model()
  -> CodexCliModel
  -> codex exec
  -> resposta final / TOOL_CALL
```

O adapter fica em:

```text
app/core/codex_cli_model.py
```

O seletor fica em:

```text
app/core/model_factory.py
```

## Limite importante

Use isso em ambiente privado/confiavel. O Codex CLI usa autenticacao local em
`~/.codex`, que deve ser tratada como segredo. Nao exponha uma VPS com Codex CLI
para execucao arbitraria de usuarios.

Para o produto, mantenha `CODEX_CLI_SANDBOX=read-only`. As tools do proprio app
fazem a execucao real de pesquisa, carrossel, video e biblioteca.
