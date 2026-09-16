# 🚨 AÇÃO URGENTE - Backend Offline

## Situação Atual

❌ **Backend está offline** (erro 502 Bad Gateway)
❌ **CORS bloqueado** (consequência do backend offline)

## O Que Você Precisa Fazer AGORA

### 1. Acesse o Easypanel

URL: https://easypanel.qc7qit.easypanel.host

### 2. Vá para o Serviço

Clique em `otear-agentes-otear`

### 3. Verifique o Status

Procure por:
- **Status:** Deve estar "Running" (verde)
- Se estiver "Stopped" (vermelho), clique em "Start"

### 4. Verifique os Logs

Clique em "Logs" ou "Console" e procure por erros:

**Copie e me envie qualquer erro que aparecer!**

### 5. Faça Restart

Clique em "Restart" e aguarde 30 segundos

### 6. Teste

Abra no navegador:
```
https://otear-agentes-otear.qc7qit.easypanel.host/health
```

**Deve retornar:**
```json
{"status":"healthy"}
```

## Se Não Funcionar

### Opção A: Rebuild

1. No Easypanel, clique em "Rebuild" ou "Redeploy"
2. Marque "No Cache" ou "Force Rebuild"
3. Aguarde o build completar (pode demorar 2-5 minutos)
4. Verifique os logs durante o build
5. Teste novamente

### Opção B: Reverter Mudanças

Se o backend estava funcionando antes das minhas mudanças:

```bash
git log --oneline -10  # Ver últimos commits
git revert HEAD  # Reverter último commit
git push origin main
```

Depois faça rebuild no Easypanel.

## Informações que Preciso

Para te ajudar melhor, me envie:

1. **Screenshot do status do container** no Easypanel
2. **Últimas 50 linhas dos logs** (copie e cole)
3. **Mensagem de erro** que aparece nos logs
4. **Quando parou de funcionar?** (antes ou depois das minhas mudanças?)

## Teste Rápido

Execute este comando no seu terminal:

```bash
curl https://otear-agentes-otear.qc7qit.easypanel.host/health
```

**Me diga o que retorna:**
- Se retornar `{"status":"healthy"}` → Backend está online ✅
- Se retornar erro 502 → Backend está offline ❌
- Se retornar erro de conexão → Easypanel pode estar offline

## Resumo

1. ⏳ **Verifique status no Easypanel**
2. ⏳ **Verifique logs (copie erros)**
3. ⏳ **Faça restart do container**
4. ⏳ **Teste `/health`**
5. ⏳ **Me envie os logs se não funcionar**

---

**IMPORTANTE:** O CORS só vai funcionar depois que o backend estiver online!

**Prioridade:** ALTA - Backend precisa estar rodando
**Tempo estimado:** 5-10 minutos
**Ação:** Verificar Easypanel AGORA
