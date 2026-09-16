"""
Normalize Video Operation
Converts HEVC/H.265 to H.264, forces 30fps, sets keyframe interval to 1s.
This MUST run as the first operation in any pipeline to prevent subtitle
desync on longer videos and ensure consistent processing.
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any
import ffmpeg
import subprocess
import json


class NormalizeOperation(BaseOperation):
    """Normalizes video to H.264/30fps/keyframe-1s for reliable downstream processing."""

    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        target_fps = params.get("fps", 30)
        keyframe_interval = params.get("keyframe_interval", 1)  # seconds
        target_codec = params.get("codec", "libx264")
        crf = params.get("crf", 18)  # high quality default

        # Probe input to check if normalization is needed
        probe = ffmpeg.probe(input_path)
        video_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"), None
        )

        if not video_stream:
            raise RuntimeError("No video stream found in input file")

        current_codec = video_stream.get("codec_name", "").lower()
        current_fps_str = video_stream.get("r_frame_rate", "30/1")

        # Parse fps fraction (e.g. "30000/1001" → 29.97)
        try:
            num, den = current_fps_str.split("/")
            current_fps = float(num) / float(den)
        except Exception:
            current_fps = 30.0

        needs_codec = current_codec in ("hevc", "h265", "vp9", "av1")
        needs_fps = abs(current_fps - target_fps) > 1.0

        if not needs_codec and not needs_fps:
            # Already normalized — still re-encode with keyframe interval for safety
            print(f"[Normalize] Video already H.264/{current_fps:.0f}fps, applying keyframe normalization")

        print(
            f"[Normalize] {current_codec}/{current_fps:.1f}fps → "
            f"h264/{target_fps}fps (keyframe every {keyframe_interval}s, crf={crf})"
        )

        gop_size = target_fps * keyframe_interval  # keyframe every N frames

        try:
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vcodec=target_codec,
                    acodec="aac",
                    r=target_fps,
                    crf=crf,
                    pix_fmt="yuv420p",
                    movflags="+faststart",
                    g=int(gop_size),        # GOP size = keyframe interval in frames
                    keyint_min=int(gop_size),
                    **{"b:a": "192k"},
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            error_log = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg normalize failed: {error_log}")

        print("[Normalize] Done")
