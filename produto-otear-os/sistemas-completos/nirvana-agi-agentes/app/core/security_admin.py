import hmac
import logging
import os

from fastapi import Security, HTTPException, Request
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

API_KEY_NAME = "x-admin-password"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def _get_admin_password() -> str | None:
    """Retorna senha admin configurada (pode ser None se só usar JWT)."""
    return os.getenv("ADMIN_PASSWORD")


async def verify_admin_access(
    api_key: str = Security(api_key_header),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    request: Request = None,
):
    """
    Verifica acesso admin via:
    1. JWT Bearer token (Supabase) — frontend autenticado
    2. x-admin-password header — integrações legadas

    Usa comparação constant-time para evitar timing attacks.
    """
    if request is not None and request.method == "OPTIONS":
        return True

    # 1. Tenta Bearer token (Supabase JWT)
    if credentials:
        from app.core.supabase import verify_supabase_jwt
        user_data = verify_supabase_jwt(credentials.credentials)
        return user_data  # Retorna dict com user_id e email

    # 2. Tenta x-admin-password header
    expected = _get_admin_password()
    if expected and api_key:
        if hmac.compare_digest(api_key.encode(), expected.encode()):
            return True

    raise HTTPException(status_code=403, detail="Admin access required")
