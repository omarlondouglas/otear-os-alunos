---
task: "Create AI Image Prompts"
order: 1
input: |
  - selected_concept: Conceito detalhado aprovado pelo usuário
  - research_brief: Conhecimento sobre prompts de IA
  - output_examples: Exemplos de prompts de referência
output: |
  - midjourney_prompt: Prompt otimizado para Midjourney v7
  - dalle_prompt: Prompt otimizado para DALL-E 3
  - flux_prompt: Prompt otimizado para Flux 2
  - post_production: Instruções de texto overlay
---

# Create AI Image Prompts

Transformar o conceito visual detalhado em 3 prompts otimizados, um para cada modelo de IA.

## Process

1. Ler o conceito selecionado e seus detalhes expandidos
2. Extrair os elementos visuais chave: sujeito, expressão, composição, cores, iluminação, fundo
3. **Prompt Midjourney v7**:
   - Linguagem descritiva fluida, como narração de cena
   - Incluir: subject + action/emotion + composition + style + lighting + colors + quality keywords
   - Parâmetros: --ar 16:9 --s 250 --q 2
   - Usar keywords: photorealistic, cinematic, dramatic lighting, 4K, ultra detailed
   - Para excluir: --no text, watermark, blurry
4. **Prompt DALL-E 3**:
   - Instruções literais e específicas, como briefing para fotógrafo
   - Começar com "Create a photorealistic YouTube thumbnail in 16:9 landscape format"
   - Descrever cada elemento separadamente com posição no frame
   - Pode incluir texto curto (2-3 palavras) — DALL-E renderiza texto melhor
5. **Prompt Flux 2**:
   - Focar em descritores de câmera e iluminação para fotorealismo
   - Enfatizar: natural skin texture, cinematic color grading
   - Incluir focal length e depth of field
   - Não pedir texto na imagem
6. Criar instruções de pós-produção para texto overlay

## Output Format

```yaml
prompts:
  midjourney:
    prompt: "..."
    parameters: "--ar 16:9 --s 250 --q 2"
    negative: "--no text, watermark, blurry, low quality"
  dalle:
    prompt: "..."
  flux:
    prompt: "..."
  post_production:
    text: "..."
    font: "..."
    color: "... (#hex)"
    position: "..."
    effects: "..."
```

## Output Example

```yaml
prompts:
  midjourney:
    prompt: "A young man with wide-eyed shock expression looking at a computer screen displaying lines of code being automatically deleted, dramatic blue side lighting from the monitor illuminating his face against dark navy background, cinematic composition with subject on the left third, photorealistic, dramatic rim light, shot on 85mm f/1.4, shallow depth of field with bokeh, 4K ultra detailed, vivid high-contrast colors, YouTube thumbnail style"
    parameters: "--ar 16:9 --s 250 --q 2"
    negative: "--no text, watermark, blurry, low quality, muted colors"
  dalle:
    prompt: "Create a photorealistic YouTube thumbnail in 16:9 landscape format. A young man in his late 20s with an expression of genuine shock — wide eyes, raised eyebrows, open mouth — is looking at a computer monitor on his right. The monitor screen shows green lines of code being crossed out by a glowing red cursor. The scene has dramatic blue lighting from the computer screen on the left side of his face, with a dark navy blue (#1a1a4e) background. The man is positioned on the left third of the frame. High contrast, vivid saturated colors, cinematic quality, 4K resolution."
  flux:
    prompt: "Photorealistic close-up portrait of a young man with shocked expression — wide eyes, raised eyebrows, open mouth — illuminated by cool blue computer screen light from the right. Dark navy environment. Dramatic side lighting creating deep shadows. Shot on Canon EOS R5 85mm f/1.4, shallow depth of field. Natural skin texture, high color contrast with vivid blues against warm skin tones. Cinematic color grading, ultra high resolution."
  post_production:
    text: "ACABOU?"
    font: "Bebas Neue Extra Bold or Impact"
    color: "Amarelo vibrante (#FFD700) com outline preto 12px"
    position: "Canto superior direito, ocupando ~25% do frame width"
    effects: "Outline preto 12px, drop shadow sutil para profundidade"
```

## Quality Criteria

- [ ] 3 prompts distintos adaptados a cada modelo
- [ ] Midjourney inclui --ar 16:9 e parâmetros
- [ ] DALL-E começa com formato e dimensão
- [ ] Flux enfatiza naturalidade e câmera
- [ ] Cores vibrantes especificadas em todos
- [ ] Iluminação detalhada em todos
- [ ] Instruções de pós-produção completas

## Veto Conditions

1. Qualquer prompt sem aspect ratio 16:9
2. Prompt pedindo mais de 3 palavras de texto renderizado na imagem
3. Mesmo prompt copiado entre modelos sem adaptação
