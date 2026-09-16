"""
TikTok Profile Lister
Lista os ultimos N posts de um perfil TikTok.

Estrategia em cascata:
  1. tikwm.com API publica (rapido, sem auth) - https://www.tikwm.com/api/user/posts
  2. yt-dlp como fallback (mais robusto, mais lento)

Limitacoes:
  - tikwm.com tem rate limits informais (~10 req/min); ok para uso esporadico
  - perfis privados nao funcionam em nenhuma das duas
"""
from __future__ import annotations

import json
import logging
import subprocess
import tempfile
from typing import List, Optional

import requests

from app.services.social.types import SocialPost

logger = logging.getLogger(__name__)

TIKWM_API = "https://www.tikwm.com/api/user/posts"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)


def list_recent_posts(handle: str, count: int = 10, timeout: int = 30) -> List[SocialPost]:
    """Tenta tikwm primeiro, cai para yt-dlp se falhar.

    Args:
        handle: @ do criador (com ou sem @).
        count: max de posts a retornar.
        timeout: segundos por tentativa.
    """
    handle_clean = handle.lstrip("@")
    try:
        posts = _list_via_tikwm(handle_clean, count, timeout)
        if posts:
            logger.info(f"[tiktok_lister] tikwm ok: {len(posts)} posts de @{handle_clean}")
            return posts
    except Exception as e:
        logger.warning(f"[tiktok_lister] tikwm falhou para @{handle_clean}: {e}")

    try:
        posts = _list_via_ytdlp(handle_clean, count, timeout)
        logger.info(f"[tiktok_lister] yt-dlp ok: {len(posts)} posts de @{handle_clean}")
        return posts
    except Exception as e:
        logger.error(f"[tiktok_lister] yt-dlp tambem falhou para @{handle_clean}: {e}")
        return []


def _list_via_tikwm(handle: str, count: int, timeout: int) -> List[SocialPost]:
    params = {"unique_id": handle, "count": str(count), "cursor": "0"}
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    r = requests.get(TIKWM_API, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(f"tikwm error: {data.get('msg', data)}")

    videos = (data.get("data") or {}).get("videos") or []
    out: List[SocialPost] = []
    for v in videos[:count]:
        vid = str(v.get("video_id") or v.get("aweme_id") or "")
        if not vid:
            continue
        out.append(SocialPost(
            post_id=vid,
            platform="tiktok",
            handle=f"@{handle}",
            url=f"https://www.tiktok.com/@{handle}/video/{vid}",
            play_url=v.get("play") or v.get("wmplay"),
            cover_url=v.get("cover") or v.get("origin_cover"),
            title=str(v.get("title") or "").strip(),
            duration=float(v.get("duration") or 0),
            posted_at=_format_ts(v.get("create_time")),
            play_count=_safe_int(v.get("play_count")),
            like_count=_safe_int(v.get("digg_count")),
            comment_count=_safe_int(v.get("comment_count")),
        ))
    return out


def _list_via_ytdlp(handle: str, count: int, timeout: int) -> List[SocialPost]:
    """Fallback: yt-dlp --flat-playlist retorna 1 JSON por linha (info simplificada)."""
    profile_url = f"https://www.tiktok.com/@{handle}"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-end", str(count),
        "--no-warnings",
        "--quiet",
        "-J",  # dump JSON unico (com 'entries')
        profile_url,
    ]
    # Em Windows, capturar stdout/stderr em pipes pode deixar o processo do
    # yt-dlp pendurado em alguns perfis do TikTok. Arquivos temporarios evitam isso.
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".json", delete=False) as out_file, \
         tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".log", delete=False) as err_file:
        out_path = out_file.name
        err_path = err_file.name

    try:
        with open(out_path, "w", encoding="utf-8") as out_handle, open(err_path, "w", encoding="utf-8") as err_handle:
            r = subprocess.run(cmd, stdout=out_handle, stderr=err_handle, timeout=timeout, text=True)

        stderr_text = ""
        if r.returncode != 0:
            try:
                stderr_text = open(err_path, "r", encoding="utf-8").read()
            except OSError:
                stderr_text = ""
            raise RuntimeError(f"yt-dlp exit={r.returncode}: {stderr_text[-200:]}")

        try:
            stdout_text = open(out_path, "r", encoding="utf-8").read()
        except OSError as e:
            raise RuntimeError(f"yt-dlp nao gerou JSON legivel: {e}")

        try:
            info = json.loads(stdout_text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"yt-dlp JSON invalido: {e}")
    finally:
        for temp_path in (out_path, err_path):
            try:
                import os
                os.unlink(temp_path)
            except OSError:
                pass

    entries = info.get("entries") or []
    out: List[SocialPost] = []
    for e in entries[:count]:
        vid = str(e.get("id") or "")
        if not vid:
            continue
        out.append(SocialPost(
            post_id=vid,
            platform="tiktok",
            handle=f"@{handle}",
            url=e.get("url") or f"https://www.tiktok.com/@{handle}/video/{vid}",
            play_url=None,  # flat-playlist nao expoe; baixaremos sob demanda
            cover_url=e.get("thumbnail"),
            title=str(e.get("title") or "").strip(),
            duration=float(e.get("duration") or 0),
            posted_at=None,
            play_count=_safe_int(e.get("view_count")),
            like_count=_safe_int(e.get("like_count")),
            comment_count=_safe_int(e.get("comment_count")),
        ))
    return out


def _format_ts(ts) -> Optional[str]:
    if not ts:
        return None
    try:
        from datetime import datetime, timezone
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except Exception:
        return None


def _safe_int(v) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None
