from fastapi import APIRouter, Depends
from app.core.database import get_supabase
from app.core.auth import verify_api_key
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.services.campaign_engine import activate_campaign, pause_campaign

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("")
async def create_campaign(data: CampaignCreate, _=Depends(verify_api_key)):
    db = get_supabase()

    campaign_data = {
        "name": data.name,
        "description": data.description,
        "target_filters": data.target_filters,
        "start_date": data.start_date.isoformat() if data.start_date else None,
        "end_date": data.end_date.isoformat() if data.end_date else None,
        "time_window_start": data.time_window_start.isoformat() if data.time_window_start else "09:00:00",
        "time_window_end": data.time_window_end.isoformat() if data.time_window_end else "18:00:00",
        "daily_limit": data.daily_limit,
        "min_delay_seconds": data.min_delay_seconds,
        "max_delay_seconds": data.max_delay_seconds,
        "status": "draft",
    }

    result = db.table("campaigns").insert(campaign_data).execute()
    campaign = result.data[0]

    # Criar templates
    for msg in data.messages:
        db.table("campaign_messages").insert({
            "campaign_id": campaign["id"],
            "variant_name": msg.variant_name,
            "template_body": msg.template_body,
            "weight": msg.weight,
        }).execute()

    return campaign


@router.get("")
async def list_campaigns(status: str | None = None, _=Depends(verify_api_key)):
    db = get_supabase()
    query = db.table("campaigns").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    result = query.execute()
    return result.data or []


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, _=Depends(verify_api_key)):
    db = get_supabase()
    campaign = db.table("campaigns").select("*").eq("id", campaign_id).single().execute()
    messages = db.table("campaign_messages").select("*").eq("campaign_id", campaign_id).execute()

    data = campaign.data
    data["messages"] = messages.data or []
    return data


@router.patch("/{campaign_id}")
async def update_campaign(campaign_id: str, data: CampaignUpdate, _=Depends(verify_api_key)):
    db = get_supabase()
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if "start_date" in updates and updates["start_date"]:
        updates["start_date"] = updates["start_date"].isoformat()
    if "end_date" in updates and updates["end_date"]:
        updates["end_date"] = updates["end_date"].isoformat()
    if "time_window_start" in updates and updates["time_window_start"]:
        updates["time_window_start"] = updates["time_window_start"].isoformat()
    if "time_window_end" in updates and updates["time_window_end"]:
        updates["time_window_end"] = updates["time_window_end"].isoformat()

    result = db.table("campaigns").update(updates).eq("id", campaign_id).execute()
    return result.data[0] if result.data else {"error": "Campanha não encontrada"}


@router.post("/{campaign_id}/activate")
async def activate(campaign_id: str, _=Depends(verify_api_key)):
    return await activate_campaign(campaign_id)


@router.post("/{campaign_id}/pause")
async def pause(campaign_id: str, _=Depends(verify_api_key)):
    return await pause_campaign(campaign_id)


@router.get("/{campaign_id}/stats")
async def campaign_stats(campaign_id: str, _=Depends(verify_api_key)):
    db = get_supabase()
    campaign = db.table("campaigns").select("*").eq("id", campaign_id).single().execute()

    if not campaign.data:
        return {"error": "Campanha não encontrada"}

    c = campaign.data
    total = c.get("total_sent", 0) or 1

    variants = db.table("campaign_messages").select("*").eq("campaign_id", campaign_id).execute()

    return {
        "campaign_id": campaign_id,
        "name": c["name"],
        "status": c["status"],
        "total_leads": c.get("total_leads", 0),
        "sent": c.get("total_sent", 0),
        "delivered": c.get("total_delivered", 0),
        "read": c.get("total_read", 0),
        "replied": c.get("total_replied", 0),
        "failed": c.get("total_failed", 0),
        "delivery_rate": round((c.get("total_delivered", 0) / total) * 100, 1) if total else 0,
        "read_rate": round((c.get("total_read", 0) / total) * 100, 1) if total else 0,
        "reply_rate": round((c.get("total_replied", 0) / total) * 100, 1) if total else 0,
        "variants": variants.data or [],
    }


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str, _=Depends(verify_api_key)):
    db = get_supabase()
    # Cancel pending messages first
    db.table("message_queue").update(
        {"status": "cancelled"}
    ).eq("campaign_id", campaign_id).eq("status", "pending").execute()

    db.table("campaigns").delete().eq("id", campaign_id).execute()
    return {"deleted": campaign_id}
