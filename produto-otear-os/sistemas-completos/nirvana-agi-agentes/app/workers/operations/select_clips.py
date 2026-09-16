"""
Select Clips Operation
Seleciona clipes virais a partir de uma transcricao usando cascata de LLMs:
Claude Sonnet -> GPT-4.1-mini -> Gemini 2.5 Flash -> Groq Llama-3.3-70b.

Input:
  - input_path: video file (so o caminho e propagado, nao usado para inferencia)
  - params:
      transcript_path: caminho do JSON com {duration, segments:[{start,end,text}], source?}
      max_clips (default 5)
      min_duration (default 30)
      max_duration (default 75)
      language (default "pt-BR")

Output:
  - output_path (.json): {source, clips: [{title, start, end, hook, reason}]}
  - sidecar .review.md ao lado do output_path
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List, Optional
import json
import os
import re
import shutil


ANTHROPIC_MODEL = os.getenv("SELECT_CLIPS_ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPENAI_MODEL = os.getenv("SELECT_CLIPS_OPENAI_MODEL", "gpt-4.1-mini")
GEMINI_MODEL = os.getenv("SELECT_CLIPS_GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.getenv("SELECT_CLIPS_GROQ_MODEL", "llama-3.3-70b-versatile")
MIN_CLIP_DURATION_SECONDS = 30.0


PROMPT_TEMPLATE = """Voce e um editor especialista em shorts virais (TikTok, Reels, YouTube Shorts).

Analise a transcricao numerada abaixo e identifique entre 1 e {max} trechos com MAIOR potencial viral.

CRITERIOS DE SELECAO:
1. Hook forte nos primeiros 3 segundos (frase que para o scroll)
2. Arco narrativo completo em 45-60s (setup -> insight -> payoff)
3. Contrarian takes, dados concretos, historias pessoais fortes
4. Auto-contido (entende sem contexto externo)
5. Momento "aha" claro

REGRAS:
- Cada segmento dura ~5s em media; um clipe bom tem 6-15 segmentos contiguos
- Duracao desejada (end-start): {min_dur}-{max_dur} segundos
- Se so 1 trecho e realmente viral, retorne apenas 1
- Nao complete quantidade com clipes fracos; qualidade > volume
- start_segment e end_segment sao NUMEROS INTEIROS (indices da lista)
- hook = copie literalmente o texto do start_segment
- title = 3-5 palavras descritivas
- reason = 1 frase explicando por que funciona como short

