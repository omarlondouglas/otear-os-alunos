# Fix: Memória de Job IDs e Polling

## Problema Identificado

Você relatou que quando pede para o agente verificar o status de um vídeo, **não vê nenhuma requisição sendo feita**.

### Causa Raiz

1. **O agente não estava guardando o job_id** - Mesmo tendo acesso ao PostgreSQL para memória persistente, as instruções não diziam explicitamente para guardar e recuperar job_ids
2. **Logs insuficientes** - O polling estava acontecendo mas sem logs detalhados para debug
3. **Agente não sabia que podia verificar depois** - Faltavam instruções sobre como usar a memória persistente

## Soluções Aplicadas

### 1. Instruções de Memória no VideoDirectorAgent

Adicionei uma seção completa sobre memória de jobs:

```python
"### MEMÓRIA DE JOBS ###",
"IMPORTANTE: Você tem memória persistente! Quando um job é criado:",
"1. GUARDE o job_id na sua memória (você tem acesso ao PostgreSQL)",
"2. Se o usuário perguntar 'como está o vídeo?' ou 'já terminou?', use o job_id guardado",
"3. SEMPRE mencione o job_id ao usuário: 'Job ID: {job_id} - Status: processando...'",
"4. Se o processamento demorar (timeout), informe: 'Job {job_id} ainda processando. Vou verificar...'",
"5. Use check_video_status_tool(job_id) para verificar jobs em andamento",
```

### 2. Logs Detalhados no Polling

Adicionei logs a cada verificação:

```python
# Antes: Log apenas a cada 10 verificações (20 segundos)
if i % 10 == 0:
    logger.info(f"[VIDEO TOOL] Job {job_id} processando... {progress}%")

# Depois: Log a cada verificação + log a cada 5 verificações (10 segundos)
logger.info(f"[VIDEO TOOL] Verificando status: GET {status_url}")
logger.info(f"[VIDEO TOOL] Job {job_id} - Status: {state}, Progress: {progress}%")

if i % 5 == 0:  # A cada 10 segundos
    logger.info(f"[VIDEO TOOL] Job {job_id} processando... {progress}% ({i*2}s/{max_retries*2}s)")
```

### 3. Mensagem Explícita de Timeout

Quando o polling atinge timeout (3 minutos), a mensagem agora é mais clara:

```python
return {
    "status": "processing",
    "id": job_id,
    "message": f"Vídeo ainda processando após {max_retries*2}s. IMPORTANTE: Guarde este job_id e use check_video_status_tool('{job_id}') para verificar o progresso."
}
```

### 4. Habilitado `learning=True`

O VideoDirectorAgent agora tem:

```python
video_director = Agent(
    name="VideoDirectorAgent",
    # ...
    db=agent_storage,  # PostgreSQL para memória persistente
    add_history_to_context=True,  # Adiciona histórico ao contexto
    learning=True,  # ✅ NOVO: Permite aprender e lembrar de job_ids
    # ...
)
```

## Como Funciona Agora

### Fluxo Normal (Vídeo completa em < 3 minutos)

```
Usuário: "Edita esse vídeo: https://exemplo.com/video.mp4"

VideoDirectorAgent:
  1. Chama edit_video_tool()
  2. Recebe job_id = "abc-123"
  3. Faz polling a cada 2 segundos
  4. Logs aparecem:
     [VIDEO TOOL] Verificando status: GET https://.../status/abc-123
     [VIDEO TOOL] Job abc-123 - Status: processing, Progress: 25%
     [VIDEO TOOL] Job abc-123 - Status: processing, Progress: 50%
     [VIDEO TOOL] Job abc-123 - Status: completed, Progress: 100%
     [VIDEO TOOL] ✓ Job abc-123 COMPLETO! URL: https://...
  5. Retorna ao usuário: "Vídeo editado! Job ID: abc-123. Download: https://..."
```

### Fluxo com Timeout (Vídeo demora > 3 minutos)

```
Usuário: "Edita esse vídeo: https://exemplo.com/video.mp4"

VideoDirectorAgent:
  1. Chama edit_video_tool()
  2. Recebe job_id = "abc-123"
  3. Faz polling por 3 minutos
  4. Timeout!
  5. Retorna: {
       "status": "processing",
       "id": "abc-123",
       "message": "Vídeo ainda processando... IMPORTANTE: Guarde este job_id..."
     }
  6. GUARDA job_id="abc-123" na memória (PostgreSQL)
  7. Responde ao usuário: "Vídeo em processamento... Job ID: abc-123. Vou continuar verificando."

[Depois de alguns minutos]

Usuário: "E o vídeo?"

VideoDirectorAgent:
  1. LEMBRA do job_id="abc-123" (da memória PostgreSQL)
  2. Chama check_video_status_tool("abc-123")
  3. Logs aparecem:
     [CHECK STATUS] Verificando job abc-123
     [CHECK STATUS] Converted relative URL: /static/... -> https://...
  4. Retorna: "Vídeo pronto! Job ID: abc-123. Download: https://..."
```

