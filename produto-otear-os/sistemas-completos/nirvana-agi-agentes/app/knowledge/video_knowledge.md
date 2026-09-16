# Video Editing Knowledge Base for Agents

This document contains everything an AI Agent needs to know to edit videos.

---

## 0. PROCESSO OBRIGATÓRIO DE SELEÇÃO VIRAL (MODO VIRAL)

**NUNCA corte um vídeo sem DETECTAR, APRESENTAR e o USUÁRIO ESCOLHER. O processo é SEMPRE:**

### Passo 1: Detectar Momentos Virais (AUTOMÁTICO)

Chame `detect_viral_moments_tool(video_url=URL, top_percent=30)`.

Esta tool faz automaticamente:
- Análise de ENERGIA DO ÁUDIO (volume, intensidade vocal) janela por janela
- Transcrição completa com timestamps
- Identificação dos momentos de MAIOR energia (quando o apresentador fala com mais força/emoção)
- Retorna highlights ranqueados com texto, timestamps e score

### Passo 2: Enriquecer com Análise de Conteúdo

Para cada highlight retornado, some ao energy_score uma pontuação de conteúdo:

| Score | Critério | Exemplo |
|-------|----------|---------|
| +5 | Gancho forte (pergunta retórica, dado chocante, polêmica) | "Ninguém te conta isso, mas..." |
| +4 | Dado/estatística com número específico | "90% das empresas falham nos primeiros 2 anos" |
| +4 | Frase quotable/compartilhável | "Dinheiro não compra felicidade, mas paga a terapia" |
| +3 | Emoção forte (raiva, surpresa, humor) | Momento de risada, indignação genuína |
| +3 | Opinião forte e clara / controvérsia | "Faculdade é a maior mentira do século" |
| +3 | História pessoal com vulnerabilidade | "Eu quebrei 3 vezes antes de acertar" |
| +2 | Dica prática e acionável | "Abra o Instagram, vá em configurações..." |
| +1 | Contexto mínimo necessário para alto-score | Frase de setup para uma punchline |
| 0 | Explicação genérica, introdução vaga | "Então pessoal, hoje vamos falar sobre..." |
| -2 | Enrolação, repetição, tangente | Repete a mesma ideia 3 vezes |
| -3 | Autopromoção, filler | "Se inscreva, ative o sininho..." |

**SCORE FINAL = (energy_score / 2) + content_score**

### Passo 3: APRESENTAR ao Usuário (OBRIGATÓRIO — NÃO PULAR)

Mostre uma tabela com TODOS os highlights detectados:
- Tempo (início-fim)
- Duração
- Score final
- Texto resumido do que é dito

Pergunte: "Quais momentos quer manter? Todos, só os TOP N, ou escolhe manualmente?"

### Passo 4: Executar o corte

Só APÓS o usuário confirmar, chame `edit_video_tool` com `smart_cut` usando os timestamps escolhidos.

### ERROS COMUNS
- Usar preset='VIRAL' para corte estratégico (preset VIRAL SÓ adiciona legenda, NÃO faz smart_cut)
- Cortar sem chamar detect_viral_moments_tool primeiro
- Cortar sem apresentar os candidatos e pedir confirmação do usuário
- Manter trechos de score 0 ou negativo
- Gerar keep_segments com o vídeo inteiro

---

## 1. Smart Cut (Corte Inteligente)

The `smart_cut` operation allows you to keep specific segments of a video and remove the rest. This is essential for:
- Removing silence while keeping "hooks" intact.
- Extracting the best parts of a long video.
- Reordering segments.

### Usage
```json
{
  "operation_type": "smart_cut",
  "params": {
    "keep_segments": [
      [0.0, 5.5],   // Keep from 0s to 5.5s
      [10.2, 15.0], // Keep from 10.2s to 15.0s
      [20.0, 25.0]  // Keep from 20.0s to 25.0s
    ]
  }
}
```

---

## 2. Animation Effects (Auto Subtitles)

When using `auto_subtitle`, you can apply specific animations to make the video more engaging.

### Available Animations

| Animation | Description | Best For |
|-----------|-------------|----------|
| `highlight-word` | Highlights each word as it is spoken (Karaoke style). | Educational, Reels, TikTok, Accessibility. |
| `typewriter` | Types text character by character. | Tech tutorials, dramatic intros, storytelling. |
| `none` (default) | Static text. | Formal content, corporate videos. |

### Parameters

- `animation`: Name of the animation (`highlight-word`, `typewriter`).
- `highlight_color`: Color of the active word (for `highlight-word`). Default: `#FFFF00` (Yellow).
- `typewriter_speed`: Speed in chars/sec (for `typewriter`). Recommended: 20-25.

### Examples

**Viral Dynamic Style (Reels/Shorts):**
```json
{
  "operation_type": "auto_subtitle",
  "params": {
    "style": {
      "font_size": 10,
      "color": "#FFFFFF",
      "highlight_color": "#FFFF00",
      "animation": "highlight-word",
      "position": "bottom"
    }
  }
}
```

**Tech/Hacker Style:**
```json
{
  "operation_type": "auto_subtitle",
  "params": {
    "style": {
      "font": "Courier New",
      "color": "#00FF00",
      "animation": "typewriter",
      "typewriter_speed": 25,
      "position": "bottom"
    }
  }
}
```

---

## 3. Text Overlays (Tarjas e Títulos)

Use `add_text_overlay` to add headlines, lower thirds, or CTAs.

### Positioning

- `"top"`, `"bottom"` (default), `"center"`
- `"top-left"`, `"top-right"`, `"bottom-left"`, `"bottom-right"`

