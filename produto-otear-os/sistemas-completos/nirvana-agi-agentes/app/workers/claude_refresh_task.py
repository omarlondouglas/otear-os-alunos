"""
Celery beat: refresh proativo do credentials.json a cada 30 minutos.

Mantem o token Claude OAuth sempre fresco no volume persistente, evitando
expiracao silenciosa entre restarts do EasyPanel.
"""
from __future__ import annotations

import logging

from celery.schedules import crontab

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="claude.refresh_credentials")
def refresh_claude_credentials_task():
    from app.services.claude_credentials_refresher import refresh_claude_credentials
    result = refresh_claude_credentials(force=False)
    logger.info(f"[claude-refresh-task] {result}")
    return result


celery_app.conf.beat_schedule = {
    **(celery_app.conf.beat_schedule or {}),
    "claude-credentials-refresh": {
        "task": "claude.refresh_credentials",
        "schedule": crontab(minute="*/30"),  # a cada 30min
    },
}
