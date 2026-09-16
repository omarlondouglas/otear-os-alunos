# Guia: Implementar Session ID no Frontend

## 🎯 Objetivo

Manter o contexto da conversa quando o usuário usa a interface web (não WhatsApp).

---

## 🔴 Problema

**Antes:** Cada mensagem criava uma nova sessão, perdendo o contexto.

```javascript
// ❌ Sem session_id
fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "Olá"
  })
})

// Próxima mensagem perde o contexto
fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "Qual foi minha última mensagem?"
  })
})
// Resposta: "Não tenho contexto" ❌
```

---

## ✅ Solução

### 1. Gerar Session ID no Frontend

```javascript
// Gerar um session_id único por usuário/sessão
function getOrCreateSessionId() {
  // Verificar se já existe no localStorage
  let sessionId = localStorage.getItem('chat_session_id');
  
  if (!sessionId) {
    // Gerar novo UUID
    sessionId = 'web_' + crypto.randomUUID();
    localStorage.setItem('chat_session_id', sessionId);
  }
  
  return sessionId;
}
```

### 2. Enviar Session ID nas Requisições

```javascript
// Incluir session_id no contexto
const sessionId = getOrCreateSessionId();

fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: "Olá",
    context: {
      session_id: sessionId  // ✅ Mantém contexto!
    }
  })
})
```

### 3. Exemplo Completo (React/TypeScript)

```typescript
// hooks/useChat.ts
import { useState, useEffect } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Inicializar session_id
  useEffect(() => {
    let sid = localStorage.getItem('chat_session_id');
    if (!sid) {
      sid = 'web_' + crypto.randomUUID();
      localStorage.setItem('chat_session_id', sid);
    }
    setSessionId(sid);
  }, []);

  const sendMessage = async (message: string) => {
    // Adicionar mensagem do usuário
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          context: {
            session_id: sessionId  // ✅ Mantém contexto
          }
        })
      });

      const data = await response.json();
      
      // Adicionar resposta do assistente
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response 
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearSession = () => {
    // Limpar sessão (nova conversa)
    const newSessionId = 'web_' + crypto.randomUUID();
    localStorage.setItem('chat_session_id', newSessionId);
    setSessionId(newSessionId);
    setMessages([]);
  };

  return { messages, sendMessage, clearSession, isLoading };
}
```

### 4. Exemplo de Componente

```typescript
// components/Chat.tsx
import { useChat } from '../hooks/useChat';

export function Chat() {
  const { messages, sendMessage, clearSession, isLoading } = useChat();
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Chat com Patricia</h2>
        <button onClick={clearSession}>Nova Conversa</button>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {isLoading && <div className="loading">Pensando...</div>}
      </div>

      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua mensagem..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Enviar
        </button>
      </form>
    </div>
  );
}
```

---

## 🔄 Fluxo Completo

### Primeira Mensagem:
```
1. Frontend gera session_id: "web_abc123"
2. Salva no localStorage
3. Envia: { message: "Olá", context: { session_id: "web_abc123" } }
4. Backend cria nova sessão com ID "web_abc123"
5. Resposta: "Olá! Como posso ajudar?"
```

### Segunda Mensagem (Mesmo Usuário):
```
1. Frontend recupera session_id do localStorage: "web_abc123"
2. Envia: { message: "Qual foi minha última mensagem?", context: { session_id: "web_abc123" } }
3. Backend carrega contexto da sessão "web_abc123"
4. Resposta: "Sua última mensagem foi 'Olá'" ✅
```

### Nova Conversa:
```
1. Usuário clica em "Nova Conversa"
2. Frontend gera novo session_id: "web_xyz789"
3. Salva no localStorage (substitui o anterior)
4. Próximas mensagens usam "web_xyz789"
5. Contexto anterior não é carregado ✅
```

---

## 📱 Alternativas para Session ID

### Opção 1: UUID (Recomendado)
```javascript
const sessionId = 'web_' + crypto.randomUUID();
// Exemplo: "web_550e8400-e29b-41d4-a716-446655440000"
```

