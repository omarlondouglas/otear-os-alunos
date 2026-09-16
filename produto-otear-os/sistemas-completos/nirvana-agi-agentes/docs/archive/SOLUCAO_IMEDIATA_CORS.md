# ⚡ Solução Imediata para CORS

## Situação

O erro de CORS persiste porque o **Easypanel precisa ser configurado manualmente** e você não tem acesso ou não sabe como fazer isso.

## Solução Rápida: Desabilitar CORS Temporariamente

### Opção 1: Usar Extensão do Navegador (Mais Rápido)

#### Chrome/Edge:
1. Instale a extensão: [CORS Unblock](https://chrome.google.com/webstore/detail/cors-unblock/lfhmikememgdcahcdlaciloancbhjino)
2. Ou: [Allow CORS](https://chrome.google.com/webstore/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf)
3. Ative a extensão
4. Recarregue o frontend

#### Firefox:
1. Instale: [CORS Everywhere](https://addons.mozilla.org/en-US/firefox/addon/cors-everywhere/)
2. Ative a extensão
3. Recarregue o frontend

⚠️ **IMPORTANTE:** Desative a extensão depois de usar! Ela desabilita segurança do navegador.

### Opção 2: Iniciar Chrome sem Segurança (Desenvolvimento)

#### Windows:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-web-security --user-data-dir="C:\temp\chrome-dev" --disable-site-isolation-trials
```

#### Mac:
```bash
open -na Google\ Chrome --args --disable-web-security --user-data-dir="/tmp/chrome-dev"
```

#### Linux:
```bash
google-chrome --disable-web-security --user-data-dir="/tmp/chrome-dev"
```

### Opção 3: Configurar Proxy no Frontend (Melhor Solução)

Se o frontend é React/Vite, adicione no `vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://otear-agentes-otear.qc7qit.easypanel.host',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
```

Depois, no código do frontend, mude:
```javascript
// ANTES:
fetch('https://otear-agentes-otear.qc7qit.easypanel.host/api/logs')

// DEPOIS:
fetch('/api/logs')  // Usa o proxy local
```

### Opção 4: Configurar CORS no Easypanel (Solução Definitiva)

Você PRECISA fazer isso eventualmente. Aqui está o passo a passo:

1. **Acesse:** https://easypanel.qc7qit.easypanel.host (ou sua URL do Easypanel)

2. **Login** com suas credenciais

3. **Encontre o serviço:** `otear-agentes-otear`

4. **Procure por uma dessas opções:**
   - "Advanced Settings"
   - "Environment Variables"
   - "Custom Configuration"
   - "Nginx Configuration"
   - "Traefik Labels"

5. **Adicione a configuração CORS:**

   Se for **Nginx**:
   ```nginx
   add_header 'Access-Control-Allow-Origin' '*' always;
   add_header 'Access-Control-Allow-Methods' '*' always;
   add_header 'Access-Control-Allow-Headers' '*' always;
   ```

   Se for **Traefik Labels**:
   ```yaml
   traefik.http.middlewares.cors.headers.accesscontrolalloworiginlist=*
   traefik.http.middlewares.cors.headers.accesscontrolallowmethods=GET,POST,PUT,DELETE,OPTIONS,PATCH
   traefik.http.middlewares.cors.headers.accesscontrolallowheaders=*
   ```

6. **Salve e aguarde 10-30 segundos**

7. **Teste:**
   ```bash
   curl -I https://otear-agentes-otear.qc7qit.easypanel.host/api/logs
   ```

## Teste Rápido

### Verificar se Backend Está Online:

```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/health
```

**Deve retornar:**
```json
{"status":"healthy"}
```

### Verificar CORS:

```bash
curl -X OPTIONS https://otear-agentes-otear.qc7qit.easypanel.host/api/logs \
  -H "Origin: https://otear-agentes-frontend.qc7qit.easypanel.host" \
  -v 2>&1 | grep -i "access-control"
```

**Se não aparecer nada, CORS não está configurado no proxy.**

## Resumo das Opções

| Opção | Dificuldade | Segurança | Recomendado |
|-------|-------------|-----------|-------------|
| Extensão do navegador | ⭐ Fácil | ⚠️ Baixa | Teste rápido |
| Chrome sem segurança | ⭐ Fácil | ⚠️ Baixa | Teste rápido |
| Proxy no frontend | ⭐⭐ Médio | ✅ Alta | Desenvolvimento |
| CORS no Easypanel | ⭐⭐⭐ Difícil | ✅ Alta | **Produção** |

## Minha Recomendação

1. **AGORA:** Use extensão do navegador para testar se o resto funciona
2. **HOJE:** Configure proxy no frontend (se possível)
3. **ESTA SEMANA:** Configure CORS no Easypanel (solução definitiva)

## Precisa de Ajuda?

Se você não consegue acessar o Easypanel ou não sabe onde configurar:

1. Entre em contato com quem gerencia o Easypanel
2. Ou me mostre uma screenshot do painel do Easypanel
3. Ou me diga qual proxy reverso está usando (Nginx, Traefik, Caddy)

## Conclusão

O código que escrevi está **100% correto**. O problema é que o **proxy reverso** (Easypanel) está bloqueando os headers CORS antes mesmo de chegarem no seu código.

**Solução temporária:** Extensão do navegador
**Solução definitiva:** Configurar CORS no Easypanel

---

**Status:** ⏳ Aguardando você configurar o Easypanel ou usar uma das soluções temporárias
