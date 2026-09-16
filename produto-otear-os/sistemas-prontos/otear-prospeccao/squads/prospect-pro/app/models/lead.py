from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class LeadClassification(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class GoogleMapsData(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None
    maps_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos_count: Optional[int] = None
    opening_hours: Optional[str] = None


class InstagramPost(BaseModel):
    url: Optional[str] = None
    likes: int = 0
    comments: int = 0
    date: Optional[datetime] = None
    caption_preview: Optional[str] = None
    is_reel: bool = False
    is_carousel: bool = False


class InstagramData(BaseModel):
    handle: Optional[str] = None
    profile_url: Optional[str] = None
    bio: Optional[str] = None
    bio_link: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    posts_count: Optional[int] = None
    is_business: Optional[bool] = None
    is_verified: bool = False
    profile_pic_url: Optional[str] = None
    recent_posts: list[InstagramPost] = Field(default_factory=list)
    engagement_rate: Optional[float] = None
    avg_likes: Optional[float] = None
    avg_comments: Optional[float] = None
    posting_frequency_days: Optional[float] = None
    last_post_date: Optional[datetime] = None


class WebsiteAudit(BaseModel):
    status: str = "unknown"
    score: int = 0
    final_url: Optional[str] = None
    problems: list[str] = Field(default_factory=list)
    checklist: dict = Field(default_factory=dict)
    response_time_seconds: Optional[float] = None
    http_status: Optional[int] = None


class ScoreBreakdown(BaseModel):
    no_website: int = 0
    bad_website: int = 0
    no_instagram: int = 0
    low_engagement: int = 0
    irregular_posting: int = 0
    few_reviews: int = 0
    low_rating: int = 0
    no_professional_bio: int = 0
    no_bio_link: int = 0
    total: int = 0
    classification: LeadClassification = LeadClassification.COLD


class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    google: GoogleMapsData
    instagram: Optional[InstagramData] = None
    website_audit: Optional[WebsiteAudit] = None
    score: Optional[ScoreBreakdown] = None
    approach_script: Optional[str] = None
    status: str = "raw"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class ScrapeRequest(BaseModel):
    query: str = Field(..., description="Ex: 'restaurantes', 'salões de beleza'")
    location: str = Field(default="São Paulo", description="Cidade ou região")
    limit: int = Field(default=20, ge=1, le=50, description="Máximo de leads")


class EnrichRequest(BaseModel):
    leads_file: Optional[str] = Field(None, description="Caminho do arquivo de leads")
    lead_ids: Optional[list[str]] = Field(None, description="IDs específicos para enriquecer")


class AnalyzeRequest(BaseModel):
    leads_file: Optional[str] = None
    lead_ids: Optional[list[str]] = None
    posts_to_analyze: int = Field(default=12, ge=1, le=30)


class ReportRequest(BaseModel):
    leads_file: Optional[str] = None
    lead_ids: Optional[list[str]] = None
    title: str = Field(default="Relatório de Prospecção")
    include_approach_scripts: bool = True


class LeadListResponse(BaseModel):
    total: int
    hot: int
    warm: int
    cold: int
    leads: list[Lead]
