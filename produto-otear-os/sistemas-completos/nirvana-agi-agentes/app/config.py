import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "FFmpeg Video Editor API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database & Redis
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/videoeditor")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, minio
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "/app/storage")
    UPLOADS_PATH: str = os.getenv("UPLOADS_PATH", "/app/uploads")
    
    # S3 / MinIO
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_BUCKET_NAME: str | None = None
    AWS_REGION: str = "us-east-1"
    MINIO_ENDPOINT_URL: str | None = None
    
    # ElevenLabs TTS
    ELEVENLABS_API_KEY: str | None = os.getenv("ELEVENLABS_API_KEY", None)
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice
    
    # Public URL for generating media links
    PUBLIC_URL: str = os.getenv("PUBLIC_URL", "http://localhost:8000")
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
