# Fix: Nome Correto do Modelo Gemini 2.0

## 🔴 Problema Original

O erro 500 estava acontecendo porque o nome do modelo estava incorreto:

```
❌ gemini-2.0-flash (INCORRETO - não existe)
❌ gemini-3-pro-preview (nome que o Agno estava tentando usar)
```

## ✅ Solução

O nome correto do modelo Gemini 2.0 Flash é:

```
✅ gemini-2.0-flash-exp (CORRETO - com sufixo -exp)
```

## 📝 Correção Aplicada

### `.env`
```env
# ANTES (INCORRETO)
MODEL_PLANNER=gemini-2.0-flash
MODEL_WRITER=gemini-2.0-flash
MODEL_FAST=gemini-2.0-flash

# DEPOIS (CORRETO)
MODEL_PLANNER=gemini-2.0-flash-exp
MODEL_WRITER=gemini-2.0-flash-exp
MODEL_FAST=gemini-2.0-flash-exp
```

### `app/agents/agno_agents.py`
```python
# ANTES (INCORRETO)
MODEL_PLANNER = os.getenv("MODEL_PLANNER", "gemini-2.0-flash")

# DEPOIS (CORRETO)
MODEL_PLANNER = os.getenv("MODEL_PLANNER", "gemini-2.0-flash-exp")
```

## 📊 Modelos Gemini Disponíveis

| Nome no Código | Nome Real na API | Status |
|----------------|------------------|--------|
| `gemini-2.0-flash-exp` | Gemini 2.0 Flash (Experimental) | ✅ Disponível |
| `gemini-1.5-flash` | Gemini 1.5 Flash | ✅ Estável |
| `gemini-1.5-pro` | Gemini 1.5 Pro | ✅ Estável |
| ~~`gemini-2.0-flash`~~ | N/A | ❌ Não existe |

## 🎯 Por Que o Sufixo `-exp`?

O sufixo `-exp` indica que é uma versão **experimental** do modelo:
- Mais recente e rápido
- Pode ter instabilidades ocasionais
- Recursos mais avançados
- Recomendado para desenvolvimento/teste

## 🧪 Como Testar

### 1. Reiniciar Serviços
```bash
docker-compose restart
```

### 2. Verificar Logs
```bash
docker-compose logs gateway | grep "gemini"
```

**Esperado:**
```
INFO:httpx:HTTP Request: POST .../gemini-2.0-flash-exp:generateContent "HTTP/1.1 200 OK"
```

### 3. Testar Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá!"}'
```

**Esperado:** Resposta sem erro 500

## ⚠️ Nota Importante

O modelo `gemini-2.0-flash-exp` é experimental, então:
- ✅ Use para desenvolvimento e teste
- ⚠️ Pode ter instabilidades ocasionais
- ⚠️ Para produção, considere `gemini-1.5-flash` (mais estável)

## 🔄 Alternativas (Se Ainda Der Erro)

Se o `gemini-2.0-flash-exp` ainda der erro 500:

### Opção 1: Gemini 1.5 Flash (Mais Estável)
```env
MODEL_PLANNER=gemini-1.5-flash
MODEL_WRITER=gemini-1.5-flash
MODEL_FAST=gemini-1.5-flash
```

### Opção 2: Gemini 1.5 Pro (Mais Poderoso)
```env
MODEL_PLANNER=gemini-1.5-pro
MODEL_WRITER=gemini-1.5-pro
MODEL_FAST=gemini-1.5-flash
```

### Opção 3: Verificar Disponibilidade Regional
Alguns modelos podem não estar disponíveis em todas as regiões. Teste com:

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

## ✅ Checklist

- [x] Corrigido nome do modelo no `.env` (adicionado `-exp`)
- [x] Corrigido fallback no `agno_agents.py`
- [ ] Reiniciado serviços
- [ ] Testado via API
- [ ] Verificado logs sem erro 500

---

**Resumo:** O problema era simplesmente o nome do modelo. O correto é `gemini-2.0-flash-exp` (com `-exp` no final), não `gemini-2.0-flash`.
