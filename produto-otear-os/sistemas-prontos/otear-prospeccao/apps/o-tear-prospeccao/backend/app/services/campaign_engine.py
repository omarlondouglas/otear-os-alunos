import random
import uuid
from datetime import datetime, timezone, timedelta
from app.core.database import get_supabase
from app.services.template_engine import resolve_template, apply_micro_variations


async def activate_campaign(campaign_id: str) -> dict:
    """Ativa uma campanha: resolve filtros, cria campaign_leads, enfileira mensagens."""
    db = get_supabase()

    # Buscar campanha
    campaign = db.table("campaigns").select("*").eq("id", campaign_id).single().execute()
    if not campaign.data:
        return {"error": "Campanha não encontrada"}

    c = campaign.data
    if c["status"] not in ("draft", "paused"):
        return {"error": f"Campanha com status '{c['status']}' não pode ser ativada"}

    # Buscar templates
    templates = db.table("campaign_messages").select("*").eq(
        "campaign_id", campaign_id
    ).execute()

    if not templates.data:
        return {"error": "Campanha sem templates de mensagem"}

    # Buscar leads com filtros
    filters = c.get("target_filters", {})
    query = db.table("leads").select("*").neq("outreach_status", "opted_out").neq(
        "outreach_status", "archived"
    )

    if filters.get("classification"):
        classifications = filters["classification"]
        if isinstance(classifications, list):
            query = query.in_("score_classification", classifications)
        else:
            query = query.eq("score_classification", classifications)

    if filters.get("min_score"):
        query = query.gte("score_total", filters["min_score"])

    if filters.get("tags"):
        query = query.overlaps("tags", filters["tags"])

    if filters.get("outreach_status"):
        query = query.eq("outreach_status", filters["outreach_status"])
    else:
        query = query.eq("outreach_status", "imported")

    leads = query.execute()

    if not leads.data:
        return {"error": "Nenhum lead encontra os filtros da campanha"}

    # Filtrar leads sem WhatsApp
    valid_leads = [l for l in leads.data if l.get("whatsapp_number")]
    # Check opt-outs
    opted_out = db.table("opt_outs").select("phone_number").execute()
    opted_out_phones = {o["phone_number"] for o in (opted_out.data or [])}
    valid_leads = [l for l in valid_leads if l["whatsapp_number"] not in opted_out_phones]

    if not valid_leads:
        return {"error": "Nenhum lead com WhatsApp válido encontrado"}

    # Selecionar variante por peso
    total_weight = sum(t["weight"] for t in templates.data)
    enqueued = 0
    now = datetime.now(timezone.utc)
    daily_limit = c.get("daily_limit", 50)

    for i, lead in enumerate(valid_leads):
        # Selecionar variante A/B
        variant = _select_variant(templates.data, total_weight)

        # Resolver template
        message = resolve_template(variant["template_body"], lead)
        message = apply_micro_variations(message)

        # Criar campaign_lead
        cl_id = str(uuid.uuid4())
        db.table("campaign_leads").insert({
            "id": cl_id,
            "campaign_id": campaign_id,
            "lead_id": lead["id"],
            "variant_id": variant["id"],
            "status": "queued",
            "queued_at": now.isoformat(),
        }).execute()

        # Calcular scheduled_for (distribuir ao longo dos dias)
        day_offset = i // daily_limit
        min_delay = c.get("min_delay_seconds", 45)
        max_delay = c.get("max_delay_seconds", 120)
        seconds_offset = (i % daily_limit) * random.randint(min_delay, max_delay)

        scheduled = now + timedelta(days=day_offset, seconds=seconds_offset)

        # Enfileirar mensagem
        db.table("message_queue").insert({
            "campaign_id": campaign_id,
            "campaign_lead_id": cl_id,
            "lead_id": lead["id"],
            "whatsapp_to": lead["whatsapp_number"],
            "message_body": message,
            "status": "pending",
            "scheduled_for": scheduled.isoformat(),
        }).execute()

        enqueued += 1

    # Atualizar campanha
    db.table("campaigns").update({
        "status": "active",
        "total_leads": enqueued,
    }).eq("id", campaign_id).execute()

    return {
        "campaign_id": campaign_id,
        "total_leads": len(valid_leads),
        "enqueued": enqueued,
        "estimated_days": (enqueued // daily_limit) + 1,
    }


async def pause_campaign(campaign_id: str) -> dict:
    """Pausa uma campanha e cancela mensagens pendentes."""
    db = get_supabase()

    db.table("campaigns").update({"status": "paused"}).eq("id", campaign_id).execute()

    # Cancelar mensagens pendentes na fila
    db.table("message_queue").update({
        "status": "cancelled",
    }).eq("campaign_id", campaign_id).eq("status", "pending").execute()

    return {"campaign_id": campaign_id, "status": "paused"}


def _select_variant(templates: list[dict], total_weight: int) -> dict:
    """Seleciona variante baseado nos pesos (A/B testing)."""
    r = random.randint(1, total_weight)
    cumulative = 0
    for t in templates:
        cumulative += t["weight"]
        if r <= cumulative:
            return t
    return templates[0]
