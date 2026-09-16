from fastapi import APIRouter, Depends
from app.core.database import get_supabase
from app.core.auth import verify_api_key

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
async def get_settings(_=Depends(verify_api_key)):
    db = get_supabase()
    result = db.table("app_settings").select("*").execute()
    return {item["key"]: item["value"] for item in (result.data or [])}


@router.patch("")
async def update_settings(updates: dict, _=Depends(verify_api_key)):
    db = get_supabase()
    for key, value in updates.items():
        db.table("app_settings").upsert({
            "key": key,
            "value": value,
        }).execute()
    return {"updated": list(updates.keys())}
