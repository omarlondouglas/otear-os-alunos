# Configurar CORS no Easypanel

## Problema

O erro de CORS persiste mesmo após configurar no código. Isso indica que o **proxy reverso do Easypanel** está bloqueando os headers CORS.

## Solução: Configurar CORS no Easypanel

### Opção 1: Via Interface do Easypanel

1. **Acesse o Easypanel**
   - URL: `https://easypanel.qc7qit.easypanel.host` (ou sua URL)

2. **Vá para o Serviço Backend**
   - Clique em `otear-agentes-otear` (ou nome do seu serviço)

3. **Configurar Domínio/Proxy**
   - Vá para a aba "Domains" ou "Routing"
   - Procure por "Custom Headers" ou "Nginx Configuration"

4. **Adicione Headers CORS**
   
   Se houver campo para "Custom Headers":
   ```
   Access-Control-Allow-Origin: https://otear-agentes-frontend.qc7qit.easypanel.host
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
   Access-Control-Allow-Headers: *
   Access-Control-Expose-Headers: *
   Access-Control-Max-Age: 3600
   Access-Control-Allow-Credentials: true
   ```

   Se houver campo para "Nginx Configuration":
   ```nginx
   add_header 'Access-Control-Allow-Origin' 'https://otear-agentes-frontend.qc7qit.easypanel.host' always;
   add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
   add_header 'Access-Control-Allow-Headers' '*' always;
   add_header 'Access-Control-Expose-Headers' '*' always;
   add_header 'Access-Control-Max-Age' '3600' always;
   add_header 'Access-Control-Allow-Credentials' 'true' always;
   
   # Handle preflight requests
   if ($request_method = 'OPTIONS') {
       add_header 'Access-Control-Allow-Origin' 'https://otear-agentes-frontend.qc7qit.easypanel.host' always;
       add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
       add_header 'Access-Control-Allow-Headers' '*' always;
       add_header 'Access-Control-Max-Age' '3600' always;
       add_header 'Content-Type' 'text/plain charset=UTF-8' always;
       add_header 'Content-Length' '0' always;
       return 204;
   }
   ```

### Opção 2: Via Docker Compose (Se Aplicável)

Se você tem acesso ao `docker-compose.yml` do Easypanel:

```yaml
services:
  backend:
    # ... outras configurações
    labels:
      - "traefik.http.middlewares.cors-headers.headers.accesscontrolalloworiginlist=https://otear-agentes-frontend.qc7qit.easypanel.host"
      - "traefik.http.middlewares.cors-headers.headers.accesscontrolallowmethods=GET,POST,PUT,DELETE,OPTIONS,PATCH"
      - "traefik.http.middlewares.cors-headers.headers.accesscontrolallowheaders=*"
      - "traefik.http.middlewares.cors-headers.headers.accesscontrolexposeheaders=*"
      - "traefik.http.middlewares.cors-headers.headers.accesscontrolmaxage=3600"
      - "traefik.http.middlewares.cors-headers.headers.accesscontrolallowcredentials=true"
```

### Opção 3: Workaround Temporário - Aceitar Todas as Origens

**⚠️ APENAS PARA DESENVOLVIMENTO - NÃO USE EM PRODUÇÃO**

No Easypanel, configure:
```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
add_header 'Access-Control-Allow-Headers' '*' always;
```

## Teste Após Configurar

### 1. Teste com curl

```bash
curl -X OPTIONS "https://otear-agentes-otear.qc7qit.easypanel.host/api/logs" \
  -H "Origin: https://otear-agentes-frontend.qc7qit.easypanel.host" \
  -H "Access-Control-Request-Method: GET" \
  -v 2>&1 | grep -i "access-control"
```

**Você DEVE ver:**
```
< access-control-allow-origin: https://otear-agentes-frontend.qc7qit.easypanel.host
< access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
< access-control-allow-headers: *
```

### 2. Teste no Navegador

Abra o console do navegador (F12) e execute:

```javascript
fetch('https://otear-agentes-otear.qc7qit.easypanel.host/cors-test', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log('✅ CORS funcionando!', data))
.catch(error => console.error('❌ CORS ainda bloqueado:', error));
```

## Alternativa: Proxy no Frontend

Se não conseguir configurar CORS no backend, você pode criar um proxy no frontend:

### Vite (React/Vue)

```javascript
// vite.config.ts
export default {
  server: {
    proxy: {
      '/api': {
        target: 'https://otear-agentes-otear.qc7qit.easypanel.host',
        changeOrigin: true,
        secure: false
      }
    }
  }
}
```

### Next.js

```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://otear-agentes-otear.qc7qit.easypanel.host/api/:path*'
      }
    ]
  }
}
```

## Verificação Final

### Checklist

- [ ] Backend reiniciado: `docker-compose restart`
- [ ] CORS configurado no código (já feito ✅)
- [ ] CORS configurado no Easypanel
- [ ] Teste com curl passou
- [ ] Teste no navegador passou
- [ ] Frontend consegue acessar `/api/logs`

## Contato com Suporte do Easypanel

Se nada funcionar, entre em contato com o suporte do Easypanel:

**Mensagem sugerida:**
```
Olá,

Estou tendo problemas com CORS no meu serviço. O backend está configurado 
corretamente com CORSMiddleware, mas o navegador ainda recebe erro:

"No 'Access-Control-Allow-Origin' header is present on the requested resource"

Serviço: otear-agentes-otear
Frontend: https://otear-agentes-frontend.qc7qit.easypanel.host
Backend: https://otear-agentes-otear.qc7qit.easypanel.host

Como posso configurar headers CORS no proxy reverso do Easypanel?

Obrigado!
```

## Resumo

O problema é que o **proxy reverso do Easypanel** está removendo ou bloqueando os headers CORS que o FastAPI está enviando.

**Solução:** Configure CORS diretamente no Easypanel (Nginx/Traefik).

---

**Importante:** Após qualquer mudança no Easypanel, aguarde alguns segundos para o proxy recarregar a configuração.
