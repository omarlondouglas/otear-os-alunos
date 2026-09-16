"""
Eval Cuts Operation
Avalia boundaries de cada clipe contra o transcript word-level. Para cada cut:
  - GOOD: silencio >= 200ms ao redor
  - WARN: gap < 100ms (apertado)
  - BAD:  cuts dentro de uma palavra
Sugere snap-to-nearest-word-boundary quando BAD ou WARN.

Input:
  - input_path: JSON {source, clips:[{title,start,end,...}]} (output do select_clips)
  - params:
      transcript_path: caminho do JSON de transcricao (auto-resolvido se ausente)
      apply: bool (default False) - se True, aplica os snaps no proprio JSON

Output:
  - output_path (.json): {clips: [{title, start, end, overall, start_eval, end_eval,
                                   suggested_start, suggested_end}]}
  - sidecar .review.md
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List, Optional
import json
import os


SILENCE_GOOD = 0.20
SILENCE_WARN = 0.10
SNAP_RADIUS = 0.50


class EvalCutsOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        clips_payload = _load_json(input_path)
        if "clips" not in clips_payload:
            raise ValueError(
                f"eval_cuts: input {input_path} does not contain 'clips' "
                "(run select_clips before eval_cuts)"
            )

        transcript_path = params.get("transcript_path") or _resolve_transcript_path(input_path, clips_payload)
        if not transcript_path or not os.path.exists(transcript_path):
            raise ValueError(
                f"eval_cuts: transcript JSON not found "
                f"(transcript_path missing and no sidecar near {input_path})"
            )

        transcript = _load_json(transcript_path)
        words = _load_words(transcript)
        clips = clips_payload.get("clips", [])

        if not words:
            print("[EvalCuts] transcript has no word/segment timestamps; skipping eval")
            report = []
        else:
            report = [_evaluate_clip(c, words) for c in clips]

        apply = bool(params.get("apply", False))
        if apply and report:
            for clip, r in zip(clips, report):
                clip["start"] = r["suggested_start"]
                clip["end"] = r["suggested_end"]
            clips_payload["clips"] = clips
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(clips_payload, f, ensure_ascii=False, indent=2)
            print(f"[EvalCuts] applied snaps to {input_path}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"clips": report}, f, ensure_ascii=False, indent=2)
        review_path = output_path + ".review.md"
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(_render_md(report))

        counts = {"good": 0, "warn": 0, "bad": 0, "unknown": 0}
        for r in report:
            counts[r["overall"]] = counts.get(r["overall"], 0) + 1
        print(
            f"[EvalCuts] {counts['good']} good, {counts['warn']} warn, "
            f"{counts['bad']} bad ({len(report)} clips)"
        )


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_transcript_path(input_path: str, clips_payload: Optional[dict] = None) -> Optional[str]:
    candidates = [input_path + ".transcript.json", os.path.splitext(input_path)[0] + ".json"]
    source = (clips_payload or {}).get("source")
    if source:
        candidates.extend([source + ".json", source + ".transcript.json"])
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return None


def _load_words(transcript: dict) -> List[Dict[str, Any]]:
    words = transcript.get("words") or []
    if words and isinstance(words[0], dict) and "start" in words[0]:
        out = []
        for w in words:
            if w.get("start") is None or w.get("end") is None:
                continue
            out.append({
                "start": float(w["start"]),
                "end": float(w["end"]),
                "text": str(w.get("word") or w.get("text", "")).strip(),
            })
        return sorted(out, key=lambda x: x["start"])
    segs = transcript.get("segments") or []
    return [
        {"start": float(s["start"]), "end": float(s["end"]), "text": s.get("text", "").strip()}
        for s in segs
    ]


def _evaluate_boundary(t: float, words: List[Dict[str, Any]], side: str) -> Dict[str, Any]:
    if not words:
        return {"status": "unknown", "reason": "no word timestamps", "snap": None}

    inside = None
    prev_end = None
    next_start = None
    for w in words:
        if w["start"] <= t < w["end"]:
            inside = w
            break
        if w["end"] <= t:
            prev_end = w["end"]
        elif w["start"] > t and next_start is None:
            next_start = w["start"]
            break

    if inside:
        snap = inside["end"] if side == "start" else inside["start"]
        return {
            "status": "bad",
            "reason": f'cuts inside word "{inside["text"]}"',
            "snap": round(snap, 3),
        }

    gap_before = (t - prev_end) if prev_end is not None else None
    gap_after = (next_start - t) if next_start is not None else None
    silence = (gap_before or 0) + (gap_after or 0)

    if silence >= SILENCE_GOOD:
        return {"status": "good", "reason": f"{silence*1000:.0f}ms silence around cut", "snap": None}
    if silence >= SILENCE_WARN:
        return {"status": "warn", "reason": f"tight {silence*1000:.0f}ms gap", "snap": None}

    candidates = []
    if gap_before is not None and gap_before <= SNAP_RADIUS:
        candidates.append(("prev_end", prev_end, gap_before))
    if gap_after is not None and gap_after <= SNAP_RADIUS:
        candidates.append(("next_start", next_start, gap_after))
    if candidates:
        candidates.sort(key=lambda x: x[2])
        return {
            "status": "warn",
            "reason": "almost mid-word - snap suggested",
            "snap": round(candidates[0][1], 3),
        }
    return {"status": "warn", "reason": "no clean boundary nearby", "snap": None}


def _evaluate_clip(clip: Dict[str, Any], words: List[Dict[str, Any]]) -> Dict[str, Any]:
    start_eval = _evaluate_boundary(float(clip["start"]), words, "start")
    end_eval = _evaluate_boundary(float(clip["end"]), words, "end")
    overall = "good"
    for ev in (start_eval, end_eval):
        if ev["status"] == "bad":
            overall = "bad"
            break
        if ev["status"] == "warn" and overall == "good":
            overall = "warn"
    return {
        "title": clip.get("title", ""),
        "start": clip["start"],
        "end": clip["end"],
        "overall": overall,
        "start_eval": start_eval,
        "end_eval": end_eval,
        "suggested_start": start_eval["snap"] if start_eval["snap"] is not None else clip["start"],
        "suggested_end": end_eval["snap"] if end_eval["snap"] is not None else clip["end"],
    }


def _render_md(report: List[Dict[str, Any]]) -> str:
    icon = {"good": "OK", "warn": "WARN", "bad": "BAD", "unknown": "?"}
    counts = {"good": 0, "warn": 0, "bad": 0}
    for r in report:
        counts[r["overall"]] = counts.get(r["overall"], 0) + 1

    lines = [
        "# Avaliacao dos cortes",
        "",
        f"**{counts['good']} OK · {counts['warn']} WARN · {counts['bad']} BAD**",
        "",
    ]
    for i, r in enumerate(report, 1):
        s_snap = (
            f"  · snap -> `{r['start_eval']['snap']:.2f}s`"
            if r["start_eval"]["snap"] is not None
            else ""
        )
        e_snap = (
            f"  · snap -> `{r['end_eval']['snap']:.2f}s`"
            if r["end_eval"]["snap"] is not None
            else ""
        )
        lines += [
            f"## {i}. {r['title']}  [{icon[r['overall']]}]",
            f"- start `{r['start']:.2f}s` -> {icon[r['start_eval']['status']]} "
            f"({r['start_eval']['reason']}){s_snap}",
            f"- end   `{r['end']:.2f}s` -> {icon[r['end_eval']['status']]} "
            f"({r['end_eval']['reason']}){e_snap}",
            "",
        ]
    if any(r["overall"] != "good" for r in report):
        lines += ["---", "", "Para aplicar snaps automaticamente: re-rodar com params.apply=true", ""]
    return "\n".join(lines)
