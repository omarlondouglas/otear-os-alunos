"""
Reddit scraper — usa endpoint publico (sem credencial) por padrao;
se REDDIT_CLIENT_ID/SECRET configurados, usa OAuth via PRAW (mais rate limit).
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "agi-agentes-news-digest/1.0")


async def _fetch_public(subreddit: str, category: str, limit: int) -> List[Dict[str, Any]]:
    url = f"https://www.reddit.com/r/{subreddit}/{category}.json?limit={limit}"
    headers = {"User-Agent": REDDIT_USER_AGENT}
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            p = child.get("data", {})
            if not p:
                continue
            posts.append({
                "title": p.get("title", ""),
                "selftext": (p.get("selftext") or "")[:1500],
                "url": f"https://www.reddit.com{p.get('permalink', '')}",
                "score": p.get("score", 0),
                "num_comments": p.get("num_comments", 0),
                "subreddit": subreddit,
                "author": p.get("author"),
                "created_utc": p.get("created_utc"),
            })
        return posts
    except Exception as e:
        logger.warning(f"[reddit] {subreddit}/{category} falhou (public): {e}")
        return []


def _fetch_praw(subreddit: str, category: str, limit: int) -> List[Dict[str, Any]]:
    try:
        import praw
    except ImportError:
        logger.info("[reddit] praw nao instalado, fallback HTTP publico")
        return []
    try:
        r = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
        sub = r.subreddit(subreddit)
        getter = {
            "rising": sub.rising,
            "hot": sub.hot,
            "top": lambda limit=limit: sub.top(time_filter="day", limit=limit),
            "new": sub.new,
        }.get(category, sub.hot)
        out = []
        for p in getter(limit=limit):
            out.append({
                "title": p.title,
                "selftext": (p.selftext or "")[:1500],
                "url": f"https://www.reddit.com{p.permalink}",
                "score": p.score,
                "num_comments": p.num_comments,
                "subreddit": subreddit,
                "author": str(p.author) if p.author else None,
                "created_utc": p.created_utc,
            })
        return out
    except Exception as e:
        logger.warning(f"[reddit] praw falhou: {e}")
        return []


async def fetch_reddit(
    subreddits: List[str],
    category: str = "rising",
    limit_per_sub: int = 5,
) -> List[Dict[str, Any]]:
    """Coleta posts de N subreddits em paralelo. category: rising|hot|top|new."""
    use_praw = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)

    async def _one(sub: str) -> List[Dict[str, Any]]:
        if use_praw:
            return await asyncio.to_thread(_fetch_praw, sub, category, limit_per_sub)
        return await _fetch_public(sub, category, limit_per_sub)

    results = await asyncio.gather(*[_one(s.strip().lstrip("r/")) for s in subreddits if s.strip()])
    flat = [p for batch in results for p in batch]
    flat.sort(key=lambda p: p.get("score", 0), reverse=True)
    return flat
