# ⚠️ Backend Offline - 502 Bad Gateway

## Problema Crítico

O erro `502 Bad Gateway` significa que o **backend não está respondendo**. O Easypanel está tentando conectar ao backend, mas ele está:
- Offline
- Crashado
- Não iniciou corretamente
- Porta errada

## Verificação Imediata

### 1. Verificar se Backend Está Online

```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/health
```

**Se retornar 502:** Backend está offline ❌
**Se retornar `{"status":"healthy"}`:** Backend está online ✅

### 2. No Easypanel - Verificar Logs

1. Acesse o Easypanel
2. Vá para `otear-agentes-otear`
3. Clique em "Logs" ou "Console"
4. Procure por erros:

**Erros Comuns:**
```
ModuleNotFoundError: No module named 'fastapi'
ImportError: cannot import name 'CORSMiddleware'
Error: Port 8000 is already in use
Failed to start application
```

### 3. Verificar Status do Container

No Easypanel, procure por:
- "Status": Deve estar "Running" (verde)
- "Health": Deve estar "Healthy"

Se estiver "Stopped" ou "Unhealthy", o container crashou.

## Possíveis Causas

### Causa 1: Erro no Código

Se você vê erro de import nos logs:
```python
ModuleNotFoundError: No module named 'datetime'
```

**Solução:** O import está errado. Vou verificar.

### Causa 2: Porta Errada

O container pode estar tentando usar uma porta que já está em uso.

**Solução:** Verificar `docker-compose.yml` e variável `PORT`.

### Causa 3: Dependências Faltando

O `requirements.txt` pode estar desatualizado.

**Solução:** Rebuild com `--no-cache`.

### Causa 4: Variável de Ambiente Faltando

O backend pode estar crashando por falta de variável obrigatória.

**Solução:** Verificar todas as variáveis no Easypanel.

## Solução Rápida

### Passo 1: Verificar Logs no Easypanel

Vá para "Logs" e copie os últimos 50 linhas. Procure por:
- `ERROR`
- `FAILED`
- `Traceback`
- `Exception`

### Passo 2: Restart do Container

No Easypanel:
1. Clique em "Restart" ou "Redeploy"
2. Aguarde 30 segundos
3. Verifique os logs novamente

### Passo 3: Rebuild Completo

Se restart não funcionar:
1. Clique em "Rebuild"
2. Marque "No Cache"
3. Aguarde o build completar
4. Verifique os logs

## Teste Local

Para verificar se o problema é no código ou no Easypanel:

```bash
# No seu computador
docker-compose down
docker-compose up

# Em outro terminal
curl http://localhost:8000/health
```

Se funcionar localmente, o problema é no Easypanel.

## Checklist de Diagnóstico

- [ ] Verificou logs no Easypanel
- [ ] Container está "Running"
- [ ] Fez restart do container
- [ ] Testou `curl /health`
- [ ] Verificou variáveis de ambiente
- [ ] Fez rebuild com no-cache

## Comandos de Teste

### Teste 1: Backend está online?
```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/health
```

### Teste 2: Endpoint raiz funciona?
```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/
```

### Teste 3: API v1 funciona?
```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/api/v1/logs
```

## O Que Fazer Agora

1. **URGENTE:** Verifique os logs no Easypanel
2. Copie o erro que aparece
3. Me envie o erro para eu ajudar
4. Enquanto isso, tente fazer restart do container

## Nota Importante

O erro de CORS só vai ser resolvido **DEPOIS** que o backend estiver online. Primeiro precisamos fazer o backend funcionar, depois resolvemos o CORS.

---

**Status:** ⚠️ Backend offline (502)
**Prioridade:** ALTA - Backend precisa estar online primeiro
**Próximo passo:** Verificar logs no Easypanel
