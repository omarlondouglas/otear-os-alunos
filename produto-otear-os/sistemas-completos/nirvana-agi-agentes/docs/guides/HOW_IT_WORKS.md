# 🔧 Como Funcionam os Efeitos de Animação

## 🎬 Visão Geral

Os efeitos de animação são implementados usando arquivos ASS (Advanced SubStation Alpha) que permitem controle preciso sobre timing e estilo das legendas.

## 📊 Fluxo de Processamento

```
Vídeo → Whisper AI → Transcrição → Gerador ASS → FFmpeg → Vídeo com Legendas
         (áudio)      (texto+timing)  (animação)   (queimar)
```

## 🎨 Como Cada Efeito Funciona

### 1. Estático (Padrão)

**Comportamento:**
- Texto completo aparece de uma vez
- Permanece na tela durante toda a frase
- Desaparece quando a próxima frase começa

**Implementação:**
```
Tempo: 0.0s - 3.5s
Texto: "Olá, bem-vindo ao tutorial"
```

**Código ASS:**
```
Dialogue: 0,0:00:00.00,0:00:03.50,Default,,0,0,0,,Olá, bem-vindo ao tutorial
```

---

### 2. Highlight Word (Karaoke)

**Comportamento:**
- Texto completo aparece
- Cada palavra muda de cor quando é falada
- Sincronizado com timestamps palavra-por-palavra

**Implementação:**
```
Tempo: 0.0s - 0.5s → "Olá" em amarelo, resto em branco
Tempo: 0.5s - 1.2s → "bem-vindo" em amarelo, resto em branco
Tempo: 1.2s - 2.0s → "ao" em amarelo, resto em branco
Tempo: 2.0s - 3.5s → "tutorial" em amarelo, resto em branco
```

**Código ASS:**
```
Dialogue: 0,0:00:00.00,0:00:00.50,Default,,0,0,0,,{\rHighlight}Olá{\rDefault} bem-vindo ao tutorial
Dialogue: 0,0:00:00.50,0:00:01.20,Default,,0,0,0,,Olá {\rHighlight}bem-vindo{\rDefault} ao tutorial
Dialogue: 0,0:00:01.20,0:00:02.00,Default,,0,0,0,,Olá bem-vindo {\rHighlight}ao{\rDefault} tutorial
Dialogue: 0,0:00:02.00,0:00:03.50,Default,,0,0,0,,Olá bem-vindo ao {\rHighlight}tutorial{\rDefault}
```

---

### 3. Typewriter (Digitação) ⌨️

**Comportamento:**
- Texto aparece caractere por caractere
- Velocidade controlada por `typewriter_speed`
- Cria ilusão de digitação em tempo real

**Implementação:**
```
Speed: 20 chars/segundo = 0.05s por caractere

Tempo: 0.00s - 0.05s → "O"
Tempo: 0.05s - 0.10s → "Ol"
Tempo: 0.10s - 0.15s → "Olá"
Tempo: 0.15s - 0.20s → "Olá,"
Tempo: 0.20s - 0.25s → "Olá, "
... e assim por diante
```

**Código ASS:**
```
Dialogue: 0,0:00:00.00,0:00:00.05,Default,,0,0,0,,O
Dialogue: 0,0:00:00.05,0:00:00.10,Default,,0,0,0,,Ol
Dialogue: 0,0:00:00.10,0:00:00.15,Default,,0,0,0,,Olá
Dialogue: 0,0:00:00.15,0:00:00.20,Default,,0,0,0,,Olá,
Dialogue: 0,0:00:00.20,0:00:00.25,Default,,0,0,0,,Olá, 
...
```

## ⚙️ Cálculo de Velocidade (Typewriter)

```python
typewriter_speed = 20  # caracteres por segundo
tempo_por_caractere = 1 / typewriter_speed  # 0.05 segundos

# Para a palavra "Olá" (3 caracteres)
duracao_total = 3 * 0.05 = 0.15 segundos
```

## 🎯 Sincronização com Whisper

O Whisper AI retorna:
- **Segments**: Frases completas com timestamps
- **Words**: Palavras individuais com timestamps

```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Olá, bem-vindo ao tutorial"
    }
  ],
  "words": [
    {"word": "Olá", "start": 0.0, "end": 0.5},
    {"word": "bem-vindo", "start": 0.5, "end": 1.2},
    {"word": "ao", "start": 1.2, "end": 2.0},
    {"word": "tutorial", "start": 2.0, "end": 3.5}
  ]
}
```

## 🔄 Pipeline Completo

1. **Extração de Áudio**
   ```
   FFmpeg extrai áudio do vídeo
   ```

2. **Transcrição**
   ```
   Whisper AI processa áudio
   Retorna texto + timestamps (segments + words)
   ```

3. **Geração ASS**
   ```python
   if animation == "typewriter":
       # Cria eventos para cada caractere
       for char in text:
           create_dialogue_event(char, timestamp)
   ```

4. **Queimar Legendas**
   ```
   FFmpeg aplica arquivo ASS no vídeo
   Gera vídeo final com legendas queimadas
   ```

## 💡 Otimizações

### Typewriter
- Agrupa caracteres por palavra para reduzir eventos
- Limita ao tempo do segmento
- Mantém texto completo no final

### Highlight Word
- Reutiliza texto completo em cada frame
- Apenas muda estilo da palavra ativa
- Reduz tamanho do arquivo ASS

## 🎨 Formato ASS

```
[V4+ Styles]
Style: Default,Arial,24,&H00FFFFFF,...
Style: Highlight,Arial,24,&H0000FFFF,...

[Events]
Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
```

**Cores ASS:**
- Formato: `&HAABBGGRR` (Alpha, Blue, Green, Red)
- Branco: `&H00FFFFFF`
- Amarelo: `&H0000FFFF`
- Verde: `&H0000FF00`

## 🧪 Testando Localmente

```python
# Gerar ASS manualmente
from app.utils.ass_generator import generate_ass

segments = [{"start": 0, "end": 3, "text": "Teste"}]
words = [{"word": "Teste", "start": 0, "end": 3}]

config = {
    "animation": "typewriter",
    "typewriter_speed": 20
}

ass_content = generate_ass(segments, words, config)
print(ass_content)
```

---

**Agora você entende como funciona por baixo dos panos!** 🎬
