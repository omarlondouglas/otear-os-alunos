"""
Twitter/X scraper sem Apify.

Estrategia em cascata (mais barato pro mais robusto):
  1. Nitter publico (sem auth, gratis)        — frageis, instancias morrem
  2. Playwright em x.com/search (anonimo)     — passa em quase tudo, lento
  3. TwitterAPI.io (TWITTERAPI_IO_KEY)        — pago barato (~$0.001/tweet)

Cada estrategia retorna a mesma estrutura de tweet pro analyzer.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import httpx

logger = logging.getLogger(__name__)

NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.tiekoetter.com",
]

TWITTERAPI_IO_KEY = os.getenv("TWITTERAPI_IO_KEY")


async def _try_nitter(query: str, max_items: int) -> List[Dict[str, Any]]:
    """Scraping HTML de instancia Nitter publica."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    out: List[Dict[str, Any]] = []
    for instance in NITTER_INSTANCES:
        url = f"{instance}/search?f=tweets&q={quote_plus(query)}"
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
                r = await c.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code != 200:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                for tw in soup.select("div.timeline-item")[:max_items]:
                    content_el = tw.select_one("div.tweet-content")
                    stats_el = tw.select("span.tweet-stat")
                    link_el = tw.select_one("a.tweet-link")
                    user_el = tw.select_one("a.username")
                    if not content_el or not link_el:
                        continue

                    def _stat(idx: int) -> int:
                        try:
                            return int((stats_el[idx].get_text(strip=True) or "0").replace(",", ""))
                        except Exception:
                            return 0

                    href = link_el.get("href", "")
                    out.append({
                        "text": content_el.get_text(" ", strip=True),
                        "url": f"https://x.com{href}" if href.startswith("/") else href,
                        "user": user_el.get_text(strip=True) if user_el else None,
                        "replies": _stat(0),
                        "retweets": _stat(1),
                        "likes": _stat(2) if len(stats_el) > 2 else 0,
                    })
                if out:
                    logger.info(f"[twitter] Nitter ok ({instance}, {len(out)} tweets)")
                    return out
        except Exception as e:
            logger.debug(f"[twitter] Nitter {instance} falhou: {e}")
            continue
    return out


async def _try_playwright(query: str, max_items: int) -> List[Dict[str, Any]]:
    """Fallback Playwright — abre x.com/search."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.info("[twitter] playwright nao instalado, pulando")
        return []

    out: List[Dict[str, Any]] = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx = await browser.new_context(viewport={"width": 1280, "height": 1024})
            page = await ctx.new_page()
            await page.goto(
                f"https://x.com/search?q={quote_plus(query)}&src=typed_query&f=top",
                wait_until="domcontentloaded",
                timeout=25_000,
            )
            try:
                await page.wait_for_selector("article", timeout=15_000)
            except Exception:
                await browser.close()
                return []
            articles = await page.locator("article").all()
            for art in articles[:max_items]:
                try:
                    text = await art.inner_text()
                    link_el = art.locator("a[href*='/status/']").first
                    href = await link_el.get_attribute("href") if await link_el.count() else None
                    if not href:
                        continue
                    out.append({
                        "text": text[:1200],
                        "url": f"https://x.com{href}" if href.startswith("/") else href,
                        "user": None,
                        "likes": 0,
                        "retweets": 0,
                        "replies": 0,
                    })
                except Exception:
                    continue
            await browser.close()
        if out:
            logger.info(f"[twitter] Playwright ok ({len(out)} tweets)")
    except Exception as e:
        logger.warning(f"[twitter] Playwright falhou: {e}")
    return out


async def _try_twitterapi_io(query: str, max_items: int) -> List[Dict[str, Any]]:
    if not TWITTERAPI_IO_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(
                "https://api.twitterapi.io/twitter/tweet/advanced_search",
                headers={"X-API-Key": TWITTERAPI_IO_KEY},
                params={"query": query, "queryType": "Top"},
            )
            r.raise_for_status()
            data = r.json()
        tweets = data.get("tweets") or data.get("data") or []
        out = []
        for t in tweets[:max_items]:
            out.append({
                "text": t.get("text", ""),
                "url": t.get("url") or f"https://x.com/i/status/{t.get('id', '')}",
                "user": (t.get("author") or {}).get("userName"),
                "likes": t.get("likeCount", 0),
                "retweets": t.get("retweetCount", 0),
                "replies": t.get("replyCount", 0),
            })
        if out:
            logger.info(f"[twitter] TwitterAPI.io ok ({len(out)} tweets)")
        return out
    except Exception as e:
        logger.warning(f"[twitter] TwitterAPI.io falhou: {e}")
        return []


async def fetch_twitter(query: str, max_items: int = 30) -> List[Dict[str, Any]]:
    """Cascata: Nitter -> Playwright -> TwitterAPI.io. Devolve primeiro com dados."""
    nitter = await _try_nitter(query, max_items)
    if nitter:
        return nitter
    pw = await _try_playwright(query, max_items)
    if pw:
        return pw
    paid = await _try_twitterapi_io(query, max_items)
    return paid
