"""
Markdown Writer for Vault references/<handle>/

Escreve:
  - _profile.md      (analise agregada do criador)
  - _meta.json       (status da extracao para frontend)
  - <date>_<id>.md   (post individual: caption + original + transcript; sem analise local)
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from app.services.social.types import CreatorAnalysis, ExtractionMeta, PostScriptAnalysis, SocialPost

VAULT_PATH = Path(os.getenv("VAULT_PATH", "{OTEAR_VAULT_ROOT}"))
REFERENCES_DIR = Path(os.getenv("REFERENCES_PATH", str(VAULT_PATH / "references")))


def _safe_dirname(handle: str) -> str:
    h = handle.lstrip("@").lower()
    # Mantem apenas alfanumerico, hifen, underscore, ponto
    return "@" + "".join(c for c in h if c.isalnum() or c in "-_.")


def get_creator_dir(handle: str) -> Path:
    return REFERENCES_DIR / _safe_dirname(handle)


def write_meta(meta: ExtractionMeta) -> Path:
    """Salva _meta.json - frontend usa para mostrar progresso."""
    d = get_creator_dir(meta.handle)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "_meta.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(meta), f, ensure_ascii=False, indent=2)
    return path


def read_meta(handle: str) -> Optional[ExtractionMeta]:
    path = get_creator_dir(handle) / "_meta.json"
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ExtractionMeta(**data)
    except Exception:
        return None


def write_post(post: SocialPost, transcript: str, analysis: Optional[PostScriptAnalysis] = None) -> Path:
    """Salva post individual com frontmatter + caption + transcript + analise local."""
    d = get_creator_dir(post.handle)
    d.mkdir(parents=True, exist_ok=True)

    date_part = (post.posted_at or _today_iso())[:10]
    filename = f"{date_part}_{post.post_id}.md"
    path = d / filename

    fm_lines = [
        "---",
        f'platform: {post.platform}',
        f'handle: "{post.handle}"',
        f'post_id: "{post.post_id}"',
        f'url: "{post.url}"',
        f'duration: {post.duration}',
        f'posted_at: "{post.posted_at or ""}"',
        f'play_count: {post.play_count if post.play_count is not None else "null"}',
        f'like_count: {post.like_count if post.like_count is not None else "null"}',
        f'comment_count: {post.comment_count if post.comment_count is not None else "null"}',
        "---",
    ]

    body_lines = [
        "",
        f"# Post {post.post_id}",
        "",
        "## Caption",
        post.title or "_(sem caption)_",
        "",
        "## Original",
        f"[Ver original]({post.url})",
        "",
        "## Transcript",
        transcript or "_(transcricao indisponivel)_",
        "",
    ]

    if analysis:
        body_lines.extend([
            "## Analise do roteiro",
            "",
            "### Hook usado",
            analysis.hook_literal or "_(hook nao identificado)_",
            "",
            "### Tipo de hook",
            analysis.hook_type or "_(tipo nao identificado)_",
            "",
            "### Analise frase a frase",
            analysis.script_breakdown_markdown or "_(analise indisponivel)_",
            "",
            "### Padroes reutilizaveis",
            _bullet_list(analysis.reusable_patterns) or "_(nenhum padrao reutilizavel identificado)_",
            "",
        ])

    path.write_text("\n".join(fm_lines + body_lines), encoding="utf-8")
    return path


def write_profile(handle: str, platform: str, kind: str,
                  posts_analyzed: int, analysis: CreatorAnalysis) -> Path:
    """Salva _profile.md com a analise agregada (consultado pelos agentes)."""
    d = get_creator_dir(handle)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "_profile.md"

    now = datetime.now(timezone.utc).isoformat()

    fm = [
        "---",
        f'handle: "{handle}"',
        f'platform: {platform}',
        f'kind: {kind}',
        f'posts_analyzed: {posts_analyzed}',
        f'last_extraction: "{now}"',
        "---",
        "",
    ]

    body = [
        f"# Perfil: {handle}",
        "",
        "## Estilo",
        "",
        "### Hook patterns",
        _bullet_list(analysis.hook_patterns) or "_(nenhum padrao identificado)_",
        "",
        "### Estrutura narrativa",
        analysis.narrative_arc or "_(nao identificada)_",
        "",
        "### Vocabulario-chave",
        ", ".join(analysis.vocabulary) if analysis.vocabulary else "_(nao identificado)_",
        "",
        "### Gatilhos emocionais",
        ", ".join(analysis.emotional_triggers) if analysis.emotional_triggers else "_(nao identificados)_",
        "",
        "## Comunicacao",
        "",
        "### Tom",
        analysis.tone or "_(nao identificado)_",
        "",
        "### Ritmo",
        analysis.pacing or "_(nao identificado)_",
        "",
        "### Formato visual",
        analysis.visual_format or "_(nao identificado)_",
        "",
        "### CTA padrao",
        analysis.cta_style or "_(nao identificado)_",
        "",
        "## Resumo",
        analysis.summary or "_(sem resumo)_",
        "",
    ]

    path.write_text("\n".join(fm + body), encoding="utf-8")
    return path


def _bullet_list(items: List[str]) -> str:
    if not items:
        return ""
    return "\n".join(f"- {it}" for it in items)


def _today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def list_creators() -> List[Dict[str, object]]:
    """Lista todos os criadores no vault com seu status (consumido pelo frontend)."""
    if not REFERENCES_DIR.exists():
        return []
    out = []
    for entry in sorted(REFERENCES_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        meta = read_meta(entry.name)
        post_count = sum(
            1 for p in entry.glob("*.md") if not p.name.startswith("_")
        )
        out.append({
            "handle": entry.name,
            "kind": meta.kind if meta else "unknown",
            "platform": meta.platform if meta else "unknown",
            "status": meta.status if meta else "done",
            "posts_total": meta.posts_total if meta else post_count,
            "posts_done": meta.posts_done if meta else post_count,
            "last_extraction": meta.finished_at if meta else None,
        })
    return out
