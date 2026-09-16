"""
Agents RPC Endpoint
Bridge entre o Hermes (orquestrador frontal) e os agentes Agno (executores).

POST /api/v1/agents/{agent_name}/run
  body: { "task": str, "user_id"?: str, "context"?: dict }
  resp: { "result": str, "agent_name": str, "duration_ms": int }

GET /api/v1/agents
  resp: [{name, role, tools_count}, ...]

Usado pelas skills do Hermes em ~/.hermes/skills/agno-bridge/.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import verify_api_key_or_token_with_context

logger = logging.getLogger(__name__)
router = APIRouter()


# Mapeamento agent_name (canonico) -> import path do Agent.
# Resolvido lazy para evitar carregar Agno e seus modelos no startup do FastAPI.
AGENT_REGISTRY = {
    # Agentes principais (Agno team original)
    "beast":              ("app.agents.agno_agents", "video_analyst"),
    "nolan":              ("app.agents.agno_agents", "video_director"),
    "ogilvy":             ("app.agents.agno_agents", "copywriter"),
    "olivetto":           ("app.agents.agno_agents", "dona"),
    "garyv":              ("app.agents.agno_agents", "carousel_agent"),
    "scher":              ("app.agents.agno_agents", "designer"),
    "erico":              ("app.agents.agno_agents", "stylist"),
    "neumeier":           ("app.agents.brandcraft_agents", "brandcraft_team"),
    "guard":              ("app.agents.agno_agents", "guard_agent"),
    # Squads adaptados do Opensquad
    "clara_copy":         ("app.agents.squad_agents", "clara_copy"),
    "news_carousel":      ("app.agents.squad_agents", "news_carousel"),
    "youtuber_thumbnail": ("app.agents.squad_agents", "youtuber_thumbnail"),
    "neuro_cover":        ("app.agents.squad_agents", "neuro_cover"),
    "insta_visual_ref":   ("app.agents.squad_agents", "insta_visual_ref"),
}


class RunAgentRequest(BaseModel):
    task: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class RunAgentResponse(BaseModel):
    result: str
    agent_name: str
    duration_ms: int
    tools_used: list = []


class AgentInfo(BaseModel):
    name: str
    role: str
    canonical_id: str


def _resolve_agent(agent_name: str):
    canonical = agent_name.lower().strip()
    if canonical not in AGENT_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. "
                   f"Available: {sorted(AGENT_REGISTRY.keys())}",
        )
    module_path, attr_name = AGENT_REGISTRY[canonical]
    import importlib
    module = importlib.import_module(module_path)
    agent = getattr(module, attr_name, None)
    if agent is None:
        raise HTTPException(
            status_code=500,
            detail=f"Registry points to {module_path}.{attr_name} but attribute missing",
        )
    return canonical, agent


@router.post("/{agent_name}/run", response_model=RunAgentResponse)
async def run_agent(
    agent_name: str,
    request: RunAgentRequest,
    user_data: dict | None = Depends(verify_api_key_or_token_with_context),
):
    """Executa uma task em um agente Agno especifico (chamado pelas skills do Hermes)."""
    canonical, agent = _resolve_agent(agent_name)

    # Setup thread-local de user/org/brand context (usado pelas tools internas)
    context = dict(request.context or {})
    user_id = request.user_id or (user_data or {}).get("user_id")
    org_id = context.get("org_id") or (user_data or {}).get("org_id")
    brand_id = context.get("brand_id") or (user_data or {}).get("brand_id")

    from app.agents.agno_tools import set_current_user_id, set_current_context
    set_current_user_id(user_id)
    set_current_context(org_id=org_id, brand_id=brand_id)

    started = time.time()
    try:
        # Agno Agent.arun() retorna um RunResponse com .content
        run_resp = await agent.arun(request.task)
        result_text = getattr(run_resp, "content", None) or str(run_resp)
        tools_used = []
        for tool_call in getattr(run_resp, "tool_calls", None) or []:
            name = getattr(tool_call, "tool_name", None) or getattr(tool_call, "name", None)
            if name:
                tools_used.append(name)
    except Exception as e:
        logger.error(f"Agent {canonical} run failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {e}")
    finally:
        duration_ms = int((time.time() - started) * 1000)

    return RunAgentResponse(
        result=result_text,
        agent_name=canonical,
        duration_ms=duration_ms,
        tools_used=tools_used,
    )


@router.get("", response_model=list[AgentInfo])
async def list_agents():
    """Lista todos os agentes RPC-callable. Hermes usa para descobrir tools disponiveis."""
    out = []
    for canonical, (module_path, attr_name) in AGENT_REGISTRY.items():
        import importlib
        try:
            module = importlib.import_module(module_path)
            agent = getattr(module, attr_name, None)
            if agent is None:
                continue
            display_name = getattr(agent, "name", canonical.title())
            role = getattr(agent, "role", "") or ""
            out.append(AgentInfo(
                name=display_name,
                role=role[:200],
                canonical_id=canonical,
            ))
        except Exception as e:
            logger.warning(f"Failed to introspect agent {canonical}: {e}")
    return out


@router.get("/health")
async def agents_health():
    """Health check rapido sem instanciar os agentes."""
    return {
        "status": "ok",
        "registered": list(AGENT_REGISTRY.keys()),
        "count": len(AGENT_REGISTRY),
    }
