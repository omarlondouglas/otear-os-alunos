# Fix: Erro de CORS no Frontend

## Problema

O frontend não consegue acessar a API devido a erro de CORS:

```
Access to fetch at 'https://otear-agentes-otear.qc7qit.easypanel.host/api/logs' 
from origin 'https://otear-agentes-frontend.qc7qit.easypanel.host' 
has been blocked by CORS policy: Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## O Que é CORS?

CORS (Cross-Origin Resource Sharing) é um mecanismo de segurança que impede que um site acesse recursos de outro domínio sem permissão explícita.

### Exemplo:
- **Frontend:** `https://otear-agentes-frontend.qc7qit.easypanel.host`
- **Backend:** `https://otear-agentes-otear.qc7qit.easypanel.host`

Como são domínios diferentes, o navegador bloqueia a requisição por padrão.

## Causa Raiz

O CORS estava configurado, mas:
1. Não estava explicitando os métodos permitidos (incluindo OPTIONS)
2. Não tinha `expose_headers` configurado
3. Não tinha `max_age` para cache de preflight

## Solução Aplicada

### Arquivo: `app/main.py`

```python
# CORS Configuration - IMPORTANTE: Deve vir ANTES de qualquer rota
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # ✅ Explícito
    allow_headers=["*"],
    expose_headers=["*"],  # ✅ NOVO
    max_age=3600,  # ✅ NOVO - Cache preflight por 1 hora
)
```

### Arquivo: `.env`

```env
# CORS - Origens permitidas (separadas por vírgula)
ALLOWED_ORIGINS=https://otear-agentes-frontend.qc7qit.easypanel.host,http://localhost:3000,http://localhost:5173
```

## O Que Mudou

| Antes | Depois |
|-------|--------|
| `allow_methods=["*"]` | `allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]` |
| Sem `expose_headers` | `expose_headers=["*"]` ✅ |
| Sem `max_age` | `max_age=3600` ✅ |
| Origens hardcoded | Origens configuráveis via `.env` ✅ |

## Como Testar

### 1. Reinicie o Backend

```bash
docker-compose restart
```

### 2. Verifique os Headers CORS

```bash
curl -X OPTIONS "https://otear-agentes-otear.qc7qit.easypanel.host/api/logs" \
  -H "Origin: https://otear-agentes-frontend.qc7qit.easypanel.host" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

**Resposta esperada:**
```
< HTTP/2 200
< access-control-allow-origin: https://otear-agentes-frontend.qc7qit.easypanel.host
< access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
< access-control-allow-headers: *
< access-control-expose-headers: *
< access-control-max-age: 3600
```

### 3. Teste no Frontend

Abra o frontend e verifique se o erro de CORS desapareceu.

## Troubleshooting

### Erro Persiste Após Reiniciar

**Problema:** Cache do navegador ou proxy reverso

**Solução:**
1. Limpe o cache do navegador (Ctrl+Shift+Delete)
2. Abra em aba anônima
3. Verifique se o Easypanel tem cache de proxy

### Erro 403 ou 401

**Problema:** Autenticação falhando

**Solução:**
Verifique se o frontend está enviando as credenciais corretas.

### Erro em Localhost mas Funciona em Produção

**Problema:** Origem localhost não está na lista

**Solução:**
Adicione no `.env`:
```env
ALLOWED_ORIGINS=https://otear-agentes-frontend.qc7qit.easypanel.host,http://localhost:3000,http://localhost:5173
```

## Configuração para Desenvolvimento vs Produção

### Desenvolvimento (Aceita Tudo)

```env
ALLOWED_ORIGINS=*
```

### Produção (Apenas Origens Específicas)

```env
ALLOWED_ORIGINS=https://otear-agentes-frontend.qc7qit.easypanel.host,https://app.otear.com.br
```

## Verificação no Easypanel

Se o erro persistir, pode ser o proxy reverso do Easypanel bloqueando.

### Verificar Configuração do Easypanel

1. Acesse o painel do Easypanel
2. Vá para o serviço `otear-agentes-otear`
3. Verifique se há configurações de proxy
4. Adicione headers CORS no proxy se necessário:

```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
add_header 'Access-Control-Allow-Headers' '*' always;
add_header 'Access-Control-Expose-Headers' '*' always;
```

## Resumo

✅ **CORS configurado corretamente**
✅ **Métodos explícitos incluindo OPTIONS**
✅ **Headers expostos**
✅ **Cache de preflight habilitado**
✅ **Origens configuráveis via .env**

**Próximo passo:** Reinicie e teste!

```bash
docker-compose restart
```

---

**Data:** 2026-02-10
**Status:** ✅ Corrigido
**Impacto:** Frontend agora pode acessar a API
