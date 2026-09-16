"""
Analyze Profile Operation

Analisa um vídeo/transcrição de um criador/perfil para extrair linguagem,
posicionamento, estrutura de roteiro e recomendações de conteúdo.

Uso típico no pipeline:
  transcribe -> analyze_profile

Input:
  - input_path: caminho do vídeo passthrough ou output da etapa anterior
  - params:
      transcript_path: opcional; se ausente, procura sidecar .json
      profile_name: opcional
      platform: instagram|tiktok|youtube|unknown
      niche: opcional
      objective: opcional (ex.: melhorar roteiro, analisar perfil, criar conteúdo)
      output_language: default pt-BR

Output:
  - output_path: JSON com análise estruturada
  - output_path + ".review.md": relatório legível
  - output_path + ".transcript.json": cópia da transcrição para auditoria
"""

from __future__ import annotations

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, Optional
import json
import os
import re
import shutil


OPENROUTER_MODEL = os.getenv("PROFILE_ANALYSIS_OPENROUTER_MODEL", os.getenv("OPENROUTER_MODEL_SMART", os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")))
OPENAI_MODEL = os.getenv("PROFILE_ANALYSIS_OPENAI_MODEL", "gpt-4.1-mini")
GEMINI_MODEL = os.getenv("PROFILE_ANALYSIS_GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.getenv("PROFILE_ANALYSIS_GROQ_MODEL", "llama-3.3-70b-versatile")


PROMPT_TEMPLATE = """Você é um estrategista de conteúdo de vídeo curto para a Agência Sem Esforço.

Analise a transcrição de um vídeo/perfil e extraia um diagnóstico prático para melhorar roteiros e criação de conteúdo.

CONTEXTO:
- Perfil/nome: {profile_name}
- Plataforma: {platform}
- Nicho: {niche}
- Objetivo: {objective}
- Idioma de saída: {output_language}

TRANSCRIÇÃO:
{transcript}

RETORNE APENAS JSON VÁLIDO, sem markdown, neste schema:
{{
  "profile_summary": "resumo do posicionamento percebido",
  "content_pillars": ["pilar 1", "pilar 2", "pilar 3"],
  "voice_and_tone": {{
    "tone": "tom dominante",
    "pace": "ritmo percebido",
    "signature_phrases": ["frase/padrão se houver"],
    "audience_relationship": "como fala com a audiência"
  }},
  "script_patterns": {{
    "hook_patterns": ["padrão de hook 1", "padrão 2"],
    "development_structure": "como desenvolve a ideia",
    "proof_style": "como usa prova, exemplo, autoridade ou história",
    "cta_style": "como chama para ação ou fecha"
  }},
  "visual_content_notes": ["observações que podem orientar edição/visual"],
  "strengths": ["força 1", "força 2"],
  "weaknesses": ["ponto a melhorar 1", "ponto a melhorar 2"],
  "opportunities": ["oportunidade 1", "oportunidade 2"],
  "recommended_video_formats": [
    {{"format": "nome do formato", "when_to_use": "quando usar", "example_hook": "exemplo de hook"}}
  ],
  "script_improvements": ["melhoria prática 1", "melhoria prática 2"],
  "next_scripts": [
    {{"title": "ideia de vídeo", "hook": "hook", "structure": "estrutura em 3-5 passos"}}
  ]
}}

REGRAS:
- Não invente dados fora da transcrição.
- Se a transcrição for curta, sinalize baixa confiança nas recomendações.
- Foque em roteiro, retenção, clareza, posicionamento e criação de conteúdo.
- Entregue recomendações acionáveis, não elogios genéricos.
"""


class AnalyzeProfileOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        transcript_path = params.get("transcript_path") or _resolve_transcript_path(input_path)
        if not transcript_path or not os.path.exists(transcript_path):
            raise ValueError(
                "analyze_profile: transcript JSON not found. "
                "Run a 'transcribe' step before 'analyze_profile' or pass params.transcript_path."
            )

        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)

        profile_name = params.get("profile_name") or params.get("handle") or "perfil analisado"
        platform = params.get("platform", "unknown")
        niche = params.get("niche", "não informado")
        objective = params.get("objective", "análise de perfil e melhoria de roteiro")
        output_language = params.get("output_language", "pt-BR")

        transcript_text = _format_transcript(transcript_data, max_chars=int(params.get("max_chars", 24000)))
        prompt = PROMPT_TEMPLATE.format(
            profile_name=profile_name,
            platform=platform,
            niche=niche,
            objective=objective,
            output_language=output_language,
            transcript=transcript_text,
        )

        llm_text = _call_llm_cascade(prompt)
        if llm_text:
            try:
                analysis = _extract_json(llm_text)
            except Exception as exc:
                print(f"[AnalyzeProfile] failed to parse LLM response: {exc}")
                analysis = _fallback_analysis(transcript_data, profile_name, platform, niche, objective)
        else:
            print("[AnalyzeProfile] no LLM backend available; writing heuristic analysis")
            analysis = _fallback_analysis(transcript_data, profile_name, platform, niche, objective)

        analysis["metadata"] = {
            "profile_name": profile_name,
            "platform": platform,
            "niche": niche,
            "objective": objective,
            "transcript_path": transcript_path,
            "duration": transcript_data.get("duration"),
            "language": transcript_data.get("language"),
            "provider": transcript_data.get("provider"),
            "confidence_note": _confidence_note(transcript_data),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        _write_review_md(output_path + ".review.md", analysis)
        shutil.copy2(transcript_path, output_path + ".transcript.json")
        print(f"[AnalyzeProfile] analysis saved to {output_path}")


def _resolve_transcript_path(input_path: str) -> Optional[str]:
    candidates = [
        input_path + ".json",
        os.path.splitext(input_path)[0] + ".json",
        input_path + ".transcript.json",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def _format_transcript(data: dict, max_chars: int = 24000) -> str:
    segments = data.get("segments") or []
    if segments:
        lines = []
        for i, s in enumerate(segments):
            start = float(s.get("start", 0))
            end = float(s.get("end", 0))
            text = str(s.get("text", "")).strip()
            lines.append(f"#{i} [{start:.1f}-{end:.1f}] {text}")
        out = "\n".join(lines)
    else:
        out = str(data.get("text", ""))
    if len(out) > max_chars:
        return out[:max_chars] + "\n\n[TRANSCRIÇÃO TRUNCADA PARA ANÁLISE]"
    return out


def _confidence_note(data: dict) -> str:
    text = data.get("text", "") or ""
    duration = float(data.get("duration", 0) or 0)
    if duration < 20 or len(text) < 300:
        return "baixa: transcrição curta; use como sinal inicial, não diagnóstico definitivo"
    if duration < 60:
        return "média: bom para analisar roteiro curto, limitado para concluir padrão de perfil completo"
    return "boa: transcrição suficiente para inferir padrões de roteiro e conteúdo"


def _fallback_analysis(data: dict, profile_name: str, platform: str, niche: str, objective: str) -> Dict[str, Any]:
    text = data.get("text", "") or ""
    words = re.findall(r"\w+", text.lower())
    common = _top_terms(words)
    return {
        "profile_summary": f"Análise heurística de {profile_name}. A transcrição permite extrair temas recorrentes, mas nenhum provedor LLM estava disponível para análise profunda.",
        "content_pillars": common[:5] or ["tema principal não identificado"],
        "voice_and_tone": {
            "tone": "não inferido com alta confiança",
            "pace": "avaliar pelo vídeo original",
            "signature_phrases": [],
            "audience_relationship": "não inferido com alta confiança",
        },
        "script_patterns": {
            "hook_patterns": [],
            "development_structure": "estrutura não inferida sem análise LLM; revisar segmentos manualmente",
            "proof_style": "não identificado",
            "cta_style": "não identificado",
        },
        "visual_content_notes": ["Gerar filmstrip/frames para complementar a análise visual se necessário."],
        "strengths": ["Há transcrição disponível para auditoria e reaproveitamento."],
        "weaknesses": ["Análise profunda depende de provedor LLM configurado."],
        "opportunities": ["Usar os termos recorrentes para criar novas pautas e testar hooks."],
        "recommended_video_formats": [
            {"format": "roteiro 45-60s", "when_to_use": "quando houver uma ideia central clara", "example_hook": "O erro que quase todo mundo comete em [tema]"}
        ],
        "script_improvements": ["Abrir com uma contradição forte nos 3 primeiros segundos.", "Fechar com CTA específico, não genérico."],
        "next_scripts": [],
    }


def _top_terms(words: list[str]) -> list[str]:
    stop = {"que", "para", "com", "uma", "por", "dos", "das", "não", "sim", "você", "isso", "esse", "essa", "mais", "como", "vai", "tem", "seu", "sua", "ele", "ela", "pra", "porque", "então", "aqui", "muito", "quando", "sobre"}
    freq: Dict[str, int] = {}
    for w in words:
        if len(w) < 4 or w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:10]]


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
    return json.loads(candidate)


def _openrouter_headers() -> dict:
    headers = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("PUBLIC_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME", "O Tear")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_name:
        headers["X-Title"] = app_name
    return headers


def _call_llm_cascade(prompt: str) -> Optional[str]:
    for provider in (_try_openrouter, _try_openai, _try_gemini, _try_groq):
        text = provider(prompt)
        if text:
            return text
    return None


def _try_openrouter(prompt: str) -> Optional[str]:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key, base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), default_headers=_openrouter_headers() or None)
        resp = client.chat.completions.create(model=OPENROUTER_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=2500)
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[AnalyzeProfile] OpenRouter failed: {e}")
        return None


