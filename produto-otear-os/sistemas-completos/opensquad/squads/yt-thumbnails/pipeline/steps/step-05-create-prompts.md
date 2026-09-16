---
execution: inline
agent: squads/yt-thumbnails/agents/prompt-engineer
inputFile: squads/yt-thumbnails/output/thumbnail-concepts.md
outputFile: squads/yt-thumbnails/output/thumbnail-prompts.md
---

# Step 05: Criar Prompts de IA

## Context Loading

Load these files before executing:
- `squads/yt-thumbnails/output/thumbnail-concepts.md` — conceito aprovado pelo usuário
- `squads/yt-thumbnails/pipeline/data/research-brief.md` — conhecimento sobre prompts de IA
- `squads/yt-thumbnails/pipeline/data/output-examples.md` — exemplos de prompts
- `squads/yt-thumbnails/pipeline/data/anti-patterns.md` — erros a evitar em prompts

## Instructions

### Process
1. Ler o conceito selecionado pelo usuário
2. Decompor o conceito em elementos do prompt: sujeito, ação/emoção, composição, estilo, iluminação, cores, detalhes técnicos
3. Gerar prompt otimizado para **Midjourney v7**:
   - Usar linguagem descritiva natural
   - Incluir parâmetros: --ar 16:9 --s 250 --q 2
   - Keywords de qualidade: photorealistic, cinematic, dramatic lighting
4. Gerar prompt otimizado para **DALL-E 3**:
   - Ser literal e descritivo
   - Especificar "YouTube thumbnail in 16:9 landscape format"
   - Incluir instruções de texto se o conceito requer texto na imagem
5. Gerar prompt otimizado para **Flux 2**:
   - Focar em descritores de câmera e iluminação
   - Enfatizar "natural skin texture" para rostos
   - Usar estilo fotorealista
6. Para cada prompt, adicionar nota sobre texto overlay em pós-produção
7. Revisar cada prompt contra anti-patterns (texto demais na imagem, cores apagadas, composição lotada)

## Output Format

```markdown
# Prompts de Thumbnail: {tema do vídeo}

## Conceito Selecionado: {nome do conceito}

### Prompt Midjourney v7
```
{prompt completo com parâmetros}
```

### Prompt DALL-E 3
```
{prompt completo}
```

### Prompt Flux 2
```
{prompt completo}
```

### Nota sobre Texto Overlay
- **Texto**: {palavras}
- **Fonte recomendada**: {nome da fonte}
- **Cor**: {cor com hex code}
- **Posição**: {onde no frame}
- **Efeitos**: {outline, shadow, glow}

### Variação A (opcional)
{prompt com ajuste de ângulo de câmera ou iluminação}

### Variação B (opcional)
{prompt com ajuste de cor ou composição}
```

## Output Example

```markdown
# Prompts de Thumbnail: Como IA vai substituir programadores

## Conceito Selecionado: Choque Digital

### Prompt Midjourney v7
```
A young man with wide-eyed shock expression looking at a computer screen displaying lines of green code being automatically deleted, dramatic cool blue side lighting from the monitor illuminating his face, dark navy blue background (#1a1a4e), cinematic composition with subject on the left third of frame, photorealistic, dramatic rim light behind head, shot on 85mm f/1.4, shallow depth of field with bokeh, 4K ultra detailed, vivid high-saturation colors, YouTube thumbnail style --ar 16:9 --s 250 --q 2 --no text, watermark, blurry, muted colors
```

### Prompt DALL-E 3
```
Create a photorealistic YouTube thumbnail in 16:9 landscape format (1280x720). A young man in his late 20s with an expression of genuine shock — wide eyes, raised eyebrows, mouth open in an O shape — is looking at a computer monitor to his right. The monitor screen shows green lines of code (#00FF41) being crossed out by a glowing red cursor. Cool blue light (#4169E1) from the screen illuminates the left side of his face against a dark navy blue background (#1a1a4e). The man is positioned on the left third of the frame, close-up from chest up. Clean empty space in upper right corner for text overlay. High contrast, vivid saturated colors, cinematic quality, 4K resolution.
```

### Prompt Flux 2
```
Photorealistic close-up portrait of a young man with intense shock expression — fully wide open eyes, raised eyebrows creating forehead wrinkles, mouth open showing upper teeth — illuminated by cool blue computer screen light from the right side. Dark navy environment fading to black. Shot on Canon EOS R5 85mm f/1.4, shallow depth of field creating soft bokeh. Natural skin texture with dramatic side shadows. High contrast between vivid blue light and warm skin tones. Cinematic color grading, ultra high resolution.
```

### Nota sobre Texto Overlay
- **Texto**: "ACABOU?"
- **Fonte**: Bebas Neue Extra Bold ou Impact
- **Cor**: Amarelo vibrante (#FFD700) com outline preto (#000000) 12px
- **Posição**: Canto superior direito, ocupando ~25% do frame width
- **Efeitos**: Stroke preto 12px outside, drop shadow sutil 4px

### Variação A: Low Angle (mais dramático)
```
A young man shot from slightly below eye level with extreme shock expression, looking up at floating holographic code being deleted by red light, dramatic blue uplight illuminating face from below, dark background, cinematic low angle close-up, photorealistic, volumetric light rays, 35mm f/2.8, 4K, vivid neon blue and green colors --ar 16:9 --s 250 --q 2 --no text, watermark
```
```

## Veto Conditions

Reject and redo if ANY are true:
1. Prompt Midjourney não inclui --ar 16:9
2. Algum prompt pede renderização de mais de 3 palavras de texto na imagem
3. Prompts não especificam iluminação
4. Cores do prompt não correspondem ao conceito aprovado

## Quality Criteria

- [ ] 3 versões de prompt (Midjourney, DALL-E, Flux)
- [ ] Todos os prompts incluem aspect ratio 16:9
- [ ] Texto overlay é tratado como pós-produção, não gerado na imagem
- [ ] Iluminação especificada em cada prompt
- [ ] Cores vibrantes e contrastantes em cada prompt
- [ ] Keywords de qualidade presentes (4K, photorealistic, etc.)
- [ ] Pelo menos 1 variação oferecida
