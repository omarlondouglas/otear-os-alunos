from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


SYSTEM_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = SYSTEM_ROOT / "outputs"
DOWNLOADS_DIR = OUTPUTS_DIR / "_downloads"


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:80] or "video"


def run_ytdlp(url: str) -> Path:
    if not shutil.which("yt-dlp"):
        raise RuntimeError("yt-dlp nao esta instalado. Instale com: pip install yt-dlp")

    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_template = str(DOWNLOADS_DIR / f"{stamp}-%(title).80s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--restrict-filenames",
        "-f",
        "bestaudio/best",
        "-o",
        output_template,
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Falha ao baixar o video: {error[-1000:]}")

    candidates = sorted(DOWNLOADS_DIR.glob(f"{stamp}-*"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError("yt-dlp terminou, mas nenhum arquivo foi encontrado.")
    return candidates[0]


def transcribe_with_openai(media_path: Path, language: str | None) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    with media_path.open("rb") as media_file:
        kwargs = {
            "model": os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1"),
            "file": media_file,
            "response_format": "verbose_json",
        }
        if language:
            kwargs["language"] = language
        transcript = client.audio.transcriptions.create(**kwargs)

    segments = []
    for segment in getattr(transcript, "segments", []) or []:
        segments.append({
            "start": getattr(segment, "start", 0),
            "end": getattr(segment, "end", 0),
            "text": getattr(segment, "text", "").strip(),
        })

    return {
        "provider": "openai",
        "model": kwargs["model"],
        "language": getattr(transcript, "language", language or "unknown"),
        "duration": getattr(transcript, "duration", None),
        "text": getattr(transcript, "text", ""),
        "segments": segments,
    }


def transcribe_with_local(media_path: Path, language: str | None, model_size: str) -> dict:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments_iter, info = model.transcribe(str(media_path), language=language, word_timestamps=False)
    segments = []
    text_parts = []
    for segment in segments_iter:
        text = segment.text.strip()
        text_parts.append(text)
        segments.append({"start": segment.start, "end": segment.end, "text": text})

    return {
        "provider": "local",
        "model": model_size,
        "language": info.language,
        "duration": info.duration,
        "text": " ".join(text_parts),
        "segments": segments,
    }


def write_outputs(result: dict, source: str, output_name: str | None) -> tuple[Path, Path]:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    base = output_name or slugify(Path(source).stem if not is_url(source) else urlparse(source).netloc)
    json_path = OUTPUTS_DIR / f"{base}.transcricao.json"
    md_path = OUTPUTS_DIR / f"{base}.transcricao.md"

    payload = {
        "source": source,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        **result,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Transcricao - {base}",
        "",
        f"Fonte: {source}",
        f"Provider: {payload.get('provider')}",
        f"Idioma: {payload.get('language')}",
        "",
        "## Texto",
        "",
        payload.get("text", "").strip(),
        "",
        "## Segmentos",
        "",
    ]
    for segment in payload.get("segments", []) or []:
        start = float(segment.get("start") or 0)
        end = float(segment.get("end") or 0)
        text = str(segment.get("text") or "").strip()
        lines.append(f"- [{start:.1f}s - {end:.1f}s] {text}")
    md_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcreve link, video ou audio para JSON e Markdown.")
    parser.add_argument("source", help="Link publico, arquivo de video ou arquivo de audio.")
    parser.add_argument("--language", default="pt", help="Idioma esperado. Use 'auto' para detectar automaticamente.")
    parser.add_argument("--model", default="base", help="Modelo local do faster-whisper: tiny, base, small, medium, large-v3.")
    parser.add_argument("--output-name", default=None, help="Nome base dos arquivos de saida.")
    args = parser.parse_args()

    language = None if args.language == "auto" else args.language
    source = args.source.strip()
    temp_dir = tempfile.TemporaryDirectory()
    try:
        if is_url(source):
            media_path = run_ytdlp(source)
        else:
            media_path = Path(source)
            if not media_path.exists():
                raise FileNotFoundError(f"Arquivo nao encontrado: {source}")

        if os.getenv("OPENAI_API_KEY"):
            result = transcribe_with_openai(media_path, language)
        else:
            result = transcribe_with_local(media_path, language, args.model)

        json_path, md_path = write_outputs(result, source, args.output_name)
        print(f"Transcricao JSON salva em: {json_path}")
        print(f"Transcricao Markdown salva em: {md_path}")
        return 0
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    finally:
        temp_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

