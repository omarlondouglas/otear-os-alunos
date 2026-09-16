"""
Digest service — orquestra os 4 scrapers em paralelo + analyzer + reporter.

Persiste resultado em content_assets (type='news_digest', metadata=payload).
Config (niche, subreddits, twitter_query) lida do vault USER.md secao
"news_radar" se existir, senao usa env defaults.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.news_digest.scrapers.youtube import fetch_youtube
from app.services.news_digest.scrapers.reddit import fetch_reddit
from app.services.news_digest.scrapers.twitter import fetch_twitter
from app.services.news_digest.scrapers.perplexity import fetch_perplexity_news
from app.services.news_digest.analyzer import (
    analyze_youtube_video,
    analyze_reddit_posts,
    analyze_twitter,
    analyze_perplexity,
)
from app.services.news_digest.reporter import generate_content_ideas, render_html

logger = logging.getLogger(__name__)


def _load_config_from_vault() -> Dict[str, Any]:
    """Le secao 'news_radar' do USER.md. Esquema esperado em YAML inline:

    § news_radar
    niche: AI agents
    youtube_query: ai agents
    subreddits: r/n8n, r/AI_Agents, r/LocalLLaMA
    twitter_query: ai agents OR n8n OR claude
    """
    try:
        from app.services.user_memory import get_user_profile
        doc = get_user_profile()
        body = doc.sections.get("news_radar", "")
        cfg: Dict[str, Any] = {}
        for line in body.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            k, v = line.split(":", 1)
            cfg[k.strip()] = v.strip()
        return cfg
    except Exception as e:
        logger.warning(f"[digest] vault config indisponivel: {e}")
        return {}


def _resolve_config(override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    vault = _load_config_from_vault()
    over = override or {}
    niche = over.get("niche") or vault.get("niche") or os.getenv("NEWS_DIGEST_NICHE", "AI agents")
    yt_query = over.get("youtube_query") or vault.get("youtube_query") or niche
    twitter_query = over.get("twitter_query") or vault.get("twitter_query") or niche
    subs_raw = over.get("subreddits") or vault.get("subreddits") or os.getenv("NEWS_DIGEST_SUBREDDITS", "n8n,AI_Agents,LocalLLaMA")
    if isinstance(subs_raw, str):
        subreddits = [s.strip().lstrip("r/") for s in subs_raw.split(",") if s.strip()]
    else:
        subreddits = list(subs_raw)
    return {
        "niche": niche,
        "youtube_query": yt_query,
        "twitter_query": twitter_query,
        "subreddits": subreddits,
    }


async def build_digest_async(override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Roda scrapers em paralelo, analisa e gera HTML + ideias. Retorna payload."""
    cfg = _resolve_config(override)
    logger.info(f"[digest] config: {cfg}")

    yt_task = fetch_youtube(cfg["youtube_query"], max_results=10)
    rd_task = fetch_reddit(cfg["subreddits"], category="rising", limit_per_sub=5)
    tw_task = fetch_twitter(cfg["twitter_query"], max_items=30)
    px_task = fetch_perplexity_news(cfg["niche"], top_n=3)

    yt_raw, rd_raw, tw_raw, px_raw = await asyncio.gather(
        yt_task, rd_task, tw_task, px_task,
        return_exceptions=True,
    )

    def _ok(x):
        if isinstance(x, Exception):
            logger.warning(f"[digest] scraper falhou: {x}")
            return None
        return x

    yt_raw = _ok(yt_raw) or []
    rd_raw = _ok(rd_raw) or []
    tw_raw = _ok(tw_raw) or []
    px_raw = _ok(px_raw) or ""

    logger.info(f"[digest] coletado: yt={len(yt_raw)} reddit={len(rd_raw)} tw={len(tw_raw)} px={len(px_raw)}chars")

    # analise (LLM-bound, roda sequencial pra nao explodir cascata)
    yt_analyzed = [await asyncio.to_thread(analyze_youtube_video, v) for v in yt_raw[:5]]
    rd_analyzed = await asyncio.to_thread(analyze_reddit_posts, rd_raw)
    tw_analyzed = await asyncio.to_thread(analyze_twitter, tw_raw)
    px_analyzed = await asyncio.to_thread(analyze_perplexity, px_raw, 3)

    digest = {
        "niche": cfg["niche"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "youtube": yt_analyzed,
        "reddit": rd_analyzed,
        "twitter": tw_analyzed,
        "perplexity": px_analyzed,
        "config": cfg,
    }
    digest["ideas"] = await asyncio.to_thread(generate_content_ideas, digest, cfg["niche"], 5)
    digest["html"] = render_html(digest, cfg["niche"], digest["ideas"])
    return digest


def run_digest(
    user_id: Optional[str] = None,
    override: Optional[Dict[str, Any]] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    """Versao sincrona (pra Celery). Persiste em content_assets se user_id."""
    digest = asyncio.run(build_digest_async(override))

    if persist and user_id:
        try:
            from app.api.v1.endpoints.library import save_asset
            saved = save_asset(
                user_id=user_id,
                asset_type="news_digest",
                title=f"Radar {digest['niche']} — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                metadata={
                    "niche": digest["niche"],
                    "config": digest["config"],
                    "youtube": digest["youtube"],
                    "reddit": digest["reddit"],
                    "twitter": digest["twitter"],
                    "perplexity": digest["perplexity"],
                    "ideas": digest["ideas"],
                    "html": digest["html"],
                    "generated_at": digest["generated_at"],
                },
            )
            digest["asset_id"] = saved.get("id")
            logger.info(f"[digest] salvo asset_id={digest.get('asset_id')}")
        except Exception as e:
            logger.error(f"[digest] persist falhou: {e}")

    return digest
