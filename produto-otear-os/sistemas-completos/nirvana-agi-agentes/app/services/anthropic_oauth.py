"""
Anthropic OAuth PKCE Authentication Module.

Extracted from OmniRoute's claude.ts OAuth flow and adapted to Python.
Allows login with Anthropic account (claude.ai) to use Claude as LLM
without a paid API key.

Usage:
    from app.services.anthropic_oauth import get_valid_token
    token = get_valid_token()  # returns access_token string or None
"""

import os
import json
import time
import hashlib
import base64
import secrets
import logging
from pathlib import Path
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)

# --- OAuth Configuration (from OmniRoute's claude.ts) ---
CLAUDE_CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
CLAUDE_AUTHORIZE_URL = "https://claude.ai/oauth/authorize"
CLAUDE_TOKEN_URL = "https://console.anthropic.com/v1/oauth/token"
CLAUDE_REDIRECT_URI = "https://platform.claude.com/oauth/code/callback"
CLAUDE_SCOPES = [
    "org:create_api_key",
    "user:profile",
    "user:inference",
]
CLAUDE_CODE_CHALLENGE_METHOD = "S256"

# Token storage file (in project root)
TOKENS_FILE = Path(os.getenv(
    "ANTHROPIC_TOKENS_FILE",
    Path(__file__).parent.parent.parent / ".anthropic_tokens.json"
))

# Buffer: refresh 5 minutes before expiry
TOKEN_EXPIRY_BUFFER = 300


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge (S256)."""
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


def get_auth_url(state: str, code_challenge: str) -> str:
    """Build the Anthropic OAuth authorization URL."""
    params = {
        "code": "true",
        "client_id": CLAUDE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": CLAUDE_REDIRECT_URI,
        "scope": " ".join(CLAUDE_SCOPES),
        "code_challenge": code_challenge,
        "code_challenge_method": CLAUDE_CODE_CHALLENGE_METHOD,
        "state": state,
    }
    return f"{CLAUDE_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code(code: str, code_verifier: str, state: str) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    auth_code = code
    code_state = ""
    if "#" in auth_code:
        parts = auth_code.split("#", 1)
        auth_code = parts[0]
        code_state = parts[1] if len(parts) > 1 else ""

    payload = {
        "code": auth_code,
        "state": code_state or state,
        "grant_type": "authorization_code",
        "client_id": CLAUDE_CLIENT_ID,
        "redirect_uri": CLAUDE_REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    response = httpx.post(
        CLAUDE_TOKEN_URL,
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Token exchange failed ({response.status_code}): {response.text}")

    return response.json()


def refresh_access_token(refresh_token: str) -> dict | None:
    """Refresh an expired access token using the refresh token."""
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLAUDE_CLIENT_ID,
    }

    try:
        response = httpx.post(
            CLAUDE_TOKEN_URL,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30,
        )

        if response.status_code != 200:
            logger.error(f"Token refresh failed ({response.status_code}): {response.text}")
            return None

        return response.json()
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return None


def save_tokens(tokens: dict) -> None:
    """Save OAuth tokens to disk."""
    data = {
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
        "scope": tokens.get("scope"),
        "saved_at": int(time.time()),
    }
    TOKENS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info(f"Tokens saved to {TOKENS_FILE}")


def load_tokens() -> dict | None:
    """Load OAuth tokens from disk."""
    if not TOKENS_FILE.exists():
        return None
    try:
        return json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load tokens: {e}")
        return None


def is_token_expired(tokens: dict) -> bool:
    """Check if the access token is expired or about to expire."""
    saved_at = tokens.get("saved_at", 0)
    expires_in = tokens.get("expires_in", 0)
    if not saved_at or not expires_in:
        return True
    return time.time() >= (saved_at + expires_in - TOKEN_EXPIRY_BUFFER)


def get_valid_token() -> str | None:
    """
    Check if OAuth credentials are available (env vars or file).
    Used for status checks only — actual LLM calls go through Claude CLI subprocess.
    """
    # 1. Check env var (Docker: injected via CLAUDE_OAUTH_ACCESS_TOKEN)
    if os.getenv("CLAUDE_OAUTH_ACCESS_TOKEN"):
        return os.getenv("CLAUDE_OAUTH_ACCESS_TOKEN")

    # 2. File-based tokens (.anthropic_tokens.json)
    tokens = load_tokens()
    if not tokens:
        return None

    if not is_token_expired(tokens):
        return tokens["access_token"]

    # Token expired, try refresh
    refresh_tok = tokens.get("refresh_token")
    if not refresh_tok:
        return None

    logger.info("Access token expired, refreshing...")
    new_tokens = refresh_access_token(refresh_tok)
    if not new_tokens or not new_tokens.get("access_token"):
        return None

    if not new_tokens.get("refresh_token"):
        new_tokens["refresh_token"] = refresh_tok

    save_tokens(new_tokens)
    return new_tokens["access_token"]
