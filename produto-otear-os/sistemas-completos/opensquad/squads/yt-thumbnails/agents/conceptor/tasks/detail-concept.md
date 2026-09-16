---
task: "Detail Selected Concept"
order: 2
input: |
  - selected_concept: Conceito escolhido pelo usuário
  - anti_patterns: Lista de erros a evitar
output: |
  - detailed_concept: Conceito expandido com especificações para prompt engineering
---

# Detail Selected Concept

Expandir o conceito selecionado pelo usuário com especificações adicionais necessárias para gerar prompts de IA de alta qualidade.

## Process

1. Ler o conceito selecionado pelo usuário (do checkpoint)
2. Expandir cada elemento com detalhes técnicos para prompt engineering:
   - Sujeito: idade aparente, vestuário, posição no frame (% exato)
   - Expressão: descrição anatômica detalhada (músculos faciais, direção do olhar)
   - Iluminação: tipo (key, fill, rim), direção, intensidade, cor
   - Câmera: ângulo (eye level, low angle), distância focal equivalente, profundidade de campo
   - Background: camadas (foreground, midground, background), blur, elementos
3. Definir espaço reservado para texto overlay (posição exata, % do frame)
4. Verificar contra anti-patterns uma última vez
5. Adicionar notas de direção por modelo de IA (o que enfatizar para cada um)

## Output Format

```yaml
detailed_concept:
  name: "..."
  subject:
    description: "..."
    age_range: "..."
    clothing: "..."
    position_in_frame: "..."
    size_in_frame: "...%"
  expression:
    overall: "..."
    eyes: "..."
    eyebrows: "..."
    mouth: "..."
    hands: "..." 
    gaze_direction: "..."
  lighting:
    key_light: "..."
    fill_light: "..."
    rim_light: "..."
    color_temperature: "..."
  camera:
    angle: "..."
    focal_length: "..."
    depth_of_field: "..."
    distance: "..."
  background:
    layers: ["..."]
    blur: "..."
  text_overlay_space:
    position: "..."
    size: "...% of frame"
  model_notes:
    midjourney: "..."
    dalle: "..."
    flux: "..."
```

## Output Example

```yaml
detailed_concept:
  name: "Choque Digital"
  subject:
    description: "Homem jovem, pele clara, cabelo curto escuro"
    age_range: "25-35"
    clothing: "Camiseta preta simples, sem logo visível"
    position_in_frame: "Lado esquerdo, rosto centrado no 1/3 esquerdo"
    size_in_frame: "40%"
  expression:
    overall: "Choque genuíno e intenso"
    eyes: "Arregalados ao máximo, pupilas dilatadas, sobrancelhas levantadas 2cm acima da posição normal"
    eyebrows: "Arqueadas e elevadas, criando rugas na testa"
    mouth: "Aberta em formato oval, lábios afastados mostrando dentes superiores"
    hands: "Ambas nas bochechas, dedos abertos, estilo Macaulay Culkin"
    gaze_direction: "Olhando diretamente para a câmera (eye contact com viewer)"
  lighting:
    key_light: "Lateral esquerda, azul frio (#4169E1), intensidade alta"
    fill_light: "Verde suave (#00FF41) vindo da tela de código à direita"
    rim_light: "Rim light branco sutil atrás da cabeça para separar do fundo"
    color_temperature: "Frio (6500K+), sensação noturna/tech"
  camera:
    angle: "Eye level, ligeiramente abaixo (5 graus) para dar presença"
    focal_length: "85mm equivalente"
    depth_of_field: "Shallow — rosto sharp, fundo com bokeh suave"
    distance: "Close-up, corte nos ombros"
  background:
    layers:
      - "Foreground: nenhum"
      - "Midground: tela de computador com código verde sendo deletado"
      - "Background: escuridão com partículas de código flutuando, bokeh"
    blur: "Gradual — midground levemente blur, background muito blur"
  text_overlay_space:
    position: "Canto superior direito"
    size: "25% do frame"
  model_notes:
    midjourney: "Enfatizar dramatic lighting e bokeh. Usar --s 250 para mais estilização"
    dalle: "Ser literal na descrição do cenário. Pode pedir texto 'ACABOU?' diretamente"
    flux: "Focar na naturalidade da pele e iluminação. Usar descritores de câmera"
```

## Quality Criteria

- [ ] Todos os campos preenchidos com especificações técnicas
- [ ] Iluminação detalhada (tipo, direção, cor)
- [ ] Câmera especificada (ângulo, focal, DoF)
- [ ] Espaço para texto overlay definido
- [ ] Notas por modelo incluídas

## Veto Conditions

1. Expressão facial descrita com adjetivos genéricos em vez de descrição anatômica
2. Sem especificação de iluminação
