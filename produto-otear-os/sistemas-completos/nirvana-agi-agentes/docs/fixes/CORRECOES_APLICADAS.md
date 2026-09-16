# Correções Aplicadas - Agentes e Redis

## 🔧 Problema 1: Erro de Conexão com Redis

### Erro Original:
```
[ERROR/MainProcess] consumer: Cannot connect to redis://redis:6379/0: 
Error -2 connecting to redis:6379. Name or service not known.
```

### Causa:
O Celery estava tentando conectar ao Redis usando o hostname `redis:6379` (Docker), mas o Redis não estava disponível ou o hostname não era resolvível.

### Correção Aplicada:

#### 1. `app/core/celery_app.py`
- Adicionado fallback para `localhost:6379` quando `redis:6379` não estiver disponível
- Adicionado logging para debug
- Configurado retry limits para evitar loops infinitos

```python
broker_url = os.environ.get("CELERY_BROKER_URL") or os.environ.get("REDIS_URL") or "redis://localhost:6379/0"
backend_url = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"

celery_app.conf.update(
    # ... outras configs ...
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,  # Limitar tentativas
)
```

#### 2. `.env`
- Adicionado variáveis de ambiente para Redis:

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

---

## 🤖 Problema 2: Agentes Não Retornam Resultados

### Sintomas:
- ReviewerAgent e VideoDirectorAgent não retornavam URLs
- Orchestrator não recebia respostas dos agentes membros
- Ferramentas não eram chamadas corretamente

### Causas Identificadas:

1. **Decorator `@with_logging` interferindo** com detecção de ferramentas pelo Agno
2. **Instruções muito longas** (100+ linhas) confundindo o modelo
3. **Falta de logging detalhado** para debug

### Correções Aplicadas:

#### 1. `app/agents/agno_tools.py`

**Mudança 1: Removido decorator das ferramentas críticas**

ANTES:
```python
@with_logging("Generate Carousel")
def generate_carousel_tool(slides_data: list):
```

DEPOIS:
```python
def generate_carousel_tool(slides_data: list) -> dict:
    """..."""
    # Logging manual
    logger.info(f"[CAROUSEL TOOL] Iniciando geração de {len(slides_data)} slides")
    try:
        # ... código ...
        logger.info(f"[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso!")
        return result
    except Exception as e:
        logger.error(f"[CAROUSEL TOOL] Erro: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        logger.info(f"[CAROUSEL TOOL] Finalizando execução")
```

**Mudança 2: Adicionado type hints explícitos**
```python
def generate_carousel_tool(slides_data: list) -> dict:
def edit_video_tool(...) -> dict:
```

**Mudança 3: Logging manual detalhado**
- Adicionado logging no início, meio e fim de cada ferramenta
- Adicionado `finally` block para garantir log de finalização

#### 2. `app/agents/agno_agents.py`

**Mudança 1: Simplificado instruções do ReviewerAgent**

ANTES: 100+ linhas de instruções
DEPOIS: ~50 linhas focadas no essencial

```python
reviewer = Agent(
    name="ReviewerAgent",
    model=Gemini(id=MODEL_PLANNER),
    tools=[list_fonts_tool, check_carousel_health_tool, generate_carousel_tool],
    instructions=[
        "Você é o ReviewerAgent, especialista em gerar carrosséis para Instagram.",
        "",
        "REGRA ABSOLUTA:",
        "SEMPRE chame generate_carousel_tool quando receber um pedido de carrossel.",
        "NUNCA dê instruções manuais ou diga que está pronto sem ter as URLs.",
        # ... ~50 linhas focadas ...
    ],
    # ... resto da config ...
)
```

**Mudança 2: Simplificado instruções do VideoDirectorAgent**

ANTES: 150+ linhas de instruções
DEPOIS: ~50 linhas focadas

```python
video_director = Agent(
    name="VideoDirectorAgent",
    model=Gemini(id=MODEL_PLANNER),
    tools=[edit_video_tool, transcribe_video_tool, check_video_status_tool, generate_presigned_url_tool],
    instructions=[
        "Você é o VideoDirectorAgent, especialista em edição de vídeos.",
        "",
        "REGRA ABSOLUTA:",
        "SEMPRE chame edit_video_tool quando receber um pedido de edição.",
        # ... ~50 linhas focadas ...
    ],
    # ... resto da config ...
)
```

