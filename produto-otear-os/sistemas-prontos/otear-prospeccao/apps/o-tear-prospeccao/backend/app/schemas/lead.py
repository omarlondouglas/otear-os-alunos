from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class LeadClassification(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class OutreachStatus(str, Enum):
    IMPORTED = "imported"
    QUEUED = "queued"
    CONTACTED = "contacted"
    REPLIED = "replied"
    CONVERTED = "converted"
    OPTED_OUT = "opted_out"
    ARCHIVED = "archived"


class LeadResponse(BaseModel):
    id: str
    prospect_pro_id: Optional[str] = None
    name: str
    category: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    maps_url: Optional[str] = None
    instagram_handle: Optional[str] = None
    instagram_followers: Optional[int] = None
    engagement_rate: Optional[float] = None
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    decision_maker_name: Optional[str] = None
    decision_maker_role: Optional[str] = None
    cnpj_owners: list[dict] = []
    score_total: int = 0
    score_classification: Optional[str] = None
    score_bad_website: int = 0
    site_status: Optional[str] = None
    site_score: Optional[int] = None
    site_final_url: Optional[str] = None
    site_problems: list[str] = []
    site_missing_items: list[str] = []
    site_present_items: list[str] = []
    site_response_time_seconds: Optional[float] = None
    site_http_status: Optional[int] = None
    site_audit: dict = {}
    approach_script: Optional[str] = None
    outreach_status: str = "imported"
    whatsapp_number: Optional[str] = None
    tags: list[str] = []
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LeadListResponse(BaseModel):
    total: int
    hot: int
    warm: int
    cold: int
    leads: list[LeadResponse]


class LeadFilters(BaseModel):
    classification: Optional[str] = None
    outreach_status: Optional[str] = None
    min_score: Optional[int] = None
    tags: Optional[list[str]] = None
    search: Optional[str] = None
    page: int = 1
    per_page: int = 25


class BulkActionRequest(BaseModel):
    lead_ids: list[str]
    action: str  # "tag", "archive", "assign_campaign"
    value: Optional[str] = None  # tag name or campaign_id


class ImportResponse(BaseModel):
    batch_id: str
    total_imported: int
    duplicates_skipped: int
    updated_existing: int = 0
    errors: int
    error_details: list[str] = []
