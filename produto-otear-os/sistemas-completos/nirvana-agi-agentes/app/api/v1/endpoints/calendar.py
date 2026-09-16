import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.core.security import verify_supabase_token
from app.core.supabase import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)


class CalendarEntryCreate(BaseModel):
    title: str
    content_type: Optional[str] = None   # 'video', 'carousel', 'reel', 'post'
    platform: Optional[str] = None       # 'instagram', 'tiktok', 'youtube'
    scheduled_at: Optional[str] = None   # ISO datetime string
    notes: Optional[str] = None
    asset_id: Optional[str] = None


class CalendarEntryUpdate(BaseModel):
    title: Optional[str] = None
    content_type: Optional[str] = None
    platform: Optional[str] = None
    scheduled_at: Optional[str] = None
    status: Optional[str] = None         # 'planned', 'created', 'published'
    notes: Optional[str] = None
    asset_id: Optional[str] = None


@router.get("")
async def list_calendar(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    user_data: dict = Depends(verify_supabase_token),
):
    """Lista entradas do calendário editorial do usuário."""
    client = get_supabase()
    query = (
        client.table("content_calendar")
        .select("*, content_assets(type, url, thumbnail_url)")
        .eq("user_id", user_data["user_id"])
        .order("scheduled_at", desc=False)
    )

    if month and year:
        start = f"{year}-{month:02d}-01"
        end_month = month + 1 if month < 12 else 1
        end_year = year if month < 12 else year + 1
        end = f"{end_year}-{end_month:02d}-01"
        query = query.gte("scheduled_at", start).lt("scheduled_at", end)

    result = query.execute()
    return {"entries": result.data or []}


@router.post("")
async def create_calendar_entry(
    body: CalendarEntryCreate,
    user_data: dict = Depends(verify_supabase_token),
):
    """Cria uma nova entrada no calendário editorial."""
    client = get_supabase()
    payload = {
        "user_id": user_data["user_id"],
        "title": body.title,
        "content_type": body.content_type,
        "platform": body.platform,
        "scheduled_at": body.scheduled_at,
        "notes": body.notes,
        "asset_id": body.asset_id,
        "status": "planned",
    }
    result = client.table("content_calendar").insert(payload).execute()
    return {"message": "Entrada criada", "entry": result.data[0] if result.data else {}}


@router.put("/{entry_id}")
async def update_calendar_entry(
    entry_id: str,
    body: CalendarEntryUpdate,
    user_data: dict = Depends(verify_supabase_token),
):
    """Atualiza uma entrada do calendário (status, data, etc.)."""
    client = get_supabase()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    result = (
        client.table("content_calendar")
        .update(updates)
        .eq("id", entry_id)
        .eq("user_id", user_data["user_id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return {"message": "Entrada atualizada", "entry": result.data[0]}


@router.delete("/{entry_id}")
async def delete_calendar_entry(
    entry_id: str,
    user_data: dict = Depends(verify_supabase_token),
):
    """Remove uma entrada do calendário."""
    client = get_supabase()
    result = (
        client.table("content_calendar")
        .delete()
        .eq("id", entry_id)
        .eq("user_id", user_data["user_id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return {"message": "Entrada removida"}
