"""
Fast Subtitles Operation
Queima legendas Hormozi-style (word-by-word highlight) usando ffmpeg + ASS.
~10-15x mais rapido que Remotion para casos sem motion graphics.

Suporta:
  - Position center / top / bottom
  - Vertical (1080x1920) com crop central
  - Headline persistente
  - Background opaco atras das legendas
  - Preview PNG (single-frame ~1-2s)

Input:
  - input_path: video file
  - params:
      transcript_path: caminho do JSON do transcribe (auto-resolvido se ausente)
      position: "center" | "top" | "bottom" (default "bottom")
      vertical: bool (default False) - crop para 1080x1920
      font: nome da fonte (default "Urbanist")
      font_size: px (default 72)
      color_primary: hex sem # (default "FFFFFF")
      color_highlight: hex sem # (default "FFD600")
      margin_v: px (override default)
      max_words: palavras por linha (default 3)
      preview_at: float - se setado, gera PNG single-frame ao inves de MP4
      subtitle_bg: hex ou "none" (default "none")
      subtitle_bg_alpha: 0-100 (default 80)
      subtitle_bg_padding: px (default 12)
      headline: str
      headline_size, headline_color, headline_bg, headline_bg_alpha
      headline_position: "top" | "bottom" (default "top")

Output:
  - output_path: MP4 final ou PNG (preview_at)
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List, Optional
import json
import math
import os
import subprocess
import tempfile


class FastSubtitlesOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        transcript_path = params.get("transcript_path") or _resolve_transcript_path(input_path)
        if not transcript_path or not os.path.exists(transcript_path):
            raise ValueError(
                "fast_subtitles: transcript JSON not found "
                "(set params.transcript_path or run 'transcribe' before)"
            )

        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = json.load(f)
        words = transcript.get("words", [])
        if not words:
            raise ValueError("fast_subtitles: transcript has no word-level timestamps")

        opts = _normalize_opts(params)
        ass_content = _build_ass(words, opts)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ass", encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(ass_content)
            ass_path = tmp.name

        try:
            ass_for_filter = ass_path.replace("\\", "/").replace(":", "\\:")
            vf_parts = []
            if opts["vertical"]:
                vf_parts.append("crop=ih*9/16:ih,scale=1080:1920")
            vf_parts.append(f"subtitles='{ass_for_filter}'")

            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            if opts["preview_at"] is not None:
                cmd = [
                    "ffmpeg", "-y", "-ss", str(opts["preview_at"]),
                    "-i", input_path,
                    "-vf", ",".join(vf_parts),
                    "-vframes", "1", "-q:v", "2",
                    output_path,
                ]
            else:
                cmd = [
                    "ffmpeg", "-y", "-i", input_path,
                    "-vf", ",".join(vf_parts),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    output_path,
                ]
            print(f"[FastSubtitles] running ffmpeg ({'preview' if opts['preview_at'] is not None else 'mp4'})")
            r = subprocess.run(cmd, capture_output=True, timeout=1800)
            if r.returncode != 0:
                err = r.stderr.decode("utf-8", errors="replace")[-500:]
                raise RuntimeError(f"ffmpeg fast_subtitles failed: {err}")
            print(f"[FastSubtitles] done -> {output_path}")
        finally:
            try:
                os.remove(ass_path)
            except OSError:
                pass


def _resolve_transcript_path(input_path: str) -> Optional[str]:
    cand = input_path + ".json"
    if os.path.exists(cand):
        return cand
    base, _ = os.path.splitext(input_path)
    cand2 = base + ".json"
    if os.path.exists(cand2):
        return cand2
    return None


def _normalize_opts(params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "position": params.get("position", "bottom"),
        "vertical": bool(params.get("vertical", False)),
        "font": params.get("font", "Urbanist"),
        "font_size": int(params.get("font_size", 72)),
        "color_primary": str(params.get("color_primary", "FFFFFF")).replace("#", "").upper(),
        "color_highlight": str(params.get("color_highlight", "FFD600")).replace("#", "").upper(),
        "margin_v": params.get("margin_v"),
        "max_words": int(params.get("max_words", 3)),
        "preview_at": params.get("preview_at"),
        "subtitle_bg": params.get("subtitle_bg", "none"),
        "subtitle_bg_alpha": int(params.get("subtitle_bg_alpha", 80)),
        "subtitle_bg_padding": int(params.get("subtitle_bg_padding", 12)),
        "headline": params.get("headline", ""),
        "headline_font": params.get("headline_font"),
        "headline_size": int(params.get("headline_size", 64)),
        "headline_color": str(params.get("headline_color", "FFFFFF")).replace("#", "").upper(),
        "headline_bg": params.get("headline_bg", "000000"),
        "headline_bg_alpha": int(params.get("headline_bg_alpha", 90)),
        "headline_position": params.get("headline_position", "top"),
        "headline_margin_v": params.get("headline_margin_v"),
    }


def _to_ass_color(hex_color: str, alpha_percent: int = 100) -> str:
    """ASS color format: &HAABBGGRR (alpha=0 opaque, alpha=255 transparent)."""
    h = hex_color.zfill(6)
    r, g, b = h[0:2], h[2:4], h[4:6]
    ass_alpha = round(255 - (alpha_percent / 100) * 255)
    aa = format(ass_alpha, "02X")
    return f"&H{aa}{b}{g}{r}"


def _fmt_time(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s - h * 3600 - m * 60
    cs = round((sec - math.floor(sec)) * 100)
    si = math.floor(sec)
    return f"{h}:{m:02d}:{si:02d}.{cs:02d}"


def _build_ass(words: List[Dict[str, Any]], opts: Dict[str, Any]) -> str:
    PLAY_RES_X = 1080
    PLAY_RES_Y = 1920 if opts["vertical"] else 1080

    alignment = 5 if opts["position"] == "center" else (8 if opts["position"] == "top" else 2)
    if opts["margin_v"] is not None:
        margin_v = int(opts["margin_v"])
    else:
        if opts["position"] == "center":
            margin_v = 0
        elif opts["position"] == "top":
            margin_v = round(PLAY_RES_Y * 0.08)
        else:
            margin_v = round(PLAY_RES_Y * 0.12)

    PRIMARY = _to_ass_color(opts["color_primary"])
    HIGHLIGHT = _to_ass_color(opts["color_highlight"])
    OUTLINE = "&H00000000"

    use_sub_bg = opts["subtitle_bg"] and opts["subtitle_bg"] != "none"
    SUB_BACK = _to_ass_color(opts["subtitle_bg"], opts["subtitle_bg_alpha"]) if use_sub_bg else "&H00000000"
    SUB_BORDER_STYLE = 3 if use_sub_bg else 1
    SUB_OUTLINE_WIDTH = opts["subtitle_bg_padding"] if use_sub_bg else 4
    SUB_SHADOW = 0 if use_sub_bg else 2

    lines = []
    lines.append("[Script Info]")
    lines.append("ScriptType: v4.00+")
    lines.append("Collisions: Normal")
    lines.append(f"PlayResX: {PLAY_RES_X}")
    lines.append(f"PlayResY: {PLAY_RES_Y}")
    lines.append("Timer: 100.0000")
    lines.append("")
    lines.append("[V4+ Styles]")
    lines.append(
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
    )
    lines.append(
        f"Style: Hormozi,{opts['font']},{opts['font_size']},{PRIMARY},{PRIMARY},{OUTLINE},"
        f"{SUB_BACK},-1,0,0,0,100,100,1,0,{SUB_BORDER_STYLE},{SUB_OUTLINE_WIDTH},"
        f"{SUB_SHADOW},{alignment},60,60,{margin_v},1"
    )

    use_headline = bool(opts["headline"] and str(opts["headline"]).strip())
    if use_headline:
        use_head_bg = opts["headline_bg"] and opts["headline_bg"] != "none"
        HEAD_COLOR = _to_ass_color(opts["headline_color"])
        HEAD_BACK = _to_ass_color(opts["headline_bg"], opts["headline_bg_alpha"]) if use_head_bg else "&H00000000"
        HEAD_BORDER = 3 if use_head_bg else 1
        HEAD_OUTLINE = 18 if use_head_bg else 3
        HEAD_SHADOW = 0 if use_head_bg else 2
        head_font = opts["headline_font"] or opts["font"]
        head_align = 2 if opts["headline_position"] == "bottom" else 8
        if opts["headline_margin_v"] is not None:
            head_margin = int(opts["headline_margin_v"])
        else:
            head_margin = round(PLAY_RES_Y * (0.06 if opts["headline_position"] == "bottom" else 0.05))
        lines.append(
            f"Style: Headline,{head_font},{opts['headline_size']},{HEAD_COLOR},"
            f"{HEAD_COLOR},{OUTLINE},{HEAD_BACK},-1,0,0,0,100,100,2,0,{HEAD_BORDER},"
            f"{HEAD_OUTLINE},{HEAD_SHADOW},{head_align},60,60,{head_margin},1"
        )

    lines.append("")
    lines.append("[Events]")
    lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")

    if use_headline:
        head_text = str(opts["headline"]).strip().replace("{", "").replace("}", "").replace("\\", "").upper()
        lines.append(f"Dialogue: 0,0:00:00.00,9:59:59.99,Headline,,0,0,0,,{head_text}")

    max_words = opts["max_words"]
    for i in range(0, len(words), max_words):
        chunk = words[i:i + max_words]
        chunk_start = float(chunk[0]["start"])
        chunk_end = float(chunk[-1]["end"])
        parts = []
        for w in chunk:
            start_ms = max(0, (float(w["start"]) - chunk_start) * 1000)
            end_ms = max(start_ms + 50, (float(w["end"]) - chunk_start) * 1000)
            word = str(w.get("word", "")).strip().replace("{", "").replace("}", "").replace("\\", "").upper()
            parts.append(
                f"{{\\t({start_ms:.0f},{start_ms:.0f},\\c{HIGHLIGHT})"
                f"\\t({end_ms:.0f},{end_ms:.0f},\\c{PRIMARY})}}{word}"
            )
        line_text = " ".join(parts)
        lines.append(
            f"Dialogue: 0,{_fmt_time(chunk_start)},{_fmt_time(chunk_end)},Hormozi,,0,0,0,,{line_text}"
        )

    return "\n".join(lines) + "\n"
