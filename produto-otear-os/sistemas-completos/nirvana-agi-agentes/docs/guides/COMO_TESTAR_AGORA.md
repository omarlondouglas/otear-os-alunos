# Como Testar as Correções Agora

## ⚡ IMPORTANTE: Nova Correção Aplicada

Foi identificado e corrigido um erro adicional:
- ❌ Modelo `gemini-2.0-flash` causando erro 500
- ✅ Alterado para `gemini-1.5-flash` (estável)

**Consulte `FIX_GEMINI_MODEL_ERROR.md` para detalhes**

---

## ⚡ Ação Imediata

Execute estes comandos na ordem:

### 1. Reiniciar os Serviços
```bash
docker-compose restart
```

### 2. Verificar se Redis Está OK
```bash
docker-compose logs redis | tail -20
```

**Esperado:** Sem erros de conexão, deve mostrar "Ready to accept connections"

### 3. Verificar Logs do Gateway
```bash
docker-compose logs gateway | tail -50
```

**Esperado:** 
- Sem erros de "Cannot connect to redis"
- Mensagens de "Celery Broker URL" e "Celery Backend URL"

### 4. Testar via API (Chat Simples)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, como você está?"}'
```

**Esperado:** Resposta JSON com `{"response": "..."}`

### 5. Testar Geração de Carrossel
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Crie um carrossel simples com 2 slides sobre produtividade"}'
```

**Esperado:** 
- Resposta com URLs das imagens
- Logs mostrando `[CAROUSEL TOOL] Iniciando geração...`

### 6. Monitorar Logs em Tempo Real
```bash
docker-compose logs -f gateway | grep -E "\[CAROUSEL TOOL\]|\[VIDEO TOOL\]|ERROR"
```

**Esperado:**
- `[CAROUSEL TOOL] Iniciando geração de X slides`
- `[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso!`
- `[CAROUSEL TOOL] Finalizando execução`

---

## 🔍 O Que Procurar nos Logs

### ✅ Sinais de Sucesso:

```
INFO:     Celery Broker URL: redis://localhost:6379/0
INFO:     Celery Backend URL: redis://localhost:6379/0
[CAROUSEL TOOL] Iniciando geração de 2 slides
[CAROUSEL TOOL] Calling API: https://...
[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso! 2 imagens criadas.
[CAROUSEL TOOL] Finalizando execução
```

### ❌ Sinais de Problema:

```
[ERROR/MainProcess] consumer: Cannot connect to redis://redis:6379/0
ERROR: Timeout waiting for response
ERROR: Tool not found
```

---

## 🧪 Testes Rápidos (Python)

Se preferir testar diretamente no Python:

```python
# Teste 1: Importar ferramentas
from app.agents.agno_tools import generate_carousel_tool
print("✅ Ferramenta importada")

# Teste 2: Validação de schema
result = generate_carousel_tool([{"type": "cover"}])  # Sem title (deve falhar)
print(result)  # Deve retornar erro sobre 'title'

# Teste 3: Importar agentes
from app.agents.agno_agents import orchestrator
print(f"✅ Orchestrator: {orchestrator.name}")

# Teste 4: Teste simples
response = orchestrator.run("Olá!")
print(response.content)
```

---

## 📊 Checklist de Validação

Execute e marque:

- [ ] Redis iniciou sem erros
- [ ] Celery conectou ao Redis
- [ ] Gateway iniciou sem erros
- [ ] API responde a `/api/chat`
- [ ] Logs mostram `[CAROUSEL TOOL]` quando solicitado
- [ ] Carrossel retorna URLs
- [ ] Sem erros de "Cannot connect to redis"
- [ ] Sem erros de "Tool not found"

---

## 🚨 Se Algo Falhar

### Problema: Redis não conecta
```bash
# Verificar se Redis está rodando
docker-compose ps redis

# Reiniciar Redis
docker-compose restart redis

# Verificar logs
docker-compose logs redis
```

### Problema: Agentes não respondem
```bash
# Verificar logs detalhados
docker-compose logs gateway | grep -A 10 -B 10 "ERROR"

# Executar diagnóstico
python diagnose_agents.py
```

### Problema: Ferramentas não são chamadas
```bash
# Verificar se as ferramentas estão registradas
python -c "from app.agents.agno_agents import reviewer; print(reviewer.tools)"

# Deve mostrar: [<function list_fonts_tool>, <function check_carousel_health_tool>, <function generate_carousel_tool>]
```

---

## 📞 Comandos Úteis

```bash
# Ver todos os logs
docker-compose logs

# Ver logs de um serviço específico
docker-compose logs gateway
docker-compose logs redis

# Seguir logs em tempo real
docker-compose logs -f

# Reiniciar um serviço específico
docker-compose restart gateway

# Reconstruir e reiniciar tudo
docker-compose down
docker-compose up --build -d

# Verificar status dos serviços
docker-compose ps

# Entrar no container
docker-compose exec gateway bash
```

---

## ✅ Resultado Esperado Final

Quando tudo estiver funcionando, você deve ver:

1. **Chat simples:** Resposta normal do agente
2. **Pedido de carrossel:** 
   - Logs mostrando `[CAROUSEL TOOL]`
   - Resposta com URLs das imagens
   - Exemplo: `https://otear-carrocel-backend.../api/image/...`
3. **Pedido de vídeo:**
   - Logs mostrando `[VIDEO TOOL]`
   - Resposta com job_id e status
   - Após processamento: URL do vídeo editado

---

**Boa sorte! 🚀**

Se precisar de ajuda, verifique:
- `RESUMO_FINAL_CORRECOES.md` - Documentação completa
- `CORRECOES_APLICADAS.md` - Detalhes técnicos
- `diagnose_agents.py` - Script de diagnóstico
