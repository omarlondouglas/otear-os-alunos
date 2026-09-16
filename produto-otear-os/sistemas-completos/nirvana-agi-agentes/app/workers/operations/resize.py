import ffmpeg
from app.workers.operations.base import BaseOperation
from typing import Dict, Any

class ResizeOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'width' not in params and 'height' not in params:
            raise ValueError("Resize requires 'width' or 'height'")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        ResizeOperation.validate_params(params)
        
        width = params.get('width', -1)  # -1 mantém aspect ratio
        height = params.get('height', -1)
        
        # Se um não for fornecido, usar -1 (FFmpeg calcula proporcional)
        if width is None: width = -1
        if height is None: height = -1
        
        try:
            stream = ffmpeg.input(input_path)
            # scale=w:h
            stream = ffmpeg.filter(stream, 'scale', width, height)
            stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg resize failed: {e.stderr.decode() if e.stderr else str(e)}")
