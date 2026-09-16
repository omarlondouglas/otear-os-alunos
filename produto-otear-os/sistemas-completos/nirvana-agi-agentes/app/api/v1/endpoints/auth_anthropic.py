"""
FastAPI routes for Anthropic OAuth login via browser.

Flow:
    1. GET  /authorize  -> returns auth_url + state (frontend opens popup)
    2. User logs in at claude.ai, gets redirected to platform.claude.com
       which shows the authorization code on screen
    3. POST /exchange   -> frontend sends code, backend exchanges for tokens
    4. GET  /status     -> check if authenticated
    5. POST /logout     -> clear tokens

Endpoints:
    GET  /api/v1/auth-anthropic/status    - Check if logged in
    GET  /api/v1/auth-anthropic/authorize - Get auth URL + PKCE data
    POST /api/v1/auth-anthropic/exchange  - Exchange code for tokens
    POST /api/v1/auth-anthropic/logout    - Clear saved tokens
"""

import secrets
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.anthropic_oauth import (
    generate_pkce_pair,
    get_auth_url,
    exchange_code,
    save_tokens,
    load_tokens,
    is_token_expired,
    get_valid_token,
    TOKENS_FILE,
)

router = APIRouter(prefix="/auth-anthropic", tags=["auth-anthropic"])

# In-memory store for PKCE sessions (state -> code_verifier)
_oauth_sessions: dict = {}


@router.get("/status")
async def auth_status():
    """Check if user has a valid Anthropic OAuth token."""
    tokens = load_tokens()
    if not tokens:
        return {"authenticated": False, "reason": "no_tokens"}

    if is_token_expired(tokens):
        new_token = get_valid_token()
        if new_token:
            return {"authenticated": True, "provider": "anthropic_oauth"}
        return {"authenticated": False, "reason": "token_expired"}

    return {"authenticated": True, "provider": "anthropic_oauth"}


@router.get("/authorize")
async def auth_authorize():
    """
    Generate OAuth authorization URL with PKCE.
    Frontend opens this URL in a popup/new tab.
    The user logs in and gets a code displayed on screen.
    """
    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(32)

    # Store PKCE verifier for the exchange step
    _oauth_sessions[state] = code_verifier

    auth_url = get_auth_url(state, code_challenge)

    return {
        "auth_url": auth_url,
        "state": state,
    }


class ExchangeRequest(BaseModel):
    code: str
    state: str


@router.post("/exchange")
async def auth_exchange(body: ExchangeRequest):
    """
    Exchange authorization code for access + refresh tokens.
    Called by frontend after user pastes the code from claude.ai.
    """
    code_verifier = _oauth_sessions.pop(body.state, None)
    if not code_verifier:
        return {"error": "invalid_state", "message": "Sessao expirada. Tente novamente."}

    try:
        tokens = exchange_code(body.code, code_verifier, body.state)
    except RuntimeError as e:
        return {"error": "exchange_failed", "message": str(e)}

    if not tokens.get("access_token"):
        return {"error": "no_token", "message": "Nenhum token recebido."}

    save_tokens(tokens)
    return {"success": True, "provider": "anthropic_oauth"}


@router.post("/logout")
async def auth_logout():
    """Clear saved OAuth tokens."""
    if TOKENS_FILE.exists():
        TOKENS_FILE.unlink()
    return {"status": "logged_out"}