## Como Verificar se Está Funcionando

### 1. Verifique os Logs

Após enviar um vídeo para edição, procure por:

```bash
docker-compose logs -f | grep "VIDEO TOOL"
```

**Você DEVE ver:**
```
[VIDEO TOOL] Calling API: https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/edit
[VIDEO TOOL] Video URL: https://...
[VIDEO TOOL] Operations: [...]
[VIDEO TOOL] Initial response: {"id": "abc-123", ...}
[VIDEO TOOL] Job abc-123 criado. Aguardando processamento...
[VIDEO TOOL] Verificando status: GET https://.../status/abc-123
[VIDEO TOOL] Job abc-123 - Status: processing, Progress: 0%
[VIDEO TOOL] Job abc-123 - Status: processing, Progress: 10%
...
```

### 2. Teste Manual da API

Verifique se a API está respondendo:

```bash
# 1. Criar um job
curl -X POST "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/edit" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW" \
  -F 'request={"video_url":"https://exemplo.com/video.mp4","operations":[{"type":"preset","params":{"name":"VIRAL"}}],"output_format":"mp4"}'

# Resposta: {"id": "abc-123", ...}

# 2. Verificar status
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/status/abc-123" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW"

# Resposta: {"status": "processing", "progress": 50, ...}
```

### 3. Teste com o Agente

```
Você: "Edita esse vídeo: https://exemplo.com/video.mp4"

Agente: "Iniciando edição... Job ID: abc-123. Aguarde..."

[Espere alguns segundos]

Você: "Como está o vídeo?"

Agente: [DEVE chamar check_video_status_tool("abc-123")]
        "Job abc-123 - Status: processando... 75%"

[Quando completar]

Você: "E agora?"

Agente: "Vídeo pronto! Job ID: abc-123. Download: https://..."
```

## Possíveis Problemas

### Problema 1: Não vejo logs de `[VIDEO TOOL]`

**Causa:** Agente não está chamando a ferramenta
**Solução:** Verificar se o Orchestrator está delegando para o VideoDirectorAgent

```bash
docker-compose logs -f | grep "VideoDirectorAgent"
```

### Problema 2: Vejo logs mas status sempre retorna 404

**Causa:** API de vídeo não está rodando ou job_id inválido
**Solução:** Verificar se o serviço de vídeo está up

```bash
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/health"
```

### Problema 3: Agente não lembra do job_id

**Causa:** Memória persistente não está funcionando
**Solução:** Verificar se o PostgreSQL está acessível

```bash
# No .env, verificar:
DATABASE_URL=postgres://postgres:92c9b3198ebec170b34e@otear_db_agi:5432/agi?sslmode=disable

# Testar conexão:
docker-compose exec app python -c "from app.agents.agno_agents import agent_storage; print(agent_storage)"
```

### Problema 4: Polling para após 3 minutos e nunca mais verifica

**Causa:** Agente não está usando check_video_status_tool
**Solução:** Instruções atualizadas para dizer explicitamente para continuar verificando

## Arquivos Modificados

| Arquivo | Mudança | Linha |
|---------|---------|-------|
| `app/agents/agno_agents.py` | Adicionada seção "MEMÓRIA DE JOBS" | ~221-235 |
| `app/agents/agno_agents.py` | Habilitado `learning=True` | ~295 |
| `app/agents/agno_tools.py` | Logs detalhados no polling | ~370-380 |
| `app/agents/agno_tools.py` | Mensagem explícita de timeout | ~425 |

## Próximos Passos

1. **Reinicie os serviços:**
   ```bash
   docker-compose restart
   ```

2. **Teste com um vídeo real:**
   - Envie uma URL de vídeo
   - Monitore os logs: `docker-compose logs -f | grep "VIDEO TOOL"`
   - Pergunte "como está o vídeo?" após alguns minutos

3. **Verifique a memória:**
   - Após o agente guardar um job_id, pergunte novamente
   - O agente DEVE lembrar do job_id e verificar automaticamente

## Resumo

✅ **Agente agora tem instruções explícitas para guardar job_ids**
✅ **Logs detalhados para debug de polling**
✅ **Memória persistente habilitada (`learning=True`)**
✅ **Mensagens claras sobre timeout e como continuar verificando**

**O agente agora deve:**
1. Fazer polling visível nos logs
2. Guardar job_ids na memória
3. Verificar status quando perguntado
4. Continuar verificando mesmo após timeout

---

**Data:** 2026-02-10
**Status:** ✅ Pronto para teste
