"""
Detect Fillers Operation
Detecta silencios + filler words ("uh", "tipo", "ne") no transcript word-level.
Produz {keep, removed} - ranges de audio para manter e remover.

Diferente do remove_silence (que so deteca silencio acustico), este olha
WORDS no transcript para remover filler words explicitos.

Input:
  - input_path: video file (passthrough)
  - params:
      transcript_path: caminho do JSON do transcribe (auto-resolvido se ausente)
      silence_threshold: gap minimo entre palavras para cortar (default 0.6s)
      padding: padding ao redor da fala (default 0.08s)
      fillers: lista extra de fillers customizados
      no_fillers: bool - desativa remocao de fillers (so silencio)

Output:
  - output_path (.json): {source_duration, silence_threshold, padding, keep, removed}
  - sidecar .review.md
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List, Set, Optional, Tuple
import json
import os
import re
import shutil


FILLERS_PT: Set[str] = {
    "ah", "eh", "hum", "hmm", "uhm", "um", "er", "aham", "ahn",
    "tipo", "ne", "né",
}

FILLER_PHRASES: List[List[str]] = [
    ["deixa", "eu", "repetir"],
    ["pode", "cortar"],
    ["pera", "ai"],
    ["pera", "aí"],
    ["espera", "um", "pouco"],
]


class DetectFillersOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        transcript_path = params.get("transcript_path") or _resolve_transcript_path(input_path)
        if not transcript_path or not os.path.exists(transcript_path):
            raise ValueError(
                f"detect_fillers: transcript JSON not found "
                f"(set params.transcript_path or run 'transcribe' before this step)"
            )

        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = json.load(f)

        words = transcript.get("words", [])
        if not words:
            raise ValueError("detect_fillers: transcript has no word-level timestamps")

        silence_threshold = float(params.get("silence_threshold", 0.6))
        padding = float(params.get("padding", 0.08))
        custom = {w.lower() for w in params.get("fillers", [])} if params.get("fillers") else set()
        no_fillers = bool(params.get("no_fillers", False))

        filler_idx = set() if no_fillers else _detect_filler_indices(words, custom)
        keep, removed = _build_keep_ranges(words, filler_idx, silence_threshold, padding)

        total = float(transcript.get("duration") or (words[-1]["end"] if words else 0))

        result = {
            "source_duration": total,
            "silence_threshold": silence_threshold,
            "padding": padding,
            "keep": keep,
            "removed": removed,
        }

        # output_path eh um vide; usamos passthrough + sidecar JSON
        if not output_path.endswith(".json"):
            shutil.copy2(input_path, output_path)
            json_path = output_path + ".json"
        else:
            json_path = output_path

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        review_path = json_path + ".review.md"
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(_write_review_md(keep, removed, total))

        kept_dur = sum(r["end"] - r["start"] for r in keep)
        print(
            f"[DetectFillers] {len(keep)} keep ranges, {len(removed)} removed; "
            f"{total:.1f}s -> {kept_dur:.1f}s ({100*(total-kept_dur)/total:.1f}% cut)"
        )


def _resolve_transcript_path(input_path: str) -> Optional[str]:
    cand = input_path + ".json"
    if os.path.exists(cand):
        return cand
    base, _ = os.path.splitext(input_path)
    cand2 = base + ".json"
    if os.path.exists(cand2):
        return cand2
    return None


def _normalize(word: str) -> str:
    return re.sub(r"[^\w\sáéíóúâêîôûãõàèìòùç]", "", word.lower()).strip()


def _detect_filler_indices(words: List[Dict[str, Any]], custom: Set[str]) -> Set[int]:
    fillers = FILLERS_PT | custom
    out: Set[int] = set()
    for i, w in enumerate(words):
        if _normalize(w.get("word", "")) in fillers:
            out.add(i)
    normed = [_normalize(w.get("word", "")) for w in words]
    for phrase in FILLER_PHRASES:
        n = len(phrase)
        for i in range(len(normed) - n + 1):
            if normed[i:i + n] == phrase:
                for k in range(n):
                    out.add(i + k)
    return out


def _build_keep_ranges(
    words: List[Dict[str, Any]],
    filler_idx: Set[int],
    silence_threshold: float,
    padding: float,
) -> Tuple[List[Dict[str, float]], List[Dict[str, Any]]]:
    if not words:
        return [], []
    keep: List[Dict[str, float]] = []
    removed: List[Dict[str, Any]] = []

    current_start = None
    current_end = None
    prev_end = None

    def flush():
        nonlocal current_start, current_end
        if current_start is not None and current_end is not None and current_end > current_start:
            keep.append({
                "start": max(0, current_start - padding),
                "end": current_end + padding,
            })
        current_start = None
        current_end = None

    for i, w in enumerate(words):
        if i in filler_idx:
            if current_start is not None:
                flush()
            removed.append({
                "start": w["start"],
                "end": w["end"],
                "reason": f"filler:{w.get('word', '').strip()}",
            })
            prev_end = w["end"]
            continue

        if prev_end is not None:
            gap = w["start"] - prev_end
            if gap > silence_threshold:
                flush()
                removed.append({
                    "start": prev_end,
                    "end": w["start"],
                    "reason": f"silence:{gap:.2f}s",
                })

        if current_start is None:
            current_start = w["start"]
        current_end = w["end"]
        prev_end = w["end"]

    flush()

    keep.sort(key=lambda r: r["start"])
    merged: List[Dict[str, float]] = []
    for r in keep:
        if merged and r["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], r["end"])
        else:
            merged.append(dict(r))
    return merged, removed


def _write_review_md(keep, removed, total_duration: float) -> str:
    kept_dur = sum(r["end"] - r["start"] for r in keep)
    removed_dur = total_duration - kept_dur
    pct = 100 * removed_dur / total_duration if total_duration else 0

    def fmt(s: float) -> str:
        m = int(s // 60)
        sec = s - m * 60
        return f"{m:02d}:{sec:05.2f}"

    lines = [
        "# Silence & Filler Cuts Review", "",
        f"**Total duration:** {fmt(total_duration)}",
        f"**Kept:** {fmt(kept_dur)} in {len(keep)} ranges",
        f"**Removed:** {fmt(removed_dur)} ({pct:.1f}% of source)",
        "",
        "## Keep ranges", "",
    ]
    for i, r in enumerate(keep, 1):
        lines.append(f"{i}. `{fmt(r['start'])} -> {fmt(r['end'])}` ({r['end']-r['start']:.2f}s)")
    lines += ["", "## Removed ranges", ""]
    for i, r in enumerate(removed, 1):
        lines.append(
            f"{i}. `{fmt(r['start'])} -> {fmt(r['end'])}` "
            f"({r['end']-r['start']:.2f}s) - {r['reason']}"
        )
    return "\n".join(lines)
