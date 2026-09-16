# 🤝 Contribuindo com Novos Efeitos

Guia para desenvolvedores que querem adicionar novos efeitos de animação.

## 🎯 Estrutura Atual

### Arquivos Principais

1. **`app/utils/ass_generator.py`** - Gera arquivos ASS com animações
2. **`app/workers/operations/auto_subtitle.py`** - Processa legendas
3. **`app/schemas/video.py`** - Define tipos de operações

## 🚀 Adicionando um Novo Efeito

### Passo 1: Planejar o Efeito

Defina:
- **Nome**: Ex: "fade-in", "bounce", "slide"
- **Comportamento**: Como o texto deve aparecer/animar
- **Parâmetros**: Velocidade, direção, etc.

### Passo 2: Editar `ass_generator.py`

Adicione sua lógica no método `generate_ass()`:

```python
elif animation == 'seu_efeito' and words:
    print(f"DEBUG ASS: Generating SEU_EFEITO Animation")
    
    for seg in segments:
        seg_start = seg['start']
        seg_end = seg['end']
        seg_text = seg['text']
        
        # Sua lógica aqui
        # Crie eventos ASS conforme necessário
        
        events += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"
```

### Passo 3: Atualizar `auto_subtitle.py`

Adicione seu efeito na lista de animações suportadas:

```python
if animation in ['highlight-word', 'typewriter', 'seu_efeito']:
    # Gerar ASS com animação
    ass_config = {
        'animation': animation,
        # ... outros parâmetros
        'seu_parametro': style.get('seu_parametro', valor_padrao)
    }
```

### Passo 4: Documentar

Adicione exemplos em:
- `CURL_DOCUMENTATION.md`
- `ANIMATION_EFFECTS.md`
- `examples/`

## 💡 Exemplos de Efeitos Possíveis

### 1. Fade In (Aparecer Gradualmente)
```python
elif animation == 'fade-in':
    # Usar tags ASS para fade
    # \fad(fade_in_ms, fade_out_ms)
    fade_duration = style_config.get('fade_duration', 500)
    
    for seg in segments:
        start = format_ass_time(seg['start'])
        end = format_ass_time(seg['end'])
        text = seg['text']
        events += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{{\\fad({fade_duration},0)}}{text}\n"
```

### 2. Slide In (Deslizar)
```python
elif animation == 'slide-in':
    # Usar \move(x1,y1,x2,y2,t1,t2)
    direction = style_config.get('direction', 'left')
    
    for seg in segments:
        # Calcular posições baseado na direção
        # Criar evento com \move
        pass
```

### 3. Bounce (Pular)
```python
elif animation == 'bounce':
    # Usar \t(t1,t2,\fscx\fscy) para escala
    # Criar múltiplos eventos com escalas diferentes
    pass
```

### 4. Word by Word (Palavra por Palavra)
```python
elif animation == 'word-by-word':
    # Similar ao typewriter, mas por palavra inteira
    for seg in segments:
        current_text = ""
        for word in seg_words:
            current_text += word['word'] + " "
            start = format_ass_time(word['start'])
            end = format_ass_time(word['end'])
            events += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{current_text}\n"
```

## 📝 Tags ASS Úteis

### Posicionamento
- `\pos(x,y)` - Posição absoluta
- `\move(x1,y1,x2,y2)` - Movimento
- `\an` - Alinhamento (1-9)

### Estilo
- `\c&HBBGGRR&` - Cor primária
- `\alpha&HXX&` - Transparência
- `\fs` - Tamanho da fonte
- `\fn` - Nome da fonte

### Animação
- `\t(t1,t2,\tag)` - Transformação ao longo do tempo
- `\fad(in,out)` - Fade in/out
- `\fscx\fscy` - Escala X/Y

### Efeitos
- `\blur` - Desfoque
- `\be` - Borda desfocada
- `\shad` - Sombra

## 🧪 Testando Seu Efeito

1. **Teste local:**
```python
from app.utils.ass_generator import generate_ass

segments = [{"start": 0, "end": 3, "text": "Teste"}]
words = [{"word": "Teste", "start": 0, "end": 3}]

config = {
    "animation": "seu_efeito",
    "seu_parametro": valor
}

ass = generate_ass(segments, words, config)
print(ass)
```

2. **Teste com vídeo:**
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@test.mp4" \
  -F 'request={
    "operations": [{
      "type": "auto_subtitle",
      "params": {
        "language": "pt",
        "model": "base",
        "style": {
          "animation": "seu_efeito"
        }
      }
    }]
  }'
```

## 📚 Recursos

### Documentação ASS
- [ASS Tags Reference](http://docs.aegisub.org/3.2/ASS_Tags/)
- [SubStation Alpha](https://en.wikipedia.org/wiki/SubStation_Alpha)

### FFmpeg Subtitles
- [FFmpeg Subtitles Filter](https://ffmpeg.org/ffmpeg-filters.html#subtitles-1)

## ✅ Checklist de Contribuição

- [ ] Efeito implementado em `ass_generator.py`
- [ ] Suporte adicionado em `auto_subtitle.py`
- [ ] Parâmetros documentados
- [ ] Exemplos de CURL criados
- [ ] Testado com vídeo real
- [ ] Documentação atualizada
- [ ] README atualizado

## 🎨 Ideias de Efeitos

1. **Fade In/Out** - Aparecer/desaparecer gradualmente
2. **Slide In** - Deslizar de um lado
3. **Bounce** - Pular/saltar
4. **Word by Word** - Palavra por palavra (sem highlight)
5. **Rotate** - Rotacionar texto
6. **Zoom** - Aumentar/diminuir
7. **Wave** - Ondular
8. **Glitch** - Efeito de falha/glitch
9. **Neon** - Efeito neon piscante
10. **Matrix** - Estilo Matrix (caracteres caindo)

## 🤝 Enviando sua Contribuição

1. Fork o repositório
2. Crie uma branch: `git checkout -b feat/novo-efeito`
3. Implemente o efeito
4. Teste completamente
5. Commit: `git commit -m "feat: adiciona efeito X"`
6. Push: `git push origin feat/novo-efeito`
7. Abra um Pull Request

## 💬 Dúvidas?

Abra uma issue no GitHub ou consulte a documentação existente!

---

**Obrigado por contribuir!** 🎬
