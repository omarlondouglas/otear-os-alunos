from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageQueueItem(BaseModel):
    id: str
    campaign_id: Optional[str] = None
    lead_id: str
    whatsapp_to: str
    message_body: str
    assigned_number_id: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class MessageStatusUpdate(BaseModel):
    status: str  # sent, delivered, read, failed
    external_message_id: Optional[str] = None
    error_message: Optional[str] = None


class ManualSendRequest(BaseModel):
    lead_id: str
    message_body: str
    whatsapp_to: str


class ConversationResponse(BaseModel):
    id: str
    lead_id: str
    lead_name: str
    whatsapp_number: str
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    unread_count: int = 0
    sentiment: Optional[str] = None


class ConversationMessageResponse(BaseModel):
    id: str
    direction: str
    message_body: str
    message_type: str = "text"
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class ReplyRequest(BaseModel):
    message_body: str
