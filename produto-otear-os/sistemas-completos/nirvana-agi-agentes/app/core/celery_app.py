import os
from celery import Celery
import logging

logger = logging.getLogger(__name__)

# Determine Broker URL with fallback to localhost
# Priority: CELERY_BROKER_URL > REDIS_URL > localhost fallback
broker_url = os.environ.get("CELERY_BROKER_URL") or os.environ.get("REDIS_URL") or "redis://localhost:6379/0"
backend_url = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"

# If BROKER is the Docker default but BACKEND looks properly configured (different), use BACKEND as broker too.
if "redis:6379" in broker_url and "redis:6379" not in backend_url:
    broker_url = backend_url

logger.info(f"Celery Broker URL: {broker_url}")
logger.info(f"Celery Backend URL: {backend_url}")

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url,
    include=[
        'app.workers.video_tasks',
        'app.workers.news_digest_task',
        'app.workers.claude_refresh_task',
        'app.workers.social_tasks',
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Configurações de retry para evitar loops infinitos
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    # Limites de tempo para tarefas longas (vídeos de 15-40 min)
    task_soft_time_limit=5400,       # 90 min → levanta SoftTimeLimitExceeded
    task_time_limit=6000,            # 100 min → mata o processo forçadamente
    worker_max_tasks_per_child=10,   # evita vazamento de memória em workers
)