### Opção 2: Timestamp + Random
```javascript
const sessionId = 'web_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
// Exemplo: "web_1707849600000_k3j5h2g9d"
```

### Opção 3: User ID (Se tiver autenticação)
```javascript
const sessionId = 'web_user_' + userId;
// Exemplo: "web_user_12345"
```

---

## 🧪 Como Testar

### Teste 1: Contexto Persistente
```javascript
// Mensagem 1
await sendMessage("Meu nome é João");
// Resposta: "Olá João! Como posso ajudar?"

// Mensagem 2
await sendMessage("Qual é meu nome?");
// Resposta: "Seu nome é João" ✅
```

### Teste 2: Nova Conversa
```javascript
// Conversa 1
await sendMessage("Meu nome é João");
clearSession(); // Nova conversa

// Conversa 2
await sendMessage("Qual é meu nome?");
// Resposta: "Não sei seu nome ainda" ✅
```

### Teste 3: Múltiplas Abas
```javascript
// Aba 1: session_id = "web_abc123"
// Aba 2: session_id = "web_abc123" (mesmo localStorage)
// Ambas compartilham o contexto ✅

// Para contextos separados por aba:
const sessionId = 'web_' + crypto.randomUUID() + '_' + Date.now();
sessionStorage.setItem('chat_session_id', sessionId); // sessionStorage em vez de localStorage
```

---

## 🔍 Verificar no Backend

### Logs:
```
DEBUG: Session ID: web_abc123
DEBUG: Calling orchestrator.run() with session_id=web_abc123
```

### Resposta da API:
```json
{
  "response": "Olá! Como posso ajudar?",
  "data": {
    "session_id": "web_abc123"
  }
}
```

---

## ⚠️ Importante

### 1. Privacidade
- Session ID não deve conter informações sensíveis
- Use UUID aleatório, não user_id diretamente

### 2. Expiração
- Considere limpar sessões antigas do localStorage
- Exemplo: Limpar após 24h de inatividade

```javascript
function getOrCreateSessionId() {
  const stored = localStorage.getItem('chat_session_data');
  
  if (stored) {
    const data = JSON.parse(stored);
    const age = Date.now() - data.timestamp;
    
    // Se mais de 24h, criar nova sessão
    if (age < 24 * 60 * 60 * 1000) {
      return data.sessionId;
    }
  }
  
  // Criar nova sessão
  const sessionId = 'web_' + crypto.randomUUID();
  localStorage.setItem('chat_session_data', JSON.stringify({
    sessionId,
    timestamp: Date.now()
  }));
  
  return sessionId;
}
```

### 3. Múltiplos Usuários
- Se múltiplos usuários usam o mesmo dispositivo
- Considere limpar sessão ao fazer logout

```javascript
function logout() {
  localStorage.removeItem('chat_session_id');
  localStorage.removeItem('chat_session_data');
}
```

---

## 📊 Comparação

### Sem Session ID:
```
Mensagem 1: "Olá" → Nova sessão
Mensagem 2: "Qual foi minha última mensagem?" → Nova sessão (perdeu contexto)
Resposta: "Não tenho contexto" ❌
```

### Com Session ID:
```
Mensagem 1: "Olá" → Sessão "web_abc123"
Mensagem 2: "Qual foi minha última mensagem?" → Sessão "web_abc123" (mesmo contexto)
Resposta: "Sua última mensagem foi 'Olá'" ✅
```

---

## 🚀 Implementação Rápida

### Vanilla JavaScript:
```javascript
// No início do seu app
let sessionId = localStorage.getItem('chat_session_id');
if (!sessionId) {
  sessionId = 'web_' + crypto.randomUUID();
  localStorage.setItem('chat_session_id', sessionId);
}

// Em cada requisição
fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userMessage,
    context: { session_id: sessionId }
  })
});
```

---

**Status:** ✅ Backend pronto para receber session_id
**Próximo passo:** Implementar no frontend conforme este guia
