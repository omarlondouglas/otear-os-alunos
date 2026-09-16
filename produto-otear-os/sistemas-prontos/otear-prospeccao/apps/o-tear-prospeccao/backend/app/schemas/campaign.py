from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime


class MessageTemplateCreate(BaseModel):
    variant_name: str = "A"
    template_body: str
    weight: int = 100


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_filters: dict = {}
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    time_window_start: time = time(9, 0)
    time_window_end: time = time(18, 0)
    daily_limit: int = 50
    min_delay_seconds: int = 45
    max_delay_seconds: int = 120
    messages: list[MessageTemplateCreate] = []


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_filters: Optional[dict] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    time_window_start: Optional[time] = None
    time_window_end: Optional[time] = None
    daily_limit: Optional[int] = None
    min_delay_seconds: Optional[int] = None
    max_delay_seconds: Optional[int] = None


class CampaignResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    target_filters: dict = {}
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None
    daily_limit: int = 50
    min_delay_seconds: int = 45
    max_delay_seconds: int = 120
    total_leads: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_replied: int = 0
    total_failed: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    messages: list[dict] = []


class CampaignStatsResponse(BaseModel):
    campaign_id: str
    name: str
    status: str
    total_leads: int
    sent: int
    delivered: int
    read: int
    replied: int
    failed: int
    delivery_rate: float
    read_rate: float
    reply_rate: float
    variants: list[dict] = []
