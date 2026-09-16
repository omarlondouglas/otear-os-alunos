import logging
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.database import engine, Base
import app.models.job

logger = logging.getLogger(__name__)

# Rate limiter — 60 requests/min per IP by default
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="O Tear Agentes API",
    description="API de Agentes IA para criação de conteúdo",
    version="0.2.0",
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restrict to known origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip() and o.strip() != "*"]

allowed_origins.append("https://otear-agentes-frontend.qc7qit.easypanel.host")

if os.getenv("ENV", "production").lower() in ("dev", "development", "local"):
    allowed_origins.extend(["http://localhost:3000", "http://localhost:5173"])
allowed_origins = list(set(allowed_origins))
logger.info(f"CORS Origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "content-type",
        "authorization",
        "x-api-key",
        "x-admin-password",
        "accept",
        "origin",
        "range",
        "x-org-id",
        "x-brand-id",
    ],
    expose_headers=["content-type", "content-length", "accept-ranges", "content-range"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; media-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none'"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    return response


@app.get("/")
def read_root():
    return {"message": "O Tear Agentes API", "version": "0.2.0"}


@app.on_event("startup")
async def setup_s3_bucket():
    """Verifica conectividade com S3/Supabase Storage no startup."""
    try:
        import boto3
        from botocore.client import Config

        s3_endpoint = os.getenv("S3_ENDPOINT_URL", "").strip().rstrip("/")
        s3_access_key = os.getenv("S3_ACCESS_KEY")
        s3_secret_key = os.getenv("S3_SECRET_KEY")
        s3_bucket = os.getenv("S3_BUCKET_NAME", "videos_agi")
        s3_region = os.getenv("S3_REGION", "auto")

        if not all([s3_endpoint, s3_access_key, s3_secret_key]):
            logger.info("S3 não configurado, pulando setup")
            return

        client = boto3.client(
            "s3",
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
            config=Config(signature_version="s3v4"),
            region_name=s3_region,
        )

        # Verificar se bucket existe (funciona com MinIO e Supabase)
        client.head_bucket(Bucket=s3_bucket)
        logger.info(f"S3 bucket '{s3_bucket}' acessível em {s3_endpoint}")
    except Exception as e:
        logger.warning(f"Falha ao verificar S3: {e}")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def setup_database_tables():
    """Create local SQLAlchemy tables when the configured database is reachable."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created")
    except Exception as e:
        logger.warning(f"Database unavailable during startup; continuing without create_all: {e}")

# Static files (processed videos)
storage_path = os.getenv("STORAGE_PATH", "/app/storage")
os.makedirs(storage_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=storage_path), name="static")
