from fastapi import APIRouter, Depends
from app.core.database import get_supabase
from app.core.auth import verify_api_key
from app.schemas.number import NumberCreate, NumberUpdate, NumberResponse, NumberHealthResponse
from app.services.number_rotation import get_warmup_limit

router = APIRouter(prefix="/api/numbers", tags=["numbers"])


@router.post("")
async def create_number(data: NumberCreate, _=Depends(verify_api_key)):
    db = get_supabase()
    result = db.table("whatsapp_numbers").insert({
        "label": data.label,
        "phone_number": data.phone_number,
        "daily_limit": data.daily_limit,
        "status": "warming_up",
    }).execute()
    return result.data[0]


@router.get("")
async def list_numbers(status: str | None = None, _=Depends(verify_api_key)):
    db = get_supabase()
    query = db.table("whatsapp_numbers").select("*").order("created_at", desc=False)
    if status:
        query = query.eq("status", status)
    result = query.execute()
    return result.data or []


@router.get("/health", response_model=NumberHealthResponse)
async def numbers_health(_=Depends(verify_api_key)):
    db = get_supabase()
    result = db.table("whatsapp_numbers").select("*").execute()
    numbers = result.data or []

    active = sum(1 for n in numbers if n["status"] == "active")
    warming = sum(1 for n in numbers if n["status"] == "warming_up")
    resting = sum(1 for n in numbers if n["status"] == "resting")
    banned = sum(1 for n in numbers if n["status"] == "banned")

    capacity = sum(n["daily_limit"] for n in numbers if n["status"] in ("active", "warming_up"))
    sent_today = sum(n["total_sent_today"] for n in numbers)

    return {
        "total_numbers": len(numbers),
        "active": active,
        "warming_up": warming,
        "resting": resting,
        "banned": banned,
        "total_capacity_today": capacity,
        "total_sent_today": sent_today,
        "numbers": numbers,
    }


@router.get("/{number_id}")
async def get_number(number_id: str, _=Depends(verify_api_key)):
    db = get_supabase()
    result = db.table("whatsapp_numbers").select("*").eq("id", number_id).single().execute()
    return result.data


@router.patch("/{number_id}")
async def update_number(number_id: str, data: NumberUpdate, _=Depends(verify_api_key)):
    db = get_supabase()
    updates = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    result = db.table("whatsapp_numbers").update(updates).eq("id", number_id).execute()
    return result.data[0] if result.data else {"error": "Número não encontrado"}


@router.post("/{number_id}/advance-warmup")
async def advance_warmup(number_id: str, _=Depends(verify_api_key)):
    """Avança o dia de warm-up e atualiza o limite diário."""
    db = get_supabase()
    number = db.table("whatsapp_numbers").select("*").eq("id", number_id).single().execute()

    if not number.data:
        return {"error": "Número não encontrado"}

    new_day = number.data["warmup_day"] + 1
    new_limit = await get_warmup_limit(new_day)

    updates = {"warmup_day": new_day, "daily_limit": new_limit}
    if new_day >= 14:
        updates["status"] = "active"

    db.table("whatsapp_numbers").update(updates).eq("id", number_id).execute()
    return {"number_id": number_id, "warmup_day": new_day, "daily_limit": new_limit}


@router.delete("/{number_id}")
async def delete_number(number_id: str, _=Depends(verify_api_key)):
    db = get_supabase()
    db.table("whatsapp_numbers").delete().eq("id", number_id).execute()
    return {"deleted": number_id}
