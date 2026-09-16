# Correção: URLs Relativas → URLs Absolutas

## 🔴 Problema Identificado

As APIs de vídeo e carrossel retornam **URLs relativas** em vez de URLs completas:

### Exemplo - Vídeo:
```json
{
  "status": "completed",
  "download_url": "/static/edcffb7c-7a30-4534-be53-d70178846e86_final.mp4"
}
```

### Exemplo - Carrossel:
```json
{
  "success": true,
  "slides": [
    {"order": 1, "url": "/api/image/abc123/slide-1.png"}
  ]
}
```

**Problema:** URLs relativas não funcionam quando enviadas ao usuário via WhatsApp!

---

## ✅ Solução Aplicada

### 1. Conversão de URL de Vídeo

**Arquivo:** `app/agents/agno_tools.py`
**Função:** `edit_video_tool()`

**Antes:**
```python
if state == "completed":
    download_url = job_status.get("download_url")
    if download_url:
        return {
            "status": "completed",
            "download_url": download_url  # ❌ URL relativa!
        }
```

**Depois:**
```python
if state == "completed":
    download_url = job_status.get("download_url")
    if download_url:
        # ✅ Se a URL for relativa (/static/...), construir URL completa
        if download_url.startswith("/"):
            full_url = f"{VIDEO_SERVICE_URL}{download_url}"
            logger.info(f"[VIDEO TOOL] ✓ URL relativa convertida: {download_url} -> {full_url}")
            return {
                "status": "completed",
                "id": job_id,
                "download_url": full_url,  # ✅ URL completa!
                "message": "Vídeo processado com sucesso!"
            }
        else:
            # URL já é absoluta (ex: Supabase)
            return {
                "status": "completed",
                "id": job_id,
                "download_url": download_url,
                "message": "Vídeo processado com sucesso!"
            }
```

### 2. Conversão de URLs de Carrossel

**Arquivo:** `app/agents/agno_tools.py`
**Função:** `generate_carousel_tool()`

**Antes:**
```python
if result.get("success"):
    slides = result.get("slides", [])
    if slides and len(slides) > 0:
        # ❌ URLs relativas não convertidas
        return result
```

**Depois:**
```python
if result.get("success"):
    slides = result.get("slides", [])
    if slides and len(slides) > 0:
        # ✅ Converter URLs relativas em URLs completas
        for slide in slides:
            url = slide.get('url', '')
            if url.startswith('/'):
                # URL relativa, construir URL completa
                slide['url'] = f"{CAROUSEL_SERVICE_URL}{url}"
                logger.info(f"[CAROUSEL TOOL]   - Slide {slide.get('order')}: {url} -> {slide['url']}")
            else:
                logger.info(f"[CAROUSEL TOOL]   - Slide {slide.get('order')}: {url}")
        
        logger.info(f"[CAROUSEL TOOL] ✓ Carrossel gerado com sucesso! {len(slides)} imagens criadas.")
        return result
```

---

## 🧪 Testes Realizados

### Teste 1: Conversão de URL de Vídeo
```python
# Input
download_url = "/static/edcffb7c-7a30-4534-be53-d70178846e86_final.mp4"

# Output
full_url = "https://otear-otear-editavideos.qc7qit.easypanel.host/static/edcffb7c-7a30-4534-be53-d70178846e86_final.mp4"

# ✅ Resultado: URL completa e funcional!
```

### Teste 2: Conversão de URLs de Carrossel
```python
# Input
slides = [
    {"order": 1, "url": "/api/image/abc123/slide-1.png"},
    {"order": 2, "url": "/api/image/abc123/slide-2.png"},
    {"order": 3, "url": "/api/image/abc123/slide-3.png"}
]

# Output
slides = [
    {"order": 1, "url": "https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/abc123/slide-1.png"},
    {"order": 2, "url": "https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/abc123/slide-2.png"},
    {"order": 3, "url": "https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/abc123/slide-3.png"}
]

# ✅ Resultado: Todas as URLs completas e funcionais!
```

### Teste 3: URL Já Absoluta (Supabase)
```python
# Input
download_url = "https://supabase.com/storage/v1/object/public/bucket/file.mp4"

# Output
download_url = "https://supabase.com/storage/v1/object/public/bucket/file.mp4"

# ✅ Resultado: URL mantida sem alteração!
```

---

## 📊 Comparação Antes/Depois

### Antes (❌ URLs Relativas)
```
Usuário: "Edita esse vídeo"
↓
VideoDirectorAgent processa
↓
Retorna: "/static/video.mp4"
↓
WhatsApp: ❌ Link quebrado!
```

### Depois (✅ URLs Completas)
```
Usuário: "Edita esse vídeo"
↓
VideoDirectorAgent processa
↓
Converte: "/static/video.mp4" → "https://otear-otear-editavideos.qc7qit.easypanel.host/static/video.mp4"
↓
WhatsApp: ✅ Link funcional!
```

---

## 🔍 Logs para Monitorar

### Vídeo:
```
[VIDEO TOOL] ✓ Job abc123 COMPLETO! URL relativa convertida: 
  /static/video.mp4 -> https://otear-otear-editavideos.qc7qit.easypanel.host/static/video.mp4
```

### Carrossel:
```
[CAROUSEL TOOL]   - Slide 1: /api/image/test/slide-1.png -> https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/test/slide-1.png
[CAROUSEL TOOL]   - Slide 2: /api/image/test/slide-2.png -> https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/test/slide-2.png
[CAROUSEL TOOL]   - Slide 3: /api/image/test/slide-3.png -> https://otear-carrocel-backend.qc7qit.easypanel.host/api/image/test/slide-3.png
```

---

## ⚙️ Configuração Necessária

As URLs dos serviços são lidas do `.env`:

```env
VIDEO_EDITOR_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host
CAROUSEL_API_URL=https://otear-carrocel-backend.qc7qit.easypanel.host
```

**Importante:** Certifique-se que essas variáveis estão corretas!

---

## 🧪 Como Testar

### Teste Automatizado:
```bash
python test_url_conversion.py
```

**Resultado esperado:**
```
✅ Conversão correta!
✅ Conversão correta!
✅ Manteve URL original
✅ URL convertida
✅ Lógica de conversão de URLs está correta!
```

### Teste Manual (via WhatsApp):
```
1. Envie: "Edita esse vídeo: https://exemplo.com/video.mp4"
2. Aguarde processamento
3. Verifique se a URL retornada é completa:
   ✅ https://otear-otear-editavideos.qc7qit.easypanel.host/static/...
   ❌ /static/...
```

---

## 📝 Resumo

**Problema:** APIs retornam URLs relativas (`/static/...`)
**Solução:** Converter para URLs absolutas (`https://...`)
**Resultado:** Links funcionam no WhatsApp e em qualquer lugar

**Status:** ✅ CORRIGIDO E TESTADO

---

## 🎯 Impacto

### Antes:
- ❌ Usuário recebia links quebrados
- ❌ Tinha que construir URL manualmente
- ❌ Experiência ruim

### Depois:
- ✅ Usuário recebe links funcionais
- ✅ Pode clicar e baixar diretamente
- ✅ Experiência perfeita

---

**Data:** 2025-02-09
**Arquivos modificados:** `app/agents/agno_tools.py`
**Linhas modificadas:** ~250-270 (vídeo), ~210-230 (carrossel)
