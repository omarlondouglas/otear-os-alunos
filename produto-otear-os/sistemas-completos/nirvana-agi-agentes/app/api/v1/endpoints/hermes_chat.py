"""
Hermes Chat Endpoint

Endpoint legado/diagnostico para rodar Hermes embutido no FastAPI.
O caminho oficial do produto e /api/v1/chat, usado pela interface e pelas
skills externas do Hermes quando ele atua como cliente do sistema.

POST /api/v1/hermes/chat
  body: { "message": str, "session_id"?: str, "user_id"?: str }
  resp: { "response": str, "session_id": str, "tools_used": [...] }

GET  /api/v1/hermes/health
  resp: { installed, home, config_yaml, soul_md, ready }

POST /api/v1/hermes/reset
  body: { "session_id"?: str }
  resp: { reset: bool }
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import verify_supabase_token
from app.models.user_profile import get_user_profile

logger = logging.getLogger(__name__)
router = APIRouter()

HERMES_TIMEOUT_S = float(os.getenv("HERMES_CHAT_TIMEOUT_S", "120"))


class HermesChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class HermesChatResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[str] = []
    onboarding_required: bool = False
    onboarding_questions: List[Dict[str, Any]] = []


class ResetRequest(BaseModel):
    session_id: Optional[str] = None


@router.get("/health")
async def hermes_health():
    """Diagnostico rapido — diz se hermes-agent esta instalado e configurado."""
    from app.services.hermes_engine import is_available
    return is_available()


@router.post("/chat", response_model=HermesChatResponse)
async def hermes_chat(
    request: HermesChatRequest,
    user_data: dict = Depends(verify_supabase_token),
):
    """Processa um turno do chat com o Hermes embutido."""
    user_id = user_data.get("user_id") or "anonymous"
    session_id = request.session_id or f"otear-{user_id}"
    profile = get_user_profile(user_id)

    if not profile or not profile.onboarding_completed:
        from app.api.v1.endpoints.onboarding import build_onboarding_questions

        questions = build_onboarding_questions()
        return HermesChatResponse(
            response=(
                "Antes de usar o Hermes, preciso configurar seu perfil no Otear OS. "
                "Responda o onboarding inicial para eu personalizar estrategia, tom, "
                "formatos e referencias desde o primeiro uso."
            ),
            session_id=session_id,
            tools_used=[],
            onboarding_required=True,
            onboarding_questions=[question.model_dump() for question in questions.questions],
        )

    try:
        from app.services.hermes_engine import chat, HermesUnavailable
        logger.info(f"[hermes-chat] iniciando user={user_id} session={request.session_id}")
        t0 = time.monotonic()
        # Roda em thread separada com timeout duro pra evitar pendurar request
        # quando LLM esta inacessivel (Claude CLI sem creds, API key invalida, etc).
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    chat,
                    user_id=user_id,
                    message=request.message,
                    session_id=request.session_id,
                ),
                timeout=HERMES_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            elapsed = time.monotonic() - t0
            logger.error(f"[hermes-chat] TIMEOUT apos {elapsed:.1f}s — LLM provavelmente travado")
            raise HTTPException(
                status_code=504,
                detail=(
                    f"Hermes nao respondeu em {int(HERMES_TIMEOUT_S)}s. "
                    "Verifica /api/v1/health/llm — pode ser credencial Claude expirada."
                ),
            )
        elapsed = time.monotonic() - t0
        logger.info(f"[hermes-chat] concluido em {elapsed:.1f}s user={user_id}")
        return HermesChatResponse(**result)
    except HermesUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Hermes chat falhou para user={user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


@router.post("/reset")
async def hermes_reset(
    request: ResetRequest,
    user_data: dict = Depends(verify_supabase_token),
):
    """Limpa cache do agente (forca recarregar config + memorias na proxima msg)."""
    from app.services.hermes_engine import reset_agent
    user_id = user_data.get("user_id") or "anonymous"
    ok = reset_agent(user_id=user_id, session_id=request.session_id)
    return {"reset": ok, "user_id": user_id, "session_id": request.session_id}
