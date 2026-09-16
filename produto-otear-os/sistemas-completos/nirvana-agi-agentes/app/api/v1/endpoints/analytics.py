import logging
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from app.core.security import verify_supabase_token
from app.core.supabase import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Período em dias para análise"),
    user_data: dict = Depends(verify_supabase_token),
):
    """Retorna resumo de uso e conteúdos criados pelo usuário."""
    client = get_supabase()
    user_id = user_data["user_id"]
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()

    # Total de ativos por tipo
    assets_result = (
        client.table("content_assets")
        .select("type, created_at")
        .eq("user_id", user_id)
        .execute()
    )
    assets = assets_result.data or []

    by_type: dict = {}
    recent_assets = []
    for asset in assets:
        t = asset.get("type", "other")
        by_type[t] = by_type.get(t, 0) + 1
        if asset.get("created_at", "") >= since:
            recent_assets.append(asset)

    # Total de ações no período
    actions_result = (
        client.table("usage_analytics")
        .select("action_type, created_at")
        .eq("user_id", user_id)
        .gte("created_at", since)
        .execute()
    )
    actions = actions_result.data or []

    actions_by_type: dict = {}
    for action in actions:
        at = action.get("action_type", "other")
        actions_by_type[at] = actions_by_type.get(at, 0) + 1

    # Últimos 10 ativos criados
    latest_result = (
        client.table("content_assets")
        .select("id, type, title, url, thumbnail_url, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    # Calendário: próximas postagens planejadas
    upcoming_result = (
        client.table("content_calendar")
        .select("id, title, content_type, platform, scheduled_at, status")
        .eq("user_id", user_id)
        .eq("status", "planned")
        .gte("scheduled_at", datetime.utcnow().isoformat())
        .order("scheduled_at")
        .limit(5)
        .execute()
    )

    return {
        "period_days": days,
        "total_assets": len(assets),
        "assets_this_period": len(recent_assets),
        "by_type": by_type,
        "actions_this_period": len(actions),
        "actions_by_type": actions_by_type,
        "latest_assets": latest_result.data or [],
        "upcoming_scheduled": upcoming_result.data or [],
    }
