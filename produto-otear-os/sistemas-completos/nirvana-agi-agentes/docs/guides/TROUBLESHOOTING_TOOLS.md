# Guia de Troubleshooting - Ferramentas de Vídeo e Carrossel

## Problemas Corrigidos

### 1. Ferramenta de Edição de Vídeo (`edit_video_tool`)

**Problemas identificados:**
- ❌ Agente não estava chamando a ferramenta corretamente
- ❌ Falta de validação de URL de entrada
- ❌ Logs insuficientes para debug
- ❌ Timeout sem mensagem clara
- ❌ Não validava se recebeu `download_url` antes de retornar

**Correções aplicadas:**
- ✅ Validação rigorosa de `video_url` (deve começar com http:// ou https://)
- ✅ Logs detalhados em cada etapa: `[VIDEO TOOL]` prefix
- ✅ Validação de presets (VIRAL, MODERN_SUBTITLES, REACTION, CLEAN)
- ✅ Retorno estruturado com `status`, `id`, `download_url`, `error`
- ✅ Mensagens de erro claras e acionáveis
- ✅ Polling melhorado com logs a cada 20 segundos

**Como usar corretamente:**
```python
# FORMATO SIMPLES (RECOMENDADO)
edit_video_tool(
    video_url='https://exemplo.com/video.mp4',
    preset='VIRAL'
)

# FORMATO AVANÇADO
edit_video_tool(
    video_url='https://exemplo.com/video.mp4',
    operations=[
        {'type': 'add_text_overlay', 'params': {'text': 'Título', 'position': 'top'}},
        {'type': 'auto_subtitle', 'params': {'style': {'font_size': 10, 'color': '#FFFF00'}}}
    ]
)
```

**Resposta esperada (sucesso):**
```json
{
    "status": "completed",
    "id": "uuid-do-job",
    "download_url": "https://url-do-video-editado.mp4",
    "message": "Vídeo processado com sucesso!"
}
```

**Resposta esperada (timeout):**
```json
{
    "status": "processing",
    "id": "uuid-do-job",
    "message": "Vídeo ainda processando após 180s. Use check_video_status_tool('uuid-do-job') para verificar o progresso."
}
```

---

### 2. Ferramenta de Geração de Carrossel (`generate_carousel_tool`)

**Problemas identificados:**
- ❌ Agente não estava sendo delegado corretamente pelo orchestrator
- ❌ Falta de validação de schema dos slides
- ❌ Não validava se recebeu URLs antes de retornar
- ❌ Mensagens de erro genéricas

**Correções aplicadas:**
- ✅ Validação completa do schema de cada slide
- ✅ Logs detalhados: `[CAROUSEL TOOL]` prefix
- ✅ Validação de campos obrigatórios (`type`, `title`)
- ✅ Validação de tipos válidos (cover, image-text, two-images, text-only)
- ✅ Retorno estruturado com `success`, `carouselId`, `slides`, `error`
- ✅ Mensagens de erro específicas por slide

**Schema obrigatório por slide:**
```json
{
    "type": "cover | image-text | two-images | text-only",
    "title": "Texto principal (OBRIGATÓRIO)",
    "subtitle": "Texto secundário (opcional)",
    "titleColor": "#ffffff",
    "bgColor": "#0a0a0a",
    "fontFamily": "urbanist",
    "images": {
        "bg": "https://url-imagem.jpg"  // Para type='cover'
    }
}
```

**Exemplo de uso correto:**
```python
generate_carousel_tool([
    {
        "type": "cover",
        "title": "5 DICAS PARA CRESCER",
        "subtitle": "No Instagram",
        "titleColor": "#A3F12E",
        "bgColor": "#0a0a0a"
    },
    {
        "type": "text-only",
        "title": "1. Poste consistentemente",
        "bgColor": "#1a1a1a",
        "titleColor": "#ffffff"
    },
    {
        "type": "text-only",
        "title": "Siga para mais dicas",
        "bgColor": "#A3F12E",
        "titleColor": "#000000"
    }
])
```

**Resposta esperada (sucesso):**
```json
{
    "success": true,
    "carouselId": "uuid-do-carrossel",
    "totalSlides": 3,
    "slides": [
        {"order": 1, "type": "cover", "url": "https://url-slide-1.png"},
        {"order": 2, "type": "text-only", "url": "https://url-slide-2.png"},
        {"order": 3, "type": "text-only", "url": "https://url-slide-3.png"}
    ],
    "storage": "supabase"
}
```

---

### 3. Melhorias nos Prompts dos Agentes

#### VideoDirectorAgent
**Antes:** Instruções genéricas, sem workflow claro
**Depois:**
- ✅ Workflow passo a passo obrigatório
- ✅ Exemplos de uso correto
- ✅ Validação de resposta antes de informar usuário
- ✅ Instruções claras sobre quando usar cada preset

#### ReviewerAgent
**Antes:** Instruções ambíguas sobre geração de carrossel
**Depois:**
- ✅ Schema detalhado com exemplos
- ✅ Workflow obrigatório passo a passo
- ✅ Validação de resposta antes de informar usuário
- ✅ Dicas de design e cores recomendadas

#### Orchestrator (Patricia)
**Antes:** Delegação não clara
**Depois:**
- ✅ Pipelines obrigatórios para carrossel e vídeo
- ✅ Regras críticas de delegação
- ✅ Validação antes de responder ao usuário
- ✅ Instruções claras sobre quando delegar para cada agente

---

## Como Testar

### Teste 1: Edição de Vídeo
```bash
# Via WhatsApp ou API
"Edita esse vídeo: https://exemplo.com/video.mp4"

# Comportamento esperado:
# 1. Orchestrator delega para VideoDirectorAgent
# 2. VideoDirectorAgent chama edit_video_tool(video_url=..., preset='VIRAL')
# 3. Ferramenta aguarda processamento (até 3 min)
# 4. Retorna URL do vídeo editado
# 5. Usuário recebe: "Vídeo editado com sucesso! Download: https://..."
```

### Teste 2: Geração de Carrossel
```bash
# Via WhatsApp ou API
"Cria um carrossel sobre 5 dicas de produtividade"

# Comportamento esperado:
# 1. Orchestrator delega para Copywriter (criar textos)
# 2. Orchestrator delega para ReviewerAgent (gerar imagens)
# 3. ReviewerAgent chama generate_carousel_tool([...])
# 4. Ferramenta retorna URLs das imagens
# 5. Usuário recebe: "Carrossel criado! Imagens: [URLs]"
```

---

## Checklist de Validação

### Para Vídeos:
- [ ] URL do vídeo começa com http:// ou https://
- [ ] Preset é válido (VIRAL, MODERN_SUBTITLES, REACTION, CLEAN)
- [ ] Ferramenta retornou `download_url` antes de informar usuário
- [ ] Logs mostram `[VIDEO TOOL]` em cada etapa

### Para Carrosséis:
- [ ] Cada slide tem `type` e `title`
- [ ] Tipos são válidos (cover, image-text, two-images, text-only)
- [ ] Ferramenta retornou `success: true` e array de `slides` com URLs
- [ ] Logs mostram `[CAROUSEL TOOL]` em cada etapa

---

## Variáveis de Ambiente Necessárias

```env
# Serviço de Vídeo
VIDEO_EDITOR_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host
VIDEO_EDITOR_API_KEY=oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW

# Serviço de Carrossel
CAROUSEL_API_URL=https://otear-carrocel-backend.qc7qit.easypanel.host
CAROUSEL_API_KEY=Senha021@Ote@r123

# Redis (para logs)
REDIS_URL=redis://localhost:6379/0
```

---

## Logs para Monitoramento

### Vídeo:
```
[VIDEO TOOL] Calling API: https://...
[VIDEO TOOL] Video URL: https://...
[VIDEO TOOL] Operations: [...]
[VIDEO TOOL] Initial response: {...}
[VIDEO TOOL] Job uuid criado. Aguardando processamento...
[VIDEO TOOL] Job uuid processando... 50% (40s/180s)
[VIDEO TOOL] ✓ Job uuid COMPLETO! URL: https://...
```

### Carrossel:
```
[CAROUSEL TOOL] Calling API: https://...
[CAROUSEL TOOL] Slides: 3 slides
[CAROUSEL TOOL] Payload: {...}
[CAROUSEL TOOL] Response: {...}
[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso! 3 imagens criadas.
[CAROUSEL TOOL]   - Slide 1: https://...
[CAROUSEL TOOL]   - Slide 2: https://...
[CAROUSEL TOOL]   - Slide 3: https://...
```

---

## Próximos Passos

1. **Monitorar logs** no Redis para identificar falhas
2. **Testar com vídeos reais** via WhatsApp
3. **Testar carrosséis** com diferentes layouts
4. **Ajustar timeouts** se necessário (atualmente 180s para vídeo)
5. **Adicionar retry logic** se serviços estiverem instáveis
