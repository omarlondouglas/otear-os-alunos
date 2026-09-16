# Correção: Memória e Contexto dos Agentes

## 🔴 Problema Identificado

Os agentes estavam **perdendo contexto** entre mensagens:

### Sintomas:
1. ❌ Vídeo processado com sucesso (logs mostram), mas agente diz "não retornou URL"
2. ❌ Agente diz "tentei mas não consegui" mesmo quando a ferramenta funcionou
3. ❌ Memória não persiste entre mensagens do mesmo usuário
4. ❌ Agentes confusos, não seguem em paralelo

### Logs mostram sucesso:
```
[libx264 @ 0x645e248c97c0] kb/s:2184.71
Task app.workers.video_tasks.process_video_task[...] succeeded in 37.79s
INFO: "GET /static/6d6676b2-37aa-46df-97f2-58be27c0dd4a_final.mp4 HTTP/1.1" 200 OK
```

### Mas agente responde:
```
"O VideoDirectorAgent não retornou nenhum ID (job_id) ou URL"
"O retorno do sistema de edição está vindo vazio"
```

---

## ✅ Soluções Aplicadas

### 1. Session ID por Usuário (`app/api/v1/webhook_router.py`)

**Problema:** Cada mensagem criava uma nova sessão, perdendo contexto.

**Antes:**
```python
# ❌ Sem session_id - cada mensagem é uma nova sessão
response = orchestrator.run(prompt, images=media["images"], videos=videos)
```

**Depois:**
```python
# ✅ Session ID baseado no número do usuário
user_number = remote_jid.split('@')[0]
session_id = f"whatsapp_{user_number}"

response = orchestrator.run(
    prompt, 
    images=media["images"], 
    videos=videos,
    session_id=session_id  # CRÍTICO: Mantém contexto
)
```

**Resultado:** Agora cada usuário tem sua própria sessão persistente!

---

### 2. Prompts Mais Assertivos

#### VideoDirectorAgent

**Adicionado:**
```python
"### FORMATO DA RESPOSTA AO USUÁRIO ###",
"Quando o vídeo estiver pronto, responda EXATAMENTE assim:",
"\"Vídeo editado com sucesso! 🎬",
"",
"Download: [URL_COMPLETA_AQUI]",
"",
"O vídeo foi processado com legendas amarelas e remoção de silêncio (preset VIRAL).\"",
"",
"NUNCA diga que está pronto sem incluir a URL completa na resposta!",
```

#### ReviewerAgent

**Adicionado:**
```python
"### FORMATO DA RESPOSTA AO USUÁRIO ###",
"Quando o carrossel estiver pronto, responda EXATAMENTE assim:",
"\"Carrossel criado com sucesso! 🎨",
"",
"Imagens geradas ({N} slides):",
"1. [URL_SLIDE_1]",
"2. [URL_SLIDE_2]",
"3. [URL_SLIDE_3]",
"",
"Todas as imagens estão prontas para download e uso no Instagram (1080x1350).\"",
"",
"NUNCA diga que está pronto sem incluir as URLs completas na resposta!",
```

#### Orchestrator (Patricia)

**Adicionado:**
```python
"### REGRA CRÍTICA DE MEMÓRIA ###",
"SEMPRE inclua na sua resposta final:",
"1. O que foi solicitado",
"2. O que foi feito (qual agente executou)",
"3. O resultado (URLs completas)",
"4. NUNCA diga 'tentei' ou 'não consegui' - se o agente retornou URLs, VOCÊ TEM AS URLs!",
"",
"### EXEMPLO DE RESPOSTA CORRETA ###",
"Usuário: 'Edita esse vídeo: https://exemplo.com/video.mp4'",
"Você delega para VideoDirectorAgent",
"VideoDirectorAgent retorna: {'download_url': 'https://...'}",
"Você responde: 'Vídeo editado! Download: https://...'",
"",
"NUNCA responda: 'O agente não retornou URL' se o agente retornou!",
"SEMPRE extraia e repasse as URLs que os agentes retornaram!",
```

---

## 🔍 Como Funciona Agora

### Fluxo com Session ID:

```
Mensagem 1 (Usuário 5511999999999):
├─ Session ID: whatsapp_5511999999999
├─ Contexto: Vazio (primeira mensagem)
└─ Resposta salva no contexto

Mensagem 2 (Mesmo usuário):
├─ Session ID: whatsapp_5511999999999
├─ Contexto: Carrega mensagem 1 + resposta 1
└─ Resposta salva no contexto

Mensagem 3 (Mesmo usuário):
├─ Session ID: whatsapp_5511999999999
├─ Contexto: Carrega mensagens 1, 2 + respostas
└─ Agente tem TODA a conversa!
```

### Fluxo de Resposta Assertiva:

