# Anti-Patterns — YouTube Thumbnail Prompts

## Never Do

### 1. Texto demais no prompt de imagem
**Problema**: Pedir ao modelo de IA para renderizar mais de 2-3 palavras de texto na imagem. Nenhum modelo atual gera texto perfeito consistentemente.
**Consequência**: Texto ilegível, letras trocadas, caracteres estranhos.
**Solução**: Gerar a imagem SEM texto e adicionar texto em pós-produção (Canva/Photoshop).

### 2. Cores apagadas ou palette muted
**Problema**: Usar tons pastéis, cinzas, ou cores de baixa saturação.
**Consequência**: Thumbnail invisível no feed do YouTube. Perde para competidores com cores vibrantes. CTR cai 20-30%.
**Solução**: Sempre especificar "vivid colors, high saturation, bold contrast" no prompt.

### 3. Composição lotada
**Problema**: Incluir muitos elementos, objetos ou detalhes no prompt.
**Consequência**: Thumbnail confusa, mensagem não é clara em 1.8 segundos. Viewer não entende e passa.
**Solução**: Um sujeito principal + um elemento de contexto + fundo limpo. Máximo 3 elementos focais.

### 4. Expressões faciais genéricas
**Problema**: Descrever emoções vagas como "happy" ou "sad" no prompt.
**Consequência**: IA gera expressão neutra ou artificial. Sem gatilho emocional, sem cliques.
**Solução**: Descrever fisicamente a expressão: "wide-eyed with raised eyebrows and open mouth showing genuine shock" em vez de "surprised face".

### 5. Ignorar aspect ratio
**Problema**: Não especificar 16:9 no prompt.
**Consequência**: Imagem quadrada ou portrait que será cortada pelo YouTube, perdendo elementos importantes.
**Solução**: SEMPRE incluir --ar 16:9 (Midjourney) ou "landscape 16:9 format" (DALL-E/Flux).

### 6. Prompt sem especificações de iluminação
**Problema**: Não descrever o tipo de luz na cena.
**Consequência**: IA escolhe iluminação flat/genérica que não cria drama visual.
**Solução**: Especificar "dramatic side lighting", "rim light", "studio lighting with key and fill" etc.

### 7. Clickbait visual desconectado do conteúdo
**Problema**: Criar thumbnail que promete algo que o vídeo não entrega.
**Consequência**: Alto CTR mas baixa retenção = YouTube penaliza o vídeo no algoritmo.
**Solução**: Thumbnail deve amplificar o conteúdo real, não inventar.

### 8. Copiar thumbnails sem adaptação
**Problema**: Replicar exatamente o estilo de outro criador (ex: MrBeast) sem adaptar à identidade do canal.
**Consequência**: Parece genérico, perde autenticidade, público não reconhece o canal.
**Solução**: Usar padrões comprovados (cores vibrantes, expressões) mas manter identidade própria.

## Always Do

### 1. Teste mental de 168×94px
Antes de finalizar o prompt, imaginar a thumbnail no tamanho mobile. Se a mensagem não é clara nesse tamanho, simplificar.

### 2. Incluir espaço para texto overlay
Deixar uma área "limpa" na thumbnail (geralmente topo ou lateral) onde o texto será adicionado em pós-produção. Especificar no prompt: "with clean space in the upper right for text overlay".

### 3. Especificar 3 versões de prompt
Sempre gerar prompts para Midjourney, DALL-E e Flux — cada modelo tem forças diferentes.

### 4. Descrever emoções fisicamente
Em vez de "excited person", descrever "person with wide smile, clenched fists raised near face, eyes bright with excitement, slightly leaning forward".

### 5. Usar cores contrastantes explícitas
Nomear as cores: "vibrant yellow (#FFD700) text against deep navy blue (#1a1a4e) background" — não deixar a IA decidir.
