from datetime import datetime, timezone, timedelta
from app.core.database import get_supabase


async def get_dashboard_stats() -> dict:
    db = get_supabase()

    # Leads counts
    leads = db.table("leads").select("score_classification", count="exact").execute()
    total_leads = leads.count or 0
    leads_by_class = {"hot": 0, "warm": 0, "cold": 0}
    for l in (leads.data or []):
        cls = l.get("score_classification")
        if cls in leads_by_class:
            leads_by_class[cls] += 1

    # Campaigns
    campaigns = db.table("campaigns").select("status", count="exact").execute()
    total_campaigns = campaigns.count or 0
    active_campaigns = sum(1 for c in (campaigns.data or []) if c["status"] == "active")

    # Messages today
    today = datetime.now(timezone.utc).date().isoformat()
    msgs_today = db.table("message_log").select("status", count="exact").gte(
        "sent_at", today
    ).execute()
    messages_sent_today = msgs_today.count or 0

    # Messages this week
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    msgs_week = db.table("message_log").select("id", count="exact").gte("sent_at", week_ago).execute()

    # Messages this month
    month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    msgs_month = db.table("message_log").select("id", count="exact").gte("sent_at", month_ago).execute()

    # Rates
    all_msgs = db.table("message_log").select("status").execute()
    total_msgs = len(all_msgs.data or [])
    if total_msgs > 0:
        delivered = sum(1 for m in all_msgs.data if m["status"] in ("delivered", "read"))
        read = sum(1 for m in all_msgs.data if m["status"] == "read")
        delivery_rate = (delivered / total_msgs) * 100
        read_rate = (read / total_msgs) * 100
    else:
        delivery_rate = 0.0
        read_rate = 0.0

    # Reply rate
    replied_leads = db.table("leads").select("id", count="exact").eq(
        "outreach_status", "replied"
    ).execute()
    contacted_leads = db.table("leads").select("id", count="exact").in_(
        "outreach_status", ["contacted", "replied", "converted"]
    ).execute()
    contacted_count = contacted_leads.count or 0
    reply_rate = ((replied_leads.count or 0) / contacted_count * 100) if contacted_count else 0.0

    # Conversations
    unread = db.table("conversations").select("id", count="exact").gt("unread_count", 0).execute()

    # Numbers
    numbers = db.table("whatsapp_numbers").select("status").execute()
    active_nums = sum(1 for n in (numbers.data or []) if n["status"] == "active")
    warming_nums = sum(1 for n in (numbers.data or []) if n["status"] == "warming_up")

    return {
        "total_leads": total_leads,
        "leads_hot": leads_by_class["hot"],
        "leads_warm": leads_by_class["warm"],
        "leads_cold": leads_by_class["cold"],
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "messages_sent_today": messages_sent_today,
        "messages_sent_week": msgs_week.count or 0,
        "messages_sent_month": msgs_month.count or 0,
        "delivery_rate": round(delivery_rate, 1),
        "read_rate": round(read_rate, 1),
        "reply_rate": round(reply_rate, 1),
        "unread_conversations": unread.count or 0,
        "numbers_active": active_nums,
        "numbers_warming_up": warming_nums,
    }


async def get_daily_summary() -> dict:
    db = get_supabase()
    today = datetime.now(timezone.utc).date().isoformat()

    msgs = db.table("message_log").select("status").gte("sent_at", today).execute()
    data = msgs.data or []

    campaigns = db.table("campaigns").select("id", count="exact").eq("status", "active").execute()
    numbers = db.table("whatsapp_numbers").select("id", count="exact").eq("status", "active").execute()
    opt_outs = db.table("opt_outs").select("id", count="exact").gte("opted_out_at", today).execute()

    return {
        "date": today,
        "sent": len(data),
        "delivered": sum(1 for m in data if m["status"] in ("delivered", "read")),
        "read": sum(1 for m in data if m["status"] == "read"),
        "replied": 0,
        "failed": sum(1 for m in data if m["status"] == "failed"),
        "active_campaigns": campaigns.count or 0,
        "active_numbers": numbers.count or 0,
        "opt_outs": opt_outs.count or 0,
    }


async def get_funnel_data() -> dict:
    db = get_supabase()

    statuses = ["imported", "queued", "contacted", "replied", "converted"]
    result = {}
    for status in statuses:
        count = db.table("leads").select("id", count="exact").eq("outreach_status", status).execute()
        result[status] = count.count or 0

    return result