def _try_openai(prompt: str) -> Optional[str]:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(model=OPENAI_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=2500)
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[AnalyzeProfile] OpenAI failed: {e}")
        return None


def _try_gemini(prompt: str) -> Optional[str]:
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        print(f"[AnalyzeProfile] Gemini failed: {e}")
        return None


def _try_groq(prompt: str) -> Optional[str]:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=key)
        resp = client.chat.completions.create(model=GROQ_MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=2500)
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[AnalyzeProfile] Groq failed: {e}")
        return None


def _write_review_md(path: str, analysis: Dict[str, Any]) -> None:
    meta = analysis.get("metadata", {})
    lines = [
        "# Análise de perfil em vídeo",
        "",
        f"**Perfil:** {meta.get('profile_name', '')}",
        f"**Plataforma:** {meta.get('platform', '')}",
        f"**Nicho:** {meta.get('niche', '')}",
        f"**Confiança:** {meta.get('confidence_note', '')}",
        "",
        "## Resumo",
        analysis.get("profile_summary", ""),
        "",
        "## Pilares de conteúdo",
    ]
    for item in analysis.get("content_pillars", []):
        lines.append(f"- {item}")

    lines += ["", "## Padrões de roteiro"]
    patterns = analysis.get("script_patterns", {})
    if patterns.get("hook_patterns"):
        lines.append("**Hooks:**")
        for h in patterns.get("hook_patterns", []):
            lines.append(f"- {h}")
    for key in ("development_structure", "proof_style", "cta_style"):
        if patterns.get(key):
            lines.append(f"- **{key}:** {patterns[key]}")

    for title, key in [
        ("Forças", "strengths"),
        ("Pontos a melhorar", "weaknesses"),
        ("Oportunidades", "opportunities"),
        ("Melhorias de roteiro", "script_improvements"),
    ]:
        lines += ["", f"## {title}"]
        for item in analysis.get(key, []):
            lines.append(f"- {item}")

    lines += ["", "## Próximos roteiros sugeridos"]
    for item in analysis.get("next_scripts", []):
        lines += [
            f"### {item.get('title', 'Ideia')}",
            f"**Hook:** {item.get('hook', '')}",
            f"**Estrutura:** {item.get('structure', '')}",
            "",
        ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")
