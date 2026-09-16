import httpx
import hashlib
import hmac
import json
from datetime import datetime, timezone
from app.core.config import get_settings
from app.core.database import get_supabase


async def dispatch_message(
    queue_id: str,
    to: str,
    message_body: str,
    from_number: str,
    lead_id: str,
    campaign_id: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Envia mensagem via POST para o webhook configurado.

    Body enviado:
    {
        "to": "5521999991639",
        "from": "5511999998888",
        "message": "Olá! Tudo bem? ...",
        "lead_id": "uuid",
        "campaign_id": "uuid",
        "queue_id": "uuid",
        "metadata": {...},
        "timestamp": "2026-03-06T12:00:00Z"
    }
    """
    settings = get_settings()

    if not settings.dispatch_webhook_url:
        return {"success": False, "error": "DISPATCH_WEBHOOK_URL não configurada"}

    payload = {
        "to": to,
        "from": from_number,
        "message": message_body,
        "lead_id": lead_id,
        "campaign_id": campaign_id,
        "queue_id": queue_id,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    headers = {"Content-Type": "application/json"}

    # Assinar payload com HMAC se secret configurado
    if settings.dispatch_webhook_secret:
        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        signature = hmac.new(
            settings.dispatch_webhook_secret.encode("utf-8"),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        headers["X-Webhook-Signature"] = f"sha256={signature}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.dispatch_webhook_url,
                json=payload,
                headers=headers,
            )

        if response.status_code in (200, 201, 202):
            response_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            return {
                "success": True,
                "status_code": response.status_code,
                "external_message_id": response_data.get("message_id", response_data.get("id")),
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text[:200],
            }
    except httpx.TimeoutException:
        return {"success": False, "error": "Timeout ao conectar no webhook"}
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}


async def process_queue_batch(batch_size: int = 5) -> list[dict]:
    """Processa um lote da fila de mensagens.

    Retorna lista de resultados com status de cada envio.
    """
    db = get_supabase()
    from app.services.number_rotation import select_available_number, record_send

    # Buscar mensagens pendentes
    now = datetime.now(timezone.utc).isoformat()
    result = db.table("message_queue").select("*").eq(
        "status", "pending"
    ).lte(
        "scheduled_for", now
    ).order(
        "priority", desc=True
    ).order(
        "created_at", desc=False
    ).limit(batch_size).execute()

    if not result.data:
        return []

    results = []
    for msg in result.data:
        # Selecionar número remetente
        number = await select_available_number()
        if not number:
            results.append({"queue_id": msg["id"], "status": "no_number_available"})
            continue

        # Marcar como processing
        db.table("message_queue").update({
            "status": "processing",
            "assigned_number_id": number["id"],
        }).eq("id", msg["id"]).execute()

        # Disparar webhook
        dispatch_result = await dispatch_message(
            queue_id=msg["id"],
            to=msg["whatsapp_to"],
            message_body=msg["message_body"],
            from_number=number["phone_number"],
            lead_id=msg["lead_id"],
            campaign_id=msg.get("campaign_id"),
        )

        if dispatch_result["success"]:
            # Atualizar fila
            db.table("message_queue").update({
                "status": "sent",
                "processed_at": now,
            }).eq("id", msg["id"]).execute()

            # Criar log
            db.table("message_log").insert({
                "queue_id": msg["id"],
                "campaign_id": msg.get("campaign_id"),
                "lead_id": msg["lead_id"],
                "whatsapp_from": number["phone_number"],
                "whatsapp_to": msg["whatsapp_to"],
                "message_body": msg["message_body"],
                "external_message_id": dispatch_result.get("external_message_id"),
                "status": "sent",
            }).execute()

            # Atualizar campaign_lead status
            if msg.get("campaign_lead_id"):
                db.table("campaign_leads").update({
                    "status": "sent",
                    "sent_at": now,
                }).eq("id", msg["campaign_lead_id"]).execute()

            # Atualizar lead outreach_status
            db.table("leads").update({
                "outreach_status": "contacted",
            }).eq("id", msg["lead_id"]).execute()

            await record_send(number["id"], success=True)
        else:
            attempts = msg.get("attempts", 0) + 1
            max_attempts = msg.get("max_attempts", 3)

            update_data = {
                "attempts": attempts,
                "last_error": dispatch_result.get("error"),
            }

            if attempts >= max_attempts:
                update_data["status"] = "failed"
            else:
                update_data["status"] = "pending"

            db.table("message_queue").update(update_data).eq("id", msg["id"]).execute()
            await record_send(number["id"], success=False, error=dispatch_result.get("error"))

        results.append({
            "queue_id": msg["id"],
            "status": "sent" if dispatch_result["success"] else "failed",
            "error": dispatch_result.get("error"),
        })

    return results
