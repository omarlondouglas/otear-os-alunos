# CLI local de agentes

Este modo roda os agentes sem FastAPI, sem Agno runtime e sem chaves API no projeto.
Ele le as personas/instrucoes locais e usa um CLI ja autenticado na maquina.

## Por que existe

O backend principal continua podendo usar Agno e providers por API. O CLI local e
um caminho separado para desenvolvimento e operacao manual:

- le `app/agents/*.py` estaticamente, sem instanciar Agno;
- le agentes markdown em `squads/**/agents/*.agent.md` e `app/knowledge/**/*.agent.md`;
- monta um prompt de sistema com nome, papel e instrucoes do agente;
- executa via `codex exec` ou `claude -p`;
- nao precisa de `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` ou `GOOGLE_API_KEY`.

Voce ainda precisa estar logado no CLI escolhido:

```powershell
codex login
# ou
claude login
```

## Comandos

Listar agentes:

```powershell
python scripts/local_agent_cli.py list
```

Ver a persona/prompt de um agente:

```powershell
python scripts/local_agent_cli.py show ogilvy
```

Executar com Codex CLI:

```powershell
python scripts/local_agent_cli.py run ogilvy "Crie um post longo para LinkedIn sobre TEAR CRM"
```

Executar com Claude CLI:

```powershell
python scripts/local_agent_cli.py run ogilvy "Crie um post longo para LinkedIn sobre TEAR CRM" --engine claude
```

Ler tarefa via pipe:

```powershell
"Crie 5 ganchos sobre CRM com IA" | python scripts/local_agent_cli.py run ogilvy
```

Somente imprimir o prompt montado:

```powershell
python scripts/local_agent_cli.py run garyv "Crie um carrossel sobre IA" --engine print
```

## Limites importantes

Este modo simula a identidade do agente, mas nao executa as ferramentas Agno.
Se uma persona exigir `generate_carousel_tool`, `edit_video_tool` ou outra tool,
o agente deve entregar a melhor versao textual possivel e avisar que a ferramenta
nao foi executada no modo local.

Para executar tools reais, use o backend:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/agents/ogilvy/run `
  -ContentType "application/json" `
  -Body '{"task":"Crie uma copy para LinkedIn"}'
```
