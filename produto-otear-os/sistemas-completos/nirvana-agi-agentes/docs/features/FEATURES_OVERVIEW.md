# 🎬 Visão Geral das Funcionalidades

Resumo completo de todas as operações disponíveis na API.

## 📋 Operações Implementadas

### ✂️ Edição Básica

#### 1. Trim (Cortar)
Corta um segmento específico do vídeo.
```json
{"type": "trim", "params": {"start": 10, "end": 60}}
```
**Uso:** Remover intro/outro, extrair clipes

---

#### 2. Resize (Redimensionar)
Altera as dimensões do vídeo.
```json
{"type": "resize", "params": {"width": 1920, "height": 1080}}
```
**Uso:** Adaptar para diferentes resoluções, redes sociais

---

#### 3. Merge (Mesclar)
Concatena dois vídeos em sequência.
```json
{"type": "merge", "params": {"secondary_url": "https://..."}}
```
**Uso:** Juntar intro + conteúdo, criar compilações

---

#### 4. Add Watermark (Marca D'água)
Adiciona logo/imagem sobre o vídeo.
```json
{
  "type": "add_watermark",
  "params": {
    "image_url": "https://...",
    "position": "top-right",
    "opacity": 0.7
  }
}
```
**Uso:** Branding, proteção de conteúdo

---

#### 5. Add Text Overlay (Texto com Tarja) 📝
Adiciona texto sobre o vídeo com tarja de fundo.
```json
{
  "type": "add_text_overlay",
  "params": {
    "text": "Meu Título",
    "position": "top",
    "font_size": 60,
    "box_color": "black",
    "box_opacity": 0.8
  }
}
```
**Uso:** Títulos, lower thirds, créditos, call to action

---

### 🎙️ Áudio

#### 6. Adjust Volume (Ajustar Volume) 🔊
Aumenta, diminui ou normaliza o áudio.
```json
{"type": "adjust_volume", "params": {"volume": 2.0}}
```
ou
```json
{"type": "adjust_volume", "params": {"normalize": true}}
```
**Uso:** Corrigir áudio baixo/alto, padronizar volume

---

#### 7. Remove Silence (Jump Cuts)
Remove partes silenciosas automaticamente.
```json
{
  "type": "remove_silence",
  "params": {"noise": "-30dB", "duration": 0.5}
}
```
**Uso:** Vlogs, podcasts, tutoriais dinâmicos

---

### 🤖 IA & Legendas

#### 8. Transcribe (Transcrever)
Converte áudio em texto usando Whisper AI.
```json
{
  "type": "transcribe",
  "params": {"language": "pt", "model": "small"}
}
```
**Uso:** Gerar transcrições, análise de conteúdo

---

#### 9. Auto Subtitle (Legendas Automáticas)
Gera e queima legendas no vídeo.
```json
{
  "type": "auto_subtitle",
  "params": {
    "language": "pt",
    "model": "small"
  }
}
```
**Uso:** Acessibilidade, redes sociais, SEO

---

### 🎨 Efeitos de Animação (Legendas)

#### 9.1. Estático (Padrão)
Legendas tradicionais sem animação.
```json
{"style": {"animation": null}}
```

#### 9.2. Highlight Word (Karaoke)
Destaca cada palavra conforme é falada.
```json
{
  "style": {
    "animation": "highlight-word",
    "color": "#FFFFFF",
    "highlight_color": "#FFFF00"
  }
}
```
**Uso:** Educação, karaoke, crianças

#### 9.3. Typewriter (Digitação) ⌨️
Efeito de texto sendo digitado.
```json
{
  "style": {
    "animation": "typewriter",
    "typewriter_speed": 20
  }
}
```
**Uso:** Tutoriais tech, efeito dramático, hacker

---

## 🎯 Pipelines Populares

### Vlog Profissional
```json
{
  "operations": [
    {"type": "trim", "params": {"start": 5, "end": 300}},
    {"type": "adjust_volume", "params": {"normalize": true}},
    {"type": "remove_silence", "params": {"noise": "-30dB", "duration": 0.4}},
    {"type": "resize", "params": {"width": 1920, "height": 1080}},
    {"type": "add_watermark", "params": {"image_url": "...", "position": "bottom-right"}}
  ]
}
```

