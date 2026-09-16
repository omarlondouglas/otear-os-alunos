from app.workers.operations.base import BaseOperation
from app.services.whisper_service import WhisperService
from app.utils.subtitle_generator import generate_srt
from typing import Dict, Any
import ffmpeg
import os

class AutoSubtitleOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        from app.utils.color import hex_to_ass
        from app.utils.ass_generator import generate_ass
        
        # 1. Transcrever
        print("Transcribing for subtitles...")
        service = WhisperService(model_size=params.get('model', 'small'))
        result = service.transcribe(input_path, language=params.get('language'))
        
        style = params.get('style', {})
        animation = style.get('animation', None)
        
        # Configurar Cores ASS
        primary_color_ass = hex_to_ass(style.get('color', '#FFFFFF'))
        highlight_color_ass = hex_to_ass(style.get('highlight_color', '#FFFF00')) # Default Yellow
        
        # Posição / Margem
        pos_map = {"bottom": 2, "top": 6, "center": 10}
        alignment = pos_map.get(style.get('position', 'bottom'), 2)
        margin_v = style.get('margin_vertical', 20)
        margin_h = style.get('margin_horizontal', 10)  # Margem horizontal (esquerda e direita)
        
        subtitle_file_path = input_path + (".ass" if animation else ".srt")
        
        # 2. Gerar Arquivo de Legenda (ASS ou SRT)
        if animation in ['highlight-word', 'typewriter', 'word-by-word']:
            # Gerar ASS com animação
            ass_config = {
                'animation': animation,
                'color': primary_color_ass,
                'highlight_color': highlight_color_ass,
                'font': style.get('font', 'Arial'),
                'font_size': style.get('font_size', 10),
                'alignment': alignment,
                'margin_v': margin_v,
                'margin_l': margin_h,  # Margem esquerda
                'margin_r': margin_h,  # Margem direita
                'typewriter_speed': style.get('typewriter_speed', 20)  # caracteres por segundo
            }
            content = generate_ass(result['segments'], result.get('words'), ass_config)
            with open(subtitle_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"ASS generated at {subtitle_file_path}")
            
            # Para ASS, o FFmpeg usa o estilo definido no arquivo
            force_style_arg = None
            
        else:
            # Gerar SRT Padrão (Fallback ou modo simples)
            max_words = style.get('max_words_per_line', None)  # Limite de palavras por linha
            srt_content = generate_srt(result['segments'], max_words_per_line=max_words)
            with open(subtitle_file_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"SRT generated at {subtitle_file_path}")
            
            # Construir Force Style para SRT (Modo Simples)
            force_style_arg = (
                f"FontName={style.get('font', 'Arial')},"
                f"FontSize={style.get('font_size', 24)},"
                f"PrimaryColour={primary_color_ass},"
                f"Alignment={alignment},"
                f"MarginV={margin_v},"
                f"Outline=1,Shadow=0"
            )

        # 3. Queimar Legenda
        try:
            input_ffmpeg = ffmpeg.input(input_path)
            
            # Filter Video Stream
            if force_style_arg:
                video = input_ffmpeg.video.filter('subtitles', subtitle_file_path, force_style=force_style_arg)
            else:
                # ASS mode: Style is inside file
                video = input_ffmpeg.video.filter('subtitles', subtitle_file_path)
                
            audio = input_ffmpeg.audio
            stream = ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')
            
            ffmpeg.run(stream, overwrite_output=True)
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg subtitle burn failed: {e.stderr.decode() if e.stderr else str(e)}")
        finally:
            if os.path.exists(subtitle_file_path) and not params.get('keep_srt'):
                os.remove(subtitle_file_path)
