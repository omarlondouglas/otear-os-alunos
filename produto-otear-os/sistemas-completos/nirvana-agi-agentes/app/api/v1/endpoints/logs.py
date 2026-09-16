from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import redis
import json
import os

from app.core.security_admin import verify_admin_access

router = APIRouter()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class LogEntry(BaseModel):
    id: str
    timestamp: str
    agent: str
    message: str
    type: str
    metadata: Optional[dict] = None


class LogsResponse(BaseModel):
    logs: List[LogEntry]
    total: int


def get_redis_client():
    """Get Redis client for log storage."""
    try:
        return redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        return None


@router.get("", response_model=LogsResponse)
async def get_logs(
    limit: int = Query(100, ge=1, le=500),
    agent: Optional[str] = Query(None),
    _: bool = Depends(verify_admin_access),
):
    """Get agent conversation logs (admin only)."""
    try:
        client = get_redis_client()
        if not client:
            return LogsResponse(logs=[], total=0)

        raw_logs = client.lrange("agent_logs", 0, limit - 1)
        logs = []

        for raw in raw_logs:
            try:
                log_data = json.loads(raw)
                logs.append(LogEntry(**log_data))
            except (json.JSONDecodeError, ValueError):
                continue

        if agent:
            logs = [log for log in logs if log.agent.lower() == agent.lower()]

        return LogsResponse(logs=logs, total=len(logs))

    except Exception:
        return LogsResponse(logs=[], total=0)


def get_demo_logs() -> List[LogEntry]:
    """Return demo logs for testing."""
    base_time = datetime.now().isoformat()
    return [
        LogEntry(id="demo-1", timestamp=base_time, agent="Jobs",
                 message="Olá! Como posso ajudar você hoje?", type="agent"),
        LogEntry(id="demo-2", timestamp=base_time, agent="User",
                 message="Quero criar um vídeo promocional", type="user"),
        LogEntry(id="demo-3", timestamp=base_time, agent="Jobs",
                 message="Perfeito! Vou acionar o Nolan para ajudar.", type="agent"),
        LogEntry(id="demo-4", timestamp=base_time, agent="Nolan",
                 message="Analisando requisitos... Sugestão: vídeo de 30s com transições suaves.", type="agent"),
    ]


async def add_log_entry(
    agent: str,
    message: str,
    log_type: str = "agent",
    metadata: Optional[dict] = None,
    **_: dict,
):
    """Utility function to add a log entry."""
    try:
        client = get_redis_client()
        if not client:
            return False

        entry = {
            "id": f"log-{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "message": message,
            "type": log_type,
        }
        if metadata:
            entry["metadata"] = metadata

        client.lpush("agent_logs", json.dumps(entry))
        client.ltrim("agent_logs", 0, 999)
        return True
    except Exception:
        return False
