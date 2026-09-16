from fastapi import APIRouter, Depends, Request
from app.core.database import get_supabase
from app.core.auth import verify_webhook_secret
from app.services.opt_out_service import check_opt_out, register_opt_out

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/message-received")
async def message_received(request: Request, _=Depends(verify_webhook_secret)):
    """Recebe mensagem de resposta de um lead (via n8n/Evolution webhook)."""
    body = await request.json()

    phone = body.get("from", body.get("phone", ""))
    message = body.get("message", body.get("text", body.get("body", "")))
    message_id = body.get("message_id", body.get("id", ""))

    if not phone or not message:
        return {"error": "phone e message são obrigatórios"}

    db = get_supabase()

    # Find lead by WhatsApp number
    lead_result = db.table("leads").select("id, name").eq("whatsapp_number", phone).execute()
    lead = lead_result.data[0] if lead_result.data else None
    lead_id = lead["id"] if lead else None

    # Check opt-out
    if await check_opt_out(message):
        await register_opt_out(phone, lead_id, f"Keyword detectada: '{message}'")
        return {"opt_out": True, "phone": phone}

    # Find or create conversation
    conv_result = db.table("conversations").select("*").eq("whatsapp_number", phone).execute()

    if conv_result.data:
        conv = conv_result.data[0]
        db.table("conversations").update({
            "last_message_at": "now()",
            "last_message_preview": message[:100],
            "unread_count": conv["unread_count"] + 1,
        }).eq("id", conv["id"]).execute()
        conv_id = conv["id"]
    else:
        new_conv = db.table("conversations").insert({
            "lead_id": lead_id,
            "whatsapp_number": phone,
            "last_message_at": "now()",
            "last_message_preview": message[:100],
            "unread_count": 1,
        }).execute()
        conv_id = new_conv.data[0]["id"]

    # Save message
    db.table("conversation_messages").insert({
        "conversation_id": conv_id,
        "direction": "inbound",
        "message_body": message,
        "external_message_id": message_id,
    }).execute()

    # Update lead status
    if lead_id:
        db.table("leads").update({"outreach_status": "replied"}).eq("id", lead_id).execute()

    return {"received": True, "conversation_id": conv_id}


@router.post("/message-status")
async def message_status(request: Request, _=Depends(verify_webhook_secret)):
    """Recebe atualização de status de mensagem (delivered, read)."""
    body = await request.json()

    message_id = body.get("message_id", body.get("id", ""))
    status = body.get("status", "")

    if not message_id or not status:
        return {"error": "message_id e status são obrigatórios"}

    db = get_supabase()

    updates = {"status": status}
    if status == "delivered":
        updates["delivered_at"] = "now()"
    elif status == "read":
        updates["read_at"] = "now()"

    db.table("message_log").update(updates).eq("external_message_id", message_id).execute()

    return {"updated": message_id, "status": status}
