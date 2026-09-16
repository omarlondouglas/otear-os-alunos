from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from datetime import datetime
from app.core.database import Base

class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(String, primary_key=True, index=True) # UUID
    user_id = Column(String, index=True, nullable=True) # Opcional por enquanto
    
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED)
    
    # Input
    input_video_path = Column(String, nullable=False)
    operations = Column(JSON, nullable=False) # Lista de operações
    
    # Output
    output_video_path = Column(String, nullable=True)
    download_url = Column(String, nullable=True)
    
    # Metadata
    progress = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    processing_time = Column(Integer, nullable=True) # em segundos
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Webhook
    webhook_url = Column(String, nullable=True)