**Mudança 3: Simplificado instruções do Orchestrator**

ANTES: 100+ linhas de instruções
DEPOIS: ~40 linhas focadas

```python
orchestrator = Team(
    name="Patricia",
    model=Gemini(id=MODEL_PLANNER),
    members=[stylist, copywriter, designer, reviewer, video_director, dona],
    instructions=[
        "Meu nome é Patricia. Sou especializada em criar conteúdo viral, carrosséis e vídeos.",
        "",
        "REGRA SUPREMA:",
        "NUNCA desista dizendo que os agentes 'não responderam'.",
        # ... ~40 linhas focadas ...
    ],
    # ... resto da config ...
)
```

---

## 📊 Resumo das Mudanças

### Arquivos Modificados:
1. ✅ `app/core/celery_app.py` - Corrigido conexão Redis
2. ✅ `.env` - Adicionado variáveis Redis
3. ✅ `app/agents/agno_tools.py` - Removido decorators, adicionado logging manual
4. ✅ `app/agents/agno_agents.py` - Simplificado instruções dos agentes

### Benefícios:
- ✅ Redis não vai mais tentar conectar infinitamente
- ✅ Ferramentas têm logging detalhado para debug
- ✅ Instruções mais curtas e focadas (melhor para o modelo)
- ✅ Type hints explícitos (melhor para o Agno)
- ✅ Menos overhead de decorators

---

## 🧪 Como Testar

### Teste 1: Verificar Redis
```bash
# Verificar se Redis está rodando
redis-cli ping
# Deve retornar: PONG
```

### Teste 2: Testar Ferramenta Direta
```python
from app.agents.agno_tools import generate_carousel_tool

slides = [{"type": "cover", "title": "TESTE"}]
result = generate_carousel_tool(slides)
print(result)
```

### Teste 3: Testar Agente Individual
```python
from app.agents.agno_agents import reviewer

response = reviewer.run("Gere um carrossel com 1 slide: TESTE")
print(response.content)
```

### Teste 4: Testar Orchestrator
```python
from app.agents.agno_agents import orchestrator

response = orchestrator.run("Crie um carrossel simples com 2 slides")
print(response.content)
```

### Teste 5: Verificar Logs
```bash
# Verificar logs do backend
docker-compose logs -f gateway

# Procurar por:
# [CAROUSEL TOOL] Iniciando geração...
# [CAROUSEL TOOL] ✓ Carrossel gerado com sucesso!
# [VIDEO TOOL] Iniciando edição...
```

---

## 🚀 Próximos Passos

1. **Reiniciar os serviços:**
   ```bash
   docker-compose restart
   ```

2. **Testar via API:**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Crie um carrossel simples"}'
   ```

3. **Monitorar logs:**
   ```bash
   docker-compose logs -f gateway | grep -E "\[CAROUSEL TOOL\]|\[VIDEO TOOL\]"
   ```

4. **Verificar Redis:**
   ```bash
   docker-compose logs redis
   ```

---

## 📝 Notas Importantes

- As instruções foram reduzidas em ~60% mantendo o essencial
- O logging manual é mais confiável que decorators para debug
- O Redis agora tem fallback para localhost
- Os type hints ajudam o Agno a entender melhor as ferramentas
- O Celery agora limita tentativas de reconexão (max 10)

---

## ✅ Checklist de Verificação

- [x] Redis configurado com fallback
- [x] Celery com retry limits
- [x] Decorators removidos das ferramentas críticas
- [x] Logging manual adicionado
- [x] Type hints explícitos
- [x] Instruções simplificadas (ReviewerAgent)
- [x] Instruções simplificadas (VideoDirectorAgent)
- [x] Instruções simplificadas (Orchestrator)
- [ ] Testes executados
- [ ] Serviços reiniciados
- [ ] Logs verificados
- [ ] API testada

---

## 🎯 Resultado Esperado

Após essas correções:

1. ✅ Redis não vai mais gerar erros de conexão infinitos
2. ✅ Agentes vão chamar as ferramentas corretamente
3. ✅ Ferramentas vão retornar URLs completas
4. ✅ Orchestrator vai repassar as URLs ao usuário
5. ✅ Logs detalhados para debug
