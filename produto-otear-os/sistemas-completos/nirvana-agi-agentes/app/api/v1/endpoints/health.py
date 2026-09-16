"""
Health endpoints — diagnostico rapido sem auth.

GET /api/v1/health        - liveness simples (200 sempre que app sobe)
GET /api/v1/health/llm    - estado dos providers LLM por API key
GET /api/v1/health/full   - todos os componentes
"""
from __future__ import annotations

import logging
import os

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def health():
    return {"status": "ok"}


@router.get("/llm")
async def llm_health():
    """
    Diagnostica TODOS os providers de LLM.
    Retorna 200 sempre (mesmo com providers quebrados) — analise o payload.
    """
    out = {
        "anthropic_api_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openrouter_api_key": bool(os.getenv("OPENROUTER_API_KEY")),
        "openai_api_key": bool(os.getenv("OPENAI_API_KEY")),
        "google_api_key": bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
        "groq_api_key": bool(os.getenv("GROQ_API_KEY")),
        "image_generation": {
            "provider": os.getenv("IMAGE_GEN_PROVIDER", "auto"),
            "google_api_key": bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")),
            "chatgpt_bridge_url": os.getenv("CHATGPT_BRIDGE_URL", "http://chatgpt-bridge:10531/v1"),
            "chatgpt_bridge_configured": bool(
                os.getenv("CODEX_AUTH_JSON")
                or os.getenv("CODEX_ACCESS_TOKEN")
                or os.path.exists("/root/.codex/auth.json")
            ),
        },
    }

    # Provider ativo segundo o model_factory
    try:
        from app.core.model_factory import get_llm_status
        out["active_provider"] = get_llm_status()
    except Exception as e:
        out["active_provider"] = {"error": str(e)}

    # Diagnostico final: tem como rodar Jobs/Hermes?
    has_any_llm = (
        out["anthropic_api_key"]
        or out["openrouter_api_key"]
        or out["google_api_key"]
    )
    out["healthy"] = has_any_llm
    if not has_any_llm:
        out["recommendation"] = (
            "Sem LLM funcional. Configure OPENROUTER_API_KEY, ANTHROPIC_API_KEY ou GOOGLE_API_KEY."
        )
    return out


@router.get("/full")
async def full_health():
    """Health completo: LLM + Redis + Supabase + Vault + sidecars."""
    out = {"llm": await llm_health()}

    # Redis
    try:
        from app.core.celery_app import celery_app
        from celery import current_app
        i = current_app.control.inspect(timeout=2.0)
        out["redis"] = {"reachable": i.ping() is not None}
    except Exception as e:
        out["redis"] = {"reachable": False, "error": str(e)}

    # Supabase
    try:
        from app.core.supabase import get_supabase
        client = get_supabase()
        client.table("user_profiles").select("id").limit(1).execute()
        out["supabase"] = {"reachable": True}
    except Exception as e:
        out["supabase"] = {"reachable": False, "error": str(e)[:200]}

    # Vault
    try:
        vault_path = os.getenv("VAULT_PATH", "/app/vault")
        out["vault"] = {
            "path": vault_path,
            "exists": os.path.isdir(vault_path),
            "is_git": os.path.isdir(os.path.join(vault_path, ".git")),
        }
    except Exception as e:
        out["vault"] = {"error": str(e)}

    # Sidecars (best effort)
    import httpx
    sidecars = {
        "remotion": os.getenv("REMOTION_SERVICE_URL", "http://remotion:8003"),
        "carousel": os.getenv("CAROUSEL_API_URL") or os.getenv("CAROUSEL_SERVICE_URL", "http://carousel:8000"),
        "chatgpt_bridge": os.getenv("CHATGPT_BRIDGE_URL", "http://chatgpt-bridge:10531/v1").replace("/v1", ""),
    }
    out["sidecars"] = {}
    for name, url in sidecars.items():
        try:
            with httpx.Client(timeout=3) as c:
                r = c.get(f"{url}/health")
                out["sidecars"][name] = {"reachable": r.status_code < 500, "status": r.status_code}
        except Exception as e:
            out["sidecars"][name] = {"reachable": False, "error": str(e)[:100]}

    return out
