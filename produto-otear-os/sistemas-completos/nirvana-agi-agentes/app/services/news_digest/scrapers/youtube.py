"""
YouTube scraper — Data API v3 (free tier ~10k units/dia) + youtube-transcript-api.

Substitui:
  - n8n YouTube node (search.list)
  - Apify karamelo~youtube-transcripts

Free tier: search.list = 100 units, videos.list = 1 unit/video.
10 videos = 110 units/dia, sobra MUITO.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") or os.getenv("GOOGLE_API_KEY")
SHORT_THRESHOLD_SECONDS = 210  # filtra Shorts (< 3min30s)


def _iso8601_to_seconds(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mi * 60 + s


async def _get_transcript(video_id: str, languages: List[str]) -> str:
    """Pega transcript via youtube-transcript-api. Tenta varios idiomas."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        logger.warning("[yt] youtube-transcript-api nao instalado")
        return ""

    def _fetch():
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                t = transcript_list.find_transcript(languages)
            except Exception:
                t = next(iter(transcript_list))
            data = t.fetch()
            return " ".join(item.get("text", "") if isinstance(item, dict) else getattr(item, "text", "") for item in data)
        except Exception as e:
            logger.info(f"[yt] sem transcript pra {video_id}: {e}")
            return ""

    return await asyncio.to_thread(_fetch)


async def fetch_youtube(
    query: str,
    max_results: int = 10,
    region: str = "US",
    transcript_langs: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Busca videos do dia + metadados + transcripts. Filtra Shorts."""
    if not YOUTUBE_API_KEY:
        logger.warning("[yt] YOUTUBE_API_KEY/GOOGLE_API_KEY ausente — pulando")
        return []

    try:
        from googleapiclient.discovery import build
    except ImportError:
        logger.error("[yt] google-api-python-client nao instalado")
        return []

    languages = transcript_langs or ["pt", "pt-BR", "en"]

    def _search() -> List[Dict[str, Any]]:
        yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False)
        published_after = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        search_resp = yt.search().list(
            part="id",
            q=query,
            type="video",
            order="relevance",
            maxResults=max_results,
            regionCode=region,
            safeSearch="moderate",
            publishedAfter=published_after,
        ).execute()
        ids = [item["id"]["videoId"] for item in search_resp.get("items", []) if item.get("id", {}).get("videoId")]
        if not ids:
            return []
        details = yt.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(ids),
        ).execute()
        out = []
        for item in details.get("items", []):
            duration = _iso8601_to_seconds(item["contentDetails"]["duration"])
            if duration < SHORT_THRESHOLD_SECONDS:
                continue
            sn = item["snippet"]
            st = item.get("statistics", {})
            out.append({
                "id": item["id"],
                "title": sn["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "channel": sn.get("channelTitle"),
                "published_at": sn.get("publishedAt"),
                "thumbnail": (sn.get("thumbnails", {}).get("high") or {}).get("url"),
                "views": int(st.get("viewCount", 0) or 0),
                "duration_seconds": duration,
                "description": sn.get("description", "")[:500],
            })
        return out

    try:
        videos = await asyncio.to_thread(_search)
    except Exception as e:
        logger.error(f"[yt] busca falhou: {e}")
        return []

    # paraleliza transcripts
    sem = asyncio.Semaphore(3)

    async def _enrich(v: Dict[str, Any]):
        async with sem:
            v["transcript"] = await _get_transcript(v["id"], languages)
        return v

    enriched = await asyncio.gather(*[_enrich(v) for v in videos], return_exceptions=False)
    return [v for v in enriched if v]
