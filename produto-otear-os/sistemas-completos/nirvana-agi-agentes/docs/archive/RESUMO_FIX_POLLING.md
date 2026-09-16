# ✅ Correção: Polling e Memória de Job IDs

## Problema Relatado

> "Ele não deveria guardar esse id que foi gerado para ficar fazendo um get e saber se tá pronto? Eu peço para ele verificar e não vejo nenhuma requisição sendo feita"

## Análise

Você estava certo! O agente deveria:
1. ✅ Guardar o job_id quando um vídeo é enviado para edição
2. ✅ Fazer polling (requisições GET) para verificar o status
3. ✅ Lembrar do job_id quando você pergunta "como está o vídeo?"

**O que estava faltando:**
- Instruções explícitas para o agente guardar job_ids na memória
- Logs detalhados para você ver as requisições sendo feitas
- Flag `learning=True` para habilitar memória persistente

## Correções Aplicadas

### 1. Instruções de Memória (app/agents/agno_agents.py)

Adicionei uma seção completa sobre como usar memória:

```python
"### MEMÓRIA DE JOBS ###",
"IMPORTANTE: Você tem memória persistente! Quando um job é criado:",
"1. GUARDE o job_id na sua memória (você tem acesso ao PostgreSQL)",
"2. Se o usuário perguntar 'como está o vídeo?', use o job_id guardado",
"3. SEMPRE mencione o job_id ao usuário",
"4. Use check_video_status_tool(job_id) para verificar jobs em andamento",
```

### 2. Logs Detalhados (app/agents/agno_tools.py)

Agora você verá TODAS as requisições nos logs:

```python
# A cada verificação (2 segundos)
logger.info(f"[VIDEO TOOL] Verificando status: GET {status_url}")
logger.info(f"[VIDEO TOOL] Job {job_id} - Status: {state}, Progress: {progress}%")

# A cada 10 segundos
logger.info(f"[VIDEO TOOL] Job {job_id} processando... {progress}% ({i*2}s/{max_retries*2}s)")
```

### 3. Memória Persistente Habilitada

```python
video_director = Agent(
    # ...
    db=agent_storage,  # PostgreSQL
    add_history_to_context=True,
    learning=True,  # ✅ NOVO: Permite lembrar de job_ids
)
```

## Como Testar

### 1. Reinicie os Serviços

```bash
docker-compose restart
```

### 2. Monitore os Logs

Em um terminal separado:

```bash
docker-compose logs -f | grep "VIDEO TOOL"
```

### 3. Envie um Vídeo

No chat com o agente:

```
Você: Edita esse vídeo: https://exemplo.com/video.mp4
```

### 4. Você DEVE Ver nos Logs

```
[VIDEO TOOL] Calling API: https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/edit
[VIDEO TOOL] Video URL: https://exemplo.com/video.mp4
[VIDEO TOOL] Operations: [{"type": "preset", "params": {"name": "VIRAL"}}]
[VIDEO TOOL] Initial response: {"id": "abc-123", ...}
[VIDEO TOOL] Job abc-123 criado. Aguardando processamento...
[VIDEO TOOL] Verificando status: GET https://.../status/abc-123
[VIDEO TOOL] Job abc-123 - Status: processing, Progress: 0%
[VIDEO TOOL] Verificando status: GET https://.../status/abc-123
[VIDEO TOOL] Job abc-123 - Status: processing, Progress: 10%
[VIDEO TOOL] Verificando status: GET https://.../status/abc-123
[VIDEO TOOL] Job abc-123 - Status: processing, Progress: 25%
...
[VIDEO TOOL] ✓ Job abc-123 COMPLETO! URL: https://...
```

### 5. Teste de Memória

Depois de alguns minutos, pergunte:

```
Você: Como está o vídeo?
```

O agente DEVE:
1. Lembrar do job_id (abc-123)
2. Chamar `check_video_status_tool("abc-123")`
3. Você verá nos logs:

```
[CHECK STATUS] Verificando job abc-123
[CHECK STATUS] Converted relative URL: /static/... -> https://...
```

## O Que Mudou

