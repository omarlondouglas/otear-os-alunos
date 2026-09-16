from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List
import ffmpeg
import os

class SmartCutOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'keep_segments' not in params:
            raise ValueError("SmartCut requires 'keep_segments' list [[start, end], ...]")
        
        segments = params['keep_segments']
        if not isinstance(segments, list):
             raise ValueError("'keep_segments' must be a list")
             
        for seg in segments:
            if not isinstance(seg, (list, tuple)) or len(seg) != 2:
                 raise ValueError("Each segment must be [start, end]")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        SmartCutOperation.validate_params(params)
        keep_segments = params['keep_segments']
        fade_ms = float(params.get('fade_ms', 30))  # default 30ms — evita pop/click
        fade_seconds = max(0.0, fade_ms / 1000.0)

        if not keep_segments:
            print("No segments to keep. Copying original.")
            import shutil
            shutil.copy2(input_path, output_path)
            return

        print(
            f"Smart Cut: Keeping {len(keep_segments)} segments "
            f"(fade={fade_ms:.0f}ms): {keep_segments}"
        )

        try:
            inputs = ffmpeg.input(input_path)
            streams = []

            for i, (start, end) in enumerate(keep_segments):
                seg_dur = max(0.0, float(end) - float(start))
                v = inputs.video.filter('trim', start=start, end=end).filter('setpts', 'PTS-STARTPTS')
                a = inputs.audio.filter('atrim', start=start, end=end).filter('asetpts', 'PTS-STARTPTS')

                # Fades curtos no audio para evitar pop/click no corte
                if fade_seconds > 0 and seg_dur > 2 * fade_seconds:
                    a = a.filter('afade', t='in', st=0, d=fade_seconds)
                    a = a.filter('afade', t='out', st=seg_dur - fade_seconds, d=fade_seconds)

                streams.extend([v, a])

            joined = ffmpeg.concat(*streams, v=1, a=1).node
            v_out = joined[0]
            a_out = joined[1]

            output = ffmpeg.output(v_out, a_out, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')

            print("Running concat operation...")
            output.run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
        except ffmpeg.Error as e:
            error_log = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg smart cut failed: {error_log}")
