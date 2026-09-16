from datetime import datetime, timezone
from app.core.database import get_supabase


async def select_available_number() -> dict | None:
    """Seleciona o número mais adequado para envio.

    Critérios (em ordem):
    1. Status = 'active'
    2. is_available = True
    3. current_daily_sent < daily_limit
    4. rest_until é NULL ou já passou
    5. consecutive_errors < 3
    6. Ordena por menor total_sent_today (distribui carga)
    7. Em empate, menor ban_risk_score
    """
    db = get_supabase()
    now = datetime.now(timezone.utc).isoformat()

    result = db.table("whatsapp_numbers").select("*").eq(
        "status", "active"
    ).eq(
        "is_available", True
    ).lt(
        "consecutive_errors", 3
    ).order(
        "total_sent_today", desc=False
    ).order(
        "ban_risk_score", desc=False
    ).limit(10).execute()

    if not result.data:
        return None

    for number in result.data:
        if number["current_daily_sent"] >= number["daily_limit"]:
            continue
        rest_until = number.get("rest_until")
        if rest_until and rest_until > now:
            continue
        return number

    return None


async def record_send(number_id: str, success: bool, error: str | None = None):
    """Registra um envio no número e atualiza contadores."""
    db = get_supabase()
    number = db.table("whatsapp_numbers").select("*").eq("id", number_id).single().execute()

    if not number.data:
        return

    data = number.data
    updates = {
        "current_daily_sent": data["current_daily_sent"] + 1,
        "total_sent_today": data["total_sent_today"] + 1,
        "total_sent_week": data["total_sent_week"] + 1,
        "total_sent_month": data["total_sent_month"] + 1,
        "last_sent_at": datetime.now(timezone.utc).isoformat(),
    }

    if success:
        updates["consecutive_errors"] = 0
    else:
        updates["consecutive_errors"] = data["consecutive_errors"] + 1
        updates["last_error"] = error
        if updates["consecutive_errors"] >= 3:
            updates["status"] = "resting"
            updates["is_available"] = False

    # Check daily limit
    if updates["current_daily_sent"] >= data["daily_limit"]:
        updates["is_available"] = False
        rest_hours = 4
        from datetime import timedelta
        updates["rest_until"] = (
            datetime.now(timezone.utc) + timedelta(hours=rest_hours)
        ).isoformat()

    # Update ban risk score
    updates["ban_risk_score"] = calculate_ban_risk(data, updates)

    db.table("whatsapp_numbers").update(updates).eq("id", number_id).execute()


def calculate_ban_risk(current: dict, updates: dict) -> int:
    """Calcula score de risco de ban (0-100)."""
    score = 0

    # Consecutive errors (weight 30)
    errors = updates.get("consecutive_errors", current.get("consecutive_errors", 0))
    score += min(errors * 10, 30)

    # Volume vs limit ratio (weight 25)
    daily_sent = updates.get("total_sent_today", current.get("total_sent_today", 0))
    daily_limit = current.get("daily_limit", 20)
    if daily_limit > 0:
        ratio = daily_sent / daily_limit
        score += min(int(ratio * 25), 25)

    # Warmup day - newer numbers are riskier (weight 20)
    warmup_day = current.get("warmup_day", 0)
    if warmup_day < 7:
        score += 20
    elif warmup_day < 14:
        score += 10
    elif warmup_day < 30:
        score += 5

    # Monthly volume (weight 25)
    monthly = updates.get("total_sent_month", current.get("total_sent_month", 0))
    if monthly > 2000:
        score += 25
    elif monthly > 1000:
        score += 15
    elif monthly > 500:
        score += 8

    return min(score, 100)


async def get_warmup_limit(warmup_day: int) -> int:
    """Retorna o limite diário baseado no dia de warm-up."""
    db = get_supabase()
    result = db.table("app_settings").select("value").eq(
        "key", "warmup_schedule"
    ).single().execute()

    if result.data:
        schedule = result.data["value"]
    else:
        schedule = {"day1_limit": 20, "day7_limit": 40, "day14_limit": 60, "day30_limit": 80}

    if warmup_day < 7:
        return schedule.get("day1_limit", 20)
    elif warmup_day < 14:
        return schedule.get("day7_limit", 40)
    elif warmup_day < 30:
        return schedule.get("day14_limit", 60)
    else:
        return schedule.get("day30_limit", 80)
