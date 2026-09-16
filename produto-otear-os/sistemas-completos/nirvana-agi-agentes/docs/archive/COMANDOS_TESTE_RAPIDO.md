# ⚡ COMANDOS DE TESTE RÁPIDO - SISTEMA CORRIGIDO

## 🚀 TESTE IMEDIATO (Execute na ordem)

### 1. **Reiniciar Serviços**
```bash
docker-compose restart
```

### 2. **Teste Básico - Chat Simples**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá Patricia, como você está?"}'
```
**Esperado:** Resposta normal do agente

### 3. **Teste Carrossel - DEVE FUNCIONAR AGORA**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Crie um carrossel com 3 slides sobre produtividade no trabalho"}'
```
**Esperado:** URLs das imagens do carrossel

### 4. **Teste Notícias - DEVE FUNCIONAR AGORA**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Busque as últimas notícias sobre inteligência artificial e crie um carrossel"}'
```
**Esperado:** Notícias + URLs do carrossel

### 5. **Teste Vídeo - DEVE FUNCIONAR AGORA**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Edite este vídeo com legendas amarelas: https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"}'
```
**Esperado:** Job ID ou URL do vídeo editado

---

## 📊 MONITORAMENTO EM TEMPO REAL

### **Ver Logs das Ferramentas:**
```bash
docker-compose logs -f gateway | grep -E "\[CAROUSEL TOOL\]|\[VIDEO TOOL\]|\[Get News\]"
```

### **Ver Todos os Logs:**
```bash
docker-compose logs -f gateway
```

### **Ver Logs Específicos:**
```bash
# Só carrossel
docker-compose logs -f gateway | grep "CAROUSEL TOOL"

# Só vídeo  
docker-compose logs -f gateway | grep "VIDEO TOOL"

# Só notícias
docker-compose logs -f gateway | grep "Get News"
```

---

## ✅ SINAIS DE SUCESSO

### **Carrossel Funcionando:**
```
Logs mostram:
[CAROUSEL TOOL] Iniciando geração de 3 slides
[CAROUSEL TOOL] Calling API: https://otear-carrocel-backend...
[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso! 3 imagens criadas.

Resposta contém:
"Carrossel criado com sucesso! 🎨"
"1. https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/..."
"2. https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/..."
```

### **Notícias Funcionando:**
```
Logs mostram:
[Get News] Iniciando execução...
[Get News] Concluído com sucesso.

Resposta contém:
Notícias sobre inteligência artificial + URLs do carrossel
```

### **Vídeo Funcionando:**
```
Logs mostram:
[VIDEO TOOL] Iniciando edição de vídeo
[VIDEO TOOL] Job XXXXX criado. Iniciando verificação...

Resposta contém:
"Vídeo editado com sucesso! 🎬"
"Job ID: xxxxx"
"Download: https://otear-otear-editavideos.qc7qit.easypanel.host/static/..."
```

---

## ❌ SINAIS DE PROBLEMA

### **Agente não chama ferramenta:**
```
❌ Logs: Sem mensagens [CAROUSEL TOOL] ou [VIDEO TOOL]
❌ Resposta: Instruções em vez de URLs
❌ Resposta: "Vou criar um carrossel..." (sem URLs)
```

### **API não responde:**
```
❌ Logs: "Erro de conexão com o serviço"
❌ Logs: "Timeout"
❌ Resposta: {"error": "..."}
```

### **Modelo não funciona:**
```
❌ Logs: "Model not found"
❌ Logs: "Invalid model"
❌ Resposta: Erro 500
```

---

## 🔧 COMANDOS DE DIAGNÓSTICO

### **Testar APIs Diretamente:**
```bash
# API Carrossel
curl -X GET "https://otear-carrocel-backend.qc7qit.easypanel.host/api/health" \
  -H "X-API-Key: Senha021@Ote@r123"

# API Vídeo
curl -X GET "https://otear-otear-editavideos.qc7qit.easypanel.host/" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW"
```

### **Testar Sistema Python:**
```bash
# Teste rápido
python test_simple.py

# Teste completo
python test_final_complete.py
```

### **Verificar Configurações:**
```bash
# Ver variáveis de ambiente
cat .env | grep -E "MODEL_|API_KEY|API_URL"

# Verificar serviços
docker-compose ps
```

---

## 🎯 TESTE FINAL DE VALIDAÇÃO

Execute este comando e veja se retorna URLs:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Crie um carrossel simples com 2 slides: Slide 1: Produtividade, Slide 2: Foco"}' \
  | jq -r '.response'
```

**Se retornar URLs começando com `https://otear-carrocel-backend...` = ✅ FUNCIONANDO!**

---

## 🚨 SE ALGO FALHAR

### **1. Reiniciar Tudo:**
```bash
docker-compose down
docker-compose up -d
```

### **2. Verificar Logs de Erro:**
```bash
docker-compose logs gateway | grep -i error
```

### **3. Testar Componentes:**
```bash
# Testar importação
python -c "from app.agents.agno_agents import orchestrator; print('OK')"

# Testar ferramentas
python -c "from app.agents.agno_tools import generate_carousel_tool; print('OK')"
```

### **4. Verificar Conectividade:**
```bash
# Testar internet
ping google.com

# Testar APIs
curl -I https://otear-carrocel-backend.qc7qit.easypanel.host
```

---

## 🏆 RESULTADO ESPERADO

Após executar os comandos de teste, você deve ver:

1. ✅ **Chat simples:** Resposta normal
2. ✅ **Carrossel:** URLs das imagens geradas
3. ✅ **Notícias:** Conteúdo com notícias recentes
4. ✅ **Vídeo:** Job ID ou URL do vídeo editado

**Se todos funcionarem = SISTEMA 100% OPERACIONAL! 🎉**