from fastapi import APIRouter, Depends, Query
from app.core.database import get_supabase
from app.core.auth import verify_api_key
from app.schemas.message import MessageStatusUpdate, ManualSendRequest
from app.services.webhook_dispatcher import process_queue_batch

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/next-batch")
async def get_next_batch(batch_size: int = Query(5, ge=1, le=20), _=Depends(verify_api_key)):
    """n8n chama este endpoint para processar a fila de mensagens."""
    results = await process_queue_batch(batch_size)
    return {"processed": len(results), "results": results}


@router.get("/queue")
async def list_queue(
    status: str | None = None,
    campaign_id: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    _=Depends(verify_api_key),
):
    db = get_supabase()
    query = db.table("message_queue").select("*", count="exact")
    if status:
        query = query.eq("status", status)
    if campaign_id:
        query = query.eq("campaign_id", campaign_id)

    offset = (page - 1) * per_page
    query = query.order("created_at", desc=True).range(offset, offset + per_page - 1)
    result = query.execute()

    return {"total": result.count or 0, "messages": result.data or []}


@router.patch("/{queue_id}/status")
async def update_message_status(queue_id: str, data: MessageStatusUpdate, _=Depends(verify_api_key)):
    db = get_supabase()

    updates = {"status": data.status}
    if data.external_message_id:
        updates["external_message_id"] = data.external_message_id
    if data.error_message:
        updates["last_error"] = data.error_message

    # Update queue
    db.table("message_queue").update(updates).eq("id", queue_id).execute()

    # Update message_log if exists
    if data.status in ("delivered", "read", "failed"):
        log_updates = {"status": data.status}
        if data.status == "delivered":
            log_updates["delivered_at"] = "now()"
        elif data.status == "read":
            log_updates["read_at"] = "now()"
        elif data.status == "failed":
            log_updates["failed_at"] = "now()"
            log_updates["error_message"] = data.error_message

        db.table("message_log").update(log_updates).eq("queue_id", queue_id).execute()

    return {"updated": queue_id, "status": data.status}


@router.post("/send-manual")
async def send_manual(data: ManualSendRequest, _=Depends(verify_api_key)):
    """Envia mensagem manual (fora de campanha)."""
    db = get_supabase()

    db.table("message_queue").insert({
        "lead_id": data.lead_id,
        "whatsapp_to": data.whatsapp_to,
        "message_body": data.message_body,
        "status": "pending",
        "priority": 10,  # manual messages get higher priority
    }).execute()

    return {"queued": True, "lead_id": data.lead_id}


@router.get("/log")
async def message_log(
    lead_id: str | None = None,
    campaign_id: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    _=Depends(verify_api_key),
):
    db = get_supabase()
    query = db.table("message_log").select("*", count="exact")
    if lead_id:
        query = query.eq("lead_id", lead_id)
    if campaign_id:
        query = query.eq("campaign_id", campaign_id)

    offset = (page - 1) * per_page
    query = query.order("sent_at", desc=True).range(offset, offset + per_page - 1)
    result = query.execute()

    return {"total": result.count or 0, "messages": result.data or []}
