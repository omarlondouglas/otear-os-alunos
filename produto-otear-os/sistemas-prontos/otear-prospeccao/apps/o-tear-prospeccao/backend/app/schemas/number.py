from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NumberCreate(BaseModel):
    label: str
    phone_number: str
    daily_limit: int = 20


class NumberUpdate(BaseModel):
    label: Optional[str] = None
    status: Optional[str] = None
    daily_limit: Optional[int] = None


class NumberResponse(BaseModel):
    id: str
    label: str
    phone_number: str
    status: str
    warmup_day: int = 0
    daily_limit: int = 20
    current_daily_sent: int = 0
    ban_risk_score: int = 0
    total_sent_today: int = 0
    total_sent_week: int = 0
    total_sent_month: int = 0
    is_available: bool = True
    last_sent_at: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_errors: int = 0
    rest_until: Optional[datetime] = None
    created_at: Optional[datetime] = None


class NumberHealthResponse(BaseModel):
    total_numbers: int
    active: int
    warming_up: int
    resting: int
    banned: int
    total_capacity_today: int
    total_sent_today: int
    numbers: list[NumberResponse]