### Styling

- `box`: `true` (default) to show background box.
- `box_color`: Hex code (e.g., `#000000`).
- `box_opacity`: 0.0 to 1.0.
- `box_padding`: Padding in pixels.

### Examples

**Big Headline (Top):**
```json
{
  "operation_type": "add_text_overlay",
  "params": {
    "text": "MY TITLE",
    "position": "top",
    "font_size": 60,
    "box_color": "#000000",
    "box_opacity": 0.8
  }
}
```

**Lower Third (Name):**
```json
{
  "operation_type": "add_text_overlay",
  "params": {
    "text": "John Doe\nCEO",
    "position": "bottom-left",
    "font_size": 30,
    "start_time": 2,
    "duration": 5
  }
}
```

---

## 4. Combinations

You can combine `smart_cut` with other operations in a single `edit_video_tool` call using the `operations` list.

**Example: Cut Video + Add Headline + Add Subtitles**
```python
edit_video_tool(
    video_url="...",
    operations=[
        {
            "type": "smart_cut",
            "params": {"keep_segments": [[0, 10], [15, 20]]}
        },
        {
            "type": "add_text_overlay",
            "params": {"text": "INSANE TRICK!", "position": "top"}
        },
        {
            "type": "auto_subtitle",
            "params": {"style": {"animation": "highlight-word"}}
        }
    ]
)
```

---

## 5. Pre-Flight: Analisar o Vídeo Antes de Editar

Sempre chame `get_video_info_tool(video_url)` antes de qualquer edição. Retorna:

```json
{
  "duration_seconds": 2340,
  "duration_human": "39m 0s",
  "width": 1920,
  "height": 1080,
  "fps": 30.0,
  "codec": "h264",
  "estimated_size_mb": 1240.5,
  "is_long_video": true,
  "processing_estimate_minutes": 58.5
}
```

### Tabela de Decisão por Duração

| Duração | Ação |
|---------|------|
| < 5 min | Processar diretamente, espera < 5 min |
| 5-20 min | Informar usuário de ~10-30 min de espera |
| 20-40 min | Informar usuário, usar `max_wait_seconds=3600` |
| > 40 min | Sugerir trim primeiro para reduzir processamento |

### Escala de font_size por Resolução

| Resolução (height) | font_size recomendado |
|--------------------|-----------------------|
| >= 1080px | 12 |
| >= 720px | 10 |
| < 720px | 8 |

### Pipeline Completo para Vídeo Longo (MODO VIRAL)

```python
# 1. Analisar primeiro
info = get_video_info_tool(video_url="https://...")
# → duration: 39m, height: 1080, processing: 58.5 min

# 2. Detectar momentos virais (análise de áudio + transcrição)
highlights = detect_viral_moments_tool(video_url="https://...", top_percent=30)
# → Retorna highlights ranqueados com texto, timestamps, energy_score

# 3. APRESENTAR ao usuário e esperar confirmação
# Mostrar tabela com highlights, perguntar quais manter

# 4. Após confirmação, cortar com smart_cut
font_size = 12 if info["height"] >= 1080 else 10
edit_video_tool(
    video_url="https://...",
    operations=[
        {"type": "smart_cut", "params": {"keep_segments": highlights["suggested_clips"]}},
        {"type": "auto_subtitle", "params": {"style": {
            "animation": "highlight-word",
            "color": "#FFFF00",
            "font_size": font_size,
            "position": "bottom",
            "margin_vertical": 80
        }}}
    ],
    max_wait_seconds=7200
)
```

---

## 6. Presets Disponíveis

### Presets Básicos (FFmpeg)

| Preset | Descrição | Posição das Legendas |
|--------|-----------|---------------------|
| `AULA` | Remove respiros/silêncios, preserva conteúdo | bottom (margin 60) |
| `VIRAL` | Legendas amarelas word-by-word + remove silêncio | bottom (margin 80) |
| `MODERN_SUBTITLES` | Legendas brancas com highlight-word | bottom (margin 60) |
| `CLEAN` | Legendas brancas highlight-word + remove silêncio | bottom (margin 50) |
| `REACTION` | Overlay de reação + legendas brancas | bottom (margin 20) |

### Presets PRO (Remotion - efeitos avançados)

| Preset | Descrição | Melhor Para |
|--------|-----------|-------------|
| `VIRAL_PRO` | Legendas Hormozi + zoom + transições + barra progresso | Reels/TikTok premium |
| `AULA_PRO` | Legendas karaoke profissionais + transições suaves | Cursos premium |
| `HORMOZI` | Estilo Alex Hormozi - legendas gigantes, punch zoom | Alto impacto |
| `PODCAST` | Layout 16:9, zoom no rosto, intro/outro | YouTube/Podcasts |

### Remotion: Capacidades Avançadas

- **Legendas:** hormozi, karaoke, bounce, typewriter, static
- **Transições:** fade, slide-left, slide-right, slide-up, wipe, zoom, blur
- **Zoom:** auto-face, ken-burns, punch, slow-zoom-in, slow-zoom-out
- **Hooks visuais:** wait-for-it, pov, watch-till-end, arrow, circle
- **Lower thirds:** modern, minimal, corporate, neon
- **B-Roll:** fullscreen, left, right, pip-top-right, pip-bottom-left
- **Branding:** intro (minimal/energetic/corporate), outro (cta/subscribe/follow)
- **Formatos:** ViralVideo (9:16), YouTubeVideo (16:9), SquareVideo (1:1)

Para uso customizado com `remotion_render`, consulte a documentação no knowledge base.

