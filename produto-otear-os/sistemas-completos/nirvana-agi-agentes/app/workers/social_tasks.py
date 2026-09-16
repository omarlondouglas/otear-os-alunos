"""
Celery tasks para extracao de perfis sociais (background, paralelo).

Disparada apos o onboarding completar — 1 task por target (cliente + inspiracoes).
"""
from __future__ import annotations

import logging
from typing import Optional

from celery.exceptions import SoftTimeLimitExceeded

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=2,
    soft_time_limit=900,   # 15 min
    time_limit=1200,       # 20 min hard kill
    name="social.extract_creator_profile",
)
def extract_creator_profile_task(
    self,
    handle: str,
    platform: str,
    kind: str = "inspiration",
    posts_count: int = 10,
):
    """Background task: extrai perfil de um creator e grava no vault.

    Idempotente — se um creator ja foi extraido, sobrescreve com versao mais nova.
    Cada chamada gera _meta.json com job_id = celery task id para o frontend
    correlacionar com a UI.
    """
    job_id = self.request.id[:8] if self.request and self.request.id else None
    logger.info(
        f"[social_task:{job_id}] start handle={handle} platform={platform} "
        f"kind={kind} posts={posts_count}"
    )

    try:
        # Import lazy para evitar custo no boot do worker
        from app.services.social.creator_extractor import extract_creator_profile

        meta = extract_creator_profile(
            handle=handle,
            platform=platform,
            kind=kind,
            posts_count=posts_count,
            job_id=job_id,
        )
        return {
            "handle": meta.handle,
            "platform": meta.platform,
            "kind": meta.kind,
            "status": meta.status,
            "posts_done": meta.posts_done,
            "posts_total": meta.posts_total,
            "job_id": meta.job_id,
            "error": meta.last_error,
        }

    except SoftTimeLimitExceeded:
        logger.error(f"[social_task:{job_id}] soft timeout para {handle}")
        try:
            from app.services.social.markdown_writer import read_meta, write_meta
            meta = read_meta(handle)
            if meta:
                meta.status = "failed"
                meta.last_error = "Timeout durante extracao"
                write_meta(meta)
        except Exception:
            pass
        return {"status": "failed", "handle": handle, "error": "timeout"}

    except Exception as e:
        logger.exception(f"[social_task:{job_id}] erro para {handle}: {e}")
        try:
            raise self.retry(exc=e, countdown=120)
        except self.MaxRetriesExceededError:
            return {"status": "failed", "handle": handle, "error": str(e)[:200]}


@celery_app.task(
    bind=True,
    max_retries=2,
    soft_time_limit=900,
    time_limit=1200,
    name="social.extract_video_reference",
)
def extract_video_reference_task(
    self,
    url: str,
    label: str = "",
    platform: str = "unknown",
    kind: str = "inspiration",
):
    """Background task: extrai estilo de uma URL de video avulsa."""
    job_id = self.request.id[:8] if self.request and self.request.id else None
    logger.info(
        f"[social_video_task:{job_id}] start url={url[:120]} platform={platform} kind={kind}"
    )

    try:
        from app.services.social.creator_extractor import extract_video_reference

        meta = extract_video_reference(
            url=url,
            label=label,
            platform=platform,
            kind=kind,
            job_id=job_id,
        )
        return {
            "handle": meta.handle,
            "platform": meta.platform,
            "kind": meta.kind,
            "status": meta.status,
            "posts_done": meta.posts_done,
            "posts_total": meta.posts_total,
            "job_id": meta.job_id,
            "error": meta.last_error,
        }

    except SoftTimeLimitExceeded:
        logger.error(f"[social_video_task:{job_id}] soft timeout para {url[:120]}")
        return {"status": "failed", "url": url, "error": "timeout"}

    except Exception as e:
        logger.exception(f"[social_video_task:{job_id}] erro para {url[:120]}: {e}")
        try:
            raise self.retry(exc=e, countdown=120)
        except self.MaxRetriesExceededError:
            return {"status": "failed", "url": url, "error": str(e)[:200]}


def enqueue_extractions(targets: list, posts_count: int = 10) -> list:
    """Helper para disparar varios extracts em paralelo.

    targets: lista de dicts {handle, platform, kind}
    """
    job_ids = []
    for t in targets:
        try:
            r = extract_creator_profile_task.apply_async(
                kwargs={
                    "handle": t["handle"],
                    "platform": t.get("platform", "unknown"),
                    "kind": t.get("kind", "inspiration"),
                    "posts_count": posts_count,
                },
                priority=5,
            )
            job_ids.append({
                "handle": t["handle"],
                "platform": t.get("platform", "unknown"),
                "kind": t.get("kind", "inspiration"),
                "job_id": r.id,
            })
        except Exception as e:
            logger.error(f"Falha ao enfileirar extracao de {t.get('handle')}: {e}")
    return job_ids
