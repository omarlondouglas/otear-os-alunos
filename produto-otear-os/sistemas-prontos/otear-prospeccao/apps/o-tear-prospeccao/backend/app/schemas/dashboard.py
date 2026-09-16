from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_leads: int = 0
    leads_hot: int = 0
    leads_warm: int = 0
    leads_cold: int = 0
    total_campaigns: int = 0
    active_campaigns: int = 0
    messages_sent_today: int = 0
    messages_sent_week: int = 0
    messages_sent_month: int = 0
    delivery_rate: float = 0.0
    read_rate: float = 0.0
    reply_rate: float = 0.0
    unread_conversations: int = 0
    numbers_active: int = 0
    numbers_warming_up: int = 0


class DailySummary(BaseModel):
    date: str
    sent: int = 0
    delivered: int = 0
    read: int = 0
    replied: int = 0
    failed: int = 0
    active_campaigns: int = 0
    active_numbers: int = 0
    opt_outs: int = 0


class FunnelData(BaseModel):
    imported: int = 0
    queued: int = 0
    contacted: int = 0
    replied: int = 0
    converted: int = 0