TRANSCRICAO (cada linha: #<indice> [<duracao>s] <texto>):
{transcript}

Duracao total do video: {total_duration:.0f} segundos
Total de segmentos: {total_segments}

RETORNE APENAS JSON VALIDO, sem texto adicional:
```json
{{
  "clips": [
    {{
      "start_segment": 42,
      "end_segment": 55,
      "title": "Titulo curto",
      "hook": "Primeira frase literal copiada do segmento 42",
      "reason": "Por que funciona como short"
    }}
  ]
}}
```"""


class SelectClipsOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        # transcript_path eh opcional: quando ausente, resolvemos via input_path + ".json"
        # (sidecar produzido por TranscribeOperation) em execute()
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        max_clips = int(params.get("max_clips", 5))
        min_duration = max(float(params.get("min_duration", MIN_CLIP_DURATION_SECONDS)), MIN_CLIP_DURATION_SECONDS)
        max_duration = float(params.get("max_duration", 75))

        transcript_path = params.get("transcript_path") or _resolve_transcript_path(input_path)
        if not transcript_path or not os.path.exists(transcript_path):
            raise ValueError(
                f"select_clips: transcript JSON not found "
                f"(tried params.transcript_path and {input_path}.json). "
                "Run a 'transcribe' step before 'select_clips'."
            )

        with open(transcript_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        duration = float(data.get("duration", 0))
        source = data.get("source") or input_path
        segments = data.get("segments", [])
        transcript_text = _format_transcript(data)

        prompt = PROMPT_TEMPLATE.format(
            max=max_clips,
            min_dur=min_duration,
            max_dur=max_duration,
            transcript=transcript_text,
            total_duration=duration,
            total_segments=len(segments),
        )

        text = _call_llm_cascade(prompt)
        if text is None:
            print("[SelectClips] no LLM backend available; writing empty clips")
            _write_outputs(input_path, output_path, source, [], transcript_path)
            return

        try:
            parsed = _extract_json(text)
            raw_clips = parsed.get("clips", [])
        except Exception as e:
            print(f"[SelectClips] failed to parse LLM response: {e}")
            print(f"[SelectClips] raw response (first 500 chars): {text[:500]}")
            _write_outputs(input_path, output_path, source, [], transcript_path)
            return

        valid = _validate_clips(raw_clips, segments, min_duration, max_duration)
        _write_outputs(input_path, output_path, source, valid, transcript_path)
        print(f"[SelectClips] {len(valid)} clip(s) saved to {output_path}")


def _resolve_transcript_path(input_path: str) -> Optional[str]:
    """TranscribeOperation salva sidecar como output_path + '.json'. No pipeline,
    output da etapa anterior vira input da proxima — entao tentamos input + '.json'."""
    candidate = input_path + ".json"
    if os.path.exists(candidate):
        return candidate
    base, _ext = os.path.splitext(input_path)
    candidate2 = base + ".json"
    if os.path.exists(candidate2):
        return candidate2
    return None


def _format_transcript(data: dict) -> str:
    segs = data.get("segments", [])
    if not segs:
        return data.get("text", "")
    lines = []
    for i, s in enumerate(segs):
        dur = float(s.get("end", 0)) - float(s.get("start", 0))
        lines.append(f"#{i} [{dur:.1f}s] {str(s.get('text', '')).strip()}")
    return "\n".join(lines)


def _clean_leading_zeros(s: str) -> str:
    return re.sub(r"(?<=[:\s,\[])0+(\d+\.)", r"\1", s)


def _extract_json(text: str) -> dict:
    candidate: Optional[str] = None
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        candidate = m.group(1)
    else:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            candidate = m.group(0)
    if candidate is None:
        raise ValueError("no JSON in response")
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return json.loads(_clean_leading_zeros(candidate))


def _validate_clips(
    raw_clips: List[Dict[str, Any]],
    segments: List[Dict[str, Any]],
    min_duration: float,
    max_duration: float,
) -> List[Dict[str, Any]]:
    valid = []
    n_segs = len(segments)
    for c in raw_clips:
        try:
            start_seg = int(c.get("start_segment", -1))
            end_seg = int(c.get("end_segment", -1))
        except (TypeError, ValueError):
            continue
        if start_seg < 0 or end_seg < 0 or end_seg <= start_seg:
            continue
        if start_seg >= n_segs or end_seg >= n_segs:
            print(
                f"[SelectClips] skip out-of-range #{start_seg}-#{end_seg} (max {n_segs - 1})"
            )
            continue
        start = float(segments[start_seg].get("start", 0))
        end = float(segments[end_seg].get("end", 0))
        dur = end - start
        if dur < min_duration or dur > max_duration:
            print(
                f"[SelectClips] skip dur {dur:.1f}s outside "
                f"[{min_duration}-{max_duration}] (#{start_seg}-#{end_seg})"
            )
            continue
        valid.append({
            "title": c.get("title", f"Clip {len(valid) + 1}"),
            "start": round(start, 2),
            "end": round(end, 2),
            "hook": c.get("hook", ""),
            "reason": c.get("reason", ""),
        })
    return valid


def _write_outputs(
    input_path: str,
    output_path: str,
    source: str,
    clips: List[Dict[str, Any]],
    transcript_path: Optional[str] = None,
) -> None:
    payload = {"source": source, "clips": clips}
    # Sempre escreve o JSON em output_path (worker trata como output JSON do job).
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    # Sidecar legivel para review humano.
    review_path = output_path + ".review.md"
    _write_review_md(review_path, clips, source)
    # Compatibilidade: se proximo step esperar um sidecar .json sobre o video,
    # tambem grava no padrao usado pelo TranscribeOperation.
    sidecar = output_path + ".clips.json"
    with open(sidecar, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    # Propaga a transcricao para etapas seguintes (ex.: eval_cuts), ja que o
    # pipeline troca o input para o JSON de clipes produzido aqui.
    if transcript_path and os.path.exists(transcript_path):
        shutil.copy2(transcript_path, output_path + ".transcript.json")


def _write_review_md(path: str, clips: List[Dict[str, Any]], source: str) -> None:
    lines = ["# Clipes sugeridos pela IA", ""]
    if source:
        lines += [f"Source: {source}", ""]
    if not clips:
        lines += ["_Nenhum clipe sugerido — edite manualmente no painel._", ""]
    for i, c in enumerate(clips, 1):
        dur = c["end"] - c["start"]
        mm_s, ss_s = int(c["start"] // 60), int(c["start"] % 60)
        mm_e, ss_e = int(c["end"] // 60), int(c["end"] % 60)
        lines += [
            f"## {i}. {c.get('title', '')}  ({dur:.1f}s)",
            f"**[{mm_s:02d}:{ss_s:02d} -> {mm_e:02d}:{ss_e:02d}]**",
            "",
            f"**Hook:** {c.get('hook', '')}",
            "",
            c.get("reason", ""),
            "",
        ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _openrouter_headers() -> dict:
    headers = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("PUBLIC_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME", "O Tear")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_name:
        headers["X-Title"] = app_name
    return headers


def _try_openrouter(prompt: str) -> Optional[str]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        model = os.getenv("SELECT_CLIPS_OPENROUTER_MODEL", os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"))
        client = OpenAI(
            api_key=key,
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            default_headers=_openrouter_headers() or None,
        )
        print(f"[SelectClips] -> OpenRouter ({model})")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[SelectClips] OpenRouter failed: {e}")
        return None


def _try_anthropic(prompt: str) -> Optional[str]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=key)
        print(f"[SelectClips] -> Claude ({ANTHROPIC_MODEL})")
        resp = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    except Exception as e:
        print(f"[SelectClips] Anthropic failed: {e}")
        return None


def _try_openai(prompt: str) -> Optional[str]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        print(f"[SelectClips] -> OpenAI ({OPENAI_MODEL})")
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[SelectClips] OpenAI failed: {e}")
        return None


def _try_gemini(prompt: str) -> Optional[str]:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        print(f"[SelectClips] -> Gemini ({GEMINI_MODEL})")
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        print(f"[SelectClips] Gemini failed: {e}")
        return None


def _try_groq(prompt: str) -> Optional[str]:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=key)
        print(f"[SelectClips] -> Groq ({GROQ_MODEL})")
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[SelectClips] Groq failed: {e}")
        return None


def _call_llm_cascade(prompt: str) -> Optional[str]:
    for provider in (_try_openrouter, _try_anthropic, _try_openai, _try_gemini, _try_groq):
        text = provider(prompt)
        if text:
            return text
    return None
