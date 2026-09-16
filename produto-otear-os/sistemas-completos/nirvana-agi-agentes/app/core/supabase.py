import os
from fastapi import HTTPException
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

_supabase_client: Client | None = None

def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise RuntimeError("SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar configurados no .env")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase_client


def verify_supabase_jwt(token: str) -> dict:
    """Valida JWT do Supabase e retorna user data."""
    client = get_supabase()
    try:
        result = client.auth.get_user(token)
        if not result or not result.user:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")
        return {"user_id": str(result.user.id), "email": result.user.email}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