```
1. Usuário: "Edita esse vídeo: https://..."
   ↓
2. Orchestrator delega para VideoDirectorAgent
   ↓
3. VideoDirectorAgent chama edit_video_tool()
   ↓
4. Ferramenta retorna: {"download_url": "https://..."}
   ↓
5. VideoDirectorAgent EXTRAI a URL
   ↓
6. VideoDirectorAgent responde: "Vídeo editado! Download: https://..."
   ↓
7. Orchestrator REPASSA a resposta com a URL
   ↓
8. Usuário recebe a URL completa ✅
```

---

## 🧪 Como Testar

### Teste 1: Persistência de Contexto

```
Mensagem 1: "Olá"
Resposta: "Olá! Como posso ajudar?"

Mensagem 2: "Qual foi minha última mensagem?"
Resposta: "Sua última mensagem foi 'Olá'" ✅

# Antes: "Não tenho contexto da conversa anterior" ❌
```

### Teste 2: Vídeo com Contexto

```
Mensagem 1: "Edita esse vídeo: https://exemplo.com/video.mp4"
Resposta: "Processando vídeo..."

Mensagem 2: "Já terminou?"
Resposta: "Sim! Download: https://..." ✅

# Antes: "Não sei de qual vídeo você está falando" ❌
```

### Teste 3: Resposta Assertiva

```
Mensagem: "Edita esse vídeo: https://exemplo.com/video.mp4"

Resposta esperada:
"Vídeo editado com sucesso! 🎬

Download: https://otear-otear-editavideos.qc7qit.easypanel.host/static/abc123_final.mp4

O vídeo foi processado com legendas amarelas e remoção de silêncio (preset VIRAL)."

# Antes: "O agente não retornou URL" ❌
```

---

## 📊 Comparação Antes/Depois

### Antes (❌ Sem Contexto):

```
Usuário: "Edita esse vídeo"
Bot: "Processando..."

[Vídeo processado com sucesso nos logs]

Usuário: "Já terminou?"
Bot: "Não sei de qual vídeo você está falando" ❌

Usuário: "O vídeo que pedi para editar"
Bot: "O agente não retornou URL" ❌ (mas retornou!)
```

### Depois (✅ Com Contexto):

```
Usuário: "Edita esse vídeo"
Bot: "Processando..."

[Vídeo processado com sucesso]

Usuário: "Já terminou?"
Bot: "Sim! Download: https://..." ✅

Usuário: "Obrigado!"
Bot: "De nada! Precisa de mais alguma coisa?" ✅
```

---

## 🔍 Logs para Monitorar

### Webhook com Session ID:
```
[Webhook] Mensagem recebida de 5511999999999@s.whatsapp.net: Edita esse vídeo
[Webhook] Session ID: whatsapp_5511999999999
[Webhook] Prompt: Edita esse vídeo...
[Webhook] Resposta do Orchestrator (250 chars): Vídeo editado! Download: https://...
[Webhook] Resposta enviada para 5511999999999@s.whatsapp.net
```

### Agente com Resposta Assertiva:
```
[VIDEO TOOL] ✓ Job abc123 COMPLETO! URL: https://...
[Agent] VideoDirectorAgent: Vídeo editado! Download: https://...
[Orchestrator] Repassando resposta com URL para usuário
```

---

## ⚙️ Configuração

### PostgreSQL (Já configurado):
```python
agent_storage = PostgresDb(
    session_table="agno_sessions",
    db_url=DATABASE_URL
)
```

### Agentes (Já configurado):
```python
video_director = Agent(
    ...
    db=agent_storage,  # ✅ Usa banco para persistir
    add_history_to_context=True,  # ✅ Adiciona histórico
    ...
)
```

---

## 📝 Resumo

**Problema 1:** Sem session_id → Cada mensagem era nova sessão
**Solução 1:** Session ID baseado no número do usuário

**Problema 2:** Agente dizia "não retornou" mesmo quando retornou
**Solução 2:** Prompts mais assertivos com formato de resposta obrigatório

**Problema 3:** Memória não persistia
**Solução 3:** PostgreSQL + session_id + add_history_to_context

**Resultado:** Agentes agora mantêm contexto e retornam URLs corretamente!

---

## 🎯 Impacto

### Antes:
- ❌ Cada mensagem era uma nova conversa
- ❌ Agente esquecia o que foi pedido
- ❌ Dizia "não consegui" mesmo quando conseguiu
- ❌ Usuário frustrado

### Depois:
- ✅ Conversa contínua com contexto
- ✅ Agente lembra de tudo
- ✅ Retorna URLs corretamente
- ✅ Usuário satisfeito

---

**Data:** 2025-02-09
**Arquivos modificados:** 
- `app/api/v1/webhook_router.py` (session_id)
- `app/agents/agno_agents.py` (prompts assertivos)

**Status:** ✅ CORRIGIDO E TESTADO
