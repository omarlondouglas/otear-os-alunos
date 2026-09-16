"""News Radar — endpoints pra disparar digest manual, listar e ler digests."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.security import verify_supabase_token
from app.core.supabase import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)


class DigestRunRequest(BaseModel):
    niche: Optional[str] = None
    youtube_query: Optional[str] = None
    twitter_query: Optional[str] = None
    subreddits: Optional[str] = None  # CSV
    sync: bool = False  # se True, roda inline (mais lento mas devolve resultado direto)


class NewsRadarConfig(BaseModel):
    niche: Optional[str] = None
    youtube_query: Optional[str] = None
    twitter_query: Optional[str] = None
    subreddits: Optional[str] = None


class RssIngestRequest(BaseModel):
    query: str
    limit: int = 20


@router.get("/feed")
async def get_news_feed(
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=120),
    user_data: dict = Depends(verify_supabase_token),
):
    """Agrega as tabelas de noticias existentes em um feed unico."""
    from app.services.news_digest.feed_service import FEED_SOURCES, build_news_feed

    normalized_source = None if not source or source == "all" else source
    if normalized_source and normalized_source not in FEED_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"Fonte invalida. Use: {', '.join(FEED_SOURCES)}",
        )

    return await asyncio.to_thread(
        build_news_feed,
        get_supabase(),
        limit=limit,
        source=normalized_source,
        search=search,
    )


@router.post("/rss/ingest")
async def ingest_rss_news_endpoint(
    body: RssIngestRequest,
    user_data: dict = Depends(verify_supabase_token),
):
    """Busca RSS por palavra-chave/nicho e persiste itens novos em `noticias`."""
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Informe uma palavra-chave ou nicho")

    def _ingest():
        from app.services.news_digest.rss_service import fetch_rss_news, rss_item_to_article_row

        client = get_supabase()
        items = fetch_rss_news(query=query, limit=max(1, min(body.limit, 100)))
        rows = [rss_item_to_article_row(item) for item in items if item.get("url")]
        urls = [row["url"] for row in rows if row.get("url")]
        existing_urls = set()

        for url in urls:
            try:
                res = client.table("noticias").select("url").eq("url", url).limit(1).execute()
                if res.data:
                    existing_urls.add(url)
            except Exception:
                logger.exception("[news_rss] falha ao checar duplicidade")

        new_rows = [row for row in rows if row.get("url") not in existing_urls]
        inserted = 0
        if new_rows:
            res = client.table("noticias").insert(new_rows).execute()
            inserted = len(res.data or new_rows)

        return {
            "ok": True,
            "query": query,
            "fetched": len(items),
            "inserted": inserted,
            "skipped": len(rows) - len(new_rows),
            "items": items,
        }

    try:
        return await asyncio.to_thread(_ingest)
    except Exception as exc:
        logger.exception("[news] ingest_rss falhou")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/run")
async def run_digest_endpoint(
    body: DigestRunRequest,
    user_data: dict = Depends(verify_supabase_token),
):
    """Dispara um digest. sync=False (default) usa Celery; sync=True roda inline."""
    override: Dict[str, Any] = {k: v for k, v in body.dict().items() if v not in (None, "") and k != "sync"}

    if body.sync:
        from app.services.news_digest.digest_service import run_digest
        digest = await asyncio.to_thread(
            run_digest,
            user_id=user_data["user_id"],
            override=override,
            persist=True,
        )
        return {
            "ok": True,
            "mode": "sync",
            "asset_id": digest.get("asset_id"),
            "digest": {
                "niche": digest["niche"],
                "youtube": digest["youtube"],
                "reddit": digest["reddit"],
                "twitter": digest["twitter"],
                "perplexity": digest["perplexity"],
                "ideas": digest["ideas"],
                "html": digest["html"],
                "generated_at": digest["generated_at"],
            },
        }

    from app.workers.news_digest_task import run_news_digest_task
    task = run_news_digest_task.delay(user_id=user_data["user_id"], override=override)
    return {"ok": True, "mode": "async", "task_id": task.id}


@router.get("/list")
async def list_digests(
    limit: int = Query(20, le=100),
    user_data: dict = Depends(verify_supabase_token),
):
    """Lista os ultimos digests do usuario (mais novo primeiro)."""
    client = get_supabase()
    res = (
        client.table("content_assets")
        .select("id,title,created_at,metadata")
        .eq("user_id", user_data["user_id"])
        .eq("type", "news_digest")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    items = []
    for row in res.data or []:
        md = row.get("metadata") or {}
        items.append({
            "id": row["id"],
            "title": row.get("title"),
            "created_at": row.get("created_at"),
            "niche": md.get("niche"),
            "counts": {
                "youtube": len(md.get("youtube", [])),
                "reddit": len(md.get("reddit", [])),
                "twitter_top": len((md.get("twitter") or {}).get("top_tweets", [])),
                "perplexity": len(md.get("perplexity", [])),
                "ideas": len(md.get("ideas", [])),
            },
        })
    return {"items": items}


@router.get("/{digest_id}")
async def get_digest(
    digest_id: str,
    user_data: dict = Depends(verify_supabase_token),
):
    client = get_supabase()
    res = (
        client.table("content_assets")
        .select("*")
        .eq("id", digest_id)
        .eq("user_id", user_data["user_id"])
        .eq("type", "news_digest")
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Digest nao encontrado")
    return res.data


@router.get("/config/current")
async def get_config(user_data: dict = Depends(verify_supabase_token)):
    """Le config atual do news_radar do vault USER.md."""
    from app.services.news_digest.digest_service import _load_config_from_vault, _resolve_config
    vault_cfg = _load_config_from_vault()
    resolved = _resolve_config()
    return {"vault": vault_cfg, "resolved": resolved}


@router.post("/config")
async def update_config(
    cfg: NewsRadarConfig,
    user_data: dict = Depends(verify_supabase_token),
):
    """Atualiza secao news_radar do USER.md no vault."""
    try:
        from app.services.user_memory import update_section
        lines = []
        if cfg.niche:
            lines.append(f"niche: {cfg.niche}")
        if cfg.youtube_query:
            lines.append(f"youtube_query: {cfg.youtube_query}")
        if cfg.twitter_query:
            lines.append(f"twitter_query: {cfg.twitter_query}")
        if cfg.subreddits:
            lines.append(f"subreddits: {cfg.subreddits}")
        if not lines:
            raise HTTPException(status_code=400, detail="Forneca pelo menos um campo")
        body = "\n".join(lines)
        update_section("user", "news_radar", body)
        return {"ok": True, "section": "news_radar", "body": body}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[news] update_config falhou")
        raise HTTPException(status_code=500, detail=str(e))
