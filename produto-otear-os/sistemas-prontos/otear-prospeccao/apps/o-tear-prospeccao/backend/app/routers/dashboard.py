from fastapi import APIRouter, Depends
from app.core.auth import verify_api_key
from app.services.analytics_service import get_dashboard_stats, get_daily_summary, get_funnel_data

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def stats(_=Depends(verify_api_key)):
    return await get_dashboard_stats()


@router.get("/daily-summary")
async def daily_summary(_=Depends(verify_api_key)):
    return await get_daily_summary()


@router.get("/funnel")
async def funnel(_=Depends(verify_api_key)):
    return await get_funnel_data()
