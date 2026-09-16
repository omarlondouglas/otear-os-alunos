from fastapi import APIRouter, Depends, Query
from app.core.database import get_supabase
from app.core.auth import verify_api_key
from app.schemas.message import ReplyRequest

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    _=Depends(verify_api_key),
):
    db = get_supabase()
    query = db.table("conversations").select(
        "*, leads!inner(name, category, instagram_handle)", count="exact"
    )

    if unread_only:
        query = query.gt("unread_count", 0)

    query = query.eq("is_archived", False).order("last_message_at", desc=True)
    offset = (page - 1) * per_page
    query = query.range(offset, offset + per_page - 1)
    result = query.execute()

    conversations = []
    for conv in (result.data or []):
        lead = conv.pop("leads", {})
        conv["lead_name"] = lead.get("name", "")
        conversations.append(conv)

    return {"total": result.count or 0, "conversations": conversations}


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    _=Depends(verify_api_key),
):
    db = get_supabase()
    offset = (page - 1) * per_page
    result = db.table("conversation_messages").select("*", count="exact").eq(
        "conversation_id", conversation_id
    ).order("created_at", desc=False).range(offset, offset + per_page - 1).execute()

    # Mark as read
    db.table("conversations").update({"unread_count": 0}).eq("id", conversation_id).execute()

    return {"total": result.count or 0, "messages": result.data or []}


@router.post("/{conversation_id}/reply")
async def reply_to_conversation(conversation_id: str, data: ReplyRequest, _=Depends(verify_api_key)):
    db = get_supabase()

    # Get conversation to find lead's WhatsApp
    conv = db.table("conversations").select("*").eq("id", conversation_id).single().execute()
    if not conv.data:
        return {"error": "Conversa não encontrada"}

    # Save outbound message
    db.table("conversation_messages").insert({
        "conversation_id": conversation_id,
        "direction": "outbound",
        "message_body": data.message_body,
    }).execute()

    # Update conversation
    db.table("conversations").update({
        "last_message_at": "now()",
        "last_message_preview": data.message_body[:100],
    }).eq("id", conversation_id).execute()

    # Queue for sending
    db.table("message_queue").insert({
        "lead_id": conv.data["lead_id"],
        "whatsapp_to": conv.data["whatsapp_number"],
        "message_body": data.message_body,
        "status": "pending",
        "priority": 10,
    }).execute()

    return {"sent": True, "conversation_id": conversation_id}


@router.patch("/{conversation_id}/archive")
async def archive_conversation(conversation_id: str, _=Depends(verify_api_key)):
    db = get_supabase()
    db.table("conversations").update({"is_archived": True}).eq("id", conversation_id).execute()
    return {"archived": conversation_id}
