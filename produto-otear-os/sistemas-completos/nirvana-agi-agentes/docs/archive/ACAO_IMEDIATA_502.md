# 🚨 AÇÃO IMEDIATA - ERRO 502

## ❌ PROBLEMA:
```
Status: 502 Bad Gateway
Service is not reachable
```

**ISSO NÃO É CORS!** O backend está fora do ar.

---

## ⚡ AÇÃO IMEDIATA (Execute na ordem):

### **1. REINICIAR TUDO:**
```bash
docker-compose down
docker-compose up -d
```

### **2. VERIFICAR STATUS:**
```bash
docker-compose ps
```
**Esperado:** Gateway com status "Up"

### **3. VERIFICAR LOGS:**
```bash
docker-compose logs gateway --tail=50
```
**Procurar por:** Erros, crashes, problemas de importação

### **4. TESTAR LOCALMENTE:**
```bash
docker-compose exec gateway curl http://localhost:8000/api/health
```
**Esperado:** JSON (não erro)

### **5. SE AINDA NÃO FUNCIONAR:**
```bash
# Reconstruir imagem
docker-compose build --no-cache gateway

# Subir novamente
docker-compose up -d gateway

# Ver logs em tempo real
docker-compose logs -f gateway
```

---

## 🔍 DIAGNÓSTICO RÁPIDO:

Execute este comando para diagnóstico automático:
```bash
python diagnose_service.py
```

Ou manualmente:

### **Verificar se container está rodando:**
```bash
docker-compose ps gateway
```

### **Verificar logs de erro:**
```bash
docker-compose logs gateway | grep -i error
```

### **Verificar se processo Python está ativo:**
```bash
docker-compose exec gateway ps aux | grep python
```

### **Testar importações:**
```bash
docker-compose exec gateway python -c "from app.agents.agno_agents import orchestrator; print('OK')"
```

---

## 🎯 POSSÍVEIS CAUSAS:

### **1. Erro de Importação:**
- Dependências Python faltando
- Erro de sintaxe no código
- Módulos não encontrados

### **2. Erro de Configuração:**
- Variáveis de ambiente incorretas
- Banco de dados não conecta
- API keys inválidas

### **3. Erro de Porta:**
- Porta 8000 não está sendo usada
- Processo não está fazendo bind correto

### **4. Container não iniciou:**
- Dockerfile com problema
- Dependências não instaladas
- Erro na inicialização

---

## ✅ VALIDAÇÃO DE SUCESSO:

Após corrigir, você deve ver:

### **1. Container rodando:**
```bash
docker-compose ps gateway
# Resultado: gateway ... Up
```

### **2. Logs sem erro:**
```bash
docker-compose logs gateway --tail=10
# Resultado: "Starting Orchestrator on port 8000..."
```

### **3. Endpoint respondendo:**
```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/api/health
# Resultado: {"status": "healthy"} (não HTML de erro)
```

### **4. Frontend funcionando:**
- Console do browser sem erro 502
- Requests sendo processados normalmente

---

## 🚨 SE NADA FUNCIONAR:

### **Debug completo:**
```bash
# Entrar no container
docker-compose exec gateway bash

# Verificar arquivos
ls -la

# Testar inicialização manual
python api_gateway.py

# Ver o que está acontecendo
tail -f /var/log/*.log
```

### **Reconstruir do zero:**
```bash
# Parar tudo
docker-compose down

# Remover containers
docker-compose rm -f

# Remover imagens
docker-compose rmi $(docker-compose config --services)

# Reconstruir tudo
docker-compose build --no-cache

# Subir novamente
docker-compose up -d
```

---

## 📞 COMANDOS ÚTEIS:

```bash
# Status dos serviços
docker-compose ps

# Logs em tempo real
docker-compose logs -f gateway

# Entrar no container
docker-compose exec gateway bash

# Reiniciar só o gateway
docker-compose restart gateway

# Ver uso de recursos
docker stats

# Verificar rede
docker network ls
```

---

## 🎯 RESULTADO ESPERADO:

Após corrigir:
- ✅ `docker-compose ps` mostra gateway "Up"
- ✅ Logs mostram "Starting Orchestrator on port 8000..."
- ✅ `curl .../api/health` retorna JSON
- ✅ Frontend conecta sem erro 502
- ✅ Chat funciona normalmente

**FOQUE NO BACKEND PRIMEIRO, CORS DEPOIS!** 🔧