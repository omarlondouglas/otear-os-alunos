# Changelog - Correção de Ferramentas de Vídeo e Carrossel

## Data: 2025-02-09

## Resumo
Correção completa dos problemas de integração das ferramentas `edit_video_tool` e `generate_carousel_tool`, incluindo melhorias nos prompts dos agentes e validações robustas.

---

## 🔧 Mudanças em `app/agents/agno_tools.py`

### `edit_video_tool` - Melhorias Críticas

**Antes:**
- Validação mínima de entrada
- Logs genéricos
- Não validava se recebeu `download_url`
- Mensagens de erro pouco claras

**Depois:**
```python
✅ Validação rigorosa de video_url (deve começar com http:// ou https://)
✅ Validação de presets válidos
✅ Logs detalhados com prefix [VIDEO TOOL]
✅ Retorno estruturado: {status, id, download_url, error, message}
✅ Mensagens de erro específicas e acionáveis
✅ Polling melhorado com logs a cada 20 segundos
✅ Documentação completa na docstring
```

**Exemplo de log melhorado:**
```
[VIDEO TOOL] Calling API: https://...
[VIDEO TOOL] Video URL: https://exemplo.com/video.mp4
[VIDEO TOOL] Operations: [{"type": "preset", "params": {"name": "VIRAL"}}]
[VIDEO TOOL] Job abc123 criado. Aguardando processamento...
[VIDEO TOOL] Job abc123 processando... 50% (40s/180s)
[VIDEO TOOL] ✓ Job abc123 COMPLETO! URL: https://...
```

---

### `generate_carousel_tool` - Melhorias Críticas

**Antes:**
- Sem validação de schema
- Não validava se recebeu URLs
- Mensagens de erro genéricas

**Depois:**
```python
✅ Validação completa do schema de cada slide
✅ Validação de campos obrigatórios (type, title)
✅ Validação de tipos válidos (cover, image-text, two-images, text-only)
✅ Logs detalhados com prefix [CAROUSEL TOOL]
✅ Retorno estruturado: {success, carouselId, totalSlides, slides, error}
✅ Mensagens de erro específicas por slide
✅ Documentação completa com exemplos
```

**Exemplo de log melhorado:**
```
[CAROUSEL TOOL] Calling API: https://...
[CAROUSEL TOOL] Slides: 3 slides
[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso! 3 imagens criadas.
[CAROUSEL TOOL]   - Slide 1: https://url1.png
[CAROUSEL TOOL]   - Slide 2: https://url2.png
[CAROUSEL TOOL]   - Slide 3: https://url3.png
```

---

## 🤖 Mudanças em `app/agents/agno_agents.py`

### VideoDirectorAgent - Prompt Melhorado

**Antes:**
```python
"Você é um Editor de Vídeos expert."
"ATENÇÃO CRÍTICA: Você NÃO PODE simular a edição."
# Instruções genéricas...
```

**Depois:**
```python
✅ Workflow obrigatório passo a passo
✅ Exemplos de uso correto
✅ Validação de resposta antes de informar usuário
✅ Instruções claras sobre quando usar cada preset
✅ Seção dedicada a validação de resposta
✅ Exemplo completo de uso correto
```

**Principais adições:**
- Seção "REGRA ABSOLUTA" no topo
- Seção "WORKFLOW OBRIGATÓRIO" com 5 passos
- Seção "VALIDAÇÃO DE RESPOSTA" com checklist
- Seção "EXEMPLO DE USO CORRETO" com diálogo completo

---

### ReviewerAgent - Prompt Melhorado

**Antes:**
```python
"Você é o Gerador de Carrosséis."
"NUNCA dê instruções manuais como 'use o Canva'."
# Schema básico...
```

**Depois:**
```python
✅ Schema detalhado com campos obrigatórios e opcionais
✅ Exemplos de chamadas corretas (2 exemplos completos)
✅ Workflow obrigatório passo a passo
✅ Validação de resposta antes de informar usuário
✅ Dicas de design e cores recomendadas
✅ Seção de cores recomendadas da marca
```

**Principais adições:**
- Seção "SCHEMA OBRIGATÓRIO" separando campos obrigatórios/opcionais
- Seção "EXEMPLOS DE CHAMADAS CORRETAS" com 2 exemplos
- Seção "WORKFLOW OBRIGATÓRIO" com 6 passos
- Seção "VALIDAÇÃO DE RESPOSTA" com checklist
- Seção "CORES RECOMENDADAS" com paleta da marca
- Seção "DICAS DE DESIGN" para cada tipo de slide

---

### Orchestrator (Patricia) - Prompt Melhorado

**Antes:**
```python
"### REGRA CRÍTICA DE DELEGAÇÃO ###"
"Para CARROSSEL: SEMPRE delegue ao 'ReviewerAgent'..."
# Instruções básicas...
```

**Depois:**
```python
✅ Pipelines obrigatórios para carrossel e vídeo
✅ Regras críticas de delegação separadas por tipo
✅ Validação antes de responder ao usuário
✅ Instruções claras sobre quando delegar para cada agente
✅ Workflow ATHENA + RALPH detalhado
```

**Principais adições:**
- Seção "REGRAS CRÍTICAS DE DELEGAÇÃO" separada em CARROSSEL e VÍDEO
- Seção "PIPELINE DE CARROSSEL (OBRIGATÓRIO)" com 5 passos
- Seção "PIPELINE DE VÍDEO (OBRIGATÓRIO)" com 5 passos
- Seção "PIPELINE GERAL (ATHENA + RALPH)" com 5 fases
- Seção "VALIDAÇÃO ANTES DE RESPONDER" com checklist

---

## 📊 Impacto das Mudanças

### Problemas Resolvidos

1. **Vídeo não era processado:**
   - ✅ Agora valida URL antes de chamar API
   - ✅ Aguarda até 3 minutos pelo processamento
   - ✅ Retorna URL apenas quando realmente pronto

2. **Carrossel não era gerado:**
   - ✅ Orchestrator agora delega corretamente para ReviewerAgent
   - ✅ ReviewerAgent valida schema antes de chamar API
   - ✅ Retorna URLs apenas quando imagens foram criadas

3. **Falta de feedback ao usuário:**
   - ✅ Logs detalhados em cada etapa
   - ✅ Mensagens de erro específicas
   - ✅ Progresso visível durante processamento

4. **Agentes não seguiam workflow:**
   - ✅ Prompts com workflows obrigatórios passo a passo
   - ✅ Validações antes de responder
   - ✅ Exemplos de uso correto

---

## 🧪 Como Testar

### Teste de Vídeo
```bash
# Via WhatsApp
"Edita esse vídeo: https://exemplo.com/video.mp4"

# Esperado:
# 1. Orchestrator → VideoDirectorAgent
# 2. VideoDirectorAgent → edit_video_tool(preset='VIRAL')
# 3. Aguarda processamento (logs a cada 20s)
# 4. Retorna: "Vídeo editado! Download: https://..."
```

### Teste de Carrossel
```bash
# Via WhatsApp
"Cria um carrossel sobre 5 dicas de produtividade"

# Esperado:
# 1. Orchestrator → Copywriter (textos)
# 2. Orchestrator → ReviewerAgent (gerar imagens)
# 3. ReviewerAgent → generate_carousel_tool([...])
# 4. Retorna: "Carrossel criado! Imagens: [URLs]"
```

---

## 📝 Arquivos Modificados

1. `app/agents/agno_tools.py`
   - `edit_video_tool()` - Reescrita completa
   - `generate_carousel_tool()` - Reescrita completa

2. `app/agents/agno_agents.py`
   - `video_director` - Prompt melhorado (60+ linhas)
   - `reviewer` - Prompt melhorado (70+ linhas)
   - `orchestrator` - Prompt melhorado (50+ linhas)

3. `TROUBLESHOOTING_TOOLS.md` - Novo arquivo de documentação

4. `CHANGELOG_TOOLS_FIX.md` - Este arquivo

---

## 🔍 Monitoramento

### Logs a Observar

**Redis (agent_logs):**
```
[VIDEO TOOL] Calling API: ...
[VIDEO TOOL] Job uuid criado...
[VIDEO TOOL] ✓ Job uuid COMPLETO!
[CAROUSEL TOOL] Calling API: ...
[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso!
```

**Celery (se aplicável):**
```
process_video_task[uuid] started
process_video_task[uuid] completed
```

---

## ⚠️ Pontos de Atenção

1. **Timeout de 180s para vídeo:**
   - Vídeos muito longos podem exceder o timeout
   - Neste caso, use `check_video_status_tool(job_id)`

2. **Rate limiting do carrossel:**
   - 30 requisições por minuto por IP
   - Considerar implementar fila se necessário

3. **Validação de URLs:**
   - Ambas ferramentas agora validam URLs de entrada
   - URLs inválidas retornam erro claro

4. **Dependência de serviços externos:**
   - VIDEO_EDITOR_API_URL deve estar acessível
   - CAROUSEL_API_URL deve estar acessível
   - Considerar health checks periódicos

---

## 🚀 Próximos Passos Recomendados

1. **Monitorar logs** no Redis por 24-48h
2. **Testar com casos reais** via WhatsApp
3. **Ajustar timeouts** se necessário
4. **Implementar retry logic** para falhas temporárias
5. **Adicionar métricas** (tempo de processamento, taxa de sucesso)
6. **Criar testes automatizados** para as ferramentas

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no Redis: `[VIDEO TOOL]` ou `[CAROUSEL TOOL]`
2. Consulte `TROUBLESHOOTING_TOOLS.md`
3. Verifique variáveis de ambiente (.env)
4. Teste conectividade com os serviços externos
