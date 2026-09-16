"""Normaliza as tabelas legadas de noticias do Supabase em um unico feed."""
from __future__ import annotations

import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)


SOURCE_TABLES = {
    "articles": "noticias",
    "perplexity": "noticias_perplexity",
    "reddit": "posts_do_reddit",
    "youtube": "videos_do_youtube",
    "twitter": "tweets",
}

RSS_SOURCE = "rss"
FEED_SOURCES = {**SOURCE_TABLES, RSS_SOURCE: "rss"}


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    rendered = str(value).strip()
    return rendered or None


def _iso_date(*values: Any) -> Optional[str]:
    for value in values:
        rendered = _text(value)
        if rendered:
            return rendered
    return None


def _tags(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(tag) for tag in value if _text(tag)]
    rendered = _text(value)
    return [tag.strip() for tag in rendered.split(",") if tag.strip()] if rendered else []


def _image_url(value: Any) -> Optional[str]:
    """Aceita URL direta ou o JSON serializado usado por url_da_thumb."""
    if isinstance(value, list):
        return _image_url(value[0]) if value else None
    if isinstance(value, dict):
        return _image_url(value.get("url") or value.get("src"))

    rendered = _text(value)
    if not rendered:
        return None
    if rendered.startswith(("[", "{")):
        try:
            return _image_url(json.loads(rendered))
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
    return rendered if rendered.startswith(("http://", "https://")) else None


def _youtube_thumbnail(video_url: Any, stored_thumbnail: Any) -> Optional[str]:
    parsed_thumbnail = _image_url(stored_thumbnail)
    if parsed_thumbnail:
        return parsed_thumbnail

    rendered_url = _text(video_url)
    if not rendered_url:
        return None
    parsed = urlparse(rendered_url)
    video_id = parse_qs(parsed.query).get("v", [None])[0]
    if not video_id and parsed.hostname in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
    return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None


def _normalize(source: str, row: Dict[str, Any]) -> Dict[str, Any]:
    row_id = str(row.get("id", ""))

    if source == "articles":
        return {
            "id": f"articles:{row_id}",
            "source": source,
            "source_label": _text(row.get("fonte")) or "Noticia",
            "title": _text(row.get("titulo")) or "Sem titulo",
            "summary": _text(row.get("resumo")) or _text(row.get("conteudo")),
            "url": _text(row.get("url")),
            "thumbnail_url": None,
            "published_at": _iso_date(row.get("publicado_em"), row.get("criado_em")),
            "category": _text(row.get("categoria")),
            "tags": _tags(row.get("tags")),
            "metrics": {},
        }

    if source == "perplexity":
        return {
            "id": f"perplexity:{row_id}",
            "source": source,
            "source_label": "Perplexity",
            "title": _text(row.get("headline")) or "Sem titulo",
            "summary": _text(row.get("resumo")),
            "url": None,
            "thumbnail_url": None,
            "published_at": _iso_date(row.get("data_atualizacao"), row.get("data_criacao")),
            "category": "Radar IA",
            "tags": [],
            "metrics": {},
        }

    if source == "reddit":
        return {
            "id": f"reddit:{row_id}",
            "source": source,
            "source_label": "Reddit",
            "title": _text(row.get("titulo")) or "Sem titulo",
            "summary": _text(row.get("resumo")),
            "url": _text(row.get("url")),
            "thumbnail_url": None,
            "published_at": _iso_date(row.get("date"), row.get("data_atualizacao"), row.get("data_criacao")),
            "category": "Comunidade",
            "tags": [],
            "metrics": {"engagement": row.get("updates_engagement")},
        }

    if source == "youtube":
        video_url = _text(row.get("link_do_video"))
        return {
            "id": f"youtube:{row_id}",
            "source": source,
            "source_label": _text(row.get("nome_do_canal")) or "YouTube",
            "title": _text(row.get("titulo")) or "Sem titulo",
            "summary": _text(row.get("resumo_rapido")) or _text(row.get("resumo_detalhado")),
            "url": video_url,
            "thumbnail_url": _youtube_thumbnail(video_url, row.get("url_da_thumb")),
            "published_at": _iso_date(row.get("updated_at"), row.get("created_at")),
            "category": "Video",
            "tags": [],
            "metrics": {"views": row.get("views")},
        }

    return {
        "id": f"twitter:{row_id}",
        "source": "twitter",
        "source_label": "X / Twitter",
        "title": _text(row.get("tweet_text")) or "Publicacao no X",
        "summary": None,
        "url": _text(row.get("url")),
        "thumbnail_url": None,
        "published_at": _iso_date(row.get("data_atualizacao"), row.get("data_criacao")),
        "category": "Social",
        "tags": [],
        "metrics": {"likes": row.get("like_count")},
    }


