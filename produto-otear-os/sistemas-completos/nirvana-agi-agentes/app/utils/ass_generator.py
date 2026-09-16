import datetime

def format_ass_time(seconds: float) -> str:
    """Format seconds into H:MM:SS.cs (centiseconds) for ASS"""
    td = datetime.timedelta(seconds=seconds)
    # Total seconds
    total_seconds = int(seconds)
    centiseconds = int((seconds - total_seconds) * 100)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

def generate_ass(segments, words=None, style_config=None):
    """
    Gera conteúdo ASS/SSA.
    Se 'words' for fornecido e style_config['animation'] == 'highlight-word',
    gera eventos palavra-por-palavra (Karaoke style).
    Se style_config['animation'] == 'typewriter', gera efeito de digitação.
    """
    if style_config is None:
        style_config = {}
        
    animation = style_config.get('animation', 'none')
    
    # Cores
    primary_color = style_config.get('color', '&H00FFFFFF') # White default (ASS format)
    highlight_color = style_config.get('highlight_color', '&H0000FFFF') # Yellow default
    
    font = style_config.get('font', 'Arial')
    font_size = style_config.get('font_size', 10)
    # Alignment: 2=Bottom
    alignment = style_config.get('alignment', 2)
    margin_v = style_config.get('margin_v', 20)
    margin_l = style_config.get('margin_l', 10)  # Margem esquerda
    margin_r = style_config.get('margin_r', 10)  # Margem direita
    
    # Header ASS
    # Script Info, V4+ Styles
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 384
PlayResY: 288
WrapStyle: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{font_size},{primary_color},&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,{alignment},{margin_l},{margin_r},{margin_v},1
Style: Highlight,{font},{font_size},{highlight_color},&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,{alignment},{margin_l},{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    events = ""
    
    if animation == 'word-by-word' and words:
        print(f"DEBUG ASS: Generating Word-by-Word Animation for {len(words)} words.")
        # Modo: Mostrar apenas a palavra sendo falada (estilo TikTok)
        
        for word_obj in words:
            word = word_obj['word'].strip()
            w_start = format_ass_time(word_obj['start'])
            w_end = format_ass_time(word_obj['end'])
            
            # Mostrar apenas esta palavra
            events += f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{word}\n"
    
    elif animation == 'highlight-word' and words:
        print(f"DEBUG ASS: Generating Highlight Animation for {len(words)} words.")
        # Modo Karaoke / Highlight
        # Estraégia: Para cada palavra, criar um evento onde ELA é Highlight e o resto é Default
        # Isso cria overlap, mas é visualmente o que queremos.
        # Ou melhor: Segmentar por frase, e dentro da frase pintar palavras.
        
        # Agrupar palavras por segmento para não ter frases soltas?
        # Se usarmos os 'segments' do whisper, sabemos o texto da frase.
        # Precisamos mapear quais palavras estão dentro daquele segmento.
        
        current_word_idx = 0
        total_words = len(words)
        
        for seg in segments:
            seg_start = seg['start']
            seg_end = seg['end']
            seg_text = seg['text']
            # print(f"DEBUG ASS: Processing segment '{seg_text}' ({seg_start}-{seg_end})")
            
            # Encontrar palavras deste segmento (aproxime pelo tempo)
            seg_words = []
            while current_word_idx < total_words:
                w = words[current_word_idx]
                if w['start'] >= seg_start - 0.5 and w['end'] <= seg_end + 0.5:
                    seg_words.append(w)
                    current_word_idx += 1
                elif w['start'] > seg_end:
                    break
                else:
                     # Palavra perdida ou anterior? Avança
                     current_word_idx += 1
            
            if not seg_words:
                # Fallback se não achar palavras (ex: timestamp ruim)
                s = format_ass_time(seg_start)
                e = format_ass_time(seg_end)
                events += f"Dialogue: 0,{s},{e},Default,,0,0,0,,{seg_text}\n"
                continue

            # Para cada palavra na frase, criar um "frame" temporal
            # O texto exibido é SEMPRE a frase inteira.
            # Mas a formatação muda.
            
            # Reconstrói a frase token por token para garantir alinhamento
            # (Seg_text pode diferir levemente da soma das words)
            full_phrase_str = " ".join([w['word'].strip() for w in seg_words])
            
            for i, active_word in enumerate(seg_words):
                w_start = format_ass_time(max(active_word['start'], seg_start))
                w_end = format_ass_time(min(active_word['end'], seg_end))
                
                # Montar o texto com Highlight na palavra i
                rendered_text = ""
                for j, w in enumerate(seg_words):
                    clean_word = w['word'].strip()
                    if j == i:
                        rendered_text += f"{{\\rHighlight}}{clean_word}{{\\rDefault}} "
                    else:
                        rendered_text += f"{clean_word} "
                
                events += f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{rendered_text.strip()}\n"
                
    elif animation == 'highlight-word' and not words:
        print("WARNING ASS: Animation 'highlight-word' requested but NO WORDS provided in parameters. Fallback to static.")
        # Fallback para estático (código abaixo)
    
    elif animation == 'typewriter' and words:
        print(f"DEBUG ASS: Generating Typewriter Animation for {len(words)} words.")
        # Efeito de digitação: mostra caracteres progressivamente por palavra
        
        current_word_idx = 0
        total_words = len(words)
        
        for seg in segments:
            seg_start = seg['start']
            seg_end = seg['end']
            seg_text = seg['text']
            
            # Encontrar palavras deste segmento
            seg_words = []
            while current_word_idx < total_words:
                w = words[current_word_idx]
                if w['start'] >= seg_start - 0.5 and w['end'] <= seg_end + 0.5:
                    seg_words.append(w)
                    current_word_idx += 1
                elif w['start'] > seg_end:
                    break
                else:
                    current_word_idx += 1
            
            if not seg_words:
                # Fallback se não achar palavras
                s = format_ass_time(seg_start)
                e = format_ass_time(seg_end)
                events += f"Dialogue: 0,{s},{e},Default,,0,0,0,,{seg_text}\n"
                continue
            
            # Loop por cada palavra para criar o efeito de digitação acumulativo
            for word_idx, word_obj in enumerate(seg_words):
                word = word_obj['word'].strip()
                word_start = word_obj['start']
                word_end = word_obj['end']
                word_duration = max(word_end - word_start, 0.05)
                
                # Texto já digitado (palavras anteriores a esta)
                base_text_before_word = " ".join([w['word'].strip() for w in seg_words[:word_idx]])
                if base_text_before_word:
                    base_text_before_word += " "
                
                # Dividir a palavra em caracteres para digitar
                for i, char in enumerate(word):
                    current_typed_word = word[:i+1]  # palavra parcial sendo digitada
                    
                    # Calcular tempo deste frame do caractere
                    char_time = word_start + (i / max(len(word), 1)) * word_duration
                    next_char_time = word_start + ((i + 1) / max(len(word), 1)) * word_duration
                    
                    end_time_val = min(next_char_time, seg_end)
                    if i == len(word) - 1:
                        # Último caractere: manter até a próxima palavra ou fim do segmento
                        if word_idx < len(seg_words) - 1:
                            next_word_start = seg_words[word_idx + 1]['start']
                            end_time_val = min(next_word_start, seg_end)
                        else:
                            end_time_val = seg_end
                    
                    start_time = format_ass_time(char_time)
                    end_time = format_ass_time(end_time_val)
                    
                    # Texto exibido: tudo que já foi digitado + a parte atual
                    display_text = base_text_before_word + current_typed_word
                    events += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{display_text}\n"
            
            # Manter o texto completo do segmento até o fim exato do segmento
            if seg_words:
                last_word_end = seg_words[-1]['end']
                full_text = " ".join([w['word'].strip() for w in seg_words])
                if last_word_end < seg_end:
                    start_time = format_ass_time(last_word_end)
                    end_time = format_ass_time(seg_end)
                    events += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{full_text}\n"
    
    elif animation == 'typewriter' and not words:
        print("WARNING ASS: Animation 'typewriter' requested but NO WORDS provided. Fallback to static.")
        # Fallback para estático
    
    else:
        # Modo Simples (Estático)
        for seg in segments:
            start = format_ass_time(seg['start'])
            end = format_ass_time(seg['end'])
            text = seg['text'].replace('\n', '\\N')
            events += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

    return header + events
