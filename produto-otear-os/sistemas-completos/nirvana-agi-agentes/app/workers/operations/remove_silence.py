from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List
import ffmpeg
import re
import math
import os
import logging

logger = logging.getLogger(__name__)

class RemoveSilenceOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        # Support both param naming conventions (preset uses threshold/min_silence_duration)
        threshold = params.get('threshold', params.get('noise', -35))
        # Normalize threshold to dB string
        if isinstance(threshold, (int, float)):
            noise_level = f"{threshold}dB"
        else:
            noise_level = str(threshold)

        min_silence_duration = params.get('min_silence_duration', params.get('duration', 0.45))
        padding = params.get('padding', 0.08)

        logger.info(
            "Detecting silence (noise < %s, min duration > %ss, padding %ss)...",
            noise_level,
            min_silence_duration,
            padding,
        )

        # 1. Detect silence
        try:
            out, err = (
                ffmpeg
                .input(input_path)
                .filter('silencedetect', noise=noise_level, d=min_silence_duration)
                .output('null', f='null')
                .run(capture_stderr=True)
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Silence detection failed: {e.stderr.decode() if e.stderr else str(e)}")

        stderr_output = err.decode()

        # 2. Parse timestamps
        silence_starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', stderr_output)]
        silence_ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', stderr_output)]

        # Handle case where silence starts but doesn't end (end of video)
        probe = ffmpeg.probe(input_path)
        total_duration = float(probe['format']['duration'])
        if len(silence_starts) > len(silence_ends):
            silence_ends.append(total_duration)

        silences = list(zip(silence_starts, silence_ends))

        if not silences:
            logger.info("No silence detected. Copying file...")
            import shutil
            shutil.copy2(input_path, output_path)
            return

        # 3. Apply padding — shrink each silence by padding on both sides
        # This preserves natural breathing room around speech
        padded_silences = []
        for start, end in silences:
            padded_start = start + padding
            padded_end = end - padding
            # Only cut if the remaining silence is still meaningful (> 0.3s)
            if padded_end - padded_start > 0.3:
                padded_silences.append((padded_start, padded_end))

        if not padded_silences:
            logger.info("After padding, no significant silences to remove. Copying file...")
            import shutil
            shutil.copy2(input_path, output_path)
            return

        # 4. Safety check — don't remove more than 50% of the video
        total_silence_removed = sum(end - start for start, end in padded_silences)
        removal_ratio = total_silence_removed / total_duration
        logger.info(
            "Would remove %.1fs of %.1fs (%s)",
            total_silence_removed,
            total_duration,
            f"{removal_ratio:.0%}",
        )

        if removal_ratio > 0.5:
            logger.warning(
                "Would remove %s of video. Raising threshold to be more conservative...",
                f"{removal_ratio:.0%}",
            )
            # Keep only the longest silences to stay under 40% removal
            padded_silences.sort(key=lambda s: s[1] - s[0], reverse=True)
            conservative_silences = []
            cumulative = 0.0
            max_removal = total_duration * 0.4
            for start, end in padded_silences:
                seg_len = end - start
                if cumulative + seg_len <= max_removal:
                    conservative_silences.append((start, end))
                    cumulative += seg_len
            padded_silences = sorted(conservative_silences, key=lambda s: s[0])
            logger.info(
                "Adjusted: removing %.1fs (%s)",
                cumulative,
                f"{(cumulative/total_duration):.0%}",
            )

            if not padded_silences:
                import shutil
                shutil.copy2(input_path, output_path)
                return

        # 5. Calculate "keep" segments (invert silence)
        keep_segments = []
        current_time = 0.0

        for start, end in padded_silences:
            if start > current_time:
                keep_segments.append((current_time, start))
            current_time = end

        if current_time < total_duration:
            keep_segments.append((current_time, total_duration))
            
        if not keep_segments:
             # Should theoretically not happen if silences were found but effectively means "all silence"
             # Let's just output an empty video or handle error, but for now copying original might be safer fallback
             # or raising error. Let's create a minimal video.
             raise RuntimeError("Video is entirely silent/removed")

        logger.info(
            "Found %d silent segments. Keeping %d active segments.",
            len(silences),
            len(keep_segments),
        )

        # 4. Construct Filter Complex
        # [0:v]trim=start=0:end=10,setpts=PTS-STARTPTS[v0];
        # [0:a]atrim=start=0:end=10,asetpts=PTS-STARTPTS[a0];
        # ...
        # [v0][a0][v1][a1]...concat=n=N:v=1:a=1[v][a]
        
        inputs = ffmpeg.input(input_path)
        streams = []
        
        for i, (start, end) in enumerate(keep_segments):
            # Video trim
            v = inputs.video.filter('trim', start=start, end=end).filter('setpts', 'PTS-STARTPTS')
            # Audio trim
            a = inputs.audio.filter('atrim', start=start, end=end).filter('asetpts', 'PTS-STARTPTS')
            streams.extend([v, a])
            
        # Concat
        joined = ffmpeg.concat(*streams, v=1, a=1).node
        v_out = joined[0]
        a_out = joined[1]
        
        output = ffmpeg.output(v_out, a_out, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')
        
        logger.info("Running concat operation...")
        output.run(overwrite_output=True)
