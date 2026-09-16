# Deploy no Easypanel - Correção de CORS

## Problema

O CORS estava funcionando antes, mas agora não funciona mais. Isso pode acontecer por:

1. **Build antigo em cache** - Easypanel está usando uma versão antiga do código
2. **Variáveis de ambiente não atualizadas** - As mudanças no `.env` não foram aplicadas
3. **Container não foi reconstruído** - Mudanças no código não foram aplicadas

## Solução: Rebuild Completo

### Passo 1: Commit e Push das Mudanças

```bash
git add .
git commit -m "fix: CORS configuration"
git push origin main
```

### Passo 2: No Easypanel

1. **Acesse o Easypanel**
   - URL: https://easypanel.qc7qit.easypanel.host

2. **Vá para o Serviço**
   - Clique em `otear-agentes-otear` (ou nome do seu serviço)

3. **Force Rebuild**
   - Procure por "Rebuild" ou "Redeploy"
   - Marque a opção "No Cache" ou "Force Rebuild"
   - Clique em "Deploy" ou "Rebuild"

4. **Aguarde o Build**
   - Acompanhe os logs do build
   - Aguarde até ver "Deployment successful" ou similar

5. **Verifique os Logs**
   - Vá para "Logs" ou "Console"
   - Procure por erros de inicialização

### Passo 3: Verificar Variáveis de Ambiente

No Easypanel, verifique se estas variáveis estão configuradas:

```env
ALLOWED_ORIGINS=*
DATABASE_URL=postgres://...
REDIS_URL=redis://...
# ... outras variáveis
```

**IMPORTANTE:** Se você adicionou `ALLOWED_ORIGINS` no `.env`, ela precisa estar no Easypanel também!

### Passo 4: Testar

Após o rebuild, teste:

```bash
curl -X OPTIONS "https://otear-agentes-otear.qc7qit.easypanel.host/api/logs" \
  -H "Origin: https://otear-agentes-frontend.qc7qit.easypanel.host" \
  -H "Access-Control-Request-Method: GET" \
  -v 2>&1 | grep -i "access-control"
```

**Deve aparecer:**
```
< access-control-allow-origin: *
< access-control-allow-methods: *
< access-control-allow-headers: *
```

## Se Ainda Não Funcionar

### Opção 1: Verificar Logs do Container

No Easypanel:
1. Vá para "Logs"
2. Procure por erros como:
   - `ModuleNotFoundError`
   - `ImportError`
   - `Failed to start`

### Opção 2: Verificar se o Container Está Rodando

```bash
# Se você tem acesso SSH ao servidor
docker ps | grep otear-agentes
```

### Opção 3: Testar Localmente

```bash
# No seu computador
docker-compose down
docker-compose build --no-cache
docker-compose up
```

Depois teste:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/cors-test
```

Se funcionar localmente mas não no Easypanel, o problema é no proxy do Easypanel.

## Configuração do Proxy no Easypanel

Se o rebuild não resolver, você precisa configurar CORS no proxy:

### No Easypanel, procure por:

1. **"Advanced Settings"** ou **"Custom Configuration"**
2. **"Environment Variables"** - adicione:
   ```
   CORS_ORIGINS=*
   ```
3. **"Labels"** (se usar Traefik) - adicione:
   ```yaml
   traefik.http.middlewares.cors.headers.accesscontrolalloworiginlist=*
   traefik.http.middlewares.cors.headers.accesscontrolallowmethods=*
   traefik.http.middlewares.cors.headers.accesscontrolallowheaders=*
   traefik.http.routers.otear-agentes.middlewares=cors
   ```

## Checklist de Deploy

- [ ] Código commitado e pushed
- [ ] Easypanel fez rebuild (sem cache)
- [ ] Variáveis de ambiente atualizadas
- [ ] Container está rodando (sem erros nos logs)
- [ ] Teste com curl passou
- [ ] Frontend consegue acessar a API

## Comandos Úteis

### Verificar se API está online
```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/health
```

### Verificar CORS
```bash
curl -I https://otear-agentes-otear.qc7qit.easypanel.host/api/logs
```

### Testar endpoint de teste
```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/cors-test
```

## Resumo

1. ✅ Código foi simplificado para `allow_origins=["*"]`
2. ⏳ **Você precisa fazer rebuild no Easypanel**
3. ⏳ Verificar se variáveis de ambiente estão corretas
4. ⏳ Testar após o rebuild

**O código está correto. Agora você precisa fazer o deploy correto no Easypanel.**

---

**Próximo passo:** Faça rebuild no Easypanel e teste novamente.
