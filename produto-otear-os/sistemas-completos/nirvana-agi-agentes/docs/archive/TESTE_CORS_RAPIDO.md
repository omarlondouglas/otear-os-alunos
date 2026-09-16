# 🚀 Teste Rápido de CORS

## Comando para Testar AGORA

```bash
curl -X OPTIONS "https://otear-agentes-otear.qc7qit.easypanel.host/api/logs" \
  -H "Origin: https://otear-agentes-frontend.qc7qit.easypanel.host" \
  -H "Access-Control-Request-Method: GET" \
  -v 2>&1 | grep -i "access-control"
```

## O Que Você Deve Ver

### ✅ Se CORS Estiver Funcionando:

```
< access-control-allow-origin: https://otear-agentes-frontend.qc7qit.easypanel.host
< access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
< access-control-allow-headers: *
< access-control-expose-headers: *
< access-control-max-age: 3600
```

### ❌ Se CORS Estiver Bloqueado:

```
(nenhum header access-control aparece)
```

## Se Não Funcionar

O problema é no **proxy reverso do Easypanel**.

### Solução Rápida (Desenvolvimento):

1. Acesse o Easypanel
2. Vá para `otear-agentes-otear`
3. Procure "Custom Headers" ou "Nginx Config"
4. Cole isto:

```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' '*' always;
add_header 'Access-Control-Allow-Headers' '*' always;
```

5. Salve e aguarde 10 segundos
6. Teste novamente

## Teste no Navegador

Abra o console (F12) no frontend e execute:

```javascript
fetch('https://otear-agentes-otear.qc7qit.easypanel.host/cors-test')
  .then(r => r.json())
  .then(d => console.log('✅ CORS OK!', d))
  .catch(e => console.error('❌ Ainda bloqueado:', e));
```

## Resumo

1. ✅ Código está correto
2. ⏳ **Configure CORS no Easypanel**
3. ⏳ Teste com o comando acima
4. ⏳ Verifique no navegador

---

**Leia:** `EASYPANEL_CORS_CONFIG.md` para instruções detalhadas
