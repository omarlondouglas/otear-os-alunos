import ffmpeg
from app.workers.operations.base import BaseOperation
from typing import Dict, Any

class AdjustVolumeOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'volume' not in params and 'normalize' not in params:
            raise ValueError("AdjustVolume requires 'volume' or 'normalize'")
        
        if 'volume' in params:
            volume = params['volume']
            if not isinstance(volume, (int, float)) or volume < 0:
                raise ValueError("Volume must be a positive number (0.0-10.0)")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        AdjustVolumeOperation.validate_params(params)
        
        normalize = params.get('normalize', False)
        volume = params.get('volume', 1.0)
        
        try:
            input_stream = ffmpeg.input(input_path)
            video = input_stream.video
            audio = input_stream.audio
            
            if normalize:
                # Normalização de áudio usando loudnorm filter
                # Normaliza para -16 LUFS (padrão para streaming)
                target_level = params.get('target_level', -16)
                audio = audio.filter('loudnorm', I=target_level, TP=-1.5, LRA=11)
            elif volume != 1.0:
                # Ajuste simples de volume
                # volume=1.0 = sem mudança
                # volume=0.5 = metade do volume
                # volume=2.0 = dobro do volume
                audio = audio.filter('volume', volume=volume)
            
            # Combinar vídeo e áudio processado
            output = ffmpeg.output(
                video, audio, output_path,
                vcodec='libx264',
                acodec='aac',
                audio_bitrate='192k'
            )
            
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
        except ffmpeg.Error as e:
            error_log = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg adjust volume failed: {error_log}")
