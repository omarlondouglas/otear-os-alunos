"""
Detect Highlights Operation
Analyzes audio energy to detect the most engaging moments of a video.
Uses a SINGLE FFmpeg pass to extract raw PCM audio, then analyzes RMS
energy per window in Python. Much faster than per-window FFmpeg calls.
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List
import ffmpeg
import json
import math
import os
import struct
import subprocess
import array


class DetectHighlightsOperation(BaseOperation):
    """Analyzes a video's audio track to detect high-energy, viral-worthy moments."""

    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        window_seconds = params.get("window_seconds", 5.0)
        min_highlight_seconds = params.get("min_highlight_seconds", 3.0)
        max_highlights = params.get("max_highlights", 20)
        top_percent = params.get("top_percent", 30.0)

        print(f"[DetectHighlights] Analyzing audio energy (window={window_seconds}s, top={top_percent}%)...")

        # 1. Get video duration
        probe = ffmpeg.probe(input_path)
        total_duration = float(probe["format"]["duration"])

        # 2. Single-pass audio analysis via raw PCM
        windows = DetectHighlightsOperation._analyze_single_pass(
            input_path, total_duration, window_seconds
        )

        if not windows:
            result = {
                "total_duration": total_duration,
                "total_highlights": 1,
                "highlights": [{
                    "start": 0.0,
                    "end": min(total_duration, 60.0),
                    "energy_score": 5.0,
                    "rank": 1,
                    "reason": "audio_analysis_fallback"
                }],
                "energy_profile": []
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return

        # 3. Score and rank
        scored = DetectHighlightsOperation._score_windows(windows, top_percent)

        # 4. Merge adjacent highlights
        highlights = DetectHighlightsOperation._merge_into_highlights(
            scored, window_seconds, min_highlight_seconds, total_duration
        )

        # 5. Rank and limit
        highlights.sort(key=lambda h: h["energy_score"], reverse=True)
        highlights = highlights[:max_highlights]
        for i, h in enumerate(highlights):
            h["rank"] = i + 1
        highlights.sort(key=lambda h: h["start"])

        energy_profile = [
            {
                "start": round(w["start"], 2),
                "end": round(w["end"], 2),
                "rms_db": round(w["rms_db"], 1),
                "is_speech": w["is_speech"],
                "normalized_energy": round(w["normalized_energy"], 2)
            }
            for w in windows
        ]

        result = {
            "total_duration": round(total_duration, 2),
            "total_highlights": len(highlights),
            "highlights": highlights,
            "energy_profile": energy_profile
        }

        json_output = output_path.rsplit(".", 1)[0] + ".json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"[DetectHighlights] Found {len(highlights)} highlights from {total_duration:.0f}s video")

    @staticmethod
    def _analyze_single_pass(
        input_path: str, total_duration: float, window_seconds: float
    ) -> List[Dict[str, Any]]:
        """Extract raw PCM audio in ONE FFmpeg call, then compute RMS per window in Python."""
        sample_rate = 16000  # 16kHz mono is enough for energy analysis
        windows = []

        try:
            # Single FFmpeg call: extract entire audio as raw 16-bit PCM mono
            cmd = [
                "ffmpeg", "-i", input_path,
                "-vn",                      # no video
                "-ac", "1",                 # mono
                "-ar", str(sample_rate),    # 16kHz
                "-f", "s16le",              # raw 16-bit signed little-endian
                "-acodec", "pcm_s16le",
                "-"                         # output to stdout
            ]

            print(f"[DetectHighlights] Extracting audio (single pass)...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=120,  # 2 min max for audio extraction
            )

            if result.returncode != 0:
                stderr_text = result.stderr.decode('utf-8', errors='replace')[-500:]
                print(f"[DetectHighlights] FFmpeg audio extraction failed: {stderr_text}")
                return []

            raw_audio = result.stdout
            if len(raw_audio) < 100:
                print(f"[DetectHighlights] Audio too short ({len(raw_audio)} bytes)")
                return []

            # Parse raw PCM samples (16-bit signed, little-endian)
            num_samples = len(raw_audio) // 2
            samples = array.array('h')  # signed short
            samples.frombytes(raw_audio[:num_samples * 2])

            print(f"[DetectHighlights] Analyzing {num_samples} samples ({num_samples/sample_rate:.0f}s audio)...")

            # Compute RMS energy per window
            samples_per_window = int(window_seconds * sample_rate)

            for i in range(0, num_samples, samples_per_window):
                chunk = samples[i:i + samples_per_window]
                if len(chunk) < sample_rate // 2:  # skip chunks < 0.5s
                    break

                start_time = i / sample_rate
                end_time = min((i + len(chunk)) / sample_rate, total_duration)

                # RMS calculation
                sum_sq = sum(s * s for s in chunk)
                rms = math.sqrt(sum_sq / len(chunk))

                # Convert to dB (reference: 32768 = 0dB for 16-bit audio)
                if rms > 0:
                    rms_db = 20 * math.log10(rms / 32768.0)
                else:
                    rms_db = -96.0

                # Speech detection: typical speech is -40 to -10 dB
                is_speech = rms_db > -45.0

                windows.append({
                    "start": start_time,
                    "end": end_time,
                    "rms_db": rms_db,
                    "is_speech": is_speech,
                    "normalized_energy": 0.0,
                })

        except subprocess.TimeoutExpired:
            print("[DetectHighlights] FFmpeg audio extraction timed out")
            return []
        except Exception as e:
            print(f"[DetectHighlights] Error in single-pass analysis: {e}")
            return []

        # Normalize energy to 0-10 scale
        if windows:
            speech_windows = [w for w in windows if w["is_speech"]]
            if not speech_windows:
                # Lower threshold and try again
                print("[DetectHighlights] No speech detected at -45dB, trying -55dB...")
                for w in windows:
                    w["is_speech"] = w["rms_db"] > -55.0
                speech_windows = [w for w in windows if w["is_speech"]]

            if speech_windows:
                min_rms = min(w["rms_db"] for w in speech_windows)
                max_rms = max(w["rms_db"] for w in speech_windows)
                rms_range = max_rms - min_rms if max_rms > min_rms else 1.0

                for w in windows:
                    if w["is_speech"]:
                        w["normalized_energy"] = round(
                            ((w["rms_db"] - min_rms) / rms_range) * 10.0, 2
                        )
                    else:
                        w["normalized_energy"] = 0.0

                print(f"[DetectHighlights] Speech windows: {len(speech_windows)}/{len(windows)} "
                      f"(RMS range: {min_rms:.1f} to {max_rms:.1f} dB)")
            else:
                print("[DetectHighlights] WARNING: No speech detected at all!")

        return windows

    @staticmethod
    def _score_windows(
        windows: List[Dict[str, Any]], top_percent: float
    ) -> List[Dict[str, Any]]:
        """Mark windows in the top N% energy as highlights."""
        speech_windows = [w for w in windows if w["is_speech"]]
        if not speech_windows:
            # If no speech, mark ALL windows with energy > 0 as potential highlights
            for w in windows:
                w["is_highlight"] = w["rms_db"] > -55.0
            return windows

        sorted_by_energy = sorted(speech_windows, key=lambda w: w["normalized_energy"], reverse=True)
        cutoff_index = max(1, int(len(sorted_by_energy) * (top_percent / 100.0)))
        threshold = sorted_by_energy[min(cutoff_index, len(sorted_by_energy) - 1)]["normalized_energy"]

        for w in windows:
            w["is_highlight"] = w["is_speech"] and w["normalized_energy"] >= threshold

        return windows

    @staticmethod
    def _merge_into_highlights(
        windows: List[Dict[str, Any]],
        window_seconds: float,
        min_highlight_seconds: float,
        total_duration: float
    ) -> List[Dict[str, Any]]:
        """Merge adjacent highlight windows into contiguous segments."""
        highlights = []
        current_start = None
        current_end = None
        current_energy_sum = 0.0
        current_count = 0

        for w in windows:
            if w.get("is_highlight"):
                if current_start is None:
                    current_start = w["start"]
                    current_end = w["end"]
                    current_energy_sum = w["normalized_energy"]
                    current_count = 1
                elif w["start"] <= current_end + window_seconds:
                    current_end = w["end"]
                    current_energy_sum += w["normalized_energy"]
                    current_count += 1
                else:
                    if current_end - current_start >= min_highlight_seconds:
                        highlights.append({
                            "start": round(max(0, current_start - 0.5), 2),
                            "end": round(min(total_duration, current_end + 0.5), 2),
                            "energy_score": round(current_energy_sum / current_count, 2),
                            "reason": "high_energy_audio"
                        })
                    current_start = w["start"]
                    current_end = w["end"]
                    current_energy_sum = w["normalized_energy"]
                    current_count = 1

        if current_start is not None and current_end - current_start >= min_highlight_seconds:
            highlights.append({
                "start": round(max(0, current_start - 0.5), 2),
                "end": round(min(total_duration, current_end + 0.5), 2),
                "energy_score": round(current_energy_sum / current_count, 2),
                "reason": "high_energy_audio"
            })

        return highlights
