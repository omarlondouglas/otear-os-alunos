"""Busca noticias via RSS por nicho/palavra-chave.

Usa Google News RSS como fonte padrao porque nao exige chave de API e aceita
queries por tema. Tambem aceita feeds RSS explicitos via NEWS_RSS_FEEDS.
"""
from __future__ import annotations

import html
import logging
import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote_plus
from xml.etree import ElementTree

import httpx

logger = logging.getLogger(__name__)

DEFAULT_QUERY = os.getenv("NEWS_DIGEST_NICHE", "inteligencia artificial OR IA")
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
RSS_TIMEOUT_SECONDS = float(os.getenv("NEWS_RSS_TIMEOUT_SECONDS", "8"))


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    rendered = html.unescape(str(value)).strip()
    return rendered or None


def _strip_html(value: Any) -> Optional[str]:
    rendered = _text(value)
    if not rendered:
        return None
    without_tags = re.sub(r"<[^>]+>", " ", rendered)
    return re.sub(r"\s+", " ", without_tags).strip() or None


def _published_at(value: Any) -> str:
    rendered = _text(value)
    if rendered:
        try:
            parsed = parsedate_to_datetime(rendered)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError, IndexError, OverflowError):
            pass
    return datetime.now(timezone.utc).isoformat()


def _source_from_title(title: str) -> Optional[str]:
    if " - " not in title:
        return None
    return title.rsplit(" - ", 1)[-1].strip() or None


def _clean_google_title(title: str, source: Optional[str]) -> str:
    if source and title.endswith(f" - {source}"):
        return title[: -(len(source) + 3)].strip()
    return title


def _child_text(item: ElementTree.Element, names: Iterable[str]) -> Optional[str]:
    for name in names:
        child = item.find(name)
        if child is not None and child.text:
            return _text(child.text)
    return None


def parse_rss_items(xml_text: str, *, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Parseia RSS 2.0/Atom simples em itens normalizados para o News Feed."""
    root = ElementTree.fromstring(xml_text)
    channel_items = root.findall(".//channel/item")
    atom_items = root.findall("{http://www.w3.org/2005/Atom}entry")
    raw_items = channel_items or atom_items

    items: List[Dict[str, Any]] = []
    seen_urls = set()
    for index, item in enumerate(raw_items):
        title = _child_text(item, ["title", "{http://www.w3.org/2005/Atom}title"]) or "Sem titulo"
        url = _child_text(item, ["link"])
        if not url:
            atom_link = item.find("{http://www.w3.org/2005/Atom}link")
            url = _text(atom_link.attrib.get("href")) if atom_link is not None else None
        if url in seen_urls:
            continue
        if url:
            seen_urls.add(url)

        source = _child_text(item, ["source"]) or _source_from_title(title) or "RSS"
        clean_title = _clean_google_title(title, source)
        published = _child_text(item, ["pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated"])
        summary = _strip_html(_child_text(item, ["description", "summary", "{http://www.w3.org/2005/Atom}summary"]))

        items.append({
            "id": f"rss:{abs(hash(url or clean_title))}:{index}",
            "source": "rss",
            "source_label": source,
            "title": clean_title,
            "summary": summary,
            "url": url,
            "thumbnail_url": None,
            "published_at": _published_at(published),
            "category": query,
            "tags": [tag.strip() for tag in re.split(r"[,;]", query) if tag.strip()][:5],
            "metrics": {},
        })
        if len(items) >= limit:
            break
    return items


def _rss_urls(query: str) -> List[str]:
    configured = [url.strip() for url in os.getenv("NEWS_RSS_FEEDS", "").split(",") if url.strip()]
    if configured:
        return configured
    return [GOOGLE_NEWS_RSS.format(query=quote_plus(query))]


def fetch_rss_news(*, query: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Busca noticias recentes por RSS. Falhas retornam lista vazia."""
    resolved_query = (query or DEFAULT_QUERY).strip() or DEFAULT_QUERY
    items: List[Dict[str, Any]] = []

    with httpx.Client(timeout=RSS_TIMEOUT_SECONDS, follow_redirects=True) as client:
        for url in _rss_urls(resolved_query):
            try:
                response = client.get(url, headers={"User-Agent": "agi-agentes-news-rss/1.0"})
                response.raise_for_status()
                items.extend(parse_rss_items(response.text, query=resolved_query, limit=limit - len(items)))
            except Exception as exc:
                logger.warning("[news_rss] falha ao buscar %s: %s", url, exc)
            if len(items) >= limit:
                break

    return items[:limit]


def rss_item_to_article_row(item: Dict[str, Any]) -> Dict[str, Any]:
    """Converte item normalizado de RSS para a tabela legada `noticias`."""
    return {
        "titulo": item.get("title"),
        "resumo": item.get("summary"),
        "fonte": item.get("source_label") or "RSS",
        "url": item.get("url"),
        "publicado_em": item.get("published_at"),
        "categoria": item.get("category") or "RSS",
        "tags": ", ".join(item.get("tags") or []),
        "ativo": True,
    }
