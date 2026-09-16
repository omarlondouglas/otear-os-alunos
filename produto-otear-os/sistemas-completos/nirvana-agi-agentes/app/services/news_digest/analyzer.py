"""
Analyzer — pega dados crus dos scrapers e devolve resumos estruturados.

Reaproveita o pattern dos chainLlm + structured_output_parser do n8n original
(via prompts que pedem JSON), mas roda na cascata Anthropic->OpenAI->Gemini->Groq.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.services.llm_cascade import call_llm

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> Any:
    """Extrai JSON de texto que pode ter ```json wrapping ou prefixo."""
    if not text:
        return None
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        # tenta achar o primeiro { ou [
        m = re.search(r"[\[{].*[\]}]", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return None


def analyze_youtube_video(video: Dict[str, Any]) -> Dict[str, Any]:
    """Resume um video do YouTube em quick + deep dive (PT-BR)."""
    transcript = video.get("transcript") or video.get("description") or ""
    if not transcript.strip():
        return {
            "title": video["title"],
            "link": video["url"],
            "quick_summary": video.get("description", "")[:200],
            "deep_dive": "",
        }

    prompt = f"""Voce eh analista de conteudo. Resuma este video do YouTube.

Antes de processar, corrija erros comuns de transcricao:
- "NA10", "NADN", "nadn", "NA-10", "na10" -> "n8n"

Video: {video["title"]}
Canal: {video.get("channel", "")}
Link: {video["url"]}

Transcript (truncado):
{transcript[:6000]}

Devolva APENAS JSON nesta forma:
{{
  "title": "...",
  "link": "{video["url"]}",
  "quick_summary": "2-3 frases capturando a tese central. Em portugues.",
  "deep_dive": "3-5 bullets (use • no inicio) com 1-2 frases de explicacao cada. Em portugues."
}}
"""
    raw = call_llm(prompt, max_tokens=1500)
    parsed = _extract_json(raw or "") or {}
    return {
        "title": parsed.get("title") or video["title"],
        "link": parsed.get("link") or video["url"],
        "quick_summary": parsed.get("quick_summary", ""),
        "deep_dive": parsed.get("deep_dive", ""),
        "thumbnail": video.get("thumbnail"),
        "channel": video.get("channel"),
        "views": video.get("views", 0),
    }


def analyze_reddit_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Para cada post, devolve {title, link, summary} resumido em PT-BR."""
    if not posts:
        return []
    payload = [
        {"title": p["title"], "selftext": p.get("selftext", "")[:800], "url": p["url"]}
        for p in posts[:10]
    ]
    prompt = f"""Voce eh analista. Para cada post Reddit abaixo, devolva titulo + URL + resumo de 1 frase EM PORTUGUES.

Posts:
{json.dumps(payload, ensure_ascii=False)}

Devolva APENAS array JSON:
[
  {{"title": "...", "link": "...", "summary": "..."}}
]
"""
    raw = call_llm(prompt, max_tokens=2000)
    parsed = _extract_json(raw or "")
    if isinstance(parsed, list):
        return parsed
    # fallback sem LLM
    return [{"title": p["title"], "link": p["url"], "summary": p.get("selftext", "")[:200]} for p in posts[:5]]


def analyze_twitter(tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Devolve top_tweets + trending_topics."""
    if not tweets:
        return {"top_tweets": [], "trending_topics": []}
    payload = [
        {"text": t["text"][:500], "url": t["url"], "user": t.get("user"), "likes": t.get("likes", 0)}
        for t in tweets[:50]
    ]
    prompt = f"""Voce eh analista social. Analise estes tweets e devolva:
1. Os 5 tweets mais engajados (criterio: likes desc).
2. 3-5 trending topics recorrentes.

Tweets:
{json.dumps(payload, ensure_ascii=False)}

Devolva APENAS JSON em portugues:
{{
  "top_tweets": [
    {{"rank": 1, "text": "...", "url": "...", "user": "...", "likes": 0}}
  ],
  "trending_topics": [
    {{"rank": 1, "title": "...", "description": "1 frase de contexto"}}
  ]
}}
"""
    raw = call_llm(prompt, max_tokens=2000)
    parsed = _extract_json(raw or "") or {}
    return {
        "top_tweets": parsed.get("top_tweets", []),
        "trending_topics": parsed.get("trending_topics", []),
    }


def analyze_perplexity(text: str, top_n: int = 3) -> List[Dict[str, str]]:
    """Estrutura resposta do Perplexity em [{headline, content}]."""
    if not text.strip():
        return []
    prompt = f"""Extraia exatamente {top_n} noticias do texto abaixo. Devolva APENAS array JSON:
[
  {{"headline": "...", "content": "..."}}
]

Remova marcadores [1], [2]. Em portugues.

Texto:
{text}
"""
    raw = call_llm(prompt, max_tokens=2000)
    parsed = _extract_json(raw or "")
    if isinstance(parsed, list):
        return parsed
    return [{"headline": "Resumo Perplexity", "content": text[:500]}]
