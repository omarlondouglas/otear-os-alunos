# Comandos para Testar Polling e Memória

## 1. Reiniciar Serviços

```bash
docker-compose restart
```

## 2. Monitorar Logs em Tempo Real

### Ver TODOS os logs do agente
```bash
docker-compose logs -f app
```

### Ver APENAS logs de vídeo
```bash
docker-compose logs -f | grep "VIDEO TOOL"
```

### Ver logs de vídeo E status
```bash
docker-compose logs -f | grep -E "VIDEO TOOL|CHECK STATUS"
```

### Ver logs do VideoDirectorAgent
```bash
docker-compose logs -f | grep "VideoDirectorAgent"
```

## 3. Testar API de Vídeo Manualmente

### Verificar se a API está online
```bash
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/health"
```

**Resposta esperada:**
```json
{"status": "ok"}
```

### Criar um job de teste
```bash
curl -X POST "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/edit" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW" \
  -F 'request={"video_url":"https://exemplo.com/video.mp4","operations":[{"type":"preset","params":{"name":"VIRAL"}}],"output_format":"mp4"}'
```

**Resposta esperada:**
```json
{"id": "abc-123-def-456", "status": "pending"}
```

### Verificar status de um job
```bash
# Substitua JOB_ID pelo ID retornado acima
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/status/JOB_ID" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW"
```

**Resposta esperada:**
```json
{
  "id": "abc-123-def-456",
  "status": "processing",
  "progress": 50,
  "download_url": null
}
```

**Quando completo:**
```json
{
  "id": "abc-123-def-456",
  "status": "completed",
  "progress": 100,
  "download_url": "/static/abc-123-def-456_final.mp4"
}
```

## 4. Testar com o Agente

### Teste 1: Vídeo Simples

**No chat:**
```
Edita esse vídeo: https://exemplo.com/video.mp4
```

**Logs esperados:**
```
[VIDEO TOOL] Calling API: https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/edit
[VIDEO TOOL] Video URL: https://exemplo.com/video.mp4
[VIDEO TOOL] Job abc-123 criado. Aguardando processamento...
[VIDEO TOOL] Verificando status: GET https://.../status/abc-123
[VIDEO TOOL] Job abc-123 - Status: processing, Progress: 0%
[VIDEO TOOL] Verificando status: GET https://.../status/abc-123
[VIDEO TOOL] Job abc-123 - Status: processing, Progress: 25%
...
[VIDEO TOOL] ✓ Job abc-123 COMPLETO! URL: https://...
```

**Resposta do agente:**
```
Vídeo editado com sucesso! 🎬

Job ID: abc-123
Download: https://otear-otear-editavideos.qc7qit.easypanel.host/static/abc-123_final.mp4

O vídeo foi processado com legendas amarelas e remoção de silêncio (preset VIRAL).
```

### Teste 2: Verificar Status Depois

**No chat (alguns minutos depois):**
```
Como está o vídeo?
```

**Logs esperados:**
```
[CHECK STATUS] Verificando job abc-123
[CHECK STATUS] Converted relative URL: /static/... -> https://...
```

**Resposta do agente:**
```
Vídeo pronto! 🎬

Job ID: abc-123
Download: https://otear-otear-editavideos.qc7qit.easypanel.host/static/abc-123_final.mp4
```

### Teste 3: Vídeo com Job ID Específico

**No chat:**
```
Verifica o status do job abc-123
```

**Logs esperados:**
```
[CHECK STATUS] Verificando job abc-123
```

## 5. Verificar Memória do Agente

### Ver sessões no PostgreSQL
```bash
docker-compose exec app python -c "
from app.agents.agno_agents import agent_storage
from sqlalchemy import text

with agent_storage.Session() as session:
    result = session.execute(text('SELECT * FROM agno_sessions LIMIT 5'))
    for row in result:
        print(row)
"
```

### Verificar se PostgreSQL está acessível
```bash
docker-compose exec app python -c "
from app.agents.agno_agents import agent_storage
print('DB URL:', agent_storage.db_url)
print('Table:', agent_storage.session_table)
"
```

## 6. Debug de Problemas

### Problema: Não vejo logs de [VIDEO TOOL]

**Verificar se o agente está sendo chamado:**
```bash
docker-compose logs -f | grep -i "video"
```

**Verificar se o Orchestrator está delegando:**
```bash
docker-compose logs -f | grep "Patricia"
```

### Problema: Status sempre retorna 404

**Verificar se o serviço de vídeo está rodando:**
```bash
docker-compose ps
```

**Verificar logs do serviço de vídeo:**
```bash
docker-compose logs video-service
```

### Problema: Polling para e nunca mais verifica

**Verificar se o agente tem memória habilitada:**
```bash
docker-compose exec app python -c "
from app.agents.agno_agents import video_director
print('Learning enabled:', video_director.learning)
print('DB configured:', video_director.db is not None)
"
```

### Problema: URL retorna 404 ao baixar

**Testar URL diretamente:**
```bash
# Substitua pela URL retornada pelo agente
curl -I "https://otear-otear-editavideos.qc7qit.easypanel.host/static/abc-123_final.mp4"
```

**Resposta esperada:**
```
HTTP/2 200
content-type: video/mp4
```

## 7. Limpar e Reconstruir (Se Necessário)

### Limpar containers e volumes
```bash
docker-compose down -v
```

### Reconstruir sem cache
```bash
docker-compose build --no-cache
```

### Subir novamente
```bash
docker-compose up -d
```

### Ver logs de inicialização
```bash
docker-compose logs -f
```

## 8. Testes Automatizados

### Teste de conversão de URL
```bash
python test_url_fix.py
```

### Teste de fluxo do agente
```bash
python test_agent_video_flow.py
```

### Teste de memória de job
```bash
python test_job_memory.py
```

## 9. Monitoramento Contínuo

### Terminal 1: Logs do agente
```bash
docker-compose logs -f app | grep -E "VIDEO TOOL|CHECK STATUS"
```

### Terminal 2: Logs do serviço de vídeo
```bash
docker-compose logs -f video-service
```

### Terminal 3: Chat com o agente
```
# Use a interface web ou API
```

## 10. Checklist de Validação

Após reiniciar, verifique:

- [ ] Serviços estão rodando: `docker-compose ps`
- [ ] API de vídeo responde: `curl https://.../api/health`
- [ ] Logs aparecem ao enviar vídeo: `docker-compose logs -f | grep "VIDEO TOOL"`
- [ ] Vejo requisições GET nos logs: `[VIDEO TOOL] Verificando status: GET ...`
- [ ] Agente retorna URL completa: `https://...`
- [ ] Agente lembra do job_id quando pergunto depois
- [ ] URL do vídeo funciona no navegador

## Resumo dos Comandos Mais Importantes

```bash
# 1. Reiniciar
docker-compose restart

# 2. Ver logs de vídeo
docker-compose logs -f | grep "VIDEO TOOL"

# 3. Testar API
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/health"

# 4. Ver status de um job
curl "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/status/JOB_ID" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW"
```

---

**Dica:** Mantenha um terminal aberto com `docker-compose logs -f | grep "VIDEO TOOL"` enquanto testa!
