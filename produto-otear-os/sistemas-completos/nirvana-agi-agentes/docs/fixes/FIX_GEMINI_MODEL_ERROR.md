# Fix: Erro 500 do Gemini API

## 🔴 Problema

```
ERROR: Error from Gemini API: 500 INTERNAL. 
{'error': {'code': 500, 'message':'Internal error encountered.', 'status': 'INTERNAL'}}
```

O log mostra que está tentando usar o modelo `gemini-3-pro-preview`, que não existe ou não está disponível.

## 🔍 Causa Raiz

O modelo configurado era `gemini-2.0-flash`, mas:

1. **Modelo pode não estar disponível:** O `gemini-2.0-flash` pode ser experimental ou não estar disponível na sua região
2. **Nome incorreto:** O Agno pode estar traduzindo o nome do modelo incorretamente
3. **API instável:** Modelos experimentais podem ter instabilidade

## ✅ Correção Aplicada

### 1. Atualizado `.env`

**ANTES:**
```env
MODEL_PLANNER=gemini-2.0-flash
MODEL_WRITER=gemini-2.0-flash
MODEL_FAST=gemini-2.0-flash
MODEL_IMAGE=gemini-2.0-flash
```

**DEPOIS:**
```env
# Modelos Gemini disponíveis:
# - gemini-2.0-flash-exp (experimental, pode ter instabilidade)
# - gemini-1.5-flash (estável, RECOMENDADO)
# - gemini-1.5-pro (mais poderoso, mais lento)
MODEL_PLANNER=gemini-1.5-flash
MODEL_WRITER=gemini-1.5-flash
MODEL_FAST=gemini-1.5-flash
MODEL_IMAGE=gemini-1.5-flash
```

### 2. Atualizado `app/agents/agno_agents.py`

**ANTES:**
```python
MODEL_PLANNER = os.getenv("MODEL_PLANNER", "gemini-2.0-flash")
MODEL_WRITER = os.getenv("MODEL_WRITER", "gemini-2.0-flash")
MODEL_FAST = os.getenv("MODEL_FAST", "gemini-2.0-flash")
```

**DEPOIS:**
```python
# Modelos Gemini disponíveis:
# - gemini-2.0-flash-exp (experimental, mais recente)
# - gemini-1.5-flash (estável, recomendado)
# - gemini-1.5-pro (mais poderoso)
MODEL_PLANNER = os.getenv("MODEL_PLANNER", "gemini-1.5-flash")
MODEL_WRITER = os.getenv("MODEL_WRITER", "gemini-1.5-flash")
MODEL_FAST = os.getenv("MODEL_FAST", "gemini-1.5-flash")
```

## 📊 Modelos Gemini Disponíveis

| Modelo | Status | Velocidade | Qualidade | Recomendação |
|--------|--------|------------|-----------|--------------|
| `gemini-1.5-flash` | ✅ Estável | Rápido | Boa | **RECOMENDADO** |
| `gemini-1.5-pro` | ✅ Estável | Médio | Excelente | Para tarefas complexas |
| `gemini-2.0-flash-exp` | ⚠️ Experimental | Muito rápido | Boa | Pode ter instabilidade |
| `gemini-1.0-pro` | ⚠️ Legado | Lento | Boa | Não recomendado |

## 🧪 Como Testar

### 1. Reiniciar os Serviços
```bash
docker-compose restart
```

### 2. Testar via API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, como você está?"}'
```

**Esperado:** Resposta sem erro 500

### 3. Verificar Logs
```bash
docker-compose logs gateway | grep -E "gemini|ERROR"
```

**Esperado:** 
- Sem erros 500
- Logs mostrando `gemini-1.5-flash` sendo usado

### 4. Testar Carrossel
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Crie um carrossel de 3 páginas sobre meus valores"}'
```

**Esperado:** Resposta com URLs das imagens

## 🔧 Alternativas

Se `gemini-1.5-flash` também der erro, tente:

### Opção 1: Usar Gemini 1.5 Pro (mais estável, mas mais lento)
```env
MODEL_PLANNER=gemini-1.5-pro
MODEL_WRITER=gemini-1.5-pro
MODEL_FAST=gemini-1.5-flash
```

### Opção 2: Usar OpenAI (se tiver créditos)
```env
LLM_PROVIDER=openai
MODEL_PLANNER=gpt-4o-mini
MODEL_WRITER=gpt-4o-mini
MODEL_FAST=gpt-4o-mini
```

### Opção 3: Testar Gemini 2.0 Experimental
```env
MODEL_PLANNER=gemini-2.0-flash-exp
MODEL_WRITER=gemini-2.0-flash-exp
MODEL_FAST=gemini-2.0-flash-exp
```

## 📝 Notas Importantes

1. **Gemini 1.5 Flash é o mais estável** para produção
2. **Gemini 2.0 é experimental** e pode ter instabilidade
3. **Sempre use modelos estáveis em produção**
4. **Verifique a disponibilidade regional** dos modelos

## 🚨 Troubleshooting

### Erro persiste após mudança?

1. **Limpar cache do Docker:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

2. **Verificar API Key:**
   ```bash
   echo $GOOGLE_API_KEY
   ```

3. **Testar API Key diretamente:**
   ```bash
   curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
   ```

4. **Verificar quota da API:**
   - Acesse: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
   - Verifique se não excedeu o limite

## ✅ Checklist

- [x] Atualizado modelo no `.env` para `gemini-1.5-flash`
- [x] Atualizado fallback no `agno_agents.py`
- [x] Adicionado comentários sobre modelos disponíveis
- [ ] Reiniciado serviços
- [ ] Testado via API
- [ ] Verificado logs sem erro 500
- [ ] Testado geração de carrossel

## 🎯 Resultado Esperado

Após reiniciar os serviços:

```
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent "HTTP/1.1 200 OK"
```

Sem erros 500, e o agente respondendo normalmente.

---

**Data:** 2026-02-11  
**Status:** ✅ Correção Aplicada - Aguardando Reinício
