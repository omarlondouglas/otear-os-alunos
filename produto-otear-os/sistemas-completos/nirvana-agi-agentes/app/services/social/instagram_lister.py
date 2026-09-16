"""
Instagram Profile Lister
Lista os ultimos N posts (Reels/Videos) de um perfil publico do Instagram.

Usa `instaloader` (sem login). Limitacoes:
  - Perfis privados retornam 0 posts.
  - Rate limit informal: ~50 perfis/dia sem login. Para escala, usar sessao logada.
  - So retorna posts com video (Reels). Fotos sao filtradas.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from app.services.social.types import SocialPost

logger = logging.getLogger(__name__)


def _get_loader():
    try:
        import instaloader
    except ImportError as e:
        raise ImportError(
            "Instagram listing requires instaloader. "
            "Run: pip install instaloader"
        ) from e

    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )
    return instaloader, L


def list_recent_posts(handle: str, count: int = 10, only_videos: bool = True) -> List[SocialPost]:
    """Lista posts publicos do perfil. Retorna lista vazia se perfil for privado."""
    handle_clean = handle.lstrip("@")
    try:
        instaloader, L = _get_loader()
    except ImportError as e:
        logger.error(f"[instagram_lister] {e}")
        return []

    try:
        profile = instaloader.Profile.from_username(L.context, handle_clean)
        if profile.is_private:
            logger.warning(f"[instagram_lister] @{handle_clean} eh privado, nada a listar")
            return []
    except Exception as e:
        logger.error(f"[instagram_lister] falha ao abrir perfil @{handle_clean}: {e}")
        return []

    out: List[SocialPost] = []
    try:
        for post in profile.get_posts():
            if only_videos and not post.is_video:
                continue
            out.append(SocialPost(
                post_id=str(post.shortcode),
                platform="instagram",
                handle=f"@{handle_clean}",
                url=f"https://www.instagram.com/p/{post.shortcode}/",
                play_url=post.video_url if post.is_video else None,
                cover_url=post.url,
                title=(post.caption or "")[:500],
                duration=float(post.video_duration or 0),
                posted_at=post.date_utc.isoformat() if post.date_utc else None,
                play_count=_safe_int(getattr(post, "video_view_count", None)),
                like_count=_safe_int(post.likes),
                comment_count=_safe_int(post.comments),
            ))
            if len(out) >= count:
                break
    except Exception as e:
        logger.warning(f"[instagram_lister] erro iterando posts de @{handle_clean}: {e}")

    logger.info(f"[instagram_lister] @{handle_clean}: {len(out)} posts retornados")
    return out


def _safe_int(v) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None