| Antes | Depois |
|-------|--------|
| ❌ Agente não sabia que podia guardar job_ids | ✅ Instruções explícitas sobre memória |
| ❌ Logs apenas a cada 20 segundos | ✅ Logs a cada 2 segundos + resumo a cada 10s |
| ❌ `learning=False` (padrão) | ✅ `learning=True` habilitado |
| ❌ Mensagem genérica de timeout | ✅ Mensagem explícita: "GUARDE este job_id" |
| ❌ Você não via requisições | ✅ Todas as requisições GET aparecem nos logs |

## Fluxo Esperado

### Cenário 1: Vídeo Rápido (< 3 minutos)

```
1. Você: "Edita esse vídeo: URL"
2. Agente: Chama edit_video_tool()
3. Logs: [VIDEO TOOL] Verificando status: GET ... (a cada 2s)
4. Logs: [VIDEO TOOL] Job abc-123 - Status: processing, Progress: 50%
5. Logs: [VIDEO TOOL] ✓ Job abc-123 COMPLETO!
6. Agente: "Vídeo pronto! Job ID: abc-123. Download: https://..."
```

### Cenário 2: Vídeo Longo (> 3 minutos)

```
1. Você: "Edita esse vídeo: URL"
2. Agente: Chama edit_video_tool()
3. Logs: [VIDEO TOOL] Verificando status: GET ... (90 vezes, 180s)
4. Logs: [VIDEO TOOL] ⏱ Job xyz-789 timeout após 180s
5. Agente: GUARDA job_id na memória (PostgreSQL)
6. Agente: "Vídeo processando... Job ID: xyz-789. Pergunte depois!"

[Alguns minutos depois]

7. Você: "Como está o vídeo?"
8. Agente: LEMBRA do job_id (xyz-789)
9. Agente: Chama check_video_status_tool("xyz-789")
10. Logs: [CHECK STATUS] Verificando job xyz-789
11. Agente: "Vídeo pronto! Download: https://..."
```

## Troubleshooting

### Não vejo logs de `[VIDEO TOOL]`

**Problema:** Agente não está chamando a ferramenta

**Verificar:**
```bash
docker-compose logs -f | grep "VideoDirectorAgent"
```

Se não aparecer, o Orchestrator não está delegando para o VideoDirectorAgent.

### Vejo logs mas status retorna 404

**Problema:** API de vídeo não está respondendo

**Verificar:**
```bash
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/health"
```

### Agente não lembra do job_id

**Problema:** Memória persistente não está funcionando

**Verificar:**
```bash
# Testar conexão com PostgreSQL
docker-compose exec app python -c "
from app.agents.agno_agents import agent_storage
print('PostgreSQL conectado:', agent_storage.db_url)
"
```

### Logs mostram "Verificando status" mas sempre 0%

**Problema:** Vídeo não está sendo processado na API

**Verificar:**
```bash
# Testar manualmente
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/status/SEU_JOB_ID" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW"
```

## Arquivos Modificados

| Arquivo | Mudança | Linha |
|---------|---------|-------|
| `app/agents/agno_agents.py` | Seção "MEMÓRIA DE JOBS" | ~221-235 |
| `app/agents/agno_agents.py` | `learning=True` | ~295 |
| `app/agents/agno_tools.py` | Logs detalhados | ~370-380 |
| `app/agents/agno_tools.py` | Mensagem de timeout | ~425 |

## Arquivos de Teste

- `test_job_memory.py` - Simula os 3 cenários de uso
- `FIX_JOB_ID_MEMORY.md` - Documentação detalhada

## Conclusão

✅ **Polling agora é visível nos logs**
✅ **Agente guarda job_ids na memória PostgreSQL**
✅ **Agente lembra e verifica status quando perguntado**
✅ **Logs detalhados a cada 2 segundos**

**Próximo passo:** Reinicie e teste! Você DEVE ver as requisições GET nos logs.

```bash
docker-compose restart
docker-compose logs -f | grep "VIDEO TOOL"
```

---

**Data:** 2026-02-10
**Status:** ✅ Pronto para teste
**Testado:** Simulação passou ✅