### Podcast/Entrevista
```json
{
  "operations": [
    {"type": "adjust_volume", "params": {"normalize": true, "target_level": -18}},
    {"type": "remove_silence", "params": {"noise": "-35dB", "duration": 1.5}},
    {"type": "auto_subtitle", "params": {"language": "pt", "model": "small"}}
  ]
}
```

### Tutorial Técnico
```json
{
  "operations": [
    {"type": "adjust_volume", "params": {"normalize": true}},
    {
      "type": "auto_subtitle",
      "params": {
        "language": "pt",
        "model": "base",
        "style": {
          "animation": "typewriter",
          "color": "#00FF00",
          "font": "Courier New"
        }
      }
    }
  ]
}
```

### Conteúdo para Redes Sociais
```json
{
  "operations": [
    {"type": "trim", "params": {"start": 0, "end": 60}},
    {"type": "remove_silence", "params": {"noise": "-28dB", "duration": 0.2}},
    {"type": "resize", "params": {"width": 1080, "height": 1920}},
    {
      "type": "auto_subtitle",
      "params": {
        "language": "pt",
        "model": "small",
        "style": {
          "animation": "highlight-word",
          "font_size": 48,
          "position": "center"
        }
      }
    }
  ]
}
```

---

## 📊 Comparação de Operações

| Operação | Velocidade | Complexidade | Uso Principal |
|----------|------------|--------------|---------------|
| Trim | ⚡⚡⚡ | Baixa | Cortar vídeo |
| Resize | ⚡⚡ | Baixa | Adaptar resolução |
| Merge | ⚡⚡ | Média | Juntar vídeos |
| Watermark | ⚡⚡ | Baixa | Branding |
| Text Overlay | ⚡⚡ | Baixa | Títulos, créditos |
| Adjust Volume | ⚡⚡⚡ | Baixa | Corrigir áudio |
| Remove Silence | ⚡ | Alta | Jump cuts |
| Transcribe | 🐢 | Alta | Gerar texto |
| Auto Subtitle | 🐢 | Alta | Legendas |

**Legenda:**
- ⚡⚡⚡ = Muito rápido (< 1 min)
- ⚡⚡ = Rápido (1-3 min)
- ⚡ = Moderado (3-10 min)
- 🐢 = Lento (10+ min)

*Tempos aproximados para vídeo de 5 minutos

---

## 🎓 Guias por Funcionalidade

### Legendas e Animações
- [ANIMATION_EFFECTS.md](ANIMATION_EFFECTS.md) - Guia completo
- [QUICKSTART_ANIMATIONS.md](QUICKSTART_ANIMATIONS.md) - Início rápido

### Ajuste de Volume
- [VOLUME_GUIDE.md](VOLUME_GUIDE.md) - Guia completo
- [SUMMARY_VOLUME.md](SUMMARY_VOLUME.md) - Resumo

### Texto com Tarja
- [TEXT_OVERLAY_GUIDE.md](TEXT_OVERLAY_GUIDE.md) - Guia completo

### API Geral
- [CURL_DOCUMENTATION.md](CURL_DOCUMENTATION.md) - Referência completa
- [README.md](README.md) - Visão geral

---

## 🚀 Próximas Funcionalidades

Operações planejadas (não implementadas):
- [ ] Crop (recortar área)
- [ ] Rotate (rotacionar)
- [ ] Speed (alterar velocidade)
- [ ] Extract Audio (extrair áudio)
- [ ] Add Audio (adicionar música)
- [ ] Filters (brilho, contraste, etc)
- [ ] Fade In/Out (transições)

---

## 💡 Dicas de Uso

1. **Ordem importa:** Sempre faça `trim` primeiro para economizar tempo
2. **Normalize antes:** Ajuste volume antes de outras operações de áudio
3. **Teste pequeno:** Use vídeos curtos para testar configurações
4. **Use webhook:** Para vídeos longos, configure webhook para notificação
5. **Prioridade alta:** Use `priority: 8-10` para jobs importantes

---

**Explore todas as funcionalidades na [documentação completa](DOCS_INDEX.md)!** 🎬
