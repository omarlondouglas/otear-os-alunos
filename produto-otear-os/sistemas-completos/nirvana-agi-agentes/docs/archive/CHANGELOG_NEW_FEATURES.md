# 🆕 Novas Funcionalidades Implementadas

## Data: 03/02/2026

### 1. 🎵 Controle de Áudio no Video Overlay

**Arquivo:** `app/workers/operations/video_overlay.py`

Agora você pode controlar qual áudio usar quando sobrepõe vídeos:

```json
{
  "type": "video_overlay",
  "params": {
    "overlay_url": "https://...",
    "audio_mode": "mix",           // "main", "overlay", "mix", "none"
    "main_volume": 1.0,            // Volume do vídeo principal (0.0-2.0)
    "overlay_volume": 0.3          // Volume do vídeo overlay (0.0-2.0)
  }
}
```

**Modos disponíveis:**
- `main` - Apenas áudio do vídeo principal (padrão)
- `overlay` - Apenas áudio do vídeo overlay
- `mix` - Mixar os dois áudios
- `none` - Sem áudio

---

### 2. 🎨 Chroma Key (Remover Fundo Verde/Azul)

**Arquivo:** `app/workers/operations/video_overlay.py`

Remova fundos verdes ou azuis de vídeos overlay:

```json
{
  "type": "video_overlay",
  "params": {
    "overlay_url": "https://...",
    "chroma_key": true,            // Ativar remoção de fundo
    "chroma_color": "green",       // "green", "blue", ou "#00FF00"
    "chroma_similarity": 0.3,      // Sensibilidade (0.0-1.0)
    "chroma_blend": 0.1            // Suavização das bordas (0.0-1.0)
  }
}
```

**Cores suportadas:**
- `"green"` - Fundo verde (padrão)
- `"blue"` - Fundo azul
- `"#00FF00"` - Cor customizada em hex

---

### 3. 📏 Margem Horizontal nas Legendas

**Arquivo:** `app/utils/ass_generator.py`, `app/workers/operations/auto_subtitle.py`

Controle a distância das legendas das laterais da tela:

```json
{
  "type": "auto_subtitle",
  "params": {
    "style": {
      "margin_vertical": 60,       // Margem de cima/baixo
      "margin_horizontal": 50      // Margem das laterais (NOVO!)
    }
  }
}
```

---

### 4. 📝 Limite de Palavras por Linha

**Arquivo:** `app/utils/subtitle_generator.py`

Controle quantas palavras aparecem por legenda:

```json
{
  "type": "auto_subtitle",
  "params": {
    "style": {
      "max_words_per_line": 5      // Máximo 5 palavras por legenda (NOVO!)
    }
  }
}
```

**Nota:** Funciona apenas com legendas **sem animação** (estáticas).

---

### 5. 🎬 Nova Animação: Word-by-Word

**Arquivo:** `app/utils/ass_generator.py`

Mostra apenas a palavra sendo falada (estilo TikTok):

```json
{
  "type": "auto_subtitle",
  "params": {
    "style": {
      "animation": "word-by-word"  // NOVO! Só mostra palavra atual
    }
  }
}
```

**Animações disponíveis:**
- `null` - Estático (padrão)
- `"highlight-word"` - Destaca palavra atual (karaoke)
- `"typewriter"` - Efeito de digitação
- `"word-by-word"` - Só mostra palavra atual (NOVO!)

---

### 6. 📐 Faixa de Largura Completa (Text Overlay)

**Arquivo:** `app/workers/operations/add_text_overlay.py`

Crie uma faixa que cobre toda a largura do vídeo:

```json
{
  "type": "add_text_overlay",
  "params": {
    "text": "Meu Título",
    "box_full_width": true,        // Faixa de largura completa (NOVO!)
    "box_height": 350,             // Altura da faixa em pixels (NOVO!)
    "box_color": "white",
    "box_opacity": 1.0
  }
}
```

---

## 🎯 Exemplos Completos

### Exemplo 1: Reação com Fundo Removido + Áudio Mixado
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video-principal.mp4",
    "operations": [{
      "type": "video_overlay",
      "params": {
        "overlay_url": "https://example.com/reacao-greenscreen.mp4",
        "position": "bottom-right",
        "scale": 0.3,
        "chroma_key": true,
        "chroma_color": "green",
        "chroma_similarity": 0.35,
        "audio_mode": "mix",
        "main_volume": 1.0,
        "overlay_volume": 0.4
      }
    }]
  }'
```

### Exemplo 2: Faixa Branca + Legendas Word-by-Word
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "POV: IA é uma bolha\n\nEu criando minha agência",
          "position": "top",
          "font_size": 60,
          "font_color": "black",
          "box_full_width": true,
          "box_height": 350,
          "box_color": "white",
          "box_opacity": 1.0
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small",
          "style": {
            "color": "#FFFF00",
            "font_size": 32,
            "position": "bottom",
            "animation": "word-by-word",
            "margin_vertical": 60,
            "margin_horizontal": 50
          }
        }
      }
    ]
  }'
```

### Exemplo 3: Legendas com Limite de Palavras
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "auto_subtitle",
      "params": {
        "language": "pt",
        "model": "small",
        "style": {
          "color": "#FFFF00",
          "font_size": 32,
          "position": "bottom",
          "max_words_per_line": 5,
          "margin_vertical": 60,
          "margin_horizontal": 40
        }
      }
    }]
  }'
```

---

## 📝 Notas Importantes

1. **max_words_per_line** só funciona com legendas estáticas (sem animação)
2. **chroma_key** requer vídeo com fundo verde/azul sólido
3. **box_full_width** cria uma faixa que cobre toda a largura do vídeo
4. **word-by-word** mostra apenas a palavra sendo falada (ideal para TikTok)
5. **margin_horizontal** controla distância das laterais (padrão: 10)

---

## 🔄 Arquivos Modificados

- `app/workers/operations/video_overlay.py` - Áudio + Chroma Key
- `app/workers/operations/add_text_overlay.py` - Faixa completa
- `app/workers/operations/auto_subtitle.py` - Margem horizontal
- `app/utils/ass_generator.py` - Word-by-word + Margens
- `app/utils/subtitle_generator.py` - Limite de palavras

---

## ✅ Próximos Passos

- [ ] Atualizar CURL_DOCUMENTATION.md
- [ ] Atualizar TEXT_OVERLAY_GUIDE.md
- [ ] Criar VIDEO_OVERLAY_GUIDE.md
- [ ] Atualizar ANIMATION_EFFECTS.md
- [ ] Adicionar exemplos no README.md
