import datetime

def format_timestamp(seconds: float) -> str:
    td = datetime.timedelta(seconds=seconds)
    # Formato HH:MM:SS,mmm
    # timedelta str é "H:MM:SS.us"
    
    total_seconds = int(seconds)
    milliseconds = int((seconds - total_seconds) * 1000)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def generate_srt(segments, max_words_per_line=None):
    """
    Gera arquivo SRT a partir dos segmentos.
    
    Args:
        segments: Lista de segmentos com start, end, text
        max_words_per_line: Número máximo de palavras por linha (None = sem limite)
    """
    srt_content = ""
    subtitle_index = 1
    
    for seg in segments:
        text = seg['text'].strip()
        
        # Se max_words_per_line está definido, quebrar o texto
        if max_words_per_line:
            words = text.split()
            
            # Se o segmento tem mais palavras que o limite, quebrar em múltiplas linhas
            if len(words) > max_words_per_line:
                # Calcular duração por palavra
                seg_duration = seg['end'] - seg['start']
                time_per_word = seg_duration / len(words)
                
                # Criar múltiplas legendas
                for i in range(0, len(words), max_words_per_line):
                    chunk_words = words[i:i + max_words_per_line]
                    chunk_text = ' '.join(chunk_words)
                    
                    # Calcular timestamps para este chunk
                    chunk_start = seg['start'] + (i * time_per_word)
                    chunk_end = seg['start'] + ((i + len(chunk_words)) * time_per_word)
                    
                    start = format_timestamp(chunk_start)
                    end = format_timestamp(chunk_end)
                    
                    srt_content += f"{subtitle_index}\n{start} --> {end}\n{chunk_text}\n\n"
                    subtitle_index += 1
            else:
                # Segmento já está dentro do limite
                start = format_timestamp(seg['start'])
                end = format_timestamp(seg['end'])
                srt_content += f"{subtitle_index}\n{start} --> {end}\n{text}\n\n"
                subtitle_index += 1
        else:
            # Sem limite de palavras (comportamento original)
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            srt_content += f"{subtitle_index}\n{start} --> {end}\n{text}\n\n"
            subtitle_index += 1
    
    return srt_content
