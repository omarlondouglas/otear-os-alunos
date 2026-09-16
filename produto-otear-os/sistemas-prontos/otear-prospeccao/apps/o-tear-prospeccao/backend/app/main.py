from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.routers import leads, campaigns, messages, numbers, conversations, dashboard, webhooks, settings

app = FastAPI(
    title="O Tear Prospecção",
    description="Plataforma de disparos WhatsApp para leads prospectados",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

config = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(campaigns.router)
app.include_router(messages.router)
app.include_router(numbers.router)
app.include_router(conversations.router)
app.include_router(dashboard.router)
app.include_router(webhooks.router)
app.include_router(settings.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "O Tear Prospecção"}
