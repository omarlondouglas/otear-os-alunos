# ⚡ Guia Rápido - Efeitos de Animação

Comece a usar os efeitos de animação em legendas em 5 minutos!

## 🚀 Início Rápido

### 1. Certifique-se que a API está rodando

```bash
docker-compose up
```

A API estará disponível em: `http://localhost:8000`

### 2. Teste o Efeito Typewriter (Digitação)

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@seu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "base",
          "style": {
            "animation": "typewriter"
          }
        }
      }
    ]
  }'
```

**Resposta:**
```json
{
  "id": "abc-123-def",
  "status": "queued",
  "progress": 0
}
```

### 3. Verifique o Status

```bash
curl -X GET "http://localhost:8000/api/v1/videos/status/abc-123-def" \
  -H "X-API-Key: dev-secret-key"
```

### 4. Baixe o Resultado

Quando `status` for `"completed"`, use o `download_url` da resposta.

---

## 🎨 3 Efeitos Disponíveis

### 1️⃣ Estático (Padrão)
Legendas normais, sem animação.

```json
"style": {
  "animation": null
}
```

### 2️⃣ Highlight Word
Destaca cada palavra conforme é falada (estilo karaoke).

```json
"style": {
  "animation": "highlight-word",
  "color": "#FFFFFF",
  "highlight_color": "#FFFF00"
}
```

### 3️⃣ Typewriter ⌨️ NOVO!
Efeito de digitação, mostra caracteres progressivamente.

```json
"style": {
  "animation": "typewriter",
  "typewriter_speed": 20
}
```

---

## 🎯 Casos de Uso Populares

### Tutorial de Programação
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@tutorial.mp4" \
  -F 'request={
    "operations": [{
      "type": "auto_subtitle",
      "params": {
        "language": "pt",
        "model": "base",
        "style": {
          "color": "#00FF00",
          "font": "Courier New",
          "animation": "typewriter",
          "typewriter_speed": 22
        }
      }
    }]
  }'
```

### Vídeo Educativo (Crianças)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@aula.mp4" \
  -F 'request={
    "operations": [{
      "type": "auto_subtitle",
      "params": {
        "language": "pt",
        "model": "small",
        "style": {
          "color": "#FFFFFF",
          "highlight_color": "#FF1493",
          "font": "Arial",
          "font_size": 30,
          "animation": "highlight-word"
        }
      }
    }]
  }'
```

### Vlog Dinâmico (Jump Cut + Typewriter)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@vlog.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "remove_silence",
        "params": {
          "noise": "-30dB",
          "duration": 0.4
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small",
          "style": {
            "animation": "typewriter",
            "typewriter_speed": 25
          }
        }
      }
    ]
  }'
```

---

## ⚙️ Parâmetros Importantes

### typewriter_speed
Velocidade de digitação em caracteres por segundo.

| Valor | Efeito | Uso |
|-------|--------|-----|
| 10-15 | Lento, dramático | Suspense, ênfase |
| 20-25 | Normal, legível | Uso geral |
| 30-40 | Rápido, dinâmico | Tech, ação |

### Cores Populares

| Estilo | color | highlight_color |
|--------|-------|-----------------|
| Clássico | `#FFFFFF` | `#FFFF00` |
| Hacker | `#00FF00` | - |
| Dramático | `#FFD700` | - |
| Moderno | `#00FFFF` | - |
| Energético | `#FFFFFF` | `#FF6600` |

### Fontes Recomendadas

| Tipo | Fonte | Uso |
|------|-------|-----|
| Terminal | Courier New, Consolas | Typewriter tech |
| Impacto | Impact | Títulos, dramático |
| Limpa | Arial, Helvetica | Geral |
| Divertida | Comic Sans MS | Infantil |

---

## 🧪 Scripts de Teste

### Teste Rápido (Python)
```bash
cd examples
python test_animations.py seu_video.mp4
```

### Comparação de Efeitos (Bash)
```bash
cd examples
chmod +x compare_animations.sh
./compare_animations.sh seu_video.mp4
```

---

## 📚 Documentação Completa

- **[CURL_DOCUMENTATION.md](CURL_DOCUMENTATION.md)** - Todos os endpoints e exemplos
- **[ANIMATION_EFFECTS.md](ANIMATION_EFFECTS.md)** - Guia detalhado dos efeitos
- **[examples/README.md](examples/README.md)** - Scripts de exemplo

---

## 💡 Dicas Rápidas

✅ **Faça:**
- Teste com vídeos curtos primeiro (30-60s)
- Ajuste `typewriter_speed` conforme o ritmo da fala
- Use fontes monoespaçadas para efeito terminal
- Combine com `remove_silence` para vídeos dinâmicos

❌ **Evite:**
- Typewriter muito rápido (> 40 chars/seg)
- Typewriter em vídeos muito longos (> 10 min)
- Cores de baixo contraste
- Fontes muito decorativas

---

## 🆘 Problemas Comuns

### "Job failed"
- Verifique se o vídeo tem áudio
- Tente um modelo menor (`tiny` ou `base`)
- Verifique os logs do worker

### Legendas não aparecem
- Certifique-se que `animation` está correto
- Verifique se o modelo Whisper está instalado
- Teste com um vídeo menor primeiro

### Typewriter muito rápido/lento
- Ajuste `typewriter_speed` (padrão: 20)
- Teste valores entre 15-30 para começar

---

## 🎬 Pronto para Começar!

Escolha um dos exemplos acima e comece a criar vídeos com legendas animadas!

**Dúvidas?** Consulte a [documentação completa](CURL_DOCUMENTATION.md).
