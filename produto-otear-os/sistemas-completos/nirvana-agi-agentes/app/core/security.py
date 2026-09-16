import hmac
import os
import logging

from fastapi import Security, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

# Headers opcionais de contexto multi-tenant
ORG_ID_HEADER = "X-Org-Id"
BRAND_ID_HEADER = "X-Brand-Id"


def _get_api_key() -> str:
    """Retorna API key configurada. Falha se não definida."""
    key = os.getenv("API_KEY") or os.getenv("VIDEO_EDITOR_API_KEY")
    if not key:
        raise RuntimeError("API_KEY não configurada no servidor")
    return key


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Valida API Key estática — usada por webhooks e integrações (WhatsApp, etc.)."""
    if not api_key:
        raise HTTPException(status_code=403, detail="Credenciais não fornecidas")

    expected_key = _get_api_key()

    if not hmac.compare_digest(api_key, expected_key):
        raise HTTPException(status_code=403, detail="API Key inválida")

    return api_key


async def verify_supabase_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    """
    Valida JWT Bearer do Supabase.
    Retorna dict com user_id e email.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Token de autenticação não fornecido")

    from app.core.supabase import verify_supabase_jwt
    return verify_supabase_jwt(credentials.credentials)


async def verify_api_key_or_token(
    api_key: str = Security(api_key_header),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict | None:
    """
    Aceita tanto API Key (webhooks) quanto JWT Bearer (frontend).
    Retorna user_data se JWT, None se API Key.
    """
    if credentials:
        from app.core.supabase import verify_supabase_jwt
        return verify_supabase_jwt(credentials.credentials)

    if api_key:
        expected_key = _get_api_key()
        if hmac.compare_digest(api_key, expected_key):
            return None
        raise HTTPException(status_code=403, detail="API Key inválida")

    raise HTTPException(status_code=401, detail="Autenticação necessária")


async def verify_api_key_or_token_with_context(
    api_key: str = Security(api_key_header),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    x_org_id: Optional[str] = Header(None, alias=ORG_ID_HEADER),
    x_brand_id: Optional[str] = Header(None, alias=BRAND_ID_HEADER),
) -> dict | None:
    """
    Igual a verify_api_key_or_token, mas inclui org_id e brand_id dos headers.
    Valida que o user é membro da org se org_id for passado.
    """
    user_data = await verify_api_key_or_token(api_key, credentials)

    if user_data and x_org_id:
        from app.models.organization import get_user_membership
        membership = get_user_membership(x_org_id, user_data["user_id"])
        if not membership:
            raise HTTPException(status_code=403, detail="Você não é membro desta organização")
        user_data["org_id"] = x_org_id
        user_data["org_role"] = membership.role

    if user_data and x_brand_id:
        from app.models.brand import get_brand
        brand = get_brand(x_brand_id)
        if brand and x_org_id and brand.org_id != x_org_id:
            raise HTTPException(status_code=403, detail="Marca não pertence a esta organização")
        user_data["brand_id"] = x_brand_id

    return user_data
