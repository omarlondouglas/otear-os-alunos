# 🚀 Deploy Imediato - Guia Rápido

## ✅ Status: TUDO CORRIGIDO!

Todas as correções foram aplicadas e testadas. Siga estes passos para colocar em produção:

---

## 📋 Checklist Pré-Deploy

- [x] ✅ Ferramentas corrigidas (`edit_video_tool`, `generate_carousel_tool`)
- [x] ✅ Prompts dos agentes melhorados
- [x] ✅ Webhook corrigido (problema crítico resolvido!)
- [x] ✅ URL do carrossel corrigida no .env
- [x] ✅ Testes automatizados passando
- [x] ✅ Sem erros de sintaxe

---

## 🔧 Passo 1: Verificar Ambiente

```bash
# Verificar se .env está correto
cat .env | grep -E "VIDEO_EDITOR_API_URL|CAROUSEL_API_URL"

# Deve mostrar (SEM barra no final do CAROUSEL):
# VIDEO_EDITOR_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host
# CAROUSEL_API_URL=https://otear-carrocel-backend.qc7qit.easypanel.host
```

---

## 🚀 Passo 2: Deploy

### Opção A: Docker (Recomendado)

```bash
# 1. Parar containers
docker-compose down

# 2. Rebuild (se necessário)
docker-compose build

# 3. Iniciar
docker-compose up -d

# 4. Ver logs
docker-compose logs -f
```

### Opção B: Local

```bash
# 1. Instalar dependências (se necessário)
pip install redis httpx

# 2. Reiniciar servidor
# Ctrl+C para parar
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Passo 3: Testar

### Teste Rápido (Local)
```bash
python test_quick.py
```

**Resultado esperado:**
```
✅ Validação de URL funcionando
✅ Validação de preset funcionando
✅ Validação de carrossel funcionando
✅ Serviço de carrossel online
```

### Teste via WhatsApp

#### Teste 1: Vídeo
```
Envie: "Edita esse vídeo: https://exemplo.com/video.mp4"

Esperado:
- Resposta em até 3 minutos
- Mensagem com URL do vídeo editado
```

#### Teste 2: Carrossel
```
Envie: "Cria um carrossel com 3 páginas sobre produtividade"

Esperado:
- Resposta em até 2 minutos
- Mensagem com URLs das 3 imagens
```

---

## 🔍 Passo 4: Monitorar Logs

### Logs Importantes:

```bash
# Docker
docker-compose logs -f | grep -E "\[Webhook\]|\[VIDEO TOOL\]|\[CAROUSEL TOOL\]"

# Local
# Logs aparecem no terminal onde uvicorn está rodando
```

### O que procurar:

**✅ Sucesso:**
```
[Webhook] Mensagem recebida de ...
[Webhook] Chamando Orchestrator...
[VIDEO TOOL] ✓ Job abc123 COMPLETO! URL: https://...
[Webhook] Resposta enviada para ...
```

**❌ Erro:**
```
[Webhook] Erro CRÍTICO no processamento: ...
[VIDEO TOOL] ✗ Job abc123 FALHOU: ...
[CAROUSEL TOOL] API retornou status 404: ...
```

---

## ⚠️ Troubleshooting Rápido

### Problema: "Erro ao importar orchestrator"
**Solução:**
```bash
# Verificar se agno está instalado
pip install agno>=1.5.1

# Verificar se google-genai está instalado
pip install google-genai>=1.0.0
```

### Problema: "Failed to log tool usage: Error 10061"
**Solução:** Redis não está rodando (não é crítico, apenas logs)
```bash
# Ignorar ou iniciar Redis:
docker run -d -p 6379:6379 redis
```

### Problema: "API retornou status 404"
**Solução:** URL do serviço está incorreta
```bash
# Verificar .env
cat .env | grep CAROUSEL_API_URL

# Deve estar SEM barra no final:
# CAROUSEL_API_URL=https://otear-carrocel-backend.qc7qit.easypanel.host
```

### Problema: "Timeout após 180s"
**Solução:** Vídeo muito longo
```bash
# Use check_video_status_tool com o job_id
# Ou aumente o timeout em agno_tools.py (linha ~250)
```

---

## 📊 Métricas para Acompanhar

### Sucesso:
- ✅ Mensagens respondidas com URLs
- ✅ Tempo de resposta < 3 minutos
- ✅ Logs sem erros críticos

### Atenção:
- ⚠️ Timeouts frequentes (vídeos muito longos?)
- ⚠️ Erros 404 (serviços offline?)
- ⚠️ Erros de validação (URLs inválidas?)

---

## 🎯 Comandos Úteis

### Ver logs em tempo real:
```bash
# Docker
docker-compose logs -f

# Filtrar por serviço
docker-compose logs -f app

# Filtrar por palavra-chave
docker-compose logs -f | grep "VIDEO TOOL"
```

### Reiniciar apenas um serviço:
```bash
docker-compose restart app
```

### Ver status dos containers:
```bash
docker-compose ps
```

### Entrar no container:
```bash
docker-compose exec app bash
```

---

## 📞 Suporte

### Se algo der errado:

1. **Verificar logs:**
   ```bash
   docker-compose logs -f | tail -100
   ```

2. **Executar testes:**
   ```bash
   python test_quick.py
   ```

3. **Verificar serviços externos:**
   ```bash
   curl https://otear-carrocel-backend.qc7qit.easypanel.host/api/health
   ```

4. **Consultar documentação:**
   - `TROUBLESHOOTING_TOOLS.md`
   - `FIX_WEBHOOK_ORCHESTRATOR.md`
   - `RESUMO_CORRECOES_FINAL.md`

---

## 🎉 Pronto!

Após seguir estes passos:

✅ Sistema estará rodando
✅ Webhook funcionando
✅ Agentes executando corretamente
✅ URLs sendo retornadas

**Teste via WhatsApp e confirme que tudo está funcionando!** 🚀

---

**Última atualização:** 2025-02-09
**Status:** ✅ Pronto para produção
