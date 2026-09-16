---
task: "Optimize Prompts"
order: 2
input: |
  - base_prompts: Prompts iniciais criados na task anterior
  - anti_patterns: Lista de erros a evitar
output: |
  - optimized_prompts: Prompts finais com variações
  - variations: Pelo menos 1 variação alternativa por modelo
---

# Optimize Prompts

Revisar e otimizar os prompts criados, adicionando variações alternativas.

## Process

1. Revisar cada prompt contra a lista de anti-patterns
2. Verificar que cada prompt tem:
   - Iluminação com direção e cor (não genérica)
   - Composição com posição explícita do sujeito
   - Keywords de qualidade apropriadas ao modelo
   - Cores nomeadas e vibrantes
3. Otimizar ordem das keywords (mais importantes primeiro para Midjourney)
4. Criar 1-2 variações para cada modelo:
   - Variação A: mudança de ângulo de câmera (ex: low angle vs eye level)
   - Variação B: mudança de iluminação (ex: warm golden vs cool blue)
5. Verificar tamanho do prompt (ideal: 50-100 palavras para Midjourney, 100-200 para DALL-E)
6. Compilar entrega final

## Output Format

```yaml
final_delivery:
  primary:
    midjourney: "..."
    dalle: "..."
    flux: "..."
  variation_a:
    description: "..."
    midjourney: "..."
    dalle: "..."
    flux: "..."
  variation_b:
    description: "..."
    midjourney: "..."
  post_production:
    text: "..."
    font: "..."
    color: "..."
    position: "..."
    effects: "..."
  optimization_notes:
    - "..."
```

## Output Example

```yaml
final_delivery:
  primary:
    midjourney: "A young man with extreme shock expression, wide eyes and open mouth, looking at computer screen with green code being deleted, dramatic cool blue side lighting from monitor, dark navy background (#1a1a4e), cinematic close-up on left third of frame, photorealistic, rim light behind head, 85mm f/1.4 shallow DOF, 4K ultra detailed, vivid high-saturation colors --ar 16:9 --s 250 --q 2 --no text, watermark, blurry"
    dalle: "Create a photorealistic YouTube thumbnail in 16:9 landscape format (1280x720). A young man in his late 20s with dark hair and a shocked expression — eyes wide open, eyebrows fully raised, mouth open in an O shape — looking at a computer monitor to his right. The monitor displays green code (#00FF41) being crossed out by a red glowing cursor. Cool blue light (#4169E1) from the screen illuminates the left side of his face. Dark navy background (#1a1a4e). The man is in the left third of the frame, close-up from chest up. Clean empty space in the upper right corner for text overlay. High contrast, vivid colors, cinematic quality."
    flux: "Photorealistic close-up of a young man with intense shock — fully wide eyes, raised eyebrows, open mouth showing teeth — illuminated by cool blue computer screen light from the right side. Dark navy environment fading to black. Shot on Canon EOS R5 with 85mm f/1.4 lens, shallow depth of field creating soft bokeh behind. Natural skin texture with dramatic side shadows. High contrast between cool blue light and warm skin tones. Cinematic color grading, ultra resolution."
  variation_a:
    description: "Low angle shot (mais imponente e dramático)"
    midjourney: "A young man shot from slightly below eye level with extreme shock expression, wide eyes and open mouth, looking up at floating holographic code being deleted, dramatic blue uplight, dark background, cinematic low angle close-up, photorealistic, volumetric light rays, 35mm wide angle f/2.8, 4K ultra detailed, vivid neon colors --ar 16:9 --s 250 --q 2 --no text, watermark"
    dalle: "..."
    flux: "..."
  variation_b:
    description: "Warm/red lighting (mais urgência e perigo)"
    midjourney: "A young man with extreme shock expression, wide eyes and open mouth, bathed in dramatic red warning light from computer screen showing code errors, dark background, cinematic close-up on left third, photorealistic, red and orange rim light, 85mm f/1.4 shallow DOF, 4K, vivid red and orange against black --ar 16:9 --s 250 --q 2 --no text, watermark"
  post_production:
    text: "ACABOU?"
    font: "Bebas Neue Extra Bold (primary) or Impact (fallback)"
    color: "Amarelo vibrante (#FFD700) com outline preto (#000000) de 12px"
    position: "Upper right quadrant, ocupando 25% do frame width"
    effects: "Stroke preto 12px outside, drop shadow 4px offset 50% opacity"
  optimization_notes:
    - "Reordenei keywords do Midjourney por importância (sujeito primeiro)"
    - "Adicionei espaço limpo para texto no prompt DALL-E"
    - "Variação A usa ângulo low para mais drama"
    - "Variação B troca azul por vermelho para sensação de urgência"
```

## Quality Criteria

- [ ] Todos os prompts verificados contra anti-patterns
- [ ] Pelo menos 1 variação completa (3 modelos)
- [ ] Notas de otimização explicando mudanças
- [ ] Tamanho dos prompts dentro do ideal (50-100 MJ, 100-200 DALL-E)
- [ ] Instruções de pós-produção finalizadas

## Veto Conditions

1. Prompts finais idênticos aos iniciais (sem otimização feita)
2. Zero variações oferecidas
