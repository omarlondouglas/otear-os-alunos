import ffmpeg
from app.workers.operations.base import BaseOperation
from typing import Dict, Any
import requests
import os
from pathlib import Path
import tempfile

class VideoOverlayOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'overlay_url' not in params:
            raise ValueError("VideoOverlay requires 'overlay_url' parameter")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        VideoOverlayOperation.validate_params(params)
        
        overlay_url = params['overlay_url']
        
        # Posição do vídeo sobreposto
        position = params.get('position', 'bottom-right')  # top-left, top-right, bottom-left, bottom-right, center, custom
        x = params.get('x', None)
        y = params.get('y', None)
        
        # Tamanho do vídeo sobreposto
        width = params.get('width', None)  # Largura em pixels ou porcentagem (ex: "25%")
        height = params.get('height', None)  # Altura em pixels
        scale = params.get('scale', 0.25)  # Escala relativa (0.25 = 25% do vídeo principal)
        
        # Timing
        start_time = params.get('start_time', 0)  # Quando o overlay aparece
        duration = params.get('duration', None)  # Duração do overlay (None = até o fim)
        
        # Efeitos
        opacity = params.get('opacity', 1.0)  # Opacidade 0.0-1.0
        border = params.get('border', False)  # Adicionar borda
        border_color = params.get('border_color', 'white')
        border_width = params.get('border_width', 3)
        
        # Margin (distância das bordas)
        margin = params.get('margin', 20)
        
        # Controle de áudio
        audio_mode = params.get('audio_mode', 'main')  # 'main', 'overlay', 'mix', 'none'
        main_volume = params.get('main_volume', 1.0)  # Volume do vídeo principal (0.0-2.0)
        overlay_volume = params.get('overlay_volume', 1.0)  # Volume do vídeo overlay (0.0-2.0)
        
        # Chroma Key (remover fundo)
        chroma_key = params.get('chroma_key', False)  # Ativar remoção de fundo
        chroma_color = params.get('chroma_color', 'green')  # 'green', 'blue', ou cor hex
        chroma_similarity = params.get('chroma_similarity', 0.3)  # 0.0-1.0 (sensibilidade)
        chroma_blend = params.get('chroma_blend', 0.1)  # 0.0-1.0 (suavização das bordas)
        
        try:
            # Baixar vídeo overlay
            overlay_path = VideoOverlayOperation._download_video(overlay_url)
            
            # Inputs
            main_video = ffmpeg.input(input_path)
            overlay_video = ffmpeg.input(overlay_path)
            
            # Obter dimensões do vídeo principal
            probe = ffmpeg.probe(input_path)
            main_width = int(probe['streams'][0]['width'])
            main_height = int(probe['streams'][0]['height'])
            
            # Calcular tamanho do overlay
            if width is None and height is None:
                # Usar escala
                overlay_width = int(main_width * scale)
                overlay_height = int(main_height * scale)
            else:
                overlay_width = width if width else -1
                overlay_height = height if height else -1
            
            # Redimensionar overlay
            overlay_scaled = overlay_video.video.filter('scale', overlay_width, overlay_height)
            
            # Aplicar chroma key se solicitado
            if chroma_key:
                # Converter cor para formato FFmpeg
                if chroma_color == 'green':
                    color_hex = '0x00FF00'
                elif chroma_color == 'blue':
                    color_hex = '0x0000FF'
                else:
                    # Assumir que é uma cor hex
                    color_hex = chroma_color if chroma_color.startswith('0x') else f'0x{chroma_color.replace("#", "")}'
                
                # Aplicar filtro chromakey
                overlay_scaled = overlay_scaled.filter(
                    'chromakey',
                    color=color_hex,
                    similarity=chroma_similarity,
                    blend=chroma_blend
                )
                
                # Garantir formato com alpha channel
                overlay_scaled = overlay_scaled.filter('format', 'yuva420p')
            
            # Aplicar opacidade se necessário
            if opacity < 1.0:
                if not chroma_key:
                    overlay_scaled = overlay_scaled.filter('format', 'yuva420p')
                overlay_scaled = overlay_scaled.filter('colorchannelmixer', aa=opacity)
            
            # Adicionar borda se solicitado
            if border:
                overlay_scaled = overlay_scaled.filter(
                    'drawbox',
                    x=0, y=0,
                    width='iw', height='ih',
                    color=border_color,
                    thickness=border_width
                )
            
            # Calcular posição
            if x is None or y is None:
                if position == 'top-left':
                    x_pos = margin
                    y_pos = margin
                elif position == 'top-right':
                    x_pos = f'main_w-overlay_w-{margin}'
                    y_pos = margin
                elif position == 'bottom-left':
                    x_pos = margin
                    y_pos = f'main_h-overlay_h-{margin}'
                elif position == 'bottom-right':
                    x_pos = f'main_w-overlay_w-{margin}'
                    y_pos = f'main_h-overlay_h-{margin}'
                elif position == 'center':
                    x_pos = '(main_w-overlay_w)/2'
                    y_pos = '(main_h-overlay_h)/2'
                elif position == 'top-center':
                    x_pos = '(main_w-overlay_w)/2'
                    y_pos = margin
                elif position == 'bottom-center':
                    x_pos = '(main_w-overlay_w)/2'
                    y_pos = f'main_h-overlay_h-{margin}'
                else:
                    x_pos = f'main_w-overlay_w-{margin}'
                    y_pos = f'main_h-overlay_h-{margin}'
            else:
                x_pos = str(x)
                y_pos = str(y)
            
            # Aplicar overlay
            if start_time > 0 or duration is not None:
                # Com timing
                enable_expr = f'gte(t,{start_time})'
                if duration is not None:
                    enable_expr += f'*lte(t,{start_time + duration})'
                
                video_out = main_video.video.overlay(
                    overlay_scaled,
                    x=x_pos,
                    y=y_pos,
                    enable=enable_expr
                )
            else:
                # Sem timing (overlay durante todo o vídeo)
                video_out = main_video.video.overlay(
                    overlay_scaled,
                    x=x_pos,
                    y=y_pos
                )
            
            # Controle de áudio baseado no modo
            if audio_mode == 'main':
                # Apenas áudio do vídeo principal
                audio_out = main_video.audio
                if main_volume != 1.0:
                    audio_out = audio_out.filter('volume', main_volume)
                    
            elif audio_mode == 'overlay':
                # Apenas áudio do vídeo overlay
                audio_out = overlay_video.audio
                if overlay_volume != 1.0:
                    audio_out = audio_out.filter('volume', overlay_volume)
                    
            elif audio_mode == 'mix':
                # Mixar os dois áudios
                main_audio = main_video.audio
                overlay_audio = overlay_video.audio
                
                # Ajustar volumes
                if main_volume != 1.0:
                    main_audio = main_audio.filter('volume', main_volume)
                if overlay_volume != 1.0:
                    overlay_audio = overlay_audio.filter('volume', overlay_volume)
                
                # Mixar
                audio_out = ffmpeg.filter([main_audio, overlay_audio], 'amix', inputs=2, duration='first')
                
            elif audio_mode == 'none':
                # Sem áudio
                audio_out = None
            else:
                # Padrão: áudio do vídeo principal
                audio_out = main_video.audio
            
            # Output
            if audio_out is not None:
                output = ffmpeg.output(
                    video_out, audio_out, output_path,
                    vcodec='libx264',
                    acodec='aac',
                    pix_fmt='yuv420p',
                    movflags='+faststart'
                )
            else:
                output = ffmpeg.output(
                    video_out, output_path,
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    movflags='+faststart'
                )
            
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
            # Limpar arquivo temporário
            if os.path.exists(overlay_path):
                os.remove(overlay_path)
                
        except ffmpeg.Error as e:
            error_log = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg video overlay failed: {error_log}")
    
    @staticmethod
    def _download_video(url: str) -> str:
        """Baixa vídeo de forma síncrona"""
        temp_dir = Path(tempfile.gettempdir())
        video_filename = f"overlay_{os.urandom(8).hex()}.mp4"
        video_path = temp_dir / video_filename
        
        # Baixar arquivo
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download overlay video from URL: {response.status_code}")
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(video_path)
