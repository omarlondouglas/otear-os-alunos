# 📚 Documentação Completa de Comandos CURL - API de Edição de Vídeos

## 🔑 Autenticação

Todas as requisições requerem o header de autenticação:
```bash
-H "X-API-Key: dev-secret-key"
```

## 📋 Índice de Operações

1. [Trim (Cortar Vídeo)](#1-trim-cortar-vídeo)
2. [Resize (Redimensionar)](#2-resize-redimensionar)
3. [Transcribe (Transcrever Áudio)](#3-transcribe-transcrever-áudio)
4. [Auto Subtitle (Legendas Automáticas)](#4-auto-subtitle-legendas-automáticas)
5. [Remove Silence / Jump Cut Automático](#5-remove-silence-remover-silêncio--jump-cut-automático)
6. [Merge (Mesclar Vídeos)](#6-merge-mesclar-vídeos)
7. [Add Watermark (Adicionar Marca D'água)](#7-add-watermark-adicionar-marca-dágua)
8. [Adjust Volume (Ajustar Volume)](#8-adjust-volume-ajustar-volume)
9. [Add Text Overlay (Adicionar Texto com Tarja)](#9-add-text-overlay-adicionar-texto-com-tarja)
10. [Add Audio (Adicionar Trilha Sonora)](#10-add-audio-adicionar-trilha-sonora)
11. [Video Overlay (Picture-in-Picture / Reação)](#11-video-overlay-picture-in-picture--reação)
12. [Operações Combinadas](#12-operações-combinadas)
13. [🎬 Edição Completa com Jump Cut](#13--edição-completa-com-jump-cut)
14. [Consultar Status do Job](#14-consultar-status-do-job)

---

## 1. Trim (Cortar Vídeo)

Corta um vídeo especificando tempo de início e fim.

### Parâmetros:
- `start`: Tempo de início (segundos ou formato "HH:MM:SS")
- `end`: Tempo de fim (segundos ou formato "HH:MM:SS")

### Exemplo 1: Cortar primeiros 10 segundos
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@meu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 0,
          "end": 10
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Cortar do segundo 30 ao 60
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@meu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 30,
          "end": 60
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Usando formato de tempo HH:MM:SS
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@meu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": "00:00:30",
          "end": "00:01:45"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

---

## 2. Resize (Redimensionar)

Redimensiona o vídeo para novas dimensões.

### Parâmetros:
- `width`: Largura em pixels (opcional, use -1 para manter proporção)
- `height`: Altura em pixels (opcional, use -1 para manter proporção)

### Exemplo 1: Redimensionar para 1280x720
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@meu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "resize",
        "params": {
          "width": 1280,
          "height": 720
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Redimensionar largura mantendo proporção
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@meu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "resize",
        "params": {
          "width": 1920,
          "height": -1
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Redimensionar altura mantendo proporção
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@meu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "resize",
        "params": {
          "width": -1,
          "height": 1080
        }
      }
    ],
    "output_format": "mp4"
  }'
```

---

## 3. Transcribe (Transcrever Áudio)

Transcreve o áudio do vídeo para texto usando Whisper AI.

### Parâmetros:
- `language`: Código do idioma (opcional, ex: "pt", "en", "es")
- `model`: Modelo Whisper ("tiny", "base", "small", "medium", "large")

### Endpoint Dedicado

```bash
curl -X POST "http://localhost:8000/api/v1/videos/transcribe" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@aula.mp4" \
  -F "language=pt" \
  -F "model=base"
```

### Usando Endpoint de Edição

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@aula.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "transcribe",
        "params": {
          "language": "pt",
          "model": "small"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo com detecção automática de idioma
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "transcribe",
        "params": {
          "model": "medium"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

**Nota:** A transcrição é salva em um arquivo JSON separado (`.json`) junto com o vídeo de saída.

---

## 🎨 Efeitos de Animação para Legendas

A API suporta três tipos de animação para legendas:

### 1. **Estático (Padrão)**
Legendas tradicionais sem animação.
```json
"style": {
  "animation": null
}
```

### 2. **Highlight Word (Destaque por Palavra)**
Destaca cada palavra conforme é falada, estilo karaoke.
```json
"style": {
  "animation": "highlight-word",
  "color": "#FFFFFF",
  "highlight_color": "#FFFF00"
}
```
**Ideal para:** Vídeos educativos, karaoke, conteúdo infantil

### 3. **Typewriter (Digitação)** ⌨️
Mostra o texto sendo "digitado" caractere por caractere.
```json
"style": {
  "animation": "typewriter",
  "typewriter_speed": 20
}
```
**Ideal para:** Tutoriais de programação, efeito dramático, estilo hacker/terminal

### Comparação de Velocidades (Typewriter)

| Speed | Caracteres/seg | Uso Recomendado |
|-------|----------------|-----------------|
| 10-15 | Lento | Dramático, suspense, ênfase |
| 20-25 | Normal | Geral, fácil leitura |
| 30-40 | Rápido | Dinâmico, energético |
| 50+ | Muito rápido | Efeito visual, não para leitura |

---

## 4. Auto Subtitle (Legendas Automáticas)

Gera e queima legendas automaticamente no vídeo usando transcrição AI.

### Parâmetros:
- `language`: Código do idioma (opcional)
- `model`: Modelo Whisper ("tiny", "base", "small", "medium", "large")
- `style`: Objeto com configurações de estilo (opcional)
  - `color`: Cor do texto em hex (ex: "#FFFFFF")
  - `highlight_color`: Cor de destaque em hex (ex: "#FFFF00") - usado com animation="highlight-word"
  - `font`: Nome da fonte (ex: "Arial", "Impact", "Courier New", "Consolas")
  - `font_size`: Tamanho da fonte (ex: 24)
  - `position`: Posição ("bottom", "top", "center")
  - `margin_vertical`: Margem vertical em pixels (ex: 20)
  - `animation`: Tipo de animação:
    - `null` ou omitido: Legendas estáticas (padrão)
    - `"highlight-word"`: Destaca cada palavra conforme é falada
    - `"typewriter"`: Efeito de digitação, mostra caracteres progressivamente ⌨️
  - `typewriter_speed`: Velocidade de digitação em caracteres/segundo (padrão: 20) - usado com animation="typewriter"
- `keep_srt`: Manter arquivo de legenda (true/false)

### Exemplo 1: Legendas básicas em português
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@aula.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Legendas com estilo customizado
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "en",
          "model": "medium",
          "style": {
            "color": "#FFFFFF",
            "font": "Impact",
            "font_size": 32,
            "position": "bottom",
            "margin_vertical": 30
          }
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Legendas com animação de destaque por palavra
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small",
          "style": {
            "color": "#FFFFFF",
            "highlight_color": "#FFFF00",
            "font": "Arial",
            "font_size": 28,
            "position": "bottom",
            "margin_vertical": 25,
            "animation": "highlight-word"
          },
          "keep_srt": false
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Legendas com efeito de digitação (typewriter) ⌨️ NOVO!
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small",
          "style": {
            "color": "#00FF00",
            "font": "Courier New",
            "font_size": 26,
            "position": "bottom",
            "margin_vertical": 30,
            "animation": "typewriter",
            "typewriter_speed": 15
          },
          "keep_srt": false
        }
      }
    ],
    "output_format": "mp4"
  }'
```

**Parâmetros do efeito typewriter:**
- `animation`: "typewriter" (ativa o efeito)
- `typewriter_speed`: Velocidade em caracteres por segundo (padrão: 20)
  - 10-15: Lento, dramático
  - 20-25: Normal, legível
  - 30-40: Rápido, dinâmico

### Exemplo 5: Typewriter com estilo hacker/terminal 💻
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@tutorial.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "en",
          "model": "base",
          "style": {
            "color": "#00FF00",
            "font": "Consolas",
            "font_size": 24,
            "position": "bottom",
            "margin_vertical": 20,
            "animation": "typewriter",
            "typewriter_speed": 25
          }
        }
      }
    ],
    "output_format": "mp4"
  }'
```

---

## 5. Remove Silence (Remover Silêncio / Jump Cut Automático)

Remove automaticamente partes silenciosas do vídeo, criando **jump cuts** automáticos. Ideal para:
- 🎙️ Podcasts e entrevistas
- 🎓 Aulas e palestras
- 🎬 Vlogs e vídeos falados
- 📹 Screencasts e tutoriais

**Como funciona:**
1. Detecta segmentos silenciosos baseado no threshold de ruído
2. Remove os silêncios automaticamente
3. Concatena as partes com áudio, criando jump cuts suaves

### Parâmetros:
- `noise`: Threshold de ruído (ex: "-30dB", "-40dB")
  - Valores mais negativos = mais sensível (detecta mais silêncios)
  - `-30dB`: Padrão, bom para a maioria dos casos
  - `-40dB`: Mais sensível, detecta silêncios sutis
  - `-20dB`: Menos sensível, apenas silêncios óbvios
- `duration`: Duração mínima de silêncio em segundos (ex: 0.5, 1.0)
  - Silêncios menores que este valor são ignorados
  - `0.3-0.5s`: Jump cuts rápidos (estilo YouTube)
  - `1.0-2.0s`: Apenas pausas longas

### Exemplo 1: Jump cut estilo YouTube (rápido e dinâmico)
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
          "duration": 0.3
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Podcast/Palestra (remover apenas pausas longas)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@palestra.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "remove_silence",
        "params": {
          "noise": "-35dB",
          "duration": 2.0
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Detecção ultra sensível (máximo de jump cuts)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@tutorial.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "remove_silence",
        "params": {
          "noise": "-40dB",
          "duration": 0.2
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Jump cut + Legendas automáticas (combo perfeito!)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_bruto.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "remove_silence",
        "params": {
          "noise": "-30dB",
          "duration": 0.5
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### 💡 Dicas de Configuração

| Tipo de Conteúdo | noise | duration | Resultado |
|------------------|-------|----------|-----------|
| Vlog/YouTube | -30dB | 0.3s | Dinâmico, muitos cuts |
| Podcast | -35dB | 1.5s | Natural, remove pausas |
| Aula/Palestra | -30dB | 2.0s | Preserva respiração |
| Tutorial/Screencast | -40dB | 0.5s | Remove hesitações |
| Entrevista | -25dB | 1.0s | Conservador |

---

## 6. Merge (Mesclar Vídeos)

Concatena dois vídeos em sequência.

### Parâmetros:
- `secondary_url`: URL do segundo vídeo a ser mesclado

### Exemplo 1: Mesclar dois vídeos
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video1.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "merge",
        "params": {
          "secondary_url": "https://example.com/video2.mp4"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Mesclar com vídeo de URL pública
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@intro.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "merge",
        "params": {
          "secondary_url": "https://storage.example.com/videos/content.mp4"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

**Nota:** O vídeo principal é enviado como arquivo, o secundário é baixado da URL fornecida.

---

## 7. Add Watermark (Adicionar Marca D'água)

Adiciona uma imagem como marca d'água no vídeo.

### Parâmetros:
- `image_url`: URL da imagem da marca d'água (PNG recomendado)
- `position`: Posição ("top-left", "top-right", "bottom-left", "bottom-right", "center")
- `opacity`: Opacidade de 0.0 a 1.0 (opcional, padrão: 1.0)
- `scale`: Escala relativa (opcional, padrão: 0.2)

### Exemplo 1: Marca d'água no canto superior direito
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_watermark",
        "params": {
          "image_url": "https://example.com/logo.png",
          "position": "top-right"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Marca d'água com opacidade
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_watermark",
        "params": {
          "image_url": "https://example.com/watermark.png",
          "position": "bottom-right",
          "opacity": 0.5,
          "scale": 0.15
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Marca d'água centralizada
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_watermark",
        "params": {
          "image_url": "https://cdn.example.com/brand.png",
          "position": "center",
          "opacity": 0.3,
          "scale": 0.25
        }
      }
    ],
    "output_format": "mp4"
  }'
```

---

## 8. Adjust Volume (Ajustar Volume)

Ajusta o volume do áudio do vídeo ou normaliza automaticamente.

### Parâmetros:
- `volume`: Multiplicador de volume (0.0-10.0)
  - 0.5 = metade do volume
  - 1.0 = sem mudança (padrão)
  - 2.0 = dobro do volume
  - 3.0 = triplo do volume
- `normalize`: Normalizar áudio automaticamente (true/false)
- `target_level`: Nível alvo em LUFS para normalização (padrão: -16)

### Exemplo 1: Aumentar volume em 50%
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "volume": 1.5
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Dobrar o volume
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_baixo.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "volume": 2.0
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Reduzir volume pela metade
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_alto.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "volume": 0.5
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Normalizar áudio automaticamente
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "normalize": true
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 5: Normalizar com nível customizado
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@podcast.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "normalize": true,
          "target_level": -14
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### 💡 Guia de Valores de Volume

| Volume | Efeito | Uso Recomendado |
|--------|--------|-----------------|
| 0.1-0.3 | Muito baixo | Música de fundo sutil |
| 0.5 | Metade | Reduzir áudio alto |
| 1.0 | Original | Sem mudança |
| 1.5 | +50% | Aumentar levemente |
| 2.0 | Dobro | Áudio muito baixo |
| 3.0-5.0 | Muito alto | Áudio extremamente baixo |

### 🎚️ Normalização vs Volume Manual

**Normalização (`normalize: true`):**
- ✅ Ajusta automaticamente para nível ideal
- ✅ Previne distorção
- ✅ Consistente entre vídeos
- ✅ Ideal para: Podcasts, entrevistas, conteúdo profissional
- ⚠️ Mais lento que ajuste manual

**Volume Manual (`volume: X`):**
- ✅ Controle preciso
- ✅ Mais rápido
- ✅ Ideal para: Ajustes específicos, música de fundo
- ⚠️ Pode causar distorção se muito alto

### 📊 Níveis de Normalização (LUFS)

| Target Level | Uso | Plataforma |
|--------------|-----|------------|
| -23 LUFS | Broadcast TV | EBU R128 |
| -16 LUFS | Streaming (padrão) | Spotify, YouTube |
| -14 LUFS | Streaming alto | Apple Music |
| -18 LUFS | Podcast | Padrão podcast |

**Nota:** Valores mais negativos = mais baixo. -14 é mais alto que -23.

---

## 9. Add Text Overlay (Adicionar Texto com Tarja)

Adiciona texto sobre o vídeo com tarja de fundo (opcional). Perfeito para títulos, créditos, anotações, lower thirds, etc.

### Parâmetros:
- `text`: Texto a ser exibido (obrigatório)
- `position`: Posição predefinida
  - "top", "bottom", "center" (padrão)
  - "top-left", "top-right", "bottom-left", "bottom-right"
  - "custom" (use x e y)
- `x`, `y`: Posição customizada em pixels (opcional)
- `font`: Nome da fonte (padrão: "Arial")
- `font_size`: Tamanho da fonte (padrão: 48)
- `font_color`: Cor do texto (padrão: "white")
- `line_spacing`: Espaçamento entre linhas em pixels (padrão: 0)
- `box`: Mostrar tarja de fundo (true/false, padrão: true)
- `box_color`: Cor da tarja (padrão: "black")
- `box_opacity`: Opacidade da tarja 0.0-1.0 (padrão: 0.7)
- `box_padding`: Espaçamento interno da tarja em pixels (padrão: 20)
- `start_time`: Quando o texto aparece em segundos (padrão: 0)
- `duration`: Duração em segundos (padrão: até o fim)

### Exemplo 1: Título no topo com tarja preta
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Meu Vídeo Incrível",
          "position": "top",
          "font_size": 60,
          "font_color": "white",
          "box_color": "black",
          "box_opacity": 0.8
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Lower Third (nome/cargo no canto inferior)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@entrevista.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "João Silva - CEO",
          "position": "bottom-left",
          "font_size": 36,
          "font_color": "white",
          "box_color": "blue",
          "box_opacity": 0.9,
          "start_time": 5,
          "duration": 10
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Texto centralizado sem tarja
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "INSCREVA-SE!",
          "position": "center",
          "font_size": 80,
          "font_color": "yellow",
          "box": false
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Créditos no final
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Produzido por: Minha Empresa",
          "position": "bottom",
          "font_size": 32,
          "font_color": "white",
          "box_color": "black",
          "box_opacity": 0.7,
          "start_time": 55,
          "duration": 5
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 5: Múltiplos textos (títulos diferentes)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Capítulo 1",
          "position": "top",
          "font_size": 50,
          "start_time": 0,
          "duration": 3
        }
      },
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Capítulo 2",
          "position": "top",
          "font_size": 50,
          "start_time": 30,
          "duration": 3
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 6: Tarja colorida estilo YouTube
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "NOVO VÍDEO!",
          "position": "top",
          "font_size": 70,
          "font_color": "white",
          "box_color": "red",
          "box_opacity": 0.95,
          "box_padding": 30,
          "start_time": 0,
          "duration": 5
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 7: Texto com múltiplas linhas e espaçamento
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Linha 1\nLinha 2\nLinha 3",
          "position": "center",
          "font_size": 50,
          "font_color": "white",
          "line_spacing": 10,
          "box_padding": 40
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 8: Título com muito espaçamento (tarja grande)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "TÍTULO GRANDE",
          "position": "top",
          "font_size": 80,
          "font_color": "white",
          "box_color": "black",
          "box_opacity": 0.9,
          "box_padding": 50
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### 🎨 Cores Disponíveis

Cores básicas (nome):
- `white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`
- `orange`, `purple`, `pink`, `brown`, `gray`, `lime`

Cores hex (formato):
- `#RRGGBB` - Ex: `#FF0000` (vermelho), `#00FF00` (verde)
- `#RRGGBBAA` - Com transparência: `#FF000080` (vermelho 50%)

### 📍 Posições Predefinidas

| Posição | Descrição |
|---------|-----------|
| `top` | Topo centralizado |
| `bottom` | Base centralizada (padrão) |
| `center` | Centro da tela |
| `top-left` | Canto superior esquerdo |
| `top-right` | Canto superior direito |
| `bottom-left` | Canto inferior esquerdo (lower third) |
| `bottom-right` | Canto inferior direito |

### 💡 Casos de Uso

**Títulos de Vídeo:**
```json
{
  "text": "Título do Vídeo",
  "position": "top",
  "font_size": 60,
  "box_opacity": 0.8
}
```

**Lower Third (Nome/Cargo):**
```json
{
  "text": "Nome - Cargo",
  "position": "bottom-left",
  "font_size": 36,
  "box_color": "blue",
  "start_time": 5,
  "duration": 10
}
```

**Call to Action:**
```json
{
  "text": "INSCREVA-SE!",
  "position": "center",
  "font_size": 80,
  "font_color": "yellow",
  "box": false
}
```

**Créditos:**
```json
{
  "text": "Produzido por...",
  "position": "bottom",
  "font_size": 32,
  "start_time": 55
}
```

**Marca D'água de Texto:**
```json
{
  "text": "@meucanal",
  "position": "top-right",
  "font_size": 24,
  "box_opacity": 0.5
}
```

---

## 10. Add Audio (Adicionar Trilha Sonora)

Adiciona música de fundo ou substitui o áudio original do vídeo. Perfeito para trilhas sonoras, música de fundo, podcasts, etc.

### Parâmetros:
- `audio_url`: URL do arquivo de áudio (MP3, WAV, AAC, etc) - obrigatório
- `mode`: Modo de operação
  - `"mix"` - Mixa música com áudio original (padrão)
  - `"replace"` - Substitui áudio original pela música
  - `"background"` - Música de fundo (igual a mix)
- `audio_volume`: Volume da música 0.0-1.0 (padrão: 0.3)
- `original_volume`: Volume do áudio original 0.0-1.0 (padrão: 1.0)
- `fade_in`: Fade in em segundos (padrão: 0)
- `fade_out`: Fade out em segundos (padrão: 0)
- `loop`: Repetir música se for mais curta que o vídeo (true/false, padrão: false)
- `start_time`: Quando a música começa em segundos (padrão: 0)

### Exemplo 1: Música de fundo (mix)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_audio",
        "params": {
          "audio_url": "https://example.com/musica.mp3",
          "mode": "mix",
          "audio_volume": 0.2,
          "original_volume": 1.0
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Substituir áudio completamente
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_audio",
        "params": {
          "audio_url": "https://example.com/trilha.mp3",
          "mode": "replace"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Música com fade in/out
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_audio",
        "params": {
          "audio_url": "https://example.com/background.mp3",
          "mode": "mix",
          "audio_volume": 0.25,
          "fade_in": 2,
          "fade_out": 3
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Música em loop (repetir)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_longo.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_audio",
        "params": {
          "audio_url": "https://example.com/musica_curta.mp3",
          "mode": "mix",
          "audio_volume": 0.3,
          "loop": true
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 5: Música começando no meio do vídeo
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_audio",
        "params": {
          "audio_url": "https://example.com/musica.mp3",
          "mode": "mix",
          "audio_volume": 0.4,
          "start_time": 10,
          "fade_in": 2
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 6: Reduzir áudio original e adicionar música
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_audio",
        "params": {
          "audio_url": "https://example.com/musica.mp3",
          "mode": "mix",
          "audio_volume": 0.5,
          "original_volume": 0.3
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### 🎵 Guia de Volumes

| Uso | audio_volume | original_volume | Resultado |
|-----|--------------|-----------------|-----------|
| Música sutil | 0.1-0.2 | 1.0 | Música quase imperceptível |
| Música de fundo | 0.2-0.4 | 1.0 | Balanceado (recomendado) |
| Música destaque | 0.5-0.7 | 0.5-0.7 | Música e voz equilibradas |
| Música dominante | 0.8-1.0 | 0.2-0.4 | Música em primeiro plano |
| Substituir | N/A | N/A | Use mode="replace" |

### 🎚️ Modos de Operação

**Mix (Padrão):**
- ✅ Mantém áudio original
- ✅ Adiciona música por cima
- ✅ Ideal para: Vlogs, tutoriais, entrevistas
- ⚠️ Pode ficar confuso se volumes não forem ajustados

**Replace:**
- ✅ Remove áudio original completamente
- ✅ Usa apenas a música
- ✅ Ideal para: Montagens, slideshows, vídeos sem fala
- ⚠️ Perde áudio original (irreversível)

**Background (igual a Mix):**
- ✅ Mesmo comportamento que mix
- ✅ Nome mais descritivo para música de fundo

### 💡 Dicas Profissionais

**1. Volumes Recomendados:**
- Vlog com música: `audio_volume: 0.2-0.3`
- Tutorial com música: `audio_volume: 0.15-0.25`
- Montagem: `mode: "replace"`
- Podcast com intro musical: `audio_volume: 0.4` nos primeiros 10s

**2. Fade In/Out:**
- Sempre use fade para transições suaves
- Fade in: 1-3 segundos
- Fade out: 2-4 segundos

**3. Loop:**
- Use quando a música é mais curta que o vídeo
- Escolha músicas que fazem loop naturalmente
- Evite músicas com final abrupto

**4. Formatos Suportados:**
- MP3 (recomendado)
- WAV
- AAC
- M4A
- OGG

### ⚠️ Cuidados

1. **Direitos Autorais**: Use apenas música livre de direitos ou licenciada
2. **Qualidade**: Use áudio de boa qualidade (128kbps+)
3. **Duração**: Se música for mais longa que vídeo, será cortada
4. **Volume**: Teste antes! Volumes muito altos podem distorcer

---

## 11. Video Overlay (Picture-in-Picture / Reação)

Sobrepõe um vídeo sobre outro. Perfeito para reações, comentários, tutoriais, split screen, etc. Estilo TikTok!

### Parâmetros:
- `overlay_url`: URL do vídeo que ficará sobreposto (obrigatório)
- `position`: Posição predefinida
  - "bottom-right" (padrão), "bottom-left", "top-right", "top-left"
  - "center", "top-center", "bottom-center"
  - "custom" (use x e y)
- `x`, `y`: Posição customizada (opcional)
- `scale`: Escala relativa 0.0-1.0 (padrão: 0.25 = 25%)
- `width`, `height`: Tamanho em pixels (opcional, sobrescreve scale)
- `margin`: Distância das bordas em pixels (padrão: 20)
- `opacity`: Opacidade 0.0-1.0 (padrão: 1.0)
- `border`: Adicionar borda (true/false, padrão: false)
- `border_color`: Cor da borda (padrão: "white")
- `border_width`: Largura da borda em pixels (padrão: 3)
- `start_time`: Quando o overlay aparece em segundos (padrão: 0)
- `duration`: Duração do overlay em segundos (padrão: até o fim)

### Exemplo 1: Reação no canto (estilo TikTok)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_principal.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "video_overlay",
        "params": {
          "overlay_url": "https://example.com/reacao.mp4",
          "position": "bottom-right",
          "scale": 0.3,
          "margin": 20,
          "border": true,
          "border_color": "white",
          "border_width": 3
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Comentarista no canto inferior esquerdo
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "video_overlay",
        "params": {
          "overlay_url": "https://example.com/comentarista.mp4",
          "position": "bottom-left",
          "scale": 0.25,
          "margin": 30
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Tutorial com instrutor no canto
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@screencast.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "video_overlay",
        "params": {
          "overlay_url": "https://example.com/instrutor.mp4",
          "position": "top-right",
          "scale": 0.2,
          "border": true
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Overlay aparecendo temporariamente
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "video_overlay",
        "params": {
          "overlay_url": "https://example.com/reacao.mp4",
          "position": "bottom-right",
          "scale": 0.3,
          "start_time": 5,
          "duration": 15
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 5: Split screen (dois vídeos lado a lado)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video1.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "video_overlay",
        "params": {
          "overlay_url": "https://example.com/video2.mp4",
          "position": "custom",
          "x": "main_w/2",
          "y": 0,
          "width": "main_w/2",
          "height": "main_h"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 6: Overlay com opacidade (semi-transparente)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "video_overlay",
        "params": {
          "overlay_url": "https://example.com/overlay.mp4",
          "position": "center",
          "scale": 0.5,
          "opacity": 0.7
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### 📐 Guia de Tamanhos

| Uso | scale | Aparência |
|-----|-------|-----------|
| Reação pequena | 0.15-0.20 | Discreto |
| Reação normal | 0.25-0.30 | Balanceado (recomendado) |
| Picture-in-Picture | 0.30-0.40 | Visível |
| Split screen | 0.50 | Metade da tela |

### 📍 Posições Populares

| Posição | Uso Comum |
|---------|-----------|
| `bottom-right` | Reações TikTok, comentários |
| `bottom-left` | Alternativa para reações |
| `top-right` | Instrutor em tutoriais |
| `top-left` | Logo, marca d'água de vídeo |
| `center` | Destaque, foco principal |

### 💡 Dicas Profissionais

**1. Reação Estilo TikTok:**
```json
{
  "position": "bottom-right",
  "scale": 0.3,
  "border": true,
  "border_color": "white",
  "border_width": 3
}
```

**2. Tutorial com Instrutor:**
```json
{
  "position": "top-right",
  "scale": 0.2,
  "border": true
}
```

**3. Split Screen:**
```json
{
  "position": "custom",
  "x": "main_w/2",
  "y": 0,
  "width": "main_w/2",
  "height": "main_h"
}
```

**4. Overlay Temporário:**
- Use `start_time` e `duration` para controlar quando aparece
- Ideal para comentários específicos em momentos do vídeo

### ⚠️ Cuidados

1. **Duração**: Se overlay for mais curto que vídeo principal, ele para
2. **Áudio**: Usa apenas áudio do vídeo principal
3. **Performance**: Vídeos grandes demoram mais para processar
4. **Qualidade**: Use vídeos de boa qualidade para ambos

---

## 12. Operações Combinadas

Você pode combinar múltiplas operações em uma única requisição. As operações são executadas na ordem especificada.

### Exemplo 1: Cortar + Redimensionar
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 10,
          "end": 60
        }
      },
      {
        "type": "resize",
        "params": {
          "width": 1280,
          "height": 720
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Remover Silêncio + Adicionar Legendas com Typewriter
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@palestra.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "remove_silence",
        "params": {
          "noise": "-30dB",
          "duration": 0.5
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small",
          "style": {
            "color": "#FFFFFF",
            "font": "Arial",
            "font_size": 24,
            "position": "bottom",
            "animation": "typewriter",
            "typewriter_speed": 22
          }
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Ajustar Volume + Adicionar Legendas
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_baixo.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "volume": 2.0
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Normalizar Áudio + Remover Silêncio
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@podcast.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "normalize": true,
          "target_level": -18
        }
      },
      {
        "type": "remove_silence",
        "params": {
          "noise": "-35dB",
          "duration": 1.0
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 5: Pipeline completo
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@raw_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 5,
          "end": 120
        }
      },
      {
        "type": "remove_silence",
        "params": {
          "noise": "-30dB",
          "duration": 0.5
        }
      },
      {
        "type": "resize",
        "params": {
          "width": 1920,
          "height": 1080
        }
      },
      {
        "type": "adjust_volume",
        "params": {
          "normalize": true
        }
      },
      {
        "type": "resize",
        "params": {
          "width": 1920,
          "height": 1080
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "medium"
        }
      },
      {
        "type": "add_watermark",
        "params": {
          "image_url": "https://example.com/logo.png",
          "position": "top-right",
          "opacity": 0.7
        }
      }
    ],
    "output_format": "mp4",
    "priority": 8
  }'
```

---

## 10. 🎬 Edição Completa com Jump Cut

Esta seção mostra como fazer uma **edição completa profissional** em uma única requisição, combinando jump cut automático com outras operações.

### Caso de Uso 1: Vlog Profissional
Corta intro/outro + Remove silêncios + Redimensiona + Adiciona marca d'água

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@vlog_bruto.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 5,
          "end": 300
        }
      },
      {
        "type": "remove_silence",
        "params": {
          "noise": "-30dB",
          "duration": 0.4
        }
      },
      {
        "type": "resize",
        "params": {
          "width": 1920,
          "height": 1080
        }
      },
      {
        "type": "add_watermark",
        "params": {
          "image_url": "https://example.com/logo.png",
          "position": "bottom-right",
          "opacity": 0.7,
          "scale": 0.15
        }
      }
    ],
    "output_format": "mp4",
    "priority": 8
  }'
```

### Caso de Uso 2: Aula/Tutorial com Legendas e Volume Normalizado
Remove pausas longas + Normaliza áudio + Adiciona legendas estilizadas

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@aula_gravada.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "adjust_volume",
        "params": {
          "normalize": true,
          "target_level": -16
        }
      },
      {
        "type": "remove_silence",
        "params": {
          "noise": "-35dB",
          "duration": 1.5
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "medium",
          "style": {
            "color": "#FFFFFF",
            "font": "Arial",
            "font_size": 28,
            "position": "bottom",
            "margin_vertical": 30
          }
        }
      }
    ],
    "output_format": "mp4",
    "priority": 7,
    "webhook_url": "https://myapp.com/webhook/video-ready"
  }'
```

### Caso de Uso 3: Podcast/Entrevista Editado
Corta intro + Jump cuts + Legendas com destaque + Marca d'água

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@podcast_raw.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 10,
          "end": 3600
        }
      },
      {
        "type": "remove_silence",
        "params": {
          "noise": "-32dB",
          "duration": 0.8
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small",
          "style": {
            "color": "#FFFFFF",
            "highlight_color": "#FFD700",
            "font": "Impact",
            "font_size": 32,
            "position": "bottom",
            "animation": "highlight-word"
          }
        }
      },
      {
        "type": "add_watermark",
        "params": {
          "image_url": "https://cdn.example.com/podcast-logo.png",
          "position": "top-right",
          "opacity": 0.8
        }
      }
    ],
    "output_format": "mp4",
    "priority": 9,
    "webhook_url": "https://myapp.com/webhook/podcast-done"
  }'
```

### Caso de Uso 4: Conteúdo para Redes Sociais (Vertical)
Jump cut agressivo + Redimensiona para 9:16 + Legendas grandes

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@content.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "remove_silence",
        "params": {
          "noise": "-28dB",
          "duration": 0.2
        }
      },
      {
        "type": "resize",
        "params": {
          "width": 1080,
          "height": 1920
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small",
          "style": {
            "color": "#FFFFFF",
            "highlight_color": "#FF00FF",
            "font": "Impact",
            "font_size": 48,
            "position": "center",
            "animation": "highlight-word"
          }
        }
      }
    ],
    "output_format": "mp4",
    "priority": 8
  }'
```

### Caso de Uso 5: Edição Completa de Screencast
Corta + Remove silêncios + Transcreve (sem queimar legendas)

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@screencast.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 3,
          "end": 600
        }
      },
      {
        "type": "remove_silence",
        "params": {
          "noise": "-35dB",
          "duration": 0.6
        }
      },
      {
        "type": "transcribe",
        "params": {
          "language": "pt",
          "model": "base"
        }
      }
    ],
    "output_format": "mp4",
    "priority": 6
  }'
```

### 💡 Dicas para Edição Completa

1. **Ordem das operações importa!**
   - Sempre faça `trim` primeiro (reduz tempo de processamento)
   - `remove_silence` antes de legendas (legendas sincronizam com vídeo editado)
   - `resize` antes de `watermark` (marca d'água se adapta ao tamanho)

2. **Performance:**
   - Trim primeiro economiza tempo em todas as operações seguintes
   - Use `priority` alta (7-9) para edições complexas
   - Configure `webhook_url` para vídeos longos

3. **Qualidade:**
   - Para conteúdo profissional: modelo `medium` ou `large`
   - Para redes sociais: modelo `small` é suficiente
   - Jump cuts muito agressivos (duration < 0.3s) podem parecer artificiais

---

## 10. Consultar Status do Job

Após enviar um vídeo para processamento, você recebe um `job_id`. Use-o para consultar o status.

### Exemplo:
```bash
curl -X GET "http://localhost:8000/api/v1/videos/status/{job_id}" \
  -H "X-API-Key: dev-secret-key"
```

### Resposta de Exemplo:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "download_url": "http://localhost:8000/downloads/output_video.mp4",
  "error_message": null,
  "created_at": "2026-01-31T10:30:00",
  "completed_at": "2026-01-31T10:35:00",
  "processing_time": 300
}
```

### Status possíveis:
- `pending`: Aguardando processamento
- `processing`: Em processamento
- `completed`: Concluído com sucesso
- `failed`: Falhou (veja `error_message`)

---

## 🎯 Parâmetros Adicionais da Requisição

### output_format
Formato do vídeo de saída. Valores aceitos:
- `mp4` (padrão)
- `avi`
- `mov`
- `mkv`
- `webm`

### priority
Prioridade do job (1-10). Valores maiores = maior prioridade.
- Padrão: 5
- Mínimo: 1
- Máximo: 10

### webhook_url
URL para receber notificação quando o processamento terminar.

```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [...],
    "output_format": "mp4",
    "priority": 8,
    "webhook_url": "https://myapp.com/webhook/video-processed"
  }'
```

---

## 🔄 Usando URL Pública ao invés de Upload

Você pode fornecer uma URL pública do vídeo ao invés de fazer upload do arquivo. Isso é útil quando o vídeo já está hospedado em algum lugar (S3, Google Drive, Dropbox, etc).

### ⚠️ Importante:
- **NÃO envie o parâmetro `video`** quando usar `video_url`
- Use `-F` para o JSON (não `-d`)
- A URL deve ser acessível publicamente

### Exemplo 1: Trim com URL pública
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F 'request={
    "video_url": "https://example.com/video.mp4",
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 0,
          "end": 30
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 2: Redimensionar vídeo de URL
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F 'request={
    "video_url": "https://storage.googleapis.com/my-bucket/video.mp4",
    "operations": [
      {
        "type": "resize",
        "params": {
          "width": 1280,
          "height": 720
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 3: Adicionar legendas em vídeo de URL
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F 'request={
    "video_url": "https://cdn.example.com/aula.mp4",
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small"
        }
      }
    ],
    "output_format": "mp4"
  }'
```

### Exemplo 4: Pipeline completo com URL
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F 'request={
    "video_url": "https://s3.amazonaws.com/my-videos/raw.mp4",
    "operations": [
      {
        "type": "trim",
        "params": {
          "start": 10,
          "end": 120
        }
      },
      {
        "type": "remove_silence",
        "params": {
          "noise": "-30dB",
          "duration": 0.5
        }
      },
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "medium"
        }
      }
    ],
    "output_format": "mp4",
    "priority": 8
  }'
```

### Exemplo 5: Transcrição de vídeo público (endpoint dedicado)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/transcribe" \
  -H "X-API-Key: dev-secret-key" \
  -F "video_url=https://example.com/palestra.mp4" \
  -F "language=pt" \
  -F "model=base"
```

---

## ⚠️ Limitações e Restrições

### Tamanho e Duração de Vídeos

**Não há limite explícito de duração ou tamanho de arquivo configurado no código**, mas existem considerações práticas:

#### 1. **Limites do FastAPI/Uvicorn**
- Por padrão, FastAPI não impõe limite de tamanho de upload
- Vídeos de **2 minutos, 10 minutos ou mais** são suportados
- O limite real depende da configuração do servidor web (Nginx, se usado)

#### 2. **Limites de Transcrição (Whisper)**
- Para transcrição via API OpenAI: **limite de 25MB por arquivo**
- Se o arquivo exceder 25MB, o sistema automaticamente divide em chunks
- Para Whisper local (faster-whisper): **sem limite de tamanho**

#### 3. **Considerações de Performance**

| Duração do Vídeo | Operação | Tempo Estimado | Recomendação |
|------------------|----------|----------------|--------------|
| 2 minutos | Trim/Resize | < 30 segundos | ✅ Rápido |
| 2 minutos | Auto Subtitle | 1-3 minutos | ✅ OK |
| 10 minutos | Trim/Resize | 1-2 minutos | ✅ OK |
| 10 minutos | Auto Subtitle | 5-15 minutos | ⚠️ Demorado |
| 30+ minutos | Auto Subtitle | 15-60 minutos | ⚠️ Muito demorado |
| 1+ hora | Qualquer operação | Variável | ⚠️ Use prioridade alta |

#### 4. **Modelos Whisper e Tempo de Processamento**

Para um vídeo de **10 minutos**:
- `tiny`: ~2-3 minutos (menos preciso)
- `base`: ~3-5 minutos (balanceado)
- `small`: ~5-8 minutos (boa precisão) ⭐ **Recomendado**
- `medium`: ~10-15 minutos (alta precisão)
- `large`: ~20-30 minutos (máxima precisão)

#### 5. **Limites de Recursos**

**Memória RAM:**
- Operações simples (trim, resize): ~500MB-1GB
- Transcrição com Whisper: 2-8GB dependendo do modelo
- Remove Silence: 1-3GB (precisa carregar vídeo completo)

**Disco:**
- Arquivos temporários podem ocupar 2-3x o tamanho do vídeo original
- Certifique-se de ter espaço suficiente em `/app/storage` e `/app/uploads`

#### 6. **Timeouts**

⚠️ **Importante**: Não há timeout configurado por padrão!

Para vídeos longos, considere:
- Usar `priority` alto (8-10) para processamento mais rápido
- Configurar `webhook_url` para receber notificação quando terminar
- Consultar o status periodicamente com `/status/{job_id}`

### Recomendações por Caso de Uso

#### ✅ **Ideal** (processamento rápido)
- Vídeos até 5 minutos
- Operações: trim, resize, watermark, merge
- Tempo total: < 5 minutos

#### ⚠️ **Aceitável** (processamento moderado)
- Vídeos de 5-15 minutos
- Operações: auto_subtitle (modelo small), remove_silence
- Tempo total: 5-20 minutos

#### 🔴 **Demorado** (requer paciência)
- Vídeos > 30 minutos
- Operações: auto_subtitle (modelo medium/large)
- Tempo total: 30+ minutos
- **Recomendação**: Use webhook para notificação

### Como Otimizar para Vídeos Longos

```bash
# Use prioridade alta e webhook
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_longo.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "small"
        }
      }
    ],
    "output_format": "mp4",
    "priority": 9,
    "webhook_url": "https://myapp.com/webhook/completed"
  }'
```

### Aumentar Limites (Configuração Avançada)

Se você precisar processar vídeos muito grandes, considere:

1. **Aumentar recursos do Docker:**
```yaml
# docker-compose.yml
services:
  worker:
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
```

2. **Usar GPU para Whisper:**
```bash
# .env
USE_GPU=true
```

3. **Configurar Nginx (se usado) para uploads grandes:**
```nginx
client_max_body_size 2G;
proxy_read_timeout 3600s;
```

---

## 📝 Notas Importantes

1. **Autenticação**: Todas as requisições precisam do header `X-API-Key`
2. **Formato JSON**: O parâmetro `request` deve ser um JSON válido
3. **Processamento Assíncrono**: As operações são processadas em background
4. **Consulta de Status**: Use o `job_id` retornado para verificar o progresso
5. **Upload vs URL**:
   - **Com arquivo**: Use `-F "video=@arquivo.mp4"` + `-F 'request={...}'`
   - **Com URL**: Use apenas `-F 'request={"video_url": "...", ...}'` (sem o parâmetro `video`)
   - **Não misture**: Envie OU arquivo OU URL, nunca ambos
6. **Modelos Whisper**: Modelos maiores são mais precisos mas mais lentos
   - `tiny`: Mais rápido, menos preciso
   - `base`: Balanceado
   - `small`: Boa precisão
   - `medium`: Alta precisão
   - `large`: Máxima precisão, mais lento
7. **Formatos de Tempo**: Aceita segundos (int/float) ou formato "HH:MM:SS"
8. **Operações em Cadeia**: São executadas sequencialmente na ordem especificada
9. **URLs Públicas**: Devem ser acessíveis sem autenticação (HTTP 200)

---

## 🚀 Documentação Interativa

Acesse a documentação Swagger em: `http://localhost:8000/docs`

---

**Desenvolvido com FastAPI, FFmpeg e OpenAI Whisper** 🎬
