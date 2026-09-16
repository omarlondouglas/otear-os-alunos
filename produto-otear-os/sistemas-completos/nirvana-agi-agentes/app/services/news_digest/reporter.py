"""
Reporter — gera HTML do digest + lista de content ideas via LLM cascade.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from app.services.llm_cascade import call_llm
from app.services.news_digest.analyzer import _extract_json

logger = logging.getLogger(__name__)


def generate_content_ideas(digest: Dict[str, Any], niche: str, num: int = 5) -> List[Dict[str, Any]]:
    """A partir dos dados agregados, gera N ideias de conteudo virais."""
    payload = {
        "youtube": digest.get("youtube", [])[:5],
        "reddit": digest.get("reddit", [])[:5],
        "twitter_top": (digest.get("twitter") or {}).get("top_tweets", [])[:5],
        "twitter_trends": (digest.get("twitter") or {}).get("trending_topics", []),
        "perplexity": digest.get("perplexity", []),
    }
    prompt = f"""Voce eh estrategista de conteudo viral. Analise os dados abaixo (nicho: {niche})
e gere {num} ideias de conteudo de alto potencial. Use principios de contraste/curiosidade.

Dados:
{json.dumps(payload, ensure_ascii=False)[:8000]}

Devolva APENAS array JSON:
[
  {{
    "title": "Titulo curto que gera curiosidade",
    "hook": "Hook (1-2 frases) com contraste claro",
    "format": "reels | carrossel | youtube short | post longo",
    "audience": "Avatar especifico (1 frase)",
    "why": "Por que isso bate (1 frase, baseado nos dados)"
  }}
]
Em portugues.
"""
    raw = call_llm(prompt, max_tokens=2500)
    parsed = _extract_json(raw or "")
    return parsed if isinstance(parsed, list) else []


def render_html(digest: Dict[str, Any], niche: str, ideas: List[Dict[str, Any]]) -> str:
    """Renderiza HTML completo do digest pra email/preview."""
    yt = digest.get("youtube", [])[:3]
    rd = digest.get("reddit", [])[:3]
    tw = digest.get("twitter") or {}
    px = digest.get("perplexity", [])[:3]

    def _esc(s: str) -> str:
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    parts = [
        '<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:680px;margin:0 auto;color:#222;">',
        '<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:28px;border-radius:12px;text-align:center;margin-bottom:24px;">',
        f'<h1 style="margin:0;font-size:24px;">Radar do dia — {_esc(niche)}</h1>',
        '<p style="margin:6px 0 0;font-size:13px;opacity:.85;">Tendencias coletadas de YouTube, Reddit, X e Perplexity</p>',
        '</div>',
    ]

    if yt:
        parts.append('<h2 style="border-left:4px solid #FF0000;padding-left:10px;">YouTube</h2>')
        for v in yt:
            parts.append(
                f'<div style="background:#fff;padding:14px;border-radius:8px;margin-bottom:12px;border-left:3px solid #FF0000;box-shadow:0 1px 4px rgba(0,0,0,.08);">'
                f'<a href="{_esc(v.get("link",""))}" style="color:#1a1a1a;font-weight:600;text-decoration:none;">{_esc(v.get("title",""))}</a>'
                f'<p style="color:#555;margin:8px 0 0;font-size:14px;">{_esc(v.get("quick_summary",""))}</p>'
                f'<details style="margin-top:8px;"><summary style="cursor:pointer;color:#0066cc;font-size:13px;">Deep dive</summary>'
                f'<div style="background:#f8f9fa;padding:10px;border-left:3px solid #3498db;margin-top:6px;font-size:13px;line-height:1.6;color:#444;">{_esc(v.get("deep_dive","")).replace(chr(10), "<br/>")}</div>'
                f'</details></div>'
            )

    if rd:
        parts.append('<h2 style="border-left:4px solid #FF4500;padding-left:10px;">Reddit</h2>')
        for r in rd:
            parts.append(
                f'<div style="background:#fff;padding:14px;border-radius:8px;margin-bottom:12px;border-left:3px solid #FF4500;box-shadow:0 1px 4px rgba(0,0,0,.08);">'
                f'<a href="{_esc(r.get("link",""))}" style="color:#1a1a1a;font-weight:600;text-decoration:none;">{_esc(r.get("title",""))}</a>'
                f'<p style="color:#555;margin:8px 0 0;font-size:14px;">{_esc(r.get("summary",""))}</p>'
                f'</div>'
            )

    if tw.get("top_tweets"):
        parts.append('<h2 style="border-left:4px solid #1DA1F2;padding-left:10px;">X (Twitter)</h2>')
        for t in tw["top_tweets"][:3]:
            parts.append(
                f'<div style="background:#f7f9fb;padding:14px;border-radius:8px;margin-bottom:10px;border-left:3px solid #1DA1F2;">'
                f'<div style="display:flex;justify-content:space-between;font-size:12px;color:#666;">'
                f'<a href="{_esc(t.get("url",""))}" style="color:#1DA1F2;">{_esc(t.get("user") or "Tweet")}</a>'
                f'<span>♥ {t.get("likes",0)}</span></div>'
                f'<p style="margin:8px 0 0;font-size:14px;color:#222;">{_esc(t.get("text",""))}</p></div>'
            )
        if tw.get("trending_topics"):
            parts.append('<h3 style="margin-top:14px;color:#1DA1F2;">Trending topics</h3>')
            for tp in tw["trending_topics"]:
                parts.append(
                    f'<div style="background:#fff;padding:10px;border-radius:6px;margin-bottom:8px;font-size:13px;">'
                    f'<strong>{_esc(tp.get("title",""))}</strong> — <span style="color:#555;">{_esc(tp.get("description",""))}</span></div>'
                )

    if px:
        parts.append('<h2 style="border-left:4px solid #20808d;padding-left:10px;">Perplexity</h2>')
        for n in px:
            parts.append(
                f'<div style="background:#fff;padding:14px;border-radius:8px;margin-bottom:10px;border-left:3px solid #20808d;">'
                f'<h4 style="margin:0 0 6px;">{_esc(n.get("headline",""))}</h4>'
                f'<p style="margin:0;color:#555;font-size:14px;">{_esc(n.get("content",""))}</p></div>'
            )

    if ideas:
        parts.append('<h2 style="border-left:4px solid #11998e;padding-left:10px;">Ideias de conteudo pra hoje</h2>')
        parts.append('<ol style="padding-left:18px;">')
        for idea in ideas:
            parts.append(
                f'<li style="margin-bottom:10px;font-size:14px;">'
                f'<strong>{_esc(idea.get("title",""))}</strong> '
                f'<span style="color:#666;">[{_esc(idea.get("format",""))}]</span><br/>'
                f'<span style="color:#444;">{_esc(idea.get("hook",""))}</span><br/>'
                f'<small style="color:#888;">→ {_esc(idea.get("audience",""))} · {_esc(idea.get("why",""))}</small>'
                f'</li>'
            )
        parts.append('</ol>')

    parts.append('</div>')
    return "".join(parts)
