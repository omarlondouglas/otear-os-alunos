import ffmpeg
from app.workers.operations.base import BaseOperation
from typing import Dict, Any

class TrimOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        required = ['start', 'end']
        if not all(k in params for k in required):
            raise ValueError(f"Missing required params for trim: {required}")
        
        # Validar tipos (pode ser int/float ou str "HH:MM:SS")
        # Simples check de existência é suficiente por enquanto

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        TrimOperation.validate_params(params)
        
        start = params['start']
        end = params['end']
        
        try:
            # ffmpeg -i input.mp4 -ss start -to end -c copy output.mp4
            # Usamos -c copy para ser ultra rápido (sem re-encoding) quando possível
            # Mas para precisão exata de frame, as vezes é melhor re-encodar.
            # Vamos começar com re-encode padrão para garantir compatibilidade
            
            stream = ffmpeg.input(input_path)
            
            # Aplicar trim
            # .trim() do ffmpeg-python as vezes é chato com áudio
            # Melhor usar .input(ss=, to=) ou filtros explícitos
            
            # Abordagem robusta: input seek (rápido)
            stream = ffmpeg.input(input_path, ss=start, to=end)
            
            # Output com codecs padrão (h264/aac) para garantir que rode em tudo
            stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart', strict='experimental')
            
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
        except ffmpeg.Error as e:
            error_log = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg trim failed: {error_log}")
