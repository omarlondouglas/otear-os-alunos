# Research Brief — YouTube Thumbnail Creation

## Domain 1: YouTube Thumbnail Psychology & CTR

### Psychological Triggers
- **1.8 segundos**: tempo médio que um viewer tem para processar uma thumbnail no feed
- **Curiosity Gap**: criar tensão visual que só se resolve assistindo o vídeo. Aumenta CTR em até 50% (HubSpot)
- **Facial Recognition Priority**: rostos humanos são processados prioritariamente pelo cérebro
- **Emotional Intensity**: thumbnails com alta intensidade emocional são 2x mais clicadas

### Dados de CTR (fontes: TubeBuddy 2025, VidIQ 2025)
| Elemento | Impacto no CTR |
|----------|---------------|
| Rosto na thumbnail | +35-50% |
| Expressão emocional autêntica | +42.3% (estudo 1.2M vídeos) |
| Cores contrastantes (vermelho/amarelo) | +20-30% |
| Texto com menos de 4 palavras | +30% vs text-heavy |
| Alta intensidade emocional | 2x mais cliques |
| Thumbnails AI-generated otimizadas | +37% CTR médio |

### Tendências 2025-2026
- **Proof of Human (POH)**: texturas de pele reais, imperfeições visíveis
- **3D Depth Layering**: camadas de profundidade com sujeito em primeiro plano
- **Thumbnails personalizadas A/B**: MrBeast testa 50+ variações por vídeo
- **Design flat minimalista está sendo penalizado** pelo algoritmo

### Alinhamento Thumbnail-Conteúdo
YouTube prioriza watch time sobre cliques. Thumbnails com alto CTR mas baixa retenção prejudicam o vídeo no algoritmo de recomendação.

---

## Domain 2: Design Visual & Hierarquia para Thumbnails

### Composição
- **Regra dos Terços**: posicionar sujeito principal e texto nas interseções do grid
- **Regra 60-30-10**: 60% cor dominante (fundo), 30% cor secundária (sujeito), 10% accent (texto/destaque)
- **Um conceito por thumbnail**: se alguém não entende a mensagem em 1 segundo, simplificar
- **Linhas diagonais e gestos de apontar** guiam o olhar do viewer

### Tipografia
- **Fontes recomendadas**: Impact, Bebas Neue, Montserrat Extra Bold, Obelix Pro (MrBeast)
- **Peso mínimo**: 700 (bold) — fontes regulares ficam ilegíveis em tamanho pequeno
- **Máximo 3-5 palavras** — texto deve cobrir 20-30% do frame
- **Máximo 2 fontes**: uma para headline, uma para accent
- **Outline obrigatório**: stroke preto 10-15px ao redor do texto branco
- **Texto levemente curvado** (arc ou bulge) adiciona dinamismo

### Contraste
- Ratio mínimo texto/fundo: 4.5:1 (WCAG AA)
- Drop shadows ou outlines para legibilidade em qualquer fundo
- **Teste P&B**: converter para preto e branco — se todos elementos são distinguíveis, o contraste está bom
- **Teste mobile**: reduzir para 168×94px — se a mensagem é clara, a thumbnail funciona

### Cores
- MrBeast: amarelos vibrantes, vermelhos intensos, azuis vívidos — saturação 100%
- Nunca usar cores apagadas/muted
- Cores quentes (vermelho, amarelo, laranja) geram mais urgência
- Contraste complementar: vermelho vs verde, amarelo vs preto

---

## Domain 3: YouTube Algorithm & CTR Data

### Benchmarks de CTR por Nicho
- CTR médio geral: 2-10%
- Canais grandes (1M+): 4-8%
- Canais educacionais: 3-6%
- Canais de entretenimento: 5-12%
- MrBeast: estimado 15-20%+ consistentemente

### Como o Algoritmo Usa CTR
1. **Impressions CTR**: % de pessoas que clicam após ver a thumbnail
2. **YouTube testa thumbnails** nos primeiros 48h — alto CTR = mais impressões
3. **Watch time x CTR**: o algoritmo equilibra ambos. Clickbait com baixa retenção é penalizado
4. **Browse features e Suggested**: CTR impacta diretamente posicionamento nestas seções

---

## Domain 4: Geração de Imagens com IA para Thumbnails

### Comparação de Modelos
| Modelo | Melhor Para | Limitação |
|--------|-------------|-----------|
| Midjourney v7 | Rostos fotorealistas, composição cinematográfica | Texto em imagens fraco |
| DALL-E 3 | Texto legível na imagem, seguir instruções literais | Rostos menos realistas |
| Flux 2 | Fotorealismo, pele natural, iluminação | Menos controle estilístico |
| Imagen 4 (Google) | Qualidade geral alta | Acesso limitado |

### Estrutura de Prompt Eficaz
1. **Sujeito**: quem/o que está na imagem
2. **Ação/Emoção**: o que o sujeito está fazendo/sentindo
3. **Composição**: enquadramento, ângulo de câmera
4. **Estilo**: fotorealístico, cinematográfico, ilustração
5. **Iluminação**: tipo de luz, direção, intensidade
6. **Cores**: palette dominante, esquema de cores
7. **Detalhes técnicos**: resolução (4K, 8K), render engine, aspect ratio
8. **Texto overlay**: indicar texto separadamente (melhor adicionado em pós-produção)

### Keywords de Qualidade
- Resolução: `4K, 8K, ultra HD, photorealistic, hyperrealistic`
- Render: `Octane render, Unreal Engine 5, cinematic lighting`
- Câmera: `shot on Canon EOS R5, 85mm lens, f/1.4, bokeh`
- Iluminação: `dramatic side lighting, golden hour, studio lighting, rim light`

### Aspect Ratio
- YouTube thumbnail: **16:9** (1280×720px)
- Midjourney: `--ar 16:9`
- DALL-E: especificar "landscape format, 16:9 aspect ratio"

### Limitações Críticas
- **Texto em imagens**: NENHUM modelo gera texto perfeitamente. Melhor adicionar texto em pós (Canva, Photoshop)
- **Rostos específicos**: IA não pode replicar rostos reais sem fine-tuning. Prompts devem descrever "a person" genérico ou usar LoRA/referência
- **Consistência**: cada geração é única. Para manter identidade visual, usar seeds/referências

### Dicas por Modelo
**Midjourney v7:**
- `--ar 16:9 --s 250 --q 2` para máxima qualidade
- Draft Mode para gerar variações rápidas
- `--style raw` para menos estilização

**DALL-E 3:**
- Melhor para thumbnails que precisam de texto legível na imagem
- Ser muito literal e descritivo no prompt
- Especificar "YouTube thumbnail style, bold colors, high contrast"

**Flux 2:**
- Excelente para pele natural e iluminação realista
- Usar descritores de câmera para fotorealismo
- Bom para thumbnails estilo documentário/vlog
