"""
Celery task pro News Digest. Pode ser disparada por beat schedule (diario)
ou via endpoint manual.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from celery.schedules import crontab

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="news_digest.run", max_retries=1)
def run_news_digest_task(self, user_id: Optional[str] = None, override: Optional[Dict[str, Any]] = None):
    from app.services.news_digest.digest_service import run_digest
    try:
        digest = run_digest(user_id=user_id, override=override, persist=True)
        return {
            "ok": True,
            "asset_id": digest.get("asset_id"),
            "niche": digest.get("niche"),
            "counts": {
                "youtube": len(digest.get("youtube", [])),
                "reddit": len(digest.get("reddit", [])),
                "twitter_top": len((digest.get("twitter") or {}).get("top_tweets", [])),
                "perplexity": len(digest.get("perplexity", [])),
                "ideas": len(digest.get("ideas", [])),
            },
        }
    except Exception as e:
        logger.exception(f"[news_digest] task falhou: {e}")
        raise self.retry(exc=e, countdown=300)


# Beat schedule: diario as 11:00 UTC (08:00 BRT)
celery_app.conf.beat_schedule = {
    **(celery_app.conf.beat_schedule or {}),
    "news-digest-daily": {
        "task": "news_digest.run",
        "schedule": crontab(hour=11, minute=0),
        "args": (),  # roda sem user_id; persiste apenas para usuario default se configurado
    },
}
