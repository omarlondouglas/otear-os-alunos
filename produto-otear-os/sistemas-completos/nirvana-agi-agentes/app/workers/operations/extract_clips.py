"""
Extract Clips Operation
Takes highlight segments and extracts each one as an individual video file.
Produces N separate .mp4 clips + a JSON manifest with metadata and download URLs.
"""

from app.workers.operations.base import BaseOperation
from app.workers.operations.detect_highlights import DetectHighlightsOperation
from typing import Dict, Any, List
import ffmpeg
import json
import os
import subprocess


MIN_CLIP_DURATION_SECONDS = 30.0


class ExtractClipsOperation(BaseOperation):
    """Extracts individual video clips from detected highlights — Opus Clip style."""

    @staticmethod
    def validate_params(params: Dict[str, Any]):
        # segments can be provided directly or auto-detected
        if not params.get("segments") and not params.get("auto_detect", False):
            raise ValueError(
                "ExtractClips requires 'segments' list [[start, end], ...] "
                "or 'auto_detect': true"
            )

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        """
        Extracts each highlight segment as a separate video clip.

        Params:
            segments (list): List of [start, end] timestamps. Optional if auto_detect=True.
            auto_detect (bool): If True, runs highlight detection first (default: False).
            max_clips (int): Maximum number of clips to extract (default: 10).
            min_duration (float): Minimum clip duration in seconds (default: 30.0).
            min_energy_score (float): Minimum auto-detected highlight score (default: 6.0).
            top_percent (float): For auto_detect — top % of energy windows (default: 25.0).
            padding (float): Extra seconds before/after each clip (default: 0.5).

        Output: JSON manifest + individual .mp4 clip files.
        """
        segments = params.get("segments")
        auto_detect = params.get("auto_detect", False)
        max_clips = params.get("max_clips", 10)
        min_duration = max(float(params.get("min_duration", MIN_CLIP_DURATION_SECONDS)), MIN_CLIP_DURATION_SECONDS)
        min_energy_score = float(params.get("min_energy_score", 6.0))
        top_percent = params.get("top_percent", 25.0)
        padding = params.get("padding", 0.5)

        # Get video duration
        probe = ffmpeg.probe(input_path)
        total_duration = float(probe["format"]["duration"])

        # Step 1: Get segments (auto-detect or from params)
        if not segments and auto_detect:
            print(f"[ExtractClips] Auto-detecting highlights (top {top_percent}%)...")
            detect_params = {
                "window_seconds": 5.0,
                "min_highlight_seconds": min_duration,
                "max_highlights": max_clips * 2,  # detect more, then pick best
                "top_percent": top_percent,
            }
            # Run detection inline using a temp output
            detect_output = output_path.rsplit(".", 1)[0] + "_detect.json"
            DetectHighlightsOperation.execute(input_path, detect_output, detect_params)

            with open(detect_output, "r", encoding="utf-8") as f:
                detect_data = json.load(f)

            highlights = detect_data.get("highlights", [])

            if highlights:
                highlights = [
                    h for h in highlights
                    if h.get("end", 0) - h.get("start", 0) >= min_duration
                    and h.get("energy_score", 0) >= min_energy_score
                ]
                # Sort by energy score (best first) and take only real candidates.
                highlights.sort(key=lambda h: h.get("energy_score", 0), reverse=True)
                highlights = highlights[:max_clips]
                highlights.sort(key=lambda h: h["start"])
                segments = [[h["start"], h["end"]] for h in highlights]
            else:
                segments = []

            if not segments:
                print(
                    "[ExtractClips] No strategic highlights passed quality gates "
                    f"(min_duration={min_duration:.1f}s, min_energy_score={min_energy_score:.1f})."
                )

            # Clean up temp file
            if os.path.exists(detect_output):
                os.remove(detect_output)
        elif segments:
            # Apply padding and clamp to video bounds
            padded = []
            for start, end in segments:
                padded_start = max(0, start - padding)
                padded_end = min(total_duration, end + padding)
                if padded_end - padded_start >= min_duration:
                    padded.append([padded_start, padded_end])
            segments = padded[:max_clips]

        if not segments:
            print("[ExtractClips] No segments found. Nothing to extract.")
            result = {"clips": [], "total_clips": 0, "error": "No highlights detected"}
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return

        print(f"[ExtractClips] Extracting {len(segments)} individual clips...")

        # Step 2: Extract each clip as a separate .mp4
        # Determine output directory (same dir as output_path)
        output_dir = os.path.dirname(output_path)
        base_name = os.path.basename(output_path).rsplit(".", 1)[0]

        clips_info = []
        for i, (start, end) in enumerate(segments):
            duration = end - start
            if duration < min_duration:
                print(
                    f"  Skip clip {i + 1}: {duration:.1f}s below "
                    f"minimum {min_duration:.1f}s"
                )
                continue

            clip_filename = f"{base_name}_clip_{i + 1}.mp4"
            clip_path = os.path.join(output_dir, clip_filename)

            try:
                print(f"  Clip {i + 1}/{len(segments)}: {start:.1f}s - {end:.1f}s ({duration:.1f}s)")

                # Use FFmpeg to extract the clip with re-encoding for clean cuts
                (
                    ffmpeg
                    .input(input_path, ss=start, t=duration)
                    .output(
                        clip_path,
                        vcodec='libx264',
                        acodec='aac',
                        pix_fmt='yuv420p',
                        movflags='+faststart',
                        **{'b:a': '192k'}
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )

                # Verify the clip was created
                if os.path.exists(clip_path) and os.path.getsize(clip_path) > 0:
                    clips_info.append({
                        "clip_number": i + 1,
                        "filename": clip_filename,
                        "start": round(start, 2),
                        "end": round(end, 2),
                        "duration": round(duration, 1),
                        "file_path": clip_path,
                    })
                else:
                    print(f"  Warning: Clip {i + 1} was not created properly")

            except ffmpeg.Error as e:
                error_log = e.stderr.decode() if e.stderr else str(e)
                print(f"  Error extracting clip {i + 1}: {error_log[:200]}")
                continue

        # Step 3: Write manifest JSON as the operation output
        total_clip_duration = sum(c["duration"] for c in clips_info)

        manifest = {
            "total_clips": len(clips_info),
            "total_duration": round(total_duration, 1),
            "total_clip_duration": round(total_clip_duration, 1),
            "clip_percentage": round((total_clip_duration / total_duration) * 100, 1) if total_duration > 0 else 0,
            "clips": clips_info,
        }

        # Write manifest as the output file
        manifest_path = output_path.rsplit(".", 1)[0] + ".json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # Also write to expected output_path
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"[ExtractClips] Done! Extracted {len(clips_info)} clips "
              f"({total_clip_duration:.0f}s from {total_duration:.0f}s video)")
