"""
Plan Scenes Operation
Takes a transcription (from a previous transcribe step) and uses AI to generate
a scene plan. Outputs JSON that the remotion_render operation consumes.

This operation doesn't modify the video — it produces a sidecar JSON file
with scenes and palette that gets passed to the next Remotion render step.
"""

from app.workers.operations.base import BaseOperation
from app.services.scene_planner import plan_scenes
from typing import Dict, Any
import json
import os


class PlanScenesOperation(BaseOperation):
    """Uses AI to analyze transcription and generate visual scene plan."""

    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass  # transcription_path is optional — can also receive words directly

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        """
        Generates a scene plan from transcription data.

        The operation looks for transcription data in this order:
        1. params["words"] — direct word list
        2. Sidecar .json from a previous transcribe operation
        3. Sidecar .json matching input_path pattern

        Params:
            words (list): Direct word timing list [{"word", "start", "end"}, ...]
            provider (str): AI provider — "claude", "gemini", or "auto" (default)
            custom_prompt (str): Additional context for the AI
            fps (int): Video frame rate (default: 30)

        Output: Copies input video to output + writes scene plan as sidecar JSON.
        """
        words = params.get("words")
        provider = params.get("provider", "auto")
        custom_prompt = params.get("custom_prompt", "")
        fps = params.get("fps", 30)

        # If no words provided, look for transcription sidecar files
        if not words:
            words = _find_transcription_words(input_path)

        if not words:
            print("[PlanScenes] No transcription data found. Skipping scene planning.")
            # Pass through — copy input to output
            import shutil
            shutil.copy2(input_path, output_path)
            return

        print(f"[PlanScenes] Planning scenes for {len(words)} words ({words[-1]['end']:.0f}s video)...")

        # Call AI scene planner
        plan = plan_scenes(
            words=words,
            fps=fps,
            provider=provider,
            custom_prompt=custom_prompt,
        )

        scenes = plan.get("scenes", [])
        palette = plan.get("palette", {})
        narrative = plan.get("narrativeFormat", "unknown")

        print(f"[PlanScenes] Generated {len(scenes)} scenes (format: {narrative})")

        # Write scene plan as sidecar JSON
        plan_path = output_path + ".scenes.json"
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump({
                "scenes": scenes,
                "palette": palette,
                "narrativeFormat": narrative,
                "words": words,  # pass through for Remotion
            }, f, ensure_ascii=False, indent=2)

        print(f"[PlanScenes] Scene plan saved to {plan_path}")

        # Copy video through (this operation doesn't modify the video)
        import shutil
        shutil.copy2(input_path, output_path)


def _find_transcription_words(input_path: str) -> list:
    """Look for transcription data in sidecar JSON files."""
    # Try common patterns for transcription sidecar files
    candidates = [
        input_path + ".json",
        input_path.rsplit(".", 1)[0] + ".json",
    ]

    # Also check the step directory for any transcription output
    dir_path = os.path.dirname(input_path)
    base_name = os.path.basename(input_path).split("_step_")[0]
    if dir_path:
        for f in os.listdir(dir_path):
            if base_name in f and f.endswith(".json"):
                candidates.append(os.path.join(dir_path, f))

    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Check for word-level timing data
                words = data.get("words")
                if words and isinstance(words, list) and len(words) > 0:
                    if "start" in words[0] and "word" in words[0]:
                        print(f"[PlanScenes] Found {len(words)} words in {path}")
                        return words

                # Check for segments with word data
                segments = data.get("segments", [])
                if segments:
                    all_words = []
                    for seg in segments:
                        seg_words = seg.get("words", [])
                        all_words.extend(seg_words)
                    if all_words and "start" in all_words[0]:
                        print(f"[PlanScenes] Found {len(all_words)} words from segments in {path}")
                        return all_words

            except Exception as e:
                print(f"[PlanScenes] Could not read {path}: {e}")
                continue

    return []
