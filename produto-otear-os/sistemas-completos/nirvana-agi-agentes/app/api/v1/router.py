from fastapi import APIRouter
from app.api.v1.endpoints import videos, logs, media, tts

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(tts.router, prefix="/tts", tags=["tts"])
from app.api.v1.endpoints import chat
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
from app.api.v1.endpoints import settings
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
from app.api.v1.endpoints import auth, users, onboarding, library, calendar, analytics, organizations, brands
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
from app.api.v1.endpoints import auth_anthropic
api_router.include_router(auth_anthropic.router, tags=["auth-anthropic"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
api_router.include_router(library.router, prefix="/library", tags=["library"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
from app.api.v1.endpoints import agents
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
from app.api.v1.endpoints import references
api_router.include_router(references.router, prefix="/references", tags=["references"])
from app.api.v1.endpoints import hermes_chat
api_router.include_router(hermes_chat.router, prefix="/hermes", tags=["hermes"])
from app.api.v1.endpoints import graph
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
from app.api.v1.endpoints import admin
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
from app.api.v1.endpoints import news
api_router.include_router(news.router, prefix="/news", tags=["news"])
from app.api.v1.endpoints import health
api_router.include_router(health.router, prefix="/health", tags=["health"])
from app.api.v1.endpoints import carousels
api_router.include_router(carousels.router, prefix="/carousels", tags=["carousels"])


