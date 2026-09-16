import ffmpeg
from app.workers.operations.base import BaseOperation
from typing import Dict, Any
import httpx
import aiofiles
import os
from pathlib import Path
import asyncio

class AddAudioOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'audio_url' not in params:
            raise ValueError("AddAudio requires 'audio_url' parameter")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        AddAudioOperation.validate_params(params)
        
        audio_url = params['audio_url']
        mode = params.get('mode', 'mix')  # 'mix', 'replace', 'background'
        audio_volume = params.get('audio_volume', 0.3)  # Volume da música (0.0-1.0)
        original_volume = params.get('original_volume', 1.0)  # Volume do áudio original
        fade_in = params.get('fade_in', 0)  # Fade in em segundos
        fade_out = params.get('fade_out', 0)  # Fade out em segundos
        loop = params.get('loop', False)  # Repetir música se for mais curta que o vídeo
        start_time = params.get('start_time', 0)  # Quando a música começa
        
        try:
            # Baixar arquivo de áudio
            audio_path = AddAudioOperation._download_audio(audio_url)
            
            # Obter duração do vídeo
            probe = ffmpeg.probe(input_path)
            video_duration = float(probe['streams'][0]['duration'])
            
            input_video = ffmpeg.input(input_path)
            input_audio = ffmpeg.input(audio_path)
            
            video = input_video.video
            original_audio = input_video.audio
            new_audio = input_audio.audio
            
            # Aplicar start_time se especificado
            if start_time > 0:
                new_audio = new_audio.filter('atrim', start=start_time)
                new_audio = new_audio.filter('asetpts', 'PTS-STARTPTS')
            
            # Loop se necessário
            if loop:
                # Repetir áudio até cobrir a duração do vídeo
                new_audio = new_audio.filter('aloop', loop=-1, size=2e9)
                new_audio = new_audio.filter('atrim', duration=video_duration)
            
            # Aplicar fade in/out
            if fade_in > 0:
                new_audio = new_audio.filter('afade', type='in', duration=fade_in)
            if fade_out > 0:
                new_audio = new_audio.filter('afade', type='out', start_time=video_duration-fade_out, duration=fade_out)
            
            # Ajustar volume da música
            if audio_volume != 1.0:
                new_audio = new_audio.filter('volume', volume=audio_volume)
            
            # Processar baseado no modo
            if mode == 'replace':
                # Substituir áudio original pela música
                final_audio = new_audio
                
            elif mode == 'mix' or mode == 'background':
                # Mixar áudio original com música
                # Ajustar volume do áudio original se necessário
                if original_volume != 1.0:
                    original_audio = original_audio.filter('volume', volume=original_volume)
                
                # Mixar os dois áudios
                final_audio = ffmpeg.filter([original_audio, new_audio], 'amix', inputs=2, duration='first')
                
            else:
                raise ValueError(f"Invalid mode: {mode}. Use 'mix', 'replace', or 'background'")
            
            # Combinar vídeo com áudio final
            output = ffmpeg.output(
                video, final_audio, output_path,
                vcodec='libx264',
                acodec='aac',
                audio_bitrate='192k',
                shortest=None,  # Usar duração do vídeo
                pix_fmt='yuv420p',
                movflags='+faststart'
            )
            
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
            # Limpar arquivo temporário
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        except ffmpeg.Error as e:
            error_log = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg add audio failed: {error_log}")
    
    @staticmethod
    def _download_audio(url: str) -> str:
        """Baixa arquivo de áudio de forma síncrona"""
        import requests
        from pathlib import Path
        import tempfile
        
        # Criar arquivo temporário
        temp_dir = Path(tempfile.gettempdir())
        audio_filename = f"audio_{os.urandom(8).hex()}.mp3"
        audio_path = temp_dir / audio_filename
        
        # Baixar arquivo
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download audio from URL: {response.status_code}")
        
        with open(audio_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(audio_path)