def _timestamp(value: Optional[str]) -> float:
    if not value:
        return 0.0
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except (TypeError, ValueError):
        return 0.0


def _query_rows(client: Any, source: str, limit: int) -> List[Dict[str, Any]]:
    table = SOURCE_TABLES[source]
    order_column = {
        "articles": "publicado_em",
        "perplexity": "data_atualizacao",
        "reddit": "data_atualizacao",
        "youtube": "updated_at",
        "twitter": "data_atualizacao",
    }[source]
    query = client.table(table).select("*")
    if source == "articles":
        query = query.eq("ativo", True)
    response = query.order(order_column, desc=True).limit(limit).execute()
    return list(response.data or [])


def build_news_feed(
    client: Any,
    *,
    limit: int = 50,
    source: Optional[str] = None,
    search: Optional[str] = None,
    include_rss_fallback: bool = True,
) -> Dict[str, Any]:
    """Le as tabelas de coleta, normaliza seus campos e ordena por data."""
    selected_sources: Iterable[str] = [source] if source else SOURCE_TABLES.keys()
    per_source_limit = min(max(limit, 20), 100)
    items: List[Dict[str, Any]] = []
    source_counts: Dict[str, int] = {}
    source_errors: Dict[str, str] = {}

    for current_source in selected_sources:
        if current_source == RSS_SOURCE:
            try:
                from app.services.news_digest.rss_service import fetch_rss_news

                rss_items = fetch_rss_news(query=search, limit=per_source_limit)
                items.extend(rss_items)
                source_counts[RSS_SOURCE] = len(rss_items)
            except Exception:
                logger.exception("[news_feed] falha ao buscar RSS")
                source_counts[RSS_SOURCE] = 0
                source_errors[RSS_SOURCE] = "RSS temporariamente indisponivel"
            continue

        try:
            rows = _query_rows(client, current_source, per_source_limit)
            normalized = [_normalize(current_source, row) for row in rows]
            items.extend(normalized)
            source_counts[current_source] = len(normalized)
        except Exception as exc:  # uma fonte indisponivel nao deve derrubar o feed inteiro
            logger.exception("[news_feed] falha ao ler %s", SOURCE_TABLES[current_source])
            source_counts[current_source] = 0
            source_errors[current_source] = "Fonte temporariamente indisponivel"

    term = (search or "").strip().casefold()
    if term:
        items = [
            item
            for item in items
            if term in " ".join(
                str(item.get(key) or "")
                for key in ("title", "summary", "source_label", "category")
            ).casefold()
        ]

    if include_rss_fallback and not items and source in (None, RSS_SOURCE):
        try:
            from app.services.news_digest.rss_service import fetch_rss_news

            rss_items = fetch_rss_news(query=search, limit=per_source_limit)
            items.extend(rss_items)
            source_counts[RSS_SOURCE] = len(rss_items)
        except Exception:
            logger.exception("[news_feed] fallback RSS falhou")
            source_counts[RSS_SOURCE] = 0
            source_errors[RSS_SOURCE] = "RSS temporariamente indisponivel"

    items.sort(key=lambda item: _timestamp(item.get("published_at")), reverse=True)
    items = items[:limit]
    return {
        "items": items,
        "total": len(items),
        "sources": source_counts,
        "source_errors": source_errors,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
