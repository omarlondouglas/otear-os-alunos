"""
Filmstrip Operation
Constroi um composite PNG (frames + waveform) para review visual de cuts.
Util como apoio visual quando humano (ou LLM) decide ajustar boundaries.

Pure ffmpeg + filter_complex - sem PIL/numpy.

Input:
  - input_path: video file
  - params:
      start: float (segundos)
      end: float (segundos)
      frames: int (default 8)
      markers: list[float] - timestamps a marcar com linha vertical vermelha
      OU
      clips_path: caminho do clips.json (gera filmstrip pra cada clipe)

Output:
  - output_path: PNG composite (ou diretorio com PNGs se clips_path)
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List, Optional
import json
import os
import subprocess


class FilmstripOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if not params.get("clips_path"):
            if params.get("start") is None or params.get("end") is None:
                raise ValueError(
                    "filmstrip requires either 'clips_path' or both 'start' and 'end'"
                )

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        FilmstripOperation.validate_params(params)
        frames = int(params.get("frames", 8))
        clips_path = params.get("clips_path")

        if clips_path:
            with open(clips_path, "r", encoding="utf-8") as f:
                clips_data = json.load(f)
            clips = clips_data.get("clips", [])
            if not clips:
                raise ValueError("filmstrip: clips_path has no clips")

            output_dir = output_path if not output_path.endswith((".png", ".jpg")) else os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            generated = []
            for i, c in enumerate(clips, 1):
                out = os.path.join(output_dir, f"clip_{i}.png")
                _build(
                    input_path,
                    float(c["start"]),
                    float(c["end"]),
                    out,
                    frames,
                    [float(c["start"]), float(c["end"])],
                )
                generated.append(out)

            manifest_path = os.path.join(output_dir, "filmstrip_manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump({"filmstrips": generated}, f, ensure_ascii=False, indent=2)

            # Se output_path for PNG, copia o primeiro como aliase de saida
            if output_path.endswith((".png", ".jpg")) and generated:
                import shutil
                shutil.copy2(generated[0], output_path)
            print(f"[Filmstrip] generated {len(generated)} PNGs in {output_dir}")
            return

        markers = params.get("markers")
        if markers:
            markers = [float(m) for m in markers]
        _build(
            input_path,
            float(params["start"]),
            float(params["end"]),
            output_path,
            frames,
            markers,
        )
        print(f"[Filmstrip] {output_path}")


def _build(
    video: str,
    start: float,
    end: float,
    out: str,
    frames: int = 8,
    markers: Optional[List[float]] = None,
) -> None:
    duration = max(0.1, end - start)
    fps = frames / duration
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    frame_w = 1920 // frames
    frame_h = int(frame_w * 9 / 16)

    drawbox = []
    if markers:
        for m in markers:
            if start <= m <= end:
                x = int((m - start) / duration * 1920)
                drawbox.append(f"drawbox=x={x}:y=0:w=2:h={frame_h}:color=red@0.9:t=fill")
    drawbox_str = ("," + ",".join(drawbox)) if drawbox else ""

    filter_complex = (
        f"[0:v]fps={fps:.4f},scale={frame_w}:{frame_h},tile={frames}x1{drawbox_str}[strip];"
        f"[0:a]showwavespic=s=1920x180:colors=0x66ccff[wave];"
        f"[strip][wave]vstack=inputs=2[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", video,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-frames:v", "1",
        out,
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=300)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"filmstrip ffmpeg failed: {err}")
