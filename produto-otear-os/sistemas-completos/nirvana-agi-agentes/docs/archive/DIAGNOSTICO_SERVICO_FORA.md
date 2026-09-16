# 🚨 DIAGNÓSTICO: SERVIÇO FORA DO AR

## ❌ PROBLEMA REAL IDENTIFICADO:

**NÃO É CORS!** O serviço está retornando **502 Bad Gateway**:
```
Status: 502
Service is not reachable
Make sure the service is running and healthy.
```

Isso significa que:
- ✅ O proxy/load balancer está funcionando
- ❌ O backend (container) está fora do ar ou não responde
- ❌ O serviço não está rodando na porta esperada

---

## 🔍 DIAGNÓSTICO IMEDIATO:

### **1. VERIFICAR STATUS DOS CONTAINERS:**
```bash
docker-compose ps
```
**Esperado:** Todos os serviços com status "Up"

### **2. VERIFICAR LOGS DO GATEWAY:**
```bash
docker-compose logs gateway --tail=50
```
**Procurar por:** Erros de inicialização, crashes, problemas de importação

### **3. VERIFICAR SE O SERVIÇO ESTÁ RODANDO:**
```bash
docker-compose logs gateway | grep -i "starting\|running\|error"
```

### **4. VERIFICAR PORTA E BIND:**
```bash
docker-compose exec gateway netstat -tlnp | grep 8000
```
**Esperado:** Porta 8000 em LISTEN

---

## 🚀 AÇÕES CORRETIVAS:

### **1. REINICIAR TODOS OS SERVIÇOS:**
```bash
docker-compose down
docker-compose up -d
```

### **2. VERIFICAR LOGS EM TEMPO REAL:**
```bash
docker-compose logs -f gateway
```
**Procurar por:** Mensagens de inicialização, erros de importação

### **3. SE O CONTAINER NÃO SUBIR:**
```bash
# Reconstruir a imagem
docker-compose build gateway

# Subir novamente
docker-compose up -d gateway
```

### **4. TESTE LOCAL (DENTRO DO CONTAINER):**
```bash
# Entrar no container
docker-compose exec gateway bash

# Testar localmente
curl http://localhost:8000/api/health

# Verificar processo
ps aux | grep python
```

---

## 🔧 POSSÍVEIS CAUSAS:

### **1. Erro de Importação Python:**
- Dependências faltando
- Erro de sintaxe no código
- Módulos não encontrados

### **2. Erro de Configuração:**
- Variáveis de ambiente incorretas
- Banco de dados não conecta
- Redis não conecta

### **3. Erro de Porta:**
- Porta 8000 já em uso
- Bind incorreto (0.0.0.0 vs 127.0.0.1)

### **4. Erro de Dependências:**
- Pacotes Python não instalados
- Versões incompatíveis

---

## 📊 COMANDOS DE DIAGNÓSTICO:

### **Verificar se o processo está rodando:**
```bash
docker-compose exec gateway ps aux | grep python
```

### **Verificar portas abertas:**
```bash
docker-compose exec gateway netstat -tlnp
```

### **Testar importações Python:**
```bash
docker-compose exec gateway python -c "from app.agents.agno_agents import orchestrator; print('OK')"
```

### **Verificar variáveis de ambiente:**
```bash
docker-compose exec gateway env | grep -E "PORT|HOST|DATABASE_URL"
```

### **Testar inicialização manual:**
```bash
docker-compose exec gateway python api_gateway.py
```

---

## 🎯 TESTE DE VALIDAÇÃO:

Após corrigir, teste:

### **1. Container está rodando:**
```bash
docker-compose ps gateway
```
**Esperado:** Status "Up"

### **2. Serviço responde localmente:**
```bash
docker-compose exec gateway curl http://localhost:8000/api/health
```
**Esperado:** JSON com status

### **3. Serviço responde externamente:**
```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/api/health
```
**Esperado:** JSON (não HTML de erro 502)

---

## 🚨 SOLUÇÃO RÁPIDA:

Se o problema persistir, execute na ordem:

```bash
# 1. Parar tudo
docker-compose down

# 2. Limpar containers antigos
docker-compose rm -f

# 3. Reconstruir imagens
docker-compose build --no-cache

# 4. Subir novamente
docker-compose up -d

# 5. Verificar logs
docker-compose logs -f gateway
```

---

## 📞 COMANDOS PARA DEBUG:

```bash
# Ver todos os logs
docker-compose logs

# Ver logs específicos do gateway
docker-compose logs gateway

# Ver logs em tempo real
docker-compose logs -f gateway

# Verificar status de todos os serviços
docker-compose ps

# Entrar no container para debug
docker-compose exec gateway bash

# Verificar se o arquivo existe
docker-compose exec gateway ls -la api_gateway.py

# Testar importações
docker-compose exec gateway python -c "import fastapi; print('FastAPI OK')"
```

---

## 🎯 RESULTADO ESPERADO:

Após corrigir o problema:
- ✅ `docker-compose ps` mostra gateway como "Up"
- ✅ `curl .../api/health` retorna JSON (não HTML)
- ✅ Logs mostram "Starting Orchestrator on port 8000..."
- ✅ Frontend consegue se conectar sem erro 502

**O problema é infraestrutura, não CORS!** 🔧